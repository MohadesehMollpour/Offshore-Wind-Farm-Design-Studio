### C05 — Navigation, shipping and aviation constraints  _(domain: site)_

- **Mandatory inputs:**
  - AIS/routes
  - AOI
- **Expected results:**
  - traffic density
  - corridors
  - aviation restrictions
- **Visualization:** traffic heatmap
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C05. Controller: src/controller.py. Status: source_backed_regional_reference_screening.

Chart contract: Shipping and aviation density overlay; Constraint exposure by zone. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


### Interactive screening implementation
Interactive EMODnet AIS WMS overlay with explicit vintage, opacity, 25 preserved point samples, adjustable density threshold and linked zone-exposure bars. Missing samples stay missing. Aviation coverage remains unavailable. Exposure is a percentage of valid point samples, not AOI area or collision risk. The 2024 vintage has reduced satellite coverage from June; 2023 is the default.

Shared implementation: backend/site_data.py and dashboard/src/SitePlots.tsx. A scenario must bind the site_screening dataset; source-free snapshots retain the explicit missing-data state.

## Editable analysis workspace (2026-11-01)

Implementation: **source_screening_with_workspace**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C05`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

AIS raster vintage/opacity/threshold and linked sample exposure; not collision risk or aviation clearance.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/SitePlots.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
