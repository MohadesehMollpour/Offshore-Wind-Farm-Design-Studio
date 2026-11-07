# Current implementation status

Updated 1 November 2026 after the environmental atlas milestone, current registries and reference revision 19. Earlier C54/doc checkpoints remain in dated reports. [Handover](../PROJECT_HANDOVER.md) · [70-category register](CATEGORIES.md) · [Verification](VERIFICATION.md) · [Roadmap](ROADMAP.md).

## Delivered tools

| Area | Implemented | Remaining boundary |
|---|---|---|
| Local workspace | FastAPI/SQLite, React/Vite, 70 routes and 22 ownership profiles | Single-user; no hosted agents or production authentication |
| Shared design | Five regions × five layouts, saved revisions, comparison/baselines, linked overview/twin | No proposed AOI or rights from regional presets |
| Sources | 14 adapters, persisted jobs, raw/cache hashes, scoped bindings and stale handling | Published/modelled data needs coverage and engineering review |
| C03–C05 | Interactive preferences, coast/port distance proxies, AIS vintage/thresholds | No navigable routing or collision-risk/site-approval model |
| C07–C12 | Monthly boxes, rose/statistics, descriptive Weibull fit, shear and hourly extremes | No site measurement, turbulence or design-extreme certification |
| Overview | Explicit published-curve/cost regional energy/LCOE with loss/shear/price basis | No site budget, proposed AOI or saved captured electricity price |
| 3D twin | Selection, FROM yaw, illustrative rotating blades/wakes, replay and procedural ocean | Conceptual fallback; no SCADA or wave-shelter/access credit |
| C37 | Published agreements and separate supplied comparison | Attachment claims unverified; excluded from yield/finance |
| Environmental atlas | C16/C48/C49/C50: 22 protected sites, 127 declared features, 2D maps and actual rayshader/Three.js EMODnet relief | No expert EIA, site surveys or supplied IUCN classes; partial designation coverage |
| C54 | Seven Lattice views, local maps/queries/model and saved procurement register | No qualified capacity, quotations or delivery commitments |
| C56 | Matched wind/wave/current/daylight/precipitation, eligibility and continuous windows | Missing visibility; illustrative thresholds, no transfer approval |
| Planning | 54 schemas; C61 sensitivity, C62 hazards, C63 labour, C64 engagement, C65 CPM, C66 timing | Assumptions/registers need real evidence and review |
| Reporting | Readiness audit, C68 disclosure, draft Markdown/JSON/CSV | Not a complete assessed report, technical annex set or approval |

## Verified reference

Project `a77feb50-35c9-424a-87e8-a42cf756be4e`, revision **19**, scenario `05c163c0-c50f-412c-bdbf-324d0ae9cf04`, is Hornsea/regular grid: 990 MW, 66 ×15 MW, D=240 m, hub=150 m. It has **no proposed AOI**. The sampling point lies within an existing Hornsea 1 (Centre) agreement and does not establish available seabed.

The regional overview estimates **4,485.094627651206 GWh/year** and **88.55044730282819 real-2024 GBP/MWh**. Its wind period is 2021–2025. The independent historical access/recent-wind period is 2025-10-01 to 2026-09-30, 8,760 matched hours. Saved C56 uses **Hs ≤2.0 m**, giving 3,422 eligible hours and 650 overlapping 12-hour starts; the 1.5 m factory comparison gives 3,019 hours and 602 starts. Both have a 17-hour longest run. These are screening values, not approved trips.

There are 14 bound datasets, 111 unique raw responses and 151,020,895 raw bytes. The environmental provider adds JNCC/Natural England boundaries and EMODnet relief; [methods and exact results](../reports/environmental_atlas.md). Revision 17 retains its earlier 13 datasets. C54 adds a separate 14 October 2026 contextual snapshot: 885 profiles, 711 site records, 34 components and 214 links. It does not add a provider binding. The C54 result was refreshed with its original/data checksums without changing inputs.

Revision 18 is Dogger Bank/staggered without Hornsea bindings; it verifies selection isolation and is not the most evidenced case. Recheck IDs/state before resuming. At this documentation checkpoint `PRAGMA quick_check` returned `ok`; 10 collection jobs were completed and none queued/running.

## Coverage is not engineering completion

The 70 evaluated reference rows classify as 25 source-screening, 19 planning calculations, five built-in calculation/project views, 17 evidence registers, one HSE register, one stakeholder register and two missing-input views (C01/C23). C54 remains an evidence register because the directory does not complete procurement. See [each category and its gaps](CATEGORIES.md).

Outstanding inputs include a proposed AOI/rights, geology/geotechnical and ecology/fisheries evidence, verified turbine/structural/electrical studies, calibrated wakes, grid/capture terms, approved vessel/task limits, visibility and vendor quotations. Conditional NPV is implemented; no saved reference price or NPV is invented. Reference HSE hazards remain unassessed.

The latest implementation checks passed **278 Python tests**, production build and environmental browser QA. Prior pure Lattice model checks remain recorded. The new source collection created revision 19 without changing design parameters, energy/LCOE or access preferences. [Verification](VERIFICATION.md) distinguishes fresh documentation/integrity checks from earlier model tests.
