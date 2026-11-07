# C54 — Supply chain, lead times and procurement

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Seven-view Lattice explorer with component anatomy, tracing/map, landscape/Sankey, disruption cases, local queries and ontology; separate revision-bound procurement evidence register.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **evidence register**, result `needs-review`, evidence maturity `source_and_planning_assumptions`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/supply_reference.py and backend/work_packages.py`; view `dashboard/src/SupplyChainWorkspace.tsx`. The category adapter is `src/controller.py`. Ownership: [A15](../../agents/A15_construction/AGENT.md).

## Evidence and continuation

Required domain inputs: vendors, durations. Expected specialist outputs: procurement critical items and cost ranges. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

The editable workspace uses `scenario.inputs.category_inputs.C54`, validated from `config/work_packages.json`. Preview is temporary; saving creates a revision. Review rows are user records, not external approval. The directory is shared contextual data, not a farm-qualified shortlist. Explorer filters/queries are temporary and do not change the saved support design, programme or prices. See [the Lattice integration notes](../../reports/c54_lattice_workspace.md). Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
