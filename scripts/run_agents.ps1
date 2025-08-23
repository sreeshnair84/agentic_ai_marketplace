# PowerShell script to run Agents service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/2"
$env:GOOGLE_API_KEY = $env:GOOGLE_API_KEY
$env:OPENAI_API_KEY = $env:OPENAI_API_KEY
$env:ANTHROPIC_API_KEY = $env:ANTHROPIC_API_KEY
$env:TOOLS_URL = "http://localhost:8005"
$env:ORCHESTRATOR_URL = "http://localhost:8003"
$env:A2A_PROTOCOL_ENABLED = "true"
$env:MCP_SERVER_ENABLED = "true"
cd ../backend/services/agents
uvicorn app.main:app --host 0.0.0.0 --port 8002
