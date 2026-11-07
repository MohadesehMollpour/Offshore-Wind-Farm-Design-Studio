### C59 — OPEX, insurance, tax and decommissioning  _(domain: finance)_

- **Mandatory inputs:**
  - O&M strategy
  - finance assumptions
- **Expected results:**
  - annual cash flow input table
- **Visualization:** stacked lifecycle cost
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C59. Controller: src/controller.py. Status: calculation.

Chart contract: OPEX and decommissioning lifecycle line; Cost uncertainty ranges. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


## Explicit regional reference calculation

The explicit regional_screening_case plus scope-checked overview_inputs and era5_wind bindings enable a regional reference estimate. Published IEA turbine data, DESNZ 2024-real cost benchmarks, Arup loss benchmarks and declared electrical/curtailment/shear assumptions remain distinguishable. No proposed AOI or feasible layout is invented. Regional results do not supply P90, NPV, IRR or payback. See reports/management_overview_data.md and backend/overview_data.py.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `published_data_with_modelling_assumptions`. Classification is snapshot-specific and is not an engineering completion rating.

Declared or explicit-regional benchmark operating/decommissioning costs with a consistent real price year.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
