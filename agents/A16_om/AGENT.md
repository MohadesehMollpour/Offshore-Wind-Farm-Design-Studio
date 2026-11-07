# A16 — O&M and Reliability


- **Folder:** agents/A16_om/
- **Owned categories:**
  - C55
  - C56
  - C57
- **Must run after:**
  - A06
  - A13
  - A07
  - A11
- **Specific instructions:** Model CTV/SOV, ports, travel/weather access, component failure and repair durations, downtime and availability. Evaluate reuse of nearby platform O&M facilities quantitatively with safety and owner-permission caveats.
- **Must create:**
  - om_model.json
  - maintenance_calendar.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C55](../../categories/C55/README.md), [C56](../../categories/C56/README.md), [C57](../../categories/C57/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
