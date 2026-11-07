# C08 — Wind direction and sector frequency

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Meteorological FROM sector frequencies, speed-stacked rose and calm accounting with explicit sample-height conventions.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **source-backed screening**, result `needs-review`, evidence maturity `publisher_api_screening`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/engine.py and backend/external_analysis.py`; view `dashboard/src/main.tsx`. The category adapter is `src/controller.py`. Ownership: [A05](../../agents/A05_resource/AGENT.md).

## Evidence and continuation

Required domain inputs: wind U, V, time. Expected specialist outputs: direction sector frequency and wind-energy-weighted frequency. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
