# C05 data sources and required evidence

Required domain evidence:

- AIS/routes
- AOI

## Connected and reference inputs

Direct provider routing in the current registry: `site_screening`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `site_screening`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

AIS raster vintage/opacity/threshold and linked sample exposure; not collision risk or aviation clearance.

Reference gaps include:

- Regional reference screening; no proposed AOI, environmental consent or available seabed is established.
- Geodesic coast/port distances are not navigable sea routes, export cable routes or vessel access times.
- AIS samples are 25 raster-cell point queries on a 10 km-spaced grid, not an area-weighted AOI exposure or collision-risk assessment.
- A missing AIS value is unavailable, not zero traffic.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
