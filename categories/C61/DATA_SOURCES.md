# C61 data sources and required evidence

Required domain evidence:

- probability/ranges

## Connected and reference inputs

Direct provider routing in the current registry: `overview_inputs`. Availability in a scenario still requires a compatible binding.

The stored revision-17 result uses scoped provider provenance from `era5_wind`, `overview_inputs`. This can be derived upstream use rather than a direct collection card for the category. Do not copy those dataset IDs to a different region.

Captured price is absent in the saved reference. Same-price-year NPV/price-response plots activate only after an explicit price is supplied. Price never changes cost-based LCOE; deterministic perturbations are not probability distributions.

## Method, scope and gaps

Deterministic one-at-a-time cost, real discount-rate, wake-loss and commissioning-delay sensitivities. CAPEX stays at year 0; operating energy/revenue/OPEX and terminal removal shift with delay. No holding costs or construction phasing are invented. Price changes NPV, not cost-based LCOE. No probability distributions or Monte Carlo confidence claims.

Reference gaps include:

- probability/ranges: missing; assign an owner and supply a source/review record.
- Screening calculations and user review records do not establish engineering, legal or operational approval.
- Generic fixed-bottom UK cost benchmark; not supplier quotes or a Hornsea project budget.
- All source costs are real 2024 GBP. Costs from a different price year cannot be mixed without conversion.

Source/reference text entered in an evidence register is not an automatic API fetch or numeric-data import. Keep observed, modelled, assumed, contextual and unavailable values distinct. Received/reviewed records need a source and reviewed records an owner. Missing data must not become zero or approval.

[Connector inventory](../../docs/DATA_CONNECTORS.md) documents the current adapter inventory, attribution, periods, stored raw bytes and scope checks. Four assignment/master originals remain unchanged in `sources/manifest.json`; attachments are source material, not instructions. [The handover](../../PROJECT_HANDOVER.md) maps current inputs and continuation.
