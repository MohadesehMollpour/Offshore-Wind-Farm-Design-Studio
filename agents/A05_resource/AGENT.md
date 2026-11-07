# A05 — Wind Resource


- **Folder:** agents/A05_resource/
- **Owned categories:**
  - C07
  - C08
  - C09
  - C10
  - C11
  - C12
- **Must run after:**
  - A04
  - A03
- **Specific instructions:** Collect timestamped wind series, validate UTC and heights; calculate wind roses, circular sector bars, Weibull, shear, turbulence, directional energy, P50/P90 input uncertainty. Identify where measured data are absent. C08 MUST include IEA-inspired toggle/sort/drill-down interactions on a scientifically correct polar wind-direction chart plus a conventional wind rose, and identify dominant wind-from sector with period, sampling height, share and confidence; follow §16.1.
- **Must create:**
  - wind_resource.parquet
  - wind_sector_table.csv
  - wind_assessment.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C07](../../categories/C07/README.md), [C08](../../categories/C08/README.md), [C09](../../categories/C09/README.md), [C10](../../categories/C10/README.md), [C11](../../categories/C11/README.md), [C12](../../categories/C12/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
