# C08 data sources and required evidence

Required domain evidence:

- wind U
- V
- time

## Connected and reference inputs

Direct provider routing in the current registry: `era5_wind`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `era5_wind`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

Meteorological FROM sector frequencies, speed-stacked rose and calm accounting with explicit sample-height conventions.

Reference gaps include:

- Regional gridded reanalysis, not a physical sensor or bankable wind assessment.
- 10 m and 100 m only; no implicit extrapolation to the assumed 150 m turbine hub.
- This reference point is not the proposed wind-farm AOI.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
