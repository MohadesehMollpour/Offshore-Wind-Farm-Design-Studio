# C09 data sources and required evidence

Required domain evidence:

- wind series

## Connected and reference inputs

Direct provider routing in the current registry: `era5_wind`. Availability in a scenario still requires a compatible binding.

The saved reference result has no public-provider provenance for this package; numeric assumptions, user records, built-in project metadata and contextual attachments must retain their own basis.

## Method, scope and gaps

Descriptive monthly and UTC-hour historical wind means; no long-term correction or design extremes.

Reference gaps include:

- wind series: missing; assign an owner and supply a source/review record.
- Screening calculations and user review records do not establish engineering, legal or operational approval.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
