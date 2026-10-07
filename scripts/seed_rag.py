#!/usr/bin/env python
"""Seed the RAG database with sample benefits and HR documents."""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.rag_retriever import RAGRetriever
from src.utils.logging_conf import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


SAMPLE_BENEFITS_FILE = Path(__file__).parent.parent / "data" / "sample_benefits.json"


def load_sample_benefits() -> list[dict]:
    """Load sample benefits from JSON file."""
    if not SAMPLE_BENEFITS_FILE.exists():
        raise FileNotFoundError(f"Sample data file not found: {SAMPLE_BENEFITS_FILE}")

    with SAMPLE_BENEFITS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Sample data must be a JSON array")

    return data


def main():
    """Load sample benefits into RAG database."""
    logger.info("Starting RAG database seeding...")

    retriever = RAGRetriever()

    # Clear existing data (optional, comment to keep)
    # retriever.delete_all()

    # Prepare documents
    texts = []
    metadatas = []

    benefits = load_sample_benefits()
    logger.info(f"Loaded {len(benefits)} benefits from {SAMPLE_BENEFITS_FILE}")

    for benefit in benefits:
        texts.append(benefit["text"])
        metadatas.append(
            {
                "category": benefit["category"],
                "region": benefit["region"],
                "source": "sample_benefits",
            }
        )

    # Add to vector store
    retriever.add_texts(texts, metadatas)

    # Test retrieval
    test_queries = [
        "What retirement benefits do we offer?",
        "Tell me about parental leave policy",
        "What's the remote work stipend?",
    ]

    logger.info("\n--- Testing Retrieval ---")
    for query in test_queries:
        results = retriever.retrieve(query, k=2)
        logger.info(f"\nQuery: {query}")
        for i, doc in enumerate(results, 1):
            preview = doc.page_content[:100] + "..."
            logger.info(f"  {i}. {preview}")

    logger.info(f"\n✅ Seeding complete! Vector DB at: {retriever.persist_dir}")


if __name__ == "__main__":
    main()
