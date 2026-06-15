"""Web search tool using Tavily API."""

from typing import List, Optional
from src.core.settings import settings

# Lazy import to avoid missing dependency
_tavily_client = None

def get_tavily_client():
    global _tavily_client
    if not _tavily_client and settings.tavily_api_key:
        try:
            from tavily import TavilyClient
            _tavily_client = TavilyClient(api_key=settings.tavily_api_key)
        except ImportError:
            pass
    return _tavily_client

async def tavily_search(query: str, max_results: int = 3) -> List[str]:
    """Perform web search using Tavily, return content snippets."""
    client = get_tavily_client()
    if not client:
        # Fallback mock for development
        return [f"[Mock] Search result for: {query} (no Tavily API key)"]
    try:
        response = client.search(query, max_results=max_results)
        return [result['content'] for result in response.get('results', {})]
    except Exception as e:
        return [f"Search error: {str(e)}"]
