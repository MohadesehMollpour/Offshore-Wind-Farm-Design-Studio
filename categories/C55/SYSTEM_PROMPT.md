# C55 — Availability, reliability, maintenance strategy: Specialist Work Package

Owner profiles: A16

## Objective
Assess availability, reliability, maintenance strategy for the selected immutable scenario.

## Inputs
- failure rates
- repairs
- access

## Tasks and outputs
- annual availability
- scheduled/unscheduled repairs

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Availability and reliability time series
2. Failure modes / O&M strategy comparison

## Dependencies
C20, C13. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Renewal approximation A=MTBF/(MTBF+active repair+waiting). Assumed time availability is distinct from energy-weighted availability and does not alter the overview loss benchmark.
