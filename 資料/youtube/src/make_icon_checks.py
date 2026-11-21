# アイコンを円形に切り抜いた確認用画像（800 / 176 / 48px）を作り、タートルが円の内側にあるか測る
import os, math
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, '..')
ic = Image.open(os.path.join(OUT, 'icon_800.png')).convert('RGBA')
m = Image.new('L', (800, 800), 0); ImageDraw.Draw(m).ellipse((0, 0, 799, 799), fill=255)
circ = Image.new('RGBA', (800, 800), (255, 255, 255, 0)); circ.paste(ic, (0, 0), m)
for s in (176, 48):
    bg = Image.new('RGBA', (s + 16, s + 16), (255, 255, 255, 255))
    bg.alpha_composite(circ.resize((s, s), Image.LANCZOS), (8, 8))
    bg.convert('RGB').save(os.path.join(OUT, 'check', f'icon_circle_{s}px.png'))
# 48px を見やすく8倍に（ドットのまま拡大）
Image.open(os.path.join(OUT, 'check', 'icon_circle_48px.png')).resize((512, 512), Image.NEAREST).save(os.path.join(OUT, 'check', 'icon_circle_48px_zoom.png'))
# タートルの絵の中で円の中心から一番遠い点（icon.html の配置 left193 top116）
sp = Image.open(os.path.join(H, 'sprites', 'leader_x9.png'))
a = sp.getchannel('A'); d = 0
for y in range(sp.height):
    for x in range(sp.width):
        if a.getpixel((x, y)) > 0:
            d = max(d, math.hypot(193 + x + .5 - 400, 116 + y + .5 - 400))
print('タートルの最遠点の半径', round(d), '/ 400')
