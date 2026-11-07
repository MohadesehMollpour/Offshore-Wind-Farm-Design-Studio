### C04 — Distance to coast, ports and substations  _(domain: site)_

- **Mandatory inputs:**
  - AOI
  - route graph
- **Expected results:**
  - geodesic and navigable route distance separately
- **Visualization:** distance network map
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C04. Controller: src/controller.py. Status: source_backed_regional_reference_screening.

Chart contract: Coast/port/grid distance map; Travel-distance comparison bars. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.


### Interactive screening implementation
Interactive linked map and bars for generalized coast and published main-port geodesic distances. Filters, selection, vessel-speed controls and straight-line time proxies are supported. Grid coordinates and navigable routes remain unavailable; the port list is not a verified offshore construction/O&M capability inventory.

Shared implementation: backend/site_data.py and dashboard/src/SitePlots.tsx. A scenario must bind the site_screening dataset; source-free snapshots retain the explicit missing-data state.

## Editable analysis workspace (2026-11-01)

Implementation: **source_screening_with_workspace**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C04`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

Coast/main-port map and distances with vessel-speed controls; straight-line proxies, not navigable routes.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/SitePlots.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
