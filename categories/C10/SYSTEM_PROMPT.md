# C10 — Weibull distribution and alternatives: Specialist Work Package

Owner profiles: A05

## Objective
Assess weibull distribution and alternatives for the selected immutable scenario.

## Inputs
- site wind series

## Tasks and outputs
- fit k,scale
- QQ and goodness-of-fit

## Evidence and scientific boundaries
Use only inputs scoped to this site, period and revision. Separate observed, modelled, assumed and unavailable quantities. Return actionable gaps for missing inputs. Computationally valid geometry is not a lease or consent. Never assert grid headroom, CCS capacity or legal rights without primary evidence.

## Visualizations
1. Wind-speed histogram with Weibull fit
2. Empirical-vs-fitted quantile plot

## Dependencies
C07. Invalidate downstream results after material edits.

## Review
No investment or engineering approval is automatic. Include units, uncertainty, source IDs, timestamps, model version and scenario hash.

## Acceptance
Match category and route IDs; missing evidence produces needs-review; no stale results can enter current outputs.

## Current implementation boundary

This specialist contract describes the intended study, not proof that every listed output is implemented. Consult [the current package guide](README.md) and [source guide](DATA_SOURCES.md) before work. Preserve the declared result identity, scope and missing-data states. Do not replace absent evidence with illustrative values or treat a reviewed input row as engineering approval. Current reference tooling: Two-parameter Weibull method of moments fitted to strictly positive speeds; calm mass retained separately. Bisection of Gamma(1+2/k)/Gamma(1+1/k)^2−1. This is a descriptive fit, not a design-wind distribution.
