# A13 — Oil and Gas Infrastructure Reuse


- **Folder:** agents/A13_oilgas/
- **Owned categories:**
  - C44
  - C45
  - C46
  - C47
- **Must run after:**
  - A04
  - A06
  - A03
  - A12
- **Specific instructions:** Find platforms, rig facilities, pipelines, ports and owner/decommission status; assess offshore maintenance reuse and logistics, operating safety, structural capacity, weather access and contracts; compare repurpose/electrification only as scenarios.
- **Must create:**
  - platforms.geojson
  - reuse_screening.json
  - asset_synergy_scenarios.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C44](../../categories/C44/README.md), [C45](../../categories/C45/README.md), [C46](../../categories/C46/README.md), [C47](../../categories/C47/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
