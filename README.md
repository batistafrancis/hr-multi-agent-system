# HR Multi-Agent System

Production-ready multi-agent system for HR innovation:  
Market research, role design, benefits analysis, and reporting.

Author: [Francis Batista](https://github.com/francisrod01)


## Phase 1: Foundation & RAG

✅ RAG pipeline for company benefits and HR documents
✅ Vector search with ChromaDB
✅ Structured logging with structlog
✅ Environment-based configuration


## Quick Start

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
context = retriever.retriever_context("What retirement benefits do we offer?")
print(context)
```

## Project Structure

- `src/agents/` - Agent implementations
- `src/tools/` - RAG, search, HRIS tools
- `src/core/` - Settings, state, graph
- `scripts/` - Seeding and utility scripts


## Phase 2: Multi-Agent Orchestration (Current)

✅ Researcher agent (web search)
✅ Role designer agent (RAG + LLM)
✅ Benefits analyst agent
✅ Report compiler
✅ LangGraph workflow
✅ API endpoint `/generate-role`


## Example Usage

```bash
curl -X POST "http://localhost:8000/generate-role?topic=AI%20Ethics%20Manager"
```

Response includes final report and role description.


## License

Apache License 2.0
