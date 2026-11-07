# C07 data sources and required evidence

Required domain evidence:

- GWA
- ERA5
- site

## Connected and reference inputs

Direct provider routing in the current registry: `operations_wind`, `era5_wind`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `era5_wind`, `operations_wind`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

Monthly wind distributions, recent/calendar-year periods, 10/100 m height, units, height-matched sailing/O&M limits and CSV/SVG exports.

Reference gaps include:

- Regional gridded reanalysis, not a physical sensor or bankable wind assessment.
- 10 m and 100 m only; no implicit extrapolation to the assumed 150 m turbine hub.
- This reference point is not the proposed wind-farm AOI.
- Hourly wind-only planning context; no gust, wave or vessel/task approval is inferred.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
