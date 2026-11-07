### C08 — Wind direction and sector frequency  _(domain: resource)_

- **Mandatory inputs:**
  - wind U
  - V
  - time
- **Expected results:**
  - direction sector frequency and wind-energy-weighted frequency
- **Visualization:** circular barplot + conventional wind rose
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C08. Controller: src/controller.py. Status: calculation.

Chart contract: Interactive circular sector bar / dominant wind-from direction, IEA-inspired controls; Conventional stacked wind rose and direction-specific energy contribution. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Public-data screening extension (0.2.0)

A configured publisher adapter can populate preliminary views. Preserve the fixed category ID and original required full-study chart contract. Label any simpler source-supported screening view accurately and retain an explicit gap for missing long-term, surveyed or engineering evidence. Source selection, revision binding, stale status, citation and raw-data export are required.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

Meteorological FROM sector frequencies, speed-stacked rose and calm accounting with explicit sample-height conventions.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
