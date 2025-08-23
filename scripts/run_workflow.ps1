# PowerShell script to run Workflow Engine service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/6"
$env:ORCHESTRATOR_URL = "http://localhost:8003"
$env:AGENTS_URL = "http://localhost:8002"
$env:TOOLS_URL = "http://localhost:8005"
$env:HOST = "0.0.0.0"
$env:PORT = "8007"
cd ../backend/services/workflow-engine
uvicorn app.main:app --host 0.0.0.0 --port 8007
