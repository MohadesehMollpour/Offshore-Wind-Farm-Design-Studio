# C61 — Price, discount, wake and schedule sensitivity

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Deterministic one-at-a-time cost, real discount-rate, wake-loss and commissioning-delay sensitivities. CAPEX stays at year 0; operating energy/revenue/OPEX and terminal removal shift with delay. No holding costs or construction phasing are invented. Price changes NPV, not cost-based LCOE. No probability distributions or Monte Carlo confidence claims.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **planning calculation**, result `needs-review`, evidence maturity `source_and_planning_assumptions`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/sensitivity.py`; view `dashboard/src/WorkPackagePage.tsx`. The category adapter is `src/controller.py`. Ownership: [A17](../../agents/A17_finance/AGENT.md).

## Evidence and continuation

Required domain inputs: probability/ranges. Expected specialist outputs: scenario results, Monte Carlo if justified. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

The editable workspace uses `scenario.inputs.category_inputs.C61`, validated from `config/work_packages.json`. Preview is temporary; saving creates a revision. Review rows are user records, not external approval. Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
