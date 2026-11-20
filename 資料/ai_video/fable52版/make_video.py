# AI動画編集部 第1回ショート（Fable 5.2版）: 縦1080x1920・30fps
# 使い方: 1) python3 make_voice.py 1.2   2) python3 make_video.py [出力.mp4] [--frames 秒,秒,...（確認用のコマだけ書き出す）]
# 台本: ../2026-11-20_第1回/台本_ショート.md（事実は台本のとおり。足していない）
import json, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CHARS = os.path.join(ROOT, "ai_office", "characters")
OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(HERE, "turtle_ainews_vol1_fable52.mp4")
ONLY = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")] if "--frames" in sys.argv else None
W, H, FPS = 1080, 1920, 30
F9 = os.path.join(HERE, "fonts", "MPLUSRounded1cwght900.ttf")
F8 = os.path.join(HERE, "fonts", "MPLUSRounded1cwght800.ttf")
FD = os.path.join(HERE, "fonts", "DotGothic16.ttf")
_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
def fit(text, p, size, maxw):
    while font(p, size).getlength(text) > maxw and size > 20: size -= 2
    return font(p, size)

NAVY, INK = (8, 16, 36), (6, 11, 24)
CYAN, WHITE, YELLOW, PINK = (60, 214, 240), (255, 255, 255), (255, 204, 77), (255, 159, 196)
MINT, VIOLET = (94, 234, 170), (184, 166, 255)
THEMES = {  # 場面ごとの色（背景の上・下、差し色）
    "intro": ((8, 16, 36), (20, 40, 104), CYAN),
    "n1": ((5, 16, 36), (10, 62, 104), CYAN),
    "n2": ((5, 24, 30), (10, 82, 78), MINT),
    "n3": ((16, 10, 44), (58, 40, 132), VIOLET),
    "outro": ((8, 16, 36), (20, 40, 104), CYAN),
}
DISCLOSE = ["この動画は、タートルアドのAIチームが", "情報収集から台本・音声・映像まで作っています"]

# ---------- 動きの関数 ----------
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
def eo(u): u = clamp(u); return 1 - (1 - u) ** 3                      # すっと止まる
def eb(u):                                                             # 少し行きすぎて戻る
    u = clamp(u); c = 1.70158; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
def ei(u): u = clamp(u); return u ** 3

# ---------- 音声と時刻表 ----------
T = json.load(open(os.path.join(HERE, "voice", "timing.json")))
L = {x["key"]: x for x in T["lines"]}
ORDER = [x["key"] for x in T["lines"]]
SCENE_OF = {"intro1": "intro", "intro2": "intro", "n1a": "n1", "n1b": "n1", "n1c": "n1", "n2a": "n2", "n2b": "n2", "n2c": "n2",
            "n3a": "n3", "n3b": "n3", "n3c": "n3", "out1": "outro", "out2": "outro"}
HEAD, GAP, SGAP, TAIL = 0.55, 0.22, 0.58, 2.7
SR = 24000
st = {}; t = HEAD; cuts = []  # cuts = 場面が切りかわる時刻
for i, k in enumerate(ORDER):
    if i and SCENE_OF[k] != SCENE_OF[ORDER[i - 1]]:
        t += SGAP - GAP; cuts.append((t - SGAP / 2 - 0.03, SCENE_OF[k]))
    st[k] = t; t += L[k]["dur"] + GAP
SPEECH_END = t - GAP
TOTAL = SPEECH_END + TAIL
NF = int(round(TOTAL * FPS))
en = {k: st[k] + L[k]["dur"] for k in ORDER}
def chunk(k, i): return st[k] + L[k]["subs"][i]["s"]   # セリフk の i番目の字幕が始まる時刻
SUBS = [(st[k] + s["s"], st[k] + s["e"], s["text"].split("/")) for k in ORDER for s in L[k]["subs"]]
VIS = [(st[k] + a, st[k] + b, v) for k in ORDER for a, b, v in L[k]["vis"]]
CHUNK_STARTS = [s for s, _, _ in SUBS]
def scene_at(tt):
    s = "intro"
    for c, name in cuts:
        if tt >= c: s = name
    return s
def scene_start(name):
    for c, n in cuts:
        if n == name: return c
    return 0.0

# 効果音（自作：サイン波とノイズだけ）
def tone(freqs, dur, amp, decay=6.0):
    x = np.arange(int(SR * dur)) / SR; y = sum(np.sin(2 * np.pi * f * x) for f in freqs) / len(freqs)
    return y * np.exp(-decay * x) * amp * np.minimum(1, x / 0.005)
def whoosh(dur=0.28, amp=0.05):
    rng = np.random.default_rng(5); n = rng.standard_normal(int(SR * dur))
    n = np.convolve(n, np.ones(24) / 24, mode="same"); x = np.linspace(0, 1, len(n))
    return n * np.sin(np.pi * x) ** 2 * amp * 4
def pop(amp=0.07):
    x = np.arange(int(SR * 0.09)) / SR; f = 700 + 5000 * x
    return np.sin(2 * np.pi * f * x) * np.exp(-30 * x) * amp
sfx = []
def S(tt, kind): sfx.append((tt, kind))
SOUNDS = {"whoosh": whoosh(), "pop": pop(), "ding": tone([1046.5, 1568], 0.6, 0.09), "wipe": whoosh(0.5, 0.06),
          "c": tone([523.25], 0.25, 0.08, 9), "e": tone([659.25], 0.25, 0.08, 9), "g": tone([784], 0.5, 0.08, 6),
          "hi": tone([1046.5, 1318.5], 0.9, 0.08, 4), "stamp": tone([180, 240], 0.2, 0.2, 22)}

def build_audio():
    a = np.zeros(int(SR * TOTAL) + SR, np.float32)
    for k in ORDER:
        with wave.open(L[k]["file"]) as f:
            assert f.getframerate() == SR and f.getnchannels() == 1
            d = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
        i = int(st[k] * SR); a[i:i + len(d)] += d
    for tt, kind in sfx:
        d = SOUNDS[kind]; i = int(max(0, tt) * SR); a[i:i + len(d)] += d[:len(a) - i]
    a = a[:int(SR * TOTAL)]; a = np.clip(a, -1, 1)
    p = os.path.join(HERE, "voice", "mix.wav")
    with wave.open(p, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((a * 32767).astype(np.int16).tobytes())
    return p

# ---------- タートルのドット絵（64x64の格子）と描き足したコマ ----------
def grid(path): return np.array(Image.open(path).convert("RGBA"))[35:480:7, 35:480:7].copy()
G_BASE = grid(os.path.join(CHARS, "single", "leader.png"))
G_TALK = grid(os.path.join(CHARS, "poses", "leader_talk.png"))
A_, E_, F_, I_, M_ = (6, 11, 24, 255), (162, 239, 223, 255), (230, 255, 248, 255), (8, 16, 36, 255), (60, 214, 240, 255)
N_ = (255, 159, 196, 255); CLR = (0, 0, 0, 0)

def body(arm):
    if arm == "down": g = G_BASE.copy(); g[:31] = 0; return g
    g = G_TALK.copy(); hand = g[27:31, 48:].copy(); g[:31] = 0; g[27:31, 48:] = hand   # 吹き出しは使わない
    if arm == "point":   # 描き足し：人さし指を立てて上のカードを指す
        g[22, 52:54] = A_
        for y in range(23, 28): g[y, 51] = A_; g[y, 52] = E_; g[y, 53] = F_; g[y, 54] = A_
    if arm in ("wave1", "wave2"):   # 描き足し：手をふる（手先を左右にずらしたコマ）
        sh = {"wave1": (2, 1), "wave2": (-1, 0)}[arm]
        for rows, dx in ((range(27, 31), sh[0]), (range(31, 34), sh[1])):
            for y in rows:
                seg = g[y, 48:62].copy(); g[y, 48:62] = 0
                g[y, 48 + dx:62 + dx] = np.where(seg[:, 3:4] > 0, seg, g[y, 48 + dx:62 + dx])
    return g

def head(mouth, eyes):
    g = G_BASE.copy(); g[31:] = 0
    g[22:25, 32:38] = I_
    if mouth == 0: g[22, 33] = g[22, 36] = g[23, 34] = g[23, 35] = M_
    elif mouth == 1: g[22:24, 34:36] = M_
    elif mouth == 2: g[22:24, 33:37] = M_; g[23, 34:36] = N_
    else: g[22:25, 33:37] = M_; g[23:25, 34:36] = N_
    if eyes != "open":
        for ex in (28, 37):
            g[16:21, ex:ex + 3] = I_
            if eyes == "blink": g[19, ex:ex + 3] = M_
            else: g[18, ex] = g[17, ex + 1] = g[18, ex + 2] = M_; g[19, ex] = g[19, ex + 2] = M_   # にっこり目
    return g

_sc = {}
def sprite(arm, mouth, eyes, nod, n):
    key = (arm, mouth, eyes, nod, n)
    if key not in _sc:
        g = body(arm); h = head(mouth, eyes)
        hs = np.zeros_like(h); hs[nod:31 + nod] = h[:31]
        g = np.where(hs[:, :, 3:4] > 0, hs, g)
        _sc[key] = Image.fromarray(np.kron(g, np.ones((n, n, 1), np.uint8)), "RGBA")
    return _sc[key]
MATES = [Image.fromarray(np.kron(grid(os.path.join(CHARS, "single", m + ".png")), np.ones((3, 3, 1), np.uint8)), "RGBA")
         for m in ("sales", "listing", "design", "automation", "research")]

random.seed(7); BLINKS = []; bt = 1.6
while bt < TOTAL: BLINKS.append(bt); bt += random.uniform(2.4, 4.2)

def mouth_at(tt):
    prev_end = -9
    for a, b, v in VIS:
        if a <= tt < b:
            if v in "aA": return 3
            if v in "oOeE": return 2
            if v in "iIuU": return 1
            return 0
        if b <= tt: prev_end = b
        elif a > tt: return 1 if (a - tt < 0.07 and tt - prev_end < 0.07) else 0
    return 0

# ---------- 部品づくり ----------
def put(fr, img, x, y, a=1.0):
    if a <= 0.01: return
    if a < 0.995: fr.paste(img, (int(x), int(y)), img.getchannel("A").point(lambda v: int(v * a)))
    else: fr.paste(img, (int(x), int(y)), img)
def put_c(fr, img, cx, cy, s=1.0, a=1.0, rot=0):   # 中心そろえ・拡大縮小つき
    if s <= 0.02: return
    if abs(s - 1) > 0.01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BICUBIC)
    if rot: img = img.rotate(rot, Image.BICUBIC, expand=True)
    put(fr, img, cx - img.width / 2, cy - img.height / 2, a)

PM = 44  # カード画像のまわりの余白
def panel(w, h, accent, r=40):
    im = Image.new("RGBA", (w + PM * 2, h + PM * 2), CLR); d = ImageDraw.Draw(im)
    d.rounded_rectangle((PM + 12, PM + 12, PM + w + 12, PM + h + 12), r, fill=tuple(int(c * 0.45) for c in accent) + (255,))  # ドット絵ふうの影
    d.rounded_rectangle((PM, PM, PM + w, PM + h), r, fill=INK + (244,), outline=accent, width=6)
    return im, d
def text_sh(d, xy, s, f, fill, anchor="mm", sh=(4, 4), shc=(0, 0, 0)):
    d.text((xy[0] + sh[0], xy[1] + sh[1]), s, font=f, fill=shc, anchor=anchor); d.text(xy, s, font=f, fill=fill, anchor=anchor)
def pill(text, f, fg, bg, padx=34, pady=14, outline=None):
    w = int(f.getlength(text)) + padx * 2; h = f.size + pady * 2
    im = Image.new("RGBA", (w, h), CLR); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=bg, outline=outline, width=4 if outline else 0)
    d.text((w / 2, h / 2 - 2), text, font=f, fill=fg, anchor="mm"); return im
def badge(num, accent, r):
    im = Image.new("RGBA", (r * 2 + 16, r * 2 + 16), CLR); d = ImageDraw.Draw(im)
    d.ellipse((10, 10, r * 2 + 10, r * 2 + 10), fill=tuple(int(c * 0.45) for c in accent)); d.ellipse((0, 0, r * 2, r * 2), fill=accent, outline=WHITE, width=max(4, r // 14))
    d.text((r, r - r * 0.06), str(num), font=font(F9, int(r * 1.3)), fill=INK, anchor="mm"); return im
def ss(w, h, draw):   # なめらかな絵（3倍で描いて縮める）
    im = Image.new("RGBA", (w * 3, h * 3), CLR); draw(ImageDraw.Draw(im), 3); return im.resize((w, h), Image.LANCZOS)
def arrow(w, h, col):
    return ss(w, h, lambda d, k: d.polygon([(0, h * k * .32), (w * k * .55, h * k * .32), (w * k * .55, 0), (w * k, h * k * .5), (w * k * .55, h * k), (w * k * .55, h * k * .68), (0, h * k * .68)], fill=col))
def tab_sme():   # 「中小企業なら」の札
    f = font(F9, 46); t = "中小企業なら"; w = int(f.getlength(t)) + 76; h = 84
    im = Image.new("RGBA", (w + 8, h + 8), CLR); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, w + 7, h + 7), 20, fill=(120, 84, 0)); d.rounded_rectangle((0, 0, w - 1, h - 1), 20, fill=YELLOW, outline=INK, width=4)
    d.text((w / 2, h / 2 - 3), t, font=f, fill=INK, anchor="mm"); return im
TAB = tab_sme()

def icon_pin(col, s=190):
    def dr(d, k):
        c = s * k / 2; r = s * k * 0.34
        d.polygon([(c - r * 0.82, c * 0.95), (c + r * 0.82, c * 0.95), (c, s * k * 0.97)], fill=col)
        d.ellipse((c - r, c * 0.72 - r, c + r, c * 0.72 + r), fill=col); d.ellipse((c - r * .42, c * .72 - r * .42, c + r * .42, c * .72 + r * .42), fill=INK)
    return ss(s, s, dr)
def icon_bubble(col, s=190):
    def dr(d, k):
        S_ = s * k
        d.rounded_rectangle((S_ * .06, S_ * .1, S_ * .94, S_ * .72), S_ * .16, fill=col)
        d.polygon([(S_ * .26, S_ * .68), (S_ * .2, S_ * .95), (S_ * .5, S_ * .68)], fill=col)
        d.text((S_ * .5, S_ * .4), "AI", font=font(F9, int(S_ * .4)), fill=INK, anchor="mm")
    return ss(s, s, dr)
def icon_phone(col, s=230):
    def dr(d, k):
        S_ = s * k
        d.arc((S_ * .14, S_ * .2, S_ * .86, S_ * .92), 200, 340, fill=col, width=int(S_ * .15))
        for ang in (203, 337):
            cx = S_ * .5 + S_ * .30 * math.cos(math.radians(ang)); cy = S_ * .56 + S_ * .30 * math.sin(math.radians(ang))
            d.rounded_rectangle((cx - S_ * .13, cy - S_ * .09, cx + S_ * .13, cy + S_ * .17), S_ * .06, fill=col)
    return ss(s, s, dr).rotate(-28, Image.BICUBIC)
def icon_tag(col, s=190):
    def dr(d, k):
        S_ = s * k
        d.polygon([(S_ * .08, S_ * .5), (S_ * .34, S_ * .2), (S_ * .92, S_ * .2), (S_ * .92, S_ * .8), (S_ * .34, S_ * .8)], fill=col)
        d.ellipse((S_ * .2, S_ * .44, S_ * .32, S_ * .56), fill=INK)
        d.text((S_ * .63, S_ * .49), "¥", font=font(F9, int(S_ * .42)), fill=INK, anchor="mm")
    return ss(s, s, dr).rotate(18, Image.BICUBIC)
def icon_clock(col, s=190):
    def dr(d, k):
        S_ = s * k; d.ellipse((S_ * .06, S_ * .06, S_ * .94, S_ * .94), fill=INK, outline=col, width=int(S_ * .08))
        for i in range(12):
            a = math.radians(i * 30); r1, r2 = S_ * .33, S_ * .38
            d.line((S_ / 2 + r1 * math.cos(a), S_ / 2 + r1 * math.sin(a), S_ / 2 + r2 * math.cos(a), S_ / 2 + r2 * math.sin(a)), fill=col, width=int(S_ * .025))
    return ss(s, s, dr)
def icon_check(s=90):
    return ss(s, s, lambda d, k: (d.ellipse((0, 0, s * k - 1, s * k - 1), fill=YELLOW), d.line([(s * k * .24, s * k * .52), (s * k * .44, s * k * .72), (s * k * .78, s * k * .3)], fill=INK, width=int(s * k * .12), joint="curve")))

# ---------- 背景 ----------
def make_bg(top, bot, accent):
    px = np.zeros((H, W, 3), np.float32)
    for i in range(3): px[..., i] = np.linspace(top[i], bot[i], H)[:, None]
    im = Image.fromarray(px.astype(np.uint8)).convert("RGBA"); ov = Image.new("RGBA", (W, H), CLR); d = ImageDraw.Draw(ov)
    r = 52
    for row in range(-1, int(H / (r * 1.5)) + 2):
        for col in range(-1, int(W / (r * 1.732)) + 2):
            cx = col * r * 1.732 + (row % 2) * r * 0.866; cy = row * r * 1.5
            d.polygon([(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)], outline=accent + (20,))
    im = Image.alpha_composite(im, ov)
    gl = Image.new("RGBA", (W, H), CLR); gd = ImageDraw.Draw(gl)
    gd.ellipse((-200, 900, 700, 1700), fill=accent + (50,)); gd.ellipse((500, 150, 1300, 900), fill=accent + (28,))
    return Image.alpha_composite(im, gl.filter(ImageFilter.GaussianBlur(140))).convert("RGB")
BG = {k: make_bg(*v) for k, v in THEMES.items()}
random.seed(11)
PART = [(random.uniform(0, W), random.uniform(0, H), random.uniform(18, 60), random.choice([6, 8, 10, 14]), random.uniform(40, 95)) for _ in range(30)]

# いつも出ている帯と番組名
TOPBAR = Image.new("RGBA", (W, 260), CLR); _d = ImageDraw.Draw(TOPBAR)
_d.rounded_rectangle((40, 56, W - 40, 130), 37, fill=YELLOW + (255,), outline=INK, width=4)
_d.text((W / 2, 91), "AIが情報収集から動画まで作っています", font=font(F9, 42), fill=INK, anchor="mm")
_d.text((56, 172), "AI動画編集部", font=font(FD, 36), fill=CYAN, anchor="lm")
_d.text((56, 220), "今週のAIニュース", font=font(F9, 44), fill=WHITE, anchor="lm")
_p = pill("11/20号", font(F9, 30), INK, CYAN, 20, 8); TOPBAR.alpha_composite(_p, (56 + int(font(F9, 44).getlength("今週のAIニュース")) + 18, 198))
CREDIT = "turtle ad ｜ 音声 VOICEVOX:春日部つむぎ"

# ---------- カード ----------
CARDS = []   # dict(img, x, y, t0, t1, extra, frm)
def add(img, x, y, t0, t1, extra=None, frm="right", snd="whoosh"):
    CARDS.append(dict(img=img, x=x - PM, y=y - PM, t0=t0, t1=t1, extra=extra, frm=frm))
    if snd: S(t0, snd)
CX, CW_ = 50, 980

NEWS = {
    "n1": dict(num=1, head=["新しいAI", "「Claude Fable 5.2」"], chip="Anthropicが発表", date="11月9日", src="出典：Anthropic公式", short="新しいAI「Claude Fable 5.2」"),
    "n2": dict(num=2, head=["ChatGPTで", "自分の会社の情報を管理"], chip="新しい仕組みがスタート", date="11月10日", src="出典：OpenAI公式X", short="ChatGPTで自分の会社の情報を管理"),
    "n3": dict(num=3, head=["Geminiの「タスク」が", "日本で無料に"], chip="日本を含む6か国", date="11月17日", src="出典：Android Authorityほか", short="Geminiの「タスク」が日本で無料に"),
}
def head_card(sc):
    n = NEWS[sc]; acc = THEMES[sc][2]; im, d = panel(CW_, 640, acc)
    im.alpha_composite(badge(n["num"], acc, 92), (PM + 44, PM + 40))
    d.text((PM + 262, PM + 96), "NEWS", font=font(FD, 64), fill=acc, anchor="lm")
    d.text((PM + 262, PM + 168), f"{n['num']} / 3", font=font(FD, 50), fill=WHITE, anchor="lm")
    for i in range(14): d.rectangle((PM + 470 + i * 34, PM + 124, PM + 470 + i * 34 + 18, PM + 142), fill=acc + (255 - i * 16,))
    for i, ln in enumerate(n["head"]):
        text_sh(d, (PM + CW_ / 2, PM + 318 + i * 122), ln, fit(ln, F9, 96, CW_ - 90), YELLOW if i else WHITE, sh=(5, 5), shc=tuple(int(c * 0.4) for c in acc))
    p = pill(n["chip"], font(F8, 40), INK, acc, 30, 12); im.alpha_composite(p, (PM + (CW_ - p.width) // 2, PM + 536))
    return im
def bar_card(sc):
    n = NEWS[sc]; acc = THEMES[sc][2]; im, d = panel(CW_, 112, acc, 30)
    im.alpha_composite(badge(n["num"], acc, 40), (PM + 18, PM + 14))
    d.text((PM + 122, PM + 54), n["short"], font=fit(n["short"], F9, 52, CW_ - 150), fill=WHITE, anchor="lm"); return im
def info_card(sc):
    n = NEWS[sc]; acc = THEMES[sc][2]; im, d = panel(470, 300, acc, 30)
    p = pill("発表日", font(F8, 34), INK, acc, 24, 8); im.alpha_composite(p, (PM + 30, PM + 28))
    d.text((PM + 235, PM + 150), n["date"], font=font(F9, 96), fill=WHITE, anchor="mm")
    d.line((PM + 30, PM + 218, PM + 440, PM + 218), fill=acc + (120,), width=3)
    d.text((PM + 235, PM + 256), n["src"], font=fit(n["src"], F8, 34, 420), fill=(205, 220, 240), anchor="mm"); return im
def stage(sc, tab=False, h=520):
    im, d = panel(CW_, h, THEMES[sc][2])
    if tab: im.alpha_composite(TAB, (PM + 34, PM - 36))
    return im, d
SY, SH_ = 418, 520   # 下の段のカードの位置

def news_cards(sc):   # ニュース1本ぶんのカード
    acc = THEMES[sc][2]; a, b, c = sc + "a", sc + "b", sc + "c"; t_in = scene_start(sc) + 0.1; t_end = [x for x, _ in cuts if x > t_in][0]
    add(head_card(sc), CX, 280, t_in, st[b] - 0.12, snd="ding")
    add(bar_card(sc), CX, 280, st[b] - 0.1, t_end, frm="top", snd=None)
    add(info_card(sc), 566, 1030, t_in + 0.25, t_end, frm="right", snd=None)
    if sc == "n1":
        im, d = stage(sc)
        d.text((PM + CW_ / 2, PM + 78), "答えが出るのが", font=font(F9, 62), fill=WHITE, anchor="mm")
        d.text((PM + CW_ / 2, PM + 458), "※前の型（Fable 5.1）と比べて", font=font(F8, 36), fill=(205, 220, 240), anchor="mm")
        tc = st[b] + L[b]["dur"] * 0.3
        def ex(fr, ox, oy, tl, tt, tc=tc):
            d2 = ImageDraw.Draw(fr); u = clamp((tt - tc) / 0.5); v = int(round(30 * eo(u))) if tt > tc else 0
            for i in range(7):    # 速さの線
                yy = oy + PM + 150 + i * 42; xx = ox + PM + 40 + ((tt * (420 + i * 60) + i * 173) % 900)
                d2.rounded_rectangle((xx, yy, xx + 70 + i * 9, yy + 8), 4, fill=(22, 84, 110))
            sc_ = 1 + 0.12 * math.sin(math.pi * clamp((tt - tc - 0.5) / 0.25)) if tt > tc + 0.5 else 1
            f1 = font(F9, int(210 * sc_)); f0 = font(F9, 84); s = f"{v}%"
            wn = f1.getlength(s); w0 = f0.getlength("最大"); w2 = f0.getlength("速く"); x0 = ox + PM + (CW_ - (w0 + wn + w2 + 30)) / 2; yb = oy + PM + 355
            d2.text((x0, yb), "最大", font=f0, fill=WHITE, anchor="ls")
            d2.text((x0 + w0 + 15 + 6, yb + 6), s, font=f1, fill=(120, 84, 0), anchor="ls"); d2.text((x0 + w0 + 15, yb), s, font=f1, fill=YELLOW, anchor="ls")
            d2.text((x0 + w0 + wn + 30, yb), "速く", font=f0, fill=WHITE, anchor="ls")
        S(tc + 0.5, "ding"); add(im, CX, SY, st[b] - 0.05, st[c] - 0.12, ex)
        im, d = stage(sc, True)
        text_sh(d, (PM + CW_ / 2, PM + 112), "使い分けがコツ", font(F9, 72), YELLOW)
        rows = [("ふだんの仕事", "今のAI", st[c] + 0.15), ("むずかしい作業", "新しいAI", chunk(c, 1))]
        def mk(l, r):
            rim = Image.new("RGBA", (900, 130), CLR); rd = ImageDraw.Draw(rim)
            rd.rounded_rectangle((0, 0, 440, 124), 24, fill=(22, 44, 80), outline=acc, width=4); rd.text((220, 58), l, font=fit(l, F9, 52, 400), fill=WHITE, anchor="mm")
            rim.alpha_composite(arrow(90, 70, YELLOW), (462, 28))
            rd.rounded_rectangle((574, 0, 899, 124), 24, fill=acc); rd.text((736, 58), r, font=fit(r, F9, 56, 290), fill=INK, anchor="mm"); return rim
        rimg = [mk(l, r) for l, r, _ in rows]
        def ex(fr, ox, oy, tl, tt):
            for i, (_, _, t0) in enumerate(rows):
                u = (tt - t0) / 0.3
                if u > 0: put(fr, rimg[i], ox + PM + 40 + (1 - eo(u)) * 120, oy + PM + 190 + i * 158, clamp(u * 1.5))
        for _, _, t0 in rows: S(t0, "pop")
        add(im, CX, SY, st[c] - 0.05, t_end, ex)
    if sc == "n2":
        im, d = stage(sc)
        d.text((PM + CW_ / 2, PM + 430), "まだ試験中の機能", font=font(F9, 68), fill=WHITE, anchor="mm")
        stp = Image.new("RGBA", (560, 250), CLR); sd = ImageDraw.Draw(stp)
        sd.rounded_rectangle((6, 6, 553, 243), 34, outline=YELLOW, width=14); sd.rounded_rectangle((30, 30, 529, 219), 20, outline=YELLOW, width=5)
        sd.text((280, 120), "ベータ", font=font(F9, 140), fill=YELLOW, anchor="mm"); stp = stp.rotate(7, Image.BICUBIC, expand=True)
        ts = st[b] + 0.3
        def ex(fr, ox, oy, tl, tt):
            u = (tt - ts) / 0.22
            if u > 0: put_c(fr, stp, ox + PM + CW_ / 2, oy + PM + 205, 2.4 - 1.4 * eo(u), clamp(u * 2))
        S(ts + 0.18, "stamp"); add(im, CX, SY, st[b] - 0.05, st[c] - 0.12, ex)
        im, d = stage(sc, True)
        pin, bub, chk = icon_pin(YELLOW), icon_bubble(acc), icon_check(84)
        lab = [("Googleマップ", 255), ("AIの中", 725)]; cap = "AIの中の自社の紹介も確認を"
        tp = [chunk(c, 0) + 0.1, chunk(c, 1) + 0.1, chunk(c, 2)]
        def ex(fr, ox, oy, tl, tt):
            d2 = ImageDraw.Draw(fr)
            for i, ic in enumerate((pin, bub)):
                u = (tt - tp[i]) / 0.3
                if u > 0:
                    put_c(fr, ic, ox + PM + lab[i][1], oy + PM + 190 + 6 * math.sin(tt * 3 + i), eb(u))
                    d2.text((ox + PM + lab[i][1], oy + PM + 322), lab[i][0], font=font(F9, 50), fill=WHITE, anchor="mm")
            if tt > tp[1]: d2.text((ox + PM + 490, oy + PM + 196), "も", font=font(F9, 84), fill=acc, anchor="mm")
            u = (tt - tp[2]) / 0.3
            if u > 0:
                f = fit(cap, F9, 56, 780); wc = f.getlength(cap)
                d2.rounded_rectangle((ox + PM + 40, oy + PM + 380, ox + PM + CW_ - 40, oy + PM + 484), 30, fill=(18, 64, 60))
                put_c(fr, chk, ox + PM + 112, oy + PM + 432, eb(u)); d2.text((ox + PM + 170 + (760 - wc) / 2, oy + PM + 429), cap, font=f, fill=YELLOW, anchor="lm")
        for x in tp: S(x, "pop")
        add(im, CX, SY, st[c] - 0.05, t_end, ex)
    if sc == "n3":
        im, d = stage(sc)
        d.text((PM + 400, PM + 96), "米国では", font=font(F9, 60), fill=acc, anchor="lm")
        text_sh(d, (PM + 400, PM + 208), "AIがお店に", font(F9, 96), WHITE, anchor="lm"); text_sh(d, (PM + 400, PM + 326), "電話も", font(F9, 96), YELLOW, anchor="lm")
        p = pill("※アメリカでの機能", font(F9, 40), INK, YELLOW, 30, 10); im.alpha_composite(p, (PM + (CW_ - p.width) // 2, PM + 420))
        ph = icon_phone(acc, 250)
        def ex(fr, ox, oy, tl, tt):
            d2 = ImageDraw.Draw(fr); cx, cy = ox + PM + 210, oy + PM + 215; ring = (tl % 1.3) < 0.7
            put_c(fr, ph, cx, cy, 1, 1, rot=9 * math.sin(tt * 38) if ring else 0)
            if ring:
                for i in range(3):
                    if (tl % 1.3) > i * 0.12: d2.arc((cx + 40 - i * 26, cy - 190 - i * 26, cx + 190 + i * 26, cy - 40 + i * 26), 285, 345, fill=YELLOW, width=9)
        add(im, CX, SY, st[b] - 0.05, st[c] - 0.12, ex)
        im, d = stage(sc, True)
        ck, tg = icon_clock(acc, 200), icon_tag(YELLOW, 200)
        tp = [chunk(c, 1) - 0.15, chunk(c, 1) + 0.25, chunk(c, 1) + 0.9]
        d.text((PM + 255, PM + 322), "営業時間", font=font(F9, 54), fill=WHITE, anchor="mm"); d.text((PM + 725, PM + 322), "料金", font=font(F9, 54), fill=WHITE, anchor="mm")
        cap = pill("いつも最新に", font(F9, 68), INK, YELLOW, 50, 12)
        def ex(fr, ox, oy, tl, tt):
            d2 = ImageDraw.Draw(fr); cx, cy = ox + PM + 255, oy + PM + 182
            put_c(fr, ck, cx, cy, eb((tt - st[c] - 0.1) / 0.3) if tt < st[c] + 0.5 else 1)
            if tt > st[c] + 0.4:
                for ang, ln, wd in ((tt * 2.2, 62, 10), (tt * 0.35, 42, 13)):
                    d2.line((cx, cy, cx + ln * math.sin(ang), cy - ln * math.cos(ang)), fill=WHITE, width=wd)
                d2.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=YELLOW)
            put_c(fr, tg, ox + PM + 725, oy + PM + 182 + 5 * math.sin(tt * 3), eb((tt - st[c] - 0.25) / 0.3) if tt < st[c] + 0.65 else 1)
            u = (tt - tp[2]) / 0.3
            if u > 0: put_c(fr, cap, ox + PM + CW_ / 2, oy + PM + 430, eb(u))
        S(st[c] + 0.1, "pop"); S(st[c] + 0.25, "pop"); S(tp[2], "ding")
        add(im, CX, SY, st[c] - 0.05, t_end, ex)


def build_cards():
    # --- はじめ ---
    im, d = panel(CW_, 360, CYAN)
    text_sh(d, (PM + CW_ / 2, PM + 118), "今週のAIニュース", font(F9, 108), WHITE, sh=(6, 6), shc=(18, 80, 110))
    p = pill("11/20号", font(F9, 54), INK, YELLOW, 34, 12); im.alpha_composite(p, (PM + 110, PM + 232))
    b0 = [badge(i, c, 52) for i, c in ((1, CYAN), (2, MINT), (3, VIOLET))]
    t3 = st["intro2"] + L["intro2"]["subs"][0]["s"] + L["intro2"]["dur"] * 0.48
    def ex(fr, ox, oy, tl, tt):
        for i in range(3):
            u = (tt - t3 - i * 0.16) / 0.3
            if u > 0: put_c(fr, b0[i], ox + PM + 540 + i * 140, oy + PM + 272, eb(u))
    for i in range(3): S(t3 + i * 0.16, "pop")
    add(im, CX, 290, st["intro2"] - 0.05, cuts[0][0], ex, frm="top")
    for i, kk in enumerate("ceg"): S(0.08 + i * 0.13, kk)

    for sc in ("n1", "n2", "n3"): news_cards(sc)

    # --- しめ ---
    t0 = scene_start("outro") + 0.1
    im, d = panel(CW_, 360, CYAN)
    text_sh(d, (PM + CW_ / 2, PM + 118), "AIは毎週", font(F9, 104), WHITE, sh=(6, 6), shc=(18, 80, 110))
    text_sh(d, (PM + CW_ / 2, PM + 250), "新しくなっています", font(F9, 92), YELLOW, sh=(6, 6), shc=(110, 78, 0))
    add(im, CX, 290, t0, st["out2"] - 0.12)
    im, d = panel(CW_, 430, CYAN)
    logo = Image.open(os.path.join(ROOT, "googlemap_logo.png")).convert("RGBA").resize((190, 190), Image.LANCZOS)
    mk = Image.new("L", (190, 190), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, 189, 189), 40, fill=255); logo.putalpha(mk)
    im.alpha_composite(logo, (PM + 62, PM + 48)); d.rounded_rectangle((PM + 62, PM + 48, PM + 251, PM + 237), 40, outline=CYAN, width=5)
    text_sh(d, (PM + 290, PM + 116), "タートルアド", font(F9, 104), WHITE, anchor="lm", sh=(5, 5), shc=(18, 80, 110))
    d.text((PM + 294, PM + 204), "turtle ad", font=font(FD, 52), fill=CYAN, anchor="lm")
    p = pill("AIの使い方 ご相談受付中", font(F9, 62), INK, YELLOW, 44, 16); im.alpha_composite(p, (PM + (CW_ - p.width) // 2, PM + 292))
    add(im, CX, 280, st["out2"] - 0.05, TOTAL + 9, snd="hi")
build_cards()

DISC = Image.new("RGBA", (980, 150), CLR); _d = ImageDraw.Draw(DISC)
_d.rounded_rectangle((0, 0, 979, 149), 28, fill=INK + (235,), outline=YELLOW, width=4)
for i, ln in enumerate(DISCLOSE): _d.text((490, 46 + i * 56), ln, font=fit(ln, F8, 40, 920), fill=WHITE, anchor="mm")
END = Image.new("RGBA", (980, 250), CLR); _d = ImageDraw.Draw(END)
_d.rounded_rectangle((0, 0, 979, 249), 28, fill=INK + (240,), outline=YELLOW, width=4)
for i, ln in enumerate(DISCLOSE): _d.text((490, 50 + i * 58), ln, font=fit(ln, F8, 42, 920), fill=WHITE, anchor="mm")
_d.line((40, 150, 940, 150), fill=YELLOW + (140,), width=3)
_d.text((490, 198), "音声　VOICEVOX:春日部つむぎ", font=font(F9, 46), fill=CYAN, anchor="mm")

# ---------- 1コマを描く ----------
SUBF = 56
def draw_sub(fr, tt, acc):
    for s, e, lines in SUBS:
        if s - 0.03 <= tt < e + (0.12 if e >= SPEECH_END - 0.01 else 0.0) or (s <= tt < e + 0.2 and not any(s2 - 0.03 <= tt < e2 for s2, e2, _ in SUBS if s2 > s)):
            u = eo((tt - s + 0.03) / 0.14); f = font(F9, SUBF)
            while max(f.getlength(l) for l in lines) > 930: f = font(F9, f.size - 2)
            lh = 80; cy = 1552; top = cy - (len(lines) - 1) * lh / 2; dy = (1 - u) * 16
            d = ImageDraw.Draw(fr, "RGBA")
            d.rounded_rectangle((40, 1458 + dy, W - 40, 1646 + dy), 30, fill=INK + (int(232 * u),), outline=acc + (int(255 * u),), width=4)
            for i, l in enumerate(lines):
                d.text((W / 2, top + i * lh + dy - 3), l, font=f, fill=WHITE + (int(255 * u),), anchor="mm", stroke_width=2, stroke_fill=INK + (int(255 * u),))
            return

def arm_state(tt, sc):
    if sc == "intro":
        if tt < en["intro1"] + 0.35: return ("wave2", "up", "wave1", "up")[int(tt * 7) % 4]
        if tt >= st["intro2"]: return "point" if tt - st["intro2"] < 0.9 else "up"
        return "down"
    if sc == "outro":
        tb = chunk("out2", 1) - 0.1
        if tt >= tb and tt < TOTAL - 0.5: return ("wave2", "up", "wave1", "up")[int(tt * 7) % 4]
        if st["out2"] <= tt < tb: return "point" if tt - st["out2"] < 0.9 else "up"
        return "down"
    last = max([c for c in CHUNK_STARTS if c <= tt + 0.05] or [-9]); dt = tt - last
    if dt < 0.85: return "point"
    if dt < 2.0: return "up"
    return "down"

def render(i):
    tt = i / FPS; sc = scene_at(tt); acc = THEMES[sc][2]
    # 背景（場面の切りかわりで色が変わる）
    fr = BG[sc].copy()
    d = ImageDraw.Draw(fr, "RGBA")
    for x, y, v, s, a in PART:
        yy = (y - v * tt) % (H + 40) - 20; xx = x + 14 * math.sin(tt * 0.7 + y)
        d.rectangle((xx, yy, xx + s, yy + s), fill=acc + (int(a),))
    # カード
    for c in CARDS:
        if not (c["t0"] <= tt < c["t1"] + 0.25): continue
        tl = tt - c["t0"]; u = eb(tl / 0.38) if c["frm"] != "top" else eo(tl / 0.3); ox, oy = c["x"], c["y"]; a = clamp(tl / 0.15)
        if c["frm"] == "right": ox += (1 - u) * 1100
        else: oy -= (1 - u) * 90
        if tt > c["t1"]:
            v = ei((tt - c["t1"]) / 0.25); ox -= v * 1150; a = 1 - v
        put(fr, c["img"], ox, oy, a)
        if c["extra"] and tt <= c["t1"]: c["extra"](fr, ox, oy, tl, tt)
    # タートル
    mouth = mouth_at(tt); blink = any(0 <= tt - b < 0.12 for b in BLINKS)
    arm = arm_state(tt, sc); eyes = "blink" if blink else "open"; nod = 0; hop = 0
    if sc == "intro" and tt < en["intro1"] + 0.3: eyes = "happy"
    if sc == "outro" and tt >= chunk("out2", 1) - 0.1: eyes = "happy"
    for k in ORDER:   # セリフの終わりに軽くうなずく
        if SCENE_OF[k] in ("n1", "n2", "n3") and -0.05 <= tt - en[k] < 0.22: nod = 1
    if sc == "outro" and st["out1"] <= tt < st["out2"]:   # 「毎週のように新しく」で大きくうなずく
        ph = (tt - st["out1"] - 0.5) / 0.55
        if 0 <= ph < 3: nod = (0, 2, 1, 0)[int((ph % 1) * 4)] if ph % 1 < 0.75 else 0
    for cs in CHUNK_STARTS:
        if 0 <= tt - cs < 0.3 and sc in ("n1", "n2", "n3"): hop = -24 * math.sin(math.pi * (tt - cs) / 0.3)
    n = 8 if sc in ("n1", "n2", "n3", "outro") else 10
    if sc == "intro": x0, y0 = (W - 640) // 2, 655
    elif sc == "outro": x0, y0 = (W - 512) // 2, 742
    else: x0, y0 = 22, 946
    enter = scene_start(sc); slide = (1 - eo((tt - enter) / 0.4)) * 60 if sc != "intro" else 0
    bob = 6 * math.sin(2 * math.pi * tt / 1.7)
    spr = sprite(arm, mouth, eyes, nod, n)
    d.ellipse((x0 + n * 16, y0 + n * 61, x0 + n * 50, y0 + n * 66), fill=(0, 0, 0, 90))
    for cs in CHUNK_STARTS:   # アンテナが光る
        u = (tt - cs) / 0.5
        if 0 <= u < 1 and sc in ("n1", "n2", "n3"):
            ax, ay = x0 + n * 34.5, y0 + n * 2 + bob + hop; r = 14 + 70 * eo(u)
            d.ellipse((ax - r, ay - r, ax + r, ay + r), outline=YELLOW + (int(255 * (1 - u)),), width=7)
    put(fr, spr, x0 - slide, y0 + bob + hop)
    if sc == "outro" and tt >= st["out2"] - 0.05:   # なかまの5体
        for j, m in enumerate(MATES):
            u = (tt - st["out2"] - 0.25 - j * 0.12) / 0.35
            if u > 0: put(fr, m, 60 + j * 192, 1262 + (1 - eb(u)) * 140 + 4 * math.sin(tt * 3.6 + j * 1.3), clamp(u * 2))
    # 上の帯と番組名、進みぐあい
    put(fr, TOPBAR, 0, 0)
    d = ImageDraw.Draw(fr, "RGBA")
    cur = {"n1": 1, "n2": 2, "n3": 3, "outro": 4}.get(sc, 0)
    for j, col in enumerate((CYAN, MINT, VIOLET)):
        cx, cy, r = 838 + j * 78, 198, 30
        if cur == j + 1:
            r = 34 + 2 * math.sin(tt * 6); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,), outline=WHITE + (255,), width=4)
            d.text((cx, cy - 3), str(j + 1), font=font(F9, 40), fill=INK + (255,), anchor="mm")
        elif cur > j + 1:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (110,)); d.text((cx, cy - 3), str(j + 1), font=font(F9, 34), fill=WHITE + (230,), anchor="mm")
        else:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(150, 170, 205, 255), width=4); d.text((cx, cy - 3), str(j + 1), font=font(F9, 34), fill=(150, 170, 205, 255), anchor="mm")
    # 字幕・表示文・クレジット
    if tt < 4.3 and sc == "intro": put(fr, DISC, 50, 1296 + (1 - eo(tt / 0.4)) * 30, clamp(tt / 0.3) * clamp((4.3 - tt) / 0.3))
    if tt >= SPEECH_END + 0.15:
        u = (tt - SPEECH_END - 0.15) / 0.35; put(fr, END, 50, 1462 + (1 - eo(u)) * 40, clamp(u * 1.5))
    else: draw_sub(fr, tt, acc)
    d = ImageDraw.Draw(fr, "RGBA")
    if tt < SPEECH_END + 0.15: d.text((W / 2, 1722), CREDIT, font=font(F8, 30), fill=(190, 205, 232, 255), anchor="mm")
    # 場面の切りかわり（ななめの帯が横切る）
    for c, name in cuts:
        u = (tt - (c - 0.3)) / 0.6
        if 0 < u < 1:
            a2 = THEMES[name][2]; xl = -1900 + 3100 * u
            for k, col in enumerate((a2, YELLOW, INK)):
                x1 = xl + k * 70; d.polygon([(x1, 0), (x1 + 1500 - k * 140, 0), (x1 + 1500 - k * 140 - 320, H), (x1 - 320, H)], fill=col + (255,))
            if 0.3 < u < 0.7 and name in NEWS:
                put_c(fr, BIGNUM[name], W / 2, H / 2 - 60, 1 + 0.25 * (u - 0.5))
    return fr
BIGNUM = {k: badge(v["num"], WHITE, 170) for k, v in NEWS.items()}
for c, name in cuts: S(c - 0.28, "wipe")

if ONLY is not None:
    os.makedirs(os.path.join(HERE, "確認コマ"), exist_ok=True)
    for tt in ONLY:
        render(int(tt * FPS)).save(os.path.join(HERE, "確認コマ", f"t{tt:05.1f}.png"))
    print("時刻表:", {k: round(v, 2) for k, v in st.items()}, "合計", round(TOTAL, 2)); sys.exit()

wav = build_audio()
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                       "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                       "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(NF): ff.stdin.write(render(i).tobytes())
ff.stdin.close(); ff.wait()
print("done", OUT, f"{TOTAL:.2f}s", NF, "frames")
