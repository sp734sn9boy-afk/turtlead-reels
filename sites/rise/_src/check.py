# リンク・画像のパス確認（python3 sites/rise/_src/check.py）
import re,os,glob,html
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad=0;ext=set()
for f in ['index.html']+[p+'/index.html' for p in ['diet','seitai','ikumou','hada']]:
    s=open(os.path.join(root,f),encoding='utf-8').read();d=os.path.dirname(os.path.join(root,f))
    ids=set(re.findall(r'id="([^"]+)"',s))
    for attr,u in re.findall(r'(href|src|srcset)="([^"]+)"',s):
        u=html.unescape(u)
        if u.startswith(('http','tel:','mailto:')): ext.add(u); continue
        path,_,frag=u.partition('#')
        if path=='' :
            if frag and frag not in ids: print('NG anchor',f,u);bad+=1
            continue
        t=os.path.normpath(os.path.join(d,path))
        if os.path.isdir(t): t=os.path.join(t,'index.html')
        if not os.path.exists(t): print('NG',f,u);bad+=1
        elif frag:
            if f'id="{frag}"' not in open(t,encoding='utf-8').read(): print('NG anchor',f,u);bad+=1
    imgs=re.findall(r'<img [^>]*>',s)
    for i in imgs:
        if 'alt="' not in i: print('alt なし',f,i[:80]);bad+=1
    hs=re.findall(r'<h([1-6])',s); print(f,'h1数',hs.count('1'),'見出し順',''.join(hs)[:60])
    for old in ['NzwOZKQ','lMeHU7K','iiv7BQk','HP特別特典','#b3262f','example.com']:
        if old in s: print('残っている',f,old);bad+=1
print('外部リンク:');[print(' ',e) for e in sorted(ext) if 'fonts.g' not in e]
print('NG合計',bad)
