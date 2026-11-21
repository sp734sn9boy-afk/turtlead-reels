// 使い方: NODE_PATH=/opt/node-tools/node_modules node render.js
// pages.html の .page を1枚ずつ 1080x1920 PNG に書き出す（保存先は data-out）。
// check/guide_*.png は上下250px（ボタンで隠れる帯）と表紙の直径600px円を重ねた確認用。
const { chromium } = require('playwright-core');
const path = require('path'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'pages.html'));
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(600);
  const root = path.join(__dirname, '..');
  // はみ出しチェック：ストーリーズは文字が y250〜1670・x0〜1080 に収まっているか、表紙は円の中か
  const rep = await p.evaluate(() => [...document.querySelectorAll('.page')].map(pg => {
    const o = pg.getBoundingClientRect(); const bad = [];
    const safe = pg.querySelector('.safe');
    if (safe && safe.scrollHeight > safe.clientHeight + 1) bad.push('safe overflow ' + (safe.scrollHeight - safe.clientHeight) + 'px');
    pg.querySelectorAll('.safe *').forEach(e => { const r = e.getBoundingClientRect(); if (!r.width) return;
      const t = r.top - o.top, bt = r.bottom - o.top, l = r.left - o.left, rr = r.right - o.left;
      if (t < 249 || bt > 1671 || l < 0 || rr > 1080) bad.push(`${e.tagName}.${e.className} ${Math.round(l)},${Math.round(t)}-${Math.round(rr)},${Math.round(bt)}`); });
    const fonts = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family);
    return { out: pg.dataset.out, bad, fonts: [...new Set(fonts)] };
  }));
  console.log(JSON.stringify(rep, null, 1));
  const pages = await p.$$('.page');
  for (const [i, el] of pages.entries()) {
    const out = path.join(root, rep[i].out); fs.mkdirSync(path.dirname(out), { recursive: true });
    await el.screenshot({ path: out });
  }
  await p.evaluate(() => document.body.classList.add('guide'));
  fs.mkdirSync(path.join(root, 'check'), { recursive: true });
  for (const [i, el] of pages.entries())
    await el.screenshot({ path: path.join(root, 'check', 'guide_' + rep[i].out.replace(/\//g, '_')) });
  await b.close();
})();
