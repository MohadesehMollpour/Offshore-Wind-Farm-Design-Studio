### C61 — Price, discount, wake and schedule sensitivity  _(domain: finance)_

- **Mandatory inputs:**
  - probability/ranges
- **Expected results:**
  - scenario results
  - Monte Carlo if justified
- **Visualization:** tornado + spider lines
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C61. Controller: src/controller.py. Status: calculation.

Chart contract: Financial sensitivity tornado; Scenario response surface / heatmap. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


## Explicit regional reference calculation

The explicit regional_screening_case plus scope-checked overview_inputs and era5_wind bindings enable a regional reference estimate. Published IEA turbine data, DESNZ 2024-real cost benchmarks, Arup loss benchmarks and declared electrical/curtailment/shear assumptions remain distinguishable. No proposed AOI or feasible layout is invented. Regional results do not supply P90, NPV, IRR or payback. See reports/management_overview_data.md and backend/overview_data.py.

## Editable analysis workspace (2026-11-01)

Implementation: **financial_sensitivity**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C61`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

Editable settings: Assumed captured electricity price [real GBP/MWh], Cost and price sensitivity range [± %], Discount-rate sensitivity range [± percentage points], Wake-loss sensitivity range [± percentage points], Maximum commissioning delay [whole years]. Defaults are explicit planning assumptions; blank inputs remain unavailable.

Price, real discount rate, CAPEX, fixed OPEX, wake loss and commissioning delay are varied independently. Cost-based LCOE is independent of selling price. A same-price-year captured-price input is required for NPV and the price/rate heatmap; no price or probability distributions are invented.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **planning calculation**; evidence maturity `source_and_planning_assumptions`. Classification is snapshot-specific and is not an engineering completion rating.

Deterministic one-at-a-time cost, real discount-rate, wake-loss and commissioning-delay sensitivities. CAPEX stays at year 0; operating energy/revenue/OPEX and terminal removal shift with delay. No holding costs or construction phasing are invented. Price changes NPV, not cost-based LCOE. No probability distributions or Monte Carlo confidence claims.

Implementation entry points: `backend/sensitivity.py` and `dashboard/src/WorkPackagePage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
