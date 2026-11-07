# C07 — Historical wind speed at several hub heights

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Monthly wind distributions, recent/calendar-year periods, 10/100 m height, units, height-matched sailing/O&M limits and CSV/SVG exports.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **source-backed screening**, result `needs-review`, evidence maturity `publisher_api_screening`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/wind_history.py and backend/engine.py`; view `dashboard/src/WindHistory.tsx`. The category adapter is `src/controller.py`. Ownership: [A05](../../agents/A05_resource/AGENT.md).

## Evidence and continuation

Required domain inputs: GWA, ERA5, site. Expected specialist outputs: time series, means, speed ranges, missingness. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
