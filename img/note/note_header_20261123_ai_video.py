from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=2; W,H=1280*S,670*S
BG=(251,246,238); INK=(58,52,48); SUB=(110,100,92); ACC=(240,132,74); ACCL=(253,226,207)
SOFT=[(236,226,212),(222,234,226),(232,226,240),(246,232,214),(226,232,242)]
F="/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
def f(px): return ImageFont.truetype(F,int(px*S))
def s(*v): return [int(x*S) for x in v]
img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
# soft background blobs
for box,col in [((820,40,1260,520),ACCL),((-120,460,360,820),(240,230,214))]:
    m=Image.new("L",(W,H),0); ImageDraw.Draw(m).ellipse(s(*box),fill=200)
    m=m.filter(ImageFilter.GaussianBlur(40*S)); img.paste(Image.new("RGB",(W,H),col),(0,0),m)
d=ImageDraw.Draw(img)

# ---- text ----
X=120
lbl="AI動画の作り方・費用・頼み方"; ft=f(22)
tw=d.textlength(lbl,font=ft)
d.rounded_rectangle(s(X,96,X+tw/S+36,134),radius=19*S,fill=ACC)
d.text((s(X+18)[0],s(115)[0]),lbl,font=ft,fill="white",anchor="lm")
big="撮影なし・顔出しなし"; fb=f(72)
d.text(s(X,160),big,font=fb,fill=INK,stroke_width=int(1.6*S),stroke_fill=INK)
# accent underline
d.rounded_rectangle(s(X,262,X+300,270),radius=4*S,fill=ACC)
mid="スマホの写真5枚から、お店の紹介動画"; fm=f(38)
d.text(s(X,292),mid,font=fm,fill=SUB,stroke_width=int(0.6*S),stroke_fill=SUB)

# ---- photo cards ----
def card(cx,cy,ang,kind,col):
    cw,ch=118,104
    c=Image.new("RGBA",(int((cw+20)*S),int((ch+20)*S)),(0,0,0,0)); cd=ImageDraw.Draw(c)
    cd.rounded_rectangle(s(12,14,cw+12,ch+14),radius=8*S,fill=(0,0,0,28))
    cd.rounded_rectangle(s(8,8,cw+8,ch+8),radius=8*S,fill="white")
    x0,y0,x1,y1=16,16,cw,ch-12
    cd.rounded_rectangle(s(x0,y0,x1,y1),radius=5*S,fill=col)
    mx=(x0+x1)/2
    if kind=="shop":
        cd.rectangle(s(mx-34,y0+30,mx+34,y1),fill=(255,250,244))
        for i in range(5):
            cd.polygon(s(mx-38+i*15.2,y0+18,mx-38+(i+1)*15.2,y0+18,mx-38+(i+1)*15.2,y0+32,mx-38+i*15.2,y0+32),fill=ACC if i%2==0 else (255,255,255))
        cd.rectangle(s(mx-8,y0+44,mx+8,y1),fill=(180,150,120))
        cd.rectangle(s(mx-28,y0+42,mx-14,y0+56),fill=(200,222,232)); cd.rectangle(s(mx+14,y0+42,mx+28,y0+56),fill=(200,222,232))
    elif kind=="chair":
        cd.rounded_rectangle(s(mx-22,y0+8,mx+22,y0+40),radius=12*S,fill=(210,228,236),outline=(255,255,255),width=3*S)
        cd.rounded_rectangle(s(mx-18,y0+44,mx+18,y0+58),radius=5*S,fill=ACC)
        cd.rectangle(s(mx-3,y0+58,mx+3,y1-6),fill=(120,110,100)); cd.rectangle(s(mx-16,y1-8,mx+16,y1-4),fill=(120,110,100))
    elif kind=="bottles":
        for i,(hh,cc) in enumerate([(40,(255,255,255)),(52,ACC),(34,(200,190,220))]):
            bx=mx-30+i*22
            cd.rounded_rectangle(s(bx,y1-6-hh,bx+16,y1-6),radius=4*S,fill=cc)
            cd.rectangle(s(bx+5,y1-12-hh,bx+11,y1-6-hh),fill=(120,110,100))
    elif kind=="cup":
        cd.rounded_rectangle(s(mx-22,y0+24,mx+14,y0+58),radius=6*S,fill="white")
        cd.arc(s(mx+6,y0+30,mx+26,y0+48),-90,90,fill="white",width=4*S)
        cd.ellipse(s(mx-34,y0+56,mx+26,y0+66),fill=(255,255,255))
        for k in (-12,0): cd.arc(s(mx+k-4,y0+4,mx+k+6,y0+20),90,270,fill=(255,255,255),width=2*S)
    elif kind=="plant":
        cd.polygon(s(mx-16,y1-30,mx+16,y1-30,mx+12,y1-6,mx-12,y1-6),fill=ACC)
        for a,b in [(-26,-10),(0,-6),(22,-12)]:
            cd.ellipse(s(mx+a-10,y0+14+abs(a)/3,mx+a+10,y0+50),fill=(120,170,130))
    c=c.rotate(ang,resample=Image.BICUBIC,expand=True)
    img.paste(c,(int(cx*S-c.width/2),int(cy*S-c.height/2)),c)
cards=[(190,470,8,"shop"),(320,505,-6,"chair"),(450,470,5,"bottles"),(580,505,-7,"cup"),(705,465,6,"plant")]
# dotted flow line
import math
pts=[(150,560),(400,585),(650,575),(800,520),(880,450)]
def bez(t):
    # simple catmull through pts
    n=len(pts)-1; i=min(int(t*n),n-1); u=t*n-i
    p0=pts[max(i-1,0)];p1=pts[i];p2=pts[i+1];p3=pts[min(i+2,n)]
    return tuple(0.5*((2*p1[k])+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u**3) for k in (0,1))
for j in range(46):
    x,y=bez(j/46); d.ellipse(s(x-3,y-3,x+3,y+3),fill=ACC)
# arrow head toward phone
ax,ay=bez(1.0); bx,by=bez(0.97); a=math.atan2(ay-by,ax-bx)
tip=(ax+14*math.cos(a),ay+14*math.sin(a))
l=(ax+14*math.cos(a+2.4),ay+14*math.sin(a+2.4)); r=(ax+14*math.cos(a-2.4),ay+14*math.sin(a-2.4))
d.polygon(s(*tip,*l,*r),fill=ACC)
for i,(cx,cy,ang,k) in enumerate(cards): card(cx,cy,ang,k,SOFT[i])

# ---- phone ----
px0,py0,px1,py1=900,92,1110,520
sh=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sh)
sd.rounded_rectangle(s(px0+8,py0+14,px1+8,py1+14),radius=34*S,fill=(90,60,40,60))
sh=sh.filter(ImageFilter.GaussianBlur(12*S)); img.paste(sh,(0,0),sh); d=ImageDraw.Draw(img)
d.rounded_rectangle(s(px0,py0,px1,py1),radius=34*S,fill=(64,58,54))
sx0,sy0,sx1,sy1=px0+10,py0+10,px1-10,py1-10
scr=Image.new("RGB",s(sx1-sx0,sy1-sy0),(246,236,224)); q=ImageDraw.Draw(scr)
sw,shh=sx1-sx0,sy1-sy0
def t(*v): return [int(x*S) for x in v]
# salon scene (no people)
q.rectangle(t(0,0,sw,shh*0.62),fill=(244,232,216))
q.rectangle(t(0,shh*0.62,sw,shh),fill=(226,208,186))
q.rounded_rectangle(t(sw/2-46,60,sw/2+46,190),radius=46*S,fill=(214,232,238),outline="white",width=6*S)
q.line(t(sw/2-20,90,sw/2+10,70),fill="white",width=4*S)
q.rounded_rectangle(t(sw/2-44,230,sw/2+44,262),radius=10*S,fill=ACC)
q.rounded_rectangle(t(sw/2-36,196,sw/2+36,236),radius=12*S,fill=(236,150,100))
q.rectangle(t(sw/2-5,262,sw/2+5,300),fill=(110,100,92)); q.rounded_rectangle(t(sw/2-34,298,sw/2+34,306),radius=4*S,fill=(110,100,92))
q.polygon(t(18,shh*0.62-6,46,shh*0.62-6,42,shh*0.62+24,22,shh*0.62+24),fill=(255,250,244))
for a in (-12,0,12): q.ellipse(t(32+a-9,190,32+a+9,shh*0.62-2),fill=(120,170,130))
q.ellipse(t(sw-70,22,sw-20,72),fill=(255,236,190))
# subtitle
cap="くつろげる空間で"; fc=f(17)
cw_=q.textlength(cap,font=fc)/S
q.rounded_rectangle(t(sw/2-cw_/2-10,shh-96,sw/2+cw_/2+10,shh-66),radius=6*S,fill=(40,36,34))
q.text(t(sw/2,shh-81),cap,font=fc,fill="white",anchor="mm")
# progress bar + play
q.rounded_rectangle(t(16,shh-36,sw-16,shh-30),radius=3*S,fill=(255,255,255))
q.rounded_rectangle(t(16,shh-36,sw*0.55,shh-30),radius=3*S,fill=ACC)
q.ellipse(t(sw*0.55-7,shh-40,sw*0.55+7,shh-26),fill=ACC)
mask=Image.new("L",scr.size,0); ImageDraw.Draw(mask).rounded_rectangle([0,0,scr.width-1,scr.height-1],radius=26*S,fill=255)
img.paste(scr,s(sx0,sy0),mask); d=ImageDraw.Draw(img)
d.rounded_rectangle(s((px0+px1)/2-30,py0+16,(px0+px1)/2+30,py0+28),radius=6*S,fill=(64,58,54))
# play badge
d.ellipse(s(px1-30,py0+44,px1+26,py0+100),fill=ACC,outline="white",width=4*S)
cx,cy=px1-2,py0+72; d.polygon(s(cx-8,cy-12,cx-8,cy+12,cx+13,cy),fill="white")
# label under phone
d.text(s((px0+px1)/2,py1+40),"AIで動画に",font=f(26),fill=ACC,anchor="mm",stroke_width=int(0.8*S),stroke_fill=ACC)
# logo
d.text(s(1240,640),"turtle ad",font=f(20),fill=SUB,anchor="rs")
img=img.resize((1280,670),Image.LANCZOS)
img.save("/home/user/turtlead-reels/img/note/note_header_20261123_ai_video.png")
