# PowerShell script to run Observability service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/7"
$env:JAEGER_ENDPOINT = "http://localhost:14268/api/traces"
$env:PROMETHEUS_GATEWAY = "http://localhost:9091"
$env:HOST = "0.0.0.0"
$env:PORT = "8008"
cd ../backend/services/observability
uvicorn app.main:app --host 0.0.0.0 --port 8008
