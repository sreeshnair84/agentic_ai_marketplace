# PowerShell script to run Tools service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/3"
$env:MCP_SERVER_REGISTRY_URL = "http://localhost:9000"
$env:A2A_PROTOCOL_ENABLED = "true"
$env:HOST = "0.0.0.0"
$env:PORT = "8005"
cd ../backend/services/tools
uvicorn app.main:app --host 0.0.0.0 --port 8005
