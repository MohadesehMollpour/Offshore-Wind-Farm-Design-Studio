# Offshore Wind Farm Design Studio

A local offshore wind planning and coursework workspace with linked management and Three.js digital-twin views, 70 category packages, 14 public-data adapters and immutable input revisions. The evidenced Hornsea case is regional screening, with no proposed site boundary or development rights.

**Continue the project:** [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md). **Find a guide:** [documentation index](docs/INDEX.md). [Current status](docs/STATUS.md), [all 70 categories](docs/CATEGORIES.md) and [the roadmap](docs/ROADMAP.md) distinguish working tools from missing engineering evidence.

## Read-only snapshot on GitHub Pages

**Open it in the browser:** <https://mohadesehmollpour.github.io/Offshore-Wind-Farm-Design-Studio/>. It opens the evidenced reference, revision 19 for Hornsea, and lets you browse all 20 saved revisions, the management overview, the 3D digital twin, all 70 category pages, charts and maps.

GitHub Pages only serves static files, so the site cannot run the Python backend or the SQLite database. In the snapshot:

- every page shows the results that were saved when the snapshot was exported;
- calculating, saving, editing inputs and collecting data show a "read-only snapshot" message;
- downloads (draft report, JSON, CSV and dataset exports) are included for revisions 19 and 20;
- the course materials (assignment, brief, assessment criteria and master prompt) are kept out of this public repository. Their checksums remain in `sources/manifest.json`.

To refresh the published snapshot after local work, export it from the local database, then commit and push `pages_snapshot/`. The [Pages workflow](.github/workflows/pages.yml) rebuilds the site on every push to `main`.

```powershell
.\.venv\Scripts\python.exe -m scripts.export_pages_snapshot
```

The first deployment needs one setting from the repository owner: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Start locally

From PowerShell in `D:\Wind_Farm_Design`:

```powershell
.\Start-Studio.ps1
```

Open <http://127.0.0.1:8000>. Reuse an existing server on port 8000 and check active ingestion before restarting it. [Operations](docs/OPERATIONS.md) covers setup, backup and recovery. If dependencies/build need preparing:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
npm.cmd ci --prefix dashboard
npm.cmd run build --prefix dashboard
```

The recorded environment is Python 3.13 and Node 24; lockfiles govern reproduction. Development Vite runs on 5173 with `/api` proxied to the backend on 8000. Frontend changes require a production build; backend changes require a restart. No hosted LLM service, deployment or paid API is configured.

## First workflow

1. Open **Management overview**, choose a region/layout or saved revision, then open **Wind Farm Digital Twin (3D View)**. Both views share selection through navigation, reload and other tabs of the project.
2. For the most evidenced case, choose **revision 19 · Hornsea**, scenario `05c163c0-c50f-412c-bdbf-324d0ae9cf04`. Revision 18 is Dogger Bank/staggered, without inherited Hornsea datasets. A newer revision is not necessarily better evidenced.
3. Use **Data sources & APIs** to collect sources or reopen a completed job. Collection attaches compatible evidence to a new revision. Check period, point/grid, source licence, timestamps and missingness. See [connectors](docs/DATA_CONNECTORS.md).
4. C03–C05 provide regional comparison preferences, coast/port distance proxies and AIS vintage/threshold plots. Existing leases are benchmarks/constraints, not available candidate sites. Screening weights are separate from the assessment rubric.
5. C07 provides monthly wind box plots with explicit-height sailing/O&M thresholds and CSV/SVG export. C56 combines historical wind, waves, currents, daylight and precipitation into eligibility and continuous-window plots. **L means Daylight**. Selected missing visibility remains unknown.
6. The 3D twin includes turbine selection, wind FROM yaw, illustrative blade rotation/wakes, historical replay and procedural ocean. Without valid C23 positions, geometry is labelled conceptual. Hub wakes do not establish wave shelter or safe vessel access.
7. **C54** follows the attached **Lattice** design: command center, turbine anatomy, component tracing/map, supply landscape, disruption scenarios, local graph queries and ontology. Its UK directory snapshot is context, not qualified suppliers, quotations or delivery commitments. The procurement review register saves separately as a new revision.
8. Supply a sourced EPSG:4326 AOI/exclusions, turbine choice and justified inputs before site-specific calculations. Hourly wind imports require explicit UTC, one height, source metadata and gap-free unique hours. Seeded placement is not a validated AEP/LCOE optimizer.
9. Review C61 sensitivity, C62 hazards, C63 labour, C64 engagement, C65 programme and C66 decommissioning assumptions. C61 computes NPV only when an explicit consistent-price-year captured price is supplied. Selling price does not change cost-based LCOE.
10. Inspect **Work package readiness**, enter actual human/AI section contributions in C68 and export draft Markdown, JSON or category CSV. Populated charts and review rows do not confer engineering or investment approval.

The reference overview estimates **4,485.0946 GWh/year** and **88.5504 real-2024 GBP/MWh** for 990 MW, using five-year ERA5, a theoretical IEA 15 MW curve and DESNZ/Arup benchmarks with declared losses/shear. Its independent saved C56 case uses **Hs ≤2.0 m**, not the 1.5 m factory example. Read the [handover](PROJECT_HANDOVER.md) before comparing these preliminary values.

The **Environmental atlas** (C16/C48/C49/C50) adds JNCC/Natural England boundaries, 22 regional sites, 127 declared conservation features, a linked 2D map and actual EMODnet relief rendered through R rayshader and Three.js. IUCN classes remain unknown. [Environmental implementation and sources](reports/environmental_atlas.md).

## Checks and continuation

```powershell
$testRunDirectory = Join-Path 'D:\Wind_Farm_Design\work' ('pytest-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q --basetemp $testRunDirectory
node tests/lattice_core.test.cjs
.\.venv\Scripts\python.exe -m scripts.verify_workspace
.\.venv\Scripts\python.exe -m scripts.verify_data_snapshots --scenario-id 05c163c0-c50f-412c-bdbf-324d0ae9cf04
.\.venv\Scripts\python.exe -m scripts.verify_documentation
npm.cmd run build --prefix dashboard
```

The latest implementation run passed **278 Python tests**, the production build and targeted environmental browser checks. Prior pure Lattice model checks remain recorded. See [verification](docs/VERIFICATION.md).

Git does not contain the populated SQLite database or collected runtime data. Back up the database, raw imports, external datasets/raw/cache, processed outputs and source libraries separately. See [architecture](docs/ARCHITECTURE.md), [API](docs/API.md) and [operations](docs/OPERATIONS.md).

## Assessment and boundaries

The official brief covers 16 lifecycle topics, with **40% analysis, 20% coherence, 20% data sources and 20% organisation/presentation**. Deadline: **17 December 2026, 14:00 Europe/London**. C68 records actual section leads/contributions and AI disclosure. The master prompt's platform, CCS and oil/gas extensions are distinct from formal assessment requirements; the 2023 Viking report is historical context. See [assessment traceability](docs/ASSESSMENT_TRACEABILITY.md).

The 22 agent profiles describe intended ownership, not running AI services. Site rights, specialist surveys, validated methods, vessel/task limits, vendor quotations, revenue terms and human review remain essential. The software is a local planning aid, not the submitted report or an approved development design.
