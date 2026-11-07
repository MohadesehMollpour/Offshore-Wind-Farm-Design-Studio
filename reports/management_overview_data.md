# Management overview data collection — 2026-11-01

> **Historical milestone:** Regional overview milestone; revision 9 and the 197-test count are historical. Later C61 supports conditional NPV when an explicit price is supplied; the saved reference still has no captured price. Current behavior and validation are in [status](../docs/STATUS.md), [verification](../docs/VERIFICATION.md) and [the handover](../PROJECT_HANDOVER.md).

The management overview in revision 9 now calculates **4,485.1 GWh/year** net energy and **£88.55/MWh in real 2024 GBP** for the 990 MW regional reference case. These are estimates, not measured project performance, a supplier budget or an investment-ready conclusion.

Scenario: `65608a36-9c03-4281-9adb-3cfc143990b6`. Live route: http://127.0.0.1:8000/projects/a77feb50-35c9-424a-87e8-a42cf756be4e/overview?scenario=65608a36-9c03-4281-9adb-3cfc143990b6

## Downloaded sources

- ERA5 via Open-Meteo: 43,824 hourly observations at each of 10 m and 100 m for 2021–2025. These are gridded reanalysis values at the existing Hornsea regional reference, not instrument measurements at a proposed site. Documentation: https://open-meteo.com/en/docs/historical-weather-api
- IEA 15 MW reference turbine: tabular power curve and specification (240 m rotor, 150 m hub), plus the archive's BSD-3-Clause licence. The curve is theoretical. Archive: https://github.com/NatLabRockies/turbine-models
- DESNZ Electricity Generation Costs 2025: current Annex A workbook and report, with generic fixed-offshore values for commissioning in 2030–2050, in real 2024 GBP. Portal: https://www.gov.uk/government/publications/electricity-generation-costs-2025
- Arup offshore cost/technical report: original PDF; manually checked wake and availability benchmarks in PDF page 53 / printed page 48. PDF checksum is pinned so an upstream replacement cannot silently change the extraction. Portal: https://www.gov.uk/government/publications/offshore-wind-cost-and-technical-assumptions

The named local source library is `D:\Wind_Farm_Design\data\library\overview-r9`. The downloadable ZIP contains 14 files: original source documents/data, hourly wind and modelled generation CSV, monthly and weather-year CSVs, results/assumptions JSON, provenance JSON, README and a SHA-256 manifest. ZIP size: 5,796,896 bytes. The app can download each preserved cost/turbine source directly.

## Calculation basis

Wind at 150 m is explicitly extrapolated from 100 m using a constant exponent of 0.095401, derived from the ratio of period-mean 100 m and 10 m speeds. The model linearly interpolates the published IEA curve, applies the assumed 66 turbines, annualizes to 8,760 reporting hours and applies sequential losses. Defaults are wake 8% and availability loss 4.1% from Arup benchmarks, plus explicitly assumed electrical loss 3% and curtailment 2%. Existing scenario loss overrides take precedence.

2030 costs use Annex A, `Technical and Cost Assumptions`, column N: pre-development N8 + construction N20 = £2,670/kW; fixed O&M N34 + insurance N36 + connection/use-of-system charges N37 = £141.6/kW/year; discount rate N39 = 8.9% real; terminal decommissioning N43 = £265,200/MW. Cell labels, units, commissioning years, price basis and required cached values are checked before use. The source workbook's external links and formulas are never executed.

LCOE uses upfront CAPEX, constant annual energy/operating costs, and terminal decommissioning discounted over 30 years. It excludes construction financing/phasing, debt, tax, degradation, seabed rent and site-specific premiums. It is not a reproduction of DESNZ's published £103/MWh generic 2030 benchmark. The latter is displayed separately as context. NPV, IRR, payback and P90 remain unavailable; no revenue price or probabilistic yield confidence is fabricated.

## App changes and scope

An explicit `regional_screening_case` flag and bound `overview_inputs` dataset activate this calculation. Regional wind collection alone still cannot produce site energy. A site-scoped imported wind dataset retains the original site calculation path. No AOI or feasible layout is invented. The new source is registered as the eleventh adapter.

The overview has selectable weather-year and wind-speed sensitivity plots, visible assumptions, original-file downloads, and a refresh action that collects data and opens a new immutable revision. Older pinned revisions offer an Open revision 9 link. C21, C26, C27, C29 and C58–C61 show the corresponding scoped regional plots and assumptions; they continue to disclose incomplete specialist methods.

## Verification

- 197 Python tests passed, including independent energy, loss reconciliation, interpolation/cut-out, LCOE, operating-cost inclusion, price-basis guards, source-table schema/units, immutable activation, original-file download integrity and preserved site-data guards.
- TypeScript checking and Vite production build passed.
- Browser verification confirmed numeric KPI cards, sensitivity selection, source workbook download, overview refresh through queued/running/completed to revision 9, older-revision navigation and C60 breakdown. No browser console errors were recorded.
- All 70 category packages and four original assignment-source checksums passed workspace verification.
- Revision 9: 11 bound source datasets, 94 unique immutable raw objects, 24,255,047 bytes; payload/raw SHA-256 and provider/project/site/AOI/reference-point checks passed. The ZIP was reopened, CRC-checked and each contained file compared to its SHA-256 manifest.

Remaining project-specific needs: proposed site boundary and rights, measured hub-height wind/long-term correction, validated wake/layout assessment, grid and curtailment evidence, surveyed seabed, itemized supplier costs and revenue terms. Regional estimates do not close these gaps.
