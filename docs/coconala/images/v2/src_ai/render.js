// 使い方: node render.js A B C （a.html 等を 1220x1240 の PNG に書き出す）
const path = require('path');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  const pg = await b.newPage({ viewport: { width: 1220, height: 1240 }, deviceScaleFactor: 1 });
  for (const k of process.argv.slice(2)) {
    await pg.goto('file://' + path.join(__dirname, k.toLowerCase() + '.html'), { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.waitForTimeout(300);
    await pg.screenshot({ path: path.join(__dirname, '..', '05_ai_' + k + '.png') });
    console.log('saved', k);
  }
  await b.close();
})();
