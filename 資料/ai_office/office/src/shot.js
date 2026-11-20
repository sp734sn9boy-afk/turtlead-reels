// 使い方: node shot.js   スマホ幅(390)とPC幅(1280)で数秒おきにスクショを撮り、はみ出しを調べる
'use strict';
const path = require('path'), fs = require('fs');
let chromium; try { ({ chromium } = require('playwright-core')); } catch { ({ chromium } = require('/opt/node-tools/node_modules/playwright-core')); }
const FILE = 'file://' + path.join(__dirname, '..', 'ai_office.html');
const OUT = path.join(__dirname, '..', 'screenshots'); fs.mkdirSync(OUT, { recursive: true });
const times = (process.env.TIMES || '3,12,22,32,45,60').split(',').map(Number);
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome' });
  for (const [name, w, h, dpr] of [['phone', 390, 844, 3], ['pc', 1280, 900, 1]]) {
    const pg = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: dpr });
    const errs = []; pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => m.type() === 'error' && errs.push(m.text()));
    await pg.goto(FILE); await pg.evaluate(() => document.fonts.ready);
    const t0 = Date.now();
    for (const s of times) {
      const wait = s * 1000 - (Date.now() - t0); if (wait > 0) await pg.waitForTimeout(wait);
      const chk = await pg.evaluate(() => {
        const bad = [];
        if (document.documentElement.scrollWidth > innerWidth) bad.push('横スクロール ' + document.documentElement.scrollWidth);
        document.querySelectorAll('.tag').forEach(t => { if (t.scrollWidth > t.clientWidth + 1) bad.push('名札はみ出し ' + t.textContent); const sl = t.parentElement.getBoundingClientRect(), r = t.getBoundingClientRect(); if (r.left < sl.left - 1 || r.right > sl.right + 1) bad.push('名札が机の幅より広い ' + t.textContent); });
        const fr = document.getElementById('floor').getBoundingClientRect();
        document.querySelectorAll('.bub.on,.pop').forEach(e => { const r = e.getBoundingClientRect(); if (r.left < fr.left - 1 || r.right > fr.right + 1) bad.push('吹き出しはみ出し ' + e.textContent); });
        document.querySelectorAll('.island').forEach(i => { const r = i.getBoundingClientRect(); if (r.right > fr.right + 1) bad.push('島はみ出し'); });
        return { bad, msg: document.getElementById('msg').textContent, h: document.documentElement.scrollHeight };
      });
      console.log(name, s + 's', chk.msg, chk.bad.length ? chk.bad : '', 'h=' + chk.h);
      await pg.screenshot({ path: path.join(OUT, `${name}_${String(s).padStart(2, '0')}s.png`), fullPage: true });
    }
    if (errs.length) console.log('ERR', name, errs);
    await pg.close();
  }
  await b.close();
})();
