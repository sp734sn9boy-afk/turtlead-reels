// 使い方: NODE_PATH=<playwright-coreのある場所>/node_modules node render.js
// cover.html を 1920x1080 で書き出す。guide版は中央70%の枠線入り（確認用）
const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome' });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'cover.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  const out = path.join(__dirname, '..');
  await p.screenshot({ path: path.join(out, 'googlemap_cover.png') });
  const r = await p.evaluate(() => {
    const s = document.querySelector('.safe').getBoundingClientRect();
    return [...document.querySelectorAll('.logo,.corp,.catch .s,.catch .m,.pill')].map(e => {
      const q = e.getBoundingClientRect();
      return { cls: e.className, l: Math.round(q.left), r: Math.round(q.right), t: Math.round(q.top), b: Math.round(q.bottom),
        inside: q.left >= s.left && q.right <= s.right && q.top >= s.top && q.bottom <= s.bottom };
    }).concat([{fonts:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family).filter((v,i,a)=>a.indexOf(v)===i)}]);
  });
  console.log(JSON.stringify(r, null, 1));
  await p.evaluate(() => document.body.classList.add('guide'));
  await p.screenshot({ path: path.join(__dirname, 'check_safe70.png') });
  await b.close();
})();
