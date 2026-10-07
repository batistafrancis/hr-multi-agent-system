# Technical onboarding: architecture and local setup

This guide explains what the project does, how its layers and runtime agents
fit together, and how to run it locally.

**Document type:** technical onboarding and architecture guide. This is not a
business roadmap, project progress tracker, or end-user HR manual.

The implementation and startup configuration were inspected for this guide.
Live models and end-to-end generation were not run as part of that inspection.
The startup instructions are code-grounded, but live operation still needs
verification. The implementation notes describe the code as inspected on
2026-10-06.

## 1. What the project does

The project is a backend API that drafts an HR role from a topic, using market
research and company-benefits information.

For example, submitting `AI Ethics Manager` is intended to produce a role
description and a Markdown report containing research and benefit
recommendations.

This is currently a prototype with a fixed, four-stage workflow, not an
autonomous HR department. Some stages use AI, some use ordinary Python, and
some still return mock data.

There is no custom frontend yet. Swagger at <http://localhost:8000/docs> is the
easiest interactive interface.

## 2. Project structure and layers

| Layer | Location | Responsibility |
|---|---|---|
| API | [src/api/](../src/api/) | Accepts HTTP requests, invokes the workflow, returns responses, and adds request IDs, logging, and HTTP metrics. |
| Orchestration and configuration | [src/core/](../src/core/) | Defines execution order, shared workflow state, and environment settings. |
| HR processing stages | [src/agents/](../src/agents/) | Researches the topic, drafts the role, recommends benefits, and compiles the report. |
| Tools and provider integrations | [src/tools/](../src/tools/) | Searches through Tavily and retrieves company information from Chroma. |
| Evaluation | [src/evaluation/](../src/evaluation/) | Contains quality-scoring methods, but is not connected to the request workflow. |
| Observability and utilities | [src/observability/](../src/observability/), [src/utils/](../src/utils/) | Defines metrics and configures console logging. |
| Data and setup | [data/](../data/), [scripts/](../scripts/) | Stores sample benefits and provides database seeding. |
| Tests | [tests/](../tests/) | Tests individual stages and graph composition with mocked providers. |
| Development environment | [.devcontainer/](../.devcontainer/) | Provides a Python 3.11 development container and a separate Ollama container. |
| Packaging and runtime | [pyproject.toml](../pyproject.toml), [Dockerfile](../Dockerfile) | Declares dependencies and builds the API runtime image. |
| Copilot and automation | [.github/](../.github/) | Contains coding-assistant instructions, reusable skills, and CI/release workflows. |

### Main technologies

- **FastAPI:** the HTTP interface.
- **Uvicorn:** the process serving that interface.
- **LangGraph:** runs the stages in the configured order and carries their
  shared state.
- **LangChain:** supplies prompt, model, and retrieval integrations.
- **Ollama:** runs models locally in a separate service.
- **Chroma:** stores document embeddings for similarity search.
- **Tavily:** an optional external web-search service.
- **Prometheus:** collects numerical metrics; it does not run the HR agents.

## 3. Runtime agent workflow

The workflow is defined in [graph.py](../src/core/graph.py):

```text
POST /generate-role?topic=...
             |
             v
       Researcher
             |
             v
       Role Designer ---> Chroma retrieval
             |             + language model
             v
     Benefits Analyst
             |
             v
      Report Compiler
             |
             v
        API response
```

### What each agent actually does

| Stage | Implementation |
|---|---|
| [ResearcherAgent](../src/agents/researcher.py) | Makes three searches: trends, competitor job descriptions, and salaries. Without a Tavily key, those searches return mock text. |
| [RoleDesignerAgent](../src/agents/role_designer.py) | Retrieves three relevant benefits documents, combines them with research and the topic, and asks a language model to draft a role. |
| [BenefitsAnalystAgent](../src/agents/benefits_analyst.py) | Returns hard-coded current benefits and recommendations. It does not analyze the generated role or use a model yet. |
| [ReportCompilerAgent](../src/agents/report_compiler.py) | Uses a Python string template to assemble a Markdown report. It makes no model call. |

Only the Role Designer currently uses a generative model in this pipeline.

### How stages communicate

The agents do not chat with one another. They read and update a shared
dictionary described by [AgentState](../src/core/state.py).

Think of it as a worksheet passed between stages:

```text
topic
research_notes
competitor_roles
compensation_data
drafted_role
role_description
current_benefits_used
recommended_benefits
final_report
error
```

Each stage returns the fields it produced. LangGraph merges those updates into
the state. Research-note and competitor-role lists have append-style merging.

The workflow is:

- Sequential, not parallel.
- Fixed, not dynamically planned.
- Without a supervisor, retry loop, human approval step, or configured
  persistent conversation memory.

There are unfinished connections: competitor roles and compensation are
collected but not explicitly used by the role-generation prompt or report
compiler.

### Runtime agents versus Copilot agents

The coding assistant configured under [.github/agents/](../.github/agents/)
helps developers work on the repository.

It is not a fifth HR agent and does not participate when someone calls the API.
The repository's Copilot skills are likewise development instructions, not
runtime components.

## 4. How RAG works

RAG means **retrieval-augmented generation**: find relevant company information
first, then include it in the model's prompt.

```text
Sample benefits JSON
        |
        v
Seeding script
        | creates numerical representations ("embeddings")
        v
Chroma database on disk

Role topic
        | embedded and compared with stored documents
        v
Three relevant benefits documents
        |
        v
Prompt + research + topic
        |
        v
Generated role
```

The source data is currently ten sample benefits in
[sample_benefits.json](../data/sample_benefits.json), not a live HR system.

[seed_rag.py](../scripts/seed_rag.py) loads those records into the database.
[RAGRetriever](../src/tools/rag_retriever.py) handles storage and retrieval.

This does not train the model. It supplies information at generation time.

Retrieval does not guarantee correctness: the model is asked to recommend
available benefits, but the output is not validated against the source
documents.

## 5. Step-by-step local startup

### Recommended route: VS Code Dev Container

This is the route documented by the project and avoids installing Python and
its dependencies directly on your host.

You need:

- Docker running; on Windows, Docker Desktop with Linux containers.
- VS Code.
- The Dev Containers extension.

If you are already working inside the project's Dev Container, skip Step 1.

Before rebuilding an existing container, follow the
[local-state migration guide](devcontainer-persistence.md). Repository files
are bind-mounted, while Copilot and VS Code remote data use dedicated Docker
volumes. SSH private keys should remain on the host.

### Step 1: Open the development container

Open the repository in VS Code, then run:

**Command Palette -> Dev Containers: Reopen in Container**

Wait for dependency installation to finish.

The configuration in
[devcontainer.json](../.devcontainer/devcontainer.json) installs the Python
dependencies. The development [compose.yml](../.devcontainer/compose.yml)
starts:

1. A Python development container.
2. An Ollama service.

It does not automatically download model weights, seed Chroma, or start the
API.

Run subsequent commands in the Dev Container terminal, from the repository
root.

### Step 2: Check Python and Ollama

```bash
python --version
curl --fail http://ollama:11434/api/tags
```

Expect Python 3.11 and an Ollama JSON response. An empty model list is fine
initially.

Inside the development container, the model server is
`http://ollama:11434`, not `http://localhost:11434`. Here, `localhost` means the
Python container itself.

Optionally check the offline tests:

```bash
python -m pytest tests -v
```

Those tests mock search, retrieval, and generation. Passing tests do not prove
the live providers work.

### Step 3: Download the configured model

```bash
curl --fail http://ollama:11434/api/pull \
  -d '{"name":"qwen3.5:4b","stream":false}'
```

This can take several minutes and requires internet access and disk space.
The model is stored in a Docker volume.

### Step 4: Configure the local demo

In the same terminal:

```bash
export OLLAMA_BASE_URL=http://ollama:11434
export OLLAMA_MODEL=qwen3.5:4b
export USE_OLLAMA_EMBEDDINGS=true
export CHROMA_PERSIST_DIR=./data/benefits_db_ollama

export OPENAI_API_KEY=
export TAVILY_API_KEY=
```

This selects local Ollama embeddings and generation, with mock web research.

Use `CHROMA_PERSIST_DIR` to configure persistence.
Environment variables override `.env` entries.
The default remains `./data/benefits_db`; this rename does not move or delete
existing data.

The separate database directory avoids mixing embeddings generated by
different models.

The current implementation uses the same Ollama model for both embedding and
generation. Successful seeding is therefore an important live compatibility
check, not just an optional setup task.

These exports apply only to the current terminal and processes started from it.
The configuration loader also supports an untracked `.env` file, but the
commands above are sufficient for this demo.

### Step 5: Seed and test retrieval

```bash
python -m scripts.seed_rag
```

This:

1. Reads the sample benefits.
2. Generates embeddings.
3. Saves documents in Chroma.
4. Runs three example retrieval queries.

Look for a seeding-complete message and retrieved document previews.

Repeated seeding adds duplicate documents, so do not run it before every API
startup.

If this step fails with a model or embedding error, resolve it before
continuing. A healthy API process alone will not prove retrieval works.

### Step 6: Start the API

Use the same terminal so the exported configuration remains active:

```bash
python -m uvicorn src.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

Keep this terminal running.

Open:

- [Swagger interface](http://localhost:8000/docs)
- [Health endpoint](http://localhost:8000/health)
- [Metrics endpoint](http://localhost:8000/metrics)

The Dev Container forwards port 8000 to your host.

### Step 7: Generate a role

In Swagger:

1. Expand **POST `/generate-role`**.
2. Select **Try it out**.
3. Enter `AI Ethics Manager` as the topic.
4. Select **Execute**.

Or, in a second Dev Container terminal:

```bash
curl --fail-with-body --get \
  --request POST \
  --data-urlencode "topic=AI Ethics Manager" \
  http://localhost:8000/generate-role
```

The topic is a query parameter, not a JSON request body.

Generation may be slow on CPU. Watch the server terminal for errors.

### Step 8: Stop the API

Press **Ctrl+C** in its terminal.

Stopping the API does not delete the seeded database or downloaded model.

## 6. Known limitations when interpreting the result

These are implementation gaps, not necessarily mistakes in your setup:

- **The API report field is wrong.** In [main.py](../src/api/main.py), the
  response reads `final_state`, while the graph produces `final_report`. You
  can therefore receive `"status": "success"` and `"report": null`.
- **JSON is requested, not enforced.** The Role Designer stores the model's
  raw response. `role_description` is not guaranteed to be valid JSON or a
  validated role object.
- **Benefits recommendations are static.** The final report's recommendations
  come from the Benefits Analyst's hard-coded list, not from parsed model
  output.
- **Research is mocked without Tavily.** Even live research currently includes
  a hard-coded `2025` trends query.
- **Health is process health only.** `/health` does not check Ollama, model
  availability, or Chroma.
- **Evaluation does not run automatically.** The evaluator is separate from
  the graph and has a known text-extraction bug.
- **Monitoring is partial.** HTTP metrics are wired; agent, RAG, and model
  metrics are mostly definitions without call-path instrumentation.
- **Logging is simpler than the documentation suggests.** The implementation
  currently uses standard Python console logging, not a full structured
  tracing setup.

For a first demo, use only sample, non-sensitive data. Adding a Tavily key sends
search queries to an external service. Switching to OpenAI can send prompt
context externally.

Start with the Dev Container route rather than treating the root
[docker-compose.yml](../docker-compose.yml) as a reliable one-command setup:
it defaults to the older sentence-transformer embedding path. The previous
persistence-variable spelling mismatch has been fixed.

Provider selection is also coupled: the Role Designer selects Ollama when
`USE_OLLAMA_EMBEDDINGS` is true or the embedding model name contains
`sentence-transformers`. Otherwise, it selects OpenAI. There is not yet a
separate, explicit generation-provider setting.

## 7. Best reading order

To understand the request from beginning to end:

1. [main.py](../src/api/main.py): What does the API accept and return?
2. [graph.py](../src/core/graph.py): What runs, and in what order?
3. [state.py](../src/core/state.py): What information passes between stages?
4. [role_designer.py](../src/agents/role_designer.py): Where does generation happen?
5. [rag_retriever.py](../src/tools/rag_retriever.py): Where does company context come from?
6. [settings.py](../src/core/settings.py): Which configuration controls it?
7. [test_graph.py](../tests/integration/test_graph.py): What behavior is currently tested?

The simplest mental model: an HTTP endpoint runs a fixed pipeline, shares a
worksheet between stages, retrieves sample company benefits, calls one
generative model, and assembles a report. The surrounding containers, tests,
metrics, and Copilot configuration support that pipeline; they are not
additional autonomous agents.

## Related documentation

- [README](../README.md): project overview and quick start.
- [Project progress](../PROGRESS.md): status and remaining work.
- [Development and release guide](releasing.md): validation, CI, and publishing.
