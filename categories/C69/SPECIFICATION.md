### C69 — Management dashboard and interactive geospatial layers  _(domain: dashboard)_

- **Mandatory inputs:**
  - validated data
  - scenarios
- **Expected results:**
  - live filters
  - KPI tiles
  - maps
  - reproducible views
- **Visualization:** dashboard panels
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C69. Controller: src/controller.py. Status: calculation.

Chart contract: Radial, interactive 70-criterion dependency and importance explorer; GIS layer coverage, provenance, and cross-category KPI scorecards. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **built-in calculation/project view**; evidence maturity `user_supplied_or_assumed`. Classification is snapshot-specific and is not an engineering completion rating.

Seventy-node dependency explorer and linked result context; graph structure is not validated causal impact or automatic optimization.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
