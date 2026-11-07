# C12 — Turbulence and extreme wind design: Specialist Work Package

Owner profiles: A05

## Objective
Assess turbulence and extreme wind design for the selected immutable scenario.

## Inputs
- turbulence
- IEC site class

## Tasks and outputs
- TI by wind bin
- extremes
- class match

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Turbulence vs wind speed scatter
2. Design wind extremes plot

## Dependencies
C07. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Descriptive maxima of hourly model means. Ten-minute turbulence, gusts and 50-year design extremes cannot be inferred from hourly reanalysis.
