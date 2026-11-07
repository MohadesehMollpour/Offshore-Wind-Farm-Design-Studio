# A10 — Electrical and Grid


- **Folder:** agents/A10_grid/
- **Owned categories:**
  - C31
  - C32
  - C33
  - C34
  - C35
  - C36
- **Must run after:**
  - A04
  - A06
  - A09
  - A03
- **Specific instructions:** Design array, offshore substation, HVAC/HVDC export, cable routes and voltage; discover feasible grid nodes and NESO constraint evidence. Never treat spare connection capacity as established from distance or TEC alone.
- **Must create:**
  - network.geojson
  - electrical_design.json
  - grid_access_register.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C31](../../categories/C31/README.md), [C32](../../categories/C32/README.md), [C33](../../categories/C33/README.md), [C34](../../categories/C34/README.md), [C35](../../categories/C35/README.md), [C36](../../categories/C36/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
