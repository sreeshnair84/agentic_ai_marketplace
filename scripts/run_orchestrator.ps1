# PowerShell script to run Orchestrator service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/1"
$env:GOOGLE_API_KEY = $env:GOOGLE_API_KEY
$env:AGENTS_URL = "http://localhost:8002"
$env:TOOLS_URL = "http://localhost:8005"
$env:RAG_URL = "http://localhost:8004"
$env:WORKFLOW_URL = "http://localhost:8007"
$env:A2A_PROTOCOL_ENABLED = "true"
$env:REMOTE_AGENTS = "http://localhost:8002,http://localhost:8004,http://localhost:8005"
$env:HOST = "0.0.0.0"
$env:PORT = "8003"
cd ../backend/services/orchestrator
uvicorn app.main:app --host 0.0.0.0 --port 8003
