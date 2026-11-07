# C23 — Turbine placement and spacing: Specialist Work Package

Owner profiles: A08

## Objective
Assess turbine placement and spacing for the selected immutable scenario.

## Inputs
- polygon
- exclusions
- D
- wind rose

## Tasks and outputs
- turbine point geometries
- spacing
- density

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Scaled turbine layout map
2. Minimum-spacing distribution plot

## Dependencies
C01, C02, C08, C20. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Exclusion/rotor-envelope-aware preliminary layout in a supplied AOI; reference geometry remains missing.
