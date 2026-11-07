### C30 — Energy price capture and curtailment exposure  _(domain: energy)_

- **Mandatory inputs:**
  - production
  - market data
  - grid restrictions
- **Expected results:**
  - captured price proxy
  - curtailment cases
- **Visualization:** time-series scenario fan
- **Classification:** extension
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C30. Controller: src/controller.py. Status: screening_calculation.

Chart contract: Price capture vs output plot; Curtailment scenario bars. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Editable analysis workspace (2026-11-01)

Implementation: **screening_calculation**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C30`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

Editable settings: Assumed baseload price [GBP/MWh], Capture ratio [fraction], Additional curtailment for this sensitivity [%]. Defaults are explicit planning assumptions; blank inputs remain unavailable.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **evidence register**; evidence maturity `source_and_planning_assumptions`. Classification is snapshot-specific and is not an engineering completion rating.

A structured evidence and review register for the selected snapshot. Missing inputs remain missing.

Implementation entry points: `backend/work_packages.py` and `dashboard/src/WorkPackagePage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
