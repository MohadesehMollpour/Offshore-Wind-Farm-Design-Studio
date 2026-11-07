# C08 — Wind direction and sector frequency: Specialist Work Package

Owner profiles: A05

## Objective
Assess wind direction and sector frequency for the selected immutable scenario.

## Inputs
- wind U
- V
- time

## Tasks and outputs
- direction sector frequency and wind-energy-weighted frequency

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Interactive circular sector bar / dominant wind-from direction, IEA-inspired controls
2. Conventional stacked wind rose and direction-specific energy contribution

## Dependencies
C07. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Meteorological FROM sector frequencies, speed-stacked rose and calm accounting with explicit sample-height conventions.
