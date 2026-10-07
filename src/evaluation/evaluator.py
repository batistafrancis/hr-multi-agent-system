"""Evaluation harness for generated roles and benefit recommendations."""

import re
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from sentence_transformers import SentenceTransformer

from src.core.settings import settings
from src.utils.logging_conf import get_logger

logger = get_logger(__name__)


class Evaluator:
    """Evaluates generated roles for consistency, benefit relevance, and completeness."""

    def __init__(self):
        self.llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.0,  # deterministic for evaluation
        )
        # Load same embedding model used in RAG
        self.embedder = SentenceTransformer(settings.embedding_model)

    async def consistency_score(self, generated_role: str, research_context: str) -> float:
        """
        Score (0-1) how well the generated role aligns with the research context.
        Uses LLM-as-judge.
        """
        prompt = f""""
Rate the consistency between the generated role and the research context on a scale of o to 1.

Return only a single number between 0 and 1.

Research context:
{research_context[:1500]}

Generated Role:
{generated_role[:1500]}

Score (0-1):
"""
        response: BaseMessage = await self.llm.ainvoke(prompt)
        context = self._extract_text(response.content)
        return self._parse_float(context, default=0.5)

    async def benefit_relevance(
        self, recommended_benefits: List[str], available_benefits: List[str]
    ) -> float:
        """
        Compute average cosine similarity between recommended benefits and available benefits.
        Higher score means the recommendations are well-aligned with the company's offerings.
        """
        if not recommended_benefits or not available_benefits:
            logger.warning("Empty benefit lists, returning 0.0")
            return 0.0

        # Encode all texts
        all_texts = recommended_benefits + available_benefits
        embeddings = self.embedder.encode(all_texts, normalize_embeddings=True)
        rec_emb = embeddings[: len(recommended_benefits)]
        avail_emb = embeddings[len(recommended_benefits) :]

        # For each recommended benefit, find max cosine similarity with available benefits
        import numpy as np

        similarities = []
        for r_emb in rec_emb:
            # dot product because embeddings are normalized
            sims = np.dot(avail_emb, r_emb)  # shape (num_available,)
            similarities.append(np.max(sims))  # best match

        return float(np.mean(similarities)) if similarities else 0.0

    async def completeness_score(self, generated_role: str) -> float:
        """
        Heuristic score (0-1) based on presence of key sections.
        Checks for: title, summary, responsibilities, skills, benefits.
        """
        sections = [r"title", r"summary", r"responsibilities", r"skills", r"benefits"]
        text_lower = generated_role.lower()
        present = sum(1 for sec in sections if re.search(sec, text_lower))
        return present / len(sections)

    def _extract_text(self, content: str | list) -> str:
        """Extract string from AIMessage content, handling list/dict cases."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            # Usually list of dics with 'text' key or just strings
            texts = []
            for item in content:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    texts.append(item["item"])
            return " ".join(texts)
        return str(content)

    def _parse_float(self, text: str, default: float) -> float:
        """Extract first float from string, return default if not found."""
        match = re.search(r"(\d+\.?\d+)", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return default
