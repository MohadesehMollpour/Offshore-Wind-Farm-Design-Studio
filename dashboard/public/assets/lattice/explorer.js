

// Author: Koorosh Aslansefat
/* Trace map geometry: where each supplier goes, a UK projection, pin grouping and HQ edge anchors.
   Pure functions, no DOM, so node can test them. Same export pattern as core.js. */
(function (root) {
  const FRAME = [-11, 49.8, 6, 61];          // lon0, lat0, lon1, lat1
  const UK_CENTRE = [54.5, -3.0];            // lat, lon
  const RAD = Math.PI / 180, EARTH_KM = 6371;
  // Approximate cluster regions (the directory publishes no boundaries): centre lat, lon, radius km,
  // then a label point over the sea and its text anchor. Starting values; tune in the browser.
  const CLUSTER_GEO = {
    'North Scotland': [57.6, -3.6, 160, 59.45, -5.6, 'middle'],
    'Forth & Tay': [56.25, -3.1, 60, 56.35, -1.7, 'start'],
    'North East': [54.85, -1.55, 55, 55.15, -0.9, 'start'],
    'Humber': [53.65, -0.35, 55, 53.95, 0.55, 'start'],
    'East Anglia': [52.55, 1.35, 65, 52.95, 2.2, 'start'],
    'Solent': [50.8, -1.25, 45, 50.35, -1.3, 'middle'],
    'Celtic Sea': [51.6, -4.6, 110, 50.9, -6.3, 'middle'],
  };
  const COUNTRY_CENTROID = {
    'United Kingdom': [54.5, -3.0], Norway: [60.5, 8.5], Netherlands: [52.2, 5.3], France: [46.6, 2.4],
    Canada: [56.1, -106.3], Germany: [51.2, 10.4], 'United States of America': [39.8, -98.6], Denmark: [56.0, 9.5],
    China: [35.9, 104.2], Slovenia: [46.1, 14.8], Belgium: [50.6, 4.6], Australia: [-25.3, 133.8],
    'United Arab Emirates': [23.4, 53.8], Ireland: [53.4, -8.0], Italy: [42.8, 12.6], Thailand: [15.9, 100.9],
    Spain: [40.2, -3.6], Sweden: [62.0, 15.0],
  };

  const isNational = (clusters, nClusters) => nClusters > 0 && new Set(clusters).size >= nClusters;

  function sitesBy(KG) {
    const out = KG.suppliers.map(() => []);
    KG.sites.forEach(s => { if (out[s[0]]) out[s[0]].push(s); });
    return out;
  }

  // Pin at the HQ site town if it resolves, else the first resolved site; or the reason it can't be placed.
  function place(si, KG, GEO, sites) {
    const rows = sites[si] || [], at = r => r[1] && GEO.places[r[1]];
    const ok = rows.filter(at);
    const pt = r => { const [lat, lon, approx] = GEO.places[r[1]]; return { town: r[1], lat, lon, approx: !!approx }; };
    if (ok.length) {
      const main = ok.find(r => r[2]) || ok[0], seen = new Set([main[1]]), others = [];
      ok.forEach(r => { if (!seen.has(r[1])) { seen.add(r[1]); others.push(pt(r)); } });
      return { pin: { ...pt(main), hqSite: !!main[2] }, others };
    }
    const abroad = rows.find(r => (GEO.abroad || []).includes(r[1]));
    if (abroad) return { off: `site outside the UK and Ireland (${abroad[1]})` };
    const lost = rows.find(r => r[1]);
    if (lost) return { off: `town not found (${lost[1]})` };
    const cl = KG.suppliers[si][5];
    if (cl.length && !isNational(cl, KG.clusters.length)) return { off: `named only by cluster (${cl.map(c => KG.clusters[c]).join(', ')})` };
    return { off: 'no site town' };
  }

  // Spherical transverse Mercator, central meridian lon0 (radians out; close to the British National Grid).
  function tm(lon, lat, lon0 = -2) {
    const l = (lon - lon0) * RAD, p = lat * RAD, b = Math.cos(p) * Math.sin(l);
    return [0.5 * Math.log((1 + b) / (1 - b)), Math.atan2(Math.tan(p), Math.cos(l))];
  }

  // Fit FRAME to a viewBox `width` wide, leaving `top` units free above the map for the component card.
  function makeProjection(width, opts = {}) {
    const pad = opts.pad ?? 10, top = opts.top ?? 0, [x0, y0, x1, y1] = opts.frame || FRAME, pts = [];
    for (let i = 0; i <= 10; i++) {
      const lon = x0 + (x1 - x0) * i / 10, lat = y0 + (y1 - y0) * i / 10;
      pts.push(tm(lon, y0), tm(lon, y1), tm(x0, lat), tm(x1, lat));
    }
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const k = (width - 2 * pad) / (maxX - minX);
    return {
      width, height: Math.round(top + (maxY - minY) * k + 2 * pad), unitsPerKm: k / EARTH_KM,
      project: (lon, lat) => { const [x, y] = tm(lon, lat); return [pad + (x - minX) * k, top + pad + (maxY - y) * k]; },
    };
  }

  // Greedy grouping: the point with the most ungrouped neighbours within r seeds the next group.
  function groupPins(pts, r) {
    const left = new Set(pts.map((_, i) => i)), out = [];
    const near = i => [...left].filter(j => Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y) <= r);
    while (left.size) {
      let best = [];
      for (const i of left) { const n = near(i); if (n.length > best.length) best = n; }
      best.forEach(j => left.delete(j));
      const mean = f => best.reduce((a, j) => a + pts[j][f], 0) / best.length;
      out.push({ x: mean('x'), y: mean('y'), ids: best.map(j => pts[j].id) });
    }
    return out;
  }

  const fanPositions = (x, y, n, radius = 26) => Array.from({ length: n }, (_, i) => {
    const a = -Math.PI / 2 + 2 * Math.PI * i / n;
    return [x + radius * Math.cos(a), y + radius * Math.sin(a)];
  });

  // Initial great-circle bearing in degrees, 0 = north, clockwise.
  function bearing(lat1, lon1, lat2, lon2) {
    const p1 = lat1 * RAD, p2 = lat2 * RAD, dl = (lon2 - lon1) * RAD;
    const y = Math.sin(dl) * Math.cos(p2), x = Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl);
    return (Math.atan2(y, x) / RAD + 360) % 360;
  }

  // Where a ray from (cx, cy) heading `deg` (0 = up, clockwise) leaves the rectangle [x0, y0, x1, y1].
  function edgeAnchor(cx, cy, deg, rect) {
    const [x0, y0, x1, y1] = rect, dx = Math.sin(deg * RAD), dy = -Math.cos(deg * RAD), ts = [];
    if (dx > 1e-9) ts.push([(x1 - cx) / dx, 'e']);
    if (dx < -1e-9) ts.push([(x0 - cx) / dx, 'w']);
    if (dy > 1e-9) ts.push([(y1 - cy) / dy, 's']);
    if (dy < -1e-9) ts.push([(y0 - cy) / dy, 'n']);
    const [t, side] = ts.sort((a, b) => a[0] - b[0])[0];
    return { x: cx + dx * t, y: cy + dy * t, side };
  }

  // Short country names for HQ chips on narrow maps.
  const COUNTRY_SHORT = { 'United States of America': 'USA', 'United Arab Emirates': 'UAE', Netherlands: 'NL' };
  const chipWidth = label => 16 + label.length * 6.6;      // 11px mono text plus padding

  // HQ chips as rectangles that overlap neither each other nor the `avoid` rectangles (pins, bubbles):
  // each starts at its edge anchor and slides along that edge until it fits; if nothing fits it keeps its anchor.
  // chips: [{side, x, y, w, h}] with x, y the anchor; rect and avoid entries: [x0, y0, x1, y1].
  // Returns [{x, y, w, h}] (top-left corners) in the same order.
  function layoutChips(chips, rect, avoid = []) {
    const [X0, Y0, X1, Y1] = rect, placed = [];
    const fit = (x, y, w, h) => [Math.max(X0, Math.min(X1 - w, x)), Math.max(Y0, Math.min(Y1 - h, y))];
    const clash = (x, y, w, h) => placed.map(p => [p.x, p.y, p.x + p.w, p.y + p.h]).concat(avoid)
      .some(([a, b, c, d]) => x < c + 2 && x + w > a - 2 && y < d + 2 && y + h > b - 2);
    return chips.map(ch => {
      const { side, w, h } = ch, along = side === 'n' || side === 's' ? 'x' : 'y', step = along === 'x' ? 12 : h + 4;
      const [x, y] = fit(side === 'e' ? X1 - w : side === 'w' ? X0 : ch.x - w / 2, side === 'n' ? Y0 : side === 's' ? Y1 - h : ch.y - h / 2, w, h);
      let best = [x, y];
      for (let k = 0; k < 160; k++) {
        const d = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * step;   // 0, +step, -step, +2 step, ...
        const p = fit(along === 'x' ? x + d : x, along === 'y' ? y + d : y, w, h);
        if (!clash(p[0], p[1], w, h)) { best = p; break; }
      }
      const r = { x: best[0], y: best[1], w, h };
      placed.push(r);
      return r;
    });
  }

  const api = { FRAME, UK_CENTRE, CLUSTER_GEO, COUNTRY_CENTROID, COUNTRY_SHORT, isNational, sitesBy, place, tm, makeProjection,
    groupPins, fanPositions, bearing, edgeAnchor, chipWidth, layoutChips };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.GeoCore = api;
})(this);

// Author: Koorosh Aslansefat
/* Shared helpers, global state and the two detail renderers every view reuses. */
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fmt = n => Number(n).toLocaleString('en-GB');
const pct = (a, b) => b ? Math.round(a / b * 100) : 0;
const pill = b => `<span class="pill b-${b}">${b}</span>`;
const bandVar = b => `var(--${{ Severe: 'sev', High: 'high', Moderate: 'mod', Low: 'low' }[b]})`;
const bar = (v, b, max = 100) => `<div class="bar"><i class="c-${b}" style="width:${Math.max(2, Math.min(100, v / max * 100))}%"></i></div>`;
const gradeBadge = g => `<span class="pill grade-${g}">${LatticeCore.GRADE[g]}</span>`;
const idl = (kind, id, label) => `<span class="idl" data-go="${kind}:${esc(id)}" tabindex="0" role="link">${esc(label ?? id)}</span>`;
const ruleChips = r => ['R2', 'R4', 'R5'].filter(k => r[k]).map(k => `<span class="rule-chip" title="${esc(RULE_TXT[k])}">${k}</span>`).join('');

const KG = window.KG;
const G = LatticeCore.index(KG);
const CI = Object.fromEntries(KG.components.map((c, i) => [c[0], i]));
const SUBNAME = Object.fromEntries(KG.subsystems);
const SUBS = KG.subsystems.map(s => s[0]);
const subVar = sid => `var(--s-${sid})`;
const TURNOVER = ['<€2m', '€2–10m', '€10–50m', '>€50m'];  // the directory reports turnover in euros
const HEADCOUNT = ['<10', '11–49', '50–249', '>250'];
const TIERS = [[1, 'Tier 1'], [2, 'Tier 2'], [4, 'Tier 3'], [8, 'Professional services'], [16, 'O&M services'], [32, 'Digital services'], [64, 'Developer'], [128, 'Research']];
const tierTxt = t => TIERS.filter(([b]) => t & b).map(([, l]) => l).join(' · ') || 'Not stated';
const windTxt = w => [w & 2 && 'Fixed', w & 4 && 'Floating', w & 1 && 'Onshore'].filter(Boolean).join(' · ') || 'Not stated';
const applicTxt = a => a === 'both' ? 'fixed & floating' : a === 'fixed' ? 'fixed-bottom only' : 'floating only';
const RULE_TXT = {
  R1: 'Inferred link: found in the company description, confidence 0.6',
  R2: 'Thin supply: two or fewer explicit or declared directory suppliers',
  R3: 'Exposure rolls up component → subsystem → turbine',
  R4: 'Cluster concentration: 3+ suppliers and ≥ 60 % in one cluster',
  R5: 'Floating gap: under half the suppliers declare floating wind',
  R6: 'Alternate source: same component, outside the affected group',
};

/* supplier-count heat scale shared by the turbine (depth mode) and the heatmap */
const HEAT_BINS = [[1, 'h1', '1'], [2, 'h2', '2–3'], [4, 'h3', '4–6'], [7, 'h4', '7–12'], [13, 'h5', '13–20'], [21, 'h6', '21+']];
const heatStep = n => { let k = 0; HEAT_BINS.forEach(([t], i) => { if (n >= t) k = i + 1; }); return k; };
const heatVar = n => n ? `var(--${HEAT_BINS[heatStep(n) - 1][1]})` : 'var(--surface2)';
const heatInk = n => heatStep(n) >= 4 ? 'var(--h-ink-hi)' : 'var(--h-ink-lo)';
const heatLegend = () => `<div class="heatlegend"><span style="margin-right:6px">Suppliers</span><i style="background:var(--surface2);box-shadow:inset 0 0 0 1px var(--line)"></i><span style="margin:0 6px 0 2px">0</span>${HEAT_BINS.map(([, v, l]) => `<i style="background:var(--${v})"></i><span style="margin:0 6px 0 2px">${l}</span>`).join('')}</div>`;

const BASE = { fixed: LatticeCore.rollup(G, 'fixed'), floating: LatticeCore.rollup(G, 'floating') };
const COMP_EXP = BASE.fixed.comps; // component scores do not depend on variant; rollups do
const ranked = COMP_EXP.slice().sort((a, b) => b.score - a.score || b.n - a.n);
const STATE = {
  variant: 'fixed', fixedType: 'monopile', colorBy: 'band',
  comp: (ranked.find(e => !e.empty) || ranked[0]).ci,
  supplier: null, traceMode: 'diagram',
  scenario: { cluster: -1, overseas: false, micro: false, floatingOnly: false },
};
const VIEW_FNS = {};

/* tooltip */
const tipEl = () => document.getElementById('tip');
function showTip(e, html) {
  const t = tipEl(); if (!t) return;
  t.innerHTML = html; t.hidden = false;
  const r = t.getBoundingClientRect(), pad = 12;
  let x = e.clientX + pad, y = e.clientY + pad;
  if (x + r.width > innerWidth - 8) x = e.clientX - r.width - pad;
  if (y + r.height > innerHeight - 8) y = e.clientY - r.height - pad;
  t.style.left = Math.max(8, x) + 'px'; t.style.top = Math.max(8, y) + 'px';
}
function hideTip() { const t = tipEl(); if (t) t.hidden = true; }

function compPath(ci) {
  const c = KG.components[ci];
  const root = c[3] === 'both' ? 'TurbineSystem (fixed & floating)' : c[3] === 'fixed' ? 'TurbineSystem (fixed)' : 'TurbineSystem (floating)';
  return `<div class="trail"><span class="s">${root}</span><span class="r">hasPart</span><span class="s">${esc(SUBNAME[c[2]])}</span><span class="r">hasPart</span><span class="s">${esc(c[1])}</span></div>`;
}

function driverRows(e) {
  return LatticeCore.DRIVERS.map((d, i) => {
    const nd = e.noData[i];
    return `<div class="drv"><span>${d}</span>${nd ? '<span class="note">no data</span>' : bar(e.drivers[i], LatticeCore.bandOf(e.drivers[i]))}<span class="num">${nd ? '–' : e.drivers[i]}</span></div>`;
  }).join('');
}

function compDetail(ci, removed) {
  const e = LatticeCore.exposure(G, ci, removed);
  const c = KG.components[ci], total = G.compLinks[ci].length, gone = e.empty && total > 0;
  const live = i => G.compLinks[i].filter(l => !(removed && removed.has(l.si))).length;
  const fired = Object.entries(e.rules).filter(([, v]) => v).map(([k]) => `<div class="rule"><b>${k}</b>${RULE_TXT[k]}</div>`).join('');
  const sups = e.links.slice().sort((a, b) => a.g - b.g || G.S[a.si][0].localeCompare(G.S[b.si][0]))
    .map(l => `<li>${idl('s', l.si, G.S[l.si][0])} ${gradeBadge(l.g)}<div class="note">${esc(l.ev)}</div></li>`).join('');
  let alt = '';
  if (e.empty) {
    const sib = KG.components.map((x, i) => i).filter(i => i !== ci && KG.components[i][2] === c[2] && live(i))
      .sort((a, b) => live(b) - live(a)).slice(0, 3);
    alt = sib.length ? `<p class="note" style="margin-top:8px">Nearest evidenced capability in ${esc(SUBNAME[c[2]])}${removed && removed.size ? ' after this scenario' : ''}: ${sib.map(i => idl('c', KG.components[i][0], `${KG.components[i][1]} (${live(i)})`)).join(', ')}.</p>` : '';
  }
  return `<h3>${esc(c[1])}</h3>
    <div class="tag">${esc(SUBNAME[c[2]])} · ${applicTxt(c[3])} · exposure <b class="num">${e.score}</b> ${pill(e.band)}</div>
    ${compPath(ci)}
    <h2 style="margin-top:14px">Exposure drivers</h2>${driverRows(e)}${e.empty ? '<p class="note">Score fixed at 100 because no supplier remains; the other drivers are undefined.</p>' : ''}
    ${fired ? `<h2 style="margin-top:14px">Rules fired</h2>${fired}` : ''}
    <h2 style="margin-top:14px">Suppliers · ${e.links.length} (${e.nStrong} explicit or declared)</h2>
    ${e.empty ? `<div class="empty">${gone ? `All ${total} supplier${total === 1 ? ' is' : 's are'} removed by this scenario.` : 'No directory supplier evidenced in the directory for this component.'}</div>${alt}` : `<ul>${sups}</ul>`}`;
}

function supplierDetail(si) {
  const s = G.S[si];
  const sites = KG.sites.filter(x => x[0] === si);
  const comps = G.supLinks[si].slice().sort((a, b) => a.g - b.g)
    .map(l => `<li>${idl('c', KG.components[l.ci][0], KG.components[l.ci][1])} ${gradeBadge(l.g)}<div class="note">${esc(l.ev)}</div></li>`).join('');
  const ves = KG.vessels.filter(v => v[0] === si).map(v => KG.vesselClasses[v[1]][1]);
  const row = (k, v) => `<div class="drv"><span class="note">${k}</span><span>${v}</span><span></span></div>`;
  const city = [...new Set(sites.map(x => x[1]).filter(Boolean))];
  return `<h3>${esc(s[0])}</h3>
    <div class="tag">${s[4] >= 0 ? esc(KG.countries[s[4]]) : 'HQ not stated'} · ${s[2] >= 0 ? TURNOVER[s[2]] : 'turnover n/a'} · ${s[3] >= 0 ? HEADCOUNT[s[3]] + ' staff' : 'headcount n/a'}</div>
    ${s[9] ? `<p class="note" style="margin:10px 0">${esc(s[9])}</p>` : ''}
    ${row('Supply chain role', esc(tierTxt(s[1])))}
    ${row('Wind type', windTxt(s[6]))}
    ${row('Clusters', s[5].map(c => idl('k', c, KG.clusters[c])).join(', ') || 'None stated')}
    ${row('Lifecycle phases', s[7].map(p => esc(KG.phases[p])).join(', ') || 'Not stated')}
    ${row('Sites', sites.length ? `${sites.length}${city.length ? ' · ' + esc(city.slice(0, 6).join(', ')) + (city.length > 6 ? '…' : '') : ''}` : 'None listed')}
    ${ves.length ? row('Vessels', esc(ves.join(', '))) : ''}
    <h2 style="margin-top:14px">Components · ${G.supLinks[si].length}</h2>
    ${comps ? `<ul>${comps}</ul>` : '<p class="note">No component-level evidence in the directory.</p>'}
    ${/^https:\/\//i.test(s[8]) ? `<p style="margin-top:12px"><a href="${esc(s[8])}" target="_blank" rel="noopener">Directory profile ↗</a></p>` : ''}`;
}

// Author: Koorosh Aslansefat
/* turbineSVG: side elevation of an offshore wind turbine (fixed-bottom or floating) with a magnified
   nacelle cut-away. Every component the KG knows is a <g data-c="id"> hit target coloured by colorOf.
   viewBox 1100 × 790: sea surface y=520, seabed y=720. */
function turbineSVG(o) {
  const fixed = o.variant !== 'floating', compact = !!o.compact;
  const fill = id => o.colorOf(CI[id]), stroke = id => o.strokeOf(CI[id]);
  const st = (id, extra = '') => `class="pf" style="fill:${fill(id)};stroke:${stroke(id)};${extra}"`;
  const ln = (id, w = 2.5, extra = '') => `class="pf ln" style="fill:none;stroke:${fill(id)};stroke-width:${w};${extra}"`;
  const P = (id, inner) => {
    const ci = CI[id], c = KG.components[ci];
    return `<g data-c="${id}" class="${o.selected === ci ? 'sel' : ''}" tabindex="0" role="button" aria-label="${esc(c[1])}"><title>${esc(c[1])}</title>${inner}</g>`;
  };
  const steel = 'style="fill:var(--steel);stroke:var(--steel2)"';
  const pts = a => a.map(p => p.map(v => v.toFixed(1)).join(',')).join(' ');
  const blade = (cx, cy, dx, dy, len, root = 12) => {
    const m = Math.hypot(dx, dy); dx /= m; dy /= m; const nx = -dy, ny = dx;
    const p = (t, w) => [cx + dx * (root + (len - root) * t) + nx * w, cy + dy * (root + (len - root) * t) + ny * w];
    return `<polygon ${st('blades')} points="${pts([p(0, 5), p(0.12, 11), p(0.3, 10), p(0.65, 6), p(1, 1.6), p(1, -0.8), p(0.65, -3), p(0.3, -4.5), p(0, -5)])}"/>`;
  };
  let s = '';
  // ---------- scene ----------
  s += `<defs>
    <linearGradient id="seaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--sea)"/><stop offset="1" style="stop-color:var(--sea2)"/></linearGradient>
    <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" style="stroke:var(--surface);stroke-width:2;opacity:.7"/></pattern>
  </defs>
  <rect x="0" y="0" width="1100" height="520" style="fill:var(--sky)"/>
  <rect x="0" y="520" width="1100" height="205" fill="url(#seaG)"/>
  <path d="M0 520 ${Array.from({ length: 23 }, (_, i) => `q 12.5 -5 25 0 t 25 0`).join(' ')}" style="fill:none;stroke:var(--sea2);stroke-width:1.5"/>
  <text x="14" y="512" class="lbl">sea level</text>`;
  // background turbine (fixed view only): neutral, with its jacket + suction buckets as parts
  if (fixed) {
    s += `<g opacity=".75"><polygon ${steel} points="594,330 606,330 609,492 591,492"/><rect x="584" y="318" width="58" height="15" rx="5" ${steel}/>
      <circle cx="580" cy="325" r="7" ${steel}/>
      ${[[0, -1, 120], [-0.7, 0.7, 86], [0.7, 0.7, 86]].map(([dx, dy, l]) => { const m = Math.hypot(dx, dy); const x2 = 580 + dx / m * l, y2 = 325 + dy / m * l; return `<line x1="580" y1="325" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" style="stroke:var(--steel2);stroke-width:5;stroke-linecap:round"/>`; }).join('')}
      <rect x="584" y="490" width="32" height="10" ${steel}/></g>`;
    s += P('jacket', `<rect x="568" y="500" width="64" height="218" style="fill:transparent"/>
      <path ${ln('jacket', 3)} d="M586 500 L574 716 M614 500 L626 716 M584 536 H616 M580 608 H620 M577 680 H623 M586 500 L620 608 M614 500 L580 608 M580 608 L623 716 M620 608 L577 716"/>`);
  }
  // seabed
  s += `<rect x="0" y="720" width="1100" height="70" style="fill:var(--bed)" opacity=".94"/>
    <path d="M0 720 H1100" style="stroke:var(--bed2);stroke-width:2"/>`;
  if (fixed) s += P('suction', `<path ${st('suction')} d="M562 712 h24 v24 h-3 v-20 h-18 v20 h-3 z M614 712 h24 v24 h-3 v-20 h-18 v20 h-3 z"/>`);
  // shore + onshore substation
  s += `<path d="M930 720 C 960 700, 975 560, 1000 505 L1100 500 L1100 790 L930 790 Z" style="fill:var(--bed2)"/>
    <path d="M1000 505 L1100 500" style="stroke:var(--low);stroke-width:2;opacity:.6"/>`;
  s += P('onshore_sub', `<rect x="1012" y="458" width="46" height="42" ${st('onshore_sub')}/><path ${ln('onshore_sub', 2)} d="M1064 500 V464 M1088 500 V464 M1060 468 H1092 M1064 476 L1088 476"/>`);
  // offshore substation
  s += P('offshore_sub', `<rect x="796" y="470" width="80" height="250" style="fill:transparent"/>
    <path ${ln('offshore_sub', 3)} d="M808 720 L816 470 M864 720 L856 470 M810 650 H862 M812 580 H860 M814 520 H858 M808 720 L860 580 M864 720 L812 580 M812 580 L858 470 M860 580 L814 470"/>
    <rect x="785" y="418" width="102" height="54" rx="3" ${st('offshore_sub')}/><rect x="851" y="410" width="34" height="8" ${st('offshore_sub')}/>`);
  s += P('hv_equip', `<rect x="793" y="428" width="28" height="36" rx="2" ${st('hv_equip')}/><rect x="825" y="428" width="28" height="36" rx="2" ${st('hv_equip')}/>
    <rect x="857" y="436" width="22" height="28" rx="2" ${st('hv_equip')}/><path d="M797 436 h20 M797 444 h20 M797 452 h20 M829 436 h20 M829 444 h20 M829 452 h20" style="stroke:var(--surface);stroke-width:1.2;opacity:.8"/>`);
  // cables
  if (fixed) {
    s += P('array_cable', `<path ${ln('array_cable', 3.2)} d="M366 716 C 380 727, 400 728, 430 728 H 568 M632 728 H 800 C 806 728, 808 724, 808 720"/>`);
    s += P('cable_acc', `<polygon ${st('cable_acc')} points="359,694 367,694 372,716 364,718"/><circle cx="380" cy="726" r="3.5" ${st('cable_acc')}/><circle cx="392" cy="728" r="3.5" ${st('cable_acc')}/>`);
  } else {
    s += P('array_cable', `<path ${ln('array_cable', 3.2)} d="M340 592 C 352 640, 372 652, 400 640 C 430 628, 460 700, 520 726 H 800 C 806 726, 808 723, 808 720"/>`);
    s += P('cable_acc', `<polygon ${st('cable_acc')} points="335,578 345,578 343,600 337,600"/>`);
    s += P('buoyancy', `${[[388, 645], [402, 640], [416, 637]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="6" ry="8" ${st('buoyancy')}/>`).join('')}`);
  }
  s += P('export_cable', `<path ${ln('export_cable', 3.2)} d="M864 720 C 870 728, 880 729, 900 729 H 940 C 975 700, 990 600, 1035 500"/>`);
  s += P('cables', `<line x1="${fixed ? 500 : 470}" y1="728" x2="${fixed ? 500 : 470}" y2="748" style="stroke:var(--muted);stroke-width:1"/>
    <circle cx="${fixed ? 500 : 470}" cy="764" r="17" ${st('cables')}/>${[[-6, -4], [6, -4], [0, 6]].map(([dx, dy]) => `<circle cx="${(fixed ? 500 : 470) + dx}" cy="${764 + dy}" r="5" style="fill:var(--surface);stroke:var(--ink);stroke-width:.8"/>`).join('')}`);
  // ---------- foundation ----------
  const towerBase = fixed ? 480 : 470;
  if (fixed) {
    s += P('fixed_fnd', `<path d="M300 482 H290 V760 H300" style="fill:none;stroke:transparent;stroke-width:14"/><path ${ln('fixed_fnd', 3)} d="M300 482 H290 V760 H300"/>`);
    s += P('monopile', `<rect x="321" y="556" width="38" height="206" ${st('monopile')}/>`);
    s += P('tp', `<rect x="320" y="480" width="40" height="76" rx="2" ${st('tp')}/>`);
    s += P('scour', [[292, 716, 9], [306, 713, 8], [318, 717, 7], [366, 717, 7], [378, 713, 8], [392, 716, 9], [300, 721, 6], [386, 721, 6], [340, 718, 6]]
      .map(([x, y, r]) => `<ellipse cx="${x}" cy="${y}" rx="${r}" ry="${r * 0.7}" ${st('scour')}/>`).join(''));
    s += P('corrosion', `<rect x="320" y="506" width="40" height="26" ${st('corrosion')}/><rect x="320" y="506" width="40" height="26" fill="url(#hatch)" style="pointer-events:none"/>
      ${[[313, 598], [359, 598], [313, 650], [359, 650]].map(([x, y]) => `<rect x="${x}" y="${y}" width="8" height="14" rx="1.5" ${st('corrosion')}/>`).join('')}`);
    s += P('secondary_steel', `<rect x="294" y="476" width="92" height="5" ${st('secondary_steel')}/><path ${ln('secondary_steel', 1.6)} d="M296 476 V464 M318 476 V464 M362 476 V464 M384 476 V464 M294 464 H386 M363 488 V556 M371 488 V556 M363 496 H371 M363 508 H371 M363 520 H371 M363 532 H371 M363 544 H371"/>`);
  } else {
    s += P('floating_sub', `<rect x="180" y="476" width="36" height="104" rx="4" ${st('floating_sub')}/><rect x="464" y="476" width="36" height="104" rx="4" ${st('floating_sub')}/>
      <rect x="322" y="470" width="36" height="110" rx="4" ${st('floating_sub')}/><rect x="180" y="566" width="320" height="14" rx="3" ${st('floating_sub')}/>
      <path ${ln('floating_sub', 3)} d="M216 492 H322 M358 492 H464 M216 540 L322 500 M464 540 L358 500"/>`);
    s += P('corrosion', `${[180, 322, 464].map(x => `<rect x="${x}" y="508" width="36" height="22" ${st('corrosion')}/><rect x="${x}" y="508" width="36" height="22" fill="url(#hatch)" style="pointer-events:none"/>`).join('')}`);
    s += P('secondary_steel', `<rect x="300" y="465" width="80" height="5" ${st('secondary_steel')}/><path ${ln('secondary_steel', 1.6)} d="M302 465 V454 M378 465 V454 M300 454 H380 M503 488 V560 M511 488 V560 M503 500 H511 M503 514 H511 M503 528 H511 M503 542 H511"/>`);
    // mooring spread: hit areas first, then lines
    const lines = ['M190 580 C 160 650, 110 715, 30 721', 'M490 580 C 520 650, 570 714, 650 721', 'M490 580 C 512 655, 545 716, 600 718'];
    s += P('chain', lines.map(d => `<path d="${d}" style="fill:none;stroke:transparent;stroke-width:12"/><path ${ln('chain', 2.6)} d="${d}"/>`).join(''));
    s += P('mooring', `<polygon ${st('mooring')} points="182,580 198,580 190,590"/><polygon ${st('mooring')} points="482,580 498,580 490,590"/>`);
    s += P('connectors', [[190, 594], [104, 706], [566, 707], [538, 694]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4.2" ${st('connectors', 'stroke-width:1.4')}/>`).join(''));
    s += P('anchors', `<polygon ${st('anchors')} points="14,716 38,716 46,728 22,730"/><polygon ${st('anchors')} points="644,716 668,716 676,728 652,730"/>`);
    s += P('suction', `<path ${st('suction')} d="M588 714 h24 v24 h-3 v-20 h-18 v20 h-3 z"/>`);
  }
  // ---------- tower ----------
  s += P('tower', `<polygon ${st('tower')} points="329,238 351,238 ${fixed ? '357,480 323,480' : '357,470 323,470'}"/><line x1="326" y1="360" x2="354" y2="360" style="stroke:var(--ink);stroke-width:1;opacity:.5"/>`);
  s += P('tower_internals', `<rect x="333" y="388" width="14" height="74" rx="2" style="fill:var(--surface2);stroke:${stroke('tower_internals')}"/>
    <path ${ln('tower_internals', 1.4)} d="M336 392 V458 M344 392 V458 ${Array.from({ length: 8 }, (_, i) => `M336 ${396 + i * 8} H344`).join(' ')}"/><rect x="335" y="414" width="10" height="12" ${st('tower_internals')}/>`);
  s += P('fasteners', `${[328, 334, 340, 346, 352].map(x => `<circle cx="${x}" cy="360" r="1.9" ${st('fasteners', 'stroke-width:.6')}/>`).join('')}
    ${[325, 331, 337, 343, 349, 355].map(x => `<circle cx="${x}" cy="${towerBase - 2}" r="1.9" ${st('fasteners', 'stroke-width:.6')}/>`).join('')}`);
  // ---------- rotor-nacelle assembly (small, in scene) ----------
  s += P('yaw', `<rect x="324" y="233" width="32" height="7" rx="1.5" ${st('yaw')}/>`);
  s += P('nacelle', `<path ${st('nacelle')} d="M222 198 Q222 194 228 194 H380 Q392 194 392 206 V222 Q392 234 380 234 H228 Q222 234 222 230 Z"/>
    <rect x="232" y="201" width="152" height="26" rx="3" style="fill:var(--surface2);stroke:none;opacity:.9"/>
    <path d="M240 214 H300 M246 206 h16 v16 h-16z M270 205 h28 v18 h-28z M304 206 h26 v16 h-26z M336 207 h16 v14 h-16z M358 208 h16 v12 h-16z" style="fill:none;stroke:var(--muted);stroke-width:1"/>`);
  s += P('cms', `<rect x="358" y="186" width="20" height="8" rx="1" ${st('cms')}/><path ${ln('cms', 1.6)} d="M386 194 V172 M380 172 H392"/><circle cx="380" cy="172" r="2.2" ${st('cms')}/><circle cx="392" cy="172" r="2.2" ${st('cms')}/>`);
  s += P('blades', blade(206, 214, 0, -1, 190) + blade(206, 214, -0.707, 0.707, 134) + blade(206, 214, 0.707, 0.707, 134));
  s += P('hub_pitch', `<circle cx="210" cy="214" r="15" ${st('hub_pitch')}/><path ${st('hub_pitch')} d="M197 203 Q180 207 176 214 Q180 221 197 225 Z"/>`);
  // ---------- nacelle cut-away inset ----------
  s += `<path d="M392 200 L600 120" style="stroke:var(--muted);stroke-width:1;stroke-dasharray:4 4;fill:none"/>
    <rect x="600" y="28" width="482" height="236" rx="10" style="fill:var(--surface);stroke:var(--line)"/>
    <text x="616" y="50" class="lbl" style="letter-spacing:.06em">NACELLE CUT-AWAY · ×2.6</text>`;
  s += `<g>` + P('nacelle', `<path ${st('nacelle')} d="M650 96 Q650 86 662 86 H1040 Q1066 86 1066 112 V176 Q1066 202 1040 202 H662 Q650 202 650 192 Z"/>
      <rect x="664" y="100" width="392" height="88" rx="6" style="fill:var(--surface2);stroke:none"/>`) +
    `<rect x="660" y="139" width="120" height="14" rx="3" ${steel}/>` +
    P('hub_pitch', `<circle cx="628" cy="146" r="26" ${st('hub_pitch')}/><circle cx="628" cy="146" r="17" style="fill:none;stroke:var(--surface);stroke-width:2;opacity:.8"/>
      <path ${st('hub_pitch')} d="M606 128 Q594 136 592 146 Q594 156 606 164 Z"/>`) +
    P('main_bearing', `<circle cx="694" cy="146" r="22" ${st('main_bearing')}/><circle cx="694" cy="146" r="11" style="fill:var(--surface2);stroke:var(--ink);stroke-width:.8"/>
      ${Array.from({ length: 8 }, (_, i) => { const a = i * Math.PI / 4; return `<circle cx="${(694 + 16.5 * Math.cos(a)).toFixed(1)}" cy="${(146 + 16.5 * Math.sin(a)).toFixed(1)}" r="2.2" style="fill:var(--surface)"/>`; }).join('')}`) +
    P('gearbox', `<rect x="728" y="112" width="74" height="68" rx="8" ${st('gearbox')}/><circle cx="752" cy="138" r="12" style="fill:none;stroke:var(--surface);stroke-width:2"/><circle cx="780" cy="156" r="16" style="fill:none;stroke:var(--surface);stroke-width:2"/>`) +
    `<rect x="802" y="141" width="10" height="10" ${steel}/>` +
    P('generator', `<rect x="812" y="116" width="72" height="62" rx="10" ${st('generator')}/>${[826, 840, 854, 868].map(x => `<line x1="${x}" y1="122" x2="${x}" y2="172" style="stroke:var(--surface);stroke-width:2;opacity:.75"/>`).join('')}`) +
    P('converter', `<rect x="892" y="108" width="48" height="74" rx="3" ${st('converter')}/>${[118, 130, 142, 154, 166].map(y => `<line x1="898" y1="${y}" x2="934" y2="${y}" style="stroke:var(--surface);stroke-width:1.6;opacity:.75"/>`).join('')}`) +
    P('turbine_trafo', `<rect x="948" y="118" width="48" height="64" rx="3" ${st('turbine_trafo')}/><path d="M958 128 v44 M968 128 v44 M978 128 v44 M988 128 v44" style="stroke:var(--surface);stroke-width:2;opacity:.75"/>`) +
    P('cms', `<rect x="1004" y="108" width="40" height="30" rx="3" ${st('cms')}/><path ${ln('cms', 2)} d="M1032 86 V58 M1022 58 H1042"/><circle cx="1022" cy="58" r="3.5" ${st('cms')}/><circle cx="1042" cy="58" r="3.5" ${st('cms')}/>`) +
    P('yaw', `<rect x="830" y="202" width="84" height="10" rx="2" ${st('yaw')}/><rect x="840" y="190" width="10" height="12" ${st('yaw')}/><rect x="894" y="190" width="10" height="12" ${st('yaw')}/>`) +
    `<path d="M848 212 L872 260 M896 212 L872 260" style="stroke:var(--steel2);stroke-width:1;opacity:.5"/></g>`;
  // ---------- labels ----------
  if (!compact) {
    const SHORT = { hub_pitch: 'Hub & pitch', cms: 'Control & CMS', turbine_trafo: 'Transformer', converter: 'Converter', nacelle: 'Nacelle housing', main_bearing: 'Main bearing' };
    const L = (id, tx, ty, anchor, px, py, short) => {
      const on = o.selected === CI[id];
      const lx = anchor === 'end' ? tx + 4 : anchor === 'start' ? tx - 4 : tx;
      return `${px != null ? `<line class="lead" x1="${lx}" y1="${ty - 3.5}" x2="${px}" y2="${py}" style="stroke:var(--muted);stroke-width:.8"/>` : ''}<text x="${tx}" y="${ty}" text-anchor="${anchor}" class="lbl ${on ? 'on' : ''}" data-c="${id}">${esc(short && SHORT[id] ? SHORT[id] : KG.components[CI[id]][1])}</text>`;
    };
    const inset = [['hub_pitch', 606, 192, 'start'], ['main_bearing', 694, 228, 'middle'], ['gearbox', 765, 246, 'middle'], ['generator', 848, 228, 'middle'],
      ['converter', 916, 246, 'middle'], ['turbine_trafo', 972, 228, 'middle'], ['cms', 1030, 246, 'middle'], ['yaw', 920, 210, 'start'], ['nacelle', 1060, 80, 'end']];
    s += inset.map(([id, x, y, a]) => L(id, x, y, a, null, null, true)).join('');
    const common = [['blades', 150, 70, 'end', 200, 66], ['hub_pitch', 150, 216, 'end', 174, 213], ['tower', 420, 300, 'start', 349, 300],
      ['fasteners', 420, 362, 'start', 354, 360], ['tower_internals', 420, 426, 'start', 347, 426], ['yaw', 420, 252, 'start', 356, 239],
      ['offshore_sub', 836, 402, 'middle'], ['hv_equip', 780, 448, 'end', 793, 446], ['onshore_sub', 1094, 450, 'end'],
      ['export_cable', 905, 748, 'middle'], ['cables', fixed ? 524 : 494, 768, 'start']];
    const fx = [['secondary_steel', 420, 470, 'start', 386, 472], ['tp', 250, 500, 'end', 320, 498], ['corrosion', 250, 530, 'end', 320, 520],
      ['monopile', 250, 620, 'end', 321, 620], ['fixed_fnd', 250, 668, 'end', 290, 668], ['scour', 250, 704, 'end', 288, 714],
      ['cable_acc', 420, 690, 'start', 370, 704], ['array_cable', 470, 716, 'middle'], ['jacket', 660, 600, 'start', 622, 600], ['suction', 660, 752, 'start', 638, 730]];
    const fl = [['floating_sub', 340, 602, 'middle'], ['secondary_steel', 250, 462, 'end', 300, 466], ['corrosion', 160, 522, 'end', 180, 519],
      ['chain', 205, 640, 'start', 160, 640], ['connectors', 150, 600, 'end', 186, 594], ['mooring', 520, 600, 'start', 494, 586],
      ['anchors', 50, 750, 'start', 32, 730], ['suction', 600, 752, 'middle'], ['buoyancy', 430, 616, 'start', 418, 630],
      ['cable_acc', 290, 622, 'end', 336, 598], ['array_cable', 640, 712, 'middle']];
    s += [...common, ...(fixed ? fx : fl)].map(a => L(...a)).join('');
  }
  return `<svg class="turbine" viewBox="0 0 1100 790" style="width:100%;height:auto;display:block" role="img" aria-label="${fixed ? 'Fixed-bottom' : 'Floating'} offshore wind turbine, components coloured by ${o.legend || 'exposure'}">${s}</svg>`;
}

/* Which component ids a variant draws (used for acceptance checks and the parts list). */
function turbineDrawn(variant) {
  const fixedOnly = ['fixed_fnd', 'monopile', 'jacket', 'tp', 'scour'], floatOnly = ['floating_sub', 'mooring', 'chain', 'anchors', 'connectors', 'buoyancy'];
  return new Set(KG.components.map(c => c[0]).filter(id => variant === 'floating' ? !fixedOnly.includes(id) : !floatOnly.includes(id)));
}

// Author: Koorosh Aslansefat
/* Command center: portfolio summary first, the ranked component list second. */
const GRADE_FILL = ['var(--accent)', 'color-mix(in srgb, var(--accent) 60%, var(--surface))', 'color-mix(in srgb, var(--accent) 28%, var(--surface))'];
const gradeLegend = () => `<div class="legend">${LatticeCore.GRADE.map((g, i) => `<span><i style="background:${GRADE_FILL[i]}"></i>${g}</span>`).join('')}</div>`;
const stackBar = (counts, max) => `<div class="stack" style="width:${Math.max(4, counts.reduce((a, v) => a + v, 0) / max * 100)}%">${counts.map((v, i) => v ? `<i style="flex:${v};background:${GRADE_FILL[i]}"></i>` : '').join('')}</div>`;

VIEW_FNS.command = function (m) {
  const S = KG.suppliers, E = COMP_EXP;
  const thin = E.filter(e => e.rules.R2), zero = E.filter(e => e.empty);
  const fl = S.filter(s => s[6] & 4).length, flOnly = S.filter(s => (s[6] & 4) && !(s[6] & 2)).length;
  const clCount = KG.clusters.map((c, i) => [i, S.filter(s => s[5].includes(i)).length]).sort((a, b) => b[1] - a[1]);
  const clustered = S.filter(s => s[5].length).length;
  const top = clCount[0];
  const worstSub = Object.entries(BASE.fixed.subs).sort((a, b) => b[1] - a[1])[0];
  const rows = E.slice().sort((a, b) => b.score - a.score || b.n - a.n);
  const appl = { both: 'Both', fixed: 'Fixed', floating: 'Floating' };
  // installation bottlenecks: vessel classes + ports, distinct suppliers by best grade
  const vrows = KG.vesselClasses.map((v, vi) => {
    const best = {}; KG.vessels.filter(x => x[1] === vi).forEach(x => { best[x[0]] = Math.min(best[x[0]] ?? 9, x[2]); });
    const c = [0, 0, 0]; Object.values(best).forEach(g => c[g]++); return [v[1], c];
  });
  const pc = [0, 0, 0]; KG.ports.forEach(p => pc[p[1]]++);
  vrows.push(['Ports & yards', pc]);
  const overseas = S.filter(s => s[4] > 0).length;  // countries[0] is the UK; -1 means HQ not stated
  vrows.sort((a, b) => b[1].reduce((x, y) => x + y) - a[1].reduce((x, y) => x + y));
  const vmax = Math.max(...vrows.map(r => r[1].reduce((x, y) => x + y)));
  m.innerHTML = `<h1>${thin.length} of ${KG.components.length} turbine components have two or fewer explicit or declared directory suppliers</h1>
    <p class="sub">The graph follows each turbine component to the directory suppliers that evidence it, then out to regional clusters and HQ countries. Built from the ${fmt(S.length)} offshore-evidenced profiles among ${fmt(KG.meta.totalProfiles)} in the UK Offshore Wind Directory. A directory supplier here is any firm listed in that directory; ${fmt(overseas)} of them have their HQ overseas.</p>
    <div class="grid kpis">
      <div class="panel kpi"><b>${thin.length}</b><span>components with thin UK supply (R2)</span><em>${zero.length} have no evidenced supplier at all</em></div>
      <div class="panel kpi"><b>${BASE.fixed.turbine} <span style="display:inline;font-size:20px;color:var(--muted)">/ ${BASE.floating.turbine}</span></b><span>turbine exposure, fixed / floating (R3)</span><em>${esc(SUBNAME[worstSub[0]])} is the weakest subsystem at ${worstSub[1]}</em></div>
      <div class="panel kpi"><b>${pct(fl, S.length)}%</b><span>of suppliers declare floating wind</span><em>${fmt(fl)} suppliers · ${flOnly} floating only</em></div>
      <div class="panel kpi"><b>${pct(top[1], clustered)}%</b><span>of clustered suppliers are in ${esc(KG.clusters[top[0]])}</span><em>${fmt(S.length - clustered)} suppliers name no cluster</em></div>
    </div>
    <div class="grid two" style="margin-top:16px">
      <section class="panel"><h2>Where to look first</h2>
        <div class="scroll"><table><thead><tr><th>Component</th><th>Turbine</th><th>Exposure</th><th>Suppliers</th><th>Rules</th></tr></thead><tbody>
        ${rows.map(e => { const c = KG.components[e.ci]; return `<tr class="click" data-go="c:${c[0]}">
          <td><b style="font-weight:600">${esc(c[1])}</b><div class="tag"><i style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${subVar(c[2])};margin-right:5px"></i>${esc(SUBNAME[c[2]])}</div></td>
          <td class="note">${appl[c[3]]}</td>
          <td style="min-width:130px"><div style="display:flex;gap:8px;align-items:center">${bar(e.score, e.band)}<span class="num">${e.score}</span></div></td>
          <td class="num">${e.empty ? '<span class="note">none evidenced</span>' : `${e.nStrong}${e.links.length - e.nStrong ? ` <span class="note">+ ${e.links.length - e.nStrong} inferred</span>` : ''}`}</td>
          <td>${ruleChips(e.rules)}</td></tr>`; }).join('')}
        </tbody></table></div>
        <p class="note">Ranked by exposure index, a transparent model, not a forecast. Select a row to trace it to suppliers, clusters and countries.</p>
      </section>
      <div style="display:flex;flex-direction:column;gap:16px;min-width:0">
        <section class="panel"><h2>Subsystem exposure (R3)</h2>
          <table><thead><tr><th>Subsystem</th><th class="num">Fixed</th><th class="num">Floating</th></tr></thead><tbody>
          ${SUBS.map(sid => `<tr><td><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${subVar(sid)};margin-right:6px"></i>${esc(SUBNAME[sid])}</td>
            ${['fixed', 'floating'].map(v => { const x = BASE[v].subs[sid]; return `<td class="num">${x == null ? '<span class="note">n/a</span>' : `${x} ${pill(LatticeCore.bandOf(x))}`}</td>`; }).join('')}</tr>`).join('')}
          </tbody></table></section>
        <section class="panel"><h2>Supplier base by cluster</h2>
          ${clCount.map(([i, n]) => `<div class="hbar click" data-go="k:${i}" tabindex="0" role="link"><span>${esc(KG.clusters[i])}</span><div class="bar"><i style="width:${n / clCount[0][1] * 100}%;background:var(--accent)"></i></div><span class="num">${n}</span></div>`).join('')}
          <p class="note">Select a cluster to simulate losing it. Suppliers can belong to several clusters.</p></section>
        <section class="panel"><h2>Installation vessels & ports</h2>${gradeLegend()}
          ${vrows.map(([nm, c]) => `<div class="hbar"><span>${esc(nm)}</span>${stackBar(c, vmax)}<span class="num">${c.reduce((a, v) => a + v)}</span></div>`).join('')}
          <p class="note">InstallationVessel and PortOrYard fill the core's Chokepoint and Port classes. Bars count the suppliers offering each, by strongest evidence: a count of firms, not of vessels, berths or capacity, so a short bar flags a possible bottleneck rather than proving one.</p></section>
      </div>
    </div>`;
};

// Author: Koorosh Aslansefat
/* Turbine anatomy: the system breakdown drawn as a turbine; every part is a Material/Component
   instance coloured by its exposure (or supplier depth) and opens its evidence. */
const anatColor = (ci, E) => STATE.colorBy === 'band' ? `color-mix(in srgb, ${bandVar(E[ci].band)} 58%, var(--surface))` : heatVar(E[ci].links.length);
const anatStroke = (ci, E) => STATE.colorBy === 'band' ? bandVar(E[ci].band) : (E[ci].links.length ? 'var(--ink)' : 'var(--sev)');

function anatLegend() {
  return STATE.colorBy === 'band'
    ? `<div class="legend">${['Severe', 'High', 'Moderate', 'Low'].map(b => `<span><i style="background:${bandVar(b)}"></i>${b}</span>`).join('')}<span>Exposure index · a transparent model, not a forecast</span></div>`
    : `<div class="legend">${heatLegend()}<span>explicit, declared and inferred suppliers</span></div>`;
}

function anatParts(E) {
  const drawn = turbineDrawn(STATE.variant);
  // one header per grid column; CSS shows as many as there are columns
  const heads = [0, 1, 2, 3, 4, 5].map(i => `<div class="parthead" ${i ? 'aria-hidden="true"' : ''}><span>Component</span><span>Exposure</span><span class="r"><b>Suppliers</b></span></div>`).join('');
  return `<div class="parts" id="parts">${heads}${SUBS.map(sid => {
    const rows = KG.components.map((c, ci) => [c, ci]).filter(([c]) => c[2] === sid);
    if (STATE.variant === 'fixed' && sid === 'STK') return `<div class="parthd"><i style="background:${subVar(sid)}"></i>${esc(SUBNAME[sid])} · floating only</div>`;
    return `<div class="parthd"><i style="background:${subVar(sid)}"></i>${esc(SUBNAME[sid])} · ${BASE[STATE.variant].subs[sid] ?? '–'}</div>` +
      rows.map(([c, ci]) => `<div class="part ${STATE.comp === ci ? 'sel' : ''} ${drawn.has(c[0]) ? '' : 'na'}" data-pc="${ci}" tabindex="0" role="button" title="${drawn.has(c[0]) ? '' : 'Not part of this turbine variant'}">
        <span class="nm">${esc(c[1])}</span>${bar(E[ci].score, E[ci].band)}<span class="num" title="Exposure score">${E[ci].score}</span><span class="num" style="color:var(--muted)" title="Suppliers">${E[ci].links.length}</span></div>`).join('');
  }).join('')}</div>`;
}

VIEW_FNS.anatomy = function (m) {
  const E = COMP_EXP, R = BASE[STATE.variant];
  const zero = E.filter(e => e.empty && LatticeCore.applies(KG.components[e.ci], STATE.variant)).length;
  const seg = (k, opts) => `<div class="seg" role="group">${opts.map(([v, l]) => `<button data-${k}="${v}" aria-pressed="${STATE[k === 'v' ? 'variant' : 'colorBy'] === v}">${l}</button>`).join('')}</div>`;
  m.innerHTML = `<h1>Every part of the turbine, scored against the UK supply base</h1>
    <p class="sub">Each component is an instance of the core Material class. Colour shows its exposure index; select a part for its ontology path, the suppliers behind it and the evidence for each link. ${zero} of the parts in this turbine have no supplier linked in this snapshot.</p>
    <div class="toolbar">
      <div class="field"><span class="lbl">Turbine</span>${seg('v', [['fixed', 'Fixed-bottom'], ['floating', 'Floating']])}</div>
      <div class="field"><span class="lbl">Colour by</span>${seg('cb', [['band', 'Exposure band'], ['depth', 'Supplier depth']])}</div>
      <div class="field"><span class="lbl">Turbine exposure (R3)</span><div style="display:flex;gap:8px;align-items:center;height:34px"><b style="font:700 22px var(--f-display)">${R.turbine}</b>${pill(LatticeCore.bandOf(R.turbine))}
        <span class="note">${Object.entries(R.subs).map(([k, v]) => `${esc(SUBNAME[k])} ${v}`).join(' · ')}</span></div></div>
    </div>
    <div class="anat">
      <div class="panel"><div id="tsvg">${turbineSVG({ variant: STATE.variant, selected: STATE.comp, colorOf: ci => anatColor(ci, E), strokeOf: ci => anatStroke(ci, E), legend: STATE.colorBy === 'band' ? 'exposure band' : 'supplier depth' })}</div>
        ${anatLegend()}${anatParts(E)}</div>
      <aside class="panel detail" id="adetail">${compDetail(STATE.comp)}</aside>
    </div>`;
  const select = ci => {
    STATE.comp = ci;
    m.querySelectorAll('#tsvg [data-c]').forEach(g => { g.classList.toggle('sel', CI[g.dataset.c] === ci); if (g.tagName === 'text') g.classList.toggle('on', CI[g.dataset.c] === ci); });
    m.querySelectorAll('.part').forEach(p => p.classList.toggle('sel', +p.dataset.pc === ci));
    $('#adetail').innerHTML = compDetail(ci);
    if (innerWidth < 1100) $('#adetail').scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  m.querySelectorAll('[data-v]').forEach(b => b.onclick = () => { STATE.variant = b.dataset.v; VIEW_FNS.anatomy(m); });
  m.querySelectorAll('[data-cb]').forEach(b => b.onclick = () => { STATE.colorBy = b.dataset.cb; VIEW_FNS.anatomy(m); });
  const svg = $('#tsvg', m);
  svg.addEventListener('click', e => { const g = e.target.closest('[data-c]'); if (g) select(CI[g.dataset.c]); });
  svg.addEventListener('keydown', e => { const g = e.target.closest('[data-c]'); if (g && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); select(CI[g.dataset.c]); } });
  svg.addEventListener('mousemove', e => {
    const g = e.target.closest('[data-c]'); if (!g) return hideTip();
    const ci = CI[g.dataset.c], x = E[ci];
    showTip(e, `<b>${esc(KG.components[ci][1])}</b><br>Exposure ${x.score} · ${x.band}<br>${x.links.length} suppliers (${x.nStrong} explicit or declared)`);
  });
  svg.addEventListener('mouseleave', hideTip);
  m.querySelectorAll('.part').forEach(p => {
    p.onclick = () => select(+p.dataset.pc);
    p.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(+p.dataset.pc); } };
  });
};

// Author: Koorosh Aslansefat
/* Trace a component: Component → Suppliers → Clusters → HQ countries, edges weighted by evidence. */
let traceStrong = false, traceSel = null, traceComp = null;

function traceSvg(ci) {
  const e = COMP_EXP[ci];
  const links = e.links.filter(l => !traceStrong || l.g < 2).slice().sort((a, b) => a.g - b.g || G.S[a.si][0].localeCompare(G.S[b.si][0]));
  const RH = 28, top = 40, X = [10, 230, 560, 760], W = [180, 250, 160, 140];
  const sups = links.map(l => l.si);
  const cls = [...new Set(sups.flatMap(si => G.S[si][5].length ? G.S[si][5] : [-1]))].sort((a, b) => (a < 0) - (b < 0) || a - b);
  const cos = [...new Set(sups.map(si => G.S[si][4]))].sort((a, b) => (a < 0) - (b < 0) || a - b);
  const rows = Math.max(sups.length, cls.length, cos.length, 1), H = top + rows * RH + 10;
  const yOf = (i, n) => top + (rows - n) * RH / 2 + i * RH;
  const sp = Object.fromEntries(sups.map((si, i) => [si, yOf(i, sups.length)]));
  const cp = Object.fromEntries(cls.map((c, i) => [c, yOf(i, cls.length)]));
  const kp = Object.fromEntries(cos.map((c, i) => [c, yOf(i, cos.length)]));
  const cy = yOf(0, 1);
  const path = (x1, y1, x2, y2) => { const mx = (x1 + x2) / 2; return `M${x1} ${y1 + 11}C${mx} ${y1 + 11},${mx} ${y2 + 11},${x2} ${y2 + 11}`; };
  let ed = '', nd = '';
  links.forEach(l => { ed += `<path class="edge" data-k="c s${l.si}" stroke="${bandVar(e.band)}" stroke-width="${(1 + l.conf * 3).toFixed(1)}" ${l.g === 2 ? 'stroke-dasharray="5 4"' : ''} d="${path(X[0] + W[0], cy, X[1], sp[l.si])}"/>`; });
  sups.forEach(si => {
    (G.S[si][5].length ? G.S[si][5] : [-1]).forEach(c => { ed += `<path class="edge" data-k="s${si} k${c}" stroke="var(--muted)" stroke-width="1.2" d="${path(X[1] + W[1], sp[si], X[2], cp[c])}"/>`; });
    ed += `<path class="edge" data-k="s${si} n${G.S[si][4]}" stroke="var(--muted)" stroke-width="1.2" d="${path(X[1] + W[1], sp[si], X[3], kp[G.S[si][4]])}"/>`;
  });
  const node = (k, x, y, w, t1, t2, extra = '') => `<g class="tnode ${traceSel === k ? 'sel' : ''}" data-n="${k}" tabindex="0" role="button" transform="translate(${x},${y})"><rect width="${w}" height="22" rx="4" ${extra}/><text x="8" y="11" dominant-baseline="central">${esc(t1)}</text>${t2 ? `<text class="sub" x="${w - 7}" y="11" dominant-baseline="central" text-anchor="end">${esc(t2)}</text>` : ''}</g>`;
  const cut = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s;
  nd += node('c', X[0], cy, W[0], cut(KG.components[ci][1], 22), `${e.score}`, `style="stroke:${bandVar(e.band)};stroke-width:2"`);
  links.forEach(l => { const s = G.S[l.si]; nd += node(`s${l.si}`, X[1], sp[l.si], W[1], cut(s[0], 30), LatticeCore.GRADE[l.g].slice(0, 3).toLowerCase() + (s[2] >= 0 ? ' · ' + TURNOVER[s[2]] : '')); });
  cls.forEach(c => { const n = sups.filter(si => (G.S[si][5].length ? G.S[si][5] : [-1]).includes(c)).length; nd += node(`k${c}`, X[2], cp[c], W[2], c < 0 ? 'No cluster stated' : cut(KG.clusters[c], 20), String(n)); });
  cos.forEach(c => { const n = sups.filter(si => G.S[si][4] === c).length; nd += node(`n${c}`, X[3], kp[c], W[3], c < 0 ? 'HQ not stated' : cut(KG.countries[c], 18), String(n)); });
  const heads = ['Component', 'Suppliers', 'Clusters', 'HQ countries'].map((t, i) => `<text class="colh" x="${X[i]}" y="20">${t}</text>`).join('');
  return `<svg viewBox="0 0 910 ${H}" style="width:100%;min-width:760px;height:auto" role="img" aria-label="Trace of ${esc(KG.components[ci][1])}">${heads}${ed}${nd}</svg>`;
}

function traceDetail(ci) {
  if (!traceSel || traceSel === 'c') return compDetail(ci);
  const id = +traceSel.slice(1), kind = traceSel[0];
  if (kind === 's') return linkBlock(ci, id) + supplierDetail(id);
  const sups = COMP_EXP[ci].links.map(l => l.si);
  if (kind === 'k') {
    const inC = sups.filter(si => id < 0 ? !G.S[si][5].length : G.S[si][5].includes(id));
    return `<h3>${id < 0 ? 'No cluster stated' : esc(KG.clusters[id])}</h3><div class="tag">RegionalCluster · ${inC.length} of ${sups.length} suppliers of ${esc(KG.components[ci][1])}</div>
      <ul>${inC.map(si => `<li>${idl('s', si, G.S[si][0])}</li>`).join('')}</ul>
      ${id >= 0 ? `<p style="margin-top:12px"><span class="btn primary" data-go="k:${id}" role="button" tabindex="0">Simulate losing ${esc(KG.clusters[id])}</span></p>` : ''}`;
  }
  const inN = sups.filter(si => G.S[si][4] === id);
  return `<h3>${id < 0 ? 'HQ not stated' : esc(KG.countries[id])}</h3><div class="tag">Country · ${inN.length} of ${sups.length} suppliers</div><ul>${inN.map(si => `<li>${idl('s', si, G.S[si][0])}</li>`).join('')}</ul>`;
}

VIEW_FNS.trace = function (m) {
  const ci = STATE.comp, e = COMP_EXP[ci], cname = esc(KG.components[ci][1]);
  const hidden = !e.empty && traceStrong && !e.links.some(l => l.g < 2);
  if (traceComp !== ci) { traceSel = null; traceComp = ci; TM.fan = null; }
  if (STATE.supplier != null) { traceSel = `s${STATE.supplier}`; STATE.supplier = null; }
  const opts = SUBS.map(sid => `<optgroup label="${esc(SUBNAME[sid])}">${KG.components.map((c, i) => [c, i]).filter(([c]) => c[2] === sid)
    .map(([c, i]) => `<option value="${i}" ${i === ci ? 'selected' : ''}>${esc(c[1])} · ${COMP_EXP[i].score} · ${COMP_EXP[i].links.length} suppliers</option>`).join('')}</optgroup>`).join('');
  m.innerHTML = `<h1>Trace a component to its supply base</h1>
    <p class="sub">Component → suppliers → regional clusters → HQ countries. Line width is evidence confidence; dashed lines are inferred from descriptions (R1). Select any node for the evidence behind it.</p>
    <div class="toolbar"><div class="field"><label for="tsel">Component</label><select id="tsel">${opts}</select></div>
      <div class="field"><span class="lbl">Evidence</span><div class="seg" role="group"><button data-ev="0" aria-pressed="${!traceStrong}">All links</button><button data-ev="1" aria-pressed="${traceStrong}">Explicit & declared</button></div></div>
      <div class="field"><span class="lbl">Show as</span><div class="seg" role="group"><button data-tm="diagram" aria-pressed="${STATE.traceMode !== 'map'}">Diagram</button><button data-tm="map" aria-pressed="${STATE.traceMode === 'map'}">Map</button></div></div></div>
    <div class="trace"><div class="panel">
      ${STATE.traceMode === 'map' ? '' : `<div class="legend"><span><i style="background:${bandVar(e.band)}"></i>Supply link (${e.band.toLowerCase()} exposure)</span><span>— explicit / declared</span><span>- - inferred</span></div>`}
      ${e.empty ? `<div class="empty">No directory supplier is evidenced for ${cname}. The core keeps the Material node, so a new supplier record would link here automatically.</div>`
        : hidden ? `<div class="empty">${e.links.length === 1 ? `The only supplier link for ${cname} is inferred from a company description` : `All ${e.links.length} supplier links for ${cname} are inferred from company descriptions`}, so none is explicit or declared. Choose All links to trace ${e.links.length === 1 ? 'it' : 'them'}.</div>`
        : STATE.traceMode === 'map' ? `<div id="tmapw">${tmInner(ci)}</div>`
        : `<div class="svgwrap" id="tsvgw">${traceSvg(ci)}</div>`}
    </div><aside class="panel detail" id="tdetail">${traceDetail(ci)}</aside></div>`;
  $('#tsel').onchange = ev => { STATE.comp = +ev.target.value; traceSel = null; TM.fan = null; VIEW_FNS.trace(m); };
  m.querySelectorAll('[data-ev]').forEach(b => b.onclick = () => { traceStrong = b.dataset.ev === '1'; traceSel = null; TM.fan = null; VIEW_FNS.trace(m); });
  m.querySelectorAll('[data-tm]').forEach(b => b.onclick = () => { STATE.traceMode = b.dataset.tm; TM.fan = null; VIEW_FNS.trace(m); });
  if (STATE.traceMode === 'map') return wireTraceMap(m, ci);
  const svg = m.querySelector('#tsvgw svg'); if (!svg) return;
  svg.querySelectorAll('.tnode').forEach(g => {
    const pick = () => { traceSel = g.dataset.n; svg.querySelectorAll('.tnode').forEach(x => x.classList.toggle('sel', x === g)); $('#tdetail').innerHTML = traceDetail(ci); };
    g.addEventListener('click', pick);
    g.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pick(); } });
    g.addEventListener('mouseenter', () => {
      // keep the node's own edges; for a cluster or country also keep the component → supplier edges feeding it
      const k = g.dataset.n, edges = [...svg.querySelectorAll('.edge')], ends = p => p.dataset.k.split(' ');
      const own = new Set(edges.filter(p => ends(p).includes(k)));
      const sups = new Set('kn'.includes(k[0]) ? [...own].map(p => ends(p)[0]) : []);
      edges.forEach(p => p.classList.toggle('dim', !(own.has(p) || (ends(p)[0] === 'c' && sups.has(ends(p)[1])))));
    });
    g.addEventListener('mouseleave', () => svg.querySelectorAll('.edge').forEach(p => p.classList.remove('dim')));
  });
  if (traceSel && traceSel[0] === 's') { const n = svg.querySelector(`[data-n="${traceSel}"]`); if (n) n.scrollIntoView({ block: 'nearest' }); }
};

// Author: Koorosh Aslansefat
/* Trace map mode: the chosen component's suppliers pinned at their site towns and linked to the
   component card with the same evidence styling as the Trace diagram. Geometry comes from geo.js. */
const HAS_GEO = !!(window.GEO && GEO.places && GEO.basemap);
const GEO_NOTE = 'Trace map: town positions from GeoNames (CC BY 4.0), placed at town level only; coastline from Natural Earth (public domain).';
const TM = { W: 700, fan: null, model: null };   // W follows the rendered map width; fan = key of the spread-out group
const TM_SITES = GeoCore.sitesBy(KG);
const TM_R = [7, 8.5, 10, 12];                    // pin radius by turnover band; unknown uses the first
const TM_GROUP = 18;                              // pins closer than this merge into a count bubble
const TM_BAND = 72;                               // height of the band above the map that holds the card
const TM_PROJ = {};
const tmF = v => v.toFixed(1);
const tmProj = W => TM_PROJ[W] || (TM_PROJ[W] = GeoCore.makeProjection(W, { top: TM_BAND }));
const tmNat = si => GeoCore.isNational(G.S[si][5], KG.clusters.length);

function tmModel(ci) {
  const e = COMP_EXP[ci], P = tmProj(TM.W), at = (lat, lon) => P.project(lon, lat);
  const rows = e.links.slice().sort((a, b) => a.g - b.g || G.S[a.si][0].localeCompare(G.S[b.si][0]))
    .map((l, i) => ({ n: i + 1, si: l.si, g: l.g, conf: l.conf, shown: !traceStrong || l.g < 2, ...GeoCore.place(l.si, KG, GEO, TM_SITES) }));
  const placed = rows.filter(r => r.shown && r.pin);
  placed.forEach(r => { [r.x, r.y] = at(r.pin.lat, r.pin.lon); });
  const groups = GeoCore.groupPins(placed.map(r => ({ id: r.n, x: r.x, y: r.y })), TM_GROUP);
  groups.forEach(gp => {
    gp.rows = gp.ids.map(id => rows[id - 1]); gp.key = gp.rows[0].si;
    gp.open = gp.rows.length > 1 && TM.fan === gp.key;
    const fan = gp.open ? GeoCore.fanPositions(gp.x, gp.y, gp.rows.length, 26) : null;
    gp.rows.forEach((r, k) => { r.group = gp; r.at = gp.rows.length === 1 ? [r.x, r.y] : fan ? fan[k] : null; r.end = r.at || [gp.x, gp.y]; });
  });
  return (TM.model = { e, rows, placed, groups, P, at });
}

function tmPin(r, band) {
  const s = G.S[r.si], rad = TM_R[s[2]] ?? TM_R[0], [x, y] = r.at.map(tmF), on = traceSel === 's' + r.si;
  const style = r.g === 0 ? `fill:${band};stroke:none` : `fill:var(--surface);stroke:${band};stroke-width:${r.g === 1 ? 2 : 1.5}`;
  return `<g class="tm-pin" data-n="s${r.si}" tabindex="0" role="button" aria-label="${esc(s[0])}, ${esc(r.pin.town)}, ${LatticeCore.GRADE[r.g].toLowerCase()}">`
    + (on ? `<circle class="tm-selring" cx="${x}" cy="${y}" r="${rad + 4}"/>` : '')
    + (r.pin.approx ? `<circle class="tm-approx" cx="${x}" cy="${y}" r="${rad + 2.5}"/>` : '')
    + `<circle cx="${x}" cy="${y}" r="${rad}" style="${style}"${r.g === 2 ? ' stroke-dasharray="3 2"' : ''}/>`
    + `<text x="${x}" y="${y}"${r.g === 0 ? ' class="on-band"' : ''}>${r.n}</text></g>`;
}

function tmSvg(ci) {
  const M = tmModel(ci), { e, P, at } = M, W = TM.W, H = P.height, band = bandVar(e.band);
  const cw = Math.min(260, W - 24), card = { x: W - cw - 12, y: 10, w: cw, h: 52 }, ox = card.x + cw / 2, oy = card.y + card.h;
  const ring = r => 'M' + r.map(([lon, lat]) => at(lat, lon).map(tmF).join(' ')).join('L') + 'Z';
  let land = '', regs = '', ties = '', lines = '', hq = '', pins = '', top = '';
  GEO.basemap.forEach(f => { land += `<path class="tm-${f.role}" d="${f.rings.map(ring).join('')}"/>`; });

  // cluster regions (approximate) with their non-national members; ties for members sited outside
  const members = {};
  M.rows.filter(r => r.shown && !tmNat(r.si)).forEach(r => G.S[r.si][5].forEach(c => (members[c] = members[c] || []).push(r)));
  Object.entries(members).forEach(([c, rs]) => {
    const geo = GeoCore.CLUSTER_GEO[KG.clusters[c]]; if (!geo) return;
    const [x, y] = at(geo[0], geo[1]), rad = geo[2] * P.unitsPerKm, [lx, ly] = at(geo[3], geo[4]);
    regs += `<g class="tm-reg ${traceSel === 'k' + c ? 'on' : ''}" data-k="${c}" style="color:${band}" tabindex="0" role="button" aria-label="${esc(KG.clusters[c])}, ${rs.length} supplier${rs.length === 1 ? '' : 's'}, approximate region">`
      + `<circle cx="${tmF(x)}" cy="${tmF(y)}" r="${tmF(rad)}"/><text x="${tmF(lx)}" y="${tmF(ly)}" text-anchor="${geo[5]}">${esc(KG.clusters[c])} · ${rs.length}</text></g>`;
    rs.forEach(r => {
      if (!r.end) return;
      const [px, py] = r.end, d = Math.hypot(px - x, py - y); if (d <= rad) return;
      ties += `<line class="tm-tie" data-n="s${r.si}" data-k="${c}" x1="${tmF(px)}" y1="${tmF(py)}" x2="${tmF(x + (px - x) / d * rad)}" y2="${tmF(y + (py - y) / d * rad)}"/>`;
    });
  });

  // supply links: card → pin (or its bubble), styled like the diagram's component → supplier edges
  M.placed.forEach(r => {
    const own = G.S[r.si][5], [x, y] = r.end, cl = tmNat(r.si) ? '' : own.length ? own.join(' ') : '-1';   // -1: no cluster stated
    lines += `<path class="edge tm-ln" data-n="s${r.si}" data-c=" ${cl} " d="M${tmF(ox)} ${tmF(oy)}Q${tmF((ox + x) / 2)} ${tmF(oy + (y - oy) * 0.15)} ${tmF(x)} ${tmF(y)}" stroke="${band}" stroke-width="${tmF(1 + r.conf * 3)}"${r.g === 2 ? ' stroke-dasharray="6 4"' : ''}/>`;
  });

  // overseas HQs: a chip where the bearing to the country leaves the frame (Ireland is on the map)
  const [ux, uy] = at(...GeoCore.UK_CENTRE), frame = [8, TM_BAND + 8, W - 8, H - 8], byCountry = {};
  M.placed.forEach(r => { const h = G.S[r.si][4]; if (h > 0) (byCountry[h] = byCountry[h] || []).push(r); });
  const chips = Object.entries(byCountry).map(([hq, rs]) => {
    const name = KG.countries[hq], c = GeoCore.COUNTRY_CENTROID[name] || GeoCore.UK_CENTRE;
    const label = `HQ: ${W < 420 ? GeoCore.COUNTRY_SHORT[name] || name : name}${rs.length > 1 ? ' · ' + rs.length : ''}`;
    let a;
    if (name === 'Ireland') { const [x, y] = at(c[0], c[1]); a = { x, y, side: 'in' }; }   // on the map: point at it
    else a = GeoCore.edgeAnchor(ux, uy, GeoCore.bearing(GeoCore.UK_CENTRE[0], GeoCore.UK_CENTRE[1], c[0], c[1]), frame);
    return { hq, rs, label, ...a, w: GeoCore.chipWidth(label), h: 22 };
  });
  // keep chips off each other and off every pin or bubble, so nothing tappable is covered
  const avoid = [];
  M.groups.forEach(gp => {
    if (gp.rows.length > 1 && !gp.open) avoid.push([gp.x - 15, gp.y - 15, gp.x + 15, gp.y + 15]);
    else gp.rows.forEach(r => { const rr = (TM_R[G.S[r.si][2]] ?? TM_R[0]) + 4; avoid.push([r.at[0] - rr, r.at[1] - rr, r.at[0] + rr, r.at[1] + rr]); });
  });
  const rects = GeoCore.layoutChips(chips, frame, avoid);
  chips.forEach((ch, i) => {
    const { x, y, w, h: hh } = rects[i], cx = x + w / 2, cy = y + hh / 2;
    ch.rs.forEach(r => {
      const [sx, sy] = r.end, dx = cx - sx, dy = cy - sy, d = Math.hypot(dx, dy) || 1;
      const t = Math.min(w / 2 / Math.max(Math.abs(dx / d), 1e-9), hh / 2 / Math.max(Math.abs(dy / d), 1e-9)) + 3;
      hq += `<line class="tm-hq" data-n="s${r.si}" x1="${tmF(sx)}" y1="${tmF(sy)}" x2="${tmF(cx - dx / d * t)}" y2="${tmF(cy - dy / d * t)}" marker-end="url(#tmArrow)"/>`;
    });
    top += `<g class="tm-chip ${traceSel === 'n' + ch.hq ? 'on' : ''}" data-q="${ch.hq}" tabindex="0" role="button" aria-label="${esc(ch.label)}"><rect x="${tmF(x)}" y="${tmF(y)}" width="${tmF(w)}" height="${hh}" rx="4"/><text x="${tmF(x + 8)}" y="${tmF(cy)}">${esc(ch.label)}</text></g>`;
  });

  // the selected supplier's other site towns
  const selR = M.placed.find(r => traceSel === 's' + r.si);
  if (selR) selR.others.forEach(o => {
    const [x, y] = at(o.lat, o.lon);
    pins += `<line class="tm-otherln" x1="${tmF(selR.end[0])}" y1="${tmF(selR.end[1])}" x2="${tmF(x)}" y2="${tmF(y)}"/><circle class="tm-other" cx="${tmF(x)}" cy="${tmF(y)}" r="3.5"><title>${esc(o.town)}</title></circle>`;
  });
  // pins, fans and count bubbles
  M.groups.forEach(gp => {
    if (gp.open) gp.rows.forEach(r => { pins += `<line class="tm-spoke" x1="${tmF(gp.x)}" y1="${tmF(gp.y)}" x2="${tmF(r.at[0])}" y2="${tmF(r.at[1])}"/>`; });
    gp.rows.forEach(r => { if (r.at) pins += tmPin(r, band); });
    if (gp.rows.length > 1 && !gp.open) pins += `<g class="tm-bub" data-g="${gp.key}" tabindex="0" role="button" aria-label="${gp.rows.length} suppliers in one place, select to spread them out"><circle cx="${tmF(gp.x)}" cy="${tmF(gp.y)}" r="13" style="stroke:${band}"/><text x="${tmF(gp.x)}" y="${tmF(gp.y)}">${gp.rows.length}</text></g>`;
  });

  const name = KG.components[ci][1], short = name.length > 26 ? name.slice(0, 25) + '…' : name;
  top += `<g class="tm-card"><rect x="${card.x}" y="${card.y}" width="${cw}" height="${card.h}" rx="8" style="stroke:${band}"/>`
    + `<text class="t1" x="${card.x + 14}" y="${card.y + 21}">${esc(short)}</text>`
    + `<text class="t2" x="${card.x + 14}" y="${card.y + 40}">Exposure ${e.score}${W >= 420 ? ` (${e.band.toLowerCase()})` : ''} · ${e.links.length} suppliers</text></g>`;
  return `<svg viewBox="0 0 ${W} ${H}" role="group" aria-label="Map of the suppliers of ${esc(name)}">`
    + `<defs><marker id="tmArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="var(--muted)" stroke-width="1.5"/></marker></defs>`
    + `<g>${land}</g><g>${regs}</g><g>${ties}</g><g>${lines}</g><g>${hq}</g><g>${pins}</g><g>${top}</g></svg>`;
}

function tmMark(r, band) {
  const st = !r.pin ? 'border:1.5px dashed var(--muted)' : r.g === 0 ? `background:${band};color:var(--surface)`
    : r.g === 1 ? `box-shadow:inset 0 0 0 2px ${band}` : `border:1.5px dashed ${band}`;
  return `<i class="tm-mk" style="${st}">${r.n}</i>`;
}

function tmList(M) {
  const band = bandVar(M.e.band), shown = M.rows.filter(r => r.shown).length, off = M.rows.filter(r => r.shown && !r.pin).length;
  return `<div class="tm-list">${M.rows.map(r => {
    const where = !r.shown ? 'Hidden by the evidence filter' : r.pin ? `${r.pin.town}${r.pin.approx ? ' (county only)' : ''}` : `Not on map · ${r.off}`;
    return `<div class="tm-row ${traceSel === 's' + r.si ? 'sel' : ''} ${r.shown ? '' : 'dim'}" data-n="s${r.si}" tabindex="0" role="button">${tmMark(r, band)}<span><b>${esc(G.S[r.si][0])}</b><small>${esc(where)} · ${LatticeCore.GRADE[r.g].toLowerCase()}</small></span></div>`;
  }).join('')}${off ? `<p class="note">${off} of ${shown} suppliers ${off === 1 ? 'is' : 'are'} not on the map.</p>` : ''}</div>`;
}

function tmLegend(band) {
  const ln = (w, dash) => `<svg width="28" height="10" aria-hidden="true"><line x1="1" y1="5" x2="27" y2="5" stroke="${band}" stroke-width="${w}"${dash ? ' stroke-dasharray="5 3"' : ''}/></svg>`;
  return `<div class="legend tm-legend"><span>${ln(4)}explicit</span><span>${ln(3.7)}declared</span><span>${ln(2.8, 1)}inferred</span>`
    + `<span>Pin size: turnover, &lt;€2m to &gt;€50m</span><span><i class="tm-mk" style="border:2px solid ${band}">3</i>several in one place</span>`
    + `<span><i class="tm-mk" style="border:1px dashed ${band}"></i>cluster, approximate</span><span><i class="tm-mk tm-hqmk">HQ</i>overseas HQ</span></div>`
    + `<p class="note">Lines show who supplies the part, not shipping routes. Town positions: GeoNames (CC BY 4.0). Coastline: Natural Earth.</p>`;
}

function tmInner(ci) {
  if (!HAS_GEO) return `<div class="empty">The map needs wind/geo.json, which is not in this build. The diagram shows the same supply base.</div>`;
  const svg = tmSvg(ci);
  return `<div class="tm-grid"><div class="tm-mapw">${svg}</div>${tmList(TM.model)}</div>${tmLegend(bandVar(TM.model.e.band))}`;
}

// Dim every link except the hovered or selected supplier's (key 's<si>') or cluster's ('k<c>'); show its ties.
function tmLight(w, key) {
  const s = key && key[0] === 's' ? key : null, k = key && key[0] === 'k' ? key.slice(1) : null;
  w.querySelectorAll('.tm-ln').forEach(p => p.classList.toggle('dim', !!(s || k) && !(s ? p.dataset.n === s : p.dataset.c.includes(` ${k} `))));
  w.querySelectorAll('.tm-tie').forEach(t => t.classList.toggle('on', !!(s || k) && (s ? t.dataset.n === s : t.dataset.k === k)));
  w.querySelectorAll('.tm-row').forEach(r => r.classList.toggle('lit', !!s && r.dataset.n === s));
}

function wireTraceMap(m, ci) {
  const w = m.querySelector('#tmapw'); if (!w || !HAS_GEO) return;
  const hit = t => t && t.closest('[data-n],[data-k],[data-q],[data-g]');
  const keyOf = t => t.dataset.n || (t.dataset.k != null ? 'k' + t.dataset.k : t.dataset.q != null ? 'n' + t.dataset.q : 'g' + t.dataset.g);
  // re-render, then put focus back on the same kind of element that was acted on (list row or map mark)
  const redraw = (focusKey, asRow) => {
    w.innerHTML = tmInner(ci); $('#tdetail').innerHTML = traceDetail(ci); tmLight(w, traceSel);
    if (focusKey) {
      const same = [...w.querySelectorAll('[tabindex]')].filter(x => keyOf(x) === focusKey);
      const f = same.find(x => x.classList.contains('tm-row') === !!asRow) || same[0];
      if (f) f.focus();
    }
  };
  const act = t => {
    const k = keyOf(t), asRow = t.classList.contains('tm-row');
    if (k[0] === 'g') { TM.fan = +k.slice(1); return redraw('s' + k.slice(1)); }
    traceSel = k;
    const r = k[0] === 's' && TM.model.rows.find(x => 's' + x.si === k);
    if (r && r.group && r.group.rows.length > 1) TM.fan = r.group.key;
    redraw(k, asRow);
    if (innerWidth < 1100) $('#tdetail').scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  w.addEventListener('click', ev => {
    const t = hit(ev.target); if (t) return act(t);
    if (TM.fan != null && ev.target.closest('svg')) { TM.fan = null; redraw(); }
  });
  w.addEventListener('keydown', ev => {
    if (ev.key === 'Escape' && TM.fan != null) { const key = TM.fan; TM.fan = null; return redraw('g' + key); }
    const t = hit(ev.target);
    if (t && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); act(t); }
  });
  w.addEventListener('mouseover', ev => { const t = hit(ev.target); tmLight(w, t ? keyOf(t) : traceSel); });
  w.addEventListener('mouseleave', () => { tmLight(w, traceSel); hideTip(); });
  w.addEventListener('mousemove', ev => {
    const t = ev.target.closest('.tm-pin'); if (!t) return hideTip();
    const r = TM.model.rows.find(x => 's' + x.si === t.dataset.n), s = G.S[r.si];
    showTip(ev, `<b>${esc(s[0])}</b><br>${esc(r.pin.town)}${r.pin.approx ? ' (county only)' : ''} · ${LatticeCore.GRADE[r.g].toLowerCase()}`
      + `<br>${s[2] >= 0 ? 'Turnover ' + TURNOVER[s[2]] : 'Turnover n/a'} · ${s[4] < 0 ? 'HQ not stated' : 'HQ ' + esc(KG.countries[s[4]])}`);
  });
  // one viewBox unit per pixel: re-render once if the map column is not the width we drew for;
  // and a supplier selected before the map opened (Diagram mode, another view) is shown fanned out
  const col = w.querySelector('.tm-mapw'), px = col ? Math.round(col.clientWidth) : 0;
  const resize = px > 200 && Math.abs(px - TM.W) > 24;
  if (resize) { TM.W = px; tmModel(ci); }        // regroup at the real width before choosing which group to open
  const sel = TM.model && TM.model.rows.find(r => r.end && traceSel === 's' + r.si);
  const open = sel && sel.group.rows.length > 1 && !sel.group.open;
  if (open) TM.fan = sel.group.key;
  if (resize || open) redraw(); else tmLight(w, traceSel);
}

// Detail-panel block explaining one supply link (both Trace modes).
function linkBlock(ci, si) {
  const l = G.compLinks[ci].find(x => x.si === si); if (!l) return '';
  const s = G.S[si], p = HAS_GEO ? GeoCore.place(si, KG, GEO, TM_SITES) : null;
  const cls = tmNat(si) ? 'All clusters' : s[5].map(c => KG.clusters[c]).join(', ') || 'None stated';
  const pin = !p ? 'Map data not in this build' : p.pin
    ? `${p.pin.town}${p.pin.approx ? ' (county only)' : ''}, ${p.pin.hqSite ? 'its HQ site' : 'its first listed site'}` : `Not on the map: ${p.off}`;
  const row = (k, v) => `<div class="drv"><span class="note">${k}</span><span>${v}</span><span></span></div>`;
  return `<div class="linkblk"><div class="tag">Supply link</div><h3>${esc(KG.components[ci][1])} ← ${esc(s[0])}</h3>${gradeBadge(l.g)}
    <h2 style="margin-top:12px">Why this line is drawn</h2><p class="ev">${esc(l.ev)}</p>
    ${row('Pin', esc(pin))}${row('Line', `${l.g === 2 ? 'Dashed' : 'Solid'}, confidence ${l.conf}`)}
    ${row('Pin size', s[2] >= 0 ? `Turnover ${TURNOVER[s[2]]}` : 'Turnover n/a')}
    ${row('HQ country', esc(s[4] < 0 ? 'HQ not stated' : KG.countries[s[4]]))}${row('Clusters', esc(cls))}</div>`;
}

// Author: Koorosh Aslansefat
/* Supply landscape: component × cluster heatmap, lifecycle Sankey and a schematic cluster tile map. */
let landCell = null;
const CL_SHORT = c => c.replace('Offshore Energy Alliance (OEA)', 'OEA');
const TILE_POS = { 'North Scotland': [1, 2], 'Offshore Energy Alliance (OEA)': [1, 4], 'Forth & Tay': [2, 2], 'North East': [2, 3],
  'Celtic Sea': [3, 1], 'Humber': [3, 3], 'East Anglia': [3, 4], 'Solent': [4, 2] };

function landSupIn(ci, k) { return COMP_EXP[ci].links.map(l => l.si).filter(si => k < 0 ? !G.S[si][5].length : G.S[si][5].includes(k)); }

function landHeat() {
  const K = [...KG.clusters.keys(), -1];
  const maxTot = Math.max(...COMP_EXP.map(e => e.links.length));
  const colTot = K.map(k => new Set(KG.links.map(l => l[0]).filter(si => k < 0 ? !G.S[si][5].length : G.S[si][5].includes(k))).size);
  let body = '';
  SUBS.forEach(sid => {
    body += `<tr class="grp"><td colspan="${K.length + 2}"><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${subVar(sid)};margin-right:6px"></i>${esc(SUBNAME[sid])}</td></tr>`;
    KG.components.forEach((c, ci) => {
      if (c[2] !== sid) return;
      const tot = COMP_EXP[ci].links.length;
      body += `<tr><td class="rn">${esc(c[1])}</td>${K.map(k => { const n = landSupIn(ci, k).length;
        return `<td class="c ${n ? '' : 'z'}" data-cell="${ci}:${k}" style="${n ? `background:${heatVar(n)};color:${heatInk(n)}` : ''}">${n || '·'}</td>`; }).join('')}
        <td class="tot"><div style="display:flex;gap:6px;align-items:center"><div class="bar" style="flex:1;min-width:40px"><i style="width:${tot / maxTot * 100}%;background:var(--muted)"></i></div><span class="num">${tot}</span></div></td></tr>`;
    });
  });
  return `<div class="scroll"><table class="heat"><thead><tr><th></th>${K.map(k => `<th title="${k < 0 ? 'No cluster stated' : esc(KG.clusters[k])}">${k < 0 ? 'None stated' : esc(CL_SHORT(KG.clusters[k]))}</th>`).join('')}<th>All suppliers</th></tr></thead>
    <tbody>${body}<tr><td class="rn note" style="padding-top:8px">Suppliers with any component</td>${colTot.map(n => `<td class="num note" style="text-align:center;padding-top:8px">${n}</td>`).join('')}<td></td></tr></tbody></table></div>`;
}

function landCellPanel() {
  if (!landCell) return `<p class="note">Select a cell to list the suppliers behind it.</p>`;
  const [ci, k] = landCell, sups = landSupIn(ci, k);
  return `<h3 style="font:700 16px var(--f-display);margin:0 0 4px">${esc(KG.components[ci][1])} · ${k < 0 ? 'no cluster stated' : esc(KG.clusters[k])}</h3>
    <div class="tag">${sups.length} supplier${sups.length === 1 ? '' : 's'}</div>
    ${sups.length ? `<ul style="margin:8px 0 0;padding-left:18px">${sups.map(si => `<li>${idl('s', si, G.S[si][0])} ${gradeBadge(G.compLinks[ci].find(l => l.si === si).g)}</li>`).join('')}</ul>` : '<p class="note">None.</p>'}
    <p class="note" style="margin-top:8px">${idl('c', KG.components[ci][0], 'Trace this component')}${k >= 0 ? ` · ${idl('k', k, 'Simulate losing the cluster')}` : ''}</p>`;
}

function landTiles() {
  const S = KG.suppliers, clustered = S.filter(s => s[5].length).length;
  const supSubs = si => { const ss = [...new Set(G.supLinks[si].map(l => KG.components[l.ci][2]))]; return ss.length ? ss : ['SVC']; };
  return `<div class="tilemap">${KG.clusters.map((c, k) => {
    const members = S.map((s, si) => si).filter(si => S[si][5].includes(k));
    const mix = [...SUBS, 'SVC'].map(sid => [sid, members.filter(si => supSubs(si).includes(sid)).length]);
    const [r, col] = TILE_POS[c] || [null, null];
    return `<div class="tile ${c.includes('OEA') ? 'net' : ''}" data-go="k:${k}" tabindex="0" role="link" style="${r ? `--r:${r};--c:${col}` : ''}">
      <span class="nm">${esc(c.includes('OEA') ? 'Offshore Energy Alliance (network)' : c)}</span>
      <div style="display:flex;align-items:baseline;gap:6px"><b>${members.length}</b><span class="note">${pct(members.length, clustered)}%</span></div>
      <div class="stack">${mix.map(([sid, n]) => n ? `<i style="flex:${n};background:${subVar(sid)}" title="${sid === 'SVC' ? 'No component evidence' : esc(SUBNAME[sid])}: ${n}"></i>` : '').join('')}</div></div>`;
  }).join('')}</div>`;
}

function landSankey(el) {
  if (!(window.d3 && d3.sankey)) { el.innerHTML = '<div class="empty">The flow diagram needs the D3 library, which did not load. The heatmap above shows the same supply base.</div>'; return; }
  const S = KG.suppliers, scopeIds = [...SUBS, 'SVC'];
  const nodes = [...KG.phases.map((p, i) => ({ id: `p${i}`, name: p, kind: 'phase' })),
    ...scopeIds.map(s => ({ id: `s${s}`, name: s === 'SVC' ? 'No component evidence' : SUBNAME[s], kind: 'scope', sid: s })),
    ...KG.clusters.map((c, k) => ({ id: `k${k}`, name: CL_SHORT(c), kind: 'cluster' })), { id: 'k-1', name: 'No cluster stated', kind: 'cluster' }];
  const acc = {};
  const add = (a, b, w, sid) => { const key = a + '>' + b; (acc[key] = acc[key] || { source: a, target: b, value: 0, sid }).value += w; };
  let total = 0;
  S.forEach((s, si) => {
    if (!s[7].length) return;
    const sc = [...new Set(G.supLinks[si].map(l => KG.components[l.ci][2]))]; const scopes = sc.length ? sc : ['SVC'];
    const cl = s[5].length ? s[5] : [-1];
    const w = 1 / (s[7].length * scopes.length * cl.length); total += 1;
    s[7].forEach(p => scopes.forEach(x => cl.forEach(k => { add(`p${p}`, `s${x}`, w, x); add(`s${x}`, `k${k}`, w, x); })));
  });
  const W = 920, H = 560;
  const sk = d3.sankey().nodeId(d => d.id).nodeWidth(12).nodePadding(17).nodeSort(null).extent([[1, 8], [W - 1, H - 8]]);
  const g = sk({ nodes: nodes.map(d => ({ ...d })), links: Object.values(acc).map(d => ({ ...d })) });
  const lp = d3.sankeyLinkHorizontal();
  const nodeFill = d => d.kind === 'scope' ? subVar(d.sid) : d.kind === 'phase' ? 'var(--ink)' : 'var(--muted)';
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;min-width:720px;height:auto" role="img" aria-label="Lifecycle phase to subsystem to cluster flows">
    ${g.links.map((d, i) => `<path class="sankey-link" data-i="${i}" d="${lp(d)}" style="stroke:${subVar(d.sid)};stroke-width:${Math.max(1, d.width).toFixed(1)};stroke-opacity:.38"/>`).join('')}
    ${g.nodes.map(d => `<g class="sankey-node"><rect x="${d.x0}" y="${d.y0}" width="${d.x1 - d.x0}" height="${Math.max(1, d.y1 - d.y0)}" rx="2" style="fill:${nodeFill(d)}"/>
      <text x="${d.x0 < W / 2 ? d.x1 + 6 : d.x0 - 6}" y="${(d.y0 + d.y1) / 2}" dominant-baseline="central" text-anchor="${d.x0 < W / 2 ? 'start' : 'end'}">${esc(d.name)} <tspan style="fill:var(--muted);font-family:var(--f-mono);font-size:10px">${d.value.toFixed(0)}</tspan></text></g>`).join('')}
  </svg>`;
  el.dataset.total = total.toFixed(3);
  el.dataset.sources = g.nodes.filter(d => d.kind === 'phase').reduce((a, d) => a + d.value, 0).toFixed(3);
  const svg = el.querySelector('svg');
  svg.addEventListener('mousemove', e => {
    const p = e.target.closest('.sankey-link');
    svg.querySelectorAll('.sankey-link').forEach(x => x.style.strokeOpacity = p ? (x === p ? .85 : .15) : .38);
    if (!p) return hideTip();
    const d = g.links[+p.dataset.i];
    showTip(e, `<b>${esc(d.source.name)} → ${esc(d.target.name)}</b><br>${d.value.toFixed(1)} suppliers (weighted)`);
  });
  svg.addEventListener('mouseleave', () => { hideTip(); svg.querySelectorAll('.sankey-link').forEach(x => x.style.strokeOpacity = .38); });
}

VIEW_FNS.landscape = function (m) {
  const S = KG.suppliers, svc = S.filter((s, si) => !G.supLinks[si].length).length, noPhase = S.filter(s => !s[7].length).length;
  m.innerHTML = `<h1>${pct(svc, S.length)}% of offshore suppliers show no turbine-component capability in the directory</h1>
    <p class="sub">These firms may still offer services, tooling, vessels or other inputs; the directory simply links them to no turbine part. Below: where component capability sits by regional cluster, and how all suppliers spread across lifecycle phases. Counts are suppliers; a supplier in several clusters counts in each.</p>
    <div class="grid two land">
      <section class="panel"><h2>Component × cluster</h2>${heatLegend()}<div style="margin-top:10px">${landHeat()}</div></section>
      <div style="display:flex;flex-direction:column;gap:16px;min-width:0">
        <section class="panel"><h2>Regional clusters · schematic</h2>${landTiles()}
          <div class="legend" style="margin-top:10px">${[...SUBS, 'SVC'].map(s => `<span><i style="background:${subVar(s)}"></i>${s === 'SVC' ? 'No component evidence' : esc(SUBNAME[s])}</span>`).join('')}</div>
          <p class="note">Schematic: tile positions are approximate. Bars show each cluster's suppliers by what they make. Select a tile to simulate losing it.</p></section>
        <section class="panel" id="lcell">${landCellPanel()}</section>
      </div>
    </div>
    <section class="panel" style="margin-top:16px"><h2>Lifecycle phase → what they supply → cluster</h2>
      <div class="legend">${[...SUBS, 'SVC'].map(s => `<span><i style="background:${subVar(s)}"></i>${s === 'SVC' ? 'No component evidence' : esc(SUBNAME[s])}</span>`).join('')}</div>
      <div class="scroll" id="lsankey"></div>
      <p class="note">Each supplier counts once in total, split evenly across its phases, subsystems and clusters, so the flows add up. Phases come from declared capabilities and site categories${noPhase ? `; the ${noPhase} supplier${noPhase === 1 ? '' : 's'} with no phase stated ${noPhase === 1 ? 'is' : 'are'} left out, so the diagram shows ${fmt(S.length - noPhase)} of ${fmt(S.length)}` : ''}.</p></section>`;
  landSankey($('#lsankey'));
  const tbl = m.querySelector('.heat');
  tbl.addEventListener('click', e => { const c = e.target.closest('[data-cell]'); if (!c) return; landCell = c.dataset.cell.split(':').map(Number); $('#lcell').innerHTML = landCellPanel(); });
  tbl.addEventListener('mousemove', e => {
    const c = e.target.closest('[data-cell]'); if (!c) return hideTip();
    const [ci, k] = c.dataset.cell.split(':').map(Number);
    showTip(e, `<b>${esc(KG.components[ci][1])}</b><br>${k < 0 ? 'No cluster stated' : esc(KG.clusters[k])}: ${landSupIn(ci, k).length} suppliers`);
  });
  tbl.addEventListener('mouseleave', hideTip);
};

// Author: Koorosh Aslansefat
/* What if…: remove part of the supplier base, recompute every component, show before → after. */
let scSel = null;

function scDumbbell(base, after, comps) {
  const max = Math.max(5, ...comps.map(ci => base.comps[ci].links.length));
  const step = max > 20 ? 5 : max > 10 ? 2 : 1, top = Math.ceil(max / step) * step;
  const L = 200, R = 600, RH = 22, H = 34 + comps.length * RH;
  const x = v => L + (R - L) * v / top;
  let s = '';
  for (let t = 0; t <= top; t += step) s += `<line x1="${x(t)}" y1="22" x2="${x(t)}" y2="${H - 4}" style="stroke:var(--line);stroke-width:1"/><text x="${x(t)}" y="14" text-anchor="middle" class="num" style="font-size:10px;fill:var(--muted)">${t}</text>`;
  comps.forEach((ci, i) => {
    const b = base.comps[ci].links.length, a = after.comps[ci].links.length, y = 34 + i * RH;
    const col = bandVar(after.comps[ci].band), sel = scSel === ci;
    s += `<g class="row" data-ci="${ci}" tabindex="0" role="button"><rect x="0" y="${y - 11}" width="640" height="${RH}" style="fill:${sel ? 'var(--surface2)' : 'transparent'}"/>
      <text x="${L - 12}" y="${y}" dominant-baseline="central" text-anchor="end" style="font-size:11.5px;fill:var(--ink)">${esc(KG.components[ci][1])}</text>
      <line x1="${x(a)}" y1="${y}" x2="${x(b)}" y2="${y}" style="stroke:var(--muted);stroke-width:2"/>
      <circle cx="${x(b)}" cy="${y}" r="5" style="fill:var(--surface);stroke:var(--muted);stroke-width:2"/>
      <circle cx="${x(a)}" cy="${y}" r="5" style="fill:${col};stroke:var(--surface);stroke-width:2"/>
      <text x="${R + 14}" y="${y}" dominant-baseline="central" class="num" style="font-size:11px;fill:var(--muted)">${b === a ? b : `${b} → ${a}`}</text></g>`;
  });
  return `<svg class="dumb" viewBox="0 0 660 ${H}" style="width:100%;min-width:560px;height:auto" role="img" aria-label="Suppliers per component before and after">${s}</svg>`;
}

VIEW_FNS.scenario = function (m) {
  const sc = STATE.scenario, v = STATE.variant;
  const removed = LatticeCore.removedBy(G, sc), base = BASE[v], after = LatticeCore.rollup(G, v, removed);
  const active = sc.cluster >= 0 || sc.overseas || sc.micro || sc.floatingOnly;
  const comps = KG.components.map((c, i) => i).filter(ci => LatticeCore.applies(KG.components[ci], v));
  const newlyThin = comps.filter(ci => !base.comps[ci].rules.R2 && after.comps[ci].rules.R2);
  const zeroAfter = comps.filter(ci => after.comps[ci].empty), zeroBase = comps.filter(ci => base.comps[ci].empty);
  const order = comps.slice().sort((a, b) => (base.comps[b].links.length - after.comps[b].links.length) - (base.comps[a].links.length - after.comps[a].links.length) || after.comps[b].score - after.comps[a].score);
  if (scSel == null || !comps.includes(scSel)) scSel = order[0];
  const parts = [sc.cluster >= 0 && `${KG.clusters[sc.cluster]} lost`, sc.overseas && 'overseas-HQ suppliers removed', sc.micro && 'micro firms (<€2m) removed', sc.floatingOnly && 'floating-capable suppliers only'].filter(Boolean);
  const title = active ? parts.join(' · ') : 'No disruption selected';
  m.innerHTML = `<h1>What happens if…</h1>
    <p class="sub">Remove part of the supplier base and every component is re-scored with the same core rules. A supplier counts as lost to a cluster only when that is its only cluster. R6 then looks for alternate sources in what remains.</p>
    <div class="toolbar">
      <div class="field"><label for="scl">Lose a cluster</label><select id="scl"><option value="-1">None</option>${KG.clusters.map((c, k) => `<option value="${k}" ${k === sc.cluster ? 'selected' : ''}>${esc(c)}</option>`).join('')}</select></div>
      <label class="check"><input type="checkbox" id="sov" ${sc.overseas ? 'checked' : ''}>Remove overseas-HQ suppliers</label>
      <label class="check"><input type="checkbox" id="smi" ${sc.micro ? 'checked' : ''}>Remove micro firms (&lt;€2m)</label>
      <label class="check"><input type="checkbox" id="sfl" ${sc.floatingOnly ? 'checked' : ''}>Floating-capable suppliers only</label>
      <div class="field"><span class="lbl">Turbine</span><div class="seg" role="group"><button data-sv="fixed" aria-pressed="${v === 'fixed'}">Fixed-bottom</button><button data-sv="floating" aria-pressed="${v === 'floating'}">Floating</button></div></div>
    </div>
    <div class="panel"><h2>${esc(title)}</h2>
      <div class="stat3">
        <div><b>${fmt(removed.size)}</b><span>suppliers removed · ${pct(removed.size, KG.suppliers.length)}% of the base</span></div>
        <div><b style="color:${newlyThin.length ? 'var(--sev)' : 'inherit'}">${newlyThin.length}</b><span>component${newlyThin.length === 1 ? '' : 's'} newly thin (R2)</span></div>
        <div><b>${zeroAfter.length}</b><span>component${zeroAfter.length === 1 ? '' : 's'} with no supplier${zeroAfter.length > zeroBase.length ? ` · +${zeroAfter.length - zeroBase.length} vs today` : ''}</span></div>
        <div><b>${base.turbine} → ${after.turbine}</b><span>${v === 'fixed' ? 'fixed-bottom' : 'floating'} turbine exposure (R3) ${pill(LatticeCore.bandOf(after.turbine))}</span></div>
      </div>
      ${active ? '' : '<p class="note">Choose a cluster or a filter above to see the effect. Until then before and after are the same.</p>'}
      <div class="grid two">
        <div><h2>Suppliers per component, before → after</h2>
          <div class="legend"><span><i style="background:var(--surface);box-shadow:inset 0 0 0 2px var(--muted);border-radius:50%"></i>Today</span><span><i style="background:var(--sev);border-radius:50%"></i>After, coloured by new exposure band</span></div>
          <div class="scroll" id="sdumb">${scDumbbell(base, after, order)}</div></div>
        <div style="min-width:0"><h2>Turbine after the disruption</h2>
          <div id="smini">${turbineSVG({ variant: v, compact: true, selected: scSel, colorOf: ci => `color-mix(in srgb, ${bandVar(after.comps[ci].band)} 58%, var(--surface))`, strokeOf: ci => bandVar(after.comps[ci].band) })}</div>
          <h2 style="margin-top:14px">Alternate sources (R6)</h2>
          ${newlyThin.length ? newlyThin.map(ci => { const alt = LatticeCore.alternates(G, ci, removed, sc).slice(0, 3);
            return `<div class="rule"><b style="font-family:var(--f-body);color:var(--ink)">${esc(KG.components[ci][1])}</b> · ${alt.length ? alt.map(si => idl('s', si, G.S[si][0])).join(', ') : '<span class="note">No alternate in the remaining base</span>'}</div>`; }).join('')
            : `<p class="note">${active ? 'No component drops to thin supply, so no alternates are needed.' : 'Alternates appear here for components that become thin.'}</p>`}
          <div class="panel detail" style="margin-top:14px;background:var(--surface2)" id="sdetail">${compDetail(scSel, removed)}</div>
        </div>
      </div></div>`;
  const upd = () => { STATE.scenario = { cluster: +$('#scl').value, overseas: $('#sov').checked, micro: $('#smi').checked, floatingOnly: $('#sfl').checked }; VIEW_FNS.scenario(m); };
  ['#scl', '#sov', '#smi', '#sfl'].forEach(id => $(id).onchange = upd);
  m.querySelectorAll('[data-sv]').forEach(b => b.onclick = () => { STATE.variant = b.dataset.sv; VIEW_FNS.scenario(m); });
  const pick = ci => { scSel = ci; m.querySelectorAll('.dumb .row').forEach(r => r.querySelector('rect').style.fill = +r.dataset.ci === ci ? 'var(--surface2)' : 'transparent');
    m.querySelectorAll('#smini [data-c]').forEach(g => g.classList.toggle('sel', CI[g.dataset.c] === ci)); $('#sdetail').innerHTML = compDetail(ci, removed); if (innerWidth < 1100) $('#sdetail').scrollIntoView({ behavior: 'smooth', block: 'start' }); };
  m.querySelectorAll('.dumb .row').forEach(r => { r.onclick = () => pick(+r.dataset.ci); r.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(+r.dataset.ci); } }; });
  $('#smini').addEventListener('click', e => { const g = e.target.closest('[data-c]'); if (g) pick(CI[g.dataset.c]); });
};

// Author: Koorosh Aslansefat
/* Ask the graph: deterministic answers from KG facts and core rules, each with its dependency trail.
   In production an LLM would phrase the narrative; it never invents the facts. */
const askLog = [];
const trail = arr => `<div class="trail">${arr.map((x, i) => i % 2 ? `<span class="r">${esc(x)}</span>` : `<span class="s">${esc(x)}</span>`).join('')}</div>`;
const evid = t => `<p class="note">Evidence: ${t}. Source: UK Offshore Wind Directory export.</p>`;
// Component aliases match whole words only; generic words ("chain", "bearing", "turbine") need their qualifier.
const ASK_ALIAS = {
  blades: /\bblades?\b/, hub_pitch: /\b(rotor hubs?|hubs?|pitch systems?)\b/, nacelle: /\bnacelles?\b/, main_bearing: /\bmain bearings?\b/,
  gearbox: /\bgear ?box(es)?\b/, generator: /(?<!diesel )\bgenerators?\b/, converter: /\b(power )?converters?\b/, turbine_trafo: /\bturbine transformers?\b/,
  yaw: /\byaw( systems?)?\b/, cms: /\bcondition monitoring\b|\bscada\b|\bturbine controls?\b/, tower: /\btowers?\b/, tower_internals: /\btower internals\b/,
  secondary_steel: /\bsecondary steel\b/, fasteners: /\b(fasteners?|bolting)\b/, fixed_fnd: /\bfixed(-bottom)? foundations?\b/, monopile: /\bmonopiles?\b/,
  jacket: /\bjackets?\b/, tp: /\btransition pieces?\b/, suction: /\bsuction (buckets?|piles?|anchors?)\b/,
  floating_sub: /\bfloating (substructures?|platforms?|foundations?)\b|\bsemi-?subs?(mersibles?)?\b/, corrosion: /\bcorrosion\b|\bcathodic\b/,
  scour: /\bscour\b/, mooring: /\bmooring systems?\b/, chain: /\bmooring (chains?|lines?|ropes?)\b|\banchor chains?\b/, anchors: /\banchors?\b/,
  connectors: /\bmooring connectors?\b|\bshackles?\b/, buoyancy: /\bbuoyancy\b/, cables: /\bsubsea (power )?cables?\b|\bpower cables?\b|\bcables?\b/,
  array_cable: /\barray cables?\b/, export_cable: /\bexport cables?\b/, cable_acc: /\bcable (accessories|protection|joints?)\b|\bbend stiffeners?\b/,
  offshore_sub: /\boffshore substations?\b/, hv_equip: /\bhvdc\b|\bswitchgear\b|\bhv equipment\b/, onshore_sub: /\bonshore substations?\b/,
};
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const topTier1 = (() => { let best = -1, n = -1; KG.suppliers.forEach((s, si) => { if ((s[1] & 1) && G.supLinks[si].length > n) { n = G.supLinks[si].length; best = si; } }); return best; })();
const ASK_SUG = ['Which components have no directory supplier?', 'Where is floating wind thinnest?', 'Who supplies mooring chain?',
  'What if North Scotland is lost?', 'How concentrated is the supply base?', `Tell me about ${KG.suppliers[topTier1][0]}`];

function matchCluster(q) {
  const alias = KG.clusters.map((c, k) => [k, [c.toLowerCase(), ...(c.includes('OEA') ? ['oea', 'offshore energy alliance'] : []), ...(c === 'Forth & Tay' ? ['forth', 'tay'] : []), ...(c === 'Celtic Sea' ? ['celtic'] : [])]]);
  const hit = alias.find(([, names]) => names.some(n => new RegExp(`\\b${reEsc(n)}\\b`).test(q)));
  return hit ? hit[0] : -1;
}
function matchComp(q) {
  let best = -1, len = 0;
  KG.components.forEach((c, ci) => { const m = q.match(ASK_ALIAS[c[0]]); if (m && m[0].length > len) { len = m[0].length; best = ci; } });
  return best;
}
function matchSupplier(q) {
  let best = -1, len = 0;
  KG.suppliers.forEach((s, si) => {
    const nm = s[0].toLowerCase().replace(/\b(ltd|limited|plc|llp)\b\.?/g, '').replace(/\s+/g, ' ').trim();
    if (nm.length >= 5 && nm.length > len && new RegExp(`(^|[^a-z0-9])${reEsc(nm)}($|[^a-z0-9])`).test(q)) { len = nm.length; best = si; }
  });
  return best;
}

function answer(raw) {
  const q = raw.toLowerCase();
  const si = matchSupplier(q);
  if (si >= 0 && (/tell me|who is|about|profile/.test(q) || matchComp(q) < 0)) {
    return `<h4>${esc(G.S[si][0])}</h4>${trail(['Supplier', 'supplies', `${G.supLinks[si].length} components`, 'memberOf', `${G.S[si][5].length} clusters`])}
      <div class="detail">${supplierDetail(si).replace(/<h3>.*?<\/h3>/, '')}</div>${evid('suppliers, sites and links for this organisation')}`;
  }
  const k = matchCluster(q);
  if (k >= 0 && /lost|lose|losing|without|if |close|shut|disrupt/.test(q)) {
    const sc = { cluster: k, overseas: false, micro: false, floatingOnly: false }, rm = LatticeCore.removedBy(G, sc);
    const af = LatticeCore.rollup(G, 'fixed', rm), thin = af.comps.filter((e, ci) => LatticeCore.applies(KG.components[ci], 'fixed') && e.rules.R2 && !COMP_EXP[ci].rules.R2);
    return `<h4>Losing ${esc(KG.clusters[k])} removes ${rm.size} suppliers</h4>${trail([KG.clusters[k], 'memberOf⁻¹', `${rm.size} suppliers`, 'supplies', 'components', 'R2'])}
      <p>For the fixed-bottom turbine, exposure moves from <b>${BASE.fixed.turbine}</b> to <b>${af.turbine}</b>. ${thin.length ? `${thin.length} components become thin:` : 'No component becomes newly thin.'}</p>
      ${thin.length ? `<ul>${thin.map(e => `<li>${idl('c', KG.components[e.ci][0], KG.components[e.ci][1])}: ${COMP_EXP[e.ci].links.length} → ${e.links.length} suppliers</li>`).join('')}</ul>` : ''}
      <p>${idl('k', k, 'Open in the simulator')}</p>${evid('Regional Cluster(s) on each supplier; only suppliers whose sole cluster is lost are removed')}`;
  }
  if (/no (uk )?suppl|zero|missing|gap|nobody|none/.test(q)) {
    const z = COMP_EXP.filter(e => e.empty);
    return `<h4>${z.length} components have no supplier linked in this snapshot</h4>${trail(['TurbineSystem', 'hasPart', 'Component', 'supplies⁻¹', '∅'])}
      <ul>${z.map(e => `<li>${idl('c', KG.components[e.ci][0], KG.components[e.ci][1])} <span class="note">${esc(SUBNAME[KG.components[e.ci][2]])}</span></li>`).join('')}</ul>
      <p class="note">Most are nacelle internals. A missing link means no evidence in the directory, not proof that no UK firm can make the part.</p>${evid('site categories, organisation categories and descriptions for all 885 suppliers')}`;
  }
  if (/float/.test(q)) {
    const fl = COMP_EXP.filter(e => KG.components[e.ci][3] === 'floating').sort((a, b) => b.score - a.score);
    const share = pct(KG.suppliers.filter(s => s[6] & 4).length, KG.suppliers.length);
    return `<h4>Floating wind is thinnest in ${esc(KG.components[fl[0].ci][1].toLowerCase())}</h4>${trail(['TurbineSystem (floating)', 'hasPart', 'Station-keeping', 'R5'])}
      <p>${share}% of all suppliers declare floating capability. Floating-only components, most exposed first:</p>
      <ul>${fl.map(e => `<li>${idl('c', KG.components[e.ci][0], KG.components[e.ci][1])} · exposure ${e.score} ${pill(e.band)} · ${e.links.length} suppliers${e.rules.R5 ? ' · <span class="rule-chip">R5</span>' : ''}</li>`).join('')}</ul>
      <p>Floating turbine exposure is <b>${BASE.floating.turbine}</b> against <b>${BASE.fixed.turbine}</b> for fixed-bottom.</p>${evid('Wind Type declarations and supply links')}`;
  }
  if (/concentrat|cluster|where are|region/.test(q) && k < 0) {
    const S = KG.suppliers, clustered = S.filter(s => s[5].length).length;
    const shares = KG.clusters.map((c, i) => [c, S.filter(s => s[5].includes(i)).length]).sort((a, b) => b[1] - a[1]);
    const r4 = COMP_EXP.filter(e => e.rules.R4);
    return `<h4>${esc(shares[0][0])} holds ${pct(shares[0][1], clustered)}% of clustered suppliers</h4>${trail(['Supplier', 'memberOf', 'RegionalCluster', 'R4'])}
      <ul>${shares.slice(0, 4).map(([c, n]) => `<li>${esc(c)}: ${n} suppliers (${pct(n, clustered)}%)</li>`).join('')}</ul>
      <p>${r4.length} components trip R4 (≥ 60 % of their clustered suppliers in one cluster): ${r4.map(e => idl('c', KG.components[e.ci][0], KG.components[e.ci][1])).join(', ')}.</p>${evid('Regional Cluster(s)')}`;
  }
  const ci = matchComp(q);
  if (ci >= 0) {
    const e = COMP_EXP[ci], ls = e.links.slice().sort((a, b) => a.g - b.g);
    return `<h4>${e.empty ? 'No directory supplier is evidenced for' : `${e.links.length} directory suppliers evidence`} ${esc(KG.components[ci][1].toLowerCase())}</h4>${compPath(ci)}
      ${e.empty ? '' : `<ul>${ls.slice(0, 8).map(l => `<li>${idl('s', l.si, G.S[l.si][0])} ${gradeBadge(l.g)}</li>`).join('')}</ul>${ls.length > 8 ? `<p class="note">and ${ls.length - 8} more.</p>` : ''}`}
      <p>Exposure <b>${e.score}</b> ${pill(e.band)} ${ruleChips(e.rules)} · ${idl('c', KG.components[ci][0], 'Trace it')}</p>${evid('supply links graded explicit, declared or inferred')}`;
  }
  if (/expos|risk|worst|weak|thin/.test(q)) {
    const r = COMP_EXP.filter(e => !e.empty).sort((a, b) => b.score - a.score).slice(0, 6);
    return `<h4>Most exposed components that have some UK supply</h4>${trail(['Component', 'exposure', 'R2 · R4 · R5'])}
      <ul>${r.map(e => `<li>${idl('c', KG.components[e.ci][0], KG.components[e.ci][1])} · ${e.score} ${pill(e.band)} ${ruleChips(e.rules)}</li>`).join('')}</ul>${evid('exposure index over all supply links')}`;
  }
  return `<h4>I can answer from the graph about components, suppliers, clusters and scenarios</h4><p>Try one of these:</p>
    <div class="chips">${ASK_SUG.map(s => `<span class="chip" tabindex="0" role="button">${esc(s)}</span>`).join('')}</div>`;
}

VIEW_FNS.ask = function (m) {
  m.innerHTML = `<div id="askv"><h1>Ask the graph</h1><p class="sub">Questions use local graph facts and transparent rules, with the dependency path shown. Answers describe this directory snapshot and do not establish procurement commitments.</p>
    <div class="chips" id="sug">${ASK_SUG.map(s => `<span class="chip" tabindex="0" role="button">${esc(s)}</span>`).join('')}</div>
    <div class="chat" id="chat" style="margin-top:16px">${askLog.map(x => `<div class="msg q">${esc(x.q)}</div><div class="msg a">${x.a}</div>`).join('')}</div>
    <form class="ask" id="af"><input id="aq" type="text" placeholder="Ask about a component, supplier, cluster or scenario" aria-label="Question" autocomplete="off"><button class="btn primary" type="submit">Ask</button></form></div>`;
  const ask = q => { if (!q.trim()) return; askLog.push({ q, a: answer(q) }); VIEW_FNS.ask(m); const c = $('#chat'); c.lastElementChild && c.lastElementChild.scrollIntoView({ block: 'nearest' }); $('#aq').focus(); };
  $('#askv').addEventListener('click', e => { const c = e.target.closest('.chip'); if (c) ask(c.textContent); });
  $('#af').onsubmit = e => { e.preventDefault(); ask($('#aq').value); };
};

// Author: Koorosh Aslansefat
/* Ontology: Lattice's core diagram with switchable industry packs. Only the Offshore Wind pack has
   data loaded here, so its classes show live instance counts from the KG. */
let ontoPack = 'wind', ontoSel = 'Material';
const O_NODES = { Risk: [90, 110], DisruptionEvent: [440, 50], Country: [90, 290], Supplier: [290, 290], Material: [520, 290],
  Product: [740, 290], Customer: [920, 290], Chokepoint: [90, 470], Port: [270, 470], Factory: [640, 470] };
const O_EXTRA = { RegionalCluster: [290, 150], LifecyclePhase: [450, 520] };
const O_EDGES = [['Country', 'Risk', 'exposedTo'], ['Supplier', 'Country', 'locatedIn'], ['Risk', 'Supplier', 'affects'],
  ['DisruptionEvent', 'Supplier', 'affectsSupplier'], ['DisruptionEvent', 'Material', 'affectsMaterial'],
  ['Supplier', 'Material', 'supplies', 'SupplyLink'], ['Material', 'Product', 'usedIn', 'BOMLine'], ['Product', 'Customer', 'soldTo'],
  ['Supplier', 'Port', 'usesPort'], ['Port', 'Chokepoint', 'dependsOn'], ['Supplier', 'Factory', 'deliversTo'],
  ['Factory', 'Material', 'holdsInventoryOf', 'InventoryPosition'], ['Factory', 'Product', 'manufactures (inferred)']];
const O_PACK_EDGES = [['Supplier', 'RegionalCluster', 'memberOf'], ['Supplier', 'LifecyclePhase', 'servesPhase']];
const O_PACKS = {
  pharma: { n: 'Pharma', c: 'var(--pk-pharma)', add: { Material: ['ActiveIngredient', 'Excipient'], Supplier: ['ContractManufacturer'], Factory: ['GMPSite'] },
    txt: 'API, excipients, CMOs, GMP sites. Alternate-source lead time extends by regulatory filing time.' },
  auto: { n: 'Automotive', c: 'var(--pk-auto)', add: { Supplier: ['TierNSupplier'], Material: ['Semiconductor'] },
    txt: 'Tier-N supplier chain, semiconductors, PPAP status on supply links.' },
  elec: { n: 'Electronics', c: 'var(--pk-elec)', add: { Factory: ['Fab'], Material: ['ProcessNode'] },
    txt: 'Fabs, process nodes, fab location as a country exposure.' },
  wind: { n: 'Offshore Wind', c: 'var(--wind)', extra: true,
    add: { Product: ['TurbineSystem', 'WindFarm'], Material: ['Component ×34', 'Subsystem ×5'], Supplier: ['Tier 1–3', 'ServiceProvider'],
      Factory: ['Site'], Port: ['PortOrYard'], Chokepoint: ['InstallationVessel'], Country: ['HQ country'] },
    notes: { supplies: 'graded ×3', usedIn: '≡ hasPart' },
    txt: 'Turbine system breakdown, evidence-graded supply links, regional clusters, lifecycle phases, installation vessels and marshalling ports.' },
};
const O_RULES_READ = { Material: ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'], Supplier: ['R1', 'R5', 'R6'], Product: ['R3'], RegionalCluster: ['R4', 'R6'],
  Country: ['R6'], Factory: [], Port: [], Chokepoint: [], LifecyclePhase: [], Risk: [], DisruptionEvent: [], Customer: [] };

function ontoInstances(cls) {
  const S = KG.suppliers, list = (rows) => `<ul>${rows.join('')}</ul>`;
  const li = (a, b) => `<li><span>${a}</span> <span class="num" style="float:right">${b}</span></li>`;
  const grades = [0, 1, 2].map(g => KG.links.filter(l => l[2] === g).length);
  switch (cls) {
    case 'Supplier': {
      const t = TIERS.map(([b, l]) => [l, S.filter(s => s[1] & b).length]).filter(x => x[1]);
      const top = G.supLinks.map((ls, si) => [si, ls.length]).sort((a, b) => b[1] - a[1]).slice(0, 4);
      return { n: fmt(S.length), unit: 'suppliers', body: list(t.map(([l, n]) => li(esc(l), n))) +
        `<p class="note">Most component links: ${top.map(([si, n]) => idl('s', si, `${S[si][0]} (${n})`)).join(', ')}</p>` };
    }
    case 'Material': return { n: KG.components.length, unit: 'components in 5 subsystems', body:
      list(KG.subsystems.map(([id, nm]) => li(`<i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${subVar(id)};margin-right:6px"></i>${esc(nm)}`, KG.components.filter(c => c[2] === id).length))) +
      `<p class="note">${fmt(KG.links.length)} supply links: ${grades[0]} explicit, ${grades[1]} declared, ${grades[2]} inferred.</p>` };
    case 'Product': return { n: 2, unit: 'turbine systems', body: list([li('Fixed-bottom · exposure', BASE.fixed.turbine), li('Floating · exposure', BASE.floating.turbine), li('WindFarm instances', '0')]) +
      '<p class="note">The directory has no project records, so WindFarm stays empty until a project feed is added.</p>' };
    case 'Factory': {
      const hq = KG.sites.filter(s => s[2]).length;
      const cities = Object.entries(KG.sites.reduce((a, s) => (s[1] && (a[s[1]] = (a[s[1]] || 0) + 1), a), {})).sort((a, b) => b[1] - a[1]).slice(0, 5);
      return { n: fmt(KG.sites.length), unit: 'sites', body: list([li('Marked as HQ', hq), ...cities.map(([c, n]) => li(esc(c), n))]) };
    }
    case 'Country': {
      const by = KG.countries.map((c, i) => [c, S.filter(s => s[4] === i).length]).filter(x => x[1]).sort((a, b) => b[1] - a[1]);
      return { n: by.length, unit: 'HQ countries', body: list(by.slice(0, 6).map(([c, n]) => li(esc(c), n))) + `<p class="note">${S.filter(s => s[4] < 0).length} suppliers do not state an HQ.</p>` };
    }
    case 'Port': return { n: KG.ports.length, unit: 'port & yard operators', body: list([0, 1, 2].map(g => li(LatticeCore.GRADE[g], KG.ports.filter(p => p[1] === g).length))) };
    case 'Chokepoint': return { n: KG.vesselClasses.length, unit: 'installation vessel classes', body:
      list(KG.vesselClasses.map((v, i) => [v[1], new Set(KG.vessels.filter(x => x[1] === i).map(x => x[0])).size]).sort((a, b) => b[1] - a[1]).map(([nm, n]) => li(esc(nm), n))) };
    case 'RegionalCluster': return { n: KG.clusters.length, unit: 'regional clusters', body:
      list(KG.clusters.map((c, i) => [c, S.filter(s => s[5].includes(i)).length]).sort((a, b) => b[1] - a[1]).map(([c, n]) => li(esc(c), n))) +
      `<p class="note">${S.filter(s => !s[5].length).length} suppliers name no cluster.</p>` };
    case 'LifecyclePhase': return { n: KG.phases.length, unit: 'lifecycle phases', body: list(KG.phases.map((p, i) => li(esc(p), S.filter(s => s[7].includes(i)).length))) };
    default: return { n: 0, unit: 'instances', body: `<p class="note">The directory does not populate ${cls}. The class stays in the core, so a risk or customer feed can be added without changing any analytics.</p>` };
  }
}

function ontoSvg() {
  const P = O_PACKS[ontoPack], W = 118, H = 34;
  const pos = { ...O_NODES, ...(P.extra ? O_EXTRA : {}) };
  const off = (a, b) => {
    const [x1, y1] = pos[a], [x2, y2] = pos[b], dx = x2 - x1, dy = y2 - y1;
    const o = Math.abs(dx) > Math.abs(dy) ? [W / 2 * Math.sign(dx), 0] : [0, H / 2 * Math.sign(dy)];
    return [x1 + o[0], y1 + o[1], x2 - o[0], y2 - o[1]];
  };
  let e = '', n = '';
  const edge = ([a, b, l, rf], packEdge) => {
    const [x1, y1, x2, y2] = off(a, b), inf = l.includes('inferred');
    const col = packEdge ? P.c : inf ? 'var(--high)' : 'var(--muted)';
    e += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${col}" stroke-width="${packEdge ? 1.8 : 1.3}" ${inf ? 'stroke-dasharray="5 4"' : ''} marker-end="url(#${packEdge ? 'arw' : 'ar'})" class="${packEdge ? 'packonly' : ''}"/>`;
    const t = inf ? 0.62 : 0.5; // inferred label sits nearer its target so it clears holdsInventoryOf
    const mx = x1 + (x2 - x1) * t, my = y1 + (y2 - y1) * t, w = l.length * 6 + 10, note = !packEdge && P.notes && P.notes[l.split(' ')[0]];
    e += `<g class="${packEdge ? 'packonly' : ''}"><rect x="${mx - w / 2}" y="${my - 8}" width="${w}" height="16" rx="3" fill="var(--bg)"/><text x="${mx}" y="${my + 3.5}" text-anchor="middle" font-size="10" fill="${col}" font-family="var(--f-mono)">${l}</text>`;
    if (rf) e += `<text x="${mx}" y="${my + 20}" text-anchor="middle" font-size="9" fill="var(--accent)" font-family="var(--f-mono)">[${rf}]</text>`;
    if (note) e += `<text class="ptag" x="${mx}" y="${my - 13}" text-anchor="middle" font-size="9.5" fill="${P.c}" font-family="var(--f-mono)">${esc(note)}</text>`;
    e += '</g>';
  };
  O_EDGES.forEach(x => edge(x, false));
  if (P.extra) {
    O_PACK_EDGES.forEach(x => edge(x, true));
    const [mx, my] = pos.Material;
    e += `<g class="packonly"><path d="M ${mx + 30} ${my - H / 2} C ${mx + 30} ${my - 62}, ${mx + 78} ${my - 62}, ${mx + 56} ${my - H / 2}" fill="none" stroke="${P.c}" stroke-width="1.8" marker-end="url(#arw)"/>
      <text x="${mx + 58}" y="${my - 58}" text-anchor="middle" font-size="10" fill="${P.c}" font-family="var(--f-mono)">partOf</text></g>`;
  }
  Object.entries(pos).forEach(([k, [x, y]]) => {
    const isExtra = !(k in O_NODES), tags = (P.add[k] || []);
    const ring = isExtra || tags.length ? P.c : 'var(--line)';
    n += `<g class="onode ${ontoSel === k ? 'sel' : ''} ${isExtra ? 'packonly' : ''}" data-cls="${k}" tabindex="0" role="button" aria-label="${k}">
      <rect x="${x - W / 2}" y="${y - H / 2}" width="${W}" height="${H}" rx="6" fill="${isExtra ? 'var(--wind-soft)' : 'var(--surface)'}" stroke="${ring}" stroke-width="${isExtra || tags.length ? 2 : 1.2}"/>
      <text x="${x}" y="${y + 4}" text-anchor="middle" font-size="12" font-weight="600" fill="var(--ink)">${k}</text>` +
      tags.map((t, i) => `<text class="ptag" style="animation-delay:${80 + i * 70}ms" x="${x}" y="${y + H / 2 + 13 + i * 12}" text-anchor="middle" font-size="9.5" fill="${P.c}" font-family="var(--f-mono)">+ ${esc(t)}</text>`).join('') + '</g>';
  });
  return `<svg viewBox="0 0 1000 560" style="width:100%;height:auto;min-width:660px" role="img" aria-label="Core ontology with the ${P.n} pack">
    <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--muted)"/></marker>
    <marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="${P.c}"/></marker></defs>${e}${n}</svg>`;
}

function ontoSide() {
  const P = O_PACKS[ontoPack];
  let cls = '';
  if (ontoPack === 'wind') {
    const r = ontoInstances(ontoSel), reads = O_RULES_READ[ontoSel] || [];
    cls = `<div class="panel detail"><h2>Class · ${esc(ontoSel)}</h2><h3><span class="num" style="font-family:var(--f-display)">${r.n}</span> <span style="font:500 14px var(--f-body);color:var(--muted)">${esc(r.unit)}</span></h3>${r.body}
      ${reads.length ? `<p class="note" style="margin-top:8px">Rules that read this class: ${reads.map(x => `<span class="rule-chip">${x}</span>`).join('')}</p>` : ''}</div>`;
  } else {
    cls = `<div class="panel"><h2>Class · ${esc(ontoSel)}</h2><p class="note">No ${esc(P.n)} data is loaded in this demo. The core classes and rules are the same in every pack; switch to Offshore Wind to see live instances.</p></div>`;
  }
  const R2 = COMP_EXP.filter(x => x.rules.R2).length, R4 = COMP_EXP.filter(x => x.rules.R4).length, R5 = COMP_EXP.filter(x => x.rules.R5).length;
  const inferred = KG.links.filter(l => l[2] === 2).length;
  const live = { R1: `${inferred} links`, R2: `${R2} of 34`, R3: `fixed ${BASE.fixed.turbine} · floating ${BASE.floating.turbine}`, R4: `${R4} components`, R5: `${R5} components`, R6: idl('view', 'scenario', 'run in What if…') };
  const rules = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'].map(k => `<div class="rule"><b>${k}</b>${RULE_TXT[k]}${ontoPack === 'wind' ? `<span class="live">${live[k]}</span>` : ''}</div>`).join('');
  return `${cls}<div class="panel"><h2>Reasoning rules on the core</h2>${rules}</div>
    <div class="panel"><h2>Active pack</h2><p style="margin:0"><b style="color:${P.c}">${P.n}</b><br><span class="note">${P.txt}</span></p></div>`;
}

function ontoMapTable() {
  const S = KG.suppliers;
  const rows = [
    ['Product', 'TurbineSystem (fixed, floating), WindFarm', '2 systems', 'system breakdown'],
    ['Material', 'Component ×34 in 5 subsystems', `${KG.links.length} links`, 'site categories + descriptions'],
    ['Supplier', 'Tier 1–3, ServiceProvider, Developer, Research', fmt(S.length), 'Supply Chain Category'],
    ['Factory', 'Site', fmt(KG.sites.length), 'Sites table'],
    ['Country', 'HQ country', KG.countries.length, 'Headquarters'],
    ['Port', 'PortOrYard', KG.ports.length, 'Port / Yard category, text'],
    ['Chokepoint', 'InstallationVessel', `${KG.vesselClasses.length} classes`, 'Vessels category, text'],
    ['new', 'RegionalCluster', KG.clusters.length, 'Regional Cluster(s)'],
    ['new', 'LifecyclePhase', KG.phases.length, 'capabilities + categories'],
  ];
  return `<div class="panel" style="margin-top:16px"><h2>How the Offshore Wind pack populates the core</h2><div class="scroll"><table>
    <thead><tr><th>Core class</th><th>Wind subclass</th><th>Instances</th><th>Directory field</th></tr></thead><tbody>
    ${rows.map(r => `<tr class="click" data-cls="${r[0] === 'new' ? r[1] : r[0]}"><td>${r[0] === 'new' ? '<span class="tag" style="color:var(--wind)">pack class</span>' : `<b>${r[0]}</b>`}</td><td>${esc(r[1])}</td><td class="num">${r[2]}</td><td class="note">${esc(r[3])}</td></tr>`).join('')}
    </tbody></table></div>
    <h2 style="margin-top:16px">Data notes</h2>${[...KG.meta.dataNotes, ...(HAS_GEO ? [GEO_NOTE] : [])].map(t => `<p class="note" style="margin:4px 0">${esc(t)}</p>`).join('')}</div>`;
}

VIEW_FNS.ontology = function (m) {
  m.innerHTML = `<h1>One ontology. Offshore wind arrives as a pack.</h1>
    <p class="sub">The core describes how any supply chain connects. The Offshore Wind pack adds subclasses, two pack classes and evidence grades, then the UK Offshore Wind Directory fills it with ${fmt(KG.suppliers.length)} supplier profiles. The analytics are written against the core, so they run unchanged.</p>
    <div class="packs" role="radiogroup" aria-label="Industry extension pack"><span class="tag">Extension pack:</span>
      ${Object.entries(O_PACKS).map(([k, p]) => `<button class="pk" role="radio" data-pk="${k}" aria-checked="${k === ontoPack}" style="color:${k === ontoPack ? p.c : 'inherit'}">${p.n}</button>`).join('')}</div>
    <div class="grid two"><div><div class="panel scroll" id="osvg">${ontoSvg()}</div>${ontoPack === 'wind' ? ontoMapTable() : ''}</div>
    <div class="ontoside" id="oside">${ontoSide()}</div></div>`;
  m.querySelectorAll('.pk').forEach(b => b.onclick = () => {
    ontoPack = b.dataset.pk;
    if (!(ontoSel in O_NODES) && ontoPack !== 'wind') ontoSel = 'Material';
    VIEW_FNS.ontology(m);
  });
  m.querySelectorAll('[data-cls]').forEach(g => {
    const pick = () => { ontoSel = g.dataset.cls; m.querySelectorAll('.onode').forEach(x => x.classList.toggle('sel', x.dataset.cls === ontoSel)); $('#oside').innerHTML = ontoSide(); };
    g.addEventListener('click', pick);
    g.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pick(); } });
  });
};

// Author: Koorosh Aslansefat
/* View order, nav, hash router and delegated navigation for [data-go] links. */
const VIEWS = [['command', 'Command center'], ['anatomy', 'Turbine anatomy'], ['trace', 'Trace a component'],
  ['landscape', 'Supply landscape'], ['scenario', 'What if…'], ['ask', 'Ask the graph'], ['ontology', 'Ontology']];
let view = 'command';
function nav() { $('#nav').innerHTML = VIEWS.map(([k, l]) => `<button data-v="${k}" aria-current="${k === view}">${l}</button>`).join(''); }
function go(v) { view = v; nav(); render(); window.scrollTo(0, 0); try { history.replaceState(null, '', '#' + v); } catch (e) {} }
function render() {
  hideTip();
  const m = $('#main'), fn = VIEW_FNS[view];
  if (fn) fn(m); else m.innerHTML = `<h1>${esc(VIEWS.find(v => v[0] === view)[1])}</h1><p class="sub">This view is not built yet.</p>`;
}
document.addEventListener('click', e => {
  const b = e.target.closest('[data-v]'); if (b && b.closest('#nav')) return go(b.dataset.v);
  const t = e.target.closest('[data-go]'); if (!t) return;
  const [kind, id] = t.dataset.go.split(':');
  if (kind === 'view') return go(id);
  if (kind === 'c') { STATE.comp = CI[id]; STATE.supplier = null; traceSel = null; return go('trace'); }
  if (kind === 's') { STATE.supplier = +id; const l = G.supLinks[+id].slice().sort((a, b) => a.g - b.g)[0]; if (l) STATE.comp = l.ci; return go('trace'); }
  if (kind === 'k') { STATE.scenario = { cluster: +id, overseas: false, micro: false, floatingOnly: false }; return go('scenario'); }
});
document.addEventListener('keydown', e => {
  // elements with their own Enter handler call preventDefault; SVG elements have no .click()
  if (e.key !== 'Enter' || e.defaultPrevented || !e.target.matches('[data-go],.chip,[role="button"]')) return;
  if (typeof e.target.click === 'function') e.target.click();
  else e.target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
});
const hashView = () => { const h = (location.hash || '').slice(1); return VIEWS.some(v => v[0] === h) ? h : null; };
addEventListener('hashchange', () => { const h = hashView(); if (h && h !== view) go(h); });
$('#nsup').textContent = fmt(KG.suppliers.length);
if (/^\d{4}-\d{2}-\d{2}$/.test(KG.meta.extracted)) $('#nexp').textContent = ` (export of ${new Date(KG.meta.extracted).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })})`;
view = hashView() || view;
nav(); render();
