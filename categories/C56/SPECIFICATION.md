### C56 — Wind turbine accessibility  _(domain: om)_

- **Mandatory inputs:**
  - distance
  - weather windows
  - ports
- **Expected results:**
  - strategy cost and feasible transfer days
- **Visualization:** accessibility calendar
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C56. Controller: src/controller.py. Status: regional_accessibility_screening.

Implemented charts: monthly Hs box plots with editable threshold; monthly joint eligibility; wind–Hs frequency distribution with month selection; daily eligible-hour calendar. Unknown selected criteria cannot pass. Continuous windows count every overlapping start and explicitly do not count independent trips. V/C/SH/L/W/R mean visibility/current/significant wave height/daylight/10 m wind/rain. Rain uses total precipitation as a conservative proxy. L = daylight is user-confirmed.

Data: access_metocean joins the latest twelve complete available months of ERA5 wind/precipitation/daylight, ERA5-Ocean waves and Meteo-France SMOC currents in UTC. Convert source current km/h to m/s. Visibility may be missing. Use provider grid coordinates and resolution, not a claimed point sensor. Preserve raw responses, scope, source identifiers, licences and checksums. Quantiles use linear interpolation at (n−1)p; observed whiskers within 1.5×IQR.

Default thresholds (10 m wind ≤10 m/s, Hs ≤1.5 m, daylight, continuous 12 h) are illustrative. Other criteria are excluded until selected. No approved vessel or transfer limits are implied. Navigable port routes, vessel motions, gusts, transfer/contingency time, task procedures and strategy costs remain gaps.

Linked route /projects/{project_id}/twin renders selected C23 computed positions, or an explicitly conceptual arrangement when C23 is unavailable. Illustrative Jensen hub-point wind deficits do not reduce historical 10 m access wind. Regional Hs stays uniform throughout the farm; no unsupported wave-shelter credit is applied. Ocean animation is procedural, not a wave solver. All saved accessibility preferences create immutable revisions.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

Joint historical wind/wave/current/daylight/precipitation, wave boxes and continuous-window screening. L means Daylight; missing selected visibility remains unknown.

Implementation entry points: `backend/accessibility.py` and `dashboard/src/AccessibilityPage.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
