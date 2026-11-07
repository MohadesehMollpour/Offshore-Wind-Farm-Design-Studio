### C64 — Stakeholders and community engagement  _(domain: people)_

- **Mandatory inputs:**
  - local actors
  - authorities
- **Expected results:**
  - stakeholder map
  - consultation plan
- **Visualization:** power-interest matrix
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C64. Controller: src/controller.py. Status: stakeholder_register.

Chart contract: Stakeholder influence-interest matrix; Engagement milestones timeline. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Editable analysis workspace (2026-11-01)

Implementation: **stakeholder_register**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C64`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **stakeholder register**; evidence maturity `planning_workspace_not_verified`. Classification is snapshot-specific and is not an engineering completion rating.

Editable influence/interest and engagement register. Named groups are a planning checklist; no contact, consultation, agreement or stakeholder preference is asserted.

Implementation entry points: `backend/work_packages.py` and `dashboard/src/WorkPackagePage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
