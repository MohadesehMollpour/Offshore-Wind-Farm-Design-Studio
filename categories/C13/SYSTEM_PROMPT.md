# C13 — Wave conditions and vessel weather windows: Specialist Work Package

Owner profiles: A06

## Objective
Assess wave conditions and vessel weather windows for the selected immutable scenario.

## Inputs
- wave time series
- limits

## Tasks and outputs
- Hs/Tp/direction and access probability

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Wave height and period joint distribution
2. Monthly marine access weather-window heatmap

## Dependencies
C01. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Seven-day wave-height/period forecast context; separate from the historical C56 access climate.
