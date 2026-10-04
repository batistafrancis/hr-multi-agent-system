# CI and release guide

## Reading this implementation

Start with these files, in order:

1. [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json) selects the
   development service, Python extensions, forwarded ports, and dependency setup.
   [compose.yml](../.devcontainer/compose.yml) supplies the Python workspace and Ollama sidecar.
2. [The coding agent](../.github/agents/hr-system-engineer.agent.md) defines project
   context and development boundaries. The four [skills](../.github/skills) describe
   development, validation, release, and Git procedures; they are instructions,
   not Python agents that run in the HR graph.
3. [pyproject.toml](../pyproject.toml) declares runtime/dev dependencies, package
   discovery, and lint/type settings. Prometheus is a runtime requirement; mypy is a dev tool.
4. [tests/conftest.py](../tests/conftest.py) replaces provider boundaries. Existing
   unit/graph tests explicitly request the fixture so live calls are not needed.
5. [CI](../.github/workflows/ci.yml) checks the code before building an image.
   [Release](../.github/workflows/release.yml) reuses CI before publishing a versioned image.
6. [Dockerfile](../Dockerfile) produces the non-root API runtime; it is separate
   from the development environment and has no model weights or seeded database.

Source-wide Black formatting and removal of unused imports/exception bindings establish
the existing lint checks' passing baseline. No runtime HR workflow behavior was redesigned
in this step. Known runtime and observability gaps remain in [PROGRESS.md](../PROGRESS.md).

## Development environment

Install Docker Desktop with its Linux engine enabled and the VS Code Dev Containers
extension. Open the repository and run **Dev Containers: Reopen in Container**.
The container includes Python 3.11, installs the project with development tools,
and starts an Ollama sidecar. No host Python installation is needed.

The dependency installation downloads PyTorch CPU wheels and the project dependencies.
It does not download model weights, seed the database, or contact model/search APIs.
The workspace is bind-mounted, so edits persist on the host.

Run the same checks as CI inside the container:

```bash
python -m ruff check src scripts tests
python -m black --check src scripts tests
python -m mypy src --ignore-missing-imports
python -m pytest tests -v
```

Tests replace search, RAG, and model providers with deterministic doubles. They verify
agent state updates and graph/report composition, not live provider availability.

The LangChain integration ranges stay on the compatible 0.2/0.1 release families
used by this project; LangGraph stays on 0.4. The unused DeepEval development dependency
was removed because the custom evaluator does not import it. These bounds are not a
fully reproducible lockfile; the existing requirements.lock is a historical environment
snapshot and is not used by CI. A curated lockfile remains follow-up work.

For a live local demo, pull a model explicitly:

```bash
curl --fail http://ollama:11434/api/pull -d '{"name":"qwen3.5:4b","stream":false}'
python scripts/seed_rag.py
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Seeding downloads the configured sentence-transformer model. Repeated seeding currently
adds documents again. Keep credentials only in an untracked `.env`, never in image layers
or committed configuration. Configure Tavily only for approved live searches; without a
key, the current search tool returns development mock data.

Open http://localhost:8000/docs for Swagger, /openapi.json for the schema,
/health for process health, and /metrics for Prometheus output.
`/health` does not verify model, search, or vector-store readiness.
Provider selection currently uses embedding settings; it is not a separate LLM switch.

## CI

The [CI workflow](../.github/workflows/ci.yml) runs on main/develop/feature branch
pushes and pull requests targeting main. The release workflow also calls it directly:

1. Install CPU PyTorch and the project with development dependencies on Python 3.11.
2. Run Ruff, Black, mypy, and the complete offline test suite.
3. Build the production image only after checks pass.
4. Import the FastAPI application inside the image to verify runtime dependencies.

Repository administrators should require the `checks` and `docker-build` jobs in branch
protection. Workflow files cannot configure those repository settings automatically.

The production Dockerfile runs as a non-root user and starts Uvicorn by default.
It does not include credentials, local vector data, test tools, or automatic seeding.
Supply configuration at runtime and mount writable persistence when deploying.

## Publishing an image

The [release workflow](../.github/workflows/release.yml) runs only for pushed
`v*.*.*` tags. It validates first, then publishes to
`ghcr.io/batistafrancis/hr-multi-agent-system` using `GITHUB_TOKEN`.
Enable GitHub Actions and permit package publication in repository/organization settings.
No personal access token is stored in the repository.

After review and explicit release approval:

1. Update the version in pyproject.toml and the FastAPI application together.
2. Run CI and review the release checklist.
3. Merge the reviewed branch, create a matching semantic-version tag, and push that tag.
4. Check the release Actions run and its image digest summary.
5. Deploy the immutable digest only after a separate deployment approval.

Stable versions receive full-version, major/minor, and commit-SHA tags.
No `latest` tag is published. Keep rollback records of the previous image digest
and its compatible configuration/data state. Roll back to that digest, not a moving tag.
Publishing an image does not create cloud infrastructure or a GitHub Release.

## v1.0.0 checklist

- [ ] CI checks and production image build pass for the release commit.
- [ ] Live role generation returns a nonempty report and role description.
- [ ] Provider errors, readiness, input validation, and HR-data handling are reviewed.
- [ ] Benefits analysis is implemented beyond the current static mock.
- [ ] Evaluation parsing and scoring are regression-tested.
- [ ] Agent/RAG metrics are wired into real call paths and dashboards/alerts are tested.
- [ ] A deployment platform is selected; persistence, rollout, and rollback are verified.
- [ ] Performance targets are measured and caching behavior is tested.
- [ ] Demo frontend and operational documentation are complete.
- [ ] Version, tag, and image digest match the approved release.
