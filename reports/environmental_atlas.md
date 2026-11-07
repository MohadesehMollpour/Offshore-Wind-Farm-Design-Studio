# Environmental atlas — protected areas and seabed relief

Implemented 1 November 2026 after the C54 Lattice milestone. This extends the selected Hornsea / East Yorkshire case using UK sources appropriate to that region. The supplied Danish Natura 2000 illustration is a visual reference; its polygons and numbers are not used as UK evidence.

## Open and reproduce the result

Choose **revision 19** (`05c163c0-c50f-412c-bdbf-324d0ae9cf04`) and **Environmental atlas** in the sidebar, or C48. C16 opens the seabed view; C49 opens all regional conservation interests; C50 combines the same spatial evidence with a separate cumulative-impact acquisition/review register. C54 retains the seven Lattice supply-chain views.

[Open C48 atlas](http://127.0.0.1:8000/projects/a77feb50-35c9-424a-87e8-a42cf756be4e/categories/C48?scenario=05c163c0-c50f-412c-bdbf-324d0ae9cf04).

The acquisition job `627a5ed9-4197-4b98-af73-794a09238d4e` completed and attached `environment_screening` dataset `a56ec572-1f7c-4add-91f5-aec4494acf89` as a new input revision. The old revision 17 and Dogger Bank revision 18 remain separate. New scenario hash: `6614f771a1f3f9b29633cd9544d4738b39e1ddce8ecde2677c0fa21ab93a3a59`.

## Collected sources

| Source | Collected evidence / vintage |
|---|---|
| [JNCC offshore/straddling MPAs](https://jncc.gov.uk/resources/ade43f34-54d6-4084-b66a-64f0b4a5ef27) | WGS84 boundary archive and qualifying-feature workbook, 3 December 2025 |
| [JNCC marine SACs](https://jncc.gov.uk/resources/598a60db-9323-4781-b5a8-dcf0ca3b29f9) | WGS84 boundaries and marine-interest workbook, 13 December 2024 |
| [JNCC marine SPAs](https://jncc.gov.uk/resources/07078ed3-496d-432b-974e-1754b47536c7) | Boundaries 19 June 2026; feature workbook 10 July 2026 |
| [Natural England MCZ service](https://environment.data.gov.uk/dataset/c0061c93-d444-481c-a14e-653b8a8e2b1a) | Bounded OGC GeoJSON query adds inshore England MCZs; dataset revision 15 July 2023, catalogue updated 13 July 2026. `gis_date` is geometry entry, not designation date. |
| [EMODnet DTM 2024](https://erddap.emodnet.eu/erddap/griddap/bathymetry_dtm_2024.html) | Explicit-stride elevation grid plus DAS datum/use metadata, metres relative to Lowest Astronomical Tide (LAT) |
| Natural Earth / OpenStreetMap | Downloaded generalized coastline for offline context; live OSM tiles are background context only, not calculation evidence |

Publisher pages, original archives/workbooks, query responses and metadata are retained with SHA-256, URL, licence and retrieval identity. Natural England is OGL; JNCC includes CNCB/UKHO/Ordnance Survey rights; EMODnet use constraints remain with its source. No IUCN/Protected Planet records were downloaded and no data-licence agreement was accepted. JNCC site WDPA identifiers are retained when supplied, but are not IUCN classes.

## Saved regional results

The 150 km disc is centred on 53.8856337085001 N, 1.8919857048095705 E, an existing Hornsea 1 (Centre) agreement reference. No proposed AOI is supplied.

- **22 unique site-code/designation pairs:** 9 SAC, 9 SPA and 4 MCZ.
- **0 source polygons cover the reference point.** Nearest Southern North Sea SAC boundary is about 11.05 km away. These values concern the point, not the whole existing agreement or a proposed farm.
- **35,448.64968874674 km² dissolved protected union**, 50.16207364976196% of the reference disc. The disc includes **land and sea**; this is neither protected marine-water fraction nor farm-impact area.
- **127 deduplicated declared conservation-interest rows** joined on exact site code. These are designation features, not observed species occurrences, abundance or collision/noise impacts. Population types remain separate; richer source feature codes are retained.
- Holderness Inshore and Cromer Shoal Chalk Beds have boundaries but their feature tables are not loaded. The UI explicitly shows unavailable interests, rather than ecological absence.
- **0 IUCN categories supplied, 22 unknown.** Management-mode hatching denotes missing classification metadata, not absence of management. SAC/SPA/MCZ must never be converted into guessed IUCN classes.
- Seabed grid **169 × 144**, 21,587 valid and 2,749 missing nodes; elevation **−93.08 to +8.101546 m LAT**. Roughly 1.8 × 2.1 km samples are taken at explicit native-grid strides, not averaged survey cells.

Areas use a local WGS84 Lambert azimuthal equal-area projection, full source geometry and dissolved overlaps. The geodesic reference ring has 2-degree azimuth steps. Proximity is a geodesic distance to the nearest projected geometry, appropriate for screening. Display polygons use 150 m topology-preserving simplification and clipping to the regional rectangular extent. If an AOI is later supplied, intersections from those display polygons are explicitly approximate and need original GIS review.

Coverage is partial: UK marine SAC/SPA, offshore/straddling MPAs and England MCZs. Other inshore national designations and SSSI/ASSI are not a complete part of this inventory. The adapter rejects unsupported non-UK sampling points; it must not claim a Danish/EU site has zero constraints from UK data.

## Maps and interactions

The Leaflet map provides designation filters, linked polygon/site selection, search, scale, management-data hatching, optional published wind-agreement outlines and in-page expansion. Selecting a site updates its source, proximity, disc area and qualifying-feature table. Tables offer selected/all-sites and feature-type filters, CSV export; map offers visible GeoJSON and source JSON exports.

Three.js renders the actual sampled elevations, with OrbitControls, source polygons including holes, coastline, reference ring/marker, optional wind agreements, a datum water plane, camera reset and adjustable **1–300× geometric exaggeration** (150× initial view). Overlays are symbolic sea-level footprints, not raised ecological volumes. Missing source vertices are omitted from triangles. Map coordinates use a regional cosine-latitude approximation for display; backend area/proximity metrics use the stated projection. Renderer resources, controls and animation are disposed on navigation. WebGL failure retains the 2D map and static render.

The texture is produced by **real R rayshader**, not a shader named after it: `sphere_shade` and `height_shade`, 8× shading exaggeration, anisotropic physical spacing normalized to square cells for normals and sampled back to the original north-up grid. No missing elevations are filled or extrapolated. The transparent mask also omits undefined-normal halos; 21,027 texture pixels are opaque. Shading exaggeration is independent of Three.js geometry scaling.

## Renderer and continuation

Core code: `backend/environment.py`; provider registry/fetch-size bounds in `backend/providers.py`; optional rendering in `backend/ingestion.py`; result routing in `backend/external_analysis.py`; allowlisted derivative route in `backend/app.py`; `dashboard/src/EnvironmentPage.tsx`, `EnvironmentTerrain.tsx`, `environment.css`; evidence draft support in `WorkPackagePage.tsx`.

R scripts: `scripts/render_environment_rayshader.R`, `scripts/run_environment_rayshader.py`, `scripts/setup_environment_rayshader.R`. The current isolated runtime is official CRAN **R 4.6.2**, rayshader **0.41.2**, rayimage **0.27.1**, rayvertex **0.15.0**, rgl **1.3.36**. Portable runtime and package library are ignored under `work/rayshader`; the user's system R and user libraries were not changed. Runtime provenance, package versions and session info are recorded there. They are **not restored by a Git clone**.

With an official compatible R runtime already available, install optional packages into the project library explicitly:

```powershell
& 'PATH-TO-YOUR-Rscript.exe' --vanilla scripts/setup_environment_rayshader.R
.\.venv\Scripts\python.exe scripts/run_environment_rayshader.py work/environment-products/terrain-input.json work/environment-products/manual-render --exaggeration 8 --rscript 'PATH-TO-YOUR-Rscript.exe'
```

Setup obtains current CRAN packages and records their versions; it is not an exact historical package lock. Compare the recorded renderer versions and outputs after upgrades. Default runner uses `work/rayshader/runtime/app/bin/x64/Rscript.exe`; the ingestion hook uses that project-local runtime only and never installs software. A custom-runtime manual render is not automatically published to the dataset cache.

Automatic products live in `data/processed/environment-relief/<terrain SHA-256>/`: input JSON, north-up PNG, labelled preview, metadata and a product-SHA manifest. The current terrain identity is `44591d7eecfad80424fea6a1811d3bbbd5bc4b07db0ef8340e5f9b01851d411d`. Backup these with the database/raw datasets if exact rendering is needed. `GET /api/datasets/{did}/environment-relief/{asset}` allows only the two PNGs and metadata, after provider and checksum validation. Optional R failure cannot make a valid source stale; source-elevation colours remain the fallback.

Do not fabricate site surveys, EIA conclusions, cumulative impacts or mitigation effectiveness. Keep the C48–C50 acquisition/review register separate under `data.evidence_workspace`; an automatic source download does not create an expert-reviewed evidence row. `WorkPackagePage` previews must accept this envelope as well as ordinary `work_package`.

## Verification

The complete Python suite passed **278 tests** (14 new environmental cases), and the final TypeScript/Vite production build passed. Tests cover archive CRS/schema and Python 3.13 seek behavior, exact-code feature joins/deduplication, overlap union, hectares/date semantics, paged-source truncation, invalid/duplicate/NoData terrain, unsupported-region rejection, scoped new revisions, unreviewed evidence and derivative cache/API identity. Existing non-fatal Shapely/Starlette warnings and Vite size warnings remain.

Live browser checks cover 2D sources/hatching/expansion, linked search and missing feature evidence, 3D real texture and display controls, category routes, and an unsaved evidence preview discarded without creating a revision. An initial Leaflet view initialization error and an authenticated basemap issue were fixed. A reload during Vite's brief dist replacement produced a temporary missing-index response; the completed build loads normally.

Offline snapshot verification passed **14 bound datasets, 111 unique raw objects, 151,020,895 bytes**, including provider/project/site/AOI/reference-point checks. SQLite quick-check returned `ok`; 10 collection jobs completed, none queued/running at inspection. Energy/LCOE remain **4,485.094627651206 GWh/year / 88.55044730282819 real-2024 GBP/MWh**. Saved C56 retains Hs 2.0 m, daylight, wind 10 m/s and 12-hour windows. No proposed AOI, price, hazard scores or reviewed ecology evidence was invented.

[Handover](../PROJECT_HANDOVER.md) · [source inventory](../docs/DATA_CONNECTORS.md) · [operations](../docs/OPERATIONS.md) · [verification](../docs/VERIFICATION.md).
