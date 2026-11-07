# A21 — Cross-Model QA and Safety


- **Folder:** agents/A21_qa/
- **Owned categories:**
  - C67
  - C68
- **Must run after:**
  - A02
  - A09
  - A10
  - A11
  - A12
  - A13
  - A17
  - A20
- **Specific instructions:** Validate schema, formula consistency, geography, scenario lineage, capacity/energy constraints, temporal/calendar rules, licence status and representation of uncertainty. Block deployment/export of material critical failures or missing evidence.
- **Must create:**
  - qa_report.json
  - consistency_checks.json
  - blocking_issues.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C67](../../categories/C67/README.md), [C68](../../categories/C68/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
