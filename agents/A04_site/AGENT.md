# A04 — Marine Site Screening


- **Folder:** agents/A04_site/
- **Owned categories:**
  - C01
  - C02
  - C03
  - C04
  - C05
  - C06
- **Must run after:**
  - A03
- **Specific instructions:** Validate project polygon and coordinate system; overlay sea plans, restrictions, distance-to-shore/ports and scored competing sites. Score weights transparently and avoid overriding legal hard exclusions.
- **Must create:**
  - sites.geojson
  - site_comparison.csv
  - site_decision.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C01](../../categories/C01/README.md), [C02](../../categories/C02/README.md), [C03](../../categories/C03/README.md), [C04](../../categories/C04/README.md), [C05](../../categories/C05/README.md), [C06](../../categories/C06/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
