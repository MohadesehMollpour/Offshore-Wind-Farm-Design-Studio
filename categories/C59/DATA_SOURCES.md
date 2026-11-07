# C59 data sources and required evidence

Required domain evidence:

- O&M strategy
- finance assumptions

## Connected and reference inputs

Direct provider routing in the current registry: `overview_inputs`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `era5_wind`, `overview_inputs`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

Declared or explicit-regional benchmark operating/decommissioning costs with a consistent real price year.

Reference gaps include:

- Generic fixed-bottom UK cost benchmark; not supplier quotes or a Hornsea project budget.
- All source costs are real 2024 GBP. Costs from a different price year cannot be mixed without conversion.
- Theoretical IEA reference curve is not a certified commercial turbine curve.
- Arup wake/availability benchmarks are based on a small survey; they are not a layout wake or reliability model.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
