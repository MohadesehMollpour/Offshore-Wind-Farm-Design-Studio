# C62 — Construction/operations HSE and emergency response: Specialist Work Package

Owner profiles: A18

## Objective
Assess construction/operations hse and emergency response for the selected immutable scenario.

## Inputs
- HAZID
- activities
- operators

## Tasks and outputs
- risk log
- ALARP decisions
- emergency plan

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Risk probability vs consequence matrix
2. Safety controls and readiness timeline

## Dependencies
C53, C56. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Editable 1–5 ordinal likelihood × consequence matrix, with separate proposed residual scores. Scores are user assessments, not measured probabilities. No score, completed form or proposed control establishes ALARP or an approved emergency plan.
