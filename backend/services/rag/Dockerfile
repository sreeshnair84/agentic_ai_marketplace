# RAG Service Dockerfile - Clean and Working Version
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2 \
    VECLIB_MAXIMUM_THREADS=2 \
    NUMEXPR_NUM_THREADS=2 \
    FAISS_NO_AVX2=1

# Set work directory
WORKDIR /app

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    git \
    unzip \
    file \
    ca-certificates \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install database and SSL libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install document processing libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install image processing libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install scientific computing libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    liblapack-dev \
    libblas-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy dependency files
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install essential RAG packages
RUN pip install --no-cache-dir \
    sqlalchemy>=2.0.0 \
    asyncpg>=0.28.0 \
    psycopg2-binary>=2.9.0 \
    sentence-transformers>=2.2.0 \
    langchain>=0.1.0 \
    langchain-community>=0.0.15 \
    faiss-cpu>=1.7.4 \
    openai>=1.0.0 \
    tiktoken>=0.5.0 \
    pypdf>=3.0.0 \
    python-docx>=0.8.11 \
    aiofiles>=23.0.0 \
    uvicorn>=0.22.0 \
    fastapi>=0.104.0 \
    numpy>=1.24.0 \
    pandas>=2.0.0

# Install optional dependencies with error handling
RUN pip install --no-cache-dir \
    chromadb>=0.4.0 \
    nltk>=3.8.1 \
    python-multipart>=0.0.6 \
    || echo "Some optional dependencies could not be installed"

# Download and cache ML models and data
COPY download_nltk_data.py /tmp/download_nltk_data.py
RUN python /tmp/download_nltk_data.py

# Create necessary directories with proper permissions
RUN mkdir -p /app/models /app/cache /app/temp_uploads /app/vector_db /app/logs \
    && chmod 755 /app/models /app/cache /app/temp_uploads /app/vector_db /app/logs

# Copy application code
COPY ./app /app/app

# Create non-root user for security and set proper permissions
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app/models /app/cache /app/temp_uploads /app/vector_db /app/logs

# Switch to non-root user
USER appuser

# Set up environment variables for the RAG service
ENV MODELS_PATH=/app/models \
    CACHE_PATH=/app/cache \
    TEMP_UPLOADS_PATH=/app/temp_uploads \
    VECTOR_DB_PATH=/app/vector_db \
    LOGS_PATH=/app/logs \
    RAG_SERVICE_ENABLED=true \
    DOCLING_ENABLED=true \
    LANGGRAPH_ENABLED=true \
    MAX_UPLOAD_SIZE_MB=100 \
    CHUNK_SIZE_DEFAULT=1000 \
    CHUNK_OVERLAP_DEFAULT=200 \
    EMBEDDING_BATCH_SIZE=32 \
    SEARCH_RESULTS_LIMIT=50 \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8004

# Simple health check
HEALTHCHECK --interval=45s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "1", "--timeout-keep-alive", "65", "--access-log", "--log-level", "info"]
