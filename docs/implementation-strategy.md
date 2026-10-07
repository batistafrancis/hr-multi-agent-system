# Implementation strategy

This is a technical implementation plan based on the inspected code and the
[technical onboarding guide](architecture-and-local-setup.md). It groups the
previous backlog into six core phases and separates later operational work.
Backlog numbers are retained so individual tasks can be tracked consistently.

Status recorded on 2026-10-06: item 1 is complete. All other items below remain
planned; existing partial implementations do not mean their acceptance criteria
have been met.

## Scope and working rules

- Fix runtime correctness before adding deployment or a frontend.
- Implement and verify a real layer before removing its runtime mock.
- Keep offline test doubles and clearly labeled sample fixtures.
- Do not silently substitute demo data, empty results, or successful-looking
  responses for failed provider calls.
- Use only approved data with external providers. Live downloads and provider
  calls require approval.
- Preserve existing behavior unless a contract change is explicitly agreed.
- Add regression tests and update related documentation with each change.
- Do not create commits automatically. When commits are requested, omit the
  Copilot signature/co-author trailer, as requested by the project owner.

## Phase overview and dependencies

| Phase | Objective | Prerequisites |
|---|---|---|
| 1 | Configuration and provider selection | None |
| 2 | API and structured output | Phase 1 provider configuration for provider-specific behavior; the report-field fix can proceed independently |
| 3 | Research layer | Phase 1 provider/error configuration; Phase 2 contracts where research changes affect responses |
| 4 | Benefits analysis and RAG | Phase 1 embedding configuration and Phase 2 role schema |
| 5 | Reporting and evaluation | Phase 2 schema, Phase 3 sourced research, and Phase 4 grounded benefits for end-to-end integration |
| 6 | Observability and verification | Instrumentation can accompany earlier phases; final acceptance depends on Phases 1-5 |

Phases 3 and 4 can progress independently after their prerequisites are ready.
Tests and instrumentation should accompany each implementation, not wait until
Phase 6. Small isolated fixes, such as evaluator text extraction, can be done
before their phase's full integration.

## Phase 1: Configuration and provider selection

Relevant code: [settings](../src/core/settings.py),
[retrieval](../src/tools/rag_retriever.py),
[role designer](../src/agents/role_designer.py),
[Dev Container configuration](../.devcontainer/compose.yml), and
[runtime Compose configuration](../docker-compose.yml).

### Backlog

- [x] **1. Correct persistence naming.** Use `chroma_persist_dir` and
  `CHROMA_PERSIST_DIR` consistently. No legacy alias or deprecation layer.
  Default storage is unchanged; existing databases are not moved or deleted.
- [ ] **2. Separate generation and embedding provider selection.** Stop
  choosing generation based on the embedding model name. Validate each
  provider's required credentials, URL, and model configuration.
- [ ] **3. Separate generation and embedding model names.** Verify embedding
  capability and use consistent embedding configuration for seeding/retrieval.
- [ ] **4. Align startup configurations.** Synchronize environment examples,
  Dev Container, runtime Compose, and documentation. Make failed downloads or
  seeding stop startup; distinguish automatic and manual steps.

### Acceptance criteria

- Tests cover supported provider choices and missing/invalid configuration
  without calling external services.
- Selecting an embedding provider does not implicitly change generation.
- Startup examples use the actual supported settings and fail explicitly when
  prerequisites are unavailable.
- Item 1 already has offline tests for defaults, environment/.env loading,
  precedence, constructor configuration, and retriever path selection.

## Phase 2: API and structured output

Relevant code: [API](../src/api/main.py),
[state](../src/core/state.py), and
[role designer](../src/agents/role_designer.py).

### Backlog

- [ ] **5. Fix the report response field.** Return the graph's `final_report`
  rather than the nonexistent `final_state`.
- [ ] **6. Validate structured role output.** Define a Pydantic role schema
  for title, summary, responsibilities, skills, and recommended benefits.
  Use supported structured output or explicit parsing and validation.
- [ ] **7. Define the API response contract.** Distinguish the structured role,
  rendered role description, and Markdown report. Preserve or explicitly
  version existing behavior.
- [ ] **8. Validate topic input.** Reject blank/whitespace-only input and agree
  on length limits. Document the query parameter or approve a body migration.
- [ ] **9. Handle failures explicitly.** Add appropriate timeouts and bounded
  retries. Return useful API errors without leaking internal exception details.
  Define whether partial results are allowed and how they are labeled.

### Decisions before implementation

- Approve field names and the compatibility approach for structured responses.
- Agree on input limits and whether the query parameter remains.
- Decide strict failure versus explicitly labeled partial output.

### Acceptance criteria

- API regression tests assert a nonempty report and valid role shape.
- Malformed model output is rejected or handled by an explicitly bounded
  recovery path, never returned as a validated role.
- Input and provider failure tests assert the agreed status codes and bodies.

## Phase 3: Research layer

Relevant code: [researcher](../src/agents/researcher.py),
[search tool](../src/tools/search.py), and [state](../src/core/state.py).

### Backlog

- [ ] **10. Implement real research and remove silent runtime mocks.**
  Require valid live configuration; retain demo behavior only if an explicit
  demo mode is approved.
- [ ] **11. Remove the hard-coded research year.** Use the current year or an
  explicitly configured research period.
- [ ] **12. Preserve provenance.** Store source URLs, titles, and snippets,
  then carry citations into the report.
- [ ] **13. Use competitor and compensation findings.** Feed relevant results
  into role design/reporting or remove unused searches and state.
- [ ] **14. Avoid blocking asynchronous requests.** Use async provider APIs
  or safely offload synchronous search/retrieval calls.

### Acceptance criteria

- Missing credentials and search failures produce explicit outcomes, not
  ordinary research text or mock results in live mode.
- Tests verify source metadata survives state updates and reaches consumers.
- Queries use the intended research period.
- Provider boundaries remain mockable; approved live smoke checks are separate.

## Phase 4: Benefits analysis and RAG

Relevant code: [benefits analyst](../src/agents/benefits_analyst.py),
[retriever](../src/tools/rag_retriever.py),
[seeding](../scripts/seed_rag.py), and
[sample benefits](../data/sample_benefits.json).

### Backlog

- [ ] **15. Implement grounded benefits analysis.** Analyze the validated role
  against company benefits, then remove hard-coded runtime benefit lists.
  Distinguish existing benefits from proposed additions.
- [ ] **16. Validate benefit recommendations.** Link recommendations to policy
  records and reconcile role-designer suggestions with final analyst output.
- [ ] **17. Make seeding idempotent.** Use stable IDs and updates/upserts.
  Make replacement/reset operations explicit.
- [ ] **18. Protect embedding compatibility.** Record provider/model metadata,
  reject incompatible collection use, and require deliberate reindexing.
- [ ] **19. Handle retrieval outcomes explicitly.** Distinguish no relevant
  documents from provider/database failures and define behavior for each.
- [ ] **20. Add approved document ingestion.** Define supported formats and
  metadata handling. Keep sample benefits as labeled demo/test fixtures.

### Decisions before implementation

- Agree on the distinction between available benefits and proposed benefits.
- Select ingestion formats and required source/policy metadata.
- Define behavior when no grounded company context is available.

### Acceptance criteria

- Seeding twice does not increase the document count for unchanged input.
- Incompatible embedding configurations fail with actionable errors.
- Recommendations presented as available reference actual company records.
- Tests cover empty retrieval, provider failures, updates, and ingestion errors.
- Static runtime recommendations are removed only after the replacement passes.

## Phase 5: Reporting and evaluation

Relevant code: [report compiler](../src/agents/report_compiler.py),
[evaluator](../src/evaluation/evaluator.py), and
[workflow](../src/core/graph.py).

### Backlog

- [ ] **21. Render validated reports.** Use structured role fields, sourced
  research, compensation/competitor findings, and grounded benefits.
  Label unavailable sections explicitly.
- [ ] **22. Fix evaluator content extraction.** Read `text`, not `item`.
  Test string and structured-message content.
- [ ] **23. Harden scoring.** Validate numeric ranges and parsing, expose
  evaluation failure, and use schema-based completeness checks.
- [ ] **24. Configure evaluation providers explicitly.** Remove the fixed
  Ollama plus sentence-transformers assumption.
- [ ] **25. Integrate evaluation deliberately.** Choose offline evaluation,
  per-request scoring, or a separate endpoint. Define thresholds and failure
  behavior rather than implicitly adding expensive model calls.

### Decisions before implementation

- Choose where evaluation runs and approve its cost/latency implications.
- Define measurable quality thresholds and what failing them means.

### Acceptance criteria

- Reports contain validated fields and traceable supporting sources.
- Evaluation tests cover malformed content, invalid/out-of-range scores, and
  incomplete roles without successful-looking fallback scores.
- Integration tests verify the chosen evaluation execution and failure policy.

## Phase 6: Observability and verification

Relevant code: [middleware](../src/api/middleware.py),
[metrics](../src/observability/metrics.py),
[logging](../src/utils/logging_conf.py), [API](../src/api/main.py),
and [tests](../tests/).

### Backlog

- [ ] **26. Instrument actual calls.** Record agent/provider errors, RAG/model
  latency, and token usage where supported. Verify metric increments.
- [ ] **27. Fix request tracing.** Establish request IDs before logging and
  propagate them through agents/provider calls, including failures.
- [ ] **28. Align logging and documentation.** Choose structured logging or
  document standard logging accurately. Exclude sensitive data.
- [ ] **29. Separate liveness from readiness.** Check required providers,
  models, and retrieval storage without confusing process health with readiness.
- [ ] **30. Expand verification.** Add regression coverage throughout the
  earlier phases and an opt-in live Ollama smoke test for seeding, retrieval,
  and generation. Keep mocked providers in offline tests.

### Acceptance criteria

- Success and failure paths emit the expected metrics and request IDs.
- Readiness fails when a required dependency is unavailable; liveness remains
  an independent process check.
- Logs do not expose credentials, private prompts, or HR records.
- Approved live generation returns a validated role and nonempty report;
  HTTP 200 alone is not sufficient.

## Validation for each implementation slice

Run focused regression tests first. Run applicable repository checks from the
Linux Dev Container terminal, not Windows PowerShell:

```bash
python -m ruff check src scripts tests
python -m black --check src scripts tests
python -m mypy src --ignore-missing-imports
python -m pytest tests -v
```

Use the selected project interpreter. Documentation-only updates do not require
Python tests. Report which checks actually ran, and keep offline verification
distinct from live provider validation.

Before marking a task complete, verify its exact acceptance criteria, update
related documentation, and confirm changes are saved. Do not count a declared
metric, prompted JSON output, or healthy HTTP process as proof of the underlying
behavior.

## Later operational work

These were backlog items 31-35, outside the six core phases:

- [ ] **31. Reproducible dependencies.** Establish a maintained lock strategy
  and verify installation in a clean environment. This can proceed independently
  or earlier if dependency instability blocks core work.
- [ ] **32. Dashboards and alerts.** Build on verified metrics from Phase 6.
- [ ] **33. Performance and caching.** Measure latency/resource targets first;
  define invalidation and HR-data isolation before adding caches.
- [ ] **34. Deployment and release verification.** Select a target, verify
  writable persistence, configuration, rollout/rollback, and image publication.
- [ ] **35. Optional demo frontend.** Add after the backend contract is stable.

Supervisor agents, parallel execution, conversation memory, and human approval
are not automatic requirements. Introduce them only when an agreed HR use case
requires them.

## Development-environment work

Persistence and SSH setup are a separate supporting workstream, not additional
HR runtime agents or a replacement for these phases. See the
[Dev Container persistence guide](devcontainer-persistence.md). Volume
restoration, rebuilt-container checks, chat rediscovery, and host SSH forwarding
must be verified before that workstream is considered complete.

## Next implementation slice

Continue with Phase 1 items 2 and 3: agree on explicit generation and embedding
configuration, implement the provider boundaries, and add offline selection and
validation tests. Then align startup configuration under item 4.

For existing project status and release procedures, see
[PROGRESS.md](../PROGRESS.md) and the [release guide](releasing.md).
