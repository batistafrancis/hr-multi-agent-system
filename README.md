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

### 1. Open the Dev Container on Windows

1. Start Docker Desktop with its Linux engine enabled.
2. Open `C:\projects-dev\hr-multi-agent-system` in VS Code.
3. Install the **Dev Containers** extension if needed.
4. Press **Ctrl+Shift+P** and select **Dev Containers: Reopen in Container**.
5. Wait for dependency installation to finish, then open a new VS Code terminal.

The terminal runs inside Linux with Python 3.11; no Windows Python installation
is required. [devcontainer.json](.devcontainer/devcontainer.json) configures the
workspace and [compose.yml](.devcontainer/compose.yml) starts an Ollama sidecar.
Run all commands below in the Dev Container terminal, not Windows PowerShell.

Before rebuilding an existing container, follow the
[local-state migration guide](docs/devcontainer-persistence.md) to preserve
Copilot/VS Code data and configure host SSH-agent forwarding.

### 2. Verify the environment

```bash
python --version
python -m pytest tests -v
curl --fail http://ollama:11434/api/tags
```

Expect Python 3.11, passing offline tests, and an Ollama JSON response.
An empty model list is normal before the first download. Tests mock providers;
they do not prove live model or RAG availability.

### 3. Download the local model

```bash
curl --fail http://ollama:11434/api/pull \
  -d '{"name":"qwen3.5:4b","stream":false}'
```

This downloads model weights and can take several minutes. Ollama model data
persists in a Docker volume.

### 4. Configure local providers and seed sample data

```bash
export OLLAMA_BASE_URL=http://ollama:11434
export OLLAMA_MODEL=qwen3.5:4b
export USE_OLLAMA_EMBEDDINGS=true
export CHROMA_PERSIST_DIR=./data/benefits_db_ollama

python -m scripts.seed_rag
```

This uses Ollama for generation and embeddings, avoiding the older
sentence-transformer dependency stack. The separate database directory avoids
mixing embedding models. `CHROMA_PERSIST_DIR` configures database persistence.
Environment variables override `.env` entries.
The default remains `./data/benefits_db`; existing data is not moved or deleted.
Repeated seeding currently adds duplicate documents.

No OpenAI or Tavily key is needed for this local demo. Without a Tavily key,
research returns development mock results. Use only sample data for initial
validation; external providers require approval before receiving HR data.
This live configuration still needs end-to-end verification.

### 5. Start the API

Run in the same terminal so the exported settings remain active:

```bash
python -m uvicorn src.api.main:app \
  --host 0.0.0.0 --port 8000 --reload
```

Keep the terminal running. VS Code forwards port 8000; open these URLs on Windows:

- [Swagger API interface](http://localhost:8000/docs)
- [Health endpoint](http://localhost:8000/health)
- [Prometheus metrics](http://localhost:8000/metrics)

In Swagger, execute `POST /generate-role` with a topic such as
`AI Ethics Manager`. Alternatively, use the curl example below in a second
Dev Container terminal. Generation can be slow on CPU. Press **Ctrl+C** in the
server terminal to stop the API.

Known limitation: the API reads the wrong report field, so `report` can be
`null` even when the graph produces a report. `/health` checks process health,
not model, search, or vector-store readiness.

See the [development and release guide](docs/releasing.md) for additional
validation commands, implementation reading notes, and image publishing.


## Test Retrieval

```python
from src.tools.rag_retriever import RAGRetriever

retriever = RAGRetriever()
context = retriever.retrieve_context("What retirement benefits do we offer?")
print(context)
```

## Project Structure

- [Technical onboarding: architecture and local setup](docs/architecture-and-local-setup.md)
  explains the layers, runtime agents, RAG flow, local startup, and known limitations.

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

Response includes a role description. The final report field currently needs
the correction described in the local startup notes above.


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

## Recommended Next Steps

1. Review the readiness implementation and verify live local seeding and generation.
2. Fix the API report-field mismatch, provider-error handling, and evaluation
   extraction; add regression tests.
3. Wire agent/RAG counters into actual calls and verify request tracing.
4. Replace static benefits recommendations with grounded analysis.
5. Add Grafana dashboards and alerting, then measure performance before caching.
6. Choose a deployment platform, verify persistence and rollback, and add a demo UI.

Prioritize runtime correctness and completing Phase 3 observability before
deployment. Follow the [progress checklist](PROGRESS.md) for remaining work.
Use the [six-phase implementation strategy](docs/implementation-strategy.md)
for the detailed code backlog, dependencies, and acceptance criteria.

For understanding the code, start with the
[implementation reading guide](docs/releasing.md#reading-this-implementation),
then the [graph](src/core/graph.py), [role designer](src/agents/role_designer.py),
and [API](src/api/main.py).

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
