# C28 — P50/P75/P90 yield and uncertainty: Specialist Work Package

Owner profiles: A09

## Objective
Assess p50/p75/p90 yield and uncertainty for the selected immutable scenario.

## Inputs
- uncertainty sources

## Tasks and outputs
- exceedance yield distribution
- assumptions

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. P50/P75/P90 energy exceedance plot
2. Uncertainty contributions tornado plot

## Dependencies
C27. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Weather-year spread is descriptive and is not P90. Optional exceedance estimates use a user-declared aggregate normal standard uncertainty; no bankable yield inference.
