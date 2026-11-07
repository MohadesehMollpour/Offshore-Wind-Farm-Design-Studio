# C31 — Inter-array cables and string topology: Specialist Work Package

Owner profiles: A10

## Objective
Assess inter-array cables and string topology for the selected immutable scenario.

## Inputs
- layout
- WTG current/cable ratings

## Tasks and outputs
- topology
- kV
- length
- N-1 rationale

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Array cable network map
2. Electrical loading per string chart

## Dependencies
C23. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Preliminary grouping into strings, collector assumed at local (0,0), straight segments between sorted positions. No cable ampacity, routing exclusion, burial, redundancy or protection solution.
