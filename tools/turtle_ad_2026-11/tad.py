"""turtle ad 投稿画像の共通部品（既存 tad_day1/day7 のデザインに合わせる）"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FD = '/tmp/claude-0/-home-user-turtlead-reels/b27c76b2-50d0-5d67-a8f8-45274e95aac1/scratchpad/fonts/package/'
F = {
    'black': FD + '900Black/NotoSansJP_900Black.ttf',
    'xbold': FD + '800ExtraBold/NotoSansJP_800ExtraBold.ttf',
    'bold': FD + '700Bold/NotoSansJP_700Bold.ttf',
    'med': FD + '500Medium/NotoSansJP_500Medium.ttf',
}
LOGO = '/tmp/claude-0/-home-user-turtlead-reels/b27c76b2-50d0-5d67-a8f8-45274e95aac1/scratchpad/src/logo.png'

WHITE = (240, 244, 252)
SUB = (170, 182, 210)
CYAN = (58, 208, 240)
PURP = (150, 130, 230)
NAVY = (12, 20, 48)
CARD = (16, 26, 58)
YELLOW = (255, 214, 64)


def font(kind, size):
    return ImageFont.truetype(F[kind], size)


def background(w, h, seed=1, nodes=True):
    random.seed(seed)
    img = Image.new('RGB', (w, h), (6, 10, 24))
    px = Image.linear_gradient('L').resize((w, h))
    top = Image.new('RGB', (w, h), (18, 30, 66))
    bot = Image.new('RGB', (w, h), (4, 7, 16))
    img = Image.composite(bot, top, px)
    # glows
    glow = Image.new('RGB', (w, h), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((w * 0.55, -h * 0.15, w * 1.25, h * 0.38), fill=(30, 90, 140))
    g.ellipse((-w * 0.35, h * 0.6, w * 0.4, h * 1.05), fill=(50, 30, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = ImageChops.add(img, glow)
    d = ImageDraw.Draw(img, 'RGBA')
    # grid
    for x in range(0, w, 60):
        d.line((x, 0, x, h), fill=(80, 120, 200, 14))
    for y in range(0, h, 60):
        d.line((0, y, w, y), fill=(80, 120, 200, 14))
    if nodes:
        pts = [(w * random.uniform(0.62, 0.98), h * random.uniform(0.02, 0.3)) for _ in range(7)]
        for i, a in enumerate(pts):
            for b in pts[i + 1:i + 3]:
                d.line((a, b), fill=(70, 170, 210, 70), width=2)
        for p in pts:
            r = random.choice([5, 7, 10])
            d.ellipse((p[0] - r * 2.2, p[1] - r * 2.2, p[0] + r * 2.2, p[1] + r * 2.2), fill=(80, 120, 230, 40))
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(70, 180, 220, 200))
    return img


def paste_logo(img, x, y, scale=1.0):
    lg = Image.open(LOGO).convert('RGB')
    if scale != 1.0:
        lg = lg.resize((int(lg.width * scale), int(lg.height * scale)), Image.LANCZOS)
    region = img.crop((x, y, x + lg.width, y + lg.height))
    img.paste(ImageChops.lighter(region, lg), (x, y))


def eyebrow(img, x, y, text, size=34):
    d = ImageDraw.Draw(img)
    d.line((x, y + size * 0.62, x + 60, y + size * 0.62), fill=CYAN, width=4)
    f = font('xbold', size)
    tx = x + 80
    for ch in text:
        d.text((tx, y), ch, font=f, fill=CYAN)
        tx += d.textlength(ch, font=f) + size * 0.14


NO_START = set('、。，．・ー」』）)！？!?ぁぃぅぇぉっゃゅょァィゥェォッャュョ〜～')


def wrap(text, f, maxw, draw=None):
    draw = draw or ImageDraw.Draw(Image.new('RGB', (1, 1)))
    lines = []
    for para in text.split('\n'):
        cur = ''
        for ch in para:
            if draw.textlength(cur + ch, font=f) > maxw and cur:
                if ch in NO_START:
                    # 行頭禁則：前の文字ごと次の行へ
                    lines.append(cur[:-1])
                    cur = cur[-1] + ch
                else:
                    lines.append(cur)
                    cur = ch
            else:
                cur += ch
        lines.append(cur)
    return lines


def text_block(img, x, y, text, kind, size, fill=WHITE, maxw=900, lh=1.35, align='left', grad=False):
    d = ImageDraw.Draw(img)
    f = font(kind, size)
    lines = wrap(text, f, maxw, d)
    for ln in lines:
        tw = d.textlength(ln, font=f)
        lx = x if align == 'left' else (x + (maxw - tw) / 2 if align == 'center' else x + maxw - tw)
        if grad:
            gradient_text(img, int(lx), int(y), ln, f)
        else:
            d.text((lx, y), ln, font=f, fill=fill)
        y += int(size * lh)
    return y


def gradient_text(img, x, y, text, f, c1=(170, 220, 230), c2=CYAN, c3=PURP):
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((x, y), text, font=f)
    w, h = r - l + 4, b - t + 4
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).text((x - l, y - t), text, font=f, fill=255)
    grad = Image.new('RGB', (w, h))
    gd = ImageDraw.Draw(grad)
    for i in range(w):
        k = i / max(1, w - 1)
        if k < 0.5:
            c = tuple(int(c1[j] + (c2[j] - c1[j]) * k * 2) for j in range(3))
        else:
            c = tuple(int(c2[j] + (c3[j] - c2[j]) * (k - 0.5) * 2) for j in range(3))
        gd.line((i, 0, i, h), fill=c)
    img.paste(grad, (l, t), mask)


def card(img, box, r=28, fill=CARD, outline=(60, 80, 130), width=2, glow=False):
    if glow:
        gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle(box, r, outline=(58, 208, 240, 160), width=10)
        gl = gl.filter(ImageFilter.GaussianBlur(14))
        img.paste(gl, (0, 0), gl)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def pill(img, x, y, text, size=40, fill=(20, 34, 70), outline=CYAN, color=WHITE, kind='bold', padx=36, pady=18):
    d = ImageDraw.Draw(img)
    f = font(kind, size)
    tw = d.textlength(text, font=f)
    box = (x, y, x + tw + padx * 2, y + size + pady * 2)
    d.rounded_rectangle(box, (size + pady * 2) // 2, fill=fill, outline=outline, width=3)
    d.text((x + padx, y + pady - size * 0.12), text, font=f, fill=color)
    return box


def page_num(img, i, n):
    """右上のページ番号（カルーセル用）"""
    d = ImageDraw.Draw(img)
    f = font('bold', 30)
    t = f'{i} / {n}'
    tw = d.textlength(t, font=f)
    w = img.width
    d.rounded_rectangle((w - 80 - tw - 40, 96, w - 80, 150), 27, fill=(20, 34, 70), outline=(70, 100, 160), width=2)
    d.text((w - 80 - tw - 20, 103), t, font=f, fill=SUB)


def swipe_hint(img, text='スワイプしてね →', y=None):
    d = ImageDraw.Draw(img)
    f = font('bold', 34)
    tw = d.textlength(text, font=f)
    y = y or img.height - 130
    d.text((img.width - 80 - tw, y), text, font=f, fill=CYAN)


def checkbox(img, x, y, size=90, checked=False):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + size, y + size), 16, outline=CYAN, width=7)
    if checked:
        d.line((x + size * .2, y + size * .52, x + size * .43, y + size * .75, x + size * .82, y + size * .28), fill=YELLOW, width=12, joint='curve')


def save(img, path):
    img.convert('RGB').save(path, 'JPEG', quality=92, optimize=True, progressive=False, subsampling=0)
