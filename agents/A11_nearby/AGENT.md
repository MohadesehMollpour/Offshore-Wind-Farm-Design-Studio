# A11 — Nearby Wind Farms


- **Folder:** agents/A11_nearby/
- **Owned categories:**
  - C37
  - C38
- **Must run after:**
  - A04
  - A03
- **Specific instructions:** Discover operating, constructing, consented and leased offshore projects; map polygon overlap and turbine distance, stage and MW, and potential cumulative wakes and ecological impacts. Never infer current operation from a lease boundary.
- **Must create:**
  - nearby_farms.geojson
  - cumulative_effects.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C37](../../categories/C37/README.md), [C38](../../categories/C38/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
