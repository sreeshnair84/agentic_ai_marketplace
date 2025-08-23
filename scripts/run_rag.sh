#!/bin/bash
# Bash script to run RAG service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/4"
export VECTOR_STORE_TYPE=pgvector
export PGVECTOR_DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export A2A_PROTOCOL_ENABLED=true
export HOST=0.0.0.0
export PORT=8004
cd ../backend/services/rag
uvicorn app.main:app --host 0.0.0.0 --port 8004
