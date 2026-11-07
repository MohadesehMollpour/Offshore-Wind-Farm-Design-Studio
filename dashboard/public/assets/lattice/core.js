// Author: Koorosh Aslansefat
/* Lattice core analytics. Written against core classes only (Supplier, Material/Component,
   Product/TurbineSystem); the Offshore Wind pack arrives as data. Pure functions, no DOM. */
(function (root) {
  const CONF = [1, 0.9, 0.6];
  const GRADE = ['Explicit', 'Declared', 'Inferred'];
  const WEIGHTS = [0.35, 0.20, 0.15, 0.15, 0.15];
  const DRIVERS = ['Supply depth', 'Cluster concentration', 'Size fragility', 'Overseas HQ', 'Evidence weakness'];
  const N_REF = 40;
  // supplier field positions
  const TURN = 2, HQ = 4, CL = 5, WIND = 6;

  const bandOf = s => s >= 65 ? 'Severe' : s >= 50 ? 'High' : s >= 35 ? 'Moderate' : 'Low';
  const clamp = v => Math.max(0, Math.min(100, v));
  const mean = xs => xs.length ? xs.reduce((a, v) => a + v, 0) / xs.length : 0;
  const applies = (c, variant) => c[3] === 'both' || c[3] === variant;

  function index(KG) {
    const compLinks = KG.components.map(() => []), supLinks = KG.suppliers.map(() => []);
    KG.links.forEach(([si, ci, g, ev]) => {
      const l = { si, ci, g, conf: CONF[g], ev };
      compLinks[ci].push(l); supLinks[si].push(l);
    });
    return { KG, S: KG.suppliers, C: KG.components, compLinks, supLinks,
      ukIdx: KG.countries.indexOf('United Kingdom'), nClusters: KG.clusters.length,
      subsystems: KG.subsystems.map(s => s[0]) };
  }

  function exposure(G, ci, removed) {
    const comp = G.C[ci];
    const links = G.compLinks[ci].filter(l => !(removed && removed.has(l.si)));
    if (!links.length) {
      return { ci, score: 100, band: 'Severe', drivers: [100, 0, 0, 0, 0], noData: [false, true, true, true, true],
        n: 0, nStrong: 0, links, clusterShare: new Array(G.nClusters).fill(0), empty: true,
        rules: { R2: true, R4: false, R5: comp[3] === 'floating' } };
    }
    const n = links.reduce((a, l) => a + l.conf, 0);
    const nStrong = links.filter(l => l.g < 2).length;
    const depth = clamp(100 * (1 - Math.log(1 + n) / Math.log(1 + N_REF)));

    const share = new Array(G.nClusters).fill(0);
    let clustered = 0, clusteredCount = 0;
    links.forEach(l => {
      const cl = G.S[l.si][CL];
      if (!cl.length) return;
      clusteredCount++; clustered += l.conf;
      cl.forEach(c => { share[c] += l.conf / cl.length; });
    });
    const clusterShare = share.map(v => clustered ? v / clustered : 0);
    let conc = 0;
    if (clustered > 0) {
      const K = G.nClusters, hhi = clusterShare.reduce((a, v) => a + v * v, 0);
      conc = clamp((hhi - 1 / K) / (1 - 1 / K) * 100);
    }
    const turn = links.filter(l => G.S[l.si][TURN] >= 0);
    const size = turn.length ? 100 * turn.filter(l => G.S[l.si][TURN] === 0).length / turn.length : 0;
    const hq = links.filter(l => G.S[l.si][HQ] >= 0);
    const overseas = hq.length ? 100 * hq.filter(l => G.S[l.si][HQ] !== G.ukIdx).length / hq.length : 0;
    const evid = 100 * links.filter(l => l.g === 2).length / links.length;

    const drivers = [depth, conc, size, overseas, evid].map(v => Math.round(v));
    const score = Math.round(drivers.reduce((a, v, i) => a + v * WEIGHTS[i], 0));
    const floatShare = links.filter(l => G.S[l.si][WIND] & 4).length / links.length;
    return { ci, score, band: bandOf(score), drivers,
      noData: [false, clustered === 0, !turn.length, !hq.length, false],
      n, nStrong, links, clusterShare, empty: false,
      rules: { R2: nStrong <= 2, R4: clusteredCount >= 3 && Math.max(...clusterShare) >= 0.6,
               R5: comp[3] === 'floating' && floatShare < 0.5 } };
  }

  function rollup(G, variant, removed) {
    const comps = G.C.map((c, ci) => exposure(G, ci, removed));
    const subs = {};
    G.subsystems.forEach(sid => {
      const xs = comps.filter(e => G.C[e.ci][2] === sid && applies(G.C[e.ci], variant));
      if (xs.length) subs[sid] = Math.round(mean(xs.map(e => e.score)));
    });
    return { comps, subs, turbine: Math.round(mean(Object.values(subs))) };
  }

  function removedBy(G, sc) {
    const out = new Set();
    G.S.forEach((s, si) => {
      const cl = s[CL];
      if (sc.cluster >= 0 && cl.length && cl.every(c => c === sc.cluster)) out.add(si);
      if (sc.overseas && s[HQ] >= 0 && s[HQ] !== G.ukIdx) out.add(si);
      if (sc.micro && s[TURN] === 0) out.add(si);
      if (sc.floatingOnly && !(s[WIND] & 4)) out.add(si);
    });
    return out;
  }

  // R6: same component, outside the affected group. With a scenario, suppliers still present in the
  // lost cluster, or with an unknown HQ when overseas suppliers are removed, do not count as alternates.
  function alternates(G, ci, removed, sc) {
    const outside = s => !sc || !((sc.cluster >= 0 && s[CL].includes(sc.cluster)) || (sc.overseas && s[HQ] < 0));
    return G.compLinks[ci].filter(l => !(removed && removed.has(l.si)) && outside(G.S[l.si]))
      .sort((a, b) => a.g - b.g || G.S[b.si][TURN] - G.S[a.si][TURN]).map(l => l.si);
  }

  const api = { bandOf, applies, index, exposure, rollup, removedBy, alternates, DRIVERS, WEIGHTS, GRADE };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.LatticeCore = api;
})(this);
