# -*- coding: utf-8 -*-
"""HyperFrames版 第1回ショート：素材（顔・ロゴ・背景・音）と HTML（index.html / compositions/*.html）を作る。

使い方: python3 tools/build.py   （hyperframes版/ の中で実行）
- 声は ../fable52版/voice/ の VOICEVOX:春日部つむぎ のWAVと timing.json を再利用（作り直さない）。
- タートルの顔は ../2026-11-20_第1回/turtle_video.py の make_faces / logo_mark を読み込んで使う（相手のファイルは変更しない）。
- 出力はすべて hyperframes版/project/ の中だけ。
"""
import json, math, os, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
PROJ = os.path.join(BASE, "project")
AV = os.path.abspath(os.path.join(BASE, ".."))
VOICE_DIR = os.path.join(AV, "fable52版", "voice")
sys.path.insert(0, os.path.join(AV, "2026-11-20_第1回"))
import turtle_video as tv  # noqa: E402

W, H, FPS, SR = 1080, 1920, 30, 48000
IMG = os.path.join(PROJ, "assets", "img"); AUD = os.path.join(PROJ, "assets", "audio")
os.makedirs(IMG, exist_ok=True); os.makedirs(AUD, exist_ok=True)
os.makedirs(os.path.join(PROJ, "compositions"), exist_ok=True)

# ------------------------------------------------------------------ 秒数表（先に決める）
timing = json.load(open(os.path.join(VOICE_DIR, "timing.json")))
L = {l["key"]: l for l in timing["lines"]}
ORDER = ["intro1", "intro2", "n1a", "n1b", "n1c", "n2a", "n2b", "n2c", "n3a", "n3b", "n3c", "out1", "out2"]
SECTION_START = {"n1a", "n2a", "n3a", "out1"}
HEAD, GAP, GAP_SEC, TAIL = 0.25, 0.25, 0.45, 2.1
start = {}; t = HEAD
for i, k in enumerate(ORDER):
    start[k] = round(t, 3)
    t += L[k]["dur"]
    if i + 1 < len(ORDER):
        t += GAP_SEC if ORDER[i + 1] in SECTION_START else GAP
end = {k: round(start[k] + L[k]["dur"], 3) for k in ORDER}
TOTAL = round(end["out2"] + TAIL, 2)

def boundary(k):  # 前のセリフの終わりと k の始まりの真ん中＝場面の切れ目
    i = ORDER.index(k); return round((end[ORDER[i - 1]] + start[k]) / 2, 3)

SCENES = [("intro", 0.0, boundary("n1a")), ("news1", boundary("n1a"), boundary("n2a")),
          ("news2", boundary("n2a"), boundary("n3a")), ("news3", boundary("n3a"), boundary("out1")),
          ("outro", boundary("out1"), TOTAL)]
SC = {n: (s, e) for n, s, e in SCENES}
def loc(scene, t_abs): return round(t_abs - SC[scene][0], 3)

# 「また来週」の始まり（エンドカードの開始）
bye = start["out2"] + L["out2"]["subs"][1]["s"]

table = ["| 時間（秒） | 場面 | セリフ | 画面の動き |", "|---|---|---|---|"]
ACT = {
    "intro1": "0秒目からタイトル「今週のAIニュース」が画面にある（つかみ）。タートルが手をふる。表示文（AIチームが作っています）",
    "intro2": "「11/20号」スタンプ、①②③が順にポンと出る",
    "n1a": "切り替えのワイプ → ①の数字がポン、見出しカードが横からすべり込む、発表日・出典",
    "n1b": "「最大30%」の数字が0から数え上がる",
    "n1c": "「中小企業なら」ラベル、ふだん→今のAI／むずかしい作業→新しいAI が順に出る",
    "n2a": "ワイプ → ②、見出しカード、発表日・出典",
    "n2b": "「ベータ」のハンコがドンと押される",
    "n2c": "「中小企業なら」＋地図ピンと吹き出しのアイコン",
    "n3a": "ワイプ → ③、見出しカード、「日本を含む6か国」",
    "n3b": "電話アイコンがゆれる＋「※アメリカでの機能」",
    "n3c": "「中小企業なら」＋時計と値札のアイコン",
    "out1": "ワイプ → 「AIは毎週 新しくなっています」、タートルがうなずく",
    "out2": "ロゴ「タートルアド」と「AIの使い方 ご相談受付中」→「また来週」から表示文とクレジット",
}
for k in ORDER:
    scene = next(n for n, s, e in SCENES if s <= start[k] < e)
    text = "".join(c["text"].replace("/", "") for c in L[k]["subs"])
    table.append(f"| {start[k]:.2f}〜{end[k]:.2f} | {scene} | {text} | {ACT[k]} |")
table.append(f"| {end['out2']:.2f}〜{TOTAL:.2f} | outro | （無音） | エンドカードを残す（ロゴ・表示文・VOICEVOX:春日部つむぎ） |")
open(os.path.join(BASE, "秒数表.md"), "w").write(
    "# 秒数表（HyperFrames版 第1回ショート）\n\n"
    f"- 縦1080×1920・30fps・全体 {TOTAL} 秒（声は fable52版/voice の春日部つむぎ・速さ1.25を再利用）\n"
    "- 場面：" + " / ".join(f"{n} {s:.2f}〜{e:.2f}" for n, s, e in SCENES) + "\n\n" + "\n".join(table) + "\n")

# ------------------------------------------------------------------ 画像
faces = tv.make_faces(scale_px=512)
for (m, b), im in faces.items():
    im.save(os.path.join(IMG, f"turtle_m{m}_b{b}.png"))
tv.logo_mark(360).save(os.path.join(IMG, "logo.png"))

def background():
    px = np.zeros((H, W, 3), np.uint8)
    top, bot = (8, 16, 36), (20, 36, 90)
    for i in range(3): px[..., i] = np.linspace(top[i], bot[i], H)[:, None]
    bg = Image.fromarray(px).convert("RGBA"); d = ImageDraw.Draw(bg, "RGBA"); r = 46
    for row in range(-1, int(H / (r * 1.5)) + 2):
        for col in range(-1, int(W / (r * 1.732)) + 2):
            cx = col * r * 1.732 + (row % 2) * r * 0.866; cy = row * r * 1.5
            d.polygon([(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)],
                      outline=(60, 214, 240, 20))
    return bg.convert("RGB")
background().save(os.path.join(IMG, "bg.png"))
g = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((150, 150, 750, 750), fill=(60, 214, 240, 90))
g.filter(ImageFilter.GaussianBlur(120)).save(os.path.join(IMG, "glow.png"))

# ------------------------------------------------------------------ 音（声・効果音・BGM を別々のトラックに）
def read_wav(p):
    with wave.open(p) as f:
        sr = f.getframerate(); a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
    if sr != SR:
        x = np.arange(len(a)) / sr; a = np.interp(np.arange(int(len(a) * SR / sr)) / SR, x, a)
    return a
def write_wav(p, a):
    a = np.clip(a, -1, 1);
    with wave.open(p, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((a * 32767).astype(np.int16).tobytes())
N = int(TOTAL * SR) + SR
voice = np.zeros(N, np.float32)
for k in ORDER:
    a = read_wav(os.path.join(VOICE_DIR, k + ".wav")); i = int(start[k] * SR); voice[i:i + len(a)] += a
write_wav(os.path.join(AUD, "voice.wav"), voice[:int(TOTAL * SR)])

def tone(freq, dur, decay, harm=0.3):
    tt = np.arange(int(SR * dur)) / SR
    env = np.exp(-tt * decay) * np.minimum(1, tt / 0.006)
    return (np.sin(2 * np.pi * freq * tt) + harm * np.sin(2 * np.pi * freq * 2 * tt)) * env
def whoosh(dur=0.55):
    rng = np.random.default_rng(7); n = int(SR * dur); x = rng.standard_normal(n)
    # 簡単なローパス（移動平均の幅を時間で変える）で「シュッ」
    out = np.zeros(n); acc = 0.0
    for i in range(n):
        a = 0.02 + 0.25 * math.sin(math.pi * i / n); acc += a * (x[i] - acc); out[i] = acc
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    return out * env * 0.9
sfx = np.zeros(N, np.float32)
def put(a, t_abs, gain):
    i = int(t_abs * SR); sfx[i:i + len(a)] += a[:max(0, N - i)] * gain
WH = whoosh()
for k in ["n1a", "n2a", "n3a", "out1"]:
    put(WH, boundary(k) - 0.27, 0.22)
    put(tv.chime(), start[k] - 0.02, 0.12)                  # 番号が出る「ポン」
POP = tone(880, 0.18, 30, 0.2)
for t_abs in [start["intro2"] + 0.55 + 0.18 * i for i in range(3)]: put(POP, t_abs, 0.10)   # ①②③
put(tone(140, 0.35, 12, 0.6) + 0.4 * whoosh(0.2)[:int(0.35 * SR)] if False else tone(150, 0.35, 12, 0.6), start["n2b"] + 0.12, 0.35)  # ハンコ「ドン」
for t_abs in [start["n1b"] + 0.25 + 0.06 * i for i in range(10)]: put(tone(1500 + 60 * (t_abs % 1), 0.05, 60, 0.0), t_abs, 0.04)  # 数え上げ「カカカ」
put(tv.chime(1046.5, 0.8), start["out2"] + 0.1, 0.12)
write_wav(os.path.join(AUD, "sfx.wav"), sfx[:int(TOTAL * SR)])

# BGM：自作の静かなアルペジオ（Cmaj7 - Am7 - Fmaj7 - G6、1小節2.4秒）
def note(f): return 440 * 2 ** ((f - 69) / 12)
CHORDS = [[48, 55, 59, 64, 67], [45, 52, 55, 60, 64], [41, 48, 52, 57, 60], [43, 50, 55, 59, 64]]
bgm = np.zeros(N, np.float32); beat = 0.6
for bar in range(int(TOTAL / 2.4) + 2):
    ch = CHORDS[bar % 4]; t0 = bar * 2.4
    pad = tone(note(ch[0] - 12), 2.6, 0.6, 0.15) * 0.35; i = int(t0 * SR); bgm[i:i + len(pad)] += pad[:max(0, N - i)]
    for e in range(8):
        f = note(ch[1 + (e * 3) % 4] + 12); a = tone(f, 0.9, 5.5, 0.12) * (0.32 if e % 2 == 0 else 0.22)
        i = int((t0 + e * beat / 2) * SR); bgm[i:i + len(a)] += a[:max(0, N - i)]
bgm = bgm / np.abs(bgm).max() * 0.5
fade = np.ones(N); fo = int(1.8 * SR); e_i = int(TOTAL * SR); fade[e_i - fo:e_i] = np.linspace(1, 0, fo); fade[e_i:] = 0
fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
write_wav(os.path.join(AUD, "bgm.wav"), (bgm * fade)[:int(TOTAL * SR)])

# ------------------------------------------------------------------ 口パク・まばたき
def mouth_state(v):
    if v in ("a", "o", "e"): return 2
    if v in ("i", "u"): return 1
    return 0
segs = []  # (t, state)
for k in ORDER:
    for a, b, v in L[k]["vis"]:
        s = mouth_state(v)
        if s == 0: continue
        segs.append((start[k] + a, start[k] + b, s))
changes = [(0.0, 0)]
for a, b, s in segs:
    a = round(a * FPS) / FPS; b = round(b * FPS) / FPS
    if b - a < 1 / FPS: b = a + 1 / FPS
    if changes[-1][0] > a: a = changes[-1][0]
    if changes[-1][1] != s: changes.append((a, s))
    changes.append((b, 0))
# 0 に戻ってすぐ同じ形になるところ（1コマ以下）は閉じない
clean = [changes[0]]
for i in range(1, len(changes)):
    tcur, s = changes[i]
    if i + 1 < len(changes) and s == 0 and changes[i + 1][0] - tcur < 1.5 / FPS: continue
    if clean[-1][1] == s: continue
    clean.append((tcur, s))
blinks = [x for x in np.arange(2.6, TOTAL - 0.5, 3.1)] + [0.9]
blinks = sorted(round(b + (0.4 if int(b) % 2 else 0), 2) for b in blinks)
events = sorted([(t_, "m", s) for t_, s in clean] + [(b, "b", 1) for b in blinks] + [(round(b + 0.13, 3), "b", 0) for b in blinks])
mouth_js = []; cur_m, cur_b = 0, 0
for t_, kind, v in events:
    if kind == "m": cur_m = v
    else: cur_b = v
    mouth_js.append(f'[{t_:.3f},"#tm{cur_m}{cur_b}"]')

# ------------------------------------------------------------------ HTML
FONT_CSS = """
    @font-face { font-family: "NotoJP"; src: url("assets/fonts/NotoSansJP-Bold.ttf"); font-weight: 700; }
    @font-face { font-family: "RoundM"; src: url("assets/fonts/RoundedMplus1c-ExtraBold.ttf"); font-weight: 800; }"""
COLORS = """--navy:#08101f; --cyan:#3cd6f0; --yellow:#ffcc4d; --ink:#08101f; --white:#ffffff; --dim:#b9c8e6; --card:rgba(4,7,15,0.86);"""

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

HL = ["Claude Fable 5.2", "最大3割", "ChatGPT", "試験中", "Gemini", "無料", "電話", "最新", "ご相談", "AIニュース", "3つ"]
def highlight(line):
    out = esc(line)
    for w in HL:
        if w in out: out = out.replace(esc(w), f'<span class="hl">{esc(w)}</span>', 1)
    return out

# 字幕（セリフのまとまりごと）
caps = []
for k in ORDER:
    for c in L[k]["subs"]:
        caps.append([start[k] + c["s"], start[k] + c["e"], c["text"]])
for i in range(len(caps)):
    s, e, _ = caps[i]
    caps[i][0] = round(max(0.12, s - 0.04), 3)
    nxt = caps[i + 1][0] - 0.04 if i + 1 < len(caps) else e + 0.6
    caps[i][1] = round(min(nxt, e + 0.3), 3)

cap_html = []; cap_js = []
for i, (s, e, text) in enumerate(caps):
    lines = text.split("/")
    inner = "<br/>".join(highlight(x) for x in lines)
    cap_html.append(f'    <div id="cap{i}" class="clip cap" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="0"><span class="capbox" id="capb{i}">{inner}</span></div>')
    cap_js.append(f"""    tl.fromTo("#capb{i}", {{opacity:0, y:26, scale:0.94}}, {{opacity:1, y:0, scale:1, duration:0.2, ease:"back.out(2)"}}, {s:.3f});
    tl.fromTo("#capb{i} .hl", {{scale:1}}, {{scale:1.12, duration:0.12, yoyo:true, repeat:1, ease:"power2.out"}}, {s + 0.18:.3f});
    tl.to("#capb{i}", {{opacity:0, duration:0.1, ease:"power2.in"}}, {e - 0.1:.3f});
    tl.set("#capb{i}", {{opacity:0, visibility:"hidden"}}, {e:.3f});""")

open(os.path.join(PROJ, "compositions", "captions.html"), "w").write(f"""<template>
  <style>{FONT_CSS}
    #root {{ position:absolute; inset:0; {COLORS} }}
    .cap {{ position:absolute; left:0; right:0; bottom:690px; text-align:center; overflow:visible; }}
    .capbox {{ display:inline-block; padding:20px 40px; border-radius:28px; background:rgba(4,7,15,0.82);
      border:3px solid rgba(60,214,240,0.55); color:#fff; font-family:"NotoJP"; font-weight:700; font-size:54px;
      line-height:1.42; letter-spacing:0.02em; max-width:960px; }}
    .hl {{ color:var(--yellow); display:inline-block; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(cap_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cap_js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
""")

# ---- 場面ごとの共通部品
def scene_file(name, body_html, js, extra_css=""):
    s, e = SC[name]
    open(os.path.join(PROJ, "compositions", f"{name}.html"), "w").write(f"""<template>
  <style>{FONT_CSS}
    #root {{ position:absolute; inset:0; {COLORS} font-family:"NotoJP"; color:#fff; }}
    .card {{ position:absolute; left:60px; right:60px; background:var(--card); border:3px solid var(--cyan); border-radius:34px; }}
    .center {{ display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }}
    .num {{ position:absolute; left:28px; top:22px; width:92px; height:92px; border-radius:50%; background:var(--cyan); color:var(--ink);
      font-family:"RoundM"; font-size:62px; line-height:92px; text-align:center; }}
    .htitle {{ position:absolute; left:142px; right:20px; top:20px; font-size:40px; line-height:1.3; white-space:nowrap; }}
    .hmeta {{ position:absolute; left:142px; right:20px; top:76px; font-size:27px; color:var(--dim); white-space:nowrap; }}
    .big {{ font-size:72px; line-height:1.3; }}
    .tag {{ display:inline-block; background:var(--yellow); color:var(--ink); font-size:34px; padding:6px 26px; border-radius:40px; }}
    .y {{ color:var(--yellow); }}
    .c {{ color:var(--cyan); }}
    .row {{ font-size:46px; line-height:1.25; margin:10px 0; white-space:nowrap; }}
    .small {{ font-size:28px; color:var(--dim); }}
{extra_css}
  </style>
  <div id="root" data-composition-id="{name}" data-width="1080" data-height="1920">
{body_html}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{name}"] = tl;
  </script>
</template>
""")

def beat_js(bid, s, e, kind="up"):
    if kind == "up":
        a = f'tl.fromTo("#{bid}-in", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:0.38, ease:"power3.out"}}, {s:.3f});'
    else:
        a = f'tl.fromTo("#{bid}-in", {{opacity:0, scale:0.8}}, {{opacity:1, scale:1, duration:0.34, ease:"back.out(1.8)"}}, {s:.3f});'
    return a + f'\n    tl.to("#{bid}-in", {{opacity:0, y:-30, duration:0.18, ease:"power2.in"}}, {e - 0.2:.3f});'

BODY_TOP, BODY_H = 520, 260  # 本体カード（y 520〜780）

def header_card(sid, num, title, meta):
    return f"""    <div id="{sid}-head" class="clip" data-start="0" data-duration="{{dur}}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:120px;">
      <div id="{sid}-headin" class="card" style="top:0;height:120px;">
        <div id="{sid}-num" class="num">{num}</div>
        <div id="{sid}-ht" class="htitle">{title}</div>
        <div id="{sid}-hm" class="hmeta">{meta}</div>
      </div>
    </div>"""
def header_js(sid, t0):
    return f"""    tl.fromTo("#{sid}-headin", {{x:900, opacity:0}}, {{x:0, opacity:1, duration:0.45, ease:"expo.out"}}, {t0:.3f});
    tl.fromTo("#{sid}-num", {{scale:0, rotation:-90}}, {{scale:1, rotation:0, duration:0.5, ease:"back.out(2.4)"}}, {t0 + 0.15:.3f});
    tl.fromTo("#{sid}-hm", {{opacity:0}}, {{opacity:1, duration:0.3}}, {t0 + 0.45:.3f});"""

def body_clip(bid, s, e, inner, h=BODY_H, top=BODY_TOP):
    return f"""    <div id="{bid}" class="clip" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="1" style="position:absolute;left:0;top:{top}px;width:1080px;height:{h}px;">
      <div id="{bid}-in" class="card center" style="top:0;height:{h}px;">
{inner}
      </div>
    </div>"""

TIP = '<div class="tag" style="margin-bottom:14px;">中小企業なら</div>'
ICON_PIN = '<svg width="96" height="96" viewBox="0 0 100 100"><path d="M50 6C32 6 18 20 18 38c0 24 32 56 32 56s32-32 32-56C82 20 68 6 50 6z" fill="#ff6b6b"/><circle cx="50" cy="38" r="13" fill="#fff"/></svg>'
ICON_BUB = '<svg width="96" height="96" viewBox="0 0 100 100"><rect x="8" y="12" width="84" height="58" rx="16" fill="#3cd6f0"/><path d="M28 68 L24 90 L48 70z" fill="#3cd6f0"/><text x="50" y="52" font-size="30" text-anchor="middle" fill="#08101f" font-family="RoundM">AI</text></svg>'
ICON_PHONE = '<svg width="110" height="110" viewBox="0 0 100 100"><path d="M30 8c4 0 8 12 10 20 1 4-6 8-6 12 0 8 18 26 26 26 4 0 8-7 12-6 8 2 20 6 20 10 0 6-8 22-22 22C42 92 8 58 8 30 8 16 24 8 30 8z" fill="#3cd6f0"/></svg>'
ICON_CLOCK = '<svg width="96" height="96" viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="none" stroke="#3cd6f0" stroke-width="9"/><path d="M50 24v28l18 12" fill="none" stroke="#ffcc4d" stroke-width="9" stroke-linecap="round"/></svg>'
ICON_TAG = '<svg width="96" height="96" viewBox="0 0 100 100"><path d="M10 14v34l42 42 38-38L48 10H14z" fill="#ffcc4d"/><circle cx="30" cy="30" r="8" fill="#08101f"/><text x="60" y="66" font-size="30" text-anchor="middle" fill="#08101f" font-family="RoundM">¥</text></svg>'

# --- intro
d_intro = SC["intro"][1]
i2 = loc("intro", start["intro2"])
intro_html = f"""    <div id="in-title" class="clip center" data-start="0" data-duration="{d_intro:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:330px;">
      <div id="in-title-in" class="card center" style="top:0;height:330px;">
        <div id="in-kicker" style="font-family:RoundM;font-size:40px;" class="c">AI動画編集部</div>
        <div id="in-t1" style="font-size:104px;line-height:1.15;">今週の<span class="y">AI</span>ニュース</div>
        <div style="margin-top:12px;display:flex;gap:22px;align-items:center;">
          <div id="in-date" class="tag" style="font-size:40px;">11/20号</div>
          <div id="in-d1" class="num" style="position:static;width:70px;height:70px;line-height:70px;font-size:44px;">1</div>
          <div id="in-d2" class="num" style="position:static;width:70px;height:70px;line-height:70px;font-size:44px;">2</div>
          <div id="in-d3" class="num" style="position:static;width:70px;height:70px;line-height:70px;font-size:44px;">3</div>
        </div>
      </div>
    </div>
    <div id="in-disc" class="clip" data-start="0" data-duration="{d_intro:.3f}" data-track-index="1" style="position:absolute;left:0;top:735px;width:1080px;height:150px;">
      <div id="in-disc-in" style="position:absolute;left:90px;right:90px;top:0;padding:16px 24px;background:rgba(4,7,15,0.78);border:2px solid rgba(185,200,230,0.6);border-radius:22px;font-size:30px;line-height:1.5;text-align:center;color:#dfe8fb;">この動画は、タートルアドのAIチームが<br/>情報収集から台本・音声・映像まで作っています</div>
    </div>"""
intro_js = f"""    tl.fromTo("#in-title-in", {{scale:1.08}}, {{scale:1, duration:0.5, ease:"expo.out"}}, 0);
    tl.fromTo("#in-t1", {{letterSpacing:"0.12em"}}, {{letterSpacing:"0em", duration:0.6, ease:"expo.out"}}, 0);
    tl.fromTo("#in-date", {{scale:2.2, opacity:0, rotation:-12}}, {{scale:1, opacity:1, rotation:-4, duration:0.3, ease:"power4.in"}}, 0.35);
    tl.fromTo("#in-d1", {{scale:0}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}, {i2 + 0.55:.3f});
    tl.fromTo("#in-d2", {{scale:0}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}, {i2 + 0.73:.3f});
    tl.fromTo("#in-d3", {{scale:0}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}, {i2 + 0.91:.3f});
    tl.fromTo("#in-disc-in", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, ease:"power2.out"}}, 0.15);
    tl.to("#in-title-in", {{opacity:0, scale:0.96, duration:0.2, ease:"power2.in"}}, {d_intro - 0.22:.3f});
    tl.to("#in-disc-in", {{opacity:0, duration:0.2}}, {d_intro - 0.22:.3f});"""
scene_file("intro", intro_html, intro_js)

def news_scene(name, sid, num, title, meta, keys, beats_html, beats_js_extra, extra_css=""):
    s0, e0 = SC[name]; dur = e0 - s0
    html = [header_card(sid, num, title, meta).replace("{dur}", f"{dur:.3f}")]
    js = [header_js(sid, 0.05)]
    for i, k in enumerate(keys):
        bs = loc(name, start[k]) - (0.1 if i else -0.15)
        be = loc(name, start[keys[i + 1]]) - 0.1 if i + 1 < len(keys) else dur
        bid = f"{sid}-b{i}"
        html.append(body_clip(bid, bs, be, beats_html[i]))
        js.append("    " + beat_js(bid, bs, be, "pop" if i == 1 else "up"))
    js.append(f'    tl.to("#{sid}-headin", {{opacity:0, duration:0.2, ease:"power2.in"}}, {dur - 0.22:.3f});')
    js.append(beats_js_extra(lambda k: loc(name, start[k])))
    scene_file(name, "\n".join(html), "\n".join(js), extra_css)

news_scene("news1", "n1", "1", "新しいAI「Claude Fable 5.2」", "発表 11月9日　｜　出典：Anthropic公式", ["n1a", "n1b", "n1c"], [
    '        <div class="big">新しいAI<br/><span class="y">「Claude Fable 5.2」</span></div>',
    '        <div style="font-size:40px;">答えが出るのが</div><div style="font-size:112px;line-height:1.1;" class="y">最大<span id="n1-count">30</span>%<span style="font-size:72px;color:#fff;">速く</span></div><div class="small">前の型（Fable 5.1）と比べて</div>',
    f'        {TIP}<div id="n1-r1" class="row">ふだん <span class="c">→</span> 今のAI</div><div id="n1-r2" class="row">むずかしい作業 <span class="c">→</span> <span class="y">新しいAI</span></div>',
], lambda t: f"""    const n1c = {{v:0}};
    tl.fromTo(n1c, {{v:0}}, {{v:30, duration:0.7, ease:"power2.out", onUpdate:()=>{{ document.querySelector("#n1-count").textContent = Math.round(n1c.v); }}}}, {t("n1b") + 0.2:.3f});
    tl.fromTo("#n1-r1", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out"}}, {t("n1c") + 0.3:.3f});
    tl.fromTo("#n1-r2", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out"}}, {t("n1c") + L["n1c"]["subs"][1]["s"]:.3f});""")

news_scene("news2", "n2", "2", "ChatGPTで 自分の会社の情報を管理", "発表 11月10日　｜　出典：OpenAI公式X", ["n2a", "n2b", "n2c"], [
    '        <div class="big"><span class="y">ChatGPT</span>で<br/>自分の会社の情報を管理</div>',
    '        <div id="n2-stamp" style="font-family:RoundM;font-size:96px;color:#ff6b6b;border:10px solid #ff6b6b;border-radius:26px;padding:0 40px;line-height:1.3;">ベータ</div><div style="font-size:40px;margin-top:14px;">まだ試験中の機能です</div>',
    f'        {TIP}<div style="display:flex;gap:30px;align-items:center;"><span id="n2-i1">{ICON_PIN}</span><span id="n2-i2">{ICON_BUB}</span><div style="font-size:44px;text-align:left;line-height:1.3;">AIの中の<br/><span class="y">自社の紹介</span>も確認を</div></div>',
], lambda t: f"""    tl.fromTo("#n2-stamp", {{scale:2.6, rotation:-20, opacity:0}}, {{scale:1, rotation:-8, opacity:1, duration:0.22, ease:"power4.in"}}, {t("n2b") + 0.02:.3f});
    tl.fromTo("#n2-i1", {{y:-50, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {t("n2c") + 0.2:.3f});
    tl.fromTo("#n2-i2", {{scale:0}}, {{scale:1, duration:0.35, ease:"back.out(2.5)"}}, {t("n2c") + 0.45:.3f});""", extra_css="    #n2-i1, #n2-i2 { display:inline-block; }")

news_scene("news3", "n3", "3", "Geminiの「タスク」が日本で無料に", "発表 11月17日　｜　出典：Android Authorityほか", ["n3a", "n3b", "n3c"], [
    '        <div class="big" style="font-size:66px;"><span class="y">Gemini</span>の「タスク」が<br/>日本で無料に</div><div id="n3-chip" class="tag" style="margin-top:12px;font-size:32px;">日本を含む6か国</div>',
    f'        <div style="display:flex;gap:26px;align-items:center;"><span id="n3-ph">{ICON_PHONE}</span><div style="font-size:52px;text-align:left;line-height:1.3;">米国では<br/>AIがお店に<span class="y">電話</span>も</div></div><div class="small" style="margin-top:10px;">※アメリカでの機能</div>',
    f'        {TIP}<div style="display:flex;gap:24px;align-items:center;"><span id="n3-i1">{ICON_CLOCK}</span><span id="n3-i2">{ICON_TAG}</span><div style="font-size:44px;text-align:left;line-height:1.3;">営業時間・料金は<br/>いつも<span class="y">最新</span>に</div></div>',
], lambda t: f"""    tl.fromTo("#n3-chip", {{scale:0}}, {{scale:1, duration:0.35, ease:"back.out(2.5)"}}, {t("n3a") + 2.0:.3f});
    tl.fromTo("#n3-ph", {{rotation:-14}}, {{rotation:14, duration:0.08, yoyo:true, repeat:9, ease:"sine.inOut"}}, {t("n3b") + 0.3:.3f});
    tl.fromTo("#n3-i1", {{rotation:-90, opacity:0}}, {{rotation:0, opacity:1, duration:0.45, ease:"back.out(2)"}}, {t("n3c") + 0.2:.3f});
    tl.fromTo("#n3-i2", {{scale:0}}, {{scale:1, duration:0.35, ease:"back.out(2.5)"}}, {t("n3c") + 0.45:.3f});""", extra_css="    #n3-ph, #n3-i1, #n3-i2 { display:inline-block; }")

# --- outro
od = TOTAL - SC["outro"][0]
o2 = loc("outro", start["out2"]); ob = loc("outro", bye)
outro_html = f"""    <div id="o-b0" class="clip" data-start="0.05" data-duration="{o2 - 0.15:.3f}" data-track-index="0" style="position:absolute;left:0;top:{BODY_TOP - 100}px;width:1080px;height:300px;">
      <div id="o-b0-in" class="card center" style="top:0;height:300px;"><div class="big">AIは毎週<br/><span class="y">新しく</span>なっています</div></div>
    </div>
    <div id="o-end" class="clip" data-start="{o2 - 0.05:.3f}" data-duration="{od - o2 + 0.05:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:420px;">
      <div id="o-end-in" class="card center" style="top:0;height:420px;">
        <img id="o-logo" src="assets/img/logo.png" style="width:150px;height:150px;" />
        <div id="o-name" style="font-family:RoundM;font-size:66px;line-height:1.2;">タートルアド</div>
        <div id="o-cta" class="tag" style="font-size:42px;margin-top:14px;">AIの使い方　ご相談受付中</div>
      </div>
    </div>
    <div id="o-disc" class="clip" data-start="{ob - 0.05:.3f}" data-duration="{od - ob + 0.05:.3f}" data-track-index="1" style="position:absolute;left:0;top:822px;width:1080px;height:200px;">
      <div id="o-disc-in" style="position:absolute;left:90px;right:90px;top:0;padding:14px 24px;background:rgba(4,7,15,0.82);border:2px solid rgba(185,200,230,0.6);border-radius:22px;font-size:29px;line-height:1.5;text-align:center;color:#dfe8fb;">この動画は、タートルアドのAIチームが<br/>情報収集から台本・音声・映像まで作っています<br/><span style="color:var(--cyan);">音声：VOICEVOX:春日部つむぎ</span></div>
    </div>"""
outro_js = f"""    tl.fromTo("#o-b0-in", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:0.4, ease:"power3.out"}}, 0.05);
    tl.to("#o-b0-in", {{opacity:0, y:-30, duration:0.18}}, {o2 - 0.3:.3f});
    tl.fromTo("#o-end-in", {{opacity:0, scale:0.85}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(1.6)"}}, {o2:.3f});
    tl.fromTo("#o-logo", {{rotation:-180, scale:0}}, {{rotation:0, scale:1, duration:0.6, ease:"back.out(1.8)"}}, {o2 + 0.1:.3f});
    tl.fromTo("#o-cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.35, ease:"power3.out"}}, {o2 + 0.5:.3f});
    tl.fromTo("#o-cta", {{scale:1}}, {{scale:1.06, duration:0.4, yoyo:true, repeat:3, ease:"sine.inOut"}}, {o2 + 1.2:.3f});
    tl.fromTo("#o-disc-in", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out"}}, {ob:.3f});"""
scene_file("outro", outro_html, outro_js)

# --- index.html（背景・上の帯・タートル・場面・字幕・ワイプ・音）
tstart = 0
turtle_imgs = "\n".join(f'          <img id="tm{m}{b}" src="assets/img/turtle_m{m}_b{b}.png" class="tface" style="opacity:{1 if (m, b) == (0, 0) else 0};" />'
                        for m in (0, 1, 2) for b in (0, 1))
wipes_html = []; wipes_js = []
for i, k in enumerate(["n1a", "n2a", "n3a", "out1"]):
    b = boundary(k); ws = round(b - 0.32, 3)
    wipes_html.append(f'      <div id="wipe{i}" class="clip" data-start="{ws:.3f}" data-duration="0.64" data-track-index="4" style="position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:40;" data-layout-ignore><div id="wipe{i}-a" class="wbar" style="background:var(--cyan);"></div><div id="wipe{i}-b" class="wbar" style="background:var(--navy);"></div></div>')
    wipes_js.append(f"""      tl.fromTo("#wipe{i}-a", {{x:-2400}}, {{x:2400, duration:0.62, ease:"power2.inOut"}}, {ws:.3f});
      tl.fromTo("#wipe{i}-b", {{x:-2600}}, {{x:2200, duration:0.62, ease:"power2.inOut"}}, {ws + 0.04:.3f});""")

scene_hosts = "\n".join(
    f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:10;"></div>'
    for n, s, e in SCENES)
nod_t = start["out1"] + 0.3
idx = f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>{FONT_CSS}
      :root {{ {COLORS} }}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:var(--navy); }}
      #root {{ position:relative; width:100%; height:100%; font-family:"NotoJP"; color:#fff; }}
      #bg {{ position:absolute; inset:0; }}
      #bg img {{ position:absolute; }}
      .tface {{ position:absolute; left:0; top:0; width:330px; height:330px; image-rendering:pixelated; }}
      .wbar {{ position:absolute; top:-400px; width:900px; height:2720px; rotate:18deg; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="bg" data-layout-ignore>
        <img id="bgimg" src="assets/img/bg.png" style="left:0;top:0;width:1080px;height:1920px;" />
        <img id="glow" src="assets/img/glow.png" style="left:90px;top:620px;width:900px;height:900px;" />
      </div>
      <div id="topbar" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="0" style="position:absolute;left:0;top:0;width:1080px;height:370px;z-index:5;">
        <div id="topbar-in" style="position:absolute;left:60px;right:60px;top:150px;height:108px;display:flex;align-items:center;gap:20px;">
          <img src="assets/img/logo.png" style="width:84px;height:84px;" />
          <div style="font-family:RoundM;font-size:38px;line-height:1.15;"><span style="color:var(--cyan);">AI動画編集部</span><br/>今週のAIニュース <span style="color:var(--yellow);">11/20号</span></div>
        </div>
        <div id="band" style="position:absolute;left:90px;right:90px;top:292px;height:68px;border-radius:34px;background:var(--yellow);color:var(--ink);font-size:36px;line-height:68px;text-align:center;">AIが情報収集から動画まで作っています</div>
      </div>
      <div id="turtle" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" style="position:absolute;left:375px;top:745px;width:330px;height:330px;z-index:20;">
        <div id="rig" style="position:absolute;left:0;top:0;width:330px;height:330px;">
{turtle_imgs}
        </div>
      </div>
{scene_hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:30;"></div>
      <div id="credit" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="5" style="position:absolute;left:0;top:1262px;width:1080px;height:44px;text-align:center;font-size:26px;color:var(--dim);z-index:6;">turtle ad ｜ 音声：VOICEVOX:春日部つむぎ</div>
{chr(10).join(wipes_html)}
      <audio id="voice" class="clip" src="assets/audio/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="6" data-volume="1"></audio>
      <audio id="bgm" class="clip" src="assets/audio/bgm.wav" data-start="0" data-duration="{TOTAL}" data-track-index="7" data-volume="0.22"></audio>
      <audio id="sfx" class="clip" src="assets/audio/sfx.wav" data-start="0" data-duration="{TOTAL}" data-track-index="8" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // 背景の光がゆっくり動く
      tl.fromTo("#glow", {{x:-60, y:0, scale:1}}, {{x:60, y:-40, scale:1.12, duration:{TOTAL / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1}}, 0);
      tl.fromTo("#topbar-in", {{y:-30, opacity:0.0}}, {{y:0, opacity:1, duration:0.4, ease:"power3.out"}}, 0);
      tl.fromTo("#band", {{scaleX:0.6}}, {{scaleX:1, duration:0.45, ease:"expo.out"}}, 0);
      // タートル：最初に手をふる（体をゆらす）→ 呼吸 → 最後にうなずく
      tl.fromTo("#rig", {{rotation:0, y:0}}, {{rotation:7, y:-14, duration:0.22, ease:"sine.inOut", yoyo:true, repeat:5, transformOrigin:"50% 90%"}}, 0.05);
      tl.fromTo("#rig", {{scaleY:1}}, {{scaleY:1.025, duration:1.2, ease:"sine.inOut", yoyo:true, repeat:{int((TOTAL - 2) / 1.2) - 1}, transformOrigin:"50% 100%"}}, 1.5);
      tl.fromTo("#rig", {{y:0}}, {{y:16, duration:0.18, ease:"power1.inOut", yoyo:true, repeat:3}}, {nod_t:.3f});
      // 口パク・まばたき（VOICEVOX の音の時刻から作った表）
      const faces = ["#tm00","#tm01","#tm10","#tm11","#tm20","#tm21"];
      const mouth = [{",".join(mouth_js)}];
      for (const [t, id] of mouth) {{ tl.set(faces.filter(f => f !== id), {{opacity:0}}, t); tl.set(id, {{opacity:1}}, t); }}
      // 場面転換のワイプ
{chr(10).join(wipes_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(PROJ, "index.html"), "w").write(idx)
print("TOTAL", TOTAL, "scenes", SCENES, "captions", len(caps), "mouth events", len(mouth_js))
