// 使い方: node render_anim.js  → logo_frames/*.png（5秒・30fps）を書き出す。そのあと ffmpeg で logo_sample.mp4 にする
const path = require('path'), fs = require('fs');
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await pg.goto('file://' + path.join(__dirname, 'anim.html'));
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(500);
  const d = process.argv[2]; fs.mkdirSync(d, { recursive: true });
  for (let i = 0; i < 150; i++) { await pg.evaluate((t) => show(t), i / 30); await pg.screenshot({ path: path.join(d, String(i).padStart(3, '0') + '.png') }); }
  await b.close();
})();
