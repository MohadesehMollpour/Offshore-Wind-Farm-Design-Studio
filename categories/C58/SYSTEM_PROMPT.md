# C58 — CAPEX and financing assumptions: Specialist Work Package

Owner profiles: A17

## Objective
Assess capex and financing assumptions for the selected immutable scenario.

## Inputs
- BoM
- installation
- finance rates

## Tasks and outputs
- breakdown,real/nominal cost,source ranges

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. CAPEX stacked breakdown
2. Financing sensitivity heatmap

## Dependencies
C22, C31, C36, C54. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Declared or explicit-regional benchmark CAPEX; not an itemized vendor quotation.
