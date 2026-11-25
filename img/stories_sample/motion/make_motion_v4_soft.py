#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ストーリーズ見本・動画版 v4_soft（v4の時間配分のまま、雰囲気をやさしくした版）
  1080x1920 / 30fps / H.264 + AAC / 3社版 12.8秒・2社版 11.2秒

使い方:  python3 make_motion_v4_soft.py
出力先:  このフォルダ（*_v4_soft.mp4）、se_v4_soft/（音のwav）、../_check/motion_v4_soft_frames_*.jpg

v4 と同じもの: 画面の順番と秒数（A 0〜2.0 / B 2.0〜3.2 / C 3.2〜4.4 / D 各1.6秒 / E まとめ→最後2秒は静止）、
              【PR】・掲載表記の位置、上下250pxに大事な文字を置かないこと、架空の会社名。
v4 から変えたもの:
  色   … 赤い帯・黄色の集中線・濃い色面をやめ、クリーム地＋淡い業種色のグラデーション。アクセントはやさしいオレンジ1色
  文字 … 丸ゴシック（M PLUS Rounded 1c）。白いふちと、ごく薄い影
  動き … 叩きつけ・揺れ・フラッシュなし。ふわっと浮き上がる／ぽよんと出る／画面どうしはフェード／ゆっくり寄る
  言葉 … 「〜の方へ」「まずは ここをチェック」「最後に まとめがあります」
  音   … ドラムなし。マリンバのゆったりした分散和音、ベル、木のポン（すべて numpy で合成した自作）。音量も控えめ
  飾り … 小さな丸・葉っぱ（車は輪っか）・きらきら（図形で自作）を少しだけ

素材の出どころ:
  - フォント: M PLUS Rounded 1c ExtraBold / Medium（SIL Open Font License 1.1、fonts/ に同梱。fonts/LICENSE_NOTE.txt 参照）
  - アイコン・飾り・音: すべて自作。写真・他社ロゴ・人物素材なし。会社名・電話番号は架空
"""
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_motion_v4 as v4  # noqa: E402

v3, v2, v1, ms = v4.v3, v4.v2, v4.v1, v4.ms
W, H, S, FPS, SR = v2.W, v2.H, v2.S, v2.FPS, v2.SR
blit, shape, clamp, back_out = v2.blit, v2.shape, v2.clamp, v2.back_out
FONT_XB = os.path.join(HERE, "fonts", "MPLUSRounded1c-ExtraBold.ttf")
FONT_M = os.path.join(HERE, "fonts", "MPLUSRounded1c-Medium.ttf")

WHITE = (255, 255, 255)
CREAM = (255, 249, 238)
INK = (92, 72, 60)                 # やわらかいこげ茶
SUB = (128, 108, 96)
ACC = (243, 150, 92)               # アクセント: やさしいオレンジ
PEACH = (255, 232, 212)
SOFT = {
    "house": dict(main=(104, 186, 140), deep=(44, 128, 90), pale=(226, 244, 232)),
    "car": dict(main=(104, 184, 214), deep=(34, 118, 156), pale=(222, 242, 249)),
}
BAR_Y = 340


def rfont(size, bold=True):
    return ImageFont.truetype(FONT_XB if bold else FONT_M, int(size * S))


def rfit(text, max_w, start, min_size=36):
    size = start
    while size > min_size and rfont(size).getlength(text) / S > max_w:
        size -= 2
    return size


def stxt(text, size, fill, ow=0, outline=WHITE, shadow=.2, bold=True):
    """やわらかい文字: 白いふち＋ごく薄い影（ow=0 ならふち・影なし）"""
    f = rfont(size, bold)
    sw = int(ow * S)
    l, t, r, b = f.getbbox(text, stroke_width=sw, anchor="ls")
    pad = 6 + (28 if ow else 0)
    size2 = (r - l + pad * 2, b - t + pad * 2)
    masks = []
    for w_ in ((sw, 0) if ow else (0,)):
        m = Image.new("L", size2, 0)
        ImageDraw.Draw(m).text((pad - l, pad - t), text, font=f, fill=255, stroke_width=w_, stroke_fill=255, anchor="ls")
        masks.append(m.resize((math.ceil(size2[0] / S), math.ceil(size2[1] / S)), Image.LANCZOS))
    out = Image.new("RGBA", masks[0].size, (0, 0, 0, 0))

    def lay(col, mask):
        im = Image.new("RGBA", out.size, tuple(col) + (255,))
        im.putalpha(mask)
        return im
    if ow:
        sh = Image.new("L", out.size, 0)
        sh.paste(masks[0], (0, 7))
        sh = sh.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * shadow))
        out = Image.alpha_composite(out, lay((70, 55, 45), sh))
        out = Image.alpha_composite(out, lay(outline, masks[0]))
    return Image.alpha_composite(out, lay(fill, masks[-1]))


def panel(w, h, fill, radius=None, outline=None, ow=4, shadow=.16):
    """角丸の板＋ふんわりした影（まわりに 24px の余白つき）"""
    radius = h / 2 if radius is None else radius
    m = 24
    w, h = int(w), int(h)
    body = shape(w, h, lambda d: d.rounded_rectangle(ms.P(0, 0, w, h), radius=int(radius * S), fill=fill,
                                                     outline=outline, width=int(ow * S) if outline else 0))
    out = Image.new("RGBA", (w + m * 2, h + m * 2), (0, 0, 0, 0))
    if shadow:
        a = Image.new("L", out.size, 0)
        a.paste(body.getchannel("A"), (m, m + 8))
        a = a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * shadow))
        sh = Image.new("RGBA", out.size, (70, 55, 45, 255))
        sh.putalpha(a)
        out = Image.alpha_composite(out, sh)
    out.alpha_composite(body, (m, m))
    return out


def put_center(base, im, dy=0, dx=0):
    base.alpha_composite(im, (int((base.width - im.width) / 2 + dx), int((base.height - im.height) / 2 + dy)))
    return base


def pill_text(text, size, fill, tcol, pad=70, hk=1.75, **kw):
    t = stxt(text, size, tcol)
    return put_center(panel(t.width + pad * 2 - 12, size * hk, fill, **kw), t, dy=-size * .03)


def hstack(parts, gap=0, center=False):
    """横に並べる（center=True なら上下中央ぞろえ、それ以外は下ぞろえ）"""
    w = sum(p.width for p in parts) + gap * (len(parts) - 1)
    h = max(p.height for p in parts)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for p in parts:
        out.alpha_composite(p, (max(0, x), (h - p.height) // 2 if center else h - p.height))
        x += p.width + gap
    return out


def gradient(c0, c1, blobs=()):
    """上から下へのやわらかいグラデーション＋ぼかした丸"""
    k = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(c0)[None, None, :] * (1 - k) + np.array(c1)[None, None, :] * k
    im = Image.fromarray(np.broadcast_to(arr, (H, W, 3)).astype("uint8").copy())
    for (x, y, r, col, a) in blobs:                      # 色ごとに「型」をぼかしてからのせる（ふちが黒ずまない）
        m = Image.new("L", (W // 4, H // 4), 0)
        ImageDraw.Draw(m).ellipse(((x - r) / 4, (y - r) / 4, (x + r) / 4, (y + r) / 4), fill=a)
        m = m.filter(ImageFilter.GaussianBlur(26)).resize((W, H), Image.BILINEAR)
        im.paste(Image.new("RGB", (W, H), tuple(col)), (0, 0), m)
    return im


def fade(im, a):
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


# ---------- 動きの型 ----------
def rise(u, dur=.4, dist=60):
    """ふわっと浮き上がる → (ずれY, 透明度)。出る前は None"""
    if u < 0:
        return None
    p = clamp(u / dur)
    return dist * (1 - p) ** 3, clamp(.25 + u / (dur * .4))


def poyon(u, dur=.5):
    """ぽよんと出る → (拡大率, 透明度)"""
    if u < 0:
        return None
    return .82 + .18 * back_out(u / dur, 1.9), clamp(u / .14)


# ---------- 素材 ----------
def prepare(spec):
    kind = spec["kind"]
    t = SOFT[kind]
    area, part, hook, comps = spec["area"], spec["particle"], spec["hook"], spec["companies"]
    n = len(comps)
    M = dict(t=t, n=n, kind=kind)
    # 背景
    M["bg"] = dict(
        A=gradient(CREAM, t["pale"], [(160, 520, 420, WHITE, 150), (980, 1250, 480, t["main"], 46), (120, 1600, 360, ACC, 30)]),
        B=gradient(CREAM, PEACH, [(900, 560, 460, WHITE, 150), (140, 1300, 460, ACC, 34)]),
        C=gradient(t["pale"], CREAM, [(540, 1040, 560, WHITE, 170), (1000, 500, 360, t["main"], 40)]),
        D=gradient(CREAM, CREAM, [(980, 700, 420, t["pale"], 200), (100, 1450, 420, PEACH, 150)]),
        E=gradient(t["pale"], CREAM, [(200, 480, 460, WHITE, 150), (980, 1500, 420, PEACH, 120)]))
    # 飾り（図形で自作）
    def leaf(d):
        pts = [(34 + 26 * math.sin(math.pi * k / 16), 100 * k / 16) for k in range(17)]
        pts += [(34 - 26 * math.sin(math.pi * k / 16), 100 * k / 16) for k in range(16, -1, -1)]
        d.polygon([ms.P(*p) for p in pts], fill=t["main"])
    def ring(d):
        d.ellipse(ms.P(4, 4, 76, 76), outline=t["main"], width=int(8 * S))
    def spark(d):
        v1.star(d, 40 * S, 40 * S, 38 * S, ACC)
    deco = [fade(shape(68, 100, leaf) if kind in ("house", "pest") else shape(80, 80, ring), .5),
            fade(shape(44, 44, lambda d: d.ellipse(ms.P(0, 0, 44, 44), fill=ACC)), .42),
            fade(shape(64, 64, lambda d: d.ellipse(ms.P(0, 0, 64, 64), fill=WHITE)), .8),
            fade(shape(80, 80, spark), .6)]
    rng = np.random.default_rng(7 if kind == "house" else 9)
    M["deco"] = [(deco[i % 4], float(rng.uniform(50, 1030)), float(rng.uniform(320, 1580)),
                  float(rng.uniform(0, 6.28)), float(rng.uniform(.6, 1.1)), float(rng.uniform(-30, 30)))
                 for i in range(11)]
    M["spark"] = shape(80, 80, spark)

    # A: 地名＋呼びかけ
    big = spec.get("area_big", area)        # 大きく積む文字（「姶良・伊佐」→「姶良伊佐」のように記号を抜く用）
    na = len(big)
    if na <= 3:
        size = min(500, int(1000 / na))
        pos = [(440, 350 + size * .97 * (i + .5)) for i in range(na)]
        de = (440 + size / 2 + 120, pos[-1][1] + size * .2, 210)
        bottom = 350 + size * .97 * na
        lands = [0.0 + .15 * i for i in range(na)]
    else:
        size = 420
        pos = [(270 + 420 * (i % 2), 400 + 205 + 410 * (i // 2)) for i in range(na)]
        de = (978, pos[-1][1] + 120, 150)
        bottom = 1220
        lands = [0.0 + .1 * i for i in range(na)]
    M["A"] = dict(chars=[stxt(c, size, t["deep"], ow=14) for c in big], pos=pos, lands=lands,
                  de=stxt(part, de[2], INK, ow=9), de_pos=de[:2], de_land=lands[-1] + .1,
                  pill=pill_text(hook, rfit(hook, 800, 118), ACC, WHITE, pad=64),
                  pill_y=min(1440, bottom + 150), pill_land=.5)
    # 固定の見出し（白い丸い帯）
    sz = 72
    while sz > 40 and rfont(sz).getlength(area + part + hook) / S > W - 200:
        sz -= 2
    row = hstack([stxt(area + part, sz, t["deep"]), stxt(hook, sz, INK)], gap=6)
    M["bar"] = put_center(panel(W - 80, 112, WHITE, outline=t["pale"], ow=4), row, dy=-3)
    # B
    b1, b2 = spec["b_lines"]
    M["B"] = dict(l1=stxt(b1, rfit(b1, 820, 290), INK, ow=12),
                  l2=pill_text(b2, rfit(b2, 760, 116), ACC, WHITE, pad=70),
                  arrow=fade(shape(120, 76, lambda d: d.polygon([ms.P(8, 8), ms.P(112, 8), ms.P(60, 70)], fill=ACC)), .9))
    # C
    lab = spec["count_label"]
    cnt = hstack([stxt(str(n), 560, ACC, ow=16), stxt("社", 250, t["deep"], ow=10)], gap=-30)
    M["C"] = dict(label=stxt(lab, rfit(lab, 900, 118), t["deep"], ow=9), count=cnt,
                  last=pill_text("最後に まとめがあります", 58, WHITE, t["deep"], pad=56, outline=t["pale"]))
    # D と E（まとめ）の部品
    def strong_row(text, size, base_col, bold=True):
        parts = [p for p in re.split(r"(\d+[^\d。、・\s]?)", text) if p]
        return hstack([stxt(p, size * 1.3, ACC) if p[0].isdigit() else stxt(p, size, base_col, bold=bold) for p in parts])
    M["D"] = []
    cw = W - 120
    for i, (name, strong, tel) in enumerate(comps):
        def f_badge(d, i=i):
            d.ellipse(ms.P(0, 0, 200, 200), fill=t["main"])
            ms.draw_text(d, (100, 92), str(i + 1), rfont(130), WHITE, anchor="mm")
        badge = Image.new("RGBA", (248, 248), (0, 0, 0, 0))
        a = Image.new("L", badge.size, 0)
        ImageDraw.Draw(a).ellipse((24, 32, 224, 232), fill=44)
        sh = Image.new("RGBA", badge.size, (70, 55, 45, 255))
        sh.putalpha(a.filter(ImageFilter.GaussianBlur(9)))
        badge = Image.alpha_composite(badge, sh)
        badge.alpha_composite(shape(200, 200, f_badge), (24, 24))
        ss = 62
        while ss > 36 and strong_row(strong, ss, t["deep"]).width > cw - 90:
            ss -= 2
        telp = panel(cw, 190, t["deep"])
        trow = hstack([put_center(panel(150, 78, WHITE, radius=20, shadow=0), stxt("TEL", 50, t["deep"]), dy=-2),
                       stxt(tel, rfit(tel, cw - 300, 104), WHITE)], gap=8, center=True)
        M["D"].append(dict(
            badge=badge, prog=stxt(f"おすすめ {i + 1} / {n}", 64, t["deep"]),
            name=stxt(name, rfit(name, 940, 180), INK, ow=10),
            strong=put_center(panel(cw, 140, WHITE, radius=34, outline=t["pale"]), strong_row(strong, ss, t["deep"]), dy=-3),
            tel=put_center(telp, trow, dy=-4)))
    # E: まとめ画面
    E = {}
    a_txt = area + part
    E["l1"] = stxt(a_txt, rfit(a_txt, 720, 150), t["deep"], ow=10)
    E["l2"] = stxt(hook, rfit(hook, 940, 104), INK, ow=9)
    r = 92

    def f_icon(d):
        d.ellipse(ms.P(0, 0, r * 2, r * 2), fill=WHITE)
        ms.ICONS[kind](d, r, r, r * 1.12, t["main"])
    ic = panel(r * 2, r * 2, WHITE, radius=r)
    ic.alpha_composite(shape(r * 2, r * 2, f_icon), (24, 24))
    E["icon"] = ic
    top, bot, gap = 700, 1462, 24
    ch = min((bot - top - gap * (n - 1)) / n, 270)
    y0 = top + (bot - top - (ch * n + gap * (n - 1))) / 2
    E["cards"], E["card_y"] = [], []
    for i, (name, strong, tel) in enumerate(comps):
        card = panel(cw, ch, WHITE, radius=30, outline=t["pale"], ow=4)
        m = 24
        nr = 40
        num = shape(nr * 2, nr * 2, lambda d, i=i: (d.ellipse(ms.P(0, 0, nr * 2, nr * 2), fill=t["main"]),
                                                    ms.draw_text(d, (nr, nr - 4), str(i + 1), rfont(54), WHITE, anchor="mm")))
        card.alpha_composite(num, (m + 28, int(m + ch / 2 - nr)))
        tx = m + 28 + nr * 2 + 24
        two = ch >= 240 or (spec.get("card_rows3") and ch >= 220)   # card_rows3: 3社でも3段（長い社名用）
        telr = hstack([put_center(panel(84, 46, t["deep"], radius=12, shadow=0), stxt("TEL", 28, WHITE), dy=-1),
                       stxt(tel, (62 if ch >= 240 else 54) if two else 50, t["deep"])], gap=-14, center=True)
        nm = stxt(name, rfit(name, cw - (tx - m) - (0 if two else telr.width) - 44, (72 if ch >= 240 else 62) if two else 60), INK)
        if two:            # 社名／強み／電話の3段
            card.alpha_composite(nm, (tx, int(m + ch * .24 - nm.height / 2)))
            ssz = 44 if ch >= 240 else 38
            st = strong_row(strong, ssz, SUB, bold=False)
            while ssz > 28 and st.width > m + cw - tx - 30:       # 長い強みは枠に入るまで縮める
                ssz -= 2
                st = strong_row(strong, ssz, SUB, bold=False)
            card.alpha_composite(st, (tx, int(m + ch * .52 - st.height / 2)))
            card.alpha_composite(telr, (tx - 24, int(m + ch * .8 - telr.height / 2)))
        else:              # 3社以上: 社名＋電話／強み
            card.alpha_composite(nm, (tx, int(m + ch * .33 - nm.height / 2)))
            card.alpha_composite(telr, (int(m + cw - 22 - telr.width), int(m + ch * .33 - telr.height / 2)))
            st = strong_row(strong, 40, SUB, bold=False)
            card.alpha_composite(st, (tx, int(m + ch * .73 - st.height / 2)))
        E["cards"].append(card)
        E["card_y"].append(y0 + i * (ch + gap) + ch / 2)
    cta = "保存して、あとで見返してね"
    ct = stxt(cta, 46, WHITE)
    bm = shape(34, 42, lambda d: ms.icon_bookmark(d, 0, 0, 34, 42, WHITE))
    E["cta"] = put_center(panel(ct.width + 34 + 20 + 90, 92, ACC), hstack([bm, ct], gap=18, center=True), dy=-2)
    M["E"] = E
    # PR・掲載表記
    pr = shape(92, 48, lambda d: (d.rounded_rectangle(ms.P(0, 0, 92, 48), radius=int(12 * S), fill=t["deep"]),
                                  ms.draw_text(d, (46, 23), "PR", rfont(30), WHITE, anchor="mm")))
    M["ov"] = (pr, stxt(spec["edition"], 32, t["deep"]), stxt(spec["footer"], 34, t["deep"]))
    return M


# ---------- 画面 ----------
def decor(fr, M, tm, move=True, sel=None):
    for k, (im, x, y, ph, sc, ang) in enumerate(M["deco"]):
        if sel is not None and k % 2 != sel:
            continue
        tt_ = tm if move else 0
        blit(fr, im, x + 8 * math.sin(tt_ * .9 + ph * 2), y + 16 * math.sin(tt_ * 1.3 + ph), s=sc,
             angle=ang + 8 * math.sin(tt_ * .8 + ph))


def scene_A(M, u, tm):
    A = M["A"]
    fr = M["bg"]["A"].copy()
    decor(fr, M, tm)
    for k, (im, (x, y), ld) in enumerate(zip(A["chars"], A["pos"], A["lands"])):
        r, p = rise(u - ld, .45, 80), poyon(u - ld, .55)
        if r:
            blit(fr, im, x, y + r[0] + 5 * math.sin(tm * 1.6 + k), s=p[0], alpha=r[1])
    r, p = rise(u - A["de_land"], .4, 50), poyon(u - A["de_land"])
    if r:
        blit(fr, A["de"], A["de_pos"][0], A["de_pos"][1] + r[0], s=p[0], alpha=r[1])
    p = poyon(u - A["pill_land"], .55)
    if p:
        blit(fr, A["pill"], W / 2, A["pill_y"], s=p[0], alpha=p[1])
    return fr


def scene_B(M, u, tm):
    B = M["B"]
    fr = M["bg"]["B"].copy()
    decor(fr, M, tm, sel=0)
    r = rise(u, .4, 60)
    blit(fr, B["l1"], W / 2, 800 + r[0], alpha=r[1])
    p = poyon(u - .2, .55)
    if p:
        blit(fr, B["l2"], W / 2, 1120, s=p[0], alpha=p[1])
        blit(fr, B["arrow"], W / 2, 1300 + 12 * math.sin((u - .2) * 5), alpha=clamp((u - .35) / .2))
        for (x, y, dl, sc) in ((190, 640, .0, 1.0), (900, 690, .25, .7), (860, 1260, .5, .8)):
            q = ((u - .3 - dl) % 1.0) / .6
            if u > .3 + dl and q < 1:
                blit(fr, M["spark"], x, y, s=sc * math.sin(q * math.pi), alpha=.9)
    return fr


def scene_C(M, u, tm):
    C = M["C"]
    fr = M["bg"]["C"].copy()
    decor(fr, M, tm, sel=1)
    r = rise(u, .4, 50)
    blit(fr, C["label"], W / 2, 630 + r[0], alpha=r[1])
    p = poyon(u - .4, .6)
    if p:
        blit(fr, C["count"], W / 2, 1030, s=p[0], alpha=p[1])
    p = poyon(u - .55, .5)
    if p:
        blit(fr, C["last"], W / 2, 1440, s=p[0], alpha=p[1])
    return fr


def scene_D(M, i, u, tm, d_len):
    t, E, n = M["t"], M["D"][i], M["n"]
    fr = M["bg"]["D"].copy()
    decor(fr, M, tm, sel=i % 2)
    d = ImageDraw.Draw(fr)
    seg = (W - 120 - 16 * (n - 1)) / n
    for k in range(n):
        x0 = 60 + k * (seg + 16)
        d.rounded_rectangle((x0, 500, x0 + seg, 516), radius=8, fill=t["pale"])
        f = 1 if k < i else (clamp(u / d_len) if k == i else 0)
        if f > 0:
            d.rounded_rectangle((x0, 500, x0 + max(16, seg * f), 516), radius=8, fill=t["main"])
    p = poyon(u, .5)
    blit(fr, E["badge"], 170, 660, s=p[0], alpha=p[1])
    r = rise(u - .05, .4, 40)
    if r:
        blit(fr, E["prog"], 300, 656 + r[0], alpha=r[1], anchor=(0, .5))
    r = rise(u - .1, .45, 60)
    if r:
        blit(fr, E["name"], 44, 920 + r[0], alpha=r[1], anchor=(0, .5))
    r = rise(u - .2, .45, 50)
    if r:
        blit(fr, E["strong"], W / 2, 1140 + r[0], alpha=r[1])
    p = poyon(u - .4, .55)
    if p:
        blit(fr, E["tel"], W / 2, 1370, s=p[0], alpha=p[1])
    return fr


def scene_E(M, u):
    E = M["E"]
    fr = M["bg"]["E"].copy()
    decor(fr, M, 0, move=False)
    blit(fr, E["l1"], 44, 440, anchor=(0, .5))
    blit(fr, E["l2"], 44, 596, anchor=(0, .5))
    blit(fr, E["icon"], W - 60 - 92, 430)
    for k, (card, cy) in enumerate(zip(E["cards"], E["card_y"])):
        r = rise(u - .1 - .12 * k, .45, 50)
        if r:
            blit(fr, card, W / 2, cy + r[0], alpha=r[1])
    v = u - .4
    p = poyon(v, .5)
    if p:
        ang = 3.5 * math.exp(-v * 4) * math.sin(v * 2 * math.pi * 2.2) if v < 1.1 else 0
        blit(fr, E["cta"], W / 2, 1532, s=p[0], alpha=p[1], angle=ang)
        cw = E["cta"].width / 2 - 30
        for (x, y, dl, sc) in ((W / 2 - cw, 1492, .1, .6), (W / 2 + cw, 1500, .25, .75), (W / 2 + cw - 60, 1572, .4, .45)):
            q = (v - dl) / .55
            if 0 < q < 1:
                blit(fr, M["spark"], x, y, s=sc * math.sin(q * math.pi))
    return fr


XF = 0.2      # 画面どうしのフェードの長さ


def render(M, T, tm, cache):
    if tm >= T["static"]:
        if "final" not in cache:
            fr = scene_E(M, T["static"] - T["E"])
            overlay(fr, M, T, T["static"])
            cache["final"] = fr
        return cache["final"]
    n = M["n"]
    bounds = [0.0, T["B"], T["C"]] + [T["D0"] + i * T["d_len"] for i in range(n)] + [T["E"], T["static"]]

    def raw(k, t_abs):
        u = t_abs - bounds[k]
        ln = bounds[k + 1] - bounds[k]
        if k == 0:
            fr = scene_A(M, u, t_abs)
        elif k == 1:
            fr = scene_B(M, u, t_abs)
        elif k == 2:
            fr = scene_C(M, u, t_abs)
        elif k < 3 + n:
            fr = scene_D(M, k - 3, u, t_abs, T["d_len"])
        else:
            return scene_E(M, u)
        return v2.camera(fr, 1 + .03 * clamp(u / ln))             # ゆっくり寄る
    k = max(i for i in range(len(bounds) - 1) if tm >= bounds[i] - 1e-9)
    fr = raw(k, tm)
    u = tm - bounds[k]
    if k > 0 and u < XF:
        if ("prev", k) not in cache:
            cache[("prev", k)] = raw(k - 1, bounds[k] - 1e-3)
        p = u / XF
        fr = Image.blend(cache[("prev", k)], fr, p * p * (3 - 2 * p))
    overlay(fr, M, T, tm)
    return fr


def overlay(fr, M, T, tm):
    if T["B"] <= tm < T["E"] + XF:                               # 固定の見出し（Bでふわっと出て、まとめで消える）
        a = clamp((tm - T["B"]) / .25) * clamp(1 - (tm - T["E"]) / XF)
        blit(fr, M["bar"], W / 2, BAR_Y + 62 - 30 * (1 - clamp((tm - T["B"]) / .3)) ** 3, alpha=a)
    pr, ed, ft = M["ov"]
    y = ms.SAFE_TOP + 22
    fr.paste(pr, (ms.MX, y), pr)
    blit(fr, ed, ms.MX + 110, y + 24, anchor=(0, .5))
    blit(fr, ft, W / 2, 1632)


# ---------- 音（すべて合成） ----------
def tt(dur):
    return np.arange(int(SR * dur)) / SR


def marimba(f, dur=.9):
    t = tt(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
    x += .32 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 24) + .1 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t * 45)
    return x * np.minimum(1, t / .003)


def bell(f, dur=1.8):
    t = tt(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) + .45 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 5.5)
    x += .2 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 9)
    return x * np.minimum(1, t / .004)


def wood(f=620.0):
    t = tt(.16)
    x = (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2.4 * f * t)) * np.exp(-t * 38)
    return x * np.minimum(1, t / .002)


CH = {"C": (261.63, 329.63, 392.0, 523.25), "F": (349.23, 440.0, 523.25, 698.46),
      "G": (392.0, 493.88, 587.33, 783.99), "Am": (220.0, 261.63, 329.63, 440.0)}


def make_audio(M, T, wav_path):
    n, A = M["n"], M["A"]
    N = int(SR * T["dur"])
    mix = np.zeros(N)

    def add(x, at, gain):
        x = x / (np.max(np.abs(x)) + 1e-9)
        i = int(round(at * SR))
        j = min(N, i + len(x))
        if i < N:
            mix[i:j] += x[: j - i] * gain

    def chord_at(tm):
        if tm < T["B"]:
            return "C"
        if tm < T["C"]:
            return "F"
        if tm < T["D0"]:
            return "G"
        i = int((tm - T["D0"]) / T["d_len"] + 1e-6)
        if i == n - 1 and tm >= T["E"] - .8 - 1e-6:
            return "G"
        return ["C", "Am", "F", "C"][i]
    # A: 文字が出るたびにマリンバが上がっていく → 呼びかけでベル
    for k, ld in enumerate(A["lands"]):
        add(marimba([523.25, 659.25, 783.99, 1046.5][k % 4]), ld, .5)
    add(wood(), A["pill_land"], .3)
    add(bell(1046.5), A["pill_land"] + .02, .3)
    add(bell(1318.5), A["pill_land"] + .1, .22)
    # ゆったりした分散和音（0.4秒ごと）と低いマリンバ（0.8秒ごと）
    pat = [0, 2, 1, 2, 3, 2, 1, 2]
    k = 0
    while .8 + k * .4 < T["E"] - 1e-6:
        at = .8 + k * .4
        c = CH[chord_at(at)]
        add(marimba(c[pat[k % 8]]), at, .3)
        if k % 2 == 0:
            add(marimba(c[0] / 2, 1.2), at, .34)
        k += 1
    # 画面の切り替えにベル、出てくるものに木のポン
    add(bell(698.46), T["B"], .26)
    add(wood(700), T["B"] + .2, .3)
    add(bell(1046.5), T["B"] + .22, .22)
    add(bell(587.33), T["C"], .22)
    for j, f in enumerate((783.99, 987.77, 1174.66)):
        add(bell(f), T["C"] + .4 + .08 * j, .24)
    for i in range(n):
        d0 = T["D0"] + i * T["d_len"]
        add(bell(CH[chord_at(d0)][1] * 2), d0, .22)
        add(wood(560 + 60 * i), d0 + .4, .32)
    for j, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        add(bell(f, 2.4), T["E"] + .06 * j, .3)
    add(marimba(130.81, 1.6), T["E"], .34)
    add(wood(740), T["cta"], .26)
    add(v1.se_kiran(), T["cta"] + .12, .14)

    mix = mix / np.max(np.abs(mix)) * 0.26                       # v4（0.40）より控えめ
    fd = int(SR * .05)
    mix[-fd:] *= np.linspace(1, 0, fd)
    os.makedirs(os.path.dirname(wav_path), exist_ok=True)
    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())


def make_video(out_name, check_name, spec):
    M = prepare(spec)
    T = v4.timeline(M["n"])
    dur = T["dur"]
    out = os.path.join(HERE, out_name)
    wav = os.path.join(HERE, "se_v4_soft", out_name.replace(".mp4", "_mix.wav"))
    make_audio(M, T, wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", str(dur), "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(dur * FPS))
    cache = {}
    for k in range(nf):
        pr.stdin.write(render(M, T, k / FPS + 1e-6, cache).tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("saved", out, {k: round(v, 2) for k, v in T.items()})
    stamps = [.2, .6, 1.9, T["B"] + .1, T["B"] + 1.1, T["C"] + 1.0, T["D0"] + 1.2,
              T["D0"] + T["d_len"] + 1.2, T["E"] + .7, (nf - 1) / FPS]
    v2.check_sheet(out, check_name, stamps)


SPECS = [
    ("01_hokusatsu_koumuten_v4_soft.mp4", "motion_v4_soft_frames_01_hokusatsu.jpg", dict(
        kind="house", edition="マイタウンガイド 北薩版", area="北薩", particle="で",
        hook="家を建てる方へ", b_lines=("まずは", "ここをチェック"), count_label="おすすめ工務店",
        companies=ms.HOUSE, footer="マイタウンガイド2026（北薩版）に掲載中")),
    ("02_amami_kuruma_v4_soft.mp4", "motion_v4_soft_frames_02_amami.jpg", dict(
        kind="car", edition="マイタウンガイド 奄美大島版", area="奄美大島", particle="で",
        hook="車検をお考えの方へ", b_lines=("まずは", "ここをチェック"), count_label="たよれる車屋さん",
        companies=ms.CAR, footer="マイタウンガイド2026（奄美大島版）に掲載中")),
]

if __name__ == "__main__":
    for out_name, check_name, spec in SPECS:
        make_video(out_name, check_name, spec)
