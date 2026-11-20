// 見本HTMLのスクリーンショットを撮るスクリプト
// 実行: NODE_PATH=/opt/node22/lib/node_modules node shot.js
const path = require('path');
const { chromium } = require('playwright');

const here = __dirname;
const url = 'file://' + path.join(here, 'ai_index_komon_sample.html');
const outDir = path.join(here, 'screenshots');

(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  for (const [label, width, dsf] of [['sp390', 390, 2], ['pc1280', 1280, 1]]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: dsf, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    // 出てくる動きを全部表示した状態にする
    await page.evaluate(() => document.querySelectorAll('.rv').forEach(e => e.classList.add('in')));
    // ヘッダーが重ならないように固定を外す
    await page.addStyleTag({ content: '.hd{position:absolute!important}' });
    // はみ出しチェック
    const overflow = await page.evaluate(() => {
      const w = document.documentElement.clientWidth;
      const bad = [];
      document.querySelectorAll('#komon *, #price *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width && (r.right > w + 0.5 || r.left < -0.5)) bad.push(el.className || el.tagName);
      });
      return { w, sw: document.documentElement.scrollWidth, bad: bad.slice(0, 10) };
    });
    console.log(label, JSON.stringify(overflow));
    await page.locator('#komon').screenshot({ path: path.join(outDir, `komon_${label}.png`) });
    await page.locator('#price').screenshot({ path: path.join(outDir, `price_${label}.png`) });
    if (label === 'sp390') {
      await page.locator('#komon .km-plans .plan').nth(1).screenshot({ path: path.join(outDir, `komon_${label}_standard_card.png`) });
    }
    await page.locator('#faq').evaluate(el => el.querySelectorAll('details').forEach(d => d.open = true));
    await page.locator('#faq').screenshot({ path: path.join(outDir, `faq_${label}.png`) });
    await ctx.close();
  }
  await browser.close();
})();
