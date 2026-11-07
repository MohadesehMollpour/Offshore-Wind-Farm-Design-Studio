# C37 — Existing, consented and planned wind farms

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Official agreements/status plus a separate supplied Hornsea comparison explorer (25 records and one map-only record).

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **source-backed screening**, result `needs-review`, evidence maturity `publisher_api_screening`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/engine.py and backend/external_analysis.py`; view `dashboard/src/AttachedFarmExplorer.tsx`. The category adapter is `src/controller.py`. Ownership: [A11](../../agents/A11_nearby/AGENT.md).

## Evidence and continuation

Required domain inputs: leases, project databases. Expected specialist outputs: names, polygons, status, MW, distance, citations. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
