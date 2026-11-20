// 公開用ファイル（公開用/ai/index.html）のスクリーンショット
// 実行: NODE_PATH=/opt/node22/lib/node_modules node shot_public.js
// ../assets/logo.css は手元にないため、元ページの控え（元ページ/logo.css）を差し込んで表示する。
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const here = __dirname;
const url = 'file://' + path.join(here, '公開用', 'ai', 'index.html');
const outDir = path.join(here, 'screenshots', '公開用');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  for (const [label, width, dsf] of [['sp390', 390, 2], ['pc1280', 1280, 1]]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: dsf, reducedMotion: 'reduce' });
    await ctx.route(/assets\/logo\.css$/, r => r.fulfill({ contentType: 'text/css', body: fs.readFileSync(path.join(here, '元ページ', 'logo.css')) }));
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => document.querySelectorAll('.rv').forEach(e => e.classList.add('in')));
    await page.addStyleTag({ content: '.hd{position:absolute!important}' });
    const sw = await page.evaluate(() => [document.documentElement.clientWidth, document.documentElement.scrollWidth]);
    console.log(label, 'width/scrollWidth', sw);
    // AI顧問欄の注意書き〜締めのボタン
    const a = await page.locator('#komon .km-notes').boundingBox();
    const b = await page.locator('#komon .km-cta').boundingBox();
    const pad = 24;
    await page.screenshot({ path: path.join(outDir, `komon_notes_cta_${label}.png`), fullPage: true,
      clip: { x: 0, y: a.y - pad, width, height: (b.y + b.height) - a.y + pad * 2 } });
    await page.locator('#contact').screenshot({ path: path.join(outDir, `contact_${label}.png`) });
    await page.locator('#flow').screenshot({ path: path.join(outDir, `flow_${label}.png`) });
    await ctx.close();
  }
  await browser.close();
})();
