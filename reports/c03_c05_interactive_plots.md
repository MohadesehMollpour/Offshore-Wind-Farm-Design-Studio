# C03, C04 and C05 interactive plots

> **Historical milestone:** C03–C05 milestone; its 177-test count and revision-5/6 identifiers are historical. Current behavior and validation are in [status](../docs/STATUS.md), [verification](../docs/VERIFICATION.md) and [the handover](../PROJECT_HANDOVER.md).

Implemented in D:\Wind_Farm_Design and available in the running local app.

- C03: adjustable three-criterion preference weights, linked ranking bars, weight sensitivity, parallel coordinates, Pareto status, accessible data and CSV export.
- C04: selectable coast/port map and distance bars, asset filters, vessel-speed controls, clearly labelled straight-line time proxies and CSV export.
- C05: annual AIS density overlay, vintage and opacity controls, density threshold, linked sample/zone selection, exposure bars and CSV export.

Ten public-source adapters are now registered. The new composite source collected 13 main-port positions, a clipped Natural Earth coastline, four existing Hornsea agreement benchmarks, and 25 AIS reference-grid samples plus four benchmark samples for both 2023 and 2024. All 58 density queries returned valid values.

Numeric values use preserved source responses. The map basemap and AIS raster are online context layers. Existing agreements are reference benchmarks, not available development sites. Ports are a published main-port inventory, not a capability assessment. Grid coordinates, navigable vessel/cable routes and aviation restrictions remain explicit gaps. The 2024 AIS series has reduced satellite coverage from June; it must not be read as a traffic trend against 2023.

The 40/30/30 screening preference defaults are separate from the assignment assessment rubric. Changing them never overrides exclusions or establishes site eligibility. Sliders explore locally; Save preferences/controls creates a new immutable revision and runs C03–C05. Revision selection can reopen older evidence without changing its results.

Data collection revision: 5, scenario 3643ee84-eec5-44b2-b660-e215c59ec829.
Browser-verified saved revision: 6, scenario cadcdc5b-b6e1-4c40-8192-b767752ff598 (default controls retained).

Validation: 177 Python tests passed; TypeScript checking and Vite production build passed. Browser checks confirmed slider-driven ranking changes, parallel-coordinate switching, linked selection, saved revision loading, C04 distance/time filtering, C05 threshold/vintage controls, and source/missing-data disclosures. Workspace/source integrity checks are recorded in docs/VERIFICATION.md.
