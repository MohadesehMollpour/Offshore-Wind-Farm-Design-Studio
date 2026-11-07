# C49 — Birds, bats and marine mammals

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

127 source-listed qualifying interests with site/type filters; designations are not observed wildlife, abundance or impact estimates.

**Current reference checkpoint:** revision 19, `05c163c0-c50f-412c-bdbf-324d0ae9cf04`; source-backed regional screening, not engineering completion. The compatible `environment_screening` dataset supplies original-boundary metrics, simplified display GeoJSON, declared qualifying features, source/coverage metadata and sampled elevations. The sidebar Environmental atlas opens C48; C16 starts in 3D, C49 starts with all regional feature rows. Without this binding the earlier category source/register fallback remains.

**Code:** `backend/environment.py`, `backend/external_analysis.py`; `dashboard/src/EnvironmentPage.tsx`, `EnvironmentTerrain.tsx`. Optional renderer: `scripts/render_environment_rayshader.R` and `run_environment_rayshader.py`. The category adapter remains `src/controller.py`.

## Evidence and continuation

[Environmental implementation report](../../reports/environmental_atlas.md) records official source vintages, 22 sites / 127 interests, grid identity, IUCN unknowns, methods, tests and reproduction. The 150 km disc includes land and sea and is not a proposed farm footprint. Boundaries are partial coverage; declared features are not wildlife observations or assessed impacts. No proposed AOI or reviewed ecological baseline was invented.

C48–C50 preserve the separate editable acquisition/review register under `data.evidence_workspace`, using `scenario.inputs.category_inputs.C49`. Valid previews are temporary; saving creates a new revision. Automatic collection does not approve a review row.

Specifications/prompts retain required specialist outputs where evidence and methods are still missing. Preserve scope, raw hashes, units, unavailable evidence and expert review boundaries. [Handover](../../PROJECT_HANDOVER.md).
