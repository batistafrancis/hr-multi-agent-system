# HR Multi-Agent System

Multi-agent system for HR innovation, progressing toward production readiness:
Market research, role design, benefits analysis, and reporting.

Author: [Francis Batista](https://github.com/batistafrancis)


## Phase 1: Foundation & RAG

- ✅ RAG pipeline for company benefits and HR documents
- ✅ Vector search with ChromaDB
- ✅ Structured logging with structlog
- ✅ Environment-based configuration


## Quick Start

### Recommended: VS Code Dev Container

Start Docker Desktop (Linux containers), install the VS Code Dev Containers extension,
then run **Dev Containers: Reopen in Container**. The configuration in
[.devcontainer](.devcontainer/devcontainer.json) supplies Python 3.11, development
dependencies, and an Ollama sidecar; host Python is not required.

See the [development and release guide](docs/releasing.md) for validation commands,
model setup, API startup, and image publishing.

### 1. Setup Environment

```bash
python -m venv venv
source venv/bin/activate # or `venv\Scripts\activate` on Windows
pip install -e .
```


## Test Retrieval

```python
from src.tools.rag_retriever import RAGRetriever

retriever = RAGRetriever()
context = retriever.retrieve_context("What retirement benefits do we offer?")
print(context)
```

## Project Structure

- `src/agents/` - Agent implementations
- `src/tools/` - RAG, search, HRIS tools
- `src/core/` - Settings, state, graph
- `scripts/` - Seeding and utility scripts


## Phase 2: Multi-Agent Orchestration

- ✅ Researcher agent (web search)
- ✅ Role designer agent (RAG + LLM)
- ✅ Benefits analyst agent (static recommendations; model-backed analysis is pending)
- ✅ Report compiler
- ✅ LangGraph workflow
- ✅ API endpoint `/generate-role`


## Example Usage

```bash
curl -X POST "http://localhost:8000/generate-role?topic=AI%20Ethics%20Manager"
```

Response includes final report and role description.


## Phase 3: Evaluation & Observability

- ✅ Evaluation harness (consistency, benefit relevance, completeness)
- ✅ Prometheus metrics endpoint (`/metrics`)
- ✅ Request ID tracing and structured logging
- ✅ Unit and integration tests


## Metrics

Prometheus metrics are available at `http://localhost:8000/metrics`:

- `http_requests_total` - request count by method/endpoint/status
- `http_request_duration_seconds` - latency histogram
- `agent_calls_total` - agent invocations
- `rag_queries_total` - RAG retrieval queries

Agent/RAG counters are defined but their call-path instrumentation remains pending.

## Phase 4: Production Readiness (Current)

- CI validates lint, formatting, types, offline tests, and production image imports.
- Version tags trigger gated image publication to GitHub Container Registry.
- Cloud deployment, dashboards/alerts, caching, and demo frontend remain pending.
- See [PROGRESS.md](PROGRESS.md) and the [release checklist](docs/releasing.md#v100-checklist).

## Repository coding agent and skills

Use the [HR system engineer](.github/agents/hr-system-engineer.agent.md) Copilot agent
for project development. It is a coding assistant, not a new runtime HR agent.
Reusable project skills:

- [HR workflow development](.github/skills/hr-workflow-development/SKILL.md)
- [HR validation](.github/skills/hr-validation/SKILL.md)
- [HR release readiness](.github/skills/hr-release-readiness/SKILL.md)
- [HR Git workflow](.github/skills/hr-git-workflow/SKILL.md) (50-character subjects,
  70-character body lines)


## Running Tests

```bash
pytest tests/ -v
```


## License

Apache License 2.0
