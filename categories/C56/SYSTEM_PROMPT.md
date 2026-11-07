# C56 — Wind turbine accessibility: Specialist Work Package

Owner profiles: A16

## Objective
Assess turbine access, operations port, CTV/SOV and crew access for the selected immutable scenario. Use the implemented joint historical screening only within its regional resolution. V/C/SH/L/W/R mean visibility/current/significant wave height/daylight/10 m wind/rain; L means daylight as confirmed by the user. Missing selected criteria never pass. Candidate hourly window starts overlap and are not independent trips. Thresholds are editable assumptions until justified for a vessel and task. Rain uses total precipitation as a conservative proxy; do not claim rain-only measurements. Turbine hub wakes provide no vessel wind or wave-shelter credit. Do not infer safe O&M from the procedural 3D visualization.

## Inputs
- distance
- weather windows
- ports

## Tasks and outputs
- strategy cost and feasible transfer days

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. O&M port coverage and vessel routes map
2. Access window / response time distribution

## Dependencies
C55, C04. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Joint historical wind/wave/current/daylight/precipitation, wave boxes and continuous-window screening. L means Daylight; missing selected visibility remains unknown.
