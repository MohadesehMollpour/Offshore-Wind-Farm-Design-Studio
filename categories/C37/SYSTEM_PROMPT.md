# C37 — Existing, consented and planned wind farms: Specialist Work Package

Owner profiles: A11

## Objective
Assess existing, consented and planned wind farms for the selected immutable scenario.

## Inputs
- leases
- project databases

## Tasks and outputs
- names
- polygons
- status
- MW
- distance
- citations

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Nearby offshore wind farms geospatial map
2. Project lifecycle-status timeline

## Dependencies
C01. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Official agreements/status plus a separate supplied Hornsea comparison explorer (25 records and one map-only record).
