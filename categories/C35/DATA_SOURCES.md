# C35 data sources and required evidence

Required domain evidence:

- NESO boundaries
- limits
- costs

## Connected and reference inputs

Direct provider routing in the current registry: `neso_tec`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `neso_tec`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

## Method, scope and gaps

Published TEC register context; no inferred network boundary capacity, constraint price or headroom.

Reference gaps include:

- Hornsea name-filtered register records, not spare grid headroom or an offer to connect this project.
- Stages, technology types and cumulative capacities may duplicate or overlap; do not sum cumulative rows.
- Register status can differ from planning/lease records; retain the original vintages and labels.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
