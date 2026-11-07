# A15 — Construction and Supply Chain


- **Folder:** agents/A15_construction/
- **Owned categories:**
  - C52
  - C53
  - C54
- **Must run after:**
  - A06
  - A07
  - A08
  - A10
- **Specific instructions:** Compare build-out ports and vessel constraints, supplier lead times, installation sequence, export cable construction, weather delay scenarios and contingency.
- **Must create:**
  - construction_plan.json
  - procurement_risks.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C52](../../categories/C52/README.md), [C53](../../categories/C53/README.md), [C54](../../categories/C54/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
