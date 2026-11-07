# C33 — Export route and onshore landfall: Specialist Work Package

Owner profiles: A10

## Objective
Assess export route and onshore landfall for the selected immutable scenario.

## Inputs
- seabed exclusions
- onshore corridors

## Tasks and outputs
- route GeoJSON
- route length
- crossings

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Export corridor and landing GIS map
2. Distance and cable-risk sensitivity

## Dependencies
C01, C31. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: A structured evidence and review register for the selected snapshot. Missing inputs remain missing.
