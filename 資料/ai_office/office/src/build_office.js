// 使い方: node build_office.js
// キャラのドット絵エンジン（../../characters/src/pixel.js・characters.js）と office_template.html を
// 1つのHTMLにまとめて ../ai_office.html に書き出す（外部読み込みは Google Fonts だけ）。
'use strict';
const fs = require('fs'), path = require('path');
const SRC = path.join(__dirname, '../../characters/src');
const pixel = fs.readFileSync(path.join(SRC, 'pixel.js'), 'utf8').replace(/module\.exports\s*=/, 'return');
const chars = fs.readFileSync(path.join(SRC, 'characters.js'), 'utf8')
  .replace(/const P = require\('\.\/pixel'\);/, '').replace(/module\.exports\s*=/, 'return');
const engine = `// ---- ドット絵エンジン（資料/ai_office/characters/src から自動で取り込み）----\nconst P = (function () {\n${pixel}\n})();\nconst CH = (function (P) {\n${chars}\n})(P);`;
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, 'logo_96.png')).toString('base64');
let html = fs.readFileSync(path.join(__dirname, 'office_template.html'), 'utf8');
html = html.replace('/*__ENGINE__*/', () => engine).replace('__LOGO__', logo);
const out = path.join(__dirname, '..', 'ai_office.html');
fs.writeFileSync(out, html);
console.log('ok', out, (html.length / 1024).toFixed(1) + 'KB');
