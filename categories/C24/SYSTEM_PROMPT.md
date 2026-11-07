# C24 — Wake interaction and neighbouring farm wakes: Specialist Work Package

Owner profiles: A08

## Objective
Assess wake interaction and neighbouring farm wakes for the selected immutable scenario.

## Inputs
- layout
- wind distribution
- adjacent turbines

## Tasks and outputs
- internal and external wakes separated

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Wake-deficit map with nearby assets
2. Directional wake-loss plot

## Dependencies
C23, C08, C21. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Illustrative hub-point Jensen top-hat wakes, constant Ct, root-sum-square deficits, capped at 90%. No wake-added turbulence, blockage, stability or validated farm calibration.
