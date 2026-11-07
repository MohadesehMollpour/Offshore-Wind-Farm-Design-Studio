# C69 — Management dashboard and interactive geospatial layers

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Seventy-node dependency explorer and linked result context; graph structure is not validated causal impact or automatic optimization.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **built-in calculation/project view**, result `needs-review`, evidence maturity `user_supplied_or_assumed`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/engine.py and backend/external_analysis.py`; view `dashboard/src/main.tsx`. The category adapter is `src/controller.py`. Ownership: [A20](../../agents/A20_dashboard/AGENT.md).

## Evidence and continuation

Required domain inputs: validated data, scenarios. Expected specialist outputs: live filters, KPI tiles, maps, reproducible views. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
