# C66 — Repowering, reuse and decommissioning: Specialist Work Package

Owner profiles: A19

## Objective
Assess repowering, reuse and decommissioning for the selected immutable scenario.

## Inputs
- asset inventory
- permit conditions

## Tasks and outputs
- end-of-life options and restoration plan

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. End-of-life scenario decision tree
2. Extension/repowering/decommissioning cost plots

## Dependencies
C59, C65. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Terminal benchmark/declared cost plus explicitly additional contingency, less assumed salvage, discounted at the declared real rate. Timing alternatives do not imply legal permission to defer removal.
