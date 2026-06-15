"""RAG retriever for company benefits and HR documents."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from src.core.settings import settings
from src.utils.logging_conf import get_logger

logger = get_logger(__name__)


class RAGRetriever:
    """Handles embedding storage and retrieval of HR documents."""

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.chrome_persist_dir
        self.embedding_function = self._get_embedding_function()
        self.vectorstore: Optional[Chroma] = None
        self._load_or_create() # Try to load existing DB


    def _get_embedding_function(self):
        """Return appropriate embedding model based on settings."""
        if settings.use_ollama_embeddings:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url
            )
        elif "sentence-transformers" in settings.embedding_model:
            # If use explicitly wants local sentence-transformers (free, no API key)
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                return HuggingFaceEmbeddings(
                    model_name=settings.embedding_model,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            except ImportError as e:
                # Fallback to community version
                from langchain_community.embeddings import HuggingFaceEmbeddings
                logger.warning("Falling back to OpenAI embeddings")
                return HuggingFaceEmbeddings(
                    model_name=settings.embedding_model,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
        else:
            # Use OpenAI embeddings
            return OpenAIEmbeddings(model=settings.embedding_model)

    def _load_or_create(self):
        """Load existing Chroma DB or create empty one."""
        persist_path = Path(self.persist_dir)

        if persist_path.exists() and any(persist_path.iterdir()):
            try:
                self.vectorstore = Chroma(
                    persist_directory=str(persist_path),
                    embedding_function=self.embedding_function
                )

                if not self.vectorstore:
                    raise ValueError("Vector store not initialized")

                count = self.vectorstore._collection.count()
                logger.info(f"Loaded existing Chroma DB from {self.persist_dir} ({count} documents)")
                return
            except Exception as e:
                logger.warning(f"Failed to load DB: {e}. Creating new.")

        # Create new
        self.vectorstore = Chroma(
            persist_directory=str(persist_path),
            embedding_function=self.embedding_function
        )
        logger.info(f"Created new Chroma DB at {self.persist_dir}")

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        if not documents:
            logger.warning("No documents provided to add")
            return

        if not self.vectorstore:
            raise ValueError("Vector store not initialized")

        self.vectorstore.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to RAG store")

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """Add raw texts to vector store with optional metadata."""
        documents = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(texts, metadatas or [{}] * len(texts))
        ]
        self.add_documents(documents)


    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve top-k relevant documents for a query."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")

        docs = self.vectorstore.similarity_search(query, k=k)
        logger.debug(f"Retrieved {len(docs)} docs for query: {query[:50]}...")
        return docs

    def retrieve_context(self, query: str, k: int = 4) -> str:
        """Retrieve and combine documents into a single context string."""
        docs = self.retrieve(query, k)
        return "\n\n---\n\n".join([doc.page_content for doc in docs])

    def delete_all(self):
        """Delete all documents from the store"""
        if self.vectorstore:
            # Chroma doesn't have bulk delete: recreate
            self.vectorstore.delete_collection()
            self._load_or_create()
            logger.info("Deleted all documents from RAG store")
