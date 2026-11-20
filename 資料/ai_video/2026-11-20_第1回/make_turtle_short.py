# タートルが話す縦型ショート動画の試作（1080x1920・30fps）
# 使い方: python3 make_turtle_short.py <narration.json> <出力.mp4> <フォント太字.ttf> <フォント丸.ttf>
#   narration.json = [{"text":..., "file":"xx.wav", "dur":秒}, ...]（VOICEVOXで作ったセリフごとの音声）
# 口パクは音声の大きさ（30fpsの1コマごと）で3段階、まばたきは数秒おき。
import json, math, subprocess, sys, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NARR, OUT, FONT_B, FONT_R = sys.argv[1:5]
W, H, FPS = 1080, 1920, 30
GAP = 0.25          # セリフの間のすき間（秒）
HEAD, TAIL = 0.4, 0.8
CHAR = "/home/user/turtlead-reels/資料/ai_office/characters/poses/leader_talk.png"
NAVY_TOP, NAVY_BOT = (8, 16, 36), (20, 36, 90)
CYAN, WHITE, YELLOW = (60, 214, 240), (255, 255, 255), (255, 204, 77)

# ---------- 音声をつなぐ ----------
meta = json.load(open(NARR))
sr = None; chunks = []; subs = []; t = HEAD
for m in meta:
    with wave.open(m["file"]) as f:
        sr = f.getframerate(); ch = f.getnchannels()
        a = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
        if ch == 2: a = a.reshape(-1, 2).mean(axis=1).astype(np.int16)
    if not chunks: chunks.append(np.zeros(int(sr * HEAD), np.int16))
    chunks.append(a); subs.append((t, t + len(a) / sr, m["text"])); t += len(a) / sr
    chunks.append(np.zeros(int(sr * GAP), np.int16)); t += GAP
chunks.append(np.zeros(int(sr * TAIL), np.int16))
audio = np.concatenate(chunks); total = len(audio) / sr
wav_out = OUT.replace(".mp4", "_voice.wav")
with wave.open(wav_out, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr); f.writeframes(audio.tobytes())
nframes = int(math.ceil(total * FPS))
spf = sr / FPS
rms = np.array([np.sqrt(np.mean(audio[int(i*spf):int((i+1)*spf)].astype(np.float32)**2) + 1e-9) for i in range(nframes)])
level = rms / (np.percentile(rms[rms > 50], 90) if (rms > 50).any() else 1)

# ---------- キャラクターの顔パーツ（64x64のドット格子：1ドット=7px、余白32px） ----------
base = Image.open(CHAR).convert("RGBA")
def box(x0, y0, x1, y1):  # 格子座標（両端含む）→ 画素の四角
    return (32 + 7*x0, 32 + 7*y0, 32 + 7*(x1+1) - 1, 32 + 7*(y1+1) - 1)
screen_col = base.getpixel((32 + 7*32 + 3, 32 + 7*18 + 3))  # 顔の画面の色
blush = base.getpixel((32 + 7*34 + 3, 32 + 7*22 + 3))
# 吹き出しを消す（話している口パクで十分なので）
clean = base.copy(); d = ImageDraw.Draw(clean)
d.rectangle((32 + 7*48, 0, 511, 32 + 7*14), fill=(0, 0, 0, 0))

def face(mouth, blink):
    im = clean.copy(); d = ImageDraw.Draw(im)
    d.rectangle(box(32, 22, 37, 24), fill=screen_col)       # 口をいったん消す
    if mouth == 0:   # 閉じた口（にっこり）
        for x, y in [(33, 22), (34, 23), (35, 23), (36, 22)]: d.rectangle(box(x, y, x, y), fill=CYAN)
    elif mouth == 1: # 少し開く
        d.rectangle(box(33, 22, 36, 22), fill=CYAN); d.rectangle(box(34, 23, 35, 23), fill=CYAN)
        d.rectangle(box(34, 22, 35, 22), fill=blush)
    else:            # 大きく開く
        d.rectangle(box(33, 22, 36, 24), fill=CYAN); d.rectangle(box(34, 22, 35, 23), fill=blush)
    if blink:        # 目を閉じる（横一本の線）
        for ex in (28, 37):
            d.rectangle(box(ex, 16, ex+2, 20), fill=screen_col); d.rectangle(box(ex, 19, ex+2, 19), fill=CYAN)
    return im

SCALE = 1.75  # 512→896px（ドット絵なのでNEARESTで拡大）
CW = int(512 * SCALE)
faces = {(m, b): face(m, b).resize((CW, CW), Image.NEAREST) for m in (0, 1, 2) for b in (0, 1)}

# ---------- 背景（紺のグラデーション＋六角形の模様） ----------
bg = Image.new("RGB", (W, H)); px = np.zeros((H, W, 3), np.uint8)
for i in range(3): px[..., i] = np.linspace(NAVY_TOP[i], NAVY_BOT[i], H)[:, None]
bg = Image.fromarray(px); d = ImageDraw.Draw(bg, "RGBA")
r = 46
for row in range(-1, int(H / (r*1.5)) + 2):
    for col in range(-1, int(W / (r*1.732)) + 2):
        cx = col * r * 1.732 + (row % 2) * r * 0.866; cy = row * r * 1.5
        pts = [(cx + r*math.cos(math.radians(60*k+30)), cy + r*math.sin(math.radians(60*k+30))) for k in range(6)]
        d.polygon(pts, outline=(60, 214, 240, 18))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse((W/2-430, 640, W/2+430, 1500), fill=(60, 214, 240, 55)); glow = glow.filter(ImageFilter.GaussianBlur(120))
bg = Image.alpha_composite(bg.convert("RGBA"), glow)

fB = lambda s: ImageFont.truetype(FONT_B, s)
fR = lambda s: ImageFont.truetype(FONT_R, s)
d = ImageDraw.Draw(bg)
# 上：番組名
d.rounded_rectangle((60, 120, W-60, 300), 36, fill=(4, 7, 15, 210), outline=CYAN, width=4)
d.text((W/2, 178), "AI動画編集部", font=fR(46), fill=CYAN, anchor="mm")
d.text((W/2, 246), "今週のAIニュース", font=fB(70), fill=WHITE, anchor="mm")
# 常に出す表示（AI制作の明示）
d.rounded_rectangle((90, 330, W-90, 400), 35, fill=(255, 204, 77, 235))
d.text((W/2, 365), "AIが情報収集から動画まで作っています", font=fB(38), fill=(8, 16, 36), anchor="mm")
# 下：クレジット
d.text((W/2, H-70), "turtle ad ｜ 音声：VOICEVOX:雀松朱司", font=fB(30), fill=(185, 200, 230), anchor="mm")
bg = bg.convert("RGB")

def wrap(text, font, maxw):
    import re
    lines, cur = [], ""
    for ch in re.findall(r"[A-Za-z0-9]+|.", text):   # 英数字（AIなど）は途中で切らない
        if font.getlength(cur + ch) > maxw and cur:
            if ch in "、。！？」）": cur += ch; ch = ""
            lines.append(cur); cur = ch
        else: cur += ch
    if cur: lines.append(cur)
    return lines

SUBF = fB(64)
def sub_at(t):
    for s, e, txt in subs:
        if s - 0.05 <= t <= e + 0.15: return txt
    return None

# まばたきの時刻（3〜5秒おきに0.13秒）
random.seed(3); blinks = []; bt = 1.2
while bt < total: blinks.append(bt); bt += random.uniform(2.8, 4.5)

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav_out, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
prev_m = 0
for i in range(nframes):
    t = i / FPS
    lv = level[i]
    m = 2 if lv > 0.55 else (1 if lv > 0.18 else 0)
    if m != prev_m and i % 2 == 1: m = prev_m   # 口が速く動きすぎないよう2コマ単位
    prev_m = m
    b = any(0 <= t - x < 0.13 for x in blinks)
    frame = bg.copy()
    bob = int(10 * math.sin(2 * math.pi * t / 1.6))           # ふわふわ上下
    frame.paste(faces[(m, b)], ((W - CW)//2, 560 + bob), faces[(m, b)])
    txt = sub_at(t)
    if txt:
        dd = ImageDraw.Draw(frame, "RGBA")
        ls = wrap(txt, SUBF, W - 200); lh = 88
        top = 1560 - (len(ls) - 1) * lh // 2
        dd.rounded_rectangle((60, top - 70, W - 60, top + (len(ls)-1)*lh + 70), 30, fill=(4, 7, 15, 215))
        for k, l in enumerate(ls):
            dd.text((W/2, top + k*lh), l, font=SUBF, fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=(8, 16, 36))
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); ff.wait()
print("done", OUT, f"{total:.2f}s", nframes, "frames")
