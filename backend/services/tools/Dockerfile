# Enhanced RAG Service Dockerfile - Working Version
FROM python:3.13-slim

# Metadata
LABEL maintainer="AI Platform Team"
LABEL description="Enhanced RAG Service with PostgreSQL support"
LABEL version="2.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=4

# Create application directory
WORKDIR /app

# Install essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
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

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy dependency files
COPY requirements.txt ./

# Install core Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install essential packages for RAG functionality
RUN pip install --no-cache-dir \
    numpy>=1.24.0 \
    scipy>=1.10.0 \
    pandas>=2.0.0 \
    sqlalchemy>=2.0.0 \
    asyncpg>=0.28.0 \
    psycopg2-binary>=2.9.0 \
    sentence-transformers>=2.2.0 \
    openai>=1.0.0 \
    langchain>=0.1.0 \
    langchain-community>=0.0.15 \
    faiss-cpu>=1.7.4 \
    pypdf>=3.0.0 \
    python-docx>=0.8.11 \
    aiofiles>=23.0.0 \
    uvicorn>=0.22.0

# Install optional RAG dependencies with error handling
RUN pip install --no-cache-dir \
    chromadb>=0.4.0 \
    nltk>=3.8.1 \
    tiktoken>=0.5.0 \
    python-multipart>=0.0.6 \
    || echo "Some optional dependencies could not be installed"

# Create directory structure
RUN mkdir -p \
    /app/models \
    /app/cache \
    /app/temp_uploads \
    /app/vector_db \
    /app/logs \
    /app/data \
    && chmod -R 755 /app/models /app/cache /app/temp_uploads /app/vector_db /app/logs /app/data

# Copy application code
COPY ./app /app/app

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV MODELS_PATH=/app/models \
    CACHE_PATH=/app/cache \
    TEMP_UPLOADS_PATH=/app/temp_uploads \
    VECTOR_DB_PATH=/app/vector_db \
    LOGS_PATH=/app/logs \
    DATA_PATH=/app/data \
    RAG_SERVICE_ENABLED=true \
    MAX_UPLOAD_SIZE_MB=500 \
    CHUNK_SIZE_DEFAULT=1000 \
    CHUNK_OVERLAP_DEFAULT=200 \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8005

# Simple health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "1", "--timeout-keep-alive", "120"]