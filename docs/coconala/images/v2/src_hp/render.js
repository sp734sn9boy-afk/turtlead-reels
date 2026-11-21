// node render.js : thumbs.html を 1220x1240 のPNGに書き出し、縮小確認用シートも作る
const path=require('path');const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const L=[['hpA','03_hp_A'],['hpB','03_hp_B'],['hpC','03_hp_C'],['hoA','04_hosyu_A'],['hoB','04_hosyu_B'],['hoC','04_hosyu_C']];
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome'});const p=await b.newPage({viewport:{width:1220,height:1240}});
for(const [k,f] of L){await p.goto('file://'+path.join(__dirname,'thumbs.html')+'?s='+k,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:path.join(__dirname,'..',f+'.png')});}
await b.close();})();
