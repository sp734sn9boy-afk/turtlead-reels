// リンク集：OGP画像の書き出しと、スマホ/PC幅の確認スクショ
// 使い方（資料/links/src/ で）：NODE_PATH=/opt/node-tools/node_modules node render.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const base = path.resolve(__dirname, '..');
const pub = path.join(base, '公開用', 'links');
const shots = path.join(base, 'screenshots');
(async () => {
  const b = await chromium.launch();
  // 1) OGP画像 1200x630
  let p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto('file://' + path.join(__dirname, 'og.html')); await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(pub, 'og_tmp.png') });
  await p.close();
  // 2) 確認用：サーバーと同じ並び（/assets/logo.css と /links/）を一時フォルダに作る
  const tmp = fs.mkdtempSync('/tmp/links-');
  fs.mkdirSync(path.join(tmp, 'assets')); fs.mkdirSync(path.join(tmp, 'links'));
  fs.copyFileSync(path.join(base, '..', 'ai_komon', '元ページ', 'logo.css'), path.join(tmp, 'assets', 'logo.css'));
  for (const f of fs.readdirSync(pub)) fs.copyFileSync(path.join(pub, f), path.join(tmp, 'links', f));
  const url = 'file://' + path.join(tmp, 'links', 'index.html');
  for (const [name, w, h, dpr] of [['sp_390', 390, 844, 3], ['sp_360', 360, 740, 2], ['pc_1280', 1280, 900, 1]]) {
    p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr });
    await p.goto(url, { waitUntil: 'networkidle' }); await p.waitForTimeout(800);
    await p.screenshot({ path: path.join(shots, name + '_full.png'), fullPage: true });
    await p.screenshot({ path: path.join(shots, name + '_firstview.png') });
    const m = await p.evaluate(() => ({
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
      btnHeights: [...document.querySelectorAll('.bt,.sns a')].filter(e => e.offsetParent).map(e => Math.round(e.getBoundingClientRect().height)),
      overflow: [...document.querySelectorAll('.bt .tx b,.bt .tx span,.sns a')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent.trim()),
      fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v, i, a) => a.indexOf(v) === i),
    }));
    console.log(name, JSON.stringify(m));
    await p.close();
  }
  await b.close();
})();
