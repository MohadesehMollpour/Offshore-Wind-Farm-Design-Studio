# C47 data sources and required evidence

Required domain evidence:

- electric demand
- platform consent

## Connected and reference inputs

No dedicated direct provider routing is declared for this category. It can use the documented upstream/scoped model inputs or user-supplied planning/evidence records; this is not a claim that the whole project lacks connected sources.

The stored revision-17 result uses scoped provider provenance from `era5_wind`, `overview_inputs`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

A structured evidence and review register for the selected snapshot. Missing inputs remain missing.

Reference gaps include:

- Supply the required numeric inputs or connect the scoped source to calculate this screening view.
- electric demand: missing; assign an owner and supply a source/review record.
- platform consent: missing; assign an owner and supply a source/review record.
- Screening calculations and user review records do not establish engineering, legal or operational approval.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
