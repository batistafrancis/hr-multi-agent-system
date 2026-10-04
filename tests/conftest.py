"""Offline provider boundaries shared by agent and graph tests."""

from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.agents import researcher, role_designer


@pytest.fixture
def offline_providers(monkeypatch):
    search = AsyncMock(return_value=["Trend: AI ethics growing"])
    monkeypatch.setattr(researcher, "tavily_search", search)
    retriever = Mock()
    retriever.retrieve_context.return_value = "Health insurance; learning budget"
    monkeypatch.setattr(role_designer, "RAGRetriever", Mock(return_value=retriever))
    model = RunnableLambda(
        lambda prompt: AIMessage(
            content='{"title": "AI Ethics Manager", "summary": "A great role"}'
        )
    )
    monkeypatch.setattr("langchain_ollama.ChatOllama", Mock(return_value=model))
    monkeypatch.setattr("langchain_openai.ChatOpenAI", Mock(return_value=model))
    return search, retriever
