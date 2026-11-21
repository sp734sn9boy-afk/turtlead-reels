# 比較画像：売れている出品の一覧（調査スクショ）と、うちの6案を同じ大きさ・同じ切れ方（上下115pxカット）で並べる
# ※他社の画像が入るので、この比較画像は社内確認用。コミット・公開しない。
from PIL import Image, ImageDraw, ImageFont
import sys
R=sys.argv[1]; d='/home/user/turtlead-reels/docs/coconala/images/v2/'
f=ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf',26)
names=['01_reel_A','01_reel_B','01_reel_C','02_logo_A','02_logo_B','02_logo_C']
ours=[Image.open(d+n+'.png').convert('RGB').crop((0,115,1220,1125)) for n in names]
top1=Image.open(R+'/sheets/reel_top.png').convert('RGB').crop((0,50,1500,1085))
top2=Image.open(R+'/sheets/logoanim_top.png').convert('RGB').crop((0,50,1500,740))
cw,ch=360,298
H=60+ch+50+60+150+40+top1.height+top2.height+80
out=Image.new('RGB',(1500,H),'white'); dr=ImageDraw.Draw(out)
dr.text((16,14),'うちの新しい6案（一覧と同じ切れ方）　左から ①A ①B ①C ②A ②B ②C',font=f,fill='black')
# 6 in a row at 240 wide? keep same size as competitors: two rows of 4/2 would be long; use 4+2
y=60
small=[]
for i,im in enumerate(ours):
    t=im.resize((cw,ch),Image.LANCZOS)
    x=16+(i%4)*370; yy=y+(i//4)*(ch+12)
    out.paste(t,(x,yy)); 
y2=y+2*(ch+12)
dr.text((16+2*370+10,y+ch+30),'↓ スマホ一覧を想定した180px幅',font=f,fill='black')
for i,im in enumerate(ours):
    out.paste(im.resize((180,149),Image.LANCZOS),(16+2*370+10+(i%3)*190,y+ch+70+(i//3)*0) if i<3 else (16+2*370+10+(i%3)*190,y+ch+70+155))
y3=y2+20
dr.text((16,y3),'売れている出品（リール動画 作成／評価件数の多い順）',font=f,fill='black'); out.paste(top1,(0,y3+40))
y4=y3+40+top1.height+10
dr.text((16,y4),'売れている出品（ロゴ アニメーション／評価件数の多い順）',font=f,fill='black'); out.paste(top2,(0,y4+40))
out=out.crop((0,0,1500,y4+40+top2.height))
out.save(d+'compare_01_02.png'); out.convert('RGB').save(sys.argv[2],quality=80); print(out.size)
