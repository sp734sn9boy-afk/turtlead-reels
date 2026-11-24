#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイタウンガイド「エリア×業種のおすすめまとめ」ストーリーズ見本・動画版
  1080x1920 / 30fps / H.264 + AAC / 8秒

使い方:  python3 make_motion.py
出力先:  このフォルダ（mp4）、se/（効果音のwav）、../_check/motion_frames_*.jpg（確認用）

素材の出どころ:
  - デザインの型・フォント・アイコン: ../make_stories.py と同じ
    （Noto Sans CJK JP = SIL Open Font License 1.1、アイコンは図形から自作）
  - 効果音: このスクリプト内で numpy を使って波形から合成（外部の音源は使っていない）
  - BGM・写真・他社ロゴ・人物素材: 使っていない
  - 会社名・電話番号: すべて架空のダミー

演出の流れ（秒）:
  0.00  色面が上からパッと下りる（PR表記・掲載表記は最初のコマから出ている）
  0.00  地名が上から落ちてくる → 0.17 着地（つぶれて弾む・画面が揺れる・光と線）「ドン」
  0.38  2行目が右から滑り込む → 0.53 着地「シュッ・タン」
  0.62  業種アイコンがポン / 0.82 補足のピルがポン
  1.10〜 会社カードが 0.35秒おきに1枚ずつ「ポン」（音がだんだん高くなる）
  カードの後 「保存して〜」がピョコっと出て左右に揺れる「キラン」＋きらめき
  その後もう一度だけ小さく揺れて、最後の約2秒は静止
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import make_stories as ms  # noqa: E402

W, H, S = ms.W, ms.H, ms.S
MX = ms.MX
FPS = 30
SR = 48000
DUR = 8.0
SIZE2 = (W * S, H * S)
HEAD_BOTTOM = 868

T_PANEL = 0.13          # 色面が下りきる
T_DROP0, T_LAND = 0.0, 0.1667
T_L2_0, T_L2_1 = 0.38, 0.5334
T_ICON = 0.62
T_PILL = 0.82
T_CARD0, CARD_STEP = 1.10, 0.35


# ---------- 部品を「絵＋透明度」で作る ----------
class Duo:
    """同じ描画を、絵（RGB）と型抜き（L）の両方に行う"""

    def __init__(self, rgb, mask):
        self.a, self.b = ImageDraw.Draw(rgb), ImageDraw.Draw(mask)

    def textlength(self, *a, **k):
        return self.a.textlength(*a, **k)

    def __getattr__(self, name):
        fa, fb = getattr(self.a, name), getattr(self.b, name)

        def f(*args, **kw):
            fa(*args, **kw)
            kw2 = dict(kw)
            for k in ("fill", "outline", "stroke_fill"):
                if kw2.get(k) is not None:
                    kw2[k] = 255
            fb(*args, **kw2)
        return f


class Sprite:
    def __init__(self, img, box):
        self.img, self.box = img, box
        self.w, self.h = img.size


def build(kind, edition, area, particle, line2, pill, companies, footer,
          area_size=210, line2_size=140, cta="保存して、あとで見返してね"):
    """make_stories.make と同じ配置で、部品ごとのスプライトを作る"""
    t = ms.THEMES[kind]
    P, font, draw_text, text_w = ms.P, ms.font, ms.draw_text, ms.text_w
    final2 = Image.new("RGB", SIZE2, ms.CREAM)
    L = {}

    def layer(name, fn):
        mask2 = Image.new("L", SIZE2, 0)
        fn(Duo(final2, mask2))
        m = mask2.resize((W, H), Image.LANCZOS)
        box = m.getbbox()
        spr = final2.resize((W, H), Image.LANCZOS).crop(box).convert("RGBA")
        spr.putalpha(m.crop(box))
        L[name] = Sprite(spr, box)

    # 色面
    def f_panel(d):
        d.rectangle(P(0, 0, W, HEAD_BOTTOM), fill=t["main"])
        band = tuple(int(m * .88 + k * .12) for m, k in zip(t["main"], t["dark"]))
        d.polygon([P(W * .52, 0), P(W * .9, 0), P(W * .38, HEAD_BOTTOM), P(0, HEAD_BOTTOM)], fill=band)
        rr = 45
        for i in range(-1, W // (rr * 2) + 2):
            cx = i * rr * 2 + rr
            d.ellipse(P(cx - rr, HEAD_BOTTOM - rr, cx + rr, HEAD_BOTTOM + rr), fill=t["main"])
    layer("panel", f_panel)

    # PR と版名
    def f_pr(d):
        y = ms.SAFE_TOP + 22
        d.rounded_rectangle(P(MX, y, MX + 92, y + 48), radius=int(10 * S), fill=ms.WHITE)
        draw_text(d, (MX + 46, y + 24), "PR", font(30), t["dark"], anchor="mm")
        draw_text(d, (MX + 110, y + 24), edition, font(32), ms.WHITE, anchor="lm")
    layer("pr", f_pr)

    # 1行目（地名）
    icon_r = 100
    stroke1 = 2
    base1 = 342 + 205
    tmp = ImageDraw.Draw(final2)
    max_w1 = W - MX * 2 - icon_r * 2 - 44
    size = area_size
    while size > 80:
        w_area = text_w(tmp, area, font(size), stroke1)
        w_part = text_w(tmp, particle, font(size * .56), 1.5) if particle else 0
        if w_area + w_part + 6 <= max_w1:
            break
        size -= 2

    def f_area(d):
        draw_text(d, (MX + stroke1, base1), area, font(size), ms.YELLOW, stroke=stroke1,
                  shadow=t["dark"], shadow_off=7)
        if particle:
            draw_text(d, (MX + w_area + 10, base1), particle, font(size * .56), ms.WHITE, stroke=1.5,
                      shadow=t["dark"], shadow_off=5)
    layer("area", f_area)

    def f_icon(d):
        icx, icy = W - MX - icon_r, base1 - 92
        d.ellipse(P(icx - icon_r + 7, icy - icon_r + 7, icx + icon_r + 7, icy + icon_r + 7), fill=t["dark"])
        d.ellipse(P(icx - icon_r, icy - icon_r, icx + icon_r, icy + icon_r), fill=ms.WHITE)
        ms.ICONS[kind](d, icx, icy, icon_r * 1.12, t["main"])
    layer("icon", f_icon)

    # 2行目
    stroke2 = 1.5
    sz2 = line2_size
    while sz2 > 60 and text_w(tmp, line2, font(sz2), stroke2) > W - MX * 2:
        sz2 -= 2
    base2 = min(base1 + 46 + sz2 * 0.98, 742)

    def f_line2(d):
        draw_text(d, (MX + stroke2, base2), line2, font(sz2), ms.WHITE, stroke=stroke2,
                  shadow=t["dark"], shadow_off=6)
    layer("line2", f_line2)

    def f_pill(d):
        f_p = font(36)
        pw = text_w(d, pill, f_p) + 56
        py = 772
        d.rounded_rectangle(P(MX, py, MX + pw, py + 62), radius=int(31 * S), fill=ms.WHITE)
        draw_text(d, (MX + 28, py + 30), pill, f_p, t["dark"], anchor="lm")
    layer("pill", f_pill)

    # 会社カード
    n = len(companies)
    cards_top, cards_bottom = 940, 1478
    gap = 18 if n >= 4 else 26
    ch = min((cards_bottom - cards_top - gap * (n - 1)) / n, 250)
    total = ch * n + gap * (n - 1)
    cy0 = cards_top + (cards_bottom - cards_top - total) / 2
    compact = n >= 3
    big = 1.0 if n >= 4 else 1.12
    for i, (name, strong, tel) in enumerate(companies):
        def f_card(d, i=i, name=name, strong=strong, tel=tel):
            top = cy0 + i * (ch + gap)
            d.rounded_rectangle(P(MX + 6, top + 8, W - MX + 6, top + ch + 8), radius=int(26 * S), fill=t["pale"])
            d.rounded_rectangle(P(MX, top, W - MX, top + ch), radius=int(26 * S), fill=ms.WHITE,
                                outline=t["main"], width=int(4 * S))
            nr = (38 * big) if compact else 50
            ncx, ncy = MX + 28 + nr, top + ch / 2
            d.ellipse(P(ncx - nr, ncy - nr, ncx + nr, ncy + nr), fill=t["main"])
            draw_text(d, (ncx, ncy - 3), str(i + 1), font(52 * big if compact else 66), ms.WHITE, anchor="mm")
            tx = ncx + nr + 26
            inner_w = W - MX - 28 - tx
            if compact:
                f_tel = font(40 * big)
                lab = 30 * big
                tel_w = text_w(d, tel, f_tel) + lab * 1.9 + 12
                ns = ms.fit_size(d, name, inner_w - tel_w - 16, 47 * big)
                row1 = top + ch * .32
                draw_text(d, (tx, row1), name, font(ns), ms.INK, anchor="lm")
                ms.icon_phone(d, W - MX - 28 - tel_w, row1 - lab / 2 + 2, lab, t["main"])
                draw_text(d, (W - MX - 28, row1), tel, f_tel, t["dark"], anchor="rm")
                draw_text(d, (tx, top + ch * .75), strong,
                          font(ms.fit_size(d, strong, inner_w, 36 * big), bold=False), ms.SUB, anchor="lm")
            else:
                ns = ms.fit_size(d, name, inner_w, 68)
                draw_text(d, (tx, top + ch * .23), name, font(ns), ms.INK, anchor="lm")
                draw_text(d, (tx, top + ch * .51), strong,
                          font(ms.fit_size(d, strong, inner_w, 42), bold=False), ms.SUB, anchor="lm")
                ms.icon_phone(d, tx, top + ch * .79 - 20, 42, t["main"])
                draw_text(d, (tx + 42 * 1.9 + 16, top + ch * .79), tel, font(58), t["dark"], anchor="lm")
        layer(f"card{i}", f_card)

    def f_cta(d):
        f_c = font(40)
        cw = text_w(d, cta, f_c) + 34 + 22 + 80
        cx0 = (W - cw) / 2
        cy = 1506
        d.rounded_rectangle(P(cx0 + 5, cy + 6, cx0 + cw + 5, cy + 86), radius=int(40 * S), fill=t["dark"])
        d.rounded_rectangle(P(cx0, cy, cx0 + cw, cy + 80), radius=int(40 * S), fill=ms.YELLOW)
        ms.icon_bookmark(d, cx0 + 40, cy + 20, 34, 42, ms.INK)
        draw_text(d, (cx0 + 40 + 34 + 22, cy + 38), cta, f_c, ms.INK, anchor="lm")
    layer("cta", f_cta)

    def f_footer(d):
        draw_text(d, (W / 2, 1632), footer, font(34), t["dark"], anchor="mm")
    layer("footer", f_footer)

    return L, final2.resize((W, H), Image.LANCZOS), n, t


# ---------- 動きの道具 ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def back_out(p, s=2.2):
    p = clamp(p) - 1
    return p * p * ((s + 1) * p + s) + 1


def put(frame, spr, dx=0.0, dy=0.0, sx=1.0, sy=1.0, angle=0.0, alpha=1.0, pivot=(.5, .5)):
    """スプライトを、基準点（pivot）を中心に 拡大・回転・移動 して貼る"""
    if alpha <= 0 or sx <= 0 or sy <= 0:
        return
    im = spr.img
    px = spr.box[0] + spr.w * pivot[0] + dx
    py = spr.box[1] + spr.h * pivot[1] + dy
    if abs(sx - 1) > 1e-3 or abs(sy - 1) > 1e-3:
        nw, nh = max(1, round(spr.w * sx)), max(1, round(spr.h * sy))
        im = im.resize((nw, nh), Image.LANCZOS)
    ox, oy = im.width * pivot[0], im.height * pivot[1]
    if abs(angle) > 1e-3:
        # 回転は中心まわり。pivot は中心として扱う
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        ox, oy = im.width / 2, im.height / 2
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    frame.paste(im, (round(px - ox), round(py - oy)), im)


def star(d, cx, cy, r, col):
    """4つの先がとがった「きらめき」"""
    k = r * .22
    d.polygon([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k),
               (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)], fill=col)


def impact_fx(frame, u, cx, cy, strength=1.0):
    """着地の光・線・輪（u = 着地からの秒）"""
    if u < 0 or u > 0.34:
        return frame
    q = u / 0.34
    ov = Image.new("RGBA", SIZE2, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(255 * (1 - q) ** 1.5 * strength)
    # 放射の線
    r0 = (150 + 520 * (1 - (1 - q) ** 3)) * S
    ln = (190 * (1 - q) + 30) * S
    for i in range(16):
        ang = math.pi * (i / 16 * 2) + 0.2
        ex = 1.35                               # 横に広い楕円状に飛ばす
        x0, y0 = cx * S + math.cos(ang) * r0 * ex, cy * S + math.sin(ang) * r0 * .75
        x1, y1 = cx * S + math.cos(ang) * (r0 + ln) * ex, cy * S + math.sin(ang) * (r0 + ln) * .75
        col = (255, 255, 255, a) if i % 2 else (255, 236, 110, a)
        d.line([(x0, y0), (x1, y1)], fill=col, width=int((16 if i % 2 else 24) * (1 - q * .6) * S))
    # 衝撃の輪
    rr = (120 + 620 * (1 - (1 - q) ** 2)) * S
    d.ellipse((cx * S - rr * 1.3, cy * S - rr * .5, cx * S + rr * 1.3, cy * S + rr * .5),
              outline=(255, 255, 255, int(a * .8)), width=int(14 * (1 - q) * S) + 2)
    ov = ov.resize((W, H), Image.BILINEAR)
    out = Image.alpha_composite(frame.convert("RGBA"), ov)
    # 一瞬の白い光
    fl = 0.42 * max(0.0, 1 - u / 0.10) * strength
    if fl > 0:
        out = Image.blend(out, Image.new("RGBA", (W, H), (255, 255, 255, 255)), fl)
    return out.convert("RGB")


def shake(frame, u, amp=1.0):
    """画面全体を少し拡大して揺らす（ふちが見えないように）"""
    if u < 0 or u > 0.36:
        return frame
    env = math.exp(-u * 11) * amp
    z = 1 + 0.05 * env
    if z < 1.002:
        return frame
    nw, nh = round(W * z), round(H * z)
    big = frame.resize((nw, nh), Image.BILINEAR)
    mx, my = (nw - W) / 2, (nh - H) / 2
    dx = mx * .8 * math.sin(u * 2 * math.pi * 17)
    dy = min(my, 30 * env) * math.cos(u * 2 * math.pi * 13)
    x, y = round(mx + dx), round(my + dy)
    return big.crop((x, y, x + W, y + H))


def render_frame(L, final, n, t_theme, tm, T):
    """tm 秒のコマを作る"""
    if tm >= T["static"]:
        return final
    fr = Image.new("RGB", (W, H), ms.CREAM)
    # 色面：上から下りる
    p = clamp(tm / T_PANEL)
    put(fr, L["panel"], dy=-470 * (1 - p) ** 2)
    put(fr, L["pr"])
    put(fr, L["footer"])

    # 地名：落下 → 着地でつぶれて弾む
    a = L["area"]
    if tm >= T_DROP0:
        if tm < T_LAND:
            p = (tm - T_DROP0) / (T_LAND - T_DROP0)
            dy = -820 * (1 - p * p)
            sc = 1.36 - 0.26 * p
            for g, al in ((2, .16), (1, .32)):        # 残像（上に尾を引く）
                put(fr, a, dy=dy - g * 90 * (.4 + p), sx=sc, sy=sc * 1.06, alpha=al, pivot=(.2, 1))
            put(fr, a, dy=dy, sx=sc, sy=sc * 1.05, pivot=(.2, 1))
        else:
            u = tm - T_LAND
            w = math.exp(-u * 13) * math.cos(u * 2 * math.pi * 5.2)
            put(fr, a, sx=1 + .16 * w, sy=1 - .24 * w, pivot=(.3, 1))

    # アイコン：ポン（少し回りながら）
    if tm >= T_ICON:
        p = (tm - T_ICON) / .28
        sc = .2 + .8 * back_out(p, 3.0)
        put(fr, L["icon"], sx=sc, sy=sc, angle=-40 * (1 - clamp(p)) ** 2, alpha=clamp(p * 5))

    # 2行目：右から滑り込み（行き過ぎて戻る）
    if tm >= T_L2_0:
        l2 = L["line2"]
        p = (tm - T_L2_0) / (T_L2_1 - T_L2_0)
        if p < 1:
            dx = 1150 * (1 - p) ** 2.2
            if p < .6:                                # 残像は遠いうちだけ（文字が読みにくくならないように）
                for g, al in ((2, .15), (1, .3)):
                    put(fr, l2, dx=dx + g * 130, alpha=al)
            put(fr, l2, dx=dx, sx=1 + .1 * (1 - p), pivot=(0, .5))
        else:
            u = tm - T_L2_1
            w = math.exp(-u * 15) * math.cos(u * 2 * math.pi * 6)
            put(fr, l2, sx=1 - .09 * w, sy=1 + .09 * w, pivot=(0, .5))

    # ピル
    if tm >= T_PILL:
        p = (tm - T_PILL) / .25
        sc = .4 + .6 * back_out(p, 2.6)
        put(fr, L["pill"], sx=sc, sy=sc, alpha=clamp(p * 5), pivot=(0, .5))

    # 会社カード：1枚ずつポン
    for i in range(n):
        t0 = T_CARD0 + i * CARD_STEP
        if tm >= t0:
            p = (tm - t0) / .3
            sc = .55 + .45 * back_out(p, 2.8)
            put(fr, L[f"card{i}"], dy=70 * (1 - clamp(p)) ** 2, sx=sc, sy=sc, alpha=clamp(p * 4))

    # 保存のひと言：ピョコ → 左右に揺れる → もう一度だけ小さく揺れる
    c = L["cta"]
    if tm >= T["cta"]:
        u = tm - T["cta"]
        p = u / .26
        sc = .3 + .7 * back_out(p, 3.2)
        ang = 8 * math.exp(-u * 3.2) * math.sin(u * 2 * math.pi * 4.2) if u < 1.2 else 0
        dy = 60 * (1 - clamp(p)) ** 2
        u2 = tm - T["cta2"]
        if 0 <= u2 < .9:
            ang = 5 * math.exp(-u2 * 3.5) * math.sin(u2 * 2 * math.pi * 4.2)
            sc = 1 + .06 * math.exp(-u2 * 6) * math.sin(u2 * 2 * math.pi * 2.5)
        put(fr, c, dy=dy, sx=sc, sy=sc, angle=ang, alpha=clamp(p * 5))
        # きらめき
        for u_s in (tm - T["kiran"], u2 - .05):
            if 0 <= u_s < .7:
                ov = Image.new("RGBA", SIZE2, (0, 0, 0, 0))
                d = ImageDraw.Draw(ov)
                cx0, cy0, cx1, cy1 = c.box
                pts = [(cx0 - 6, cy0 + 4, 46, 0.0), (cx1 + 6, cy0 + 2, 54, .08),
                       (cx1 - 2, cy1 + 2, 34, .18), (cx0 + 14, cy1 + 4, 30, .24)]
                for (x, y, r, dl) in pts:
                    q = (u_s - dl) / .42
                    if 0 < q < 1:
                        rr = r * math.sin(q * math.pi) * S
                        star(d, x * S, y * S, rr, ms.WHITE + (255,))
                        star(d, x * S, y * S, rr * .62, (255, 214, 40, 255))
                ov = ov.resize((W, H), Image.LANCZOS)
                fr = Image.alpha_composite(fr.convert("RGBA"), ov).convert("RGB")

    # 着地の効果と揺れ
    ax0, ay0, ax1, ay1 = a.box
    fr = impact_fx(fr, tm - T_LAND, (ax0 + ax1) / 2, ay1 - 30)
    fr = shake(fr, tm - T_LAND, 1.0)
    fr = shake(fr, tm - T_L2_1, 0.28)
    return fr


# ---------- 効果音（すべて合成） ----------
def _t(dur):
    return np.arange(int(SR * dur)) / SR


def _lp(x, fc):
    """かんたんなローパス（1次）。fc は数値か配列"""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def se_don():
    """着地「ドン」: 低い音が下がりながら消える ＋ 短い打撃音。スマホでも聞こえる帯域を足す"""
    t = _t(.55)
    f = 55 + 150 * np.exp(-t * 22)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    mid = (np.sin(ph * 2) * .45 + np.sin(ph * 3) * .25) * np.exp(-t * 13)
    rng = np.random.default_rng(1)
    nz = _lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 55) * 1.2
    x = np.tanh((body + mid + nz) * 1.6)
    return x * np.minimum(1, t / .002)


def se_whoosh(dur=.2, f0=500, f1=3500, seed=2):
    """「シュッ」: 風切り音（雑音の明るさを上げていく）"""
    t = _t(dur)
    rng = np.random.default_rng(seed)
    p = t / dur
    x = _lp(rng.standard_normal(len(t)), f0 + (f1 - f0) * p ** 2)
    x = x - _lp(x, 250)
    env = np.sin(np.pi * p ** 1.6) ** 1.5
    return x * env


def se_tan():
    """2行目の着地「タン」"""
    t = _t(.2)
    f = 170 + 260 * np.exp(-t * 45)
    ph = 2 * np.pi * np.cumsum(f) / SR
    rng = np.random.default_rng(3)
    nz = _lp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90) * .5
    return (np.sin(ph) + .3 * np.sin(2 * ph)) * np.exp(-t * 22) + nz


def se_pon(freq=523.0, dur=.26):
    """「ポン」: 丸い音。出だしだけ音程が高い"""
    t = _t(dur)
    f = freq * (1 + .55 * np.exp(-t * 55))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + .22 * np.sin(2 * ph) + .08 * np.sin(3 * ph)) * np.exp(-t * 17)
    return x * np.minimum(1, t / .003)


def se_pyoko():
    """「ピョコ」: 音程がすばやく上がる"""
    t = _t(.16)
    f = 420 + 700 * (t / .16) ** .7
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + .2 * np.sin(2 * ph)) * np.sin(np.pi * t / .16) ** .8


def se_kiran():
    """「キラン」: 高い鈴のような音を2つ重ねて余韻を残す"""
    dur = 1.1
    t = _t(dur)
    x = np.zeros(len(t))
    for f, st, g in ((1568, 0.0, .8), (2093, .07, 1.0), (3136, .13, .45)):
        tt = np.maximum(t - st, 0)
        on = (t >= st)
        tone = (np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * f * 2.01 * tt)
                + .15 * np.sin(2 * np.pi * f * 3.02 * tt))
        x += on * g * tone * np.exp(-tt * 5.5) * np.minimum(1, tt / .004)
    return x * (1 + .25 * np.sin(2 * np.pi * 9 * t))


def make_audio(n, T, wav_path):
    se_dir = os.path.join(HERE, "se")
    os.makedirs(se_dir, exist_ok=True)
    mix = np.zeros(int(SR * DUR))
    saved = {}

    def add(name, x, at, gain):
        x = x / (np.max(np.abs(x)) + 1e-9)
        saved[name] = x
        i = int(at * SR)
        j = min(len(mix), i + len(x))
        mix[i:j] += x[: j - i] * gain

    add("whoosh_drop", se_whoosh(.2, 400, 2600, 2), T_DROP0, .22)
    add("don", se_don(), T_LAND, 1.0)
    add("whoosh_slide", se_whoosh(.2, 700, 4500, 5), T_L2_0, .2)
    add("tan", se_tan(), T_L2_1, .42)
    add("pon_small_a", se_pon(880, .16), T_ICON, .2)
    add("pon_small_b", se_pon(988, .16), T_PILL, .2)
    notes = [523.25, 659.25, 783.99, 1046.5]
    for i in range(n):
        add(f"pon_{i + 1}", se_pon(notes[i]), T_CARD0 + i * CARD_STEP, .5)
    add("pyoko", se_pyoko(), T["cta"], .32)
    add("kiran", se_kiran(), T["kiran"], .36)
    add("kiran_soft", se_kiran(), T["cta2"] + .05, .13)

    # ピークを抑える（書き出し後で -6dB 前後）。最後は無音で終わらせる
    peak = np.max(np.abs(mix))
    mix = mix / peak * 0.36   # AACにすると山が少し伸びるので余裕をとる
    fade = int(SR * .05)
    mix[-fade:] *= np.linspace(1, 0, fade)

    def write(path, x, g=1.0):
        pcm = (np.clip(x * g, -1, 1) * 32767).astype("<i2")
        st = np.repeat(pcm[:, None], 2, axis=1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(st.tobytes())

    write(wav_path, mix)
    for k, x in saved.items():
        write(os.path.join(se_dir, k + ".wav"), x, .5)


# ---------- 書き出し ----------
def make_video(out_name, check_name, **spec):
    L, final, n, t_theme = build(**spec)
    cta_t = T_CARD0 + n * CARD_STEP + .25
    T = dict(cta=cta_t, kiran=cta_t + .22, cta2=cta_t + 2.3)
    T["static"] = T["cta2"] + 1.0
    out = os.path.join(HERE, out_name)
    wav = os.path.join(HERE, "se", out_name.replace(".mp4", "_mix.wav"))
    make_audio(n, T, wav)

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", "scale=out_color_matrix=bt709:out_range=tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
           "-t", str(DUR), "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    final_bytes = final.tobytes()
    for k in range(int(DUR * FPS)):
        tm = k / FPS
        fr = render_frame(L, final, n, t_theme, tm, T)
        pr.stdin.write(final_bytes if fr is final else fr.tobytes())
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("saved", out, f"(静止は {T['static']:.2f}秒〜{DUR}秒)")
    check_sheet(out, check_name)


def check_sheet(mp4, check_name):
    """出来た動画から 0.2 / 0.5 / 1.0 / 2.0秒 / 最後 のコマを抜いて並べる"""
    chk = os.path.join(os.path.dirname(HERE), "_check")
    os.makedirs(chk, exist_ok=True)
    stamps = [("0.2秒", 0.2), ("0.5秒", 0.5), ("1.0秒", 1.0), ("2.0秒", 2.0), ("最後", DUR - 1 / FPS)]
    cw, chh = W // 2, H // 2
    sheet = Image.new("RGB", (len(stamps) * (cw + 12) + 12, chh + 80), (50, 50, 50))
    d = ImageDraw.Draw(sheet)
    f = ms.ImageFont.truetype(ms.FONT_B, 40)
    for i, (lab, ts) in enumerate(stamps):
        tmp = os.path.join(chk, f"_tmp_{i}.png")
        n = round(ts * FPS)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4,
                        "-vf", f"select=eq(n\\,{n})", "-frames:v", "1", tmp], check=True)
        im = Image.open(tmp).convert("RGBA")
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        do = ImageDraw.Draw(ov)
        do.rectangle((0, 0, W, ms.SAFE_TOP), fill=(0, 0, 0, 90))       # 上下250pxの目安
        do.rectangle((0, ms.SAFE_BOTTOM, W, H), fill=(0, 0, 0, 90))
        im = Image.alpha_composite(im, ov).convert("RGB").resize((cw, chh), Image.LANCZOS)
        x = 12 + i * (cw + 12)
        sheet.paste(im, (x, 68))
        d.text((x + 8, 8), lab, font=f, fill=(255, 255, 255))
        os.remove(tmp)
    path = os.path.join(chk, check_name)
    sheet.save(path, quality=90)
    print("saved", path)


if __name__ == "__main__":
    # 1) 北薩 × 工務店（3社・緑）
    make_video("01_hokusatsu_koumuten.mp4", "motion_frames_01_hokusatsu.jpg",
               kind="house", edition="マイタウンガイド 北薩版", area="北薩", particle="で",
               line2="家を建てるなら", pill="おすすめ工務店・建築会社　3社", companies=ms.HOUSE,
               footer="マイタウンガイド2026（北薩版）に掲載中")
    # 2) 奄美大島 × 車屋さん（2社・水色）
    make_video("02_amami_kuruma.mp4", "motion_frames_02_amami.jpg",
               kind="car", edition="マイタウンガイド 奄美大島版", area="奄美大島", particle="で",
               line2="車のことなら", pill="車検・修理・中古車　おすすめ2社", companies=ms.CAR,
               footer="マイタウンガイド2026（奄美大島版）に掲載中")
