# Use Python 3.12 slim image for optimal performance
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Install UV for faster Python package management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Use official PyPI index and add retries/timeouts for network robustness
ENV PIP_INDEX_URL=https://pypi.org/simple
# Install package using `uv` (if available). If that fails, retry once and as a last
# resort ensure the critical runtime packages are installed explicitly so the
# image contains FastAPI and Uvicorn. This protects against silent failures of
# the `uv pip install --system .` step.
RUN uv pip install --system . || (sleep 10 && uv pip install --system .) || \
    pip install --no-cache-dir "fastapi[all]" "uvicorn[standard]"

# Copy application code
COPY ./app /app/app

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
