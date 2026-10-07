---
name: hr-validation
description: Use when testing or validating changes to the HR system in the Python Dev Container.
---

# HR validation

Open the repository with **Dev Containers: Reopen in Container**. Python 3.11 and
Ollama are configured by .devcontainer; project dependencies install on container creation.

Run from the workspace root inside the container:

```bash
python -m ruff check src scripts tests
python -m black --check src scripts tests
python -m mypy src --ignore-missing-imports
python -m pytest tests -v
```

For a focused change, run its test first, then the full offline suite before publishing.
Unit and graph integration tests must mock external provider boundaries.
Do not silently skip failing tests or weaken assertions to obtain a green result.

Live validation is separate and requires approval for credentials, downloads, and external calls:
pull the Ollama model, seed RAG, start Uvicorn, then check /health, /metrics, /docs,
and a complete /generate-role response. Confirm the report is nonempty, not merely HTTP 200.
Report exactly which checks passed and which remain unverified.
