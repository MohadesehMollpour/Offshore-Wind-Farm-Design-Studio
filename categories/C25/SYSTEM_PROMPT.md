# C25 — Multiple-objective optimisation: Specialist Work Package

Owner profiles: A08

## Objective
Assess multiple-objective optimisation for the selected immutable scenario.

## Inputs
- layout cases
- environment
- cost

## Tasks and outputs
- AEP/LCOE/ecology trade-off Pareto frontier

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Energy-cost-environment Pareto scatter
2. Trade-off comparison parallel coordinates

## Dependencies
C24, C03. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Deterministic comparison of five conceptual strategies using illustrative Jensen hub-point wakes at one direction/speed. Not an AEP/LCOE optimizer or feasible-AOI ranking.
