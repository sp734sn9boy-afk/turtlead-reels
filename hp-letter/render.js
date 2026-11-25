// letter.html → ホームページ案内文_2種.pdf と確認用PNG（node render.js）
// 見本付き版：node render.js letter_sample.html ホームページ案内文_見本付き版_2種.pdf preview_sample_
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path=require('path'); const D=__dirname;
const [HTML='letter.html',PDF='ホームページ案内文_2種.pdf',PNG='preview_']=process.argv.slice(2);
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:900,height:1200},deviceScaleFactor:2});
  await p.goto('file://'+path.join(D,HTML),{waitUntil:'networkidle'});
  await p.evaluate(()=>document.fonts.ready);
  const fonts=await p.evaluate(()=>['Noto Sans JP','Outfit','M PLUS Rounded 1c'].map(f=>f+':'+document.fonts.check('900 12px "'+f+'"')+'/'+document.fonts.check('700 12px "'+f+'"')));
  console.log('fonts',fonts.join(' '));
  const chk=await p.evaluate(()=>[...document.querySelectorAll('.page')].map(pg=>{const r=pg.getBoundingClientRect();const kids=[...pg.children];const sum=kids.reduce((a,k)=>a+k.getBoundingClientRect().height,0);
    const body=pg.querySelector('.body');const inner=[...body.children].reduce((a,k)=>Math.max(a,k.getBoundingClientRect().bottom),0);
    const over=[...pg.querySelectorAll('*')].filter(e=>{const q=e.getBoundingClientRect();return q.width&&(q.right>r.right+0.5||q.bottom>r.bottom+0.5)}).map(e=>e.className||e.tagName).slice(0,5);
    const clip=[...pg.querySelectorAll('h1,h2,h3,p,li,b,span')].filter(e=>e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='visible').length;
    return {id:pg.id,h:r.height.toFixed(1),childrenSum:sum.toFixed(1),bodyBottomSpare:(body.getBoundingClientRect().bottom-inner).toFixed(1),over}}));
  console.log(JSON.stringify(chk));
  for(const id of ['A','B']){ const el=await p.$('#'+id); await el.screenshot({path:path.join(D,PNG+id+'.png')}); }
  await p.emulateMedia({media:'print'});
  await p.pdf({path:path.join(D,PDF),format:'A4',printBackground:true,margin:{top:0,right:0,bottom:0,left:0},preferCSSPageSize:true});
  await b.close();
})();
