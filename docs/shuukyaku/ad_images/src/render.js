const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(const n of ['ad_turtle_A','ad_turtle_B','ad_job_A','ad_job_B']){await p.goto('file://'+__dirname+'/'+n+'.html',{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);await p.screenshot({path:__dirname+'/../'+n+'.png'});}
await b.close();})();
