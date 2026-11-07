# C29 — Monthly production and hourly generation proxy: Specialist Work Package

Owner profiles: A09

## Objective
Assess monthly production and hourly generation proxy for the selected immutable scenario.

## Inputs
- wind hourly and turbine curve

## Tasks and outputs
- 8760/8784 hourly simulation
- seasons

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Monthly energy production line
2. Hourly proxy heatmap with methodology label

## Dependencies
C27. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Monthly/weather-year generation context from the explicit regional model; not measured plant output.
