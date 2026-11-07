# C03 — Site suitability and multi-criteria comparison

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Adjustable regional screening preferences, linked ranking/sensitivity, parallel coordinates and Pareto context.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **source-backed screening**, result `needs-review`, evidence maturity `publisher_api_screening`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/engine.py and backend/external_analysis.py`; view `dashboard/src/SitePlots.tsx`. The category adapter is `src/controller.py`. Ownership: [A04](../../agents/A04_site/AGENT.md).

## Evidence and continuation

Required domain inputs: site candidates, weight ranges. Expected specialist outputs: score matrix, Pareto options, weight sensitivity. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
