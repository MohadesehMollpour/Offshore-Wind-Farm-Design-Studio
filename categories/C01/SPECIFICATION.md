### C01 — Candidate AOI polygon and coordinates  _(domain: site)_

- **Mandatory inputs:**
  - polygon
  - CRS
  - shoreline
- **Expected results:**
  - valid polygon
  - centroid
  - area km2
  - data bounds
- **Visualization:** GIS map
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C01. Controller: src/controller.py. Status: calculation.

Chart contract: Interactive AOI polygon map; Site-area and boundary-quality summary. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **required inputs missing**; evidence maturity `unavailable`. Classification is snapshot-specific and is not an engineering completion rating.

Validation of a supplied EPSG:4326 polygon, projected area and boundary quality; reference revision 17 has no proposed AOI.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
