// shared helpers for every subway page
const NS = 'http://www.w3.org/2000/svg';
const WHITE = '#f5f4ef', INK = '#0d0d0e', DIM = '#a3a39d';
const el = (n, a = {}, p) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); (p || document.querySelector('svg')).appendChild(e); return e; };
const Q = new URLSearchParams(location.search);
const fmtN = n => Number(n).toLocaleString('en-US');
const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const io = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const oq = t => 1 - Math.pow(1 - t, 4);
const back = t => { const c = 2.2; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
// line colours come from colors.js (the colouring guide): pinned keys keep theirs, a new key hashes into its tier's spare list
const P = window.PALETTE;
function colourOf(key, tier, taken) {
  for (const t of ['now', 'side', 'work']) if (P[t].pinned[key]) return P[t].pinned[key];
  const spare = P[tier || 'side'].spare; let h = 2166136261; for (const c of key) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); }
  let i = (h >>> 0) % spare.length;
  if (taken) for (let n = 0; n < spare.length && taken.has(spare[i]); n++) i = (i + 1) % spare.length;
  return spare[i];
}
// building now = a line whose lane opens its film (link "film", or an old-style "#anchor")
const isNow = l => l.link === 'film' || (l.link || '').startsWith('#');
// one colour per known key. keys are visited in sorted order so the result never depends on what is on the map today
function colours(lines) { const D = window.DATA || {}, taken = new Set(), out = {}, tier = {};
  for (const l of (D.lines || lines || [])) tier[l.key] = isNow(l) ? 'now' : 'side';
  const keys = D.names ? Object.keys(D.names) : (lines || []).map(l => l.key);
  for (const k of [...keys].sort()) { out[k] = colourOf(k, tier[k], taken); taken.add(out[k]); }
  for (const k in P.work.pinned) out[k] = P.work.pinned[k];
  return out; }
function rounded(pts, r = 24) {                       // polyline with arcs at the bends
  let s = `M${pts[0].x} ${pts[0].y}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const p = pts[i], a = pts[i - 1], b = pts[i + 1];
    const la = Math.hypot(a.x - p.x, a.y - p.y), lb = Math.hypot(b.x - p.x, b.y - p.y), q = Math.min(r, la / 2, lb / 2);
    if (la < .01 || lb < .01) continue;
    s += ` L${p.x + (a.x - p.x) / la * q} ${p.y + (a.y - p.y) / la * q} Q${p.x} ${p.y} ${p.x + (b.x - p.x) / lb * q} ${p.y + (b.y - p.y) / lb * q}`;
  }
  const e = pts[pts.length - 1]; return s + ` L${e.x} ${e.y}`;
}
// THE ROUTE: one line runs down the left of the whole page. Measured in Chromium at an 830 px README, a summary image starts
// 16.94 px in (the disclosure triangle), lanes are 94% wide and signs 95%, the map and the last-stop sign 100% with no triangle.
// These stage x values (out of 1200) put the line at the same screen x, 36.4 px, in all of them.
const ROUTE = { lane: 30, sign: 29.7, full: 52.7 };
// an interchange on the route: white disc, ink ring, white core
function interchange(p, x, y, r = 19) { el('circle', { cx: x, cy: y, r, fill: WHITE }, p); el('circle', { cx: x, cy: y, r: r * .66, fill: INK }, p); el('circle', { cx: x, cy: y, r: r * .34, fill: WHITE }, p); }
// show the stretch [lo, hi] (px) of a path
function span(e, lo, hi, len) { const v = Math.max(0, hi - lo); e.style.opacity = v > .5 ? 1 : 0; e.setAttribute('stroke-dasharray', `${Math.max(.01, v)} ${len + 99}`); e.setAttribute('stroke-dashoffset', -lo); }
// the line bullet: a disc, or a diamond for the express (vel)
function bullet(p, x, y, r, key, colour) {
  return key === 'vel' ? el('rect', { x: x - r * .86, y: y - r * .86, width: r * 1.72, height: r * 1.72, fill: colour, transform: `rotate(45 ${x} ${y})` }, p)
                       : el('circle', { cx: x, cy: y, r, fill: colour }, p);
}
// arrow in a white disc, as on the signs. dir in degrees, 0 = up
function arrowDisc(p, x, y, r, dir) { const g = el('g', { transform: `translate(${x} ${y}) rotate(${dir}) scale(${r / 33})` }, p);
  el('circle', { r: 33, fill: WHITE }, g); el('path', { d: 'M0 19 V-17 M-15 -3 L0 -18 L15 -3', fill: 'none', stroke: INK, 'stroke-width': 8 }, g); return g; }
