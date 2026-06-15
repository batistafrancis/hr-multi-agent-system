"""Role Designer - generates role description using RAG and LLM."""

import importlib

from src.agents.base import BaseAgent
from src.tools.rag_retriever import RAGRetriever
from langchain_core.prompts import ChatPromptTemplate
from src.core.settings import settings


class RoleDesignerAgent(BaseAgent):
    async def run(self, state: dict) -> dict:
        self.log_start(state)
        topic = state["topic"]
        research = "\n".join(state.get("research_notes", []))

        # Retrieve benefits context
        retriever = RAGRetriever()
        benefits_context = retriever.retrieve_context(topic, k=3)

        # LLM generation
        if settings.use_ollama_embeddings or "sentence-transformers" in settings.embedding_model:
            ChatOllama = getattr(importlib.import_module("langchain_ollama"), "ChatOllama")
            llm = ChatOllama(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
                temperature=0.7
            )
        else:
            ChatOpenAI = getattr(importlib.import_module("langchain_openai"), "ChatOpenAI")
            llm = ChatOpenAI(model=settings.llm_model, temperature=0.7)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert HR role designer. Output a JSON object."),
            ("user", f"""
Topic: {topic}
Research: {research}
Benefits available: {benefits_context}

Generate a job role with:
- title
- summary (2-3 sentences)
- key_responsibilities (3-5 bullet points)
- required_skills (3-5)
- recommended_benefits (2-4 from the list above)

Return valid JSON.
""")
        ])
        chain = prompt | llm
        response = await chain.ainvoke({})

        # Simple extraction (in production, use structured output)
        return {
            "drafted_role": {"raw": response.content},
            "role_description": response.content
        }
