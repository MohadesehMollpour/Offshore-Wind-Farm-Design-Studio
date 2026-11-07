# A14 — Environmental and Consenting


- **Folder:** agents/A14_environment/
- **Owned categories:**
  - C48
  - C49
  - C50
  - C51
- **Must run after:**
  - A04
  - A06
  - A11
  - A12
  - A13
- **Specific instructions:** Produce EIA plan not a fictional completed EIA; identify protected areas, ecological surveys, consultation, cumulative wind/oil-gas/CCS impacts, mitigation, legislation and data gaps.
- **Must create:**
  - eia_plan.json
  - environment_layers.geojson
  - impact_register.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C48](../../categories/C48/README.md), [C49](../../categories/C49/README.md), [C50](../../categories/C50/README.md), [C51](../../categories/C51/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.

## Environmental atlas milestone — 1 November 2026

C48–C50 now have a real `environment_screening` public-source path: JNCC/Natural England geometry, declared protected interests and EMODnet relief with Leaflet/Three.js and real rayshader rendering. Revision 19 contains 22 regional sites, 127 interest rows and explicit unavailable IUCN metadata. The EIA, observed-species baseline and cumulative impact remain open. The independent acquisition register stays unreviewed until actual source/owner review. [Source identities, files, tests and reproduction](../../reports/environmental_atlas.md).
