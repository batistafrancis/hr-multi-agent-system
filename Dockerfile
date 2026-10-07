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
COPY src ./src

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir .

COPY scripts ./scripts
COPY data/sample_benefits.json ./data/sample_benefits.json

# Create data directory for ChromaDB
RUN useradd --create-home app && \
    mkdir -p /app/data/benefits_db && \
    chown -R app:app /app

# Set Python path
ENV PYTHONPATH=/app

USER app
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
