# Verification record and commands

Updated 1 November 2026. [Handover](../PROJECT_HANDOVER.md) · [status](STATUS.md) · [operations](OPERATIONS.md).

## Latest environmental atlas verification

The complete Python suite passed **278 tests**, including 14 new environmental tests. The final TypeScript/Vite build passed. Live browser QA verified the official-boundary map, IUCN metadata hatching, linked search/feature results, expansion, actual rayshader-textured Three.js terrain, water/agreement/exaggeration/camera controls and an unsaved evidence preview. Current scoped snapshot verification passed **14 datasets, 111 raw objects, 151,020,895 bytes** for revision 19. SQLite quick-check returned `ok`, with 10 completed jobs and none queued/running at inspection. Energy/LCOE and saved access settings remain unchanged. [Detailed source identities and method checks](../reports/environmental_atlas.md).

R checks include north-up orientation with an asymmetric diagnostic, source NoData transparency, physical-cell resampling and rejection of an entirely missing grid. A real R 4.6.2 / rayshader 0.41.2 render was generated, served and visually inspected. Optional runtime/library and exact render products require a separate backup.

## Earlier C54 implementation verification

Implementation `f3c13f7` (C54 Lattice), followed by byte-preservation/handover commit `3aaa30e`, passed the **264-test complete Python suite**, pure Node Lattice model checks, TypeScript/Vite production build and representative browser QA. These are recorded implementation results, not a claim that all engineering studies or every specialist visual is complete.

Python coverage includes package/ownership contracts, geometry/exclusions/spacing, wind time/height/unit rules, Weibull/shear and other planning methods, energy/loss/finance reconciliation, source scope/raw integrity, jobs/cache/errors, immutable saves/previews, access unknown/window semantics, C54 source validation and provenance. Node checks independently exercise the supplied pure reference core's 47/42 fixed/floating baselines, missing evidence, cluster membership, alternate-source filtering and baseline preservation under stress tests.

Browser coverage across the implemented milestones includes selection/reload/cross-tab synchronization, management preview/full twin identity and cleanup, C03–C05 controls, C07 thresholds/exports, C37 filters, C56 criteria/windows, C61 contained preview errors and price/LCOE separation, C62/C65 registers, all-category readiness, and all seven C54 views. C54 checks included fixed/floating switching, component diagram/map, disruption recalculation, local graph answers, ontology, full-screen expansion and revision-specific procurement controls.

Existing non-fatal warnings concern Starlette/httpx test-client and Shapely transforms. Vite reports large chunks; this is not a build failure. A local Node memory-allocation failure was resolved for the C54 build using a process-local 512 MB heap setting and D:-based temporary directory. Do not describe the initial failure as the final validation outcome.

## Earlier documentation-only refresh

No runtime model, scenario inputs or collected data were changed. The refresh checks:

- SQLite `PRAGMA quick_check`: `ok`; one project, nine completed jobs and no queued/running collection at inspection.
- Workspace registry: 70 category packages, 22 profiles, five regions, five strategies, 16 topics and official 40/20/20/20 weights; four supplied-original checksums unchanged.
- Saved reference revision 17: 13 scoped datasets, 98 unique raw responses, 25,538,350 raw bytes; payload/raw SHA-256 and provider/project/site/AOI/reference-point checks pass.
- Both contextual references and the Lattice original/bundle hashes retain identity. Git attributes preserve checksum-sensitive bytes.
- Documentation: local link targets, code fences, all-category coverage and handover export links; see `scripts.verify_documentation` and the documentation refresh report.

The model suite/build were not rerun solely to change documentation. Historical reports retain their earlier test counts and scenario IDs as milestone evidence; they must not override this current record. Documentation checks establish consistency, not the accuracy of future upstream data or engineering approval.

## Repeat the appropriate checks

```powershell
$testRunDirectory = Join-Path 'D:\Wind_Farm_Design\work' ('pytest-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q --basetemp $testRunDirectory
node tests/lattice_core.test.cjs
.\.venv\Scripts\python.exe -m scripts.verify_workspace
.\.venv\Scripts\python.exe -m scripts.verify_data_snapshots --scenario-id 05c163c0-c50f-412c-bdbf-324d0ae9cf04
.\.venv\Scripts\python.exe -m scripts.verify_documentation
npm.cmd run build --prefix dashboard
```

Always use a fresh scratch `--basetemp`; pytest may clear a reused one. Never use real data, originals or backup folders. Run the full suite after material model/backend changes, targeted checks for narrow changes, and browser QA for UI changes. Keep a record of what actually ran, its date, source/scenario identity and any unresolved error.
