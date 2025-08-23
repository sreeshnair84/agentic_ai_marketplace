#!/bin/bash
# Bash script to run Agents service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/2"
export GOOGLE_API_KEY="$GOOGLE_API_KEY"
export OPENAI_API_KEY="$OPENAI_API_KEY"
export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
export TOOLS_URL="http://localhost:8005"
export ORCHESTRATOR_URL="http://localhost:8003"
export A2A_PROTOCOL_ENABLED=true
export MCP_SERVER_ENABLED=true
cd ../backend/services/agents
uvicorn app.main:app --host 0.0.0.0 --port 8002
