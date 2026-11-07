# A12 — CO2 Storage and Reservoirs


- **Folder:** agents/A12_ccs/
- **Owned categories:**
  - C39
  - C40
  - C41
  - C42
  - C43
- **Must run after:**
  - A04
  - A03
- **Specific instructions:** Discover depleted oil/gas fields, saline aquifers, wells and carbon licences. Evaluate sealing, pressure, injectivity, capacity uncertainty, legacy well integrity, plume migration, seismic, transport, MMV, liabilities and jurisdiction. Separate candidate vs licensed vs permitted vs technically verified.
- **Must create:**
  - reservoir_candidates.geojson
  - ccs_screening.json
  - ccs_permissions.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C39](../../categories/C39/README.md), [C40](../../categories/C40/README.md), [C41](../../categories/C41/README.md), [C42](../../categories/C42/README.md), [C43](../../categories/C43/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
