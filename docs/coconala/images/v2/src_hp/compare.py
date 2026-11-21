# 売れている画像の一覧（スクラッチパッド）と、うちの6案を同じ大きさで並べる
from PIL import Image,ImageDraw,ImageFont
R='/tmp/claude-0/-home-user-turtlead-reels/98039a62-44c3-5ee8-bbca-2d7f968b9a31/scratchpad/coconala_research/sheets/'
hp=Image.open(R+'hp_top.png').convert('RGB');wp=Image.open(R+'wphosyu_top.png').convert('RGB')
s=0.72;hp=hp.resize((int(hp.width*s),int(hp.height*s)));wp=wp.resize(hp.size)
tw=int(360*s)+2;th=int(tw/1.208)
o=Image.new('RGB',(hp.width+2*tw+90+wp.width,hp.height),'white');o.paste(hp,(0,0));o.paste(wp,(hp.width+2*tw+90,0))
d=ImageDraw.Draw(o);f=ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf',22)
x0=hp.width+30;d.text((x0,20),'うちの案（一覧と同じ切り取り）',fill='red',font=f)
for i,n in enumerate(['03_hp_A','03_hp_B','03_hp_C','04_hosyu_A','04_hosyu_B','04_hosyu_C']):
    im=Image.open(f'../{n}.png').convert('RGB').crop((0,115,1220,1125)).resize((tw,th),Image.LANCZOS)
    x=x0+(i%2)*(tw+15);y=70+(i//2)*(th+60);o.paste(im,(x,y));d.text((x,y+th+6),n,fill='black',font=f)
o.save('../compare_03_04.png')
