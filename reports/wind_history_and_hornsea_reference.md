# Monthly wind box plots and Hornsea reference integration

> **Historical milestone:** Monthly-wind/C37 milestone; revision 11 and the 217-test count are historical. Current behavior and validation are in [status](../docs/STATUS.md), [verification](../docs/VERIFICATION.md) and [the handover](../PROJECT_HANDOVER.md).

Implemented in D:\Wind_Farm_Design, 2026-11-01. Current saved plot settings: revision 11, scenario `0f446760-01bd-4a93-b16e-0d5c684e888f`.

## C07 historical wind

The primary wind view now shows one box per UTC calendar month: Q1, median, Q3, observed whisker endpoints within 1.5×IQR, and optional outlier crosses. Quantiles use linear interpolation at rank (n−1)p. Missing observations are not replaced by zero.

The new operations_wind adapter downloaded **2025-10-01 through 2026-09-30**, the latest twelve whole months before the seven-day ERA5 availability allowance. There are **8,760 hourly values at each of 10 m and 100 m**, with no missing hours in the collected period. The independent 2021–2025 ERA5 dataset remains bound for the existing overview model and provides calendar-year selections. The calendar-year option reproduces January–December monthly ordering as in the supplied chart example.

Controls include period, wind sampling height, m/s or knots, sailing and O&M wind thresholds, threshold reference height, outlier visibility and selected month. Selected-month readouts and a monthly table expose quartiles, counts, missing hours and percentages of valid hourly values at/below the thresholds. Both CSV and standalone SVG downloads work; the SVG includes period and source/threshold metadata.

Defaults are **12 m/s sailing** and **10 m/s O&M**, referenced to 10 m. These are explicit illustrative planning assumptions, not published universal safe limits. The user can change them and record a vessel/task-specific basis. Lines and comparison percentages are hidden when the wind sampling height differs from the declared limit height. No implicit extrapolation is applied to this view.

Hourly reanalysis and wind-only percentages do not establish safe sailing, a transfer limit or consecutive workable hours. Gusts, waves, wave period/direction, currents, visibility, vessel response, task duration and approved operating procedures remain relevant. General transfer guidance: https://www.energyinst.org/technical/publications/sectors/renewables/good-practice-guideline-offshore-wind-farm-transfer . This source is guidance context, not the source of the illustrative numeric thresholds.

Saving plot settings creates a new immutable revision and refreshes all bound-source categories. Browser verification confirmed that C27 remains 4,485.0946 GWh/year and C60 remains 88.5504 real 2024 GBP/MWh after saving these display/threshold settings. Prior scenarios and source files retain their inputs and outputs.

Wind source: https://open-meteo.com/en/docs/historical-weather-api . ERA5 / Copernicus via Open-Meteo, CC BY 4.0, educational access. Recent dataset: 14730252-379d-4282-b14d-c064b62010fa. Historical values are gridded reanalysis, not physical sensor observations or measured turbine-hub wind.

## C37 attached Hornsea page

The supplied `Wind Farms Around Hornsea.html` belongs in **C37: Existing, consented and planned wind farms**, with a shortcut from the management overview. The official agreement map/status plots remain separate from the new attached-reference explorer.

The page's embedded JSON was parsed without executing its scripts. The app now provides a radial CF/capacity comparison, rolling/lifetime CF selection, operating/pipeline and area filters, sort options, linked schematic map, farm readout, accessible table and CSV/JSON/original-page downloads. There are **25 comparison records** and **one map-only record**. Missing capacity factors remain unavailable; pipeline records do not acquire invented generation data.

The snapshot claims October 2026 and cites EnergyNumbers, EMODnet and Wikipedia. Its capacities, capacity factors, owners, dates and project-status claims are **user-supplied and not independently verified**. Its reference point (53.8833° N, 1.9219° E), distances and SVG outlines are retained separately from the project's sampling point, official GIS geometry and any proposed AOI. This attachment never feeds suitability, wind-yield or finance calculations. It is context for nearby developments, not evidence of cumulative wake effects.

Original source SHA-256: `4b02e38d044ac03248237358b0ee3ba16d86bef0609cf4fd22abd7975ba686fa`. The original is preserved unchanged under `sources/references/hornsea_farms`, with derived JSON and metadata. The original download is served as an attachment; the app does not run its JavaScript or load its external fonts. The rebuilt visualization uses the existing local app styling.

## Verification

- 217 Python tests passed. New checks cover quartiles, IQR outliers, leap-month expected counts, missing versus zero wind, publication-lag month selection, height/source identity, imported-height preservation, preference validation, immutable save/refresh, overview-result preservation, reference SVG/numeric validation and original-file integrity.
- TypeScript checking and the Vite production build passed. The attached explorer loads separately when C37 opens.
- Browser checks covered wind period/height/unit selection, sliders, height mismatch, monthly readouts, saved revision loading, CSV/SVG exports, farm filters, linked selections and original/filtered downloads. Final visual checks corrected threshold-label overlap and missing-CF rendering.
- Revision 11 integrity: 12 datasets, 95 unique raw objects, 24,583,031 bytes; provider/project/site/AOI/reference-point checks and payload/raw checksums passed. The imported original HTML also matches its recorded checksum.
- The 70 category packages and four original assignment-source checksums passed workspace verification.

The screenshot supplied by the user was used as a visual reference for box-plot structure; its wave-height values were not used as wind data.
