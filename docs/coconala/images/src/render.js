// 使い方: node render.js  （thumb.html を 1220x1240 の PNG に書き出す）
const path = require('path');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const out = path.resolve(__dirname, '..');
const list = [['reel', '01_reel'], ['logo', '02_logo'], ['hp', '03_hp'], ['hosyu', '04_hosyu'], ['ai', '05_ai']];
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  const pg = await b.newPage({ viewport: { width: 1220, height: 1240 }, deviceScaleFactor: 1 });
  for (const [k, f] of list) {
    await pg.goto('file://' + path.join(__dirname, 'thumb.html') + '?s=' + k, { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.screenshot({ path: path.join(out, f + '.png') });
    console.log('saved', f);
  }
  await b.close();
})();
