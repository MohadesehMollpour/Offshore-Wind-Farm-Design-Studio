// Regression checks for the reviewed, pure reference analytics. No browser or UI automation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const sandbox = {module: {exports: {}}};
vm.runInNewContext(fs.readFileSync(path.join(root, 'dashboard/public/assets/lattice/core.js'), 'utf8'), sandbox);
const core = sandbox.module.exports;
const kg = JSON.parse(fs.readFileSync(path.join(root, 'sources/references/lattice_supply/reference.json'), 'utf8')).data.kg;
const g = core.index(kg);
assert.equal(core.rollup(g, 'fixed').turbine, 47);
assert.equal(core.rollup(g, 'floating').turbine, 42);
const empty = kg.components.findIndex(c => c[0] === 'hub_pitch');
const noEvidence = core.exposure(g, empty);
assert.equal(noEvidence.empty, true);
assert.equal(noEvidence.score, 100);
assert.equal(noEvidence.nStrong, 0);
const sc = {cluster: 0, overseas: false, micro: false, floatingOnly: false};
const removed = core.removedBy(g, sc);
const single = kg.suppliers.findIndex(s => s[5].length === 1 && s[5][0] === 0);
const multi = kg.suppliers.findIndex(s => s[5].includes(0) && s[5].length > 1);
assert(single >= 0 && multi >= 0);
assert(removed.has(single));
assert(!removed.has(multi));
const all = new Set(kg.suppliers.map((_, i) => i));
assert.equal(core.rollup(g, 'fixed', all).turbine, 100);
assert.equal(core.exposure(g, 0, all).links.length, 0);
assert.equal(core.rollup(g, 'fixed').turbine, 47); // Stress tests leave the baseline intact.
for (let ci = 0; ci < kg.components.length; ci++) {
  const e = core.exposure(g, ci);
  assert(Number.isFinite(e.score) && e.score >= 0 && e.score <= 100);
  for (const si of core.alternates(g, ci, removed, sc)) {
    assert(!removed.has(si));
    assert(!kg.suppliers[si][5].includes(0));
  }
}
console.log('Lattice core: baseline, missing evidence, cluster disruption, alternates and immutability passed.');
