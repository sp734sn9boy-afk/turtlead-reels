// 使い方: node render.js  → ../01_reel_A.png など（1220x1240）を書き出す
const path = require('path');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const list = [['rA', '01_reel_A'], ['rB', '01_reel_B'], ['rC', '01_reel_C'], ['lA', '02_logo_A'], ['lB', '02_logo_B'], ['lC', '02_logo_C']];
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  const pg = await b.newPage({ viewport: { width: 1220, height: 1240 }, deviceScaleFactor: 1 });
  for (const [k, f] of list) {
    await pg.goto('file://' + path.join(__dirname, 'thumbs.html') + '?s=' + k, { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(300);
    await pg.screenshot({ path: path.join(__dirname, '..', f + '.png') });
  }
  await b.close();
})();
