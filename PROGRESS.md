# Project Progress

## Current Status

The project has completed the foundation, multi-agent orchestration, and core observability work.
The remaining work is mostly production-readiness, documentation, deployment, and release hardening.

## Completed

- RAG pipeline and Chroma persistence
- Multi-agent workflow and FastAPI endpoint
- Unit and integration tests
- Prometheus metrics endpoint
- Local Docker and docker-compose setup
- CI workflow for lint, tests, and Docker build
- Python 3.11 Dev Container with Ollama sidecar
- Dev Container image creates vscode-owned state mount points before connection
- Repository Copilot coding agent and four reusable development skills
- Git skill enforcing 50-character subjects and 70-character body lines
- Offline provider doubles for unit and graph integration tests
- Tag-triggered, validation-gated GHCR image publishing configuration
- Corrected CHROMA_PERSIST_DIR configuration,
  updated local setup documentation, and offline persistence regression tests

## Partial

- Monitoring: Prometheus scraping exists, but dashboards and alerting are not present
- Documentation: basic setup and full local startup are documented; deployment and architecture guidance remain incomplete
- Release automation: configured, but a tagged registry publication has not been verified
- Phase 3: metric definitions exist, but agent/RAG call-path instrumentation is absent
- Runtime correctness: API reads `final_state` instead of the graph's `final_report`
- Evaluation: structured content extraction reads `item` instead of `text`; coverage is missing
- Benefits analysis: recommendations are still static mock data

## Missing

- Cloud deployment configuration
- Demo frontend
- Performance tuning and caching

## Remaining Checklist

### Documentation

- [x] Document Dev Container and full local startup flow
- [ ] Complete environment-variable and provider-option reference
- [x] Add API usage examples and Swagger/OpenAPI notes
- [ ] Add deployment guide
- [ ] Add architecture overview

### Observability

- [ ] Add Grafana dashboards or dashboard JSON
- [ ] Add alerting rules and operating notes

### Deployment

- [ ] Choose a target platform
- [ ] Add deployment manifests or platform config
- [ ] Document rollout and rollback steps

### Product Surface

- [ ] Add a simple demo frontend
- [ ] Add performance tuning items for RAG and model calls

### Release

- [x] Fill in release automation (tag publication awaits verification)
- [x] Define a v1.0.0 release checklist in docs/releasing.md
- [ ] Bump version when release scope is complete

## Next-Step Roadmap

- [Six-phase implementation strategy](docs/implementation-strategy.md):
  code backlog, dependencies, decisions, and acceptance criteria.
- Ordered next steps: [.github/workflows/What_s next_(Post_PR_3).md](.github/workflows/What_s%20next_(Post_PR_3).md)
