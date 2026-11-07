# C37 data sources and required evidence

Required domain evidence:

- leases
- project databases

## Connected and reference inputs

Direct provider routing in the current registry: `tce_wind`, `repd`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `repd`, `tce_wind`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

The supplied Hornsea HTML is a separate, unverified contextual snapshot: embedded JSON is parsed without executing its scripts. Its capacity factors/statuses never feed overview energy/finance. See [reference methods](../../reports/wind_history_and_hornsea_reference.md).

## Method, scope and gaps

Official agreements/status plus a separate supplied Hornsea comparison explorer (25 records and one map-only record).

Reference gaps include:

- Bounding-envelope discovery is not an AOI intersection or permitted development area.
- Reported status is publisher metadata, not an independent commercial or engineering certification.
- Quarterly planning-register snapshot, not live operating status.
- Capacity, turbine count and turbine rating may refer to different planning revisions; do not assume they reconcile.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
