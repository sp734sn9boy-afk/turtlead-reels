# 表紙の確認用：円形に切り抜いて小さくした見え方を作る（python3 check_covers.py）
# check/cover_circles.png … 上段：中央の直径600px円で切り抜き（表紙の安全範囲）
#                           中段：幅いっぱいの直径1080px円（Instagramの初期の切り抜き相当）
#                           下段：プロフィールでの実寸に近い 66px（明るい画面・暗い画面）
from PIL import Image, ImageDraw, ImageFont
import os
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
names = ['01_AI動画編集部', '02_料金', '03_制作例', '04_AI顧問', '05_お問い合わせ']
labels = ['AI動画編集部', '料金', '制作例', 'AI顧問', 'お問い合わせ']
font = ImageFont.truetype(os.path.join(R, '..', 'ai_video', 'fonts', 'NotoSansJP-Bold.ttf'), 22)

def circle(im, d, size):
    cx, cy = 540, 960
    c = im.crop((cx - d // 2, cy - d // 2, cx + d // 2, cy + d // 2)).resize((size, size), Image.LANCZOS)
    m = Image.new('L', (size * 4, size * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    out = Image.new('RGBA', (size, size)); out.paste(c, (0, 0), m.resize((size, size), Image.LANCZOS)); return out

def ring(bg, x, y, s, col):
    ImageDraw.Draw(bg).ellipse((x - 5, y - 5, x + s + 4, y + s + 4), outline=col, width=2)

W = 5 * 220 + 40
bg = Image.new('RGB', (W, 820), '#ffffff')
dk = Image.new('RGB', (W, 140), '#000000'); bg.paste(dk, (0, 680))
d = ImageDraw.Draw(bg)
d.text((20, 10), '上：中央600px円　中：幅いっぱい1080px円　下：実寸に近い66px（明るい画面／暗い画面）', font=font, fill='#333')
for i, n in enumerate(names):
    im = Image.open(os.path.join(R, 'cover', n + '.png')).convert('RGBA')
    x = 40 + i * 220
    a = circle(im, 600, 160); bg.paste(a, (x, 50), a)
    b = circle(im, 1080, 160); bg.paste(b, (x, 250), b)
    for j, (yy, col, tc) in enumerate([(470, '#c8c8c8', '#222'), (700, '#555555', '#eee')]):
        c = circle(im, 1080, 66); xx = x + 47; ring(bg, xx, yy, 66, col); bg.paste(c, (xx, yy), c)
        tw = d.textlength(labels[i], font=font); d.text((x + 80 - tw / 2, yy + 78), labels[i], font=font, fill=tc)
    tw = d.textlength(labels[i], font=font); d.text((x + 80 - tw / 2, 215), labels[i], font=font, fill='#222')
bg.save(os.path.join(R, 'check', 'cover_circles.png'))
print('ok')
