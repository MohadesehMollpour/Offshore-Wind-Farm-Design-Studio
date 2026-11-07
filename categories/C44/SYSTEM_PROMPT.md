# C44 — Offshore platform and rig inventory: Specialist Work Package

Owner profiles: A13

## Objective
Assess offshore platform and rig inventory for the selected immutable scenario.

## Inputs
- platform status
- ownership
- locations

## Tasks and outputs
- name/type,owner,operation/decommission status,distances

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Offshore platforms and rigs map
2. Asset status / decommissioning timeline

## Dependencies
C01. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Published NSTA surface infrastructure context; not a suitability or reuse-permission assessment.
