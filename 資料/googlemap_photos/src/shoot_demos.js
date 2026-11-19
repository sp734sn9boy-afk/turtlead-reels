// 使い方: NODE_PATH=/opt/node-tools/node_modules node shoot_demos.js
// turtle-ad.com/demo/ の見本サイトを パソコン(1440x900) と スマホ(390x844) で撮影して shots/ に保存
const { chromium } = require('playwright-core');
const path = require('path');
const demos = ['eisei', 'kanetamaru', 'motowaki'];
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  for (const d of demos) {
    const url = `https://www.turtle-ad.com/demo/${d}/`;
    for (const [kind, vp, dpr, mobile] of [['pc', { width: 1440, height: 900 }, 1.5, false], ['sp', { width: 390, height: 844 }, 3, true]]) {
      const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: dpr, isMobile: mobile, hasTouch: mobile });
      const p = await ctx.newPage();
      await p.goto(url, { waitUntil: 'networkidle' });
      await p.evaluate(() => document.fonts.ready);
      // 出てくる動き（フェードイン）を全部表示状態にする
      await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); });
      await p.waitForTimeout(1500);
      await p.screenshot({ path: path.join(__dirname, 'shots', `${d}_${kind}.png`) });
      await p.screenshot({ path: path.join(__dirname, 'shots', `${d}_${kind}_full.png`), fullPage: true });
      if (kind === 'pc') console.log(d, await p.title());
      await ctx.close();
    }
  }
  await b.close();
})();
