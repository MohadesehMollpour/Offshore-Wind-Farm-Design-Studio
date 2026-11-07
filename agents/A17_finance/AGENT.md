# A17 — Finance and Hybrid Synergies


- **Folder:** agents/A17_finance/
- **Owned categories:**
  - C58
  - C59
  - C60
  - C61
- **Must run after:**
  - A09
  - A10
  - A12
  - A13
  - A14
  - A15
  - A16
- **Specific instructions:** Compute dated real/nominal CAPEX OPEX cash flows, discounted LCOE, NPV, IRR, price capture and uncertain scenarios. Separately compare baseline farm, shared O&M, platform power and CCS hybrid options; assign boundary/system costs correctly.
- **Must create:**
  - finance_model.py
  - finance_scenarios.json
  - sensitivity.csv
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C58](../../categories/C58/README.md), [C59](../../categories/C59/README.md), [C60](../../categories/C60/README.md), [C61](../../categories/C61/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
