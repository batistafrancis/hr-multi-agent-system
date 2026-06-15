FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence-transformers and chromadb
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for better caching)
COPY pyproject.toml ./
COPY .env.example .env

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    langchain \
    langchain-community \
    langchain-ollama \
    langchain-openai \
    langchain-chroma \
    langgraph \
    tavily-python \
    chromadb \
    sentence-transformers \
    pydantic \
    pydantic-settings \
    python-dotenv \
    structlog \
    fastapi \
    uvicorn \
    httpx && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the application
COPY . .

# Create data directory for ChromaDB
RUN mkdir -p /app/data/benefits_db

# Set Python path
ENV PYTHONPATH=/app

# Run the seeding script during build (optional)
# CMD ["python", "scripts/seed_rag.py"]
