"""Offline regression tests for Chroma persistence configuration."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.settings import Settings
from src.tools import rag_retriever


@pytest.fixture(autouse=True)
def clear_persistence_environment(monkeypatch):
    for name in ("CHROMA_PERSIST_DIR", "chroma_persist_dir"):
        monkeypatch.delenv(name, raising=False)


def test_default_persistence_directory():
    assert Settings(_env_file=None).chroma_persist_dir == "./data/benefits_db"


@pytest.mark.parametrize("name", ["CHROMA_PERSIST_DIR", "chroma_persist_dir"])
def test_canonical_environment_variable(monkeypatch, name):
    monkeypatch.setenv(name, "/tmp/canonical-benefits")
    assert Settings(_env_file=None).chroma_persist_dir == "/tmp/canonical-benefits"


def test_dotenv_configuration(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CHROMA_PERSIST_DIR=./configured-benefits\n", encoding="utf-8")
    config = Settings(_env_file=env_file)
    assert config.chroma_persist_dir == "./configured-benefits"


def test_environment_overrides_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("CHROMA_PERSIST_DIR=./dotenv-benefits\n", encoding="utf-8")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "./environment-benefits")
    assert Settings(_env_file=env_file).chroma_persist_dir == "./environment-benefits"


def test_canonical_constructor_setting():
    config = Settings(_env_file=None, chroma_persist_dir="./constructor-benefits")
    assert config.chroma_persist_dir == "./constructor-benefits"


@pytest.mark.parametrize("explicit_path", [None, "./explicit-benefits"])
def test_retriever_uses_configured_directory(monkeypatch, explicit_path):
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "./configured-benefits")
    config = Settings(_env_file=None)
    with (
        patch.object(rag_retriever, "settings", config),
        patch.object(rag_retriever.RAGRetriever, "_get_embedding_function"),
        patch.object(rag_retriever, "Chroma") as chroma,
    ):
        retriever = rag_retriever.RAGRetriever(persist_dir=explicit_path)

    expected = explicit_path or "./configured-benefits"
    assert retriever.persist_dir == expected
    assert chroma.call_args.kwargs["persist_directory"] == str(Path(expected))
