# C65 — Life cycle, consents and critical path: Specialist Work Package

Owner profiles: A19

## Objective
Assess life cycle, consents and critical path for the selected immutable scenario.

## Inputs
- all agent durations

## Tasks and outputs
- milestone and dependency graph

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Dependencies and critical-path Gantt
2. Milestone confidence / delay-risk waterfall

## Dependencies
C54, C36, C64. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Forward/backward critical-path calculation in relative months; dependencies must be acyclic. Template durations are editable assumptions, not supplier or consent commitments.
