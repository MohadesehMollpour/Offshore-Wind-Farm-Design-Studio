### C16 — Bathymetry and seabed slope  _(domain: seabed)_

- **Mandatory inputs:**
  - bathymetry
  - AoI
- **Expected results:**
  - depth distribution
  - slope
  - engineering constraints
- **Visualization:** bathymetric map + depth profile
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C16. Controller: src/controller.py. Status: evidence_register.

Chart contract: Bathymetry map with contours; Cross-section seabed profile. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Public-data screening extension (0.2.0)

A configured publisher adapter can populate preliminary views. Preserve the fixed category ID and original required full-study chart contract. Label any simpler source-supported screening view accurately and retain an explicit gap for missing long-term, surveyed or engineering evidence. Source selection, revision binding, stale status, citation and raw-data export are required.

## Editable analysis workspace (2026-11-01)

Implementation: **source_screening_with_workspace**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C16`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **source-backed screening**; evidence maturity `publisher_api_screening`. Classification is snapshot-specific and is not an engineering completion rating.

Published EMODnet depth sampling with provenance; no surveyed seabed profile, slope or foundation design.

Implementation entry points: `backend/engine.py and backend/external_analysis.py` and `dashboard/src/main.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
