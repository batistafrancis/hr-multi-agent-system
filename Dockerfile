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

# Copy project definition
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install -e . && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the application
COPY . .

# Create data directory for ChromaDB
RUN mkdir -p /app/data/benefits_db

# Set Python path
ENV PYTHONPATH=/app

# Run the seeding script during build (optional)
# CMD ["python", "scripts/seed_rag.py"]
