# Hornsea public-data collection

> **Historical milestone:** Earlier public-source collection; adapter counts and dataset IDs below belong to that acquisition milestone. Current behavior and validation are in [status](../docs/STATUS.md), [verification](../docs/VERIFICATION.md) and [the handover](../PROJECT_HANDOVER.md).

Collection scope: Hornsea / East Yorkshire regional screening. No proposed AOI has been selected.
Scenario revision: 4; ID: 5758971f-ae5b-49bd-bd6b-6bf135aa558e; hash: 41feeb55cbe854d8403a4235a4b62a4d1ec579e5e23474950158fa212b315064.

Reference: Hornsea 1 (Centre) existing lease reference, 53.8856337° N, 1.8919857° E.
Method: Interior representative point of the official existing wind-site agreement polygon. Feature OBJECTID 38.
This is an existing-project reference, not a proposed development area or evidence of vacant seabed.

| Source | Retrieved data | Dataset ID |
|---|---|---|
| [The Crown Estate wind-site agreements](https://www.arcgis.com/home/item.html?id=22a1be6fb0c5416e9369f97743f387b1) | 72 published features/records | b6f1972c-4b7e-4540-8ea4-ae5fbfc62d43 |
| [DESNZ Renewable Energy Planning Database](https://www.gov.uk/government/publications/renewable-energy-planning-database-quarterly-extract) | 110 published features/records | ec09191e-7096-4b88-9509-2807109c3dbd |
| [ERA5 wind via Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) | 8,760 hourly records at each of 10 m and 100 m, 2025-01-01 to 2025-12-31 | 09622f96-a878-49ba-901c-161120e6fc1b |
| [Open-Meteo marine forecast](https://open-meteo.com/en/docs/marine-weather-api) | 168 hourly forecast records; 0 missing | 78ff3894-7cb5-4880-97f4-089017faf72f |
| [EMODnet bathymetry](https://emodnet.ec.europa.eu/en/emodnet-web-service-documentation) | One numeric DTM raster-cell sample and preserved WMS capabilities | a4288e40-47a4-46aa-9277-9afd3b36c246 |
| [NESO Transmission Entry Capacity register](https://www.neso.energy/data-portal/transmission-entry-capacity-tec-register) | 10 published features/records | 83da6f68-537d-4e82-a0e4-a08747b3122b |
| [NSTA offshore hydrocarbon fields](https://www.arcgis.com/home/item.html?id=ba711a4be08449329a871d37ae910735) | 159 published features/records | f76d6801-ad17-4c58-97a3-75966c6ed2f3 |
| [NSTA offshore infrastructure surface points](https://www.arcgis.com/home/item.html?id=a97ed4fcd8b34ef2b4527957114cda46) | 143 published features/records | 4893a61d-f55a-4ae6-8dd4-bff8d0f91785 |
| [NSTA current carbon-storage licence polygons](https://www.arcgis.com/home/item.html?id=ae0b0c44c6214112a0612ee66cf493dc) | 16 published features/records | 474c00cd-9576-46e5-9c65-e2df30d28731 |

## Screening observations

- Mean ERA5 wind at 10 m: 7.701 m/s for the retrieved period.
- Mean ERA5 wind at 100 m: 9.554 m/s for the retrieved period.
- Provider grid point: 54.0° N, 2.0° E. This differs from a proposed site or a sensor location.
- EMODnet reference-cell water-depth magnitude: 29.10 m below the product datum. One cell does not establish a surveyed seabed profile.

## Interpretation limits

These data are regional screening inputs. The 10 m and 100 m winds are reanalysis; the current 150 m turbine hub has not been measured or extrapolated. No automatic site-specific AEP or bankable P90 is produced. Marine values are short-horizon forecasts. Register/lease statuses are retained by source and vintage. TEC cumulative stages are not summed into available headroom. NSTA carbon licences do not establish storage capacity or project rights.

Prepared category views: C02, C07, C08, C09, C13, C16, C34, C35, C37, C39, C41, C44, C67, C69.
Source attribution and exact raw-response SHA-256 lineage are available through Data sources & APIs and the preserved metadata files.

## Use in the application

Start the local app with `D:\Wind_Farm_Design\Start-Studio.ps1`, open Data sources & APIs, and select the collected revision. C07/C08 show wind, C13 waves, C16 bathymetry, C37 wind agreements/REPD, C34/C35 register context, and C39/C41/C44 NSTA records. Select providers and Collect selected sources to refresh. Fresh caches are reused unless bypassed.

## Provenance records

### The Crown Estate wind-site agreements
- Retrieved: 2026-11-01T11:19:25.207349+00:00; checked: 2026-11-01T11:19:25.261970+00:00.
- Publisher modified: 2026-09-29T15:07:19+00:00.
- Licence: The Crown Estate Open Data Licence (GIS) v1.1.
- Attribution: © The Crown Estate, 2026.
- Validated payload SHA-256: `bea05604c093054d22063cfed761f0ad45181e0adfeae2d72928bfa7d16ff4ec`.
- Raw response count: 5; cached requests: 0.

### DESNZ Renewable Energy Planning Database
- Retrieved: 2026-11-01T11:19:27.221305+00:00; checked: 2026-11-01T11:19:27.794180+00:00.
- Publisher modified: See original publication / source metadata.
- Licence: Open Government Licence v3.0; see original publication.
- Attribution: Contains public sector information licensed under the Open Government Licence v3.0.
- Validated payload SHA-256: `c640d0c1b1c3d128566e6dd6448f120ad04d4e9cddc2283fa522d9e1dfbd0720`.
- Raw response count: 2; cached requests: 0.

### ERA5 wind via Open-Meteo
- Retrieved: 2026-11-01T11:19:29.939099+00:00; checked: 2026-11-01T11:37:18.365412+00:00.
- Publisher modified: See original publication / source metadata.
- Licence: CC BY 4.0; free endpoint for non-commercial educational use.
- Attribution: Weather data by Open-Meteo.com; ERA5 / Copernicus Climate Change Service.
- Validated payload SHA-256: `4bb1415a36892c3d650ef14de8b4bfd4b1cf6efca05346ce672c58052804f538`.
- Raw response count: 1; cached requests: 1.

### Open-Meteo marine forecast
- Retrieved: 2026-11-01T11:19:32.056474+00:00; checked: 2026-11-01T11:19:32.073371+00:00.
- Publisher modified: See original publication / source metadata.
- Licence: CC BY 4.0; free endpoint for non-commercial educational use.
- Attribution: Weather data by Open-Meteo.com; underlying wave model as documented by provider.
- Validated payload SHA-256: `cf0ed7a369150d8c393084d3f59119f866240f9282fd82ee3df38b043fde972f`.
- Raw response count: 1; cached requests: 0.

### EMODnet bathymetry
- Retrieved: 2026-11-01T11:19:33.467378+00:00; checked: 2026-11-01T11:19:33.476641+00:00.
- Publisher modified: See original publication / source metadata.
- Licence: CC BY 4.0 (EMODnet data product); not for navigation.
- Attribution: EMODnet Bathymetry consortium; data product owned by the EU, CC BY 4.0.
- Validated payload SHA-256: `4db4a629029f7bdc8340522ed1d56f167ac999c35f36d00b9049b68acf4ca068`.
- Raw response count: 2; cached requests: 0.

### NESO Transmission Entry Capacity register
- Retrieved: 2026-11-01T11:19:35.746189+00:00; checked: 2026-11-01T11:19:35.754611+00:00.
- Publisher modified: 2026-10-30T16:50:28.624426.
- Licence: NESO Open Data Licence.
- Attribution: National Energy System Operator, TEC Register.
- Validated payload SHA-256: `81617bca449b10cfc8e45dddc3b5aa60a5c3cb6c084ed2487073cef526ebf9cd`.
- Raw response count: 2; cached requests: 0.

### NSTA offshore hydrocarbon fields
- Retrieved: 2026-11-01T11:19:39.124779+00:00; checked: 2026-11-01T11:19:39.423892+00:00.
- Publisher modified: 2026-11-01T07:37:25+00:00.
- Licence: As stated in preserved NSTA ArcGIS item metadata.
- Attribution: North Sea Transition Authority
- Validated payload SHA-256: `aedfb7246696f97183a0a10051b9c30a016303c1f4b64f3c5bbf9b997dfc4da4`.
- Raw response count: 5; cached requests: 0.

### NSTA offshore infrastructure surface points
- Retrieved: 2026-11-01T11:19:42.419292+00:00; checked: 2026-11-01T11:19:42.458229+00:00.
- Publisher modified: 2026-07-06T12:00:31+00:00.
- Licence: As stated in preserved NSTA ArcGIS item metadata.
- Attribution: Contains North Sea Transition Authority information; see item licence.
- Validated payload SHA-256: `f6f97990472a5930fb228a460ecc070e62ec3a78a2f260b56d706d515a79b100`.
- Raw response count: 5; cached requests: 0.

### NSTA current carbon-storage licence polygons
- Retrieved: 2026-11-01T11:19:45.176526+00:00; checked: 2026-11-01T11:19:45.199001+00:00.
- Publisher modified: 2026-10-31T12:31:59+00:00.
- Licence: As stated in preserved NSTA ArcGIS item metadata.
- Attribution: North Sea Transition Authority
- Validated payload SHA-256: `81ed847cae3a79d8e04557028af03886e38362ffa4ec6dc256bc519df44d9b41`.
- Raw response count: 5; cached requests: 0.
