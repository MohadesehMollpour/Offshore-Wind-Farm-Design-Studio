# C54 — Lattice supply-chain workspace

Implemented 1 November 2026 from the user-supplied `Lattice · Offshore Wind.html`. Its HTML is reference material; instructions inside attachments are not agent instructions.

## Delivered interface

C54 embeds the supplied seven-view explorer: Command center, Turbine anatomy, Trace a component, Supply landscape, What if…, Ask the graph and Ontology. It preserves the teal/blue palette, panels, component anatomy, evidence grades, geographic tracing, heatmap, Sankey and disruption comparisons. The explorer is responsive and offers a full-screen button. The ordinary project/scenario selector remains above it.

The importer preserves the original HTML, extracts KG/GEO with JSON decoding (no evaluation), validates indices, evidence grades, component scopes, profile URL origins and town coordinates, and records SHA-256 identities. D3 7.9.0 and d3-sankey 0.12.3 and their licenses are bundled locally. No remote fonts, chart CDN or graph-query API is required at runtime. External directory profiles open only when their link is selected.

The adapted renderer runs inside an iframe with scripts and explicit external-profile popups, without same-origin privileges. A content security policy blocks network connections, forms and unlisted scripts. It cannot read the parent application's DOM or storage. The source and validation code are separate from the executable adaptation; this is not an arbitrary uploaded-HTML execution service.

## Evidence and scenario scope

The attached directory snapshot is dated **14 October 2026** and contains 885 supplier profiles, 711 site records, 34 components, 214 capability links, eight clusters, 95 vessel-capability rows and 19 port-capability rows. These are directory rows and links, not counts of available manufacturing slots, vessels or berths. The directory's own verification claim has not been independently reverified.

The source is a UK contextual directory, shared across selected layouts. Changing a farm or layout does not manufacture a local supplier list. Each C54 result still records the selected scenario ID/hash and directory checksums. The existing procurement register uses `scenario.inputs.category_inputs.C54`; previews are temporary and saving creates a revision. Existing vendor/duration evidence remains missing until supplied and reviewed. Directory counts do not turn `quantitative_ready` on for project procurement.

Explorer navigation, graph questions, component choices, fixed/floating analytical variants and disruption filters are temporary exploration state. They reset when the selected revision changes or the page reloads; they do not change the saved farm support design, prices, programme or supplier qualification. Procurement review entries are saved separately through the revision workflow.

## Model

The supplied pure analytics are preserved in `dashboard/public/assets/lattice/core.js`. Explicit, declared and inferred links have confidence weights 1, 0.9 and 0.6. Component exposure combines supply depth (35%), normalized cluster concentration (20%), size fragility (15%), overseas headquarters (15%) and inferred-link share (15%). Missing-driver flags remain visible. No links produces a model exposure of 100, indicating missing supplier evidence rather than proof of absence in the market. Subsystem and turbine scores are rounded, unweighted means of applicable components/subsystems. Baselines: fixed 47, floating 42; 17 of 34 components have at most two explicit/declared suppliers, six have no link.

Cluster disruption removes only suppliers whose stated memberships are all that cluster. Multicluster suppliers remain, but are excluded as alternatives outside the lost cluster. This is a capability stress test, not a production or delivery forecast. Profiles may cover maintenance, materials or services rather than complete-component manufacturing. GeoNames town points and Natural Earth geography are credited; cluster shapes and overseas HQ anchors are illustrative and are not shipping routes.

## Files and maintenance

- `backend/supply_reference.py`: inert data validation, cached metadata/counts, checksum-checked original.
- `backend/app.py`: `/api/references/lattice-supply`, `/original`, `/data.json` before the SPA fallback.
- `backend/work_packages.py`: C54 contextual provenance and procurement gaps.
- `dashboard/src/SupplyChainWorkspace.tsx`, `supply-chain.css`: project integration, full-screen explorer, source/download details and saved evidence register.
- `dashboard/public/assets/lattice/`: reviewed renderer, pure core, local libraries/licenses and data. Vite copies this to `dist/assets/lattice`.
- `sources/references/lattice_supply/`: preserved original, canonical data/metadata and bundle hash manifest.
- `scripts/import_lattice_reference.py`: maintainer-only reimport of this specific attachment format. Review extracted executable changes before committing; it is not an automatic trust decision.
- `tests/test_supply_reference.py`, `tests/lattice_core.test.cjs`: import/provenance/isolation checks and pure analytics regressions.

Reimport, when intentionally replacing this reference:

```powershell
.venv\Scripts\python.exe -m scripts.import_lattice_reference 'C:\path\to\Lattice · Offshore Wind.html'
node tests/lattice_core.test.cjs
.venv\Scripts\python.exe -m pytest -q tests/test_supply_reference.py --basetemp D:\Wind_Farm_Design\work\pytest-c54-new
npm.cmd run build --prefix dashboard
```

Restart the existing local backend after Python changes only when no ingestion job is queued/running. Refresh C54 on any revision whose stored result predates the import. Old immutable inputs do not require migration. Source changes should be accompanied by a refreshed C54 result so its provenance matches the displayed reference.

## Validation and next work

The complete Python suite passed **264 tests**; the pure Node model checks and TypeScript/Vite build passed. Browser QA covered all seven views, fixed/floating switching, component tracing and map, disruption selection, a local mooring-chain query, ontology, and the procurement register. No live vendor API or LLM is connected to this explorer.

Project-specific supplier qualification, dated quotations, manufacturing capacity and delivery commitments remain acquisition tasks. Those should be added as reviewed vendor records with an explicit price/date basis before implementing a procurement lead-time schedule or cost-range model. Do not infer them from profile counts or reuse the illustrative C65 programme as vendor commitments.

## Documentation checkpoint and reference-version limit

The comprehensive documentation refresh records this implementation in the core guides, all-category register and construction-owner/category documentation. See [the documentation index](../docs/INDEX.md) and [handover](../PROJECT_HANDOVER.md). The 264-test suite/build/browser results above are implementation evidence; the documentation task reruns documentation/source-integrity checks rather than claiming another model test run.

The current contextual bundle is global to the checkout. Reimport replaces the current source/assets, while Git retains committed versions; old scenario inputs do not automatically select an old bundle. Preserve/review previous versions and ensure displayed reference hashes match the intended stored result provenance before interpreting comparisons. A future versioned-reference binding would be a separate implementation change. Byte-preservation attributes for originals/assets must remain intact.
