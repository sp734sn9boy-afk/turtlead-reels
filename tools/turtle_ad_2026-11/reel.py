"""リール書き出しの共通部品（文字＋自作BGM。ナレーションなし）"""
import subprocess, wave, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from tad import *

RW, RH, FPS = 1080, 1920, 30


# ---------------- BGM（numpyで自作。外部素材なし） ----------------
def make_music(path, dur=15.0, bpm=100, seed=0, root=60):
    sr = 44100
    n = int(sr * dur)
    t = np.arange(n) / sr
    out = np.zeros((n, 2))
    beat = 60 / bpm
    prog = [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]  # I V vi IV
    if seed % 2:
        prog = [[5, 9, 12], [7, 11, 14], [4, 7, 11], [9, 12, 16]]  # IV V iii vi
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    bar = beat * 4
    # パッド
    for bi in range(int(dur / bar) + 1):
        ch = prog[bi % 4]
        s0, s1 = int(bi * bar * sr), min(n, int((bi + 1) * bar * sr))
        if s0 >= n:
            break
        tt = t[s0:s1] - bi * bar
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.3)
        for k, iv in enumerate(ch):
            fr = f(root + iv - 12)
            sig = (np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(2 * np.pi * fr * 2.003 * tt)) * env * 0.05
            out[s0:s1, 0] += sig * (1 if k != 2 else .7)
            out[s0:s1, 1] += sig * (1 if k != 0 else .7)
        # ベース
        fr = f(root + ch[0] - 24)
        for q in range(4):
            q0 = s0 + int(q * beat * sr)
            q1 = min(s1, q0 + int(beat * 0.9 * sr))
            if q0 >= s1:
                break
            tq = t[q0:q1] - t[q0]
            out[q0:q1] += (np.sin(2 * np.pi * fr * tq) * np.exp(-tq * 3) * 0.12)[:, None]
    # アルペジオ（8分）
    step = beat / 2
    for i in range(int(dur / step)):
        ch = prog[int(i * step / bar) % 4]
        note = root + ch[[0, 1, 2, 1, 2, 0, 1, 2][i % 8]] + (12 if i % 4 == 2 else 0)
        s0 = int(i * step * sr)
        s1 = min(n, s0 + int(0.5 * sr))
        tt = t[s0:s1] - t[s0]
        fr = f(note)
        sig = (np.sin(2 * np.pi * fr * tt) + 0.4 * np.sin(2 * np.pi * fr * 2 * tt) + 0.15 * np.sin(2 * np.pi * fr * 3 * tt)) * np.exp(-tt * 7) * 0.07
        pan = 0.5 + 0.3 * math.sin(i)
        out[s0:s1, 0] += sig * (1 - pan) * 2
        out[s0:s1, 1] += sig * pan * 2
    # キック・ハイハット（やわらかく）
    for i in range(int(dur / beat)):
        s0 = int(i * beat * sr)
        s1 = min(n, s0 + int(0.25 * sr))
        tt = t[s0:s1] - t[s0]
        kick = np.sin(2 * np.pi * (50 + 80 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12) * 0.22
        out[s0:s1] += kick[:, None]
        h0 = s0 + int(beat / 2 * sr)
        h1 = min(n, h0 + int(0.05 * sr))
        if h0 < n:
            rng = np.random.default_rng(i)
            hh = rng.normal(0, 1, h1 - h0) * np.exp(-np.arange(h1 - h0) / sr * 80) * 0.03
            out[h0:h1] += hh[:, None]
    # フェード
    fade = np.ones(n)
    fi, fo = int(0.3 * sr), int(1.5 * sr)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    out *= fade[:, None]
    out /= max(1e-6, np.abs(out).max()) / 0.7
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ---------------- 動き ----------------
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def prog(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))


def cover(img, w, h, zoom=1.0, cx=0.5, cy=0.5):
    """img を w×h に敷き詰め（ズーム・位置つき）"""
    s = max(w / img.width, h / img.height) * zoom
    nw, nh = int(img.width * s) + 1, int(img.height * s) + 1
    im = img.resize((nw, nh), Image.BILINEAR)
    x = int((nw - w) * cx)
    y = int((nh - h) * cy)
    return im.crop((x, y, x + w, y + h))


def layer():
    return Image.new('RGBA', (RW, RH), (0, 0, 0, 0))


def put(base, lay, alpha=1.0, dy=0, dx=0, scale=1.0):
    if alpha <= 0:
        return
    l = lay
    if scale != 1.0:
        w, h = int(RW * scale), int(RH * scale)
        l = lay.resize((w, h), Image.BILINEAR)
        tmp = layer()
        tmp.paste(l, ((RW - w) // 2, (RH - h) // 2))
        l = tmp
    if alpha < 1:
        a = l.getchannel('A').point(lambda v: int(v * alpha))
        l = l.copy(); l.putalpha(a)
    base.alpha_composite(l, (int(dx), int(dy)))


def text_layer(lines, y, size=96, kind='black', fill=WHITE, stroke=None, shadow=True, lh=1.3, grad=False, box=None):
    """中央寄せ文字のレイヤー。lines は改行区切り。box=(色, 余白) で座布団"""
    lay = layer()
    d = ImageDraw.Draw(lay)
    f = font(kind, size)
    ls = lines.split('\n')
    if box:
        col, pad = box
        mw = max(d.textlength(l, font=f) for l in ls)
        hh = int(size * lh) * len(ls)
        d.rounded_rectangle((RW / 2 - mw / 2 - pad, y - pad * .6, RW / 2 + mw / 2 + pad, y + hh + pad * .3), 28, fill=col)
    yy = y
    for l in ls:
        tw = d.textlength(l, font=f)
        x = (RW - tw) / 2
        if shadow and not box:
            sh = layer()
            ImageDraw.Draw(sh).text((x, yy + 6), l, font=f, fill=(0, 0, 0, 170))
            sh = sh.filter(ImageFilter.GaussianBlur(8))
            lay.alpha_composite(sh)
            d = ImageDraw.Draw(lay)
        if grad:
            gradient_text(lay, int(x), int(yy), l, f)
        else:
            d.text((x, yy), l, font=f, fill=fill, stroke_width=(stroke[1] if stroke else 0), stroke_fill=(stroke[0] if stroke else None))
        yy += int(size * lh)
    return lay


def sample_badge():
    lay = layer()
    d = ImageDraw.Draw(lay)
    f = font('black', 46)
    t = '※見本です'
    tw = d.textlength(t, font=f)
    x1 = RW - 48
    d.rounded_rectangle((x1 - tw - 50, 150, x1, 228), 39, fill=(255, 255, 255, 240))
    d.text((x1 - tw - 25, 154), t, font=f, fill=(200, 40, 40))
    return lay


def end_card(seed=9, price_label='AI動画 1本', url='turtle-ad.com/reel/'):
    img = background(RW, RH, seed).convert('RGBA')
    d = ImageDraw.Draw(img)
    eyebrow(img, 120, 420, 'AI VIDEO')
    f1 = font('black', 84)
    d.text((120, 520), price_label, font=f1, fill=WHITE)
    f2 = font('black', 190)
    d.text((110, 620), '9,800', font=f2, fill=YELLOW)
    w2 = d.textlength('9,800', font=f2)
    d.text((110 + w2 + 10, 760), '円', font=font('black', 80), fill=YELLOW)
    d.text((120, 880), '（税込・15秒前後）', font=font('bold', 50), fill=SUB)
    card(img, (120, 1020, RW - 120, 1160), glow=True)
    f3 = font('black', 64)
    tw = d.textlength(url, font=f3)
    ImageDraw.Draw(img).text(((RW - tw) / 2, 1048), url, font=f3, fill=WHITE)
    ImageDraw.Draw(img).text((120, 1210), '全国どこでもオンラインで対応', font=font('bold', 46), fill=SUB)
    rgb = img.convert('RGB')
    paste_logo(rgb, 120, 1330, 1.3)
    return rgb.convert('RGBA')


def render(frame_fn, dur, out_path, wav_path):
    n = int(dur * FPS)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{RW}x{RH}', '-r', str(FPS), '-i', '-',
           '-i', wav_path, '-map', '0:v', '-map', '1:a',
           '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '20',
           '-r', str(FPS), '-g', str(FPS * 2),
           '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-ac', '2',
           '-movflags', '+faststart', '-shortest', out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        fr = frame_fn(i / FPS)
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close()
    p.wait()
    return p.returncode
