# C13 data sources and required evidence

Required domain evidence:

- wave time series
- limits

## Connected and reference inputs

Direct provider routing in the current registry: `marine`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `marine`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

Seven-day wave-height/period forecast context; separate from the historical C56 access climate.

Reference gaps include:

- Seven-day model forecast; not an observed or long-term wave climate.
- No installation weather-window, safety or monthly access conclusion can be inferred from this short forecast.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
