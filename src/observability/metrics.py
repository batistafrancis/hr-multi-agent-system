"""Prometheus metrics for observability."""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY

# HTTP metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

# Agent metrics
AGENT_CALLS = Counter('agent_calls_total', 'Agent invocations', ['agent_name'])
AGENT_ERRORS = Counter('agent_errors_total', 'Agent errors', ['agent_name', 'error_type'])

# RAG metrics
RAG_QUERIES = Counter('rag_queries_total', 'RAG retrieval queries')
RAG_LATENCY = Histogram('rag_latency_seconds', 'RAG retrieval latency')

# LLM metrics
LLM_TOKENS = Counter('llm_tokens_total', 'LLM tokens used', ['model', 'type'])  # token type: prompt or completion

# System metrics
ACTIVE_REQUESTS = Gauge('active_requests', 'Number of active HTTP requests')


def track_agent_call(agent_name: str):
    AGENT_CALLS.labels(agent_name=agent_name).inc()

def track_agent_error(agent_name: str, error_type: str):
    AGENT_ERRORS.labels(agent_name=agent_name, error_type=error_type).inc()

def track_rag_query():
    RAG_QUERIES.inc()

def track_rag_latency(seconds: float):
    RAG_LATENCY.observe(seconds)

def track_llm_tokens(model: str, token_type: str, count: int):
    LLM_TOKENS.labels(model=model, type=token_type).inc(count)

def get_metrics():
    return generate_latest(REGISTRY)
