---
name: hr-workflow-development
description: Use when changing HR agents, LangGraph orchestration, RAG retrieval, or generate-role behavior.
---

# HR workflow development

1. Read src/core/state.py and src/core/graph.py, then the affected agents and API.
2. Trace each state key from producer to consumer. Nodes return updates, not necessarily full state.
3. Inspect src/core/settings.py for the actual provider selection rules before changing integrations.
4. Add a focused offline regression test before changing observable behavior.
5. Keep external calls behind mockable boundaries; do not download embeddings or call paid APIs in tests.
6. Check report content, state merging, error paths, and metrics for the affected flow.
7. Run the validation skill and update README.md and PROGRESS.md if the public contract changes.

Do not claim benefits analysis is model-backed while it remains a static mock.
Do not claim an HTTP health response proves model or vector-store readiness.
