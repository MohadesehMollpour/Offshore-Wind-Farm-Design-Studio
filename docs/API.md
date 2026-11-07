# Local API and data contracts

Updated 1 November 2026 from the running service's OpenAPI schema. The service's `/docs`, `/openapi.json` and `backend/app.py` are authoritative for exact request/response fields. This guide does not grant permission for external actions. [Architecture](ARCHITECTURE.md) · [connectors](DATA_CONNECTORS.md) · [operations](OPERATIONS.md).

## Mutation and snapshot rules

- Scenario creation accepts project, explicit site/layout, optional parent, reason and inputs. Request defaults are SITE_01/LAYOUT_01; a parent does not automatically choose them. Inputs merge at the top level. Preserve other `category_inputs` entries when replacing one category.
- Editing/restoring/importing/attaching new evidence creates a new immutable input snapshot. Results include scenario/project/site/layout/revision/hash. Cross-region source reuse must pass the binding guards.
- Category `run`, `screen` and `refresh-evidence` write cached results/events for the requested snapshot. Same-snapshot reruns replace that category's latest result; full per-run payload retention is not implemented.
- Workspace `preview`, accessibility evaluation and farm preview calculate temporary responses without creating saved input revisions. Preview validation errors must retain the last valid frontend model and disable saving until corrected.
- `collect` and overview preparation acquire public inputs through persisted jobs and create a new compatible bound revision on usable acquisition. Refresh is manual and jobs may partially fail.
- Marking a baseline is a stored workflow action, not engineering approval. GET reference/download/report endpoints read or export existing local records; no messaging or external publication occurs.

Workspace drafts use `scenario.inputs.category_inputs[cid]`. Use declared defaults and `validate_work_inputs()`. Unknown fields/settings are rejected. Required numeric defaults cannot be cleared; explicitly optional fields can remain null. Received/reviewed evidence needs a source; reviewed evidence needs an owner. Reviewed hazards also need scores, controls and evidence. Programme predecessors must be valid and acyclic.

C37 and C54 references are separate from scoped provider bindings. C54 metadata/counts, original and data JSON are read-only contextual endpoints. The original HTML downloads as octet-stream; the reviewed local adaptation is served under `/assets/lattice/`. A global reference replacement does not create a versioned reference binding for every past scenario.

## Hourly wind CSV contract

The wind import body supplies CSV text plus source name, URL, licence, method and measurement type. CSV columns are `timestamp_utc,wind_speed_ms,direction_deg,hub_height_m`. Supply at least 24 contiguous unique hourly rows at one height, explicit UTC timestamps, finite values and meteorological FROM directions clockwise from north. Keep measured, reanalysis, modelled and synthetic-demo provenance distinct. The source height must match the calculation's declared height unless an explicit supported extrapolation method is selected; the recent-wind plot never silently extrapolates thresholds.

## Current route inventory

| Method | Route | OpenAPI operation |
|---|---|---|
| GET | `/api/health` | Health |
| GET | `/api/catalog` | Catalog |
| GET | `/api/projects` | Projects |
| POST | `/api/projects` | Create Project |
| GET | `/api/projects/{pid}/scenarios` | Scenarios |
| POST | `/api/projects/{pid}/scenarios` | Create Scenario |
| GET | `/api/scenarios/{sid}` | Get Scenario |
| POST | `/api/scenarios/{sid}/baseline` | Baseline |
| POST | `/api/scenarios/{sid}/categories/{cid}/run` | Run |
| POST | `/api/scenarios/{sid}/screen` | Screen |
| POST | `/api/scenarios/{sid}/wind` | Import Wind |
| GET | `/api/projects/{pid}/history` | History |
| GET | `/api/sources/{source_id}` | Source File |
| GET | `/api/scenarios/{sid}/export.json` | Export Json |
| GET | `/api/scenarios/{sid}/categories/{cid}/export.csv` | Category Csv |
| GET | `/api/scenarios/{sid}/report.md` | Report |
| POST | `/api/scenarios/{sid}/categories/{cid}/preview` | Work Package Preview |
| GET | `/api/scenarios/{sid}/readiness` | Readiness |
| POST | `/api/scenarios/{sid}/farm-preview` | Farm Preview |
| POST | `/api/scenarios/{sid}/accessibility/evaluate` | Access Evaluate |
| GET | `/api/scenarios/{sid}/accessibility/history.csv` | Access History Csv |
| POST | `/api/scenarios/{sid}/overview/prepare` | Prepare Overview |
| GET | `/api/datasets/{did}/files/{filename}` | Source File |
| GET | `/api/providers` | Providers |
| GET | `/api/references/lattice-supply` | Lattice Supply Reference |
| GET | `/api/references/lattice-supply/original` | Lattice Supply Original |
| GET | `/api/references/lattice-supply/data.json` | Lattice Supply Data |
| GET | `/api/references/hornsea-farms` | Hornsea Reference |
| GET | `/api/references/hornsea-farms/original` | Hornsea Original |
| POST | `/api/scenarios/{sid}/refresh-evidence` | Refresh Bound Evidence |
| POST | `/api/scenarios/{sid}/collect` | Collect Data |
| GET | `/api/data-jobs/{jid}` | Get Data Job |
| GET | `/api/projects/{pid}/data-jobs` | Recent Data Jobs |
| GET | `/api/projects/{pid}/datasets` | Datasets |
| GET | `/api/scenarios/{sid}/datasets` | Bound Datasets |
| GET | `/api/datasets/{did}` | Dataset |
| GET | `/api/datasets/{did}/download.json` | Download Dataset |
| GET | `/api/datasets/{did}/environment-relief/{asset}` | Environment Relief Asset |

## Result and export identity

Category outputs retain method/run time, scenario ID/hash, evidence maturity, gaps and provenance. A numerical value can remain `needs-review`. CSV/JSON/draft reports must be read with that identity and source/assumption context. JSON input import into a workspace is validated draft data; a source-reference text field is not an automatic fetch of that document. C54 directory-data JSON exports the preserved source snapshot, while scenario export contains that revision's inputs/results.

The backend accepts configured loopback hosts/origins. It is a local single-user service, not an authenticated multi-tenant API. Keep runtime data private to the installation and use the [operation guide](OPERATIONS.md) for backups/recovery.

## Environmental payload and render assets

The composite `environment_screening` provider is collected through the existing persisted-job contract and attaches evidence to a new compatible revision. C16/C48/C49/C50 expose records, display GeoJSON, terrain, source/coverage metadata and relief availability. `evidence_workspace` preserves the C48–C50 draft/review register; the preview envelope differs from an ordinary `work_package`. The UI handles both.

Derivative `asset` is restricted to `terrain-relief.png`, `terrain-relief-preview.png`, or `terrain-relief.metadata.json`. Missing products return 404; provider, canonical terrain checksum and file hashes are checked. The route never installs R, runs supplied HTML, accepts arbitrary paths or generates a new image on GET. [Methods and data identities](../reports/environmental_atlas.md).
