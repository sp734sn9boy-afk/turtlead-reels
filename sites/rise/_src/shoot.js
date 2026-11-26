// 使い方: node sites/rise/_src/shoot.js  （OGP画像・favicon・スクリーンショットを書き出し）
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const ROOT=path.resolve(__dirname,'..');const OUT=path.join(ROOT,'screenshots');
const pages=[['top','index.html'],['diet','diet/index.html'],['seitai','seitai/index.html'],['ikumou','ikumou/index.html'],['hada','hada/index.html']];
(async()=>{
 const b=await chromium.launch();
 const only=process.argv[2];
 if(!only||only==='ogp'){
  const p=await b.newPage({viewport:{width:1200,height:630}});
  await p.goto('file://'+path.join(__dirname,'ogp.html'));await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
  await p.screenshot({path:path.join(ROOT,'img/ogp.jpg'),type:'jpeg',quality:88});await p.close();
  const f=await b.newPage({viewport:{width:64,height:64}});
  await f.setContent('<body style="margin:0;background:transparent"><div style="width:64px;height:64px;border-radius:14px;background:#1d5a3e;display:grid;place-items:center;border:3px solid #e9cf8a;box-sizing:border-box"><span style="font:italic 700 40px Georgia,serif;color:#e9cf8a">R</span></div></body>');
  await f.screenshot({path:path.join(ROOT,'img/favicon.png'),omitBackground:true});await f.close();
  if(only==='ogp'){await b.close();return}
 }
 fs.mkdirSync(OUT,{recursive:true});
 for(const [w,tag] of [[375,'sp375'],[1280,'pc1280']]){
  const ctx=await b.newContext({viewport:{width:w,height:w<500?812:800},deviceScaleFactor:2,isMobile:w<500,hasTouch:w<500});
  for(const [name,file] of pages){
   if(only&&only!==name)continue;
   const p=await ctx.newPage();
   await p.goto('file://'+path.join(ROOT,file));
   await p.evaluate(()=>document.querySelectorAll('[loading=lazy]').forEach(e=>e.loading='eager'));await p.waitForLoadState('networkidle').catch(()=>{});await p.evaluate(()=>document.fonts.ready);
   await p.waitForTimeout(3200);// ファーストビューの動きが終わるまで
   await p.screenshot({path:path.join(OUT,`${tag}-${name}-top.png`)});
   // ふわっと表示を全部出す
   await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=400){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60))}window.scrollTo(0,0);document.querySelectorAll('.rv').forEach(e=>e.classList.add('on'))});
   await p.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})))});
   await p.addStyleTag({content:'.fbar{display:none!important}'});
   await p.waitForTimeout(2500);
   const sw=await p.evaluate(()=>document.documentElement.scrollWidth);
   if(sw>w)console.log('横スクロールあり',tag,name,sw);
   await p.screenshot({path:path.join(OUT,`${tag}-${name}-full.png`),fullPage:true});
   await p.close();
  }
  await ctx.close();
 }
 await b.close();
})();
