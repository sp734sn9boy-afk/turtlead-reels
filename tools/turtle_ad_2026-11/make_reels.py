import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from reel import *
import illus

OUT = '/home/user/turtlead-reels/img/turtle_ad/2026-11/'
TMP = '/tmp/claude-0/-home-user-turtlead-reels/b27c76b2-50d0-5d67-a8f8-45274e95aac1/scratchpad/'
os.makedirs(OUT, exist_ok=True)
DUR = 15.0


def polaroid(img, w=400):
    h = int(w * 1440 / 1080)
    p = Image.new('RGBA', (w + 36, h + 90), (252, 252, 248, 255))
    p.paste(img.resize((w, h), Image.LANCZOS), (18, 18))
    return p


def strength_layer(num, text, shop):
    """3つの強みカード（下寄せ。Instagramの下部UIを避ける）"""
    lay = layer()
    d = ImageDraw.Draw(lay)
    y0 = 1130
    d.rounded_rectangle((90, y0, RW - 90, y0 + 300), 36, fill=(252, 250, 244, 245))
    cx = RW / 2
    d.ellipse((cx - 58, y0 - 58, cx + 58, y0 + 58), fill=YELLOW)
    f = font('black', 60)
    t = f'{num:02d}'
    d.text((cx - d.textlength(t, font=f) / 2, y0 - 44), t, font=f, fill=(20, 24, 40))
    f2 = font('black', 88 if len(text) <= 8 else 74)
    d.text((cx - d.textlength(text, font=f2) / 2, y0 + 92), text, font=f2, fill=(20, 28, 60))
    f3 = font('bold', 34)
    s = f'強み {num} / 3'
    d.text((cx - d.textlength(s, font=f3) / 2, y0 + 222), s, font=f3, fill=(120, 120, 130))
    return lay


def shop_band(shop, sub):
    lay = layer()
    d = ImageDraw.Draw(lay)
    d.rectangle((0, 250, RW, 420), fill=(14, 22, 52, 225))
    f = font('black', 76)
    d.text(((RW - d.textlength(shop, font=f)) / 2, 262), shop, font=f, fill=WHITE)
    f2 = font('bold', 36)
    d.text(((RW - d.textlength(sub, font=f2)) / 2, 364), sub, font=f2, fill=CYAN)
    return lay


def sample_part(base_t, photos, shop, sub, strengths, t0=5.0, t1=12.0):
    """t0〜t1：写真にゆっくり動きをつけ、店名と強み3つを出す"""
    seg = (t1 - t0) / len(strengths)
    band = shop_band(shop, sub)
    cards = [strength_layer(i + 1, s, shop) for i, s in enumerate(strengths)]

    def fn(t):
        k = min(len(strengths) - 1, int((t - t0) / seg))
        lt = t - t0 - k * seg
        z = 1.0 + 0.10 * (lt / seg)
        cxs = [0.3, 0.6, 0.45, 0.5]
        fr = cover(photos[k], RW, RH, z, cxs[k % 4], 0.5).convert('RGBA')
        if k > 0 and lt < 0.3:
            prev = cover(photos[k - 1], RW, RH, 1.1, cxs[(k - 1) % 4], 0.5).convert('RGBA')
            fr = Image.blend(prev, fr, lt / 0.3)
        put(fr, band, ease(prog(t, t0, t0 + 0.4)))
        a = ease(lt / 0.35)
        put(fr, cards[k], a, dy=(1 - a) * 80)
        return fr
    return fn


def make_sample_reel(name, intro_fn, photos, shop, sub, strengths, music_seed):
    wav = TMP + f'{name}.wav'
    make_music(wav, DUR, bpm=100, seed=music_seed)
    badge = sample_badge()
    part = sample_part(None, photos, shop, sub, strengths)
    endc = end_card(seed=music_seed + 3)

    def frame(t):
        if t < 5.0:
            fr = intro_fn(t)
        elif t < 12.0:
            fr = part(t)
        else:
            fr = part(11.99) if t < 12.4 else endc.copy()
            if t < 12.4:
                fr = Image.blend(fr, endc, (t - 12) / 0.4)
        put(fr, badge, 1.0)
        return fr
    out = OUT + name + '.mp4'
    rc = render(frame, DUR, out, wav)
    print(out, rc)


# ---------------- 11/21 カフェ ----------------
def reel_1121():
    ph = [illus.cafe_lunch(), illus.cafe_interior(), illus.cafe_exterior(sign='CAFE'), illus.cafe_coffee(), illus.cafe_takeout()]
    bg = background(RW, RH, 21).convert('RGBA')
    t1 = text_layer('写真5枚が、', 300, 130)
    pols = [polaroid(p, 340) for p in ph]
    pos = [(30, 640, -6), (345, 600, 3), (650, 650, 7), (180, 1160, 5), (500, 1140, -5)]
    rots = [pl.rotate(r, expand=True, resample=Image.BICUBIC) for pl, (_, _, r) in zip(pols, pos)]
    t2 = text_layer('15秒の動画に\nなります', 1180, 110, box=((14, 22, 52, 230), 50))
    order = [0, 1, 2]  # 料理・店内・外観

    def intro(t):
        if t < 2.0:
            fr = bg.copy()
            put(fr, t1, ease(prog(t, 0, .35)), dy=(1 - ease(prog(t, 0, .35))) * 40)
            for i, (im, (x, y, r)) in enumerate(zip(rots, pos)):
                a = ease(prog(t, .25 + i * .2, .55 + i * .2))
                if a > 0:
                    s = 0.6 + 0.4 * a
                    w, h = int(im.width * s), int(im.height * s)
                    im2 = im.resize((w, h), Image.BILINEAR)
                    fr.alpha_composite(im2, (int(x + (im.width - w) / 2), int(y + (im.height - h) / 2)))
            return fr
        # 2〜5秒：料理→店内→外観
        k = min(2, int((t - 2.0) / 1.0))
        lt = t - 2.0 - k * 1.0
        fr = cover(ph[order[k]], RW, RH, 1.0 + 0.06 * lt, .5, .5).convert('RGBA')
        if lt < 0.25:
            prev = bg if k == 0 else cover(ph[order[k - 1]], RW, RH, 1.06, .5, .5).convert('RGBA')
            fr = Image.blend(prev, fr, lt / 0.25)
        put(fr, t2, ease(prog(t, 2.1, 2.5)))
        return fr

    make_sample_reel('2026-11-21_AI動画作例_カフェ', intro, [ph[0], ph[2], ph[4]],
                     'カフェ〇〇（架空）', 'AI動画の見本', ['手づくりランチ', '駐車場あり', 'テイクアウトOK'], 0)


# ---------------- 11/28 美容室 ----------------
def reel_1128():
    ph = [illus.salon_chair(), illus.salon_products(), illus.salon_kids()]
    bg = Image.new('RGBA', (RW, RH), (236, 236, 236, 255))
    tb = text_layer('BEFORE：写真だけ', 300, 100, fill=(40, 40, 50), shadow=False)
    ta = text_layer('AFTER：AI動画に', 820, 110, box=((14, 22, 52, 235), 50))
    tiles = [p.resize((470, 627), Image.LANCZOS) for p in ph]

    def intro(t):
        if t < 3.0:
            fr = bg.copy()
            put(fr, tb, 1.0)
            fr.paste(tiles[0], (50, 520)); fr.paste(tiles[1], (560, 520)); fr.paste(tiles[2], (305, 1180))
            return fr
        lt = t - 3.0
        fr = cover(ph[0], RW, RH, 1.0 + 0.05 * lt, .5, .5).convert('RGBA')
        if lt < 0.3:
            b = bg.copy(); b.paste(tiles[0], (50, 520)); b.paste(tiles[1], (560, 520)); b.paste(tiles[2], (305, 1180))
            fr = Image.blend(b, fr, lt / 0.3)
        a = ease(prog(t, 3.1, 3.5))
        put(fr, ta, a, scale=0.9 + 0.1 * a)
        return fr

    # BEFORE 0〜3秒、AFTER 3〜12秒（3〜5秒は「AFTER」の見出し、5〜12秒で店名と強み）
    make_sample_reel('2026-11-28_AI動画作例_美容室', intro, ph, 'hair salon 〇〇（架空）', 'AI動画の見本',
                     ['完全予約制', '髪にやさしい薬剤', 'キッズスペースあり'], 1)


# ---------------- 12/2 工務店 ----------------
def reel_1202():
    ph = [illus.house_exterior(), illus.house_kitchen(), illus.house_living()]
    bg = background(RW, RH, 12).convert('RGBA')
    tq = text_layer('施工写真、\n眠って\nいませんか？', 330, 120)
    grid = []
    allp = ph + [illus.house_exterior(), illus.house_living(), illus.house_kitchen()]
    for i, p in enumerate(allp * 2):
        grid.append(p.resize((330, 440), Image.LANCZOS))
    ts = text_layer('その写真で、\n動画が作れます', 1250, 96, box=((14, 22, 52, 235), 50))

    def intro(t):
        if t < 3.0:
            fr = bg.copy()
            # スマホのアルバム風に並べて暗く
            off = -60 * t
            for i, g in enumerate(grid[:9]):
                x = 30 + (i % 3) * 345
                y = int(820 + (i // 3) * 455 + off)
                fr.alpha_composite(g.convert('RGBA'), (x, y))
            shade = Image.new('RGBA', (RW, RH), (6, 10, 24, 120))
            fr.alpha_composite(shade)
            put(fr, tq, ease(prog(t, 0, .4)), dy=(1 - ease(prog(t, 0, .4))) * 40)
            return fr
        lt = t - 3.0
        fr = cover(ph[0], RW, RH, 1.0 + 0.05 * lt, .5, .5).convert('RGBA')
        if lt < 0.3:
            fr = Image.blend(bg, fr, lt / 0.3)
        put(fr, ts, ease(prog(t, 3.1, 3.5)))
        return fr

    make_sample_reel('2026-12-02_AI動画作例_工務店', intro, ph, '〇〇工務店（架空）', 'AI動画の見本',
                     ['新築', 'リフォーム', '地元で〇〇年'], 2)


# ---------------- 11/25 頼み方3ステップ ----------------
def reel_1125():
    wav = TMP + 'r1125.wav'
    make_music(wav, DUR, bpm=104, seed=3, root=62)
    bg = background(RW, RH, 25).convert('RGBA')
    q = text_layer('AI動画、\nどうやって\n頼むの？', 520, 140)
    steps = [
        ('STEP 1', '① 写真を送る', '（スマホの写真でOK）'),
        ('STEP 2', '② お店の強みを\n3つ教える', ''),
        ('STEP 3', '③ 確認して完成', ''),
    ]
    th = [illus.cafe_lunch(), illus.cafe_interior(), illus.cafe_exterior()]
    thumbs = [polaroid(p, 220).convert('RGBA') for p in th]
    endc = end_card(seed=7, price_label='1本')

    def step_layer(k):
        lay = layer()
        d = ImageDraw.Draw(lay)
        lab, main, sub = steps[k]
        eyebrow_img = Image.new('RGBA', (RW, 80), (0, 0, 0, 0))
        f = font('xbold', 46)
        d.text((120, 330), lab, font=f, fill=CYAN)
        d.line((120, 400, 260, 400), fill=CYAN, width=6)
        y = 450
        for ln in main.split('\n'):
            d.text((120, y), ln, font=font('black', 100), fill=WHITE)
            y += 135
        if sub:
            d.text((120, y + 10), sub, font=font('bold', 56), fill=YELLOW)
        return lay

    sl = [step_layer(k) for k in range(3)]
    bubbles = ['手づくりランチ', '駐車場あり', 'テイクアウトOK']

    def frame(t):
        if t >= 12.0:
            fr = endc.copy()
            if t < 12.35:
                prev = bg.copy()
                fr = Image.blend(prev, fr, (t - 12) / 0.35)
            return fr
        fr = bg.copy()
        if t < 3.0:
            a = ease(prog(t, 0, .4))
            put(fr, q, a, scale=0.92 + 0.08 * a)
            return fr
        k = min(2, int((t - 3.0) / 3.0))
        lt = t - 3.0 - k * 3.0
        a = ease(lt / 0.35)
        put(fr, sl[k], a, dx=(1 - a) * 80)
        d = ImageDraw.Draw(fr)
        if k == 0:
            # スマホに写真が送られていく
            px, py = 340, 900
            d.rounded_rectangle((px, py, px + 400, py + 760), 60, fill=(20, 28, 58), outline=(120, 150, 210), width=8)
            d.rounded_rectangle((px + 24, py + 70, px + 376, py + 690), 30, fill=(236, 240, 248))
            for i, tb in enumerate(thumbs):
                ai = ease(prog(lt, .3 + i * .45, .7 + i * .45))
                if ai > 0:
                    x = int(px - 330 + (390) * ai) if i != 1 else int(px + 90)
                    tbs = tb.resize((int(tb.width * .62), int(tb.height * .62)))
                    yy = int(py + 110 + i * 175 - (1 - ai) * 200)
                    fr.alpha_composite(tbs, (px + 90, yy)) if ai >= 1 else fr.alpha_composite(tbs, (px + 90, yy))
        elif k == 1:
            for i, b in enumerate(bubbles):
                ai = ease(prog(lt, .3 + i * .5, .6 + i * .5))
                if ai > 0:
                    y = 1000 + i * 190
                    f = font('black', 64)
                    tw = d.textlength(b, font=f)
                    x0 = 120 + (1 - ai) * 60
                    d.rounded_rectangle((x0, y, x0 + tw + 140, y + 130), 50, fill=(252, 250, 244))
                    d.ellipse((x0 + 26, y + 30, x0 + 96, y + 100), fill=YELLOW)
                    d.text((x0 + 44, y + 28), str(i + 1), font=font('black', 52), fill=(20, 24, 40))
                    d.text((x0 + 116, y + 24), b, font=f, fill=(20, 28, 60))
        else:
            ai = ease(prog(lt, .3, .9))
            cx, cy, r = RW / 2, 1250, 200
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=CYAN, width=14)
            if ai > 0:
                p1 = (cx - 100, cy + 5); p2 = (cx - 25, cy + 85); p3 = (cx + 115, cy - 85)
                if ai < .4:
                    e = ai / .4
                    d.line((p1, (p1[0] + (p2[0] - p1[0]) * e, p1[1] + (p2[1] - p1[1]) * e)), fill=YELLOW, width=30)
                else:
                    e = (ai - .4) / .6
                    d.line((p1, p2, (p2[0] + (p3[0] - p2[0]) * e, p2[1] + (p3[1] - p2[1]) * e)), fill=YELLOW, width=30, joint='curve')
            if lt > 1.2:
                f = font('black', 72)
                t2 = '完成！'
                d.text(((RW - d.textlength(t2, font=f)) / 2, 1500), t2, font=f, fill=WHITE)
        return fr

    out = OUT + '2026-11-25_AI動画の頼み方3ステップ.mp4'
    print(out, render(frame, DUR, out, wav))


if __name__ == '__main__':
    which = sys.argv[1:] or ['1121', '1125', '1128', '1202']
    for w in which:
        globals()['reel_' + w]()
