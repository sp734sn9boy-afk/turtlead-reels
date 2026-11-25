// make_letters.py から呼ばれる：差し込み済みHTML → 1社1枚のPDF
// フォントの読み込みを待ち、会社名が長いときは文字を縮めて1行に収め、はみ出し・下余白を調べる。
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 1200 } });
  const out = [];
  for (const j of jobs) {
    await p.goto('file://' + j.html, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const MM = 96 / 25.4, warn = [];
      const fontsOK = document.fonts.check('900 12px "Noto Sans JP"') && document.fonts.check('700 12px "Outfit"');
      if (!fontsOK) warn.push('フォント読み込み失敗');
      const pg = document.querySelector('.page'), pr = pg.getBoundingClientRect();

      // 宛名：日付とぶつからない幅に収める
      const addr = pg.querySelector('.addr'), to = addr.querySelector('.to'), nm = to.querySelector('.mm-name'), dt = addr.querySelector('.date');
      let ns = parseFloat(getComputedStyle(nm).fontSize) * 72 / 96;
      const nameFits = () => to.getBoundingClientRect().right <= addr.getBoundingClientRect().right + .5 &&
        to.getBoundingClientRect().width + dt.getBoundingClientRect().width + 4 * MM <= addr.getBoundingClientRect().width;
      while (!nameFits() && ns > 6) { ns -= .25; nm.style.fontSize = ns + 'pt'; }
      if (!nameFits()) warn.push('宛名が長すぎて収まらない');

      // 感謝価格の見出し：1行のまま・PRICEとぶつからない
      const sh = pg.querySelector('.price3 .sec-h'), h2 = sh.querySelector('h2'), bl = h2.querySelector('.blank'), bt = bl.querySelector('.mm-t'), en = sh.querySelector('.en');
      let bs = parseFloat(getComputedStyle(bt).fontSize) * 72 / 96;
      const blankFits = () => h2.scrollWidth <= h2.clientWidth + 1 && en.getBoundingClientRect().right <= sh.getBoundingClientRect().right + .5 &&
        h2.getBoundingClientRect().right + 2 * MM <= en.getBoundingClientRect().left;
      const bs0 = bs, shrink = (min) => { while (!blankFits() && bs > min) { bs -= .25; bt.style.fontSize = bs + 'pt'; } };
      shrink(9);                                   // 9pt未満にしない（年配の方向けの決まり）
      if (!blankFits() && bl.dataset.fixed !== '1' && bl.dataset.short !== bt.textContent) {
        bt.textContent = bl.dataset.short; bs = bs0; bt.style.fontSize = ''; shrink(9);   // 「株式会社」などを外して再挑戦
      }
      if (!blankFits()) { shrink(6); warn.push(blankFits() ? '感謝価格の見出しの会社名が9pt未満で小さい（CSVの「略称」列に短い名前を入れると直ります）' : '感謝価格の見出しに会社名が収まらない（「略称」列に短い名前を入れてください）'); }
      const bl_text = bt.textContent;

      // はみ出し・下余白
      const over = [...pg.querySelectorAll('*')].filter(e => { const q = e.getBoundingClientRect(); return q.width && (q.right > pr.right + .5 || q.bottom > pr.bottom + .5); });
      if (over.length) warn.push('紙面からはみ出し');
      const fine = pg.querySelector('.fine'), rg = document.createRange(); rg.selectNodeContents(fine);
      const bottomMM = (pr.bottom - rg.getBoundingClientRect().bottom) / MM;
      if (bottomMM < 4.9) warn.push('下余白が5mm未満');
      const qr = pg.querySelector('.mm-qr');
      if (qr) { const a = qr.getBoundingClientRect(), bx = qr.parentElement.getBoundingClientRect();
        if (a.left < bx.left + 1.5 * MM || a.right > bx.right - 1.5 * MM || a.top < bx.top + 1.5 * MM || a.bottom > bx.bottom - 1.5 * MM) warn.push('QRが点線の枠からはみ出し');
        if (a.width < 20 * MM) warn.push('QRが小さすぎる'); }
      return { warn, bottomMM: bottomMM.toFixed(1), nameSize: ns.toFixed(2), blankSize: bs.toFixed(2), blankText: bl_text, qrMM: qr ? (qr.getBoundingClientRect().width / MM).toFixed(1) : '' };
    });
    await p.emulateMedia({ media: 'print' });
    await p.pdf({ path: j.pdf, format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, preferCSSPageSize: true });
    await p.emulateMedia({ media: 'screen' });
    out.push(r);
  }
  await b.close();
  console.log(JSON.stringify(out));
})();
