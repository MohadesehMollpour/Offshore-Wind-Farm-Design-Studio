### C54 — Supply chain, lead times and procurement  _(domain: construction)_

- **Mandatory inputs:**
  - vendors
  - durations
- **Expected results:**
  - procurement critical items and cost ranges
- **Visualization:** dependency graph
- **Classification:** core
- **Acceptance criteria:**
  - Units and method explicit
  - At least one primary source or clear data-gap statement
  - Confidence and uncertainty stated
  - Machine-readable output
  - Engineering and regulatory caveats

## Local implementation
Route: /projects/{project_id}/categories/C54. Controller: src/controller.py. Status: evidence_register.

Chart contract: Supplier lead-time schedule; Procurement risk matrix. Missing datasets must produce an empty state with acquisition actions. All outputs bind to an immutable scenario.

## Lattice supply-chain explorer (2026-11-01)

C54 uses the attached Lattice design, with seven interactive views: command center, turbine anatomy, component tracing/map, supply landscape heatmap/Sankey, disruption scenarios, deterministic graph questions and ontology. The UK directory snapshot is dated 14 October 2026 (885 profiles, 34 components, 214 links), preserved with checksums and bundled locally. It is contextual evidence, not a qualified shortlist or vendor capacity/lead-time forecast. Temporary explorer filters do not change the saved farm design. The procurement evidence register remains revision-bound and does not auto-complete from directory counts.

See [C54 implementation, model and continuation notes](../../reports/c54_lattice_workspace.md) for source handling, assumptions and remaining procurement evidence.

## Editable analysis workspace (2026-11-01)

Implementation: **evidence_register**. Numeric parameters and evidence/register inputs are declared in `config/work_packages.json`, validated in `backend/work_packages.py`, and saved in `scenario.inputs.category_inputs.C54`. Draft previews do not persist results; saving creates a new immutable revision. The UI includes editable inputs, validated JSON import/export, source/owner/review fields, method notes and quantitative charts when their data is available. The original expected engineering outputs above remain requirements, not claims of approval.

## Current implementation and documentation checkpoint

Updated 1 November 2026 against implementation `f3c13f7` and reference revision 17. Current reference classification: **evidence register**; evidence maturity `source_and_planning_assumptions`. Classification is snapshot-specific and is not an engineering completion rating.

Seven-view Lattice explorer with component anatomy, tracing/map, landscape/Sankey, disruption cases, local queries and ontology; separate revision-bound procurement evidence register.

Implementation entry points: `backend/supply_reference.py and backend/work_packages.py` and `dashboard/src/SupplyChainWorkspace.tsx`. The original expected outputs/chart contracts above remain the target study requirements; current screens may be contextual, preliminary or evidence-only. [Current source guide](DATA_SOURCES.md), [package overview](README.md) and [all-category register](../../docs/CATEGORIES.md) describe the implemented subset and remaining inputs.
