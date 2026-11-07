### C53 — Foundation, cable, turbine installation sequence  _(domain: construction)_

- **Mandatory inputs:**
  - design and weather windows
- **Expected results:**
  - installation method statement and sequencing
- **Visualization:** Gantt with weather risk
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C53. Controller: src/controller.py. Status: screening_calculation.

Chart contract: Installation sequencing Gantt; Marine weather-delay risk chart. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Editable analysis workspace (2026-11-01)

Implementation: **screening_calculation**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C53`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

Editable settings: Foundation installation [working days/turbine], Turbine erection [working days/turbine], Cable work [working days/turbine], Assumed workable installation fraction [fraction]. Defaults are explicit planning assumptions; blank inputs remain unavailable.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **planning calculation**; evidence maturity `planning_workspace_not_verified`. Classification is snapshot-specific and is not an engineering completion rating.

Turbine count × declared workdays / assumed workable installation fraction. Serial task allowance, not a vessel-optimised schedule; crew-transfer weather criteria are not substituted for installation limits.

Implementation entry points: `backend/work_packages.py` and `dashboard/src/WorkPackagePage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
