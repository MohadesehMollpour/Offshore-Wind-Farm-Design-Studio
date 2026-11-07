### C03 — Site suitability and multi-criteria comparison  _(domain: site)_

- **Mandatory inputs:**
  - site candidates
  - weight ranges
- **Expected results:**
  - score matrix
  - Pareto options
  - weight sensitivity
- **Visualization:** parallel-coordinates + rank bars
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C03. Controller: src/controller.py. Status: source_backed_regional_reference_screening.

Chart contract: Multi-criteria ranking bars; Sensitivity / parallel-coordinates plot. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


### Interactive screening implementation
Interactive published-agreement reference comparison with three adjustable weights, normalized rank bars, sensitivity curves, parallel coordinates, selected-reference metrics and CSV export. Preferences can be pinned in a new immutable revision. Existing agreements remain ineligible as new sites; these three metrics are not a complete suitability assessment.

Shared implementation: backend/site_data.py and dashboard/src/SitePlots.tsx. A scenario must bind the site_screening dataset; source-free snapshots retain the explicit missing-data state.

## Editable analysis workspace (2026-11-01)

Implementation: **source_screening_with_workspace**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C03`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

Adjustable regional screening preferences, linked ranking/sensitivity, parallel coordinates and Pareto context.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/SitePlots.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
