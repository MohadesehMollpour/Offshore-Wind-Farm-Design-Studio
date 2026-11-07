### C31 — Inter-array cables and string topology  _(domain: electrical)_

- **Mandatory inputs:**
  - layout
  - WTG current/cable ratings
- **Expected results:**
  - topology
  - kV
  - length
  - N-1 rationale
- **Visualization:** network schematic
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C31. Controller: src/controller.py. Status: screening_calculation.

Chart contract: Array cable network map; Electrical loading per string chart. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Editable analysis workspace (2026-11-01)

Implementation: **screening_calculation**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C31`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

Editable settings: Maximum turbines per conceptual string [turbines], Assumed array voltage [kV], Assumed power factor [fraction]. Defaults are explicit planning assumptions; blank inputs remain unavailable.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **planning calculation**; evidence maturity `planning_workspace_not_verified`. Classification is snapshot-specific and is not an engineering completion rating.

Preliminary grouping into strings, collector assumed at local (0,0), straight segments between sorted positions. No cable ampacity, routing exclusion, burial, redundancy or protection solution.

Implementation entry points: `backend/work_packages.py` and `dashboard/src/WorkPackagePage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
