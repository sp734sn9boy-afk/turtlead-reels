#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストーリーズ見本・動画版 v2（カット割り＋ビート）
  1080x1920 / 30fps / H.264 + AAC / 9.6秒

使い方:  python3 make_motion_v2.py
出力先:  このフォルダ（*_v2.mp4）、se_v2/（音のwav）、../_check/motion_v2_frames_*.jpg

v1（make_motion.py）との違い:
  1枚の画面に積み上げるのをやめ、ビート（1拍=0.4秒）に合わせて画面ごと切り替える。
    A 0.0〜 地名が画面いっぱいに1文字ずつ叩きつけられる（緑）
    B 0.8〜 色が反転（黄×こげ茶）して「家を／建てるなら」
    C 1.6〜 濃い色の画面で「おすすめ工務店」→ 特大の「3社」
    D 2.4〜 会社を1社ずつ全画面で（社名・強み・電話）
    E       全社が並ぶまとめ画面（v1の完成形）→ 最後の約2秒は静止

素材の出どころ:
  - デザインの型・フォント・アイコン: ../make_stories.py と同じ（Noto Sans CJK JP = SIL OFL 1.1、アイコンは自作）
  - 音（ドラム・ベース・和音・効果音）: すべてこのスクリプト内で numpy から合成した自作。外部の音源・楽曲は使っていない
  - 写真・他社ロゴ・人物素材: 使っていない。会社名・電話番号は架空
  - 演出の手法（冒頭を最優先・1語ずつ出す文字・ビートに合わせたカット・寄り＋揺れ＋打撃音）は
    公開されている編集ノウハウ記事を参考にした。他社の動画・素材そのものは使っていない
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_motion as v1  # noqa: E402

ms = v1.ms
W, H, S = ms.W, ms.H, ms.S
FPS, SR = 30, 48000
BEAT = 0.4                # 150BPM（30fpsでちょうど12コマ）
DUR = 9.6
back_out, clamp = v1.back_out, v1.clamp


# ---------- 部品づくり ----------
def fit(text, max_w, start, stroke=0, min_size=40):
    size = start
    while size > min_size and ms.font(size).getlength(text) / S + stroke * 2 > max_w:
        size -= 2
    return size


def tsprite(text, size, fill, stroke=0, shadow=None, off=0, bold=True):
    """文字だけの透明スプライト（ふちが濁らないよう、型抜きしてから色をのせる）"""
    f = ms.font(size, bold)
    sw = int(stroke * S)
    l, t, r, b = f.getbbox(text, stroke_width=sw, anchor="ls")
    pad = 6
    m = Image.new("L", (r - l + pad * 2, b - t + pad * 2), 0)
    ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255, stroke_width=sw, stroke_fill=255, anchor="ls")
    m = m.resize((math.ceil(m.width / S), math.ceil(m.height / S)), Image.LANCZOS)
    o = int(off)
    out = Image.new("RGBA", (m.width + o, m.height + o), (0, 0, 0, 0))
    for col, pos in ((shadow, (o, o)), (fill, (0, 0))):
        if col is None:
            continue
        a = Image.new("L", out.size, 0)
        a.paste(m, pos)
        lay = Image.new("RGBA", out.size, tuple(col) + (255,))
        lay.putalpha(a)
        out = Image.alpha_composite(out, lay)
    return out


def shape(w, h, fn):
    """図形＋その上の文字のスプライト"""
    im = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im))
    return im.resize((int(w), int(h)), Image.LANCZOS)


def blit(fr, im, x, y, s=1.0, sx=None, sy=None, angle=0.0, alpha=1.0, anchor=(.5, .5)):
    """im の anchor の位置を (x, y) に合わせて貼る"""
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    if alpha <= 0.01 or sx <= 0 or sy <= 0:
        return
    if abs(sx - 1) > 1e-3 or abs(sy - 1) > 1e-3:
        im = im.resize((max(1, round(im.width * sx)), max(1, round(im.height * sy))), Image.LANCZOS)
    ax, ay = im.width * anchor[0], im.height * anchor[1]
    if abs(angle) > 1e-3:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        ax, ay = im.width / 2, im.height / 2
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    fr.paste(im, (round(x - ax), round(y - ay)), im)


def mix_col(a, b, k):
    return tuple(int(x * (1 - k) + y * k) for x, y in zip(a, b))


def sunburst(bg, col, ang, cx=W / 2, cy=H * .47, n=14):
    """集中線の背景（ゆっくり回る）"""
    im = Image.new("RGB", (W // 2, H // 2), bg)
    d = ImageDraw.Draw(im)
    R = 1400
    for i in range(n):
        a0 = math.radians(ang + i * 360 / n)
        a1 = a0 + math.radians(180 / n)
        d.polygon([(cx / 2, cy / 2), (cx / 2 + R * math.cos(a0), cy / 2 + R * math.sin(a0)),
                   (cx / 2 + R * math.cos(a1), cy / 2 + R * math.sin(a1))], fill=col)
    return im.resize((W, H), Image.BILINEAR)


def slam(u, dur=.067, big=2.6):
    """叩きつけ: u<0 で落下中、u>=0 で着地後。→ (拡大率X, 拡大率Y, 透明度) / 出る前は None"""
    if u < -dur:
        return None
    if u < 0:
        p = 1 + u / dur
        s = big - (big - 1) * p * p
        return s, s, 1
    w = math.exp(-u * 14) * math.cos(u * 2 * math.pi * 5.5)
    return 1 + .13 * w, 1 - .16 * w, 1


def area_layout(area):
    """地名を画面いっぱいに置く: 3文字までは縦に積む、4文字は2×2"""
    n = len(area)
    if n <= 3:
        size = min(600, int(1230 / n))
        pos = [(470, 350 + size * .97 * (i + .5)) for i in range(n)]
        de = (915, pos[-1][1] + size * .2, 250)
        lands = [.067, .267] if n == 2 else [.067 + .15 * i for i in range(n)]
    else:
        size = 480
        pos = [(300 + 480 * (i % 2), 350 + 235 + 470 * (i // 2)) for i in range(n)]
        de = (890, 1420, 230)
        lands = [.067 + .1 * i for i in range(n)]
    return size, pos, de, lands


# ---------- 1本ぶんの素材 ----------
def prepare(spec):
    kind = spec["kind"]
    t = ms.THEMES[kind]
    INK, YEL, WH, CREAM = ms.INK, ms.YELLOW, ms.WHITE, ms.CREAM
    A = {}
    # A 地名
    size, pos, de, lands = area_layout(spec["area"])
    A["chars"] = [tsprite(c, size, YEL, stroke=6, shadow=t["dark"], off=16) for c in spec["area"]]
    A["pos"], A["lands"], A["de_pos"] = pos, lands, de[:2]
    A["de"] = tsprite(spec["particle"], de[2], WH, stroke=4, shadow=t["dark"], off=10)
    A["de_land"] = lands[-1] + .167
    # B 2行目（2つに分ける）
    l1, l2 = spec["line2_split"]
    s1 = fit(l1, 900, 430, 6)
    B = {"l1": tsprite(l1, s1, INK, stroke=5)}
    s2 = fit(l2, 840, 230, 2)
    tw = ms.font(s2).getlength(l2) / S
    bw, bh = tw + 110, s2 * 1.42

    def f_block(d):
        d.rounded_rectangle(ms.P(0, 0, bw, bh), radius=int(28 * S), fill=INK)
        ms.draw_text(d, (bw / 2, bh * .47), l2, ms.font(s2), YEL, stroke=2, anchor="mm")
    B["l2"] = shape(bw, bh, f_block)
    total = s1 + 40 + bh
    top = max(350, 950 - total / 2)
    B["y1"], B["y2"] = top + s1 / 2, top + s1 + 40 + bh / 2
    # C 何社か
    n = len(spec["companies"])
    r = 118

    def f_icon(d):
        d.ellipse(ms.P(0, 0, r * 2, r * 2), fill=WH)
        ms.ICONS[kind](d, r, r, r * 1.12, t["main"])
    C = {"icon": shape(r * 2, r * 2, f_icon),
         "label": tsprite(spec["count_label"], fit(spec["count_label"], 940, 132, 3), WH, stroke=3)}
    num = tsprite(str(n), 640, YEL, stroke=8, shadow=(0, 0, 0), off=14)
    sha = tsprite("社", 300, YEL, stroke=5, shadow=(0, 0, 0), off=10)
    cnt = Image.new("RGBA", (num.width + sha.width + 10, num.height), (0, 0, 0, 0))
    cnt.alpha_composite(num, (0, 0))
    cnt.alpha_composite(sha, (num.width + 10, num.height - sha.height - 20))
    C["count"] = cnt
    # D 会社ごと
    D = []
    for i, (name, strong, tel) in enumerate(spec["companies"]):
        def f_badge(d, i=i):
            d.ellipse(ms.P(8, 10, 228, 230), fill=t["dark"])
            d.ellipse(ms.P(0, 0, 220, 220), fill=t["main"])
            ms.draw_text(d, (110, 104), str(i + 1), ms.font(150), WH, anchor="mm")
        sw_ = W - 120
        ss = fit(strong, sw_ - 70, 70)

        def f_strong(d, strong=strong, ss=ss):
            d.rounded_rectangle(ms.P(0, 0, sw_, 130), radius=int(24 * S), fill=WH, outline=t["main"], width=int(5 * S))
            ms.draw_text(d, (sw_ / 2, 62), strong, ms.font(ss), t["dark"], anchor="mm")

        def f_tel(d, tel=tel):
            d.rounded_rectangle(ms.P(8, 10, sw_ + 8, 210), radius=int(44 * S), fill=t["dark"])
            d.rounded_rectangle(ms.P(0, 0, sw_, 200), radius=int(44 * S), fill=t["main"])
            d.rounded_rectangle(ms.P(44, 58, 204, 142), radius=int(16 * S), fill=WH)
            ms.draw_text(d, (124, 97), "TEL", ms.font(58), t["dark"], anchor="mm")
            ms.draw_text(d, (236, 94), tel, ms.font(fit(tel, sw_ - 280, 112)), WH, stroke=1.5, anchor="lm")
        D.append(dict(
            badge=shape(232, 234, f_badge),
            prog=tsprite(f"おすすめ {i + 1} / {n}", 72, t["dark"]),
            name=tsprite(name, fit(name, 950, 196, 3), INK, stroke=3),
            strong=shape(sw_, 130, f_strong),
            tel=shape(sw_ + 10, 212, f_tel)))
    # PR・掲載表記（どの画面でも同じ位置。色だけ画面に合わせる）
    OV = {}
    for key, pill, prc, txt in (("color", WH, t["dark"], WH), ("yellow", INK, YEL, INK), ("cream", t["main"], WH, t["dark"]),
                                ("card", WH, t["dark"], None)):
        def f_pr(d, pill=pill, prc=prc):
            d.rounded_rectangle(ms.P(0, 0, 92, 48), radius=int(10 * S), fill=pill)
            ms.draw_text(d, (46, 24), "PR", ms.font(30), prc, anchor="mm")
        # "card" = 会社の画面用: 上は色の帯なので白、下はクリーム地なので濃い色
        OV[key] = (shape(92, 48, f_pr), tsprite(spec["edition"], 32, txt or WH),
                   tsprite(spec["footer"], 34, txt or t["dark"]))
    # E まとめ画面（v1の完成形をそのまま使う）
    v1spec = {k: spec[k] for k in ("kind", "edition", "area", "particle", "line2", "pill", "companies", "footer")}
    L, final, n_, th = v1.build(**v1spec)
    return dict(t=t, n=n, A=A, B=B, C=C, D=D, OV=OV, L=L, final=final, kind=kind)


def timeline(n):
    d_len = 1.2 if n >= 3 else 1.6
    T = dict(A=0.0, B=0.8, C=1.6, D0=2.4, d_len=d_len)
    T["E"] = 2.4 + d_len * n
    T["cta"] = T["E"] + .4
    T["static"] = T["cta"] + 1.2
    return T


# ---------- 画面ごとの絵 ----------
def scene_A(M, u):
    t, A = M["t"], M["A"]
    fr = sunburst(t["main"], mix_col(t["main"], t["dark"], .22), u * 25)
    for im, (x, y), ld in zip(A["chars"], A["pos"], A["lands"]):
        r = slam(u - ld)
        if r:
            blit(fr, im, x, y, sx=r[0], sy=r[1], alpha=r[2])
    r = slam(u - A["de_land"], big=2.0)
    if r:
        blit(fr, A["de"], *A["de_pos"], sx=r[0], sy=r[1], alpha=r[2], angle=-6)
    return fr


def scene_B(M, u):
    B = M["B"]
    fr = sunburst(ms.YELLOW, (255, 208, 30), -u * 25 + 9)
    blit(fr, B["l1"], W / 2, B["y1"])
    r = slam(u - .4, big=2.6)
    if r:
        blit(fr, B["l2"], W / 2, B["y2"], sx=r[0], sy=r[1], alpha=r[2], angle=-3)
    return fr


def scene_C(M, u):
    t, C = M["t"], M["C"]
    bg = mix_col(t["dark"], (0, 0, 0), .25)
    fr = sunburst(bg, mix_col(bg, t["main"], .28), u * 25 + 4, cy=1180)
    p = u / .2
    blit(fr, C["icon"], W / 2, 535, s=.3 + .7 * back_out(p, 3), angle=-30 * (1 - clamp(p)) ** 2)
    blit(fr, C["label"], W / 2 - 700 * (1 - clamp(u / .13)) ** 2, 745)
    r = slam(u - .4, big=3.2)
    if r:
        blit(fr, C["count"], W / 2 + 10, 1175, sx=r[0], sy=r[1], alpha=r[2])
    return fr


def scene_D(M, i, u):
    t, E = M["t"], M["D"][i]
    bg = ms.CREAM if i % 2 == 0 else t["pale"]
    fr = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(fr)
    d.rectangle((0, 0, W, 330), fill=t["main"])               # 上の帯（PR表記の下地）
    for k in range(-1, 13):
        d.ellipse((k * 90, 285, k * 90 + 90, 375), fill=t["main"])
    y0 = 90
    p = u / .22
    blit(fr, E["badge"], 176, 470 + y0, s=.2 + .8 * back_out(p, 3.2), angle=40 * (1 - clamp(p)) ** 2)
    blit(fr, E["prog"], 320 + 500 * (1 - clamp(u / .15)) ** 2, 470 + y0, anchor=(0, .5))
    q = clamp(u / .17)
    blit(fr, E["name"], 60 + 1000 * (1 - q) ** 2.2, 760 + y0, anchor=(0, .5),
         sx=1 + .12 * (1 - q) - .05 * math.exp(-max(u - .17, 0) * 16) * math.cos(max(u - .17, 0) * 38) * (q >= 1))
    q2 = clamp((u - .12) / .16)
    blit(fr, E["strong"], W / 2, 975 + y0 + 60 * (1 - q2) ** 2, alpha=q2)
    r = slam(u - .4, dur=.07, big=1.9)
    if r:
        blit(fr, E["tel"], W / 2 + 4, 1210 + y0, sx=r[0], sy=r[1], alpha=r[2])
    # 切り替えのひと掃き（色の帯が横切る）
    if u < .134:
        x = -500 + 2100 * (u / .134)
        ImageDraw.Draw(fr).polygon([(x, 0), (x + 420, 0), (x + 200, H), (x - 220, H)], fill=t["main"])
    return fr


def scene_E(M, u, T):
    # v1 の描画を「全部出そろった後」の時刻で呼び、保存のひと言だけ動かす
    vt = dict(cta=10 + (T["cta"] - T["E"]), cta2=99, static=10 + (T["static"] - T["E"]))
    vt["kiran"] = vt["cta"] + .2
    return v1.render_frame(M["L"], M["final"], M["n"], M["t"], 10 + u, vt)


def overlay(fr, M, key):
    pr, ed, ft = M["OV"][key]
    y = ms.SAFE_TOP + 22
    fr.paste(pr, (ms.MX, y), pr)
    blit(fr, ed, ms.MX + 110, y + 24, anchor=(0, .5))
    blit(fr, ft, W / 2, 1632)


def camera(fr, z, dx=0.0, dy=0.0):
    """画面ごと寄る・揺らす"""
    if z < 1.002:
        return fr
    nw, nh = round(W * z), round(H * z)
    big = fr.resize((nw, nh), Image.BILINEAR)
    mx, my = (nw - W) / 2, (nh - H) / 2
    x = round(mx + max(-mx, min(mx, dx)))
    y = round(my + max(-my, min(my, dy)))
    return big.crop((x, y, x + W, y + H))


def render(M, T, tm):
    n = M["n"]
    if tm >= T["static"]:
        return M["final"]
    hits = []            # (時刻, 強さ) 画面が揺れる・寄るタイミング
    punches = []         # (時刻, 寄りの量) カットの頭で一瞬寄る
    for ld in M["A"]["lands"]:
        hits.append((ld, 1.0))
    hits.append((M["A"]["de_land"], .5))
    hits += [(T["B"] + .4, .9), (T["C"] + .4, 1.2)]
    punches += [(T["B"], .16), (T["C"], .1), (T["E"], .14)]
    for i in range(n):
        hits.append((T["D0"] + i * T["d_len"] + .4, .45))
        punches.append((T["D0"] + i * T["d_len"], .06))

    if tm < T["B"]:
        u, ln, key = tm, .8, "color"
        fr = scene_A(M, u)
        creep = .05 * max(0, u - .55) / .25
    elif tm < T["C"]:
        u, key = tm - T["B"], "yellow"
        fr = scene_B(M, u)
        creep = .05 * u / .8
    elif tm < T["D0"]:
        u, key = tm - T["C"], "color"
        fr = scene_C(M, u)
        creep = .05 * u / .8
    elif tm < T["E"]:
        i = int((tm - T["D0"]) / T["d_len"] + 1e-6)
        u, key = tm - T["D0"] - i * T["d_len"], "card"
        fr = scene_D(M, i, u)
        creep = .025 * u / T["d_len"]
    else:
        u, key = tm - T["E"], None
        fr = scene_E(M, u, T)
        creep = 0

    z, dx, dy, flash = 1 + creep, 0.0, 0.0, 0.0
    for (t0, amp) in hits:
        v = tm - t0
        if 0 <= v < .3:
            env = math.exp(-v * 12) * amp
            z += .045 * env
            dx += 16 * env * math.sin(v * 2 * math.pi * 17)
            dy += 34 * env * math.cos(v * 2 * math.pi * 13)
            flash = max(flash, .22 * amp * max(0, 1 - v / .07))
    for (t0, amt) in punches:
        v = tm - t0
        if 0 <= v < .17:
            z += amt * (1 - v / .17) ** 2
            flash = max(flash, amt * 3 * max(0, 1 - v / .07))
    if key is None:
        fr = fr.copy()
    fr = camera(fr, z, dx, dy)
    if flash > 0.01:
        fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), min(.5, flash))
    if key:
        overlay(fr, M, key)
    return fr


# ---------- 音（すべて合成） ----------
def tt(dur):
    return np.arange(int(SR * dur)) / SR


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / (1 + (lo / np.maximum(f, 1)) ** 6) / (1 + (f / hi) ** 6)
    return np.fft.irfft(X * g, len(x))


def noise(dur, seed):
    return np.random.default_rng(seed).standard_normal(int(SR * dur))


def a_kick():
    t = tt(.32)
    f = 48 + 150 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 10) + .5 * np.sin(2 * ph) * np.exp(-t * 16)
    x += band(noise(.32, 11), 1500, 6000) * np.exp(-t * 180) * .4
    return np.tanh(x * 2.2)


def a_boom(long=.9):
    """叩きつけの音: 低音の落ち込み＋中低音の胴鳴り＋破裂音"""
    t = tt(long)
    f = 42 + 190 * np.exp(-t * 20)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 5)
    x += (.6 * np.sin(2 * ph) + .35 * np.sin(3 * ph) + .2 * np.sin(4.02 * ph)) * np.exp(-t * 9)
    x += band(noise(long, 12), 120, 900) * np.exp(-t * 14) * .9          # 胴鳴り
    x += band(noise(long, 13), 2000, 9000) * np.exp(-t * 40) * .5         # 破裂
    return np.tanh(x * 2.0) * np.minimum(1, t / .0015)


def a_clap():
    t = tt(.25)
    env = sum(np.exp(-np.maximum(t - d, 0) * 70) * (t >= d) for d in (0, .011, .023)) / 2
    return band(noise(.25, 14), 900, 5000) * (env + np.exp(-t * 22) * .5)


def a_hat():
    t = tt(.07)
    return band(noise(.07, 15), 7000, 16000) * np.exp(-t * 70)


def a_bass(freq, dur=.19):
    t = tt(dur)
    x = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 9))
    x += .5 * np.sin(2 * np.pi * freq * 2 * t)                              # スマホ向けに1オクターブ上を足す
    env = np.minimum(1, t / .004) * np.exp(-t * 9) * np.minimum(1, (dur - t) / .01)
    return np.tanh(x * 1.1) * env


def a_stab(freqs, dur=.5):
    t = tt(dur)
    x = np.zeros(len(t))
    for f in freqs:
        for det in (.997, 1.003):
            x += sum(np.sin(2 * np.pi * f * det * k * t) / k for k in (1, 2, 3, 4, 5, 6))
    return x * np.minimum(1, t / .003) * np.exp(-t * 8)


def a_riser(dur=.3):
    t = tt(dur)
    p = t / dur
    x = v1._lp(noise(dur, 16), 400 + 7000 * p ** 2)
    x = x - v1._lp(x, 300)
    tone = np.sin(2 * np.pi * np.cumsum(220 + 900 * p ** 2) / SR) * .25
    return (x + tone) * p ** 2


def make_audio(M, T, wav_path):
    n = M["n"]
    N = int(SR * DUR)
    mix = np.zeros(N)
    saved = {}

    def add(name, x, at, gain):
        x = x / (np.max(np.abs(x)) + 1e-9)
        saved.setdefault(name, x)
        i = int(round(at * SR))
        if i >= N:
            return
        j = min(N, i + len(x))
        mix[i:j] += x[: j - i] * gain

    boom, kick, clap, hat = a_boom(), a_kick(), a_clap(), a_hat()
    whoosh = v1.se_whoosh(.16, 600, 5000, 7)
    # A: 文字の着地ごとに叩く → 吸い込む音 → B の頭で一番大きく
    lands = M["A"]["lands"]
    for k, ld in enumerate(lands):
        add("boom", boom, ld, 1.0 if k == 0 or k == len(lands) - 1 else .8)
    add("clap", clap, M["A"]["de_land"], .5)
    add("riser", a_riser(.26), T["B"] - .26, .45)
    add("boom", boom, T["B"], 1.0)
    add("boom", boom, T["B"] + .4, .75)
    add("riser", a_riser(.2), T["C"] + .2, .35)
    add("boom", boom, T["C"] + .4, 1.0)
    # ビート（B の頭から E の頭まで）: 4つ打ち＋裏のハット＋2・4拍のクラップ＋裏打ちのベース
    roots = [110.0, 110.0, 87.31, 98.0]                       # A・A・F・G（自作の進行）
    chords = [(220, 261.63, 329.63), (220, 261.63, 329.63), (174.61, 220, 261.63), (196, 246.94, 293.66)]
    b = 0
    while T["B"] + b * BEAT < T["E"] - 1e-6:
        at = T["B"] + b * BEAT
        bar = (b // 4) % 4
        add("kick", kick, at, .8)
        add("hat", hat, at + BEAT / 2, .2)
        if b % 2 == 1:
            add("clap", clap, at, .4)
        add("bass", a_bass(roots[bar]), at + BEAT / 2, .5)
        if b >= 2:
            add("bass", a_bass(roots[bar] * 2, .1), at + BEAT * .75, .22)
        b += 1
    # カットの頭: ウーシュ＋和音のひと刺し
    cuts = [T["C"]] + [T["D0"] + i * T["d_len"] for i in range(n)]
    for c in cuts:
        bar = int(round((c - T["B"]) / BEAT)) // 4 % 4
        add("whoosh", whoosh, c - .14, .3)
        add("stab", a_stab(chords[bar]), c, .32)
    # D: 電話番号が出るところで「ポン」
    for i in range(n):
        add("pon", v1.se_pon([659.25, 783.99, 880.0, 1046.5][i], .22), T["D0"] + i * T["d_len"] + .4, .32)
    # E: 最後の一発 → 明るい和音 → きらめき。ここで音楽は止まる
    add("riser", a_riser(.3), T["E"] - .3, .5)
    add("boom", boom, T["E"], 1.0)
    add("stab_end", a_stab((261.63, 329.63, 392.0, 523.25), 1.4), T["E"], .4)
    add("pyoko", v1.se_pyoko(), T["cta"], .3)
    add("kiran", v1.se_kiran(), T["cta"] + .2, .34)

    mix = np.tanh(mix * 1.15)                                   # 山をやわらかくつぶす
    mix = mix / np.max(np.abs(mix)) * 0.40                      # AAC後で -6dB 前後
    fade = int(SR * .05)
    mix[-fade:] *= np.linspace(1, 0, fade)

    def write(path, x, g=1.0):
        pcm = (np.clip(x * g, -1, 1) * 32767).astype("<i2")
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())

    os.makedirs(os.path.dirname(wav_path), exist_ok=True)
    write(wav_path, mix)
    for k, x in saved.items():
        write(os.path.join(os.path.dirname(wav_path), k + ".wav"), x, .5)


# ---------- 書き出し ----------
def make_video(out_name, check_name, spec):
    M = prepare(spec)
    T = timeline(M["n"])
    out = os.path.join(HERE, out_name)
    wav = os.path.join(HERE, "se_v2", out_name.replace(".mp4", "_mix.wav"))
    make_audio(M, T, wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", str(DUR), "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(round(DUR * FPS))):
        pr.stdin.write(render(M, T, k / FPS + 1e-6).tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("saved", out, {k: round(v, 2) for k, v in T.items()})
    stamps = [.1, .2, .5, 1.0, 1.4, 2.0, T["D0"] + .9, T["D0"] + T["d_len"] + .9, T["E"] + .7, DUR - 1 / FPS]
    check_sheet(out, check_name, stamps)


def check_sheet(mp4, check_name, stamps):
    chk = os.path.join(os.path.dirname(HERE), "_check")
    cw, chh, cols = 432, 768, 5
    rows = math.ceil(len(stamps) / cols)
    sheet = Image.new("RGB", (cols * (cw + 12) + 12, rows * (chh + 70) + 10), (50, 50, 50))
    d = ImageDraw.Draw(sheet)
    f = ms.ImageFont.truetype(ms.FONT_B, 38)
    for i, ts in enumerate(stamps):
        tmp = os.path.join(chk, f"_tmp_{i}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4,
                        "-vf", f"select=eq(n\\,{round(ts * FPS)})", "-frames:v", "1", tmp], check=True)
        im = Image.open(tmp).convert("RGBA")
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        do = ImageDraw.Draw(ov)
        do.rectangle((0, 0, W, ms.SAFE_TOP), fill=(0, 0, 0, 90))
        do.rectangle((0, ms.SAFE_BOTTOM, W, H), fill=(0, 0, 0, 90))
        im = Image.alpha_composite(im, ov).convert("RGB").resize((cw, chh), Image.LANCZOS)
        x, y = 12 + (i % cols) * (cw + 12), 8 + (i // cols) * (chh + 70)
        sheet.paste(im, (x, y + 56))
        d.text((x + 6, y), "最後" if i == len(stamps) - 1 else f"{ts:.1f}秒", font=f, fill=(255, 255, 255))
        os.remove(tmp)
    path = os.path.join(chk, check_name)
    sheet.save(path, quality=90)
    print("saved", path)


SPECS = [
    ("01_hokusatsu_koumuten_v2.mp4", "motion_v2_frames_01_hokusatsu.jpg", dict(
        kind="house", edition="マイタウンガイド 北薩版", area="北薩", particle="で",
        line2="家を建てるなら", line2_split=("家を", "建てるなら"), count_label="おすすめ工務店",
        pill="おすすめ工務店・建築会社　3社", companies=ms.HOUSE,
        footer="マイタウンガイド2026（北薩版）に掲載中")),
    ("02_amami_kuruma_v2.mp4", "motion_v2_frames_02_amami.jpg", dict(
        kind="car", edition="マイタウンガイド 奄美大島版", area="奄美大島", particle="で",
        line2="車のことなら", line2_split=("車の", "ことなら"), count_label="たよれる車屋さん",
        pill="車検・修理・中古車　おすすめ2社", companies=ms.CAR,
        footer="マイタウンガイド2026（奄美大島版）に掲載中")),
]

if __name__ == "__main__":
    for out_name, check_name, spec in SPECS:
        make_video(out_name, check_name, spec)
