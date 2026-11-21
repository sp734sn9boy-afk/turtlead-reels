# 6案を並べた確認シート（一覧と同じく上下115pxを切った横長でも表示）
from PIL import Image
import sys
ns=['03_hp_A','03_hp_B','03_hp_C','04_hosyu_A','04_hosyu_B','04_hosyu_C']
o=Image.new('RGB',(3*620,2*640+2*160),'white')
for i,n in enumerate(ns):
    im=Image.open(f'../{n}.png').convert('RGB')
    o.paste(im.resize((610,620)),((i%3)*620,(i//3)*790))
    c=im.crop((0,115,1220,1125)).resize((180,149),Image.LANCZOS)
    o.paste(c,((i%3)*620+10,(i//3)*790+630))
o.save(sys.argv[1])
