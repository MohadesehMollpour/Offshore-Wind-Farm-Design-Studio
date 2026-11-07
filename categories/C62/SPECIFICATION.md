### C62 — Construction/operations HSE and emergency response  _(domain: hse)_

- **Mandatory inputs:**
  - HAZID
  - activities
  - operators
- **Expected results:**
  - risk log
  - ALARP decisions
  - emergency plan
- **Visualization:** risk matrix + bow-tie
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C62. Controller: src/controller.py. Status: risk_register.

Chart contract: Risk probability vs consequence matrix; Safety controls and readiness timeline. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Editable analysis workspace (2026-11-01)

Implementation: **risk_register**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C62`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

Hazard templates start unassessed. User-assigned ordinal scores and proposed residual scores do not establish probability, tolerability or ALARP. Reviewed records require controls, initial scores, a responsible owner and evidence. HSE, G+ and MCA guidance links are reference material rather than site approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **HSE risk register**; evidence maturity `planning_workspace_not_verified`. Classification is snapshot-specific and is not an engineering completion rating.

Editable 1–5 ordinal likelihood × consequence matrix, with separate proposed residual scores. Scores are user assessments, not measured probabilities. No score, completed form or proposed control establishes ALARP or an approved emergency plan.

Implementation entry points: `backend/work_packages.py` and `dashboard/src/WorkPackagePage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
