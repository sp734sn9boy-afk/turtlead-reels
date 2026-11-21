// 架空のお店「ムーンテイル」（MOONTAIL BAKERY）のロゴアニメ（5秒）。logoSVG(t) で t秒時点のコマを返す。
// 素材はすべて自作（図形と文字のみ）。他社ロゴ・写真は不使用。
let _uid = 0;
const cl = (x) => Math.max(0, Math.min(1, x));
const easeOut = (x) => 1 - Math.pow(1 - cl(x), 3);
const back = (x) => { x = cl(x); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
function logoSVG(t, o = {}) {
  const id = 'm' + (_uid++);
  const bg = o.bg === undefined ? (o.mono ? '#FFFFFF' : '#14235A') : o.bg;
  const brown = o.mono ? '#8a8a8a' : '#FFFFFF', gold = o.mono ? '#b5b5b5' : '#FFC81E', red = o.mono ? '#9a9a9a' : '#FF5A36';
  const C = 2 * Math.PI * 120;
  const ring = easeOut(t / 1.0);
  const cs = back((t - 0.8) / 0.7), cr = -120 * (1 - easeOut((t - 0.8) / 0.7));
  const pulse = 1 + 0.05 * Math.sin(Math.PI * cl((t - 3.6) / 0.5));
  const chars = ['ム', 'ー', 'ン', 'テ', 'イ', 'ル'];
  let txt = '';
  chars.forEach((c, i) => {
    const p = (t - (1.5 + 0.15 * i)) / 0.45;
    if (p <= 0) return;
    const y = 532 + 70 * (1 - back(p));
    txt += `<text x="${640 + (i - 2.5) * 90}" y="${y}" text-anchor="middle" font-family="'Zen Maru Gothic'" font-weight="900" font-size="86" fill="${brown}" opacity="${cl(p * 2.5)}">${c}</text>`;
  });
  const bp = easeOut((t - 2.6) / 0.7);
  const ls = 6 + 30 * (1 - bp);
  const lp = easeOut((t - 3.0) / 0.5);
  const sp = back((t - 3.4) / 0.5), sr = 90 * (1 - easeOut((t - 3.4) / 0.6));
  const star = (cx, cy, r) => `M${cx} ${cy - r} Q${cx} ${cy} ${cx + r} ${cy} Q${cx} ${cy} ${cx} ${cy + r} Q${cx} ${cy} ${cx - r} ${cy} Q${cx} ${cy} ${cx} ${cy - r}Z`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${o.vb || "0 0 1280 720"}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
  ${bg ? `<rect width="1280" height="720" fill="${bg}"/>` : ''}
  <defs><mask id="${id}"><rect width="1280" height="720" fill="#fff"/><circle cx="672" cy="246" r="62" fill="#000"/></mask></defs>
  <g transform="translate(640 360) scale(${pulse}) translate(-640 -360)">
    <circle cx="640" cy="262" r="120" fill="none" stroke="${brown}" stroke-width="18" stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - ring)}" transform="rotate(-90 640 262)"/>
    ${t > 0.8 ? `<g transform="translate(640 262) rotate(${cr}) scale(${cs}) translate(-640 -262)"><circle cx="640" cy="262" r="80" fill="${gold}" mask="url(#${id})"/></g>` : ''}
    ${t > 3.4 ? `<g transform="translate(772 150) rotate(${sr}) scale(${sp}) translate(-772 -150)"><path d="${star(772, 150, 38)}" fill="${red}"/></g><g transform="translate(826 214) scale(${sp}) translate(-826 -214)"><path d="${star(826, 214, 17)}" fill="${gold}"/></g>` : ''}
    ${txt}
    ${t > 2.6 ? `<text x="${640 + ls / 2}" y="632" text-anchor="middle" font-family="'Zen Maru Gothic'" font-weight="900" font-size="32" letter-spacing="${ls}" fill="${gold}" opacity="${bp}">MOONTAIL BAKERY</text>` : ''}
    ${t > 3.0 ? `<path d="M408 620 h${-70 * lp} M872 620 h${70 * lp}" stroke="${gold}" stroke-width="7" stroke-linecap="round"/>` : ''}
  </g></svg>`;
}
