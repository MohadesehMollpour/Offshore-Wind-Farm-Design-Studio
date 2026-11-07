# C56 data sources and required evidence

Required domain evidence:

- distance
- weather windows
- ports

## Connected and reference inputs

Direct provider routing in the current registry: `access_metocean`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `access_metocean`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

Reference access history has 8,760 matched hours, 2025-10-01–2026-09-30; visibility is missing. L = Daylight. Saved revision 17 uses Hs ≤2.0 m, not the 1.5 m factory example. Current speed units are converted explicitly and total precipitation is a conservative rain proxy. Wave grids do not resolve per-turbine shelter.

## Method, scope and gaps

Joint historical wind/wave/current/daylight/precipitation, wave boxes and continuous-window screening. L means Daylight; missing selected visibility remains unknown.

Reference gaps include:

- ERA5 archive does not provide visibility at this location/period; V remains unknown when selected.
- Regional model histories, not live instrument observations or operational approval.
- Wave and wind grid cells differ in position and resolution; a time join does not establish farm-scale spatial shelter.
- Visibility remains unavailable; no missing criterion is replaced by an assumed good condition.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
