### C23 — Turbine placement and spacing  _(domain: layout)_

- **Mandatory inputs:**
  - polygon
  - exclusions
  - D
  - wind rose
- **Expected results:**
  - turbine point geometries
  - spacing
  - density
- **Visualization:** interactive turbine map
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C23. Controller: src/controller.py. Status: calculation.

Chart contract: Scaled turbine layout map; Minimum-spacing distribution plot. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **required inputs missing**; evidence maturity `unavailable`. Classification is snapshot-specific and is not an engineering completion rating.

Exclusion/rotor-envelope-aware preliminary layout in a supplied AOI; reference geometry remains missing.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
