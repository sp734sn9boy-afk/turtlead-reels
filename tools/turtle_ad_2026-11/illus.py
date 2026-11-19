"""見本リール用のイラスト（自作・PILで描画。人物・実在ロゴなし）"""
import random
from PIL import Image, ImageDraw, ImageFilter

S = 2  # 内部2倍で描いて縮小（なめらかにする）


def _canvas(w, h, top, bot, s=S):
    g = Image.linear_gradient('L').resize((w * s, h * s))
    return Image.composite(Image.new('RGB', (w * s, h * s), bot), Image.new('RGB', (w * s, h * s), top), g)


def _shadow(img, box, r=40, off=(0, 30), blur=40, alpha=90, ellipse=False):
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    b = (box[0] + off[0], box[1] + off[1], box[2] + off[0], box[3] + off[1])
    (d.ellipse if ellipse else d.rounded_rectangle)(b, **({} if ellipse else {'radius': r}), fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(sh, (0, 0), sh)


def _wood(img, y0, c1=(196, 150, 104), c2=(170, 124, 82)):
    d = ImageDraw.Draw(img)
    w, h = img.size
    d.rectangle((0, y0, w, h), fill=c1)
    random.seed(3)
    for i in range(60):
        y = random.randint(y0, h)
        d.line((0, y, w, y + random.randint(-20, 20)), fill=c2, width=random.randint(2, 6))


def _fin(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def cafe_lunch(w=1080, h=1440):
    img = _canvas(w, h, (250, 238, 220), (232, 214, 190))
    _wood(img, 0)
    d = ImageDraw.Draw(img)
    W, H = img.size
    # トレイ
    tb = (W * .08, H * .12, W * .92, H * .88)
    _shadow(img, tb, 60)
    d.rounded_rectangle(tb, 60, fill=(150, 100, 60))
    d.rounded_rectangle((tb[0] + 30, tb[1] + 30, tb[2] - 30, tb[3] - 30), 44, fill=(176, 122, 74))
    # メイン皿
    cx, cy, r = W * .5, H * .38, W * .3
    _shadow(img, (cx - r, cy - r, cx + r, cy + r), ellipse=True, blur=30)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 250, 246))
    d.ellipse((cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8), outline=(230, 228, 220), width=6)
    # ハンバーグ
    d.ellipse((cx - r * .55, cy - r * .2, cx + r * .15, cy + r * .45), fill=(110, 60, 34))
    d.ellipse((cx - r * .5, cy - r * .15, cx + r * .1, cy + r * .2), fill=(130, 72, 40))
    d.ellipse((cx - r * .45, cy - r * .05, cx + r * .2, cy + r * .4), fill=(88, 40, 22))
    # サラダ
    random.seed(5)
    for i in range(40):
        x = cx + random.uniform(.05, .55) * r
        y = cy + random.uniform(-.55, .1) * r
        col = random.choice([(110, 180, 80), (140, 200, 90), (90, 160, 70), (230, 70, 60), (250, 200, 60)])
        rr = random.uniform(.06, .13) * r
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)
    # ごはん
    for (bx, by, col, kind) in [(W * .25, H * .7, (245, 245, 240), 'rice'), (W * .5, H * .74, (200, 160, 110), 'soup'), (W * .75, H * .7, (240, 236, 226), 'side')]:
        rb = W * .11
        _shadow(img, (bx - rb, by - rb, bx + rb, by + rb), ellipse=True, blur=20, alpha=80)
        d.ellipse((bx - rb, by - rb, bx + rb, by + rb), fill=(60, 50, 44) if kind != 'side' else (250, 250, 246))
        d.ellipse((bx - rb * .82, by - rb * .82, bx + rb * .82, by + rb * .82), fill=col)
        if kind == 'rice':
            for i in range(60):
                x, y = bx + random.uniform(-.7, .7) * rb, by + random.uniform(-.7, .7) * rb
                d.ellipse((x - 6, y - 4, x + 6, y + 4), fill=(255, 255, 255))
        if kind == 'soup':
            for i in range(6):
                x, y = bx + random.uniform(-.5, .5) * rb, by + random.uniform(-.5, .5) * rb
                d.rectangle((x - 12, y - 12, x + 12, y + 12), fill=(250, 248, 236))
            d.ellipse((bx - 30, by - 50, bx + 30, by - 10), fill=(60, 120, 60))
        if kind == 'side':
            d.ellipse((bx - rb * .5, by - rb * .4, bx + rb * .5, by + rb * .4), fill=(250, 210, 80))
    # 箸
    d.line((W * .12, H * .85, W * .6, H * .83), fill=(80, 50, 30), width=14)
    d.line((W * .12, H * .87, W * .6, H * .855), fill=(80, 50, 30), width=14)
    return _fin(img, w, h)


def cafe_interior(w=1080, h=1440):
    img = _canvas(w, h, (246, 236, 220), (236, 222, 202), s=1)
    d = ImageDraw.Draw(img)
    W, H = img.size
    # 窓
    for i in range(3):
        x0 = W * (.08 + i * .3)
        d.rounded_rectangle((x0, H * .1, x0 + W * .26, H * .5), 20, fill=(200, 226, 236), outline=(140, 100, 70), width=18)
        d.line((x0 + W * .13, H * .1, x0 + W * .13, H * .5), fill=(140, 100, 70), width=12)
        d.ellipse((x0 + W * .02, H * .3, x0 + W * .2, H * .48), fill=(150, 200, 140))
    # 床
    _wood(img, int(H * .62), (180, 130, 86), (160, 112, 72))
    d.rectangle((0, H * .58, W, H * .62), fill=(150, 104, 66))
    # ペンダントライト
    for i in range(3):
        x = W * (.2 + i * .3)
        d.line((x, 0, x, H * .2), fill=(60, 50, 40), width=6)
        d.pieslice((x - 80, H * .17, x + 80, H * .29), 180, 360, fill=(60, 60, 56))
        gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse((x - 160, H * .2, x + 160, H * .36), fill=(255, 220, 140, 110))
        gl = gl.filter(ImageFilter.GaussianBlur(50))
        img.paste(gl, (0, 0), gl)
        d = ImageDraw.Draw(img)
    # テーブルといす
    for i, x in enumerate([W * .27, W * .73]):
        y = H * .72
        _shadow(img, (x - 220, y + 160, x + 220, y + 220), ellipse=True, blur=25, alpha=70, off=(0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle((x - 18, y, x + 18, y + 190), fill=(80, 56, 38))
        d.ellipse((x - 230, y - 50, x + 230, y + 40), fill=(120, 82, 52))
        d.ellipse((x - 230, y - 62, x + 230, y + 22), fill=(150, 104, 66))
        for s in (-1, 1):
            cx = x + s * 300
            d.rounded_rectangle((cx - 70, y - 160, cx + 70, y + 20), 20, fill=(90, 120, 100))
            d.rectangle((cx - 70, y + 10, cx + 70, y + 40), fill=(70, 96, 80))
            d.rectangle((cx - 60, y + 40, cx - 46, y + 200), fill=(60, 44, 30))
            d.rectangle((cx + 46, y + 40, cx + 60, y + 200), fill=(60, 44, 30))
        d.ellipse((x - 40, y - 100, x + 40, y - 30), fill=(250, 250, 246))
    # 観葉植物
    px = W * .93
    d.polygon([(px - 70, H * .6), (px + 70, H * .6), (px + 50, H * .72), (px - 50, H * .72)], fill=(200, 180, 150))
    for a in range(9):
        random.seed(a)
        ox, oy = random.randint(0, 140), random.randint(0, 260)
        d.ellipse((px - 120 + ox, H * .38 + oy, px - 20 + ox, H * .44 + oy), fill=random.choice([(70, 140, 80), (90, 160, 90), (60, 120, 70)]))
    return _fin(img, w, h)


def cafe_exterior(w=1080, h=1440, sign='CAFE'):
    img = _canvas(w, h, (150, 200, 240), (210, 232, 246))
    d = ImageDraw.Draw(img)
    W, H = img.size
    # 雲
    for (x, y, s) in [(.2, .08, 1), (.75, .12, .8)]:
        for k in range(4):
            d.ellipse((W * x - 120 * s + k * 70 * s, H * y - 40 * s - (k % 2) * 30 * s, W * x + k * 70 * s, H * y + 50 * s), fill=(255, 255, 255))
    # 建物
    d.rectangle((W * .08, H * .22, W * .92, H * .8), fill=(244, 236, 222))
    d.polygon([(W * .04, H * .24), (W * .5, H * .12), (W * .96, H * .24)], fill=(110, 80, 60))
    # オーニング
    aw_y = H * .4
    for i in range(10):
        x0 = W * .1 + i * (W * .8 / 10)
        d.polygon([(x0, aw_y), (x0 + W * .08, aw_y), (x0 + W * .08 + 10, aw_y + 110), (x0 - 10, aw_y + 110)], fill=(60, 120, 100) if i % 2 == 0 else (250, 248, 240))
    # 看板（架空）
    d.rounded_rectangle((W * .3, H * .27, W * .7, H * .36), 20, fill=(70, 50, 40))
    from tad import font
    f = font('black', 110)
    tw = d.textlength(sign, font=f)
    d.text((W * .5 - tw / 2, H * .27 + 4), sign, font=f, fill=(250, 236, 200))
    # 窓とドア
    d.rectangle((W * .14, H * .5, W * .44, H * .72), fill=(190, 220, 230), outline=(90, 64, 46), width=14)
    d.rectangle((W * .56, H * .48, W * .78, H * .8), fill=(120, 84, 56))
    d.rectangle((W * .6, H * .52, W * .74, H * .66), fill=(190, 220, 230))
    d.ellipse((W * .74, H * .64, W * .76, H * .66), fill=(230, 200, 120))
    # 地面と植木
    d.rectangle((0, H * .8, W, H), fill=(170, 170, 166))
    for x in (W * .1, W * .88):
        d.rectangle((x - 50, H * .74, x + 50, H * .82), fill=(160, 110, 70))
        d.ellipse((x - 90, H * .62, x + 90, H * .77), fill=(80, 150, 90))
    return _fin(img, w, h)


def cafe_coffee(w=1080, h=1440):
    img = _canvas(w, h, (240, 228, 210), (220, 200, 176), s=1)
    _wood(img, 0, (214, 176, 134), (194, 154, 114))
    d = ImageDraw.Draw(img)
    W, H = img.size
    # カップ
    cx, cy = W * .38, H * .5
    _shadow(img, (cx - 300, cy - 300, cx + 300, cy + 300), ellipse=True, blur=35)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - 300, cy - 300, cx + 300, cy + 300), fill=(250, 250, 246))
    d.ellipse((cx - 200, cy - 200, cx + 200, cy + 200), fill=(240, 238, 232))
    d.ellipse((cx - 170, cy - 170, cx + 170, cy + 170), fill=(130, 80, 44))
    d.ellipse((cx - 90, cy - 70, cx + 90, cy + 90), fill=(236, 210, 170))
    d.ellipse((cx - 40, cy - 30, cx + 40, cy + 40), fill=(130, 80, 44))
    d.rounded_rectangle((cx + 190, cy - 40, cx + 290, cy + 40), 30, fill=(250, 250, 246))
    # ケーキ
    kx, ky = W * .72, H * .78
    _shadow(img, (kx - 220, ky - 200, kx + 220, ky + 200), ellipse=True, blur=30)
    d = ImageDraw.Draw(img)
    d.ellipse((kx - 220, ky - 200, kx + 220, ky + 200), fill=(250, 250, 246))
    d.polygon([(kx - 140, ky + 60), (kx + 150, ky + 20), (kx - 20, ky - 140)], fill=(250, 230, 190))
    d.polygon([(kx - 140, ky + 60), (kx + 150, ky + 20), (kx + 150, ky + 70), (kx - 140, ky + 110)], fill=(236, 200, 150))
    d.ellipse((kx - 60, ky - 110, kx + 10, ky - 50), fill=(220, 40, 60))
    return _fin(img, w, h)


def cafe_takeout(w=1080, h=1440):
    img = _canvas(w, h, (236, 242, 238), (214, 226, 220))
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((0, H * .7, W, H), fill=(200, 170, 130))
    # 紙袋
    bx0, bx1, by0, by1 = W * .2, W * .62, H * .3, H * .82
    _shadow(img, (bx0, by0, bx1, by1), 10, off=(30, 20))
    d = ImageDraw.Draw(img)
    d.rectangle((bx0, by0, bx1, by1), fill=(200, 160, 110))
    d.rectangle((bx0, by0, bx1, by0 + 60), fill=(180, 140, 92))
    d.arc((W * .3, H * .2, W * .52, H * .36), 180, 360, fill=(120, 90, 60), width=18)
    d.ellipse((W * .33, H * .48, W * .49, H * .6), outline=(250, 240, 220), width=10)
    # ドリンク
    cx = W * .78
    d.polygon([(cx - 110, H * .46), (cx + 110, H * .46), (cx + 80, H * .82), (cx - 80, H * .82)], fill=(250, 250, 246))
    d.rectangle((cx - 120, H * .42, cx + 120, H * .47), fill=(240, 240, 236))
    d.rectangle((cx - 100, H * .58, cx + 100, H * .66), fill=(60, 120, 100))
    d.line((cx + 30, H * .42, cx + 70, H * .3), fill=(60, 60, 60), width=16)
    return _fin(img, w, h)


# ---- 美容室 ----
def salon_chair(w=1080, h=1440):
    img = _canvas(w, h, (238, 236, 232), (222, 218, 212), s=1)
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((0, H * .72, W, H), fill=(200, 196, 190))
    # 鏡
    d.rounded_rectangle((W * .22, H * .08, W * .78, H * .5), 300, fill=(206, 222, 230), outline=(190, 160, 110), width=24)
    gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).polygon([(W * .35, H * .12), (W * .45, H * .12), (W * .3, H * .46), (W * .22, H * .46)], fill=(255, 255, 255, 90))
    img.paste(gl, (0, 0), gl)
    d = ImageDraw.Draw(img)
    # 棚
    d.rectangle((W * .1, H * .52, W * .9, H * .55), fill=(190, 160, 110))
    for i, c in enumerate([(240, 200, 200), (200, 220, 240), (250, 250, 250), (220, 200, 240)]):
        x = W * (.15 + i * .07)
        d.rounded_rectangle((x, H * .45, x + 50, H * .52), 12, fill=c)
    # いす
    cx = W * .5
    _shadow(img, (cx - 260, H * .86, cx + 260, H * .92), ellipse=True, off=(0, 0), blur=25)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((cx - 190, H * .5, cx + 190, H * .7), 60, fill=(50, 50, 56))
    d.rounded_rectangle((cx - 240, H * .66, cx + 240, H * .76), 40, fill=(40, 40, 46))
    d.rounded_rectangle((cx - 270, H * .62, cx - 220, H * .72), 20, fill=(30, 30, 34))
    d.rounded_rectangle((cx + 220, H * .62, cx + 270, H * .72), 20, fill=(30, 30, 34))
    d.rectangle((cx - 25, H * .76, cx + 25, H * .86), fill=(180, 180, 186))
    d.ellipse((cx - 180, H * .84, cx + 180, H * .9), fill=(170, 170, 176))
    # 植物
    d.ellipse((W * .84, H * .4, W * .98, H * .62), fill=(110, 160, 110))
    d.rectangle((W * .87, H * .6, W * .95, H * .72), fill=(240, 240, 236))
    return _fin(img, w, h)


def salon_products(w=1080, h=1440):
    img = _canvas(w, h, (244, 238, 232), (230, 220, 210))
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((0, H * .66, W, H), fill=(250, 248, 244))
    cols = [(232, 214, 200), (200, 214, 206), (250, 250, 248), (214, 200, 220), (240, 226, 190)]
    for i, c in enumerate(cols):
        x = W * (.12 + i * .16)
        hh = H * (.28 + (i % 2) * .06)
        _shadow(img, (x, H * .66 - hh, x + W * .13, H * .66), 30, off=(16, 10), blur=20, alpha=60)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, H * .66 - hh, x + W * .13, H * .66), 34, fill=c)
        d.rectangle((x + W * .04, H * .66 - hh - 50, x + W * .09, H * .66 - hh + 5), fill=(60, 60, 60))
        d.rounded_rectangle((x + 16, H * .66 - hh * .6, x + W * .13 - 16, H * .66 - hh * .3), 10, fill=(255, 255, 255))
    # 葉
    for k in range(7):
        random.seed(k + 10)
        x = random.uniform(.1, .9) * W
        d.ellipse((x - 60, H * .76, x + 60, H * .82), fill=(150, 190, 140))
    return _fin(img, w, h)


def salon_kids(w=1080, h=1440):
    img = _canvas(w, h, (250, 244, 230), (240, 232, 214))
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((0, H * .62, W, H), fill=(170, 210, 190))
    # マット
    for i in range(4):
        for j in range(3):
            c = [(250, 200, 120), (140, 200, 230), (240, 150, 150), (180, 220, 140)][(i + j) % 4]
            d.rectangle((W * .1 + i * W * .2, H * .66 + j * H * .1, W * .1 + (i + 1) * W * .2 - 6, H * .66 + (j + 1) * H * .1 - 6), fill=c)
    # 積み木
    for k, (x, y, c) in enumerate([(.3, .6, (240, 90, 80)), (.36, .54, (80, 150, 230)), (.42, .6, (250, 200, 60)), (.7, .6, (120, 190, 120))]):
        d.rectangle((W * x, H * y, W * x + 90, H * y + 90), fill=c)
    # 本棚
    d.rectangle((W * .55, H * .2, W * .9, H * .56), fill=(200, 160, 110))
    for r in range(3):
        for b in range(6):
            c = [(240, 120, 110), (110, 170, 230), (250, 210, 90), (140, 200, 140)][(r + b) % 4]
            d.rectangle((W * .58 + b * 55, H * .23 + r * H * .11, W * .58 + b * 55 + 40, H * .23 + r * H * .11 + H * .09), fill=c)
    # ボール
    d.ellipse((W * .12, H * .5, W * .26, H * .6), fill=(250, 120, 120))
    d.arc((W * .12, H * .5, W * .26, H * .6), 200, 340, fill=(255, 255, 255), width=12)
    return _fin(img, w, h)


# ---- 工務店 ----
def house_exterior(w=1080, h=1440):
    img = _canvas(w, h, (140, 196, 240), (214, 236, 248))
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((0, H * .74, W, H), fill=(120, 170, 100))
    d.rectangle((0, H * .78, W, H), fill=(190, 186, 176))
    # 家
    d.rectangle((W * .12, H * .38, W * .88, H * .76), fill=(236, 230, 218))
    d.rectangle((W * .5, H * .38, W * .88, H * .76), fill=(150, 110, 76))
    for i in range(12):
        x = W * .5 + i * (W * .38 / 12)
        d.line((x, H * .38, x, H * .76), fill=(130, 94, 64), width=4)
    d.polygon([(W * .06, H * .4), (W * .5, H * .22), (W * .94, H * .4)], fill=(60, 64, 70))
    d.rectangle((W * .18, H * .46, W * .42, H * .62), fill=(190, 220, 236), outline=(60, 60, 60), width=10)
    d.rectangle((W * .6, H * .52, W * .76, H * .76), fill=(80, 56, 38))
    d.rectangle((W * .56, H * .42, W * .82, H * .48), fill=(190, 220, 236))
    for x in (W * .08, W * .93):
        d.ellipse((x - 80, H * .58, x + 80, H * .78), fill=(70, 140, 80))
    return _fin(img, w, h)


def house_living(w=1080, h=1440):
    img = _canvas(w, h, (250, 246, 238), (238, 230, 218))
    d = ImageDraw.Draw(img)
    W, H = img.size
    # 天井の梁
    for i in range(5):
        d.rectangle((0, H * .03 + i * 50, W, H * .03 + i * 50 + 20), fill=(214, 180, 136))
    d.rectangle((W * .1, H * .2, W * .9, H * .55), fill=(200, 226, 238), outline=(200, 170, 130), width=18)
    d.line((W * .5, H * .2, W * .5, H * .55), fill=(200, 170, 130), width=12)
    _wood(img, int(H * .6), (214, 176, 130), (196, 158, 112))
    d = ImageDraw.Draw(img)
    # ソファ
    _shadow(img, (W * .15, H * .74, W * .85, H * .8), ellipse=True, off=(0, 20), blur=25, alpha=70)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((W * .15, H * .56, W * .85, H * .7), 40, fill=(140, 160, 150))
    d.rounded_rectangle((W * .12, H * .64, W * .88, H * .78), 40, fill=(120, 140, 130))
    d.rounded_rectangle((W * .3, H * .6, W * .44, H * .68), 20, fill=(240, 220, 170))
    # ラグ・テーブル
    d.ellipse((W * .2, H * .82, W * .8, H * .95), fill=(236, 228, 210))
    d.rounded_rectangle((W * .35, H * .84, W * .65, H * .88), 10, fill=(170, 124, 82))
    return _fin(img, w, h)


def house_kitchen(w=1080, h=1440):
    img = _canvas(w, h, (246, 244, 240), (232, 228, 222))
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((W * .1, H * .14, W * .9, H * .3), fill=(230, 214, 190))
    for i in range(4):
        d.rectangle((W * .12 + i * W * .2, H * .15, W * .12 + (i + 1) * W * .2 - 10, H * .29), outline=(200, 180, 150), width=6)
    d.rectangle((W * .1, H * .3, W * .9, H * .5), fill=(250, 250, 248))
    d.rectangle((W * .4, H * .33, W * .6, H * .45), fill=(200, 226, 238), outline=(200, 180, 150), width=8)
    _wood(img, int(H * .78), (200, 160, 116), (184, 144, 100))
    d = ImageDraw.Draw(img)
    d.rectangle((W * .06, H * .5, W * .94, H * .54), fill=(240, 240, 236))
    d.rectangle((W * .08, H * .54, W * .92, H * .8), fill=(214, 180, 136))
    for i in range(4):
        d.rectangle((W * .1 + i * W * .205, H * .56, W * .1 + (i + 1) * W * .205 - 12, H * .78), outline=(190, 156, 112), width=6)
        d.rectangle((W * .1 + i * W * .205 + 60, H * .58, W * .1 + i * W * .205 + 120, H * .59), fill=(120, 120, 120))
    d.line((W * .3, H * .5, W * .3, H * .42, W * .34, H * .42), fill=(160, 160, 166), width=14)
    for i in range(3):
        x = W * (.25 + i * .25)
        d.line((x, 0, x, H * .08), fill=(80, 80, 80), width=5)
        d.ellipse((x - 40, H * .07, x + 40, H * .12), fill=(250, 230, 180))
    return _fin(img, w, h)
