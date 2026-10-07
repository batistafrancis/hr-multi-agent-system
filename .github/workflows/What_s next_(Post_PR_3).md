# Next Steps After PR #3

## Readiness work implemented

- Repository Copilot coding agent and four development skills.
- Python 3.11 Dev Container with Ollama sidecar.
- CI for lint, formatting, types, offline tests, and production image validation.
- Validation-gated GHCR image publication on version tags.
- Development guide and v1.0.0 release checklist.

GitHub CI checks passed for the readiness implementation. Live provider behavior
and tagged registry publication still require verification. Image automation alone
does not establish production readiness.

## Recommended implementation order

### 1. Review and validate the local workflow

- [ ] Review PR #3 and the implementation reading guide.
- [ ] Follow the README's Windows Dev Container startup steps.
- [ ] Download the Ollama model and seed only sample benefits.
- [ ] Verify live role generation and inspect the generated state and response.
- [ ] Record provider failures and startup limitations before deploying.

### 2. Fix runtime correctness

Recommended next branch scope: runtime correctness and Phase 3 observability.

- [ ] Return `final_report` from the API instead of reading `final_state`.
- [ ] Ensure provider failures are explicit, not successful reports or research.
- [ ] Correct evaluation content extraction from `item` to `text`.
- [ ] Add regression tests for report content, evaluation extraction, and errors.
- [ ] Keep external providers mocked in automated tests.

### 3. Complete Phase 3 instrumentation

- [ ] Wire agent and RAG counters into actual call paths.
- [ ] Verify request ID propagation and structured logging.
- [ ] Keep metric labels bounded and avoid sensitive HR data in telemetry.
- [ ] Add tests for successful and failed calls.

### 4. Implement grounded benefits analysis

- [ ] Replace static recommendations with analysis grounded in available benefits.
- [ ] Keep state keys and report compilation consistent across agents.
- [ ] Test relevance, missing context, and provider failure behavior.

### 5. Add monitoring and measured performance improvements

- [ ] Add Grafana dashboards and operating notes.
- [ ] Add and test actionable alerting rules.
- [ ] Measure RAG and model latency before selecting optimizations.
- [ ] Add caching with tested invalidation and data-isolation behavior.
- [ ] Review blocking provider calls and async execution.

### 6. Prepare deployment and the demo

- [ ] Choose a cloud platform explicitly.
- [ ] Add deployment configuration, writable persistence, and readiness checks.
- [ ] Document and verify rollout and rollback.
- [ ] Add a simple demo frontend.
- [ ] Complete architecture and environment-variable documentation.

### 7. Release only after readiness gates pass

- [ ] Complete the v1.0.0 checklist.
- [ ] Obtain approval for the version bump, release tag, and image publication.
- [ ] Verify the tagged Actions run and published image digest.
- [ ] Obtain separate approval for cloud deployment.

## References

- [Local startup and recommended next steps](../../README.md)
- [Project progress checklist](../../PROGRESS.md)
- [Implementation reading guide and release checklist](../../docs/releasing.md)
