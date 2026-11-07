# A08 — Layout and Wake


- **Folder:** agents/A08_layout/
- **Owned categories:**
  - C23
  - C24
  - C25
- **Must run after:**
  - A07
  - A05
  - A04
  - A11
- **Specific instructions:** Generate compliant turbine point candidates; calculate directional wakes including other wind farms only with justified models; assess internal spacing, array footprint, cost/ecology trade-offs and errors in supplied coordinate geometry.
- **Must create:**
  - turbines.geojson
  - layout_scenarios.json
  - wake_results.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C23](../../categories/C23/README.md), [C24](../../categories/C24/README.md), [C25](../../categories/C25/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
