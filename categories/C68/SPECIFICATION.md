### C68 — AI disclosure, authorship, evidence and learning  _(domain: quality)_

- **Mandatory inputs:**
  - agent logs
  - student input
- **Expected results:**
  - AI per section
  - original contribution
  - critique records
- **Visualization:** learning audit table
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C68. Controller: src/controller.py. Status: calculation.

Chart contract: Per-section AI disclosure matrix; Human contributions and source traceability chart. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **built-in calculation/project view**; evidence maturity `user_supplied_or_assumed`. Classification is snapshot-specific and is not an engineering completion rating.

Human/AI section contribution/disclosure coverage; actual authorship and review must be entered.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
