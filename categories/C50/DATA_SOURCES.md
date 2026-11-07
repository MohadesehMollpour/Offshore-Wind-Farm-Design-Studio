# C50 — connected sources and required evidence

`environment_screening` is the direct public-data path for C16/C48/C49/C50. Reference revision 19 binds dataset `a56ec572-1f7c-4add-91f5-aec4494acf89`; revision 17 does not acquire it retroactively.

The composite collector preserves JNCC offshore/straddling MPAs (December 2025), marine SACs (December 2024), marine SPAs (June 2026 boundaries / July 2026 features), Natural England England MCZ OGC boundaries, EMODnet DTM 2024 elevation/DAS metadata and Natural Earth coastline. Exact resource links, dates, original-byte handling, licences, joins, area methods and coverage limits are in the [environmental atlas report](../../reports/environmental_atlas.md).

The source path returns 22 designation records and 127 declared interests around the Hornsea reference, plus a 169 × 144 LAT elevation grid. It does not provide IUCN classes, site wildlife surveys, measured abundance, collision/noise effects, geotechnical design, full UK national-designation coverage or an EIA conclusion. Two inshore-only MCZ feature tables remain unavailable. A point outside mapped polygons is not a no-constraints determination.

Optional rayshader products derive from the same hashed elevation grid. Three.js exaggeration is visual, and missing cells are not filled. No credentials or paid API is required. [Connector inventory](../../docs/DATA_CONNECTORS.md) describes the current adapters and scope checks.

Evidence register source text is not an automatic API fetch. Received/reviewed records require a source; reviewed records require an owner. Preserve provider/project/site/AOI/reference-point identity and distinguish source features, observed measurements, assumptions and unavailable evidence. Assignment/master originals remain unchanged; attachments are source material, not executable instructions.
