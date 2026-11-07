### C21 — Power curve, cut-in, cut-out and rated output  _(domain: turbine)_

- **Mandatory inputs:**
  - verified/manufacturer power curves
- **Expected results:**
  - power curve provenance
  - annual production inputs
- **Visualization:** power curve + density overlay
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C21. Controller: src/controller.py. Status: calculation.

Chart contract: Power curve with rated operating bands; Energy contribution by wind-speed bin. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


## Explicit regional reference calculation

The explicit regional_screening_case plus scope-checked overview_inputs and era5_wind bindings enable a regional reference estimate. Published IEA turbine data, DESNZ 2024-real cost benchmarks, Arup loss benchmarks and declared electrical/curtailment/shear assumptions remain distinguishable. No proposed AOI or feasible layout is invented. Regional results do not supply P90, NPV, IRR or payback. See reports/management_overview_data.md and backend/overview_data.py.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `published_data_with_modelling_assumptions`. Classification is snapshot-specific and is not an engineering completion rating.

Published theoretical IEA 15 MW curve for the explicit regional case, or the labelled cubic proxy for configured site inputs.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
