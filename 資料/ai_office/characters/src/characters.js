// タートルアド AI社員：6体の定義とポーズ
// 体は全員共通（ロゴの六角形＝亀の甲羅の胴体、画面の顔、アンテナ）。担当ごとに差し色と小物を変える。
'use strict';
const P = require('./pixel');
const { Grid, ellipse, rect, roundRect, hex, hexPts, line, thick, minus, union, shade, OUT } = P;

// ブランド色
const C = {
  navy: '#14245a', navy2: '#081024', navy3: '#04070f', cyan: '#3CD6F0', violet: '#b9a6ff',
  // 頭と手足（水色がかった金属）
  mLight: '#e6fff8', mBase: '#a2efdf', mMid: '#62cfbf', mDark: '#2b8d93',
  // 胸の甲羅（ロゴの中の濃い青緑）
  plate: '#0f3c46', plateDark: '#0a2a34', spoke: '#2bb4cf', rimLight: '#b4f5ff',
  white: '#ffffff', blush: '#ff9fc4',
};

// 担当（差し色は1体1色）
const ROLES = [
  { id: 'leader', ja: 'リーダー', en: 'LEADER', job: '全体の舵取り・担当へのふり分け', accent: '#ffcc4d', accentDark: '#c98a12', item: 'ヘッドセット・腕章' },
  { id: 'design', ja: 'デザイン担当', en: 'DESIGN', job: '画像・チラシ・見た目をそろえる', accent: '#ff8fd0', accentDark: '#c9479a', item: 'ベレー帽・ペン' },
  { id: 'sales', ja: '営業担当', en: 'SALES', job: '案件の見極め・見積もり', accent: '#ff5468', accentDark: '#b51f36', item: 'ネクタイ・名刺' },
  { id: 'listing', ja: '出品・発信担当', en: 'POST', job: '出品ページ・SNSの投稿', accent: '#5ee38f', accentDark: '#1f9a54', item: 'メガホン' },
  { id: 'automation', ja: '仕組み担当', en: 'SYSTEM', job: '自動化・ホームページ公開', accent: '#ff9a3d', accentDark: '#b85b0e', item: 'ヘルメット・スパナ・ケーブル' },
  { id: 'research', ja: '調べもの担当', en: 'RESEARCH', job: '調べて裏付けをとる', accent: '#b9a6ff', accentDark: '#6f58d6', item: '虫めがね・丸めがね' },
];

const dk = c => { // 少し暗く
  const n = parseInt(c.slice(1), 16), f = .62; const r = (n >> 16) * f, g = ((n >> 8) & 255) * f, b = (n & 255) * f;
  return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
};

// pose: 'stand' | 'type'（待機：パソコンを打つ） | 'work'（仕事中：画面が光る） | 'talk'（話す） | 'stretch'（席で伸び）
// opt.tap: 1|2 打つ手を1ドット上げる（キーを打つコマ） / opt.step: 1|2 片足を上げる（歩くコマ）
function build(role, pose = 'stand', opt = {}) {
  const g = new Grid();
  const A = role.accent, AD = role.accentDark;
  const atDesk = pose === 'type' || pose === 'work' || pose === 'stretch';
  const glow = pose === 'work';
  const metal = shade(C.mLight, C.mBase, C.mDark);

  // ---- 1. 背中の甲羅（胴より大きく、左右にはみ出す＝亀のシルエット）----
  const shellPts = hexPts(31, 43.5, 21.5).map(([x, y]) => [x, 43.5 + (y - 43.5) * .78]);
  g.part(P.polygon(shellPts), (x, y) => (x < 20 ? '#1a2f70' : '#20398a'));
  // 甲羅のふち（水色）と、甲羅の模様（六角形のすじ）
  g.dot(P.minus(P.polygon(shellPts), P.polygon(hexPts(31, 43.5, 19.8).map(([x, y]) => [x, 43.5 + (y - 43.5) * .78]))), '#3CD6F0');
  g.dot([[14, 38], [15, 38], [13, 46], [14, 46], [15, 54], [16, 54], [17, 31], [18, 31], [17, 32], [13, 39], [12, 45], [14, 53]], '#24407f');
  g.dot([[16, 39], [16, 40], [16, 41], [16, 42], [16, 43], [16, 44], [16, 45], [17, 46], [17, 47], [17, 48], [17, 49], [17, 50], [17, 51], [17, 52], [17, 53]], '#24407f');
  // しっぽ（左下に少し）
  if (!atDesk) g.part([[11, 56], [12, 56], [10, 57], [11, 57], [12, 57]], C.mMid);

  // ---- 2. 足（ずんぐり＋指）----
  if (!atDesk) {
    const f1 = opt.step === 1 ? 1.4 : 0, f2 = opt.step === 2 ? 1.4 : 0;
    g.part(ellipse(25, 59.6 - f1, 5.2, 3.4), metal); g.dot([[22, 62], [24, 62], [26, 62]].map(([x, y]) => [x, y - Math.round(f1)]), C.mDark);
    g.part(ellipse(41, 59.6 - f2, 5.2, 3.4), metal); g.dot([[39, 62], [41, 62], [43, 62]].map(([x, y]) => [x, y - Math.round(f2)]), C.mMid);
  }

  // ---- 3. 奥の腕（向かって左）：甲羅の下から出るヒレのような手 ----
  const armL = pose === 'stretch' ? union(ellipse(13, 31, 3.4, 4.2), ellipse(15.5, 38, 3, 4))
    : atDesk ? ellipse(19, 51 - (opt.tap === 1 ? 1 : 0), 4.2, 4) : ellipse(12.5, 47, 3.6, 5.6);
  g.part(armL, shade(C.mBase, C.mMid, C.mDark, { side: .45 }));

  // ---- 4. 胸の甲羅（ロゴの六角形）----
  const cx = 33, cy = 44, R = 15;
  g.part(hex(cx, cy, R), (x, y) => (x > cx + 2 && y < cy - 4) ? C.rimLight : C.cyan);
  g.part(hex(cx, cy, R - 2.2), (x, y) => x < cx - 7 ? C.plateDark : C.plate, { outline: false });
  // 内側の六角形・線・ノード（ロゴの模様）
  const ic = [cx + 1, cy], ir = 6.2;
  const inner = hexPts(ic[0], ic[1], ir), outer = hexPts(cx, cy, R - 2.6);
  for (let i = 0; i < 6; i++) g.dot(line(...inner[i], ...outer[i]), C.spoke);
  for (let i = 0; i < 6; i++) g.dot(line(...inner[i], ...inner[(i + 1) % 6]), C.cyan);
  const coreOn = glow ? C.white : C.cyan;
  g.dot(rect(ic[0] - 1, ic[1] - 1, ic[0] + 1, ic[1] + 1), coreOn);
  if (glow) g.dot([[ic[0], ic[1] - 2], [ic[0], ic[1] + 2], [ic[0] - 2, ic[1]], [ic[0] + 2, ic[1]]], C.cyan);
  for (const [x, y] of inner) g.dot(rect(Math.round(x) - 1, Math.round(y) - 1, Math.round(x), Math.round(y)), C.white);

  // ---- 5. 手前の腕（向かって右）----
  let armR;
  if (pose === 'stretch') armR = union(ellipse(51, 38, 3, 4), ellipse(53, 31, 3.4, 4.2));
  else if (atDesk) armR = ellipse(46, 51 - (opt.tap === 2 ? 1 : 0), 4.2, 4);
  else if (pose === 'talk') armR = union(ellipse(50.5, 39, 3.4, 4.5), ellipse(53, 32, 3.6, 3.8));
  else armR = ellipse(49.5, 45, 3.8, 6);
  g.part(armR, metal);

  // ---- 6. 頭 ----
  g.part(roundRect(15, 8, 44, 30, 10), C.mDark);                       // 頭の側面（奥行き）
  g.part(roundRect(18, 8, 47, 30, 10), shade(C.mLight, C.mBase, C.mMid, { side: .12, top: .25 }));
  // 頭のてっぺんに小さな甲羅模様（六角形の点）
  g.dot([[29, 10], [30, 10], [36, 10], [37, 10]], C.mLight);
  // 顔の画面
  const screen = roundRect(22, 13, 44, 26, 4);
  g.part(screen, glow ? '#0d2a52' : C.navy2, { outColor: '#1b3d7a' });
  g.dot([[24, 14], [25, 14], [23, 15]], glow ? '#2c5fa0' : '#1b2f63'); // 画面の反射

  // 目と口
  const eye = (x, y) => {
    if (pose === 'stretch') { // 気持ちよさそうな目（＾＾）
      g.dot([[x, y + 3], [x + 1, y + 2], [x + 2, y + 3]], C.cyan); return;
    }
    if (pose === 'type') { // 手元を見る（下向きの目）
      g.dot(rect(x, y + 2, x + 2, y + 3), C.cyan); return;
    }
    if (glow) { // 光る画面を見つめる（キラッとした目）
      g.dot(rect(x, y, x + 2, y + 4), C.cyan); g.dot([[x, y], [x + 1, y]], C.white); g.dot([[x + 2, y + 4]], C.white); return;
    }
    g.dot(rect(x, y, x + 2, y + 4), C.cyan); g.dot([[x, y]], C.white);
  };
  eye(28, 16); eye(37, 16);
  g.dot([[26, 22], [27, 22]], C.blush); g.dot([[41, 22], [42, 22]], C.blush);
  if (pose === 'talk') { g.dot(rect(33, 22, 36, 22), C.cyan); g.dot(rect(34, 23, 35, 23), C.cyan); g.dot([[34, 22], [35, 22]], C.blush); }
  else g.dot([[33, 22], [34, 23], [35, 23], [36, 22]], C.cyan);

  // ---- 7. アンテナ（先は担当の差し色の六角形）----
  g.part(rect(34, 4, 34, 7), C.mDark, { outline: true });
  g.part(hex(34.5, 2.6, 2.6), (x, y) => (x >= 35 && y <= 2) ? '#ffffff' : A);
  if (glow) g.dot([[30, 1], [39, 1], [31, 4], [38, 4]], A);

  // ---- 8. 担当の小物 ----
  if (ITEMS[role.id]) ITEMS[role.id](g, role, pose, { A, AD, armR }); // 知らない id は小物なし（オフィス用の係は別に描き足す）

  // ---- 9. 机とノートパソコン（待機・仕事中）----
  if (atDesk) laptop(g, glow);
  // ---- 10. 吹き出し（話す）----
  if (pose === 'talk' && !opt.noBubble) {
    g.part(union(roundRect(49, 2, 62, 11, 3), [[51, 12], [52, 12], [51, 13]]), '#ffffff');
    g.dot([[52, 7], [53, 7], [55, 7], [56, 7], [58, 7], [59, 7]], role.accentDark);
  }
  // ---- 11. 仕事中：画面の光が顔に当たる ----
  if (glow) {
    g.dot(rect(23, 25, 43, 25), 'rgba(60,214,240,0.55)');
    g.dot([[46, 26], [47, 25], [19, 26], [18, 25]], 'rgba(60,214,240,0.5)');
  }
  return g;
}

function laptop(g, glow) {
  // 机の天板
  g.part(rect(6, 57, 59, 59), (x, y) => y === 57 ? '#3a5aa8' : C.navy, { outColor: OUT });
  g.part(rect(9, 60, 11, 63), C.navy); g.part(rect(54, 60, 56, 63), C.navy);
  // パソコン（ふたの裏側がこちらを向く。ロゴの六角形入り）
  const lid = [[22, 43], [44, 43], [46, 56], [20, 56]];
  g.part(P.polygon(lid), (x, y) => x < 25 ? '#8aa0c8' : '#c3d2ec');
  g.part(hex(33, 49.5, 3.6), glow ? C.white : C.cyan, { outline: false });
  g.dot(hexPts(33, 49.5, 1.4).length ? [[33, 49], [33, 50]] : [], glow ? C.cyan : '#1b4e8a');
  g.part(rect(18, 56, 48, 56), '#7186b5', { outline: false });
  if (glow) {
    // ふたのふちから漏れる光と、きらめき
    const L = 'rgba(60,214,240,0.55)';
    g.dot(line(21, 42, 45, 42), '#c8f8ff'); g.dot(line(19, 41, 47, 41), L);
    g.dot([[19, 44], [47, 44], [18, 47], [48, 47]], L);
    g.dot(P.polygon([[22, 43], [44, 43], [44.6, 46], [21.4, 46]]).filter(([x]) => x >= 25), '#e6fbff');
    const spark = (x, y, c) => g.dot([[x, y - 2], [x, y - 1], [x - 2, y], [x - 1, y], [x, y], [x + 1, y], [x + 2, y], [x, y + 1], [x, y + 2]], c);
    spark(10, 38, '#b9a6ff'); spark(55, 36, '#3CD6F0'); spark(8, 50, '#3CD6F0'); spark(58, 49, '#ffffff');
  }
}

// ---- 担当ごとの小物 ----
const ITEMS = {
  leader(g, role, pose, { A, AD }) {
    // ヘッドセット：頭の上を通るバンド＋耳当て＋マイク
    g.part(union(thick(line(16, 13, 20, 7), 2), thick(line(20, 6, 41, 6), 2), thick(line(41, 6, 46, 11), 2)), '#33405e');
    g.part(roundRect(44, 13, 49, 22, 2), (x, y) => y < 15 ? '#ffe39a' : A); // 手前の耳当て
    g.part(roundRect(13, 14, 16, 22, 2), AD);                             // 奥の耳当て
    if (pose !== 'type' && pose !== 'work') {
      g.part(union(thick(line(45, 22, 42, 27), 1), [[41, 27], [40, 27]]), '#33405e', { outline: false });
      g.part(roundRect(37, 26, 40, 28, 1), A);                            // マイク
    } else {
      g.part(thick(line(45, 22, 43, 27), 1), '#33405e', { outline: false });
      g.part(roundRect(40, 26, 43, 28, 1), A);
    }
    // 腕章（奥の腕に金の帯）＋胸の星バッジ
    if (pose === 'stand' || pose === 'talk') {
      g.dot(rect(9, 45, 16, 46), A); g.dot([[9, 46], [16, 46]], AD);
    }
    star(g, 23, 34, A, AD);
  },
  design(g, role, pose, { A, AD }) {
    // ベレー帽（ななめにかぶる）
    g.part(ellipse(30, 9, 13, 4.8), (x, y) => y <= 6 && x > 30 ? '#ffc4e6' : (x < 22 ? AD : A));
    g.part(rect(31, 3, 32, 4), AD);
    // ペン（手前の手で持つ、大きめ）
    if (pose === 'stand' || pose === 'talk') {
      const pen = thick(line(50, 52, 59, 30), 3);
      g.part(pen, (x, y) => y < 35 ? A : (y > 48 ? '#ffffff' : '#ffe4f3'));
      g.part(polyTip(49, 52), '#33405e', { outline: false });
      g.dot(rect(47, 43, 52, 47), C.mBase); g.dot([[52, 43], [52, 47]], C.mDark);
    }
    // 胸に小さなパレット色
    g.dot([[22, 36], [23, 36]], A); g.dot([[22, 37], [23, 37]], C.cyan);
  },
  sales(g, role, pose, { A, AD }) {
    // ネクタイ（胸の甲羅の上）
    g.part(union(rect(32, 31, 35, 33), P.polygon([[32, 34], [36, 34], [37.5, 46], [34, 50], [30.5, 46]])),
      (x, y) => y <= 33 ? AD : (x < 33 ? AD : A));
    g.dot([[33, 37], [34, 39], [35, 41], [33, 43]], '#ff97a3');
    // 名刺（手前の手で持ち上げる）
    if (pose === 'stand' || pose === 'talk') {
      g.part(rect(49, 34, 60, 41), '#ffffff');
      g.dot(rect(51, 36, 54, 36), A); g.dot(rect(51, 38, 58, 38), '#9aa7c7'); g.dot(rect(51, 40, 56, 40), '#9aa7c7');
      g.dot(hexPts(57.5, 36.2, 1).map(p => [Math.round(p[0]), Math.round(p[1])]), C.cyan);
      g.part(ellipse(50, 42, 3.4, 3.4), shade(C.mLight, C.mBase, C.mDark));
    }
  },
  listing(g, role, pose, { A, AD }) {
    // メガホン（手前の手で前に向ける）
    if (pose === 'stand' || pose === 'talk') {
      const cone = P.polygon([[47, 36], [60, 29], [60, 45], [47, 40]]);
      g.part(cone, (x, y) => x > 57 ? '#c9ffe0' : (y < 36 ? '#a6f5c6' : A));
      g.part(rect(44, 36, 47, 40), AD);
      g.part(rect(48, 41, 50, 47), '#33405e');
      // 音の線
      g.dot([[62, 32], [63, 31], [62, 42], [63, 43], [62, 37], [63, 37]], A);
    }
    // 胸にスマホ（ポケットから少し出る）
    g.part(roundRect(20, 34, 24, 41, 1), '#33405e');
    g.dot(rect(21, 35, 23, 39), A); g.dot([[22, 40]], '#9aa7c7');
  },
  automation(g, role, pose, { A, AD }) {
    // 安全ヘルメット
    g.part(union(ellipse(31.5, 11, 13.5, 8).filter(([x, y]) => y <= 11), rect(14, 11, 49, 12)),
      (x, y) => y >= 11 ? AD : (x > 33 && y < 7 ? '#ffd2a3' : A));
    g.dot([[31, 4], [31, 5], [31, 6], [31, 7], [31, 8], [31, 9], [31, 10]], AD);
    g.part(rect(34, 1, 34, 3), C.mDark, { outline: false });
    // スパナ（手前の手）
    if (pose === 'stand' || pose === 'talk') {
      g.part(thick(line(50, 48, 57, 33), 3), '#b8c4dc');
      g.part(minus(ellipse(58.5, 30.5, 4, 4), union(rect(57, 26, 60, 30))), '#b8c4dc');
      g.dot(thick(line(51, 46, 53, 42), 3), A);
    }
    // ケーブル（甲羅の横から出て、足元でプラグ）
    g.part(union(line(19, 50, 13, 54), line(13, 54, 10, 58), line(10, 58, 11, 61)), A, { outline: true });
    g.part(rect(10, 61, 13, 63), '#33405e');
    g.dot([[11, 63]], '#b8c4dc');
  },
  research(g, role, pose, { A, AD }) {
    // 丸めがね（顔の画面の上）
    for (const ex of [29, 38]) g.dot(ellipseRing(ex, 18.2, 3.6, 3.8), A);
    g.dot([[33, 18], [34, 18]], A);
    // 虫めがね（手前の手で持ち上げる）
    if (pose === 'stand' || pose === 'talk') {
      g.part(thick(line(50, 50, 52, 41), 3), AD);
      g.part(ellipse(55.5, 34, 7, 7), A);
      g.part(ellipse(55.5, 34, 5, 5), (x, y) => (x - y > 19 && x - y < 23) ? '#ffffff' : 'rgba(210,240,255,0.55)', { outline: false });
    }
    // 胸にメモ
    g.part(rect(20, 35, 24, 40), '#ffffff'); g.dot([[21, 37], [22, 37], [23, 37], [21, 39], [22, 39]], A);
  },
};

function star(g, x, y, c, cd) {
  g.dot([[x, y - 1], [x - 1, y], [x, y], [x + 1, y], [x, y + 1]], c);
}
function polyTip(x, y) { return [[x, y], [x + 1, y], [x, y + 1], [x - 1, y + 2]]; }
function ellipseRing(cx, cy, rx, ry) {
  const a = ellipse(cx, cy, rx, ry), b = ellipse(cx, cy, rx - 1, ry - 1); return minus(a, b);
}

module.exports = { ROLES, C, build, laptop };
