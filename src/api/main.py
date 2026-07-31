"""FastAPI entry point."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from src.core.graph import graph
from src.core.state import AgentState
from src.core.settings import settings
from src.utils.logging_conf import configure_logging
from src.api.middleware import RequestIDMiddleware, MetricsMiddleware, LoggingMiddleware
from src.observability.metrics import get_metrics

# Configure logging
configure_logging()

app = FastAPI(title="HR Multi-Agent System", version="0.1.0")

# Middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}

@app.get("/")
async def root():
    return {"message": "HR Multi-Agent System API", "status": "running"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

@app.post("/generate-role")
async def generate_role(topic: str):
    """Run multi-agent pipeline to create a new HR role."""
    initial_state: AgentState = {
        "topic": topic,
        "research_notes": [],
        "competitor_roles": [],
        "compensation_data": None,
        "drafted_role": None,
        "role_description": None,
        "current_benefits_used": [],
        "recommended_benefits": [],
        "final_report": None,
        "error": None
    }
    try:
        final_state = await graph.ainvoke(initial_state)
        return {
            "status": "success",
            "topic": topic,
            "report": final_state.get("final_state"),
            "role_description": final_state.get("role_description")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
