# C68 — AI disclosure, authorship, evidence and learning

[Specification](SPECIFICATION.md) · [Data sources](DATA_SOURCES.md) · [Specialist prompt](SYSTEM_PROMPT.md) · [Changelog](CHANGELOG.md) · [All categories](../../docs/CATEGORIES.md)

## Implemented behavior

Human/AI section contribution/disclosure coverage; actual authorship and review must be entered.

**Reference checkpoint:** revision 17, `7a527938-aa43-4d17-8203-9ce2d64d0bb1`; classification **built-in calculation/project view**, result `needs-review`, evidence maturity `user_supplied_or_assumed`. This is the saved Hornsea reference, not a claim about every scenario or engineering completion.

**Code:** `backend/engine.py and backend/external_analysis.py`; view `dashboard/src/main.tsx`. The category adapter is `src/controller.py`. Ownership: [A01](../../agents/A01_intake/AGENT.md), [A02](../../agents/A02_review/AGENT.md), [A21](../../agents/A21_qa/AGENT.md).

## Evidence and continuation

Required domain inputs: agent logs, student input. Expected specialist outputs: AI per section, original contribution, critique records. These remain requirements where evidence or a specialist method is missing. Read the source guide and current result gaps before extending the package.

Preserve provider/project/site/AOI/reference-point scope, source hashes, units and assumption labels. See [the handover](../../PROJECT_HANDOVER.md) for the implementation map and verification workflow.
