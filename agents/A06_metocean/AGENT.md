# A06 — Metocean and Seabed


- **Folder:** agents/A06_metocean/
- **Owned categories:**
  - C13
  - C14
  - C15
  - C16
  - C17
  - C18
  - C19
- **Must run after:**
  - A04
  - A03
- **Specific instructions:** Interrogate waves, currents, tides, seabed, sediment, geotechnical surveys and weather access; present site-specific versus regional evidence separately.
- **Must create:**
  - metocean.nc
  - geohazards.geojson
  - seabed_report.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C13](../../categories/C13/README.md), [C14](../../categories/C14/README.md), [C15](../../categories/C15/README.md), [C16](../../categories/C16/README.md), [C17](../../categories/C17/README.md), [C18](../../categories/C18/README.md), [C19](../../categories/C19/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
