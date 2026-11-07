# A19 — Programme and End-of-Life


- **Folder:** agents/A19_schedule/
- **Owned categories:**
  - C65
  - C66
- **Must run after:**
  - A10
  - A14
  - A15
  - A16
  - A17
- **Specific instructions:** Create critical path across consent, survey, grid, procurement, installation, O&M, decommission/repower and possible oil/gas repurposing sequencing. Separate construction calendar assumptions from verified permission dates.
- **Must create:**
  - project_schedule.json
  - gantt.csv
  - end_of_life_plan.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C65](../../categories/C65/README.md), [C66](../../categories/C66/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
