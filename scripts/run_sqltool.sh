#!/bin/bash
# Bash script to run SQLTool service locally
export ENVIRONMENT=development
export DATABASE_URL="postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
export REDIS_URL="redis://localhost:6379/5"
export ALLOWED_DB_TYPES="postgresql,mysql,sqlite,mssql"
export MAX_QUERY_EXECUTION_TIME=30
export HOST=0.0.0.0
export PORT=8006
cd ../backend/services/sqltool
uvicorn app.main:app --host 0.0.0.0 --port 8006
