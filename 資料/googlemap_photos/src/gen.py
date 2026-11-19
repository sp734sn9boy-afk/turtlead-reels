# 使い方: python3 gen.py → 01〜06 の HTML を作る（書き出しは render.js）
LOGO='<svg viewBox="0 0 100 100" aria-hidden="true"><polygon points="50,6 88.1,28 88.1,72 50,94 11.9,72 11.9,28" fill="#0D3A34" stroke="#3CD6F0" stroke-width="3" stroke-linejoin="round"/><polygon points="50,32 65.6,41 65.6,59 50,68 34.4,59 34.4,41" fill="none" stroke="#3CD6F0" stroke-width="2.5" stroke-linejoin="round"/><path d="M50 6 L50 32 M88.1 28 L65.6 41 M88.1 72 L65.6 59 M50 94 L50 68 M11.9 72 L34.4 59 M11.9 28 L34.4 41" stroke="#3CD6F0" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.8"/><g fill="#fff"><circle cx="50" cy="32" r="3"/><circle cx="65.6" cy="41" r="3"/><circle cx="65.6" cy="59" r="3"/><circle cx="50" cy="68" r="3"/><circle cx="34.4" cy="59" r="3"/><circle cx="34.4" cy="41" r="3"/></g><circle cx="50" cy="50" r="5" fill="#3CD6F0"/></svg>'
FONTS='<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&family=M+PLUS+Rounded+1c:wght@800&display=block" rel="stylesheet">'
MARK=f'<span class="mark">{LOGO}<span>turtle <b>ad</b></span></span>'
def page(name,title,css,body):
    open(name,'w').write(f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>{title}</title>{FONTS}
<link rel="stylesheet" href="base.css"><style>{css}</style></head><body>{body}</body></html>''')

DEV_CSS='''
.laptop{position:absolute;left:168px;top:330px;width:792px}
.laptop .scr{width:792px;height:507px;padding:16px;border-radius:18px;background:#0b0f1a;border:2px solid #3a4560;box-shadow:0 30px 60px rgba(0,0,0,.55),0 0 40px rgba(79,227,255,.15)}
.laptop .scr img{width:760px;height:475px;object-fit:cover;object-position:top;border-radius:4px;display:block}
.laptop .base{width:900px;height:26px;margin-left:-54px;border-radius:0 0 18px 18px;background:linear-gradient(#56627e,#2a3248);position:relative}
.laptop .base::before{content:"";position:absolute;left:50%;top:0;width:150px;height:9px;margin-left:-75px;border-radius:0 0 9px 9px;background:#1b2133}
.phone{position:absolute;left:812px;top:460px;width:252px;height:530px;padding:11px;border-radius:38px;background:#0b0f1a;border:2px solid #3a4560;box-shadow:0 30px 60px rgba(0,0,0,.6),0 0 40px rgba(79,227,255,.18)}
.phone img{width:226px;height:504px;object-fit:cover;object-position:top;border-radius:28px;display:block}
'''
def demo(fn,site,kicker,title,crop=0):
    body=f'''<div class="head"><p class="kicker">{kicker}</p><h1 class="title">{title}</h1></div>
<div class="laptop"><div class="scr"><img src="shots/{site}_pc.png" style="object-position:0 -{crop}px;height:{475+crop}px;margin-bottom:-{crop}px"></div><div class="base"></div></div>
<div class="phone"><img src="shots/{site}_sp.png"></div>
<div class="foot">{MARK}<span class="sep"></span><span>ホームページ見本（パソコン・スマホ）</span></div>'''
    page(fn,title,DEV_CSS+'.laptop .scr{overflow:hidden}',body)
demo('01_hp_katsuobushi.html','kanetamaru','ホームページ制作','鰹節工場の見本サイト')
demo('02_hp_bankin.html','motowaki','ホームページ制作','建築板金会社の見本サイト',crop=0)

REEL_CSS='''
.row{position:absolute;left:125px;top:292px;width:950px;display:flex;gap:22px}
.ph{width:302px}
.ph .f{width:302px;height:521px;padding:10px;border-radius:34px;background:#0b0f1a;border:2px solid #3a4560;box-shadow:0 24px 50px rgba(0,0,0,.55),0 0 34px rgba(79,227,255,.15)}
.ph img{width:278px;height:497px;object-fit:cover;border-radius:24px;display:block}
.ph p{margin-top:16px;text-align:center;font-size:30px;font-weight:700}
.note{position:absolute;left:120px;right:120px;top:900px;text-align:center;font-size:22px;color:var(--sub)}
'''
page('03_reel.html','AIリール動画',REEL_CSS,f'''<div class="head"><p class="kicker">AIリール動画</p><h1 class="title">縦長のショート動画を制作</h1></div>
<div class="row">
<div class="ph"><div class="f"><img src="frames/izakaya_sel.png"></div><p>居酒屋</p></div>
<div class="ph"><div class="f"><img src="frames/biyoshitsu_sel.png"></div><p>美容室</p></div>
<div class="ph"><div class="f"><img src="frames/koumuten_sel.png"></div><p>工務店</p></div>
</div>
<p class="note">※サンプル動画の一場面。お店・住宅はAIで作ったイメージ（架空）です</p>
<div class="foot">{MARK}</div>''')

COV=['ichikikushikino','kanoya','kirishima','minamikyushu','satsuma']
MAG_CSS='''
.fan{position:absolute;left:0;top:0;width:1200px;height:1200px}
.fan img{position:absolute;width:300px;height:424px;border-radius:6px;box-shadow:0 20px 40px rgba(0,0,0,.6);border:3px solid #fff}
.sub{position:absolute;left:120px;right:120px;top:902px;text-align:center;font-size:30px;font-weight:700;color:var(--sub)}
'''
pos=[(-16,150,420,1),(-8,290,385,2),(16,750,420,1),(8,610,385,2),(0,450,365,3)]
order=['ichikikushikino','kanoya','satsuma','minamikyushu','kirishima']
imgs=''.join(f'<img src="dl/{c}-2026-cover.webp" style="left:{x}px;top:{y}px;transform:rotate({r}deg);z-index:{z}">' for c,(r,x,y,z) in zip(order,pos))
page('04_mytown.html','マイタウンガイド',MAG_CSS,f'''<div class="head"><p class="kicker">地域情報誌</p><h1 class="title">マイタウンガイド</h1></div>
<div class="fan">{imgs}</div>
<p class="sub">鹿児島の各地域で発行するフリーペーパー</p>
<div class="foot">{MARK}</div>''')

AI_CSS='''
.chips{position:absolute;left:120px;right:120px;top:292px;display:flex;justify-content:center;gap:16px}
.chips span{font-size:28px;font-weight:700;padding:10px 26px;border-radius:30px;border:2px solid rgba(79,227,255,.45);color:var(--sub)}
.chips .on{background:var(--cyan);color:#04101c;border-color:var(--cyan)}
.win{position:absolute;left:150px;top:390px;width:900px;border-radius:22px;background:rgba(8,16,36,.92);border:2px solid rgba(79,227,255,.4);box-shadow:0 30px 60px rgba(0,0,0,.5);padding:30px 34px}
.msg{display:flex;gap:16px;align-items:flex-start}
.msg.me{justify-content:flex-end}
.bub{font-size:30px;line-height:1.55;padding:18px 24px;border-radius:20px}
.me .bub{background:#2a3f7a;border-bottom-right-radius:6px;max-width:700px}
.ai{margin-top:24px}
.ai .ic{flex:0 0 58px;width:58px;height:58px}
.ai .bub{background:#f2f6ff;color:#16203a;border-top-left-radius:6px;max-width:760px}
.ai .bub strong{display:block;font-size:30px;font-weight:900;margin-bottom:4px}
.tag{display:inline-block;font-size:20px;font-weight:700;color:#04101c;background:var(--violet);border-radius:6px;padding:1px 10px;margin-bottom:8px}
.note{position:absolute;left:120px;right:120px;top:1010px;text-align:center;font-size:22px;color:var(--sub)}
'''
page('05_ai.html','AI活用サポート',AI_CSS,f'''<div class="head"><p class="kicker">AI活用サポート</p><h1 class="title">「書く仕事」をAIで下書き</h1></div>
<div class="chips"><span>メール返信</span><span class="on">求人文</span><span>SNS投稿</span></div>
<div class="win">
 <div class="msg me"><div class="bub">求人のメモです。伝わる文章にしてください。<br>・板金工事の見習い ・未経験OK ・週休2日</div></div>
 <div class="msg ai"><div class="ic">{LOGO}</div><div class="bub"><span class="tag">下書き</span><strong>未経験から、手に職を。</strong>屋根や外壁の板金工事を、先輩と一緒に<br>一から覚えていくお仕事です。<br>道具の使い方から、丁寧に教えます。<br>お休みは週2日です。</div></div>
</div>
<p class="note">※AIの下書きは、最後に人が確認してから使います</p>''')
# 05は下端までウィンドウがあるので foot は付けない

LG_CSS='''
.c{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.big{display:flex;align-items:center;gap:26px;font-family:'M PLUS Rounded 1c',sans-serif;font-weight:800;font-size:120px;line-height:1;color:#fff}
.big svg{width:160px;height:160px;filter:drop-shadow(0 0 14px rgba(60,214,240,.75))}
.big b{color:var(--logo);text-shadow:0 0 22px rgba(60,214,240,.6)}
.corp{margin-top:26px;font-size:40px;font-weight:700;letter-spacing:.06em;color:var(--sub)}
.rule{width:130px;height:5px;border-radius:3px;margin:40px 0 34px;background:linear-gradient(90deg,var(--cyan),var(--violet))}
.biz{font-size:36px;font-weight:700;line-height:1.6;color:#fff}
.biz em{font-style:normal;color:var(--cyan)}
'''
page('06_logo.html','ロゴ',LG_CSS,f'''<div class="c"><div class="big">{LOGO}<span>turtle <b>ad</b></span></div>
<p class="corp">合同会社turtle ad（タートルアド）</p><div class="rule"></div>
<p class="biz"><em>鹿児島</em>　ホームページ制作・AI動画<br>地域情報誌マイタウンガイド</p></div>''')
