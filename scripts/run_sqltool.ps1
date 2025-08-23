# PowerShell script to run SQLTool service locally
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
$env:REDIS_URL = "redis://localhost:6379/5"
$env:ALLOWED_DB_TYPES = "postgresql,mysql,sqlite,mssql"
$env:MAX_QUERY_EXECUTION_TIME = "30"
$env:HOST = "0.0.0.0"
$env:PORT = "8006"
cd ../backend/services/sqltool
uvicorn app.main:app --host 0.0.0.0 --port 8006
