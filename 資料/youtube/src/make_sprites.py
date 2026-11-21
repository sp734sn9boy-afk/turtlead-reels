# キャラクターのドット絵を整数倍に拡大（nearest neighbor）して src/sprites/ に置く
# 元PNGは 512x512 の中に 64x64 ドットが 1ドット=7px・左上32pxずれで描かれている
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'ai_office', 'characters', 'single')
OUT = os.path.join(HERE, 'sprites'); os.makedirs(OUT, exist_ok=True)
SCALES = {'leader': [6, 9], 'sales': [3], 'listing': [3], 'design': [3], 'automation': [3], 'research': [3]}
for name, ks in SCALES.items():
    im = Image.open(os.path.join(SRC, name + '.png')).convert('RGBA').crop((32, 32, 480, 480))
    dot = im.resize((64, 64), Image.NEAREST)
    dot = dot.crop(dot.getbbox())
    for k in ks:
        big = dot.resize((dot.width * k, dot.height * k), Image.NEAREST)
        big.save(os.path.join(OUT, f'{name}_x{k}.png'))
        print(name, k, big.size)
