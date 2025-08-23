#!/bin/bash
# Bash script to run Tools service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/3"
export MCP_SERVER_REGISTRY_URL="http://localhost:9000"
export A2A_PROTOCOL_ENABLED=true
export HOST=0.0.0.0
export PORT=8005
cd ../backend/services/tools
uvicorn app.main:app --host 0.0.0.0 --port 8005
