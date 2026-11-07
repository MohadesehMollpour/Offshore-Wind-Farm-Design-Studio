# C07 — Historical wind speed at several hub heights: Specialist Work Package

Owner profiles: A05

## Objective
Assess historical wind speed at several hub heights for the selected immutable scenario.

## Inputs
- GWA
- ERA5
- site

## Tasks and outputs
- time series
- means
- speed ranges
- missingness

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Hub-height wind speed time series
2. Wind speed by height plot

## Dependencies
C01. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Monthly wind distributions, recent/calendar-year periods, 10/100 m height, units, height-matched sailing/O&M limits and CSV/SVG exports.
