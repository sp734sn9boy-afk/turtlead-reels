// 使い方: node build.js   （playwright-core と /usr/bin/google-chrome を使う）
// characters.js のドット絵 → SVG → HTML → PNG を書き出す。HTMLは src/html/ に残す。
'use strict';
const fs = require('fs'), path = require('path');
let chromium; try { ({ chromium } = require('playwright-core')); } catch { ({ chromium } = require('/opt/node-tools/node_modules/playwright-core')); }
const P = require('./pixel');
const { ROLES, build } = require('./characters');

const OUT = path.join(__dirname, '..');
const HTML = path.join(__dirname, 'html');
fs.mkdirSync(HTML, { recursive: true });
['single', 'poses', 'check'].forEach(d => fs.mkdirSync(path.join(OUT, d), { recursive: true }));
const LOGO = 'file://' + path.resolve(__dirname, '../../../googlemap_logo.png');

const FONTS = `<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&family=M+PLUS+Rounded+1c:wght@800&family=Outfit:wght@600;700&display=block" rel="stylesheet">`;
const BASE_CSS = `*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Noto Sans JP',sans-serif;font-feature-settings:"palt";color:#f2f6ff;overflow:hidden;
 background:radial-gradient(70% 90% at 50% 35%,#14245a 0%,#081024 60%,#04070f 100%)}
.hexbg{position:absolute;inset:0;opacity:.07;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='97' viewBox='0 0 56 97'%3E%3Cpath d='M28 0l28 16v32L28 64 0 48V16zM28 64v33' fill='none' stroke='%233CD6F0' stroke-width='2'/%3E%3C/svg%3E")}
.head{display:flex;align-items:center;gap:18px}
.head img{width:72px;height:72px;border-radius:16px}
.brand{font-family:'M PLUS Rounded 1c',sans-serif;font-weight:800;font-size:30px;color:#fff;letter-spacing:.02em}
.brand b{color:#3CD6F0}
h1{font-weight:900;line-height:1.1;letter-spacing:.02em}
h1 span{background:linear-gradient(90deg,#4fe3ff,#b9a6ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:#c9d4f0;font-weight:700}
.card{position:relative;display:flex;flex-direction:column;align-items:center;border-radius:28px;
 background:linear-gradient(180deg,rgba(60,214,240,.10),rgba(20,36,90,.35));border:2px solid rgba(60,214,240,.35)}
.card .floor{position:absolute;left:50%;transform:translateX(-50%);border-radius:50%;background:rgba(60,214,240,.18)}
.card svg{position:relative;image-rendering:pixelated}
.tag{display:flex;flex-direction:column;align-items:center;gap:4px}
.tag .ja{font-weight:900;color:#fff;white-space:nowrap}
.tag .en{font-family:'Outfit',sans-serif;font-weight:700;letter-spacing:.18em;padding:2px 14px;border-radius:999px;color:#081024}
.tag .job{color:#c9d4f0;font-weight:500;white-space:nowrap}`;

const svg = (role, pose, scale) => P.toSVG(build(role, pose), { scale });
const page = (w, h, css, body, title) => `<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>${title}</title>${FONTS}
<style>${BASE_CSS}\nhtml,body{width:${w}px;height:${h}px}\n${css}</style></head><body><div class="hexbg"></div>${body}</body></html>`;
const card = (r, scale, cls = '') => `<div class="card ${cls}" style="--a:${r.accent}">${'<div class="floor"></div>'}${svg(r, 'stand', scale)}
<div class="tag"><div class="ja">${r.ja}</div><div class="en" style="background:${r.accent}">${r.en}</div><div class="job">${r.job}</div></div></div>`;
const header = (titleSize, subSize) => `<div class="head"><img src="${LOGO}" alt=""><div class="brand">turtle <b>ad</b></div></div>
<h1 style="font-size:${titleSize}px">タートルアドの <span>AI社員</span></h1>
<p class="sub" style="font-size:${subSize}px">ロゴの六角形＝亀の甲羅から生まれた、6人のチーム</p>`;

// ---- 1. 一覧（横 1920x1080）----
const wide = page(1920, 1080, `
.wrap{position:absolute;inset:0;padding:0 80px 30px;display:flex;flex-direction:column;justify-content:center}
.top{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:34px}
.top .t{display:flex;flex-direction:column;gap:10px}
.grid{display:grid;grid-template-columns:repeat(6,1fr);gap:22px}
.card{padding:34px 0 34px}
.card .floor{top:270px;width:190px;height:26px}
.card svg{margin-bottom:22px}
.points{margin-top:40px;display:flex;gap:22px;justify-content:center}
.points div{font-size:24px;font-weight:700;color:#e6eeff;padding:14px 30px;border-radius:999px;background:rgba(60,214,240,.10);border:2px solid rgba(60,214,240,.4)}
.points b{color:#4fe3ff}
.tag .ja{font-size:32px}.tag .en{font-size:18px;margin:4px 0 8px}.tag .job{font-size:17px;white-space:normal;text-align:center;padding:0 16px;line-height:1.45}
.note{position:absolute;right:80px;bottom:40px;color:#7f8fb8;font-size:18px}`,
  `<div class="wrap"><div class="top"><div class="t">${header(64, 26)}</div></div>
<div class="grid">${ROLES.map(r => card(r, 4)).join('')}</div>
<div class="points"><div><b>胸の六角形</b>＝ロゴ（亀の甲羅）</div><div><b>アンテナの先</b>＝担当の色</div><div><b>小物</b>で役わりがひと目でわかる</div></div></div>
<div class="note">キャラクターデザイン案（2026-11）</div>`, 'AI社員 一覧');

// ---- 2. 一覧（縦 1080x1920・スマホ用）----
const tall = page(1080, 1920, `
.wrap{position:absolute;inset:0;padding:80px 60px 0;display:flex;flex-direction:column;align-items:center;text-align:center}
.wrap h1{margin:26px 0 14px}
.grid{margin-top:50px;display:grid;grid-template-columns:repeat(2,1fr);gap:28px;width:100%}
.card{padding:16px 0 26px}
.card .floor{top:312px;width:220px;height:30px}
.card svg{margin-bottom:6px}
.tag .ja{font-size:42px}.tag .en{font-size:20px}`,
  `<div class="wrap">${header(84, 32)}<div class="grid">${ROLES.map(r => card(r, 5).replace(/<div class="job">.*?<\/div>/, '')).join('')}</div></div>`, 'AI社員 一覧（縦）');

// ---- 3. ポーズ見本（リーダーで3ポーズ）----
const POSES = [['type', '待機', 'パソコンを打つ'], ['work', '仕事中', 'パソコンが光り、目がキラッ'], ['talk', '話す', '手を上げて吹き出し']];
const poses = page(1920, 1080, `
.wrap{position:absolute;inset:0;padding:0 80px 20px;display:flex;flex-direction:column;justify-content:center}
.grid{margin-top:40px;display:grid;grid-template-columns:repeat(3,1fr);gap:36px}
.card{padding:20px 0 34px}.card .floor{top:438px;width:300px;height:34px}
.tag .ja{font-size:40px}.tag .job{font-size:22px}`,
  `<div class="wrap"><div class="head"><img src="${LOGO}" alt=""><div class="brand">turtle <b>ad</b></div></div>
<h1 style="font-size:56px;margin-top:18px">AI社員の <span>ポーズ見本</span>（リーダー）</h1>
<div class="grid">${POSES.map(([p, ja, d]) => `<div class="card"><div class="floor"></div>${svg(ROLES[0], p, 7)}<div class="tag"><div class="ja">${ja}</div><div class="job">${d}</div></div></div>`).join('')}</div></div>`, 'AI社員 ポーズ見本');

// ---- 4. 小さく表示したときの確認（64px・48px・32px、暗い背景と白い背景）----
const sizes = [[1, 64], [.75, 48], [.5, 32]];
const small = page(1200, 520, `
body{background:#081024}.row{display:flex;gap:28px;align-items:flex-end;padding:20px 40px}
.row.w{background:#ffffff}.row svg{image-rendering:pixelated}.lbl{width:90px;font-size:18px;color:#9fb0d8}.row.w .lbl{color:#445}`,
  sizes.map(([s, px]) => ['', 'w'].map(c => `<div class="row ${c}"><div class="lbl">${px}px</div>${ROLES.map(r => P.toSVG(build(r, 'stand'), { scale: s })).join('')}</div>`).join('')).join(''), '小さい表示の確認');

// 単体：64ドット×7px＝448px を 512px の中央に置く（まわり32pxの余白。動かすときに切れないように）
const single = (r, pose) => `<!doctype html><html><head><meta charset="utf-8"><style>*{margin:0}html,body{width:512px;height:512px;background:transparent}svg{position:absolute;left:32px;top:32px}</style></head><body>${svg(r, pose, 7)}</body></html>`;

(async () => {
  const files = { 'sheet_wide.html': wide, 'sheet_vertical.html': tall, 'poses.html': poses, 'check_small.html': small };
  for (const [f, h] of Object.entries(files)) fs.writeFileSync(path.join(HTML, f), h);
  for (const r of ROLES) fs.writeFileSync(path.join(OUT, 'single', `${r.id}.svg`), P.toSVG(build(r, 'stand'), { scale: 8 }));
  for (const [p] of POSES) fs.writeFileSync(path.join(OUT, 'poses', `leader_${p}.svg`), P.toSVG(build(ROLES[0], p), { scale: 8 }));

  const b = await chromium.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome' });
  const shot = async (html, w, h, out, transparent = false) => {
    const pg = await b.newPage({ viewport: { width: w, height: h } });
    const tmp = path.join(HTML, '_tmp.html');
    fs.writeFileSync(tmp, html);
    await pg.goto('file://' + tmp); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(300);
    // はみ出しチェック：ページより大きい要素・カードからはみ出す文字
    const over = await pg.evaluate(() => {
      const bad = [];
      document.querySelectorAll('.card').forEach(c => { const cr = c.getBoundingClientRect(); c.querySelectorAll('.ja,.en,.job').forEach(e => { const r = e.getBoundingClientRect(); if (r.left < cr.left || r.right > cr.right || r.bottom > cr.bottom) bad.push(e.textContent); }); if (cr.bottom > innerHeight || cr.right > innerWidth) bad.push('card out of page'); });
      return bad;
    });
    if (over.length) console.log('はみ出し', out, over);
    await pg.screenshot({ path: out, omitBackground: transparent }); await pg.close(); fs.unlinkSync(tmp);
    console.log('ok', path.relative(OUT, out));
  };
  await shot(wide, 1920, 1080, path.join(OUT, 'ai_staff_sheet_1920x1080.png'));
  await shot(tall, 1080, 1920, path.join(OUT, 'ai_staff_sheet_vertical_1080x1920.png'));
  await shot(poses, 1920, 1080, path.join(OUT, 'poses', 'leader_poses_sheet_1920x1080.png'));
  await shot(small, 1200, 520, path.join(OUT, 'check', 'check_small_sizes.png'));
  for (const r of ROLES) await shot(single(r, 'stand'), 512, 512, path.join(OUT, 'single', `${r.id}.png`), true);
  for (const [p] of POSES) await shot(single(ROLES[0], p), 512, 512, path.join(OUT, 'poses', `leader_${p}.png`), true);
  await b.close();
})();
