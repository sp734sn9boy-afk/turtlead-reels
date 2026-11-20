// タートルアド AI社員 キャラクター：ドット絵エンジン（64x64格子）
// 自作。外部素材なし。ロゴ（六角形＝亀の甲羅、ノードと線）をもとに描く。
'use strict';
const W = 64, H = 64;
const OUT = '#060b18'; // 輪郭線（ブランドの最暗色に近い紺黒）

class Grid {
  constructor() { this.px = new Array(W * H).fill(null); }
  get(x, y) { return (x < 0 || y < 0 || x >= W || y >= H) ? null : this.px[y * W + x]; }
  set(x, y, c) { if (x >= 0 && y >= 0 && x < W && y < H && c) this.px[y * W + x] = c; }
  // mask: [[x,y],...] / color: (x,y,box)=>色 / outline: 外側1pxの輪郭を先に塗る
  part(mask, color, { outline = true, outColor = OUT } = {}) {
    if (!mask.length) return;
    const key = new Set(mask.map(([x, y]) => y * W + x));
    if (outline) {
      for (const [x, y] of mask) for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const k = (y + dy) * W + (x + dx);
        if (!key.has(k)) this.set(x + dx, y + dy, outColor);
      }
    }
    const xs = mask.map(p => p[0]), ys = mask.map(p => p[1]);
    const box = { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
    box.w = box.x1 - box.x0 + 1; box.h = box.y1 - box.y0 + 1;
    for (const [x, y] of mask) this.set(x, y, typeof color === 'function' ? color(x, y, box, key) : color);
  }
  dot(pts, c) { for (const [x, y] of pts) this.set(x, y, c); }
}

// ---- 形（ピクセル中心で判定） ----
const all = f => { const r = []; for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (f(x + .5, y + .5)) r.push([x, y]); return r; };
const ellipse = (cx, cy, rx, ry) => all((x, y) => ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1);
const rect = (x0, y0, x1, y1) => { const r = []; for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) r.push([x, y]); return r; };
const roundRect = (x0, y0, x1, y1, rad) => all((x, y) => {
  if (x < x0 || x > x1 + 1 || y < y0 || y > y1 + 1) return false;
  const cx = Math.min(Math.max(x, x0 + rad), x1 + 1 - rad), cy = Math.min(Math.max(y, y0 + rad), y1 + 1 - rad);
  return (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad;
});
const polygon = pts => all((x, y) => {
  let inside = false;
  for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
    const [xi, yi] = pts[i], [xj, yj] = pts[j];
    if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
});
// とがった頂点が上の六角形（ロゴと同じ向き）
const hexPts = (cx, cy, r) => [0, 1, 2, 3, 4, 5].map(i => { const a = Math.PI / 180 * (-90 + 60 * i); return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
const hex = (cx, cy, r) => polygon(hexPts(cx, cy, r));
const line = (x0, y0, x1, y1) => { // ブレゼンハム
  const r = []; x0 = Math.round(x0); y0 = Math.round(y0); x1 = Math.round(x1); y1 = Math.round(y1);
  const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
  for (;;) { r.push([x0, y0]); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
  return r;
};
const thick = (pts, w = 2) => { const s = new Map(); for (const [x, y] of pts) for (let i = 0; i < w; i++) for (let j = 0; j < w; j++) s.set((y + j) * W + x + i, [x + i, y + j]); return [...s.values()]; };
const minus = (a, b) => { const k = new Set(b.map(([x, y]) => y * W + x)); return a.filter(([x, y]) => !k.has(y * W + x)); };
const union = (...ms) => { const s = new Map(); for (const m of ms) for (const [x, y] of m) s.set(y * W + x, [x, y]); return [...s.values()]; };

// 立体感：左が奥（側面）＝暗く、右上が明るい（少し右を向いている）
const shade = (light, base, dark, { side = .22, top = .3 } = {}) => (x, y, b) => {
  const u = (x - b.x0) / Math.max(1, b.w - 1), v = (y - b.y0) / Math.max(1, b.h - 1);
  if (u < side) return dark;
  if (v < top && u > .5) return light;
  return base;
};

// ---- SVG化（横に並んだ同じ色をまとめる） ----
function toSVG(g, { scale = 8, pad = 0 } = {}) {
  let s = '';
  for (let y = 0; y < H; y++) {
    let x = 0;
    while (x < W) {
      const c = g.get(x, y); if (!c) { x++; continue; }
      let n = 1; while (x + n < W && g.get(x + n, y) === c) n++;
      s += `<rect x="${x}" y="${y}" width="${n}" height="1" fill="${c}"/>`;
      x += n;
    }
  }
  const size = (W + pad * 2) * scale;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${-pad} ${-pad} ${W + pad * 2} ${H + pad * 2}" width="${size}" height="${size}" shape-rendering="crispEdges">${s}</svg>`;
}

module.exports = { W, H, OUT, Grid, ellipse, rect, roundRect, polygon, hex, hexPts, line, thick, minus, union, shade, toSVG };
