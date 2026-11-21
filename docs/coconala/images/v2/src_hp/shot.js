// 見本サイト3つを PC(1440x900) と スマホ(390x844 @2x) で撮る: node shot.js
const path=require('path');const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome'});
for(const s of ['koumuten','izakaya','biyou']){
 for(const [k,vp,sf] of [['pc',{width:1440,height:900},1],['sp',{width:390,height:800},2]]){
  const p=await b.newPage({viewport:vp,deviceScaleFactor:sf});
  await p.goto('file://'+path.join(__dirname,'site_'+s+'.html'),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
  await p.screenshot({path:path.join(__dirname,'shots',s+'_'+k+'.png')});
  await p.screenshot({path:path.join(__dirname,'shots',s+'_'+k+'_full.png'),fullPage:true});await p.close();}}
await b.close();})();
