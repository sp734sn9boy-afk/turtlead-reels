# -*- coding: utf-8 -*-
"""タートルが話す縦型ショート動画（1080x1920・30fps）を作る共通部品。

使う側：make_vol1.py（本番版）、../声の聞き比べ/make_voice_compare.py（声の聞き比べ）

前提：VOICEVOX ENGINE（公式・CPU版）がこのパソコンの 50021 番で動いていること。
  docker run -d --rm --name vv -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest
  （Docker 自体が止まっているときは先に dockerd を起動）

台本のデータの形（Line のリスト）：
  Line(chunks=[Chunk(["字幕1行目", "字幕2行目"]), ...], head=..., body=..., gap=秒)
  - 字幕は1つの Chunk が画面1枚分（2行まで）。音声も Chunk ごとに作るので字幕と声がぴったり合う。
  - 読み上げ用の文は、字幕の文に READING（読み方の置きかえ）をかけて自動で作る。Chunk(…, tts="…") で直接指定も可。
"""
import json, math, os, random, subprocess, urllib.parse, urllib.request, wave
from dataclasses import dataclass, field
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))           # リポジトリの一番上
FONT_B = os.path.join(HERE, "..", "fonts", "NotoSansJP-Bold.ttf")
FONT_R = os.path.join(HERE, "..", "fonts", "RoundedMplus1c-ExtraBold.ttf")
CHAR = os.path.join(ROOT, "資料", "ai_office", "characters", "poses", "leader_talk.png")
VV = "http://127.0.0.1:50021"

W, H, FPS = 1080, 1920, 30
SR = 48000
NAVY_TOP, NAVY_BOT = (8, 16, 36), (20, 36, 90)
CYAN, WHITE, YELLOW, INK = (60, 214, 240), (255, 255, 255), (255, 204, 77), (8, 16, 36)
DIM = (185, 200, 230)

# 読み方の置きかえ（字幕の文 → 読み上げ用の文）。長いものから順に置きかえる。
READING = {
    "Claude Fable 5.2": "クロード・フェイブル5.2",
    "ChatGPT": "チャットジーピーティー",
    "Googleマップ": "グーグルマップ",
    "Google": "グーグル",
    "Gemini": "ジェミニ",
    "Anthropic": "アンソロピック",
    "OpenAI": "オープンエーアイ",
    "十分": "じゅうぶん",       # VOICEVOXは「じゅっぷん」と読むため
    "日本": "にほん",           # 「にっぽん」になるため
}

_fonts = {}
def fB(s):
    if ("B", s) not in _fonts: _fonts[("B", s)] = ImageFont.truetype(FONT_B, s)
    return _fonts[("B", s)]
def fR(s):
    if ("R", s) not in _fonts: _fonts[("R", s)] = ImageFont.truetype(FONT_R, s)
    return _fonts[("R", s)]


@dataclass
class Chunk:
    lines: list                 # 字幕（1〜2行）
    tts: str = None             # 読み上げ用の文（省略時は字幕から自動）


@dataclass
class Line:
    chunks: list
    head: str = None            # パネル上段（ニュースの番号・日付・出典）のキー
    body: str = None            # パネル本体のキー
    gap: float = 0.26           # このセリフのあとの間（秒）
    nod: bool = False           # うなずく
    chime: bool = False         # セリフの頭に小さな「ポン」（自作の音）


def to_tts(text):
    for k in sorted(READING, key=len, reverse=True):
        text = text.replace(k, READING[k])
    return text


# ---------------------------------------------------------------- 音声（VOICEVOX）
_op = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # localhost はプロキシを通さない

def speaker_id(name, style="ノーマル"):
    """声の名前（例：春日部つむぎ）→ スタイルID。無ければ ValueError。"""
    sp = json.loads(_op.open(VV + "/speakers").read())
    for s in sp:
        if s["name"] == name:
            for st in s["styles"]:
                if st["name"] == style: return st["id"]
            return s["styles"][0]["id"]
    raise ValueError(f"VOICEVOXに「{name}」がありません。あるのは：" + "、".join(s["name"] for s in sp))


def synth(text, spk, speed=1.1, pitch=0.0, intonation=1.0, volume=1.0):
    q = json.loads(_op.open(urllib.request.Request(
        f"{VV}/audio_query?speaker={spk}&text=" + urllib.parse.quote(text), method="POST")).read())
    q.update(speedScale=speed, pitchScale=pitch, intonationScale=intonation, volumeScale=volume,
             prePhonemeLength=0.05, postPhonemeLength=0.12, outputSamplingRate=SR, outputStereo=False)
    wav = _op.open(urllib.request.Request(f"{VV}/synthesis?speaker={spk}", data=json.dumps(q).encode(),
                                          headers={"Content-Type": "application/json"})).read()
    import io
    with wave.open(io.BytesIO(wav)) as f:
        a = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a, q["kana"]


def chime(freq=1318.5, dur=0.45):
    """自作の小さな合図の音（サイン波2つを減衰させただけ）。著作権の問題なし。"""
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 9) * np.minimum(1, t / 0.005)
    return (0.6 * np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 1.5 * t)) * env


def build_audio(lines, voice, speed=1.1, pitch=0.0, intonation=1.0, head=0.3, tail=2.3, chime_db=-26,
                log=None):
    """台本 → (声のみの波形, 合図入り波形, 字幕のタイミング, 各セリフの開始・終了)"""
    spk = speaker_id(voice)
    pieces, subs, spans = [np.zeros(int(SR * head), np.float32)], [], []
    t = head; chimes = []
    for li, ln in enumerate(lines):
        st = t
        if ln.chime: chimes.append(t)
        for ci, ch in enumerate(ln.chunks):
            text = ch.tts or to_tts("".join(ch.lines))
            a, kana = synth(text, spk, speed, pitch, intonation)
            if log is not None: log.append(f"{li+1}-{ci+1}\t{text}\t{kana}")
            pieces.append(a); subs.append((t, t + len(a) / SR, ch.lines)); t += len(a) / SR
            last = ci == len(ln.chunks) - 1
            g = ln.gap if last else (0.18 if "".join(ch.lines).endswith("。") else 0.06)
            pieces.append(np.zeros(int(SR * g), np.float32)); t += g
        spans.append((st, subs[-1][1]))
    pieces.append(np.zeros(int(SR * tail), np.float32))
    voice_a = np.concatenate(pieces)
    # 音量をそろえる（声によって大きさが違うため）：話している部分のRMSを -15dBFS に（スマホ向けに約-16LUFS）。
    # 大きすぎる山だけをやわらかく抑える（0.8を超えた分を tanh で丸める＝割れ防止）
    act = voice_a[np.abs(voice_a) > 0.01]
    rms = np.sqrt(np.mean(act ** 2)) if len(act) else 1
    voice_a = voice_a * (10 ** (-15 / 20) / rms)
    th = 0.8; over = np.abs(voice_a) > th
    voice_a[over] = np.sign(voice_a[over]) * (th + (0.98 - th) * np.tanh((np.abs(voice_a[over]) - th) / (0.98 - th)))
    mix = voice_a.copy()
    c = chime() * 10 ** (chime_db / 20) / 0.9
    for ct in chimes:
        i = int(ct * SR); j = min(len(mix), i + len(c)); mix[i:j] += c[:j - i]
    return voice_a, mix, subs, spans


def write_wav(path, a):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- キャラクター
def make_faces(scale_px=585):
    base = Image.open(CHAR).convert("RGBA")
    def box(x0, y0, x1, y1):  # 64x64のドット格子（1ドット=7px、余白32px）→ 画素の四角
        return (32 + 7*x0, 32 + 7*y0, 32 + 7*(x1+1) - 1, 32 + 7*(y1+1) - 1)
    screen_col = base.getpixel((32 + 7*32 + 3, 32 + 7*18 + 3))
    blush = base.getpixel((32 + 7*34 + 3, 32 + 7*22 + 3))
    clean = base.copy(); d = ImageDraw.Draw(clean)
    d.rectangle((32 + 7*48, 0, 511, 32 + 7*14), fill=(0, 0, 0, 0))   # 吹き出しを消す
    def face(mouth, blink):
        im = clean.copy(); d = ImageDraw.Draw(im)
        d.rectangle(box(32, 22, 37, 24), fill=screen_col)
        if mouth == 0:
            for x, y in [(33, 22), (34, 23), (35, 23), (36, 22)]: d.rectangle(box(x, y, x, y), fill=CYAN)
        elif mouth == 1:
            d.rectangle(box(33, 22, 36, 22), fill=CYAN); d.rectangle(box(34, 23, 35, 23), fill=CYAN)
            d.rectangle(box(34, 22, 35, 22), fill=blush)
        else:
            d.rectangle(box(33, 22, 36, 24), fill=CYAN); d.rectangle(box(34, 22, 35, 23), fill=blush)
        if blink:
            for ex in (28, 37):
                d.rectangle(box(ex, 16, ex+2, 20), fill=screen_col); d.rectangle(box(ex, 19, ex+2, 19), fill=CYAN)
        return im.resize((scale_px, scale_px), Image.NEAREST)
    return {(m, b): face(m, b) for m in (0, 1, 2) for b in (0, 1)}


# ---------------------------------------------------------------- 背景・共通の表示
def make_background(credit, credit_size=32):
    px = np.zeros((H, W, 3), np.uint8)
    for i in range(3): px[..., i] = np.linspace(NAVY_TOP[i], NAVY_BOT[i], H)[:, None]
    bg = Image.fromarray(px); d = ImageDraw.Draw(bg, "RGBA")
    r = 46
    for row in range(-1, int(H / (r*1.5)) + 2):
        for col in range(-1, int(W / (r*1.732)) + 2):
            cx = col * r * 1.732 + (row % 2) * r * 0.866; cy = row * r * 1.5
            d.polygon([(cx + r*math.cos(math.radians(60*k+30)), cy + r*math.sin(math.radians(60*k+30))) for k in range(6)],
                      outline=(60, 214, 240, 18))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((W/2-420, 930, W/2+420, 1520), fill=(60, 214, 240, 55)); glow = glow.filter(ImageFilter.GaussianBlur(110))
    bg = Image.alpha_composite(bg.convert("RGBA"), glow)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((60, 120, W-60, 300), 36, fill=(4, 7, 15, 210), outline=CYAN, width=4)
    d.text((W/2, 178), "AI動画編集部", font=fR(46), fill=CYAN, anchor="mm")
    d.text((W/2, 246), "今週のAIニュース", font=fB(70), fill=WHITE, anchor="mm")
    d.rounded_rectangle((90, 330, W-90, 400), 35, fill=(255, 204, 77, 235))
    d.text((W/2, 365), "AIが情報収集から動画まで作っています", font=fB(38), fill=INK, anchor="mm")
    text_fit(d, (W/2, H-78), credit, credit_size, W - 80, fill=DIM if credit_size <= 32 else WHITE, anchor="mm")
    return bg.convert("RGB")


def logo_mark(size):
    """タートルアドのロゴマーク（資料/googlemap_photos/src/06_logo.html のSVGと同じ形）"""
    S = 4; im = Image.new("RGBA", (size*S, size*S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = size * S / 100
    P = lambda pts: [(x*k, y*k) for x, y in pts]
    outer = [(50, 6), (88.1, 28), (88.1, 72), (50, 94), (11.9, 72), (11.9, 28)]
    inner = [(50, 32), (65.6, 41), (65.6, 59), (50, 68), (34.4, 59), (34.4, 41)]
    d.polygon(P(outer), fill=(13, 58, 52))
    for a, b in zip(outer, inner): d.line(P([a, b]), fill=(60, 214, 240, 205), width=int(2*k))
    d.line(P(outer + outer[:1]), fill=CYAN, width=int(3.2*k), joint="curve")
    d.line(P(inner + inner[:1]), fill=CYAN, width=int(2.5*k), joint="curve")
    for x, y in inner: d.ellipse((x*k-3*k, y*k-3*k, x*k+3*k, y*k+3*k), fill=WHITE)
    d.ellipse((45*k, 45*k, 55*k, 55*k), fill=CYAN)
    return im.resize((size, size), Image.LANCZOS)


def text_fit(d, xy, s, size, maxw, font=fB, **kw):
    """幅に収まるまで文字を小さくして描く"""
    while font(size).getlength(s) > maxw and size > 20: size -= 2
    d.text(xy, s, font=font(size), **kw)
    return size


# ---------------------------------------------------------------- 字幕
SUB_TOP = 1500          # 字幕の箱の上端（キャラの足元 ≒ 1480 より下）
SUB_SIZE = 46           # 1行20字前後が 900px に収まる大きさ
def draw_sub(frame, lines):
    d = ImageDraw.Draw(frame, "RGBA")
    f = fB(SUB_SIZE); lh = 70
    size = SUB_SIZE
    while max(fB(size).getlength(l) for l in lines) > 920: size -= 2
    f = fB(size)
    hgt = 44 + lh * len(lines)
    d.rounded_rectangle((60, SUB_TOP, W - 60, SUB_TOP + hgt), 28, fill=(4, 7, 15, 222), outline=(60, 214, 240, 90), width=2)
    for k, l in enumerate(lines):
        d.text((W/2, SUB_TOP + 22 + lh * k + lh/2), l, font=f, fill=WHITE, anchor="mm",
               stroke_width=2, stroke_fill=INK)


def sub_overflow_check(subs):
    """字幕がはみ出していないかを数字で確認（1行の幅・行数）"""
    bad = []
    for _, _, lines in subs:
        if len(lines) > 2: bad.append(("3行以上", lines))
        for l in lines:
            if fB(SUB_SIZE).getlength(l) > 920: bad.append(("幅オーバー（縮小で対応）", l))
    return bad


# ---------------------------------------------------------------- 1本の動画に書き出す
PANEL_Y = 425           # パネル（ニュースの表示）を置く高さ。パネルは 1080x500
CHAR_Y = 930            # キャラの箱（585px）の上端

def render(out_mp4, lines, layers, voice_a, mix_a, subs, spans, end_layer=None, tail_card=None):
    """layers: {キー: 1080x500のRGBA画像 or 関数}。end_layer: 最後の声のあとに字幕の場所へ出す画像。"""
    total = len(mix_a) / SR
    wav = out_mp4[:-4] + "_audio.wav"; write_wav(wav, mix_a)
    nframes = int(math.ceil(total * FPS)); spf = SR / FPS
    rms = np.array([np.sqrt(np.mean(voice_a[int(i*spf):int((i+1)*spf)] ** 2) + 1e-12) for i in range(nframes)])
    ref = np.percentile(rms[rms > 0.01], 90) if (rms > 0.01).any() else 1
    level = rms / ref
    faces = make_faces(); CW = faces[(0, 0)].size[0]
    bg = layers["__bg__"]

    # パネルの上段・本体が切り替わる時刻
    def timeline(attr):
        ev = []; prev = object()
        for ln, (st, en) in zip(lines, spans):
            k = getattr(ln, attr)
            if k != prev: ev.append((st - 0.08 if ev else -1.0, k)); prev = k   # 最初の表示は0秒目から出しておく
        return ev
    tl = {"head": timeline("head"), "body": timeline("body")}
    def current(attr, t):
        cur = (None, 0)
        for st, k in tl[attr]:
            if t >= st: cur = (k, st)
        return cur
    fade_cache = {}
    def faded(key, a):
        a = round(a, 1)
        if (key, a) not in fade_cache:
            im = layers[key].copy()
            if a < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
            fade_cache[(key, a)] = im
        return fade_cache[(key, a)]

    random.seed(3); blinks = []; bt = 1.4
    while bt < total: blinks.append(bt); bt += random.uniform(2.8, 4.5)
    nod_spans = [sp for ln, sp in zip(lines, spans) if ln.nod]
    last_voice_end = spans[-1][1]

    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                           "-movflags", "+faststart", out_mp4], stdin=subprocess.PIPE)
    prev_m = 0
    for i in range(nframes):
        t = i / FPS
        frame = bg.copy()
        for attr in ("head", "body"):
            k, st = current(attr, t)
            if k:
                a = min(1.0, max(0.0, (t - st) / 0.25)); dy = int((1 - a) * 24)
                im = faded(k, a); frame.paste(im, (0, PANEL_Y + dy), im)
        lv = level[i]
        m = 2 if lv > 0.55 else (1 if lv > 0.18 else 0)
        if m != prev_m and i % 2 == 1: m = prev_m
        prev_m = m
        b = any(0 <= t - x < 0.13 for x in blinks)
        bob = int(8 * math.sin(2 * math.pi * t / 1.6))
        for s, e in nod_spans:                    # うなずき：0.5秒で1回、2回
            if s <= t <= s + 1.0: bob += int(18 * max(0, math.sin(2 * math.pi * (t - s) / 0.5)))
        fc = faces[(m, b)]
        frame.paste(fc, ((W - CW)//2, CHAR_Y + bob), fc)
        txt = None
        for s, e, ls in subs:
            if s - 0.05 <= t <= e + 0.12: txt = ls
        if txt: draw_sub(frame, txt)
        elif end_layer is not None and t > last_voice_end + 0.1:
            a = min(1.0, (t - last_voice_end - 0.1) / 0.25)
            im = end_layer.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
            frame.paste(im, (0, SUB_TOP - 10), im)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    return total
