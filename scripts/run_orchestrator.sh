#!/bin/bash
# Bash script to run Orchestrator service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/1"
export GOOGLE_API_KEY="$GOOGLE_API_KEY"
export AGENTS_URL="http://localhost:8002"
export TOOLS_URL="http://localhost:8005"
export RAG_URL="http://localhost:8004"
export WORKFLOW_URL="http://localhost:8007"
export A2A_PROTOCOL_ENABLED=true
export REMOTE_AGENTS="http://localhost:8002,http://localhost:8004,http://localhost:8005"
export HOST=0.0.0.0
export PORT=8003
cd ../backend/services/orchestrator
uvicorn app.main:app --host 0.0.0.0 --port 8003
