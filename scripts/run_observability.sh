#!/bin/bash
# Bash script to run Observability service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/7"
export JAEGER_ENDPOINT="http://localhost:14268/api/traces"
export PROMETHEUS_GATEWAY="http://localhost:9091"
export HOST=0.0.0.0
export PORT=8008
cd ../backend/services/observability
uvicorn app.main:app --host 0.0.0.0 --port 8008
