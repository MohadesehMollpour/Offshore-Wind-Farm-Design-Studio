### C07 — Historical wind speed at several hub heights  _(domain: resource)_

- **Mandatory inputs:**
  - GWA
  - ERA5
  - site
- **Expected results:**
  - time series
  - means
  - speed ranges
  - missingness
- **Visualization:** time-series bands
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C07. Controller: src/controller.py. Status: calculation.

Chart contract: Hub-height wind speed time series; Wind speed by height plot. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Public-data screening extension (0.2.0)

A configured publisher adapter can populate preliminary views. Preserve the fixed category ID and original required full-study chart contract. Label any simpler source-supported screening view accurately and retain an explicit gap for missing long-term, surveyed or engineering evidence. Source selection, revision binding, stale status, citation and raw-data export are required.


## 2026-11-01 extension

Monthly wind box plots, thresholds and UTC source-period selection are implemented in backend/wind_history.py and dashboard/src/WindHistory.tsx. The recent operational wind adapter is independent of the long-term overview input. Threshold comparisons require matching reference heights and remain illustrative wind-only planning context. See reports/wind_history_and_hornsea_reference.md.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

Monthly wind distributions, recent/calendar-year periods, 10/100 m height, units, height-matched sailing/O&M limits and CSV/SVG exports.

Implementation entry points: `backend/wind_history.py and backend/engine.py` and `dashboard/src/WindHistory.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
