# C61 — Price, discount, wake and schedule sensitivity: Specialist Work Package

Owner profiles: A17

## Objective
Assess price, discount, wake and schedule sensitivity for the selected immutable scenario.

## Inputs
- probability/ranges

## Tasks and outputs
- scenario results
- Monte Carlo if justified

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Financial sensitivity tornado
2. Scenario response surface / heatmap

## Dependencies
C60. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Deterministic one-at-a-time cost, real discount-rate, wake-loss and commissioning-delay sensitivities. CAPEX stays at year 0; operating energy/revenue/OPEX and terminal removal shift with delay. No holding costs or construction phasing are invented. Price changes NPV, not cost-based LCOE. No probability distributions or Monte Carlo confidence claims.
