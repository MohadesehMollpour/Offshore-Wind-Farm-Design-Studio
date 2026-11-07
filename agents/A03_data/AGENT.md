# A03 — Source and Data Librarian


- **Folder:** agents/A03_data/
- **Owned categories:**
  - C67
- **Must run after:**
  - A01
- **Specific instructions:** Find authoritative data by jurisdiction and date. Record retrieval URL, publisher, coverage, variable, spatial/temporal resolution, licensing, download method, checksum and limitations. Explicitly mark inaccessible data and prohibited scraping.
- **Must create:**
  - source_catalog.json
  - data_licence_register.csv
  - data_gap_register.json
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C67](../../categories/C67/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
