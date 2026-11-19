// 使い方: NODE_PATH=/opt/node-tools/node_modules node render.js
// 01〜06 の HTML を 1200x1200 で撮って、親フォルダに JPG（品質90）で保存。check/ に中央80%枠つきの確認画像
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  const p = await b.newPage({ viewport: { width: 1200, height: 1200 }, deviceScaleFactor: 1 });
  fs.mkdirSync(path.join(__dirname, 'check'), { recursive: true });
  for (const f of fs.readdirSync(__dirname).filter(f => /^0\d_.*\.html$/.test(f)).sort()) {
    await p.goto('file://' + path.join(__dirname, f), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
    const base = f.replace('.html', '');
    const png = path.join(__dirname, 'check', base + '.png');
    await p.screenshot({ path: png });
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', png, '-q:v', '2', path.join(__dirname, '..', base + '.jpg')]);
    await p.evaluate(() => document.body.classList.add('guide'));
    await p.screenshot({ path: path.join(__dirname, 'check', base + '_guide.png') });
    const fonts = await p.evaluate(() => [...new Set([...document.fonts].filter(x => x.status === 'loaded').map(x => x.family))]);
    console.log(base, fonts.join(','));
  }
  await b.close();
})();
