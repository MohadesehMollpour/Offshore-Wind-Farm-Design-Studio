### C29 — Monthly production and hourly generation proxy  _(domain: energy)_

- **Mandatory inputs:**
  - wind hourly and turbine curve
- **Expected results:**
  - 8760/8784 hourly simulation
  - seasons
- **Visualization:** hourly heatmap
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C29. Controller: src/controller.py. Status: evidence_register.

Chart contract: Monthly energy production line; Hourly proxy heatmap with methodology label. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


## Explicit regional reference calculation

The explicit regional_screening_case plus scope-checked overview_inputs and era5_wind bindings enable a regional reference estimate. Published IEA turbine data, DESNZ 2024-real cost benchmarks, Arup loss benchmarks and declared electrical/curtailment/shear assumptions remain distinguishable. No proposed AOI or feasible layout is invented. Regional results do not supply P90, NPV, IRR or payback. See reports/management_overview_data.md and backend/overview_data.py.

## Editable analysis workspace (2026-11-01)

Implementation: **source_screening_with_workspace**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C29`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `published_data_with_modelling_assumptions`. Classification is snapshot-specific and is not an engineering completion rating.

Monthly/weather-year generation context from the explicit regional model; not measured plant output.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
