# Data connectors and contextual references

Updated 1 November 2026 from `backend/providers.py` and the verified saved reference. There are **14 configured public/read-only adapters**. The current educational paths require no API keys. They do not configure autonomous agents or an unattended refresh schedule. [Handover](../PROJECT_HANDOVER.md) · [API](API.md) · [operations](OPERATIONS.md).

## Registered adapters

| Provider ID | Source / direct category views | Cache freshness |
|---|---|---|
| `environment_screening` | JNCC marine SAC/SPA/offshore MPAs, Natural England MCZ, EMODnet grid; C16, C48, C49, C50 | 720 h (coast context 8760 h) |
| `access_metocean` | Historical accessibility wind, waves, currents and daylight; C56 | 168 h |
| `operations_wind` | Recent operational wind history via ERA5; C07 | 168 h |
| `overview_inputs` | UK cost benchmarks and IEA 15 MW turbine curve; C21, C26, C27, C29, C58, C59, C60, C61 | 720 h |
| `site_screening` | Coast, ports and vessel-density screening; C03, C04, C05 | 720 h |
| `tce_wind` | The Crown Estate wind-site agreements; C02, C37 | 168 h |
| `repd` | DESNZ Renewable Energy Planning Database; C37 | 168 h |
| `era5_wind` | ERA5 wind via Open-Meteo; C07, C08, C09 | 720 h |
| `marine` | Open-Meteo marine forecast; C13 | 6 h |
| `bathymetry` | EMODnet bathymetry; C16 | 720 h |
| `neso_tec` | NESO Transmission Entry Capacity register; C34, C35 | 72 h |
| `nsta_fields` | NSTA offshore hydrocarbon fields; C39 | 168 h |
| `nsta_platforms` | NSTA offshore infrastructure surface points; C44 | 168 h |
| `nsta_carbon` | NSTA current carbon-storage licence polygons; C41 | 168 h |

The table lists direct provider routing; derived workspaces can reuse scoped inputs (for example C10/C11 use wind, C14 uses historical currents and C52 uses port context). [Category data-source files](CATEGORIES.md) distinguish configured sources from bindings actually used by saved reference revisions. Cache hours are application request-cache settings, not guaranteed publisher update frequency.

## Collection and identity

Open **Data sources & APIs**, choose providers/period and collect. Persisted jobs expose queued/running/completed/partial/failed states and per-provider progress. A usable acquisition creates a new revision with compatible bindings. Reopen completed jobs to inspect their original collected revision. Refresh is manual; bypassing fresh cache requests a new response. Bounded retries and explicit stale fallback retain source identity; schema/scope failures must not silently produce zero or successful empty layers.

The source fetcher validates HTTPS hosts/redirects and configured publisher metadata. Raw bytes, payload hashes, licences, attribution, publisher/retrieval/check timestamps and actual returned grid coordinates are preserved. Scope checks cover provider, project, site, AOI hash and reference point. `attached_data()` resolves the selected snapshot's bindings. Never copy a dataset ID from Hornsea into another region just to populate a page.

Original responses/cache are under `data/external_raw` and `data/http_cache`, immutable dataset payloads under `data/external`, and runtime records in SQLite. User wind imports and execution outputs also require backup. [Operations](OPERATIONS.md) covers storage; `scripts.verify_data_snapshots` verifies scope and hashes offline.

## Periods and scientific interpretation

- The reference point is 53.8856337085001° N, 1.8919857048095705° E, the interior representative point of the existing Hornsea 1 (Centre) agreement. It is not a proposed AOI, a vacant lease or permission to develop.
- Long-term overview wind is 2021–2025: 43,824 hourly values at each of 10 m and 100 m. Recent C07 and access history use 2025-10-01 through 2026-09-30: 8,760 hours. The rolling rule chooses twelve complete available months after a seven-day source lag, not the last 365 days ending today.
- The explicit regional energy/cost case combines scoped ERA5 with `overview_inputs`: the theoretical IEA 15 MW curve/specification, DESNZ real-2024 cost workbook and pinned Arup loss references. Declared shear, electrical and curtailment assumptions remain separate. Ordinary regional wind alone cannot become measured site energy. The direct imported-wind path retains height/source guards.
- Historical access matches ERA5 wind/daylight/precipitation, ERA5-Ocean waves and SMOC currents. Source current km/h is converted to m/s; total precipitation is a conservative rain proxy. Visibility is missing. Grid cells differ and cannot resolve turbine-level wave shelter. The short marine forecast is a separate dataset, not the access climate.
- Coast/port distances and AIS cell samples are screening proxies. Port inventories do not establish berth/draft/crane capacity; AIS density is not collision probability. Reduced 2024 satellite coverage from June limits cross-year interpretation.
- A bathymetry point is not a surveyed profile/slope or foundation design. TEC rows are not headroom or an offer. NSTA fields/platforms/licences do not establish reuse permission, CO₂ capacity or injectivity. Existing wind agreements remain distinct from planning status in REPD.

## Supplied contextual references

| Reference | Use | Source handling / limit |
|---|---|---|
| `Wind Farms Around Hornsea.html` | C37 comparison, 25 records plus one map-only record | JSON parsed without executing HTML; original/checksums under `sources/references/hornsea_farms`; claims not independently verified; no overview yield/finance input |
| `Lattice · Offshore Wind.html` | C54's seven interactive views; 885 supplier profiles, 711 sites, 34 components, 214 links; 14 October 2026 | Original/JSON/hash manifest under `sources/references/lattice_supply`; reviewed adaptation and local libraries under `dashboard/public/assets/lattice`; isolated iframe, local queries; no qualification, capacity or delivery forecast |
| Accessibility images | C56 banner and criteria reference | Preserved assets/checksums under `dashboard/public/assets`; L = Daylight; images provide no numeric wind/wave data |

These references are **not additional providers** and do not replace the four preserved assessment/master originals in `sources/manifest.json`. C54's exposure weights, rule behavior and model checks are in [its implementation report](../reports/c54_lattice_workspace.md).

Contextual reference bundles are global to the checkout, unlike per-scenario provider datasets. Their maintainers' import scripts replace the current bundle; Git retains committed versions but the application does not automatically select an old bundle for an old scenario. Before updating, archive/review the old source and assets, record new checksums and refresh affected results. Do not present an older result checksum as the identity of a newly replaced live explorer. Versioned reference bindings are future work.

## Attribution and refresh

Exact licences/attribution are stored with each response; the provider registry is a summary. Check publisher availability, access terms, vintage and schema when collecting again. Existing raw records do not need to be refetched merely to edit documentation. Earlier collection counts/periods are preserved in [dated collection reports](../reports/data_collection.md); [current status](STATUS.md) records the latest evidenced reference.

## Environmental atlas milestone

Revision 19 adds `environment_screening`: 22 regional designation records, 127 qualifying-feature rows and a 169 × 144 LAT elevation grid. Raw UK source archives/workbooks, bounded OGC query and EMODnet metadata are preserved; 14 bound datasets now verify as 111 unique raw objects / 151,020,895 bytes. The reference point is outside these protection polygons. IUCN classes remain unavailable and qualifying features are not observations. See [exact vintages, methods, coverage and real rayshader/Three.js implementation](../reports/environmental_atlas.md).

Protected archives require an explicit bounded 75 MB fetch allowance; the general request limit remains 25 MB. No archive is extracted to disk by the reader. PyShp 2.3.1 uses independent seekable in-memory parts to avoid Python 3.13 ZIP_STORED seek misreads. Optional R rendering is a derivative, not source acquisition or a required API credential.
