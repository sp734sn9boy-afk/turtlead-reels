// 使い方: NODE_PATH=/opt/node-tools/node_modules node render.js
// （先に python3 make_sprites.py でキャラ画像を作っておく）
// 出力: ../icon_800.png, ../banner_2560x1440.png, ../check/*.png
const { chromium } = require('playwright-core');
const path = require('path');
const OUT = path.join(__dirname, '..');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome' });

  // アイコン 800x800
  let p = await b.newPage({ viewport: { width: 800, height: 800 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'icon.html'));
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(OUT, 'icon_800.png') });
  await p.evaluate(() => document.body.classList.add('guide'));
  await p.screenshot({ path: path.join(OUT, 'check', 'icon_guide.png') });
  await p.close();

  // バナー 2560x1440
  p = await b.newPage({ viewport: { width: 2560, height: 1440 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'banner.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(OUT, 'banner_2560x1440.png') });
  const r = await p.evaluate(() => {
    const s = document.querySelector('.safe').getBoundingClientRect();
    const out = [...document.querySelectorAll('.turtle,.brand,.title,.sub,.pill,.team img')].map(e => {
      const q = e.getBoundingClientRect();
      return { el: e.className || e.getAttribute('src'), l: Math.round(q.left), r: Math.round(q.right), t: Math.round(q.top), b: Math.round(q.bottom),
        inside: q.left >= s.left && q.right <= s.right && q.top >= s.top && q.bottom <= s.bottom };
    });
    const fonts = [...document.fonts].map(f => f.family + ':' + f.status);
    return { safe: [s.left, s.top, s.right, s.bottom], out, fonts };
  });
  console.log(JSON.stringify(r, null, 1));
  // スマホ想定：中央 1546x423 だけ
  await p.screenshot({ path: path.join(OUT, 'check', 'banner_phone_safe_1546x423.png'), clip: { x: 507, y: 509, width: 1546, height: 423 } });
  // パソコン想定：横いっぱい 2560x423
  await p.screenshot({ path: path.join(OUT, 'check', 'banner_desktop_2560x423.png'), clip: { x: 0, y: 509, width: 2560, height: 423 } });
  await p.evaluate(() => document.body.classList.add('guide'));
  await p.screenshot({ path: path.join(OUT, 'check', 'banner_guide_safe.png') });
  await b.close();
})();
