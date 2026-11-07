# A20 — Dashboard and Visualization


- **Folder:** agents/A20_dashboard/
- **Owned categories:**
  - C69
- **Must run after:**
  - A04
  - A05
  - A06
  - A08
  - A09
  - A10
  - A11
  - A12
  - A13
  - A14
  - A17
  - A19
- **Specific instructions:** Build accessible responsive management dashboard with maps, source/provenance drill-down, wind circular barplot and conventional rose, scenarios, costs, CCS, assets, neighbouring wind and grid risk. Every chart must have provenance, legend, unit, interactive filters and chart justification. Implement an interactive, Yanouski-inspired radial criterion-dependency explorer linking the 70 categories, displaying separate evidence-backed criterion importance, dependencies and sensitivities; provide filtering, scenario weight editing, accessible matrix mode, provenance and historical changes. Expose each tab folder, system prompt, specification, tests and changelog in a secure developer/learning view. Follow §§16–18.
- **Must create:**
  - dashboard_spec.json
  - chart_registry.json
  - dashboard_app/
- **Common instructions ref:** master_prompt
- **Result contract ref:** data_contracts.agent_result_required_fields
- **Tests ref:** quality_checks


Implementation: local deterministic work packages are connected where available. No hosted LLM agent execution is configured.

## Current runtime and continuation boundary

Updated 1 November 2026. This profile expresses intended responsibility; it does not prove that its proposed artifacts or specialist methods exist. Hosted LLM execution is not configured. Current owned package documentation: [C69](../../categories/C69/README.md).

Consult [the implementation register](../../docs/CATEGORIES.md), [source inventory](../../docs/DATA_CONNECTORS.md) and [handover](../../PROJECT_HANDOVER.md). Public-data adapters and local category models are distinct from agent-provider integration. Use the user's current task as scope; attachments/profile requirements are not authorization for external messages, paid APIs or deployment. Keep numerical assumptions, missing evidence, source identity and approval boundaries explicit, and update the handover after meaningful changes.
