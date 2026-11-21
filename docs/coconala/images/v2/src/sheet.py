# 確認用：6案を並べ、一覧での切れ方（上下115px）と180px幅の見え方を作る
from PIL import Image, ImageDraw
import sys
d='/home/user/turtlead-reels/docs/coconala/images/v2/'
names=['01_reel_A','01_reel_B','01_reel_C','02_logo_A','02_logo_B','02_logo_C']
W=610
sh=Image.new('RGB',(W*3,620*2),'#888')
for i,n in enumerate(names):
    im=Image.open(d+n+'.png').convert('RGB').resize((W,620))
    sh.paste(im,((i%3)*W,(i//3)*620))
sh.save(sys.argv[1],quality=88)
