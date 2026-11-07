# A09 — Energy Yield and Uncertainty


- **Folder:** agents/A09_energy/
- **Owned categories:**
  - C26
  - C27
  - C28
  - C29
  - C30
- **Must run after:**
  - A05
  - A07
  - A08
  - A11
- **Specific instructions:** Calculate gross generation from wind distribution and certified or explicitly assumed power curves; track losses exactly once and net P50/P90, hourly proxy and capacity factor.
- **Must create:**
  - energy_model.py
  - yield_scenarios.json
  - energy_hourly.parquet
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C26](../../categories/C26/README.md), [C27](../../categories/C27/README.md), [C28](../../categories/C28/README.md), [C29](../../categories/C29/README.md), [C30](../../categories/C30/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
