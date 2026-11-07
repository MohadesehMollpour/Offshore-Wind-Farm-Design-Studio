# C66 — Repowering, reuse and decommissioning

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Terminal benchmark/declared cost plus explicitly additional contingency, less assumed salvage, discounted at the declared real rate. Timing alternatives do not imply legal permission to defer removal.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **planning calculation**, result `needs-review`, evidence maturity `source_and_planning_assumptions`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/work_packages.py`; view `dashboard/src/WorkPackagePage.tsx`. The category adapter is `src/controller.py`. Ownership: [A19](../../agents/A19_schedule/AGENT.md).

## Evidence and continuation

Required domain inputs: asset inventory, permit conditions. Expected specialist outputs: end-of-life options and restoration plan. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

The editable workspace uses `scenario.inputs.category_inputs.C66`, validated from `config/work_packages.json`. Preview is temporary; saving creates a revision. Review rows are user records, not external approval. Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
