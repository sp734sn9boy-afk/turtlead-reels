#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マイタウンガイド「エリア×業種のおすすめまとめ」ストーリーズ見本（1080x1920）

使い方:  python3 make_stories.py
出力先:  このスクリプトと同じフォルダ

素材の出どころ:
  - フォント: Noto Sans CJK JP Bold / Regular（SIL Open Font License 1.1、
    Ubuntu の fonts-noto-cjk パッケージ）
  - アイコン（家・フォークとナイフ・車・電話・しおり）: このスクリプト内で図形から自作
  - 写真・他社ロゴ・人物素材: 使っていない
  - 会社名・電話番号: すべて架空のダミー

型のルール:
  - 上下 250px は Instagram の画面部品に隠れるので文字を置かない（SAFE_TOP / SAFE_BOTTOM）
  - 見出しは2行。1行目=地名（特大・黄色）、2行目=何の話か（白）
  - 業種ごとに色とアイコンを変える（THEMES）
"""
import os
from PIL import Image, ImageDraw, ImageFont

S = 2                      # 2倍で描いて縮小（ふちをなめらかにする）
W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 250, 1670
MX = 60                    # 左右の余白
OUT = os.path.dirname(os.path.abspath(__file__))

FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

CREAM = (255, 247, 230)
INK = (51, 40, 32)         # こげ茶（黒より柔らかい）
SUB = (110, 94, 82)
YELLOW = (255, 226, 60)
WHITE = (255, 255, 255)

THEMES = {
    "house": dict(main=(27, 158, 92), dark=(13, 100, 56), pale=(226, 244, 232)),
    "food": dict(main=(240, 84, 40), dark=(168, 48, 14), pale=(255, 232, 220)),
    "car": dict(main=(8, 150, 190), dark=(4, 96, 126), pale=(220, 242, 248)),
}


def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, int(size * S), index=0)


def P(*v):
    """座標を2倍にする"""
    if len(v) == 1:
        v = v[0]
    return tuple(int(round(x * S)) for x in v)


def text_w(d, s, f, stroke=0):
    return d.textlength(s, font=f) / S + stroke * 2


def draw_text(d, xy, s, f, fill, stroke=0, shadow=None, shadow_off=6, anchor="ls"):
    """stroke は同じ色のふち取りで文字を太らせる（極太ウェイトの代わり）"""
    x, y = xy
    sw = int(stroke * S)
    if shadow:
        d.text(P(x + shadow_off, y + shadow_off), s, font=f, fill=shadow,
               stroke_width=sw, stroke_fill=shadow, anchor=anchor)
    d.text(P(x, y), s, font=f, fill=fill, stroke_width=sw, stroke_fill=fill, anchor=anchor)


def fit_size(d, s, max_w, start, stroke=0, min_size=40):
    size = start
    while size > min_size and text_w(d, s, font(size), stroke) > max_w:
        size -= 2
    return size


# ---------- アイコン（自作） ----------
def icon_house(d, cx, cy, r, col):
    d.polygon([P(cx - r * .62, cy - r * .02), P(cx, cy - r * .58), P(cx + r * .62, cy - r * .02)], fill=col)
    d.rectangle(P(cx - r * .44, cy - r * .04, cx + r * .44, cy + r * .5), fill=col)
    d.rectangle(P(cx + r * .26, cy - r * .5, cx + r * .4, cy - r * .2), fill=col)   # えんとつ
    d.rounded_rectangle(P(cx - r * .12, cy + r * .12, cx + r * .12, cy + r * .5), radius=int(r * .04 * S), fill=WHITE)


def icon_food(d, cx, cy, r, col):
    # 皿
    d.ellipse(P(cx - r * .36, cy - r * .36, cx + r * .36, cy + r * .36), fill=col)
    d.ellipse(P(cx - r * .22, cy - r * .22, cx + r * .22, cy + r * .22), fill=WHITE)
    # フォーク（左）
    fx = cx - r * .56
    for dx in (-.08, 0, .08):
        d.rounded_rectangle(P(fx + r * dx - r * .022, cy - r * .5, fx + r * dx + r * .022, cy - r * .2),
                            radius=int(r * .02 * S), fill=col)
    d.rounded_rectangle(P(fx - r * .1, cy - r * .26, fx + r * .1, cy - r * .12), radius=int(r * .05 * S), fill=col)
    d.rounded_rectangle(P(fx - r * .035, cy - r * .2, fx + r * .035, cy + r * .5), radius=int(r * .03 * S), fill=col)
    # ナイフ（右）
    kx = cx + r * .56
    d.pieslice(P(kx - r * .12, cy - r * .52, kx + r * .12, cy + r * .1), 270, 90, fill=col)
    d.rounded_rectangle(P(kx - r * .035, cy - r * .5, kx + r * .035, cy + r * .5), radius=int(r * .03 * S), fill=col)


def icon_car(d, cx, cy, r, col):
    # 屋根
    d.polygon([P(cx - r * .4, cy - r * .04), P(cx - r * .24, cy - r * .36), P(cx + r * .2, cy - r * .36),
               P(cx + r * .42, cy - r * .04)], fill=col)
    # 窓
    d.polygon([P(cx - r * .27, cy - r * .06), P(cx - r * .17, cy - r * .27), P(cx - r * .04, cy - r * .27),
               P(cx - r * .04, cy - r * .06)], fill=WHITE)
    d.polygon([P(cx + r * .04, cy - r * .06), P(cx + r * .04, cy - r * .27), P(cx + r * .15, cy - r * .27),
               P(cx + r * .29, cy - r * .06)], fill=WHITE)
    # 車体
    d.rounded_rectangle(P(cx - r * .66, cy - r * .08, cx + r * .66, cy + r * .24), radius=int(r * .1 * S), fill=col)
    # タイヤ
    for wx in (-.36, .36):
        d.ellipse(P(cx + r * wx - r * .17, cy + r * .08, cx + r * wx + r * .17, cy + r * .42), fill=WHITE)
        d.ellipse(P(cx + r * wx - r * .12, cy + r * .13, cx + r * wx + r * .12, cy + r * .37), fill=col)


ICONS = {"house": icon_house, "food": icon_food, "car": icon_car}


def icon_phone(d, x, y, size, col):
    """「TEL」の小さなラベル（幅は size*1.9、高さは size）"""
    d.rounded_rectangle(P(x, y, x + size * 1.9, y + size), radius=int(size * .22 * S), fill=col)
    draw_text(d, (x + size * .95, y + size * .47), "TEL", font(size * .62), WHITE, anchor="mm")


def icon_bookmark(d, x, y, w, h, col):
    d.polygon([P(x, y), P(x + w, y), P(x + w, y + h), P(x + w / 2, y + h * .72), P(x, y + h)], fill=col)


# ---------- 本体 ----------
def make(path, kind, edition, area, particle, line2, pill, companies, footer,
         area_size=210, line2_size=140, cta="保存して、あとで見返してね"):
    """
    area + particle が1行目（例: 北薩 + の）、line2 が2行目。
    line2 は文字列、または [(文字, "white"|"yellow"|"big"), ...] のリスト。
    """
    t = THEMES[kind]
    img = Image.new("RGB", (W * S, H * S), CREAM)
    d = ImageDraw.Draw(img)

    n = len(companies)
    head_bottom = 868

    # --- 上の色面 ---
    d.rectangle(P(0, 0, W, head_bottom), fill=t["main"])
    # 太いななめ帯（色面だけで動きを出す）
    band = tuple(int(m * .88 + k * .12) for m, k in zip(t["main"], t["dark"]))
    d.polygon([P(W * .52, 0), P(W * .9, 0), P(W * .38, head_bottom), P(0, head_bottom)], fill=band)
    d.rectangle(P(0, head_bottom, W, H), fill=CREAM)
    # 波型の切り替え（やわらかさ）
    rr = 45
    for i in range(-1, W // (rr * 2) + 2):
        cx = i * rr * 2 + rr
        d.ellipse(P(cx - rr, head_bottom - rr, cx + rr, head_bottom + rr), fill=t["main"])

    # --- PR と版名（小さく） ---
    y = SAFE_TOP + 22
    f_pr = font(30)
    d.rounded_rectangle(P(MX, y, MX + 92, y + 48), radius=int(10 * S), fill=WHITE)
    draw_text(d, (MX + 46, y + 24), "PR", f_pr, t["dark"], anchor="mm")
    draw_text(d, (MX + 110, y + 24), edition, font(32), WHITE, anchor="lm")

    # --- 見出し 1行目: 地名（特大） + アイコン ---
    icon_r = 100
    stroke1 = 2
    max_w1 = W - MX * 2 - icon_r * 2 - 24
    p_size_ratio = 0.56
    size = area_size
    while size > 80:
        w_area = text_w(d, area, font(size), stroke1)
        w_part = text_w(d, particle, font(size * p_size_ratio), 1.5) if particle else 0
        if w_area + w_part + 6 <= max_w1:
            break
        size -= 2
    f_area = font(size)
    base1 = 342 + 205                       # 1行目のベースライン
    draw_text(d, (MX + stroke1, base1), area, f_area, YELLOW, stroke=stroke1, shadow=t["dark"], shadow_off=7)
    if particle:
        draw_text(d, (MX + w_area + 10, base1), particle, font(size * p_size_ratio), WHITE, stroke=1.5,
                  shadow=t["dark"], shadow_off=5)
    # アイコン（白丸の中）
    icx, icy = W - MX - icon_r, base1 - 92
    d.ellipse(P(icx - icon_r + 7, icy - icon_r + 7, icx + icon_r + 7, icy + icon_r + 7), fill=t["dark"])
    d.ellipse(P(icx - icon_r, icy - icon_r, icx + icon_r, icy + icon_r), fill=WHITE)
    ICONS[kind](d, icx, icy, icon_r * 1.12, t["main"])

    # --- 見出し 2行目 ---
    stroke2 = 1.5
    segs = [(line2, "white")] if isinstance(line2, str) else line2

    def seg_font(sz, style):
        return font(sz * (1.42 if style == "big" else 1))

    sz2 = line2_size
    while sz2 > 60:
        tot = sum(text_w(d, s, seg_font(sz2, st), stroke2) for s, st in segs)
        if tot <= W - MX * 2:
            break
        sz2 -= 2
    base2 = base1 + 46 + sz2 * 0.98
    base2 = min(base2, 742)
    x = MX
    for s, st in segs:
        f = seg_font(sz2, st)
        col = WHITE if st == "white" else YELLOW
        draw_text(d, (x + stroke2, base2), s, f, col, stroke=stroke2, shadow=t["dark"], shadow_off=6)
        x += text_w(d, s, f, stroke2)

    # --- 補足のピル ---
    f_pill = font(36)
    pw = text_w(d, pill, f_pill) + 56
    py = 772
    d.rounded_rectangle(P(MX, py, MX + pw, py + 62), radius=int(31 * S), fill=WHITE)
    draw_text(d, (MX + 28, py + 30), pill, f_pill, t["dark"], anchor="lm")

    # --- 会社カード ---
    cards_top, cards_bottom = 940, 1478
    gap = 18 if n >= 4 else 26
    ch = min((cards_bottom - cards_top - gap * (n - 1)) / n, 250)
    total = ch * n + gap * (n - 1)
    cy0 = cards_top + (cards_bottom - cards_top - total) / 2
    compact = n >= 3
    big = 1.0 if n >= 4 else 1.12
    for i, (name, strong, tel) in enumerate(companies):
        top = cy0 + i * (ch + gap)
        # 影 + 白カード
        d.rounded_rectangle(P(MX + 6, top + 8, W - MX + 6, top + ch + 8), radius=int(26 * S), fill=t["pale"])
        d.rounded_rectangle(P(MX, top, W - MX, top + ch), radius=int(26 * S), fill=WHITE,
                            outline=t["main"], width=int(4 * S))
        # 番号
        nr = (38 * big) if compact else 50
        ncx, ncy = MX + 28 + nr, top + ch / 2
        d.ellipse(P(ncx - nr, ncy - nr, ncx + nr, ncy + nr), fill=t["main"])
        draw_text(d, (ncx, ncy - 3), str(i + 1), font(52 * big if compact else 66), WHITE, anchor="mm")
        tx = ncx + nr + 26
        inner_w = W - MX - 28 - tx
        if compact:
            # 1行目: 会社名（左）＋電話（右） / 2行目: 強み
            f_tel = font(40 * big)
            lab = 30 * big
            tel_w = text_w(d, tel, f_tel) + lab * 1.9 + 12
            ns = fit_size(d, name, inner_w - tel_w - 16, 47 * big)
            row1 = top + ch * .32
            draw_text(d, (tx, row1), name, font(ns), INK, anchor="lm")
            icon_phone(d, W - MX - 28 - tel_w, row1 - lab / 2 + 2, lab, t["main"])
            draw_text(d, (W - MX - 28, row1), tel, f_tel, t["dark"], anchor="rm")
            draw_text(d, (tx, top + ch * .75), strong,
                      font(fit_size(d, strong, inner_w, 36 * big), bold=False), SUB, anchor="lm")
        else:
            ns = fit_size(d, name, inner_w, 68)
            draw_text(d, (tx, top + ch * .23), name, font(ns), INK, anchor="lm")
            draw_text(d, (tx, top + ch * .51), strong, font(fit_size(d, strong, inner_w, 42), bold=False),
                      SUB, anchor="lm")
            icon_phone(d, tx, top + ch * .79 - 20, 42, t["main"])
            draw_text(d, (tx + 42 * 1.9 + 16, top + ch * .79), tel, font(58), t["dark"], anchor="lm")

    # --- 行動のひと言 ---
    f_cta = font(40)
    cw = text_w(d, cta, f_cta) + 34 + 22 + 80
    cx0 = (W - cw) / 2
    cy = 1506
    d.rounded_rectangle(P(cx0 + 5, cy + 6, cx0 + cw + 5, cy + 80 + 6), radius=int(40 * S), fill=t["dark"])
    d.rounded_rectangle(P(cx0, cy, cx0 + cw, cy + 80), radius=int(40 * S), fill=YELLOW)
    icon_bookmark(d, cx0 + 40, cy + 20, 34, 42, INK)
    draw_text(d, (cx0 + 40 + 34 + 22, cy + 38), cta, f_cta, INK, anchor="lm")

    # --- フッター ---
    draw_text(d, (W / 2, 1632), footer, font(34), t["dark"], anchor="mm")

    img = img.resize((W, H), Image.LANCZOS)
    img.save(path, quality=95)
    print("saved", path)
    return img


def guide(img, path):
    """確認用: Instagramの画面部品に隠れる範囲（上下250px）を灰色で示す"""
    g = img.copy().convert("RGBA")
    ov = Image.new("RGBA", g.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle((0, 0, W, SAFE_TOP), fill=(0, 0, 0, 120))
    d.rectangle((0, SAFE_BOTTOM, W, H), fill=(0, 0, 0, 120))
    Image.alpha_composite(g, ov).convert("RGB").save(path, quality=90)


HOUSE = [
    ("〇〇工務店", "木の家づくり50年。相談無料", "0996-00-0000"),
    ("△△建設", "新築もリフォームもおまかせ", "0996-00-0001"),
    ("□□ホーム", "平屋が得意。見学会を開催中", "0996-00-0002"),
]
FOOD = [
    ("〇〇食堂", "日替わり定食がボリューム満点", "0995-00-0000"),
    ("カフェ△△", "手作りランチと自家製スイーツ", "0995-00-0001"),
    ("そば処□□", "打ちたてのそばと天ぷら", "0995-00-0002"),
    ("洋食◇◇亭", "黒豚ハンバーグが看板メニュー", "0995-00-0003"),
]
CAR = [
    ("〇〇モータース", "車検・修理は当日お返しOK", "0997-00-0000"),
    ("△△自動車", "軽の中古車がいつも30台以上", "0997-00-0001"),
]

if __name__ == "__main__":
    imgs = {}
    # 1) 住まい：北薩×工務店（3社）
    imgs["01"] = make(os.path.join(OUT, "01_hokusatsu_koumuten.png"), "house",
                      "マイタウンガイド 北薩版", "北薩", "の", "おすすめ工務店",
                      "工務店・建築会社　3社をご紹介", HOUSE,
                      "マイタウンガイド2026（北薩版）に掲載中")
    # 2) 飲食：霧島市×ランチ（4社）
    imgs["02"] = make(os.path.join(OUT, "02_kirishima_lunch.png"), "food",
                      "マイタウンガイド 霧島市版", "霧島", "で", "ランチに迷ったら",
                      "霧島市のおすすめランチ　4店", FOOD,
                      "マイタウンガイド2026（霧島市版）に掲載中")
    # 3) 車：奄美大島×車屋さん（2社）
    imgs["03"] = make(os.path.join(OUT, "03_amami_kuruma.png"), "car",
                      "マイタウンガイド 奄美大島版", "奄美大島", "の", "たよれる車屋さん",
                      "車検・修理・中古車　2社をご紹介", CAR,
                      "マイタウンガイド2026（奄美大島版）に掲載中")
    # 見出しの別案（1枚目と同じ型）
    # 別案A：問いかけ型「北薩で 家を建てるなら」
    imgs["01A"] = make(os.path.join(OUT, "01_altA_toikake.png"), "house",
                       "マイタウンガイド 北薩版", "北薩", "で", "家を建てるなら",
                       "おすすめ工務店・建築会社　3社", HOUSE,
                       "マイタウンガイド2026（北薩版）に掲載中")
    # 別案B：数字型「北薩の 工務店 3選」（数字を特大に）
    imgs["01B"] = make(os.path.join(OUT, "01_altB_suuji.png"), "house",
                       "マイタウンガイド 北薩版", "北薩", "の",
                       [("工務店", "white"), (" 3", "big"), ("選", "yellow")],
                       "家づくり・リフォームの相談先", HOUSE,
                       "マイタウンガイド2026（北薩版）に掲載中")
    # 確認用
    chk = os.path.join(OUT, "_check")
    os.makedirs(chk, exist_ok=True)
    for k, im in imgs.items():
        guide(im, os.path.join(chk, f"{k}_safe.jpg"))
    sheet = Image.new("RGB", (W * 5 // 2 + 60, H // 2 + 20), (60, 60, 60))
    for i, k in enumerate(imgs):
        sheet.paste(imgs[k].resize((W // 2, H // 2), Image.LANCZOS), (10 + i * (W // 2 + 10), 10))
    sheet.save(os.path.join(chk, "all.jpg"), quality=88)
