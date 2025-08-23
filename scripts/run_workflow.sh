#!/bin/bash
# Bash script to run Workflow Engine service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/6"
export ORCHESTRATOR_URL="http://localhost:8003"
export AGENTS_URL="http://localhost:8002"
export TOOLS_URL="http://localhost:8005"
export HOST=0.0.0.0
export PORT=8007
cd ../backend/services/workflow-engine
uvicorn app.main:app --host 0.0.0.0 --port 8007
