# C52 — Construction port, staging and vessel choices: Specialist Work Package

Owner profiles: A15

## Objective
Assess construction port, staging and vessel choices for the selected immutable scenario.

## Inputs
- port constraints
- WTG dimensions

## Tasks and outputs
- port ranking
- equipment and mobilisation

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Construction ports and vessel routes map
2. Port selection score plot

## Dependencies
C04, C20. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Return distance proxy divided by assumed speed; no berth, draft, crane, storage, navigable route or vessel suitability is inferred.
