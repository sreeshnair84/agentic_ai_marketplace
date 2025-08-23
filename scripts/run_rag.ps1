# PowerShell script to run RAG service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/4"
$env:VECTOR_STORE_TYPE = "pgvector"
$env:PGVECTOR_DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:A2A_PROTOCOL_ENABLED = "true"
$env:HOST = "0.0.0.0"
$env:PORT = "8004"
cd ../backend/services/rag
uvicorn app.main:app --host 0.0.0.0 --port 8004
