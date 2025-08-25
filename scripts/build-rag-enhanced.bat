@echo off
REM Enhanced RAG System Build and Deploy Script for Windows
REM Builds and deploys the complete RAG system with all dependencies

setlocal enabledelayedexpansion

REM Set color codes
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Script configuration
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set BUILD_DATE=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%T%time:~0,2%:%time:~3,2%:%time:~6,2%Z
set BUILD_VERSION=v2.0.0
if defined BUILD_COMMIT (
    set BUILD_COMMIT=%BUILD_COMMIT%
) else (
    for /f %%i in ('git rev-parse --short HEAD 2^>nul') do set BUILD_COMMIT=%%i
    if not defined BUILD_COMMIT set BUILD_COMMIT=unknown
)

echo %BLUE%🚀 Enhanced RAG System Build Script%NC%
echo %BLUE%====================================%NC%
echo Build Date: %BUILD_DATE%
echo Version: %BUILD_VERSION%
echo Commit: %BUILD_COMMIT%
echo Project Root: %PROJECT_ROOT%
echo.

REM Function to check dependencies
call :check_dependencies
if errorlevel 1 exit /b 1

REM Function to create directories
call :create_directories

REM Function to create environment file
call :create_env_file

REM Function to create monitoring config
call :create_monitoring_config

REM Function to validate compose file
call :validate_compose
if errorlevel 1 exit /b 1

REM Parse command line arguments
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=build

if "%COMMAND%"=="build" (
    call :build_images
) else if "%COMMAND%"=="start" (
    call :start_services
    call :show_status
    call :health_check
) else if "%COMMAND%"=="stop" (
    call :stop_services
) else if "%COMMAND%"=="restart" (
    call :restart_services
) else if "%COMMAND%"=="status" (
    call :show_status
) else if "%COMMAND%"=="health" (
    call :health_check
) else if "%COMMAND%"=="logs" (
    call :show_logs
) else if "%COMMAND%"=="clean" (
    call :clean_services
) else if "%COMMAND%"=="help" (
    call :show_usage
) else (
    echo %RED%Unknown command: %COMMAND%%NC%
    call :show_usage
    exit /b 1
)

exit /b 0

:check_dependencies
echo %BLUE%Checking dependencies...%NC%

docker --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Docker is not installed or not in PATH%NC%
    echo Please install Docker Desktop and try again.
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Docker Compose is not installed or not in PATH%NC%
    echo Please install Docker Compose and try again.
    exit /b 1
)

echo %GREEN%✓ All dependencies are installed%NC%
goto :eof

:create_directories
echo %BLUE%Creating necessary directories...%NC%

set DIRS=data\models data\cache data\vector_db data\logs data\uploads monitoring\prometheus monitoring\grafana\dashboards monitoring\grafana\datasources

for %%d in (%DIRS%) do (
    if not exist "%PROJECT_ROOT%\%%d" (
        mkdir "%PROJECT_ROOT%\%%d"
        echo %GREEN%✓ Created directory: %%d%NC%
    )
)
goto :eof

:create_env_file
set ENV_FILE=%PROJECT_ROOT%\.env.rag

if not exist "%ENV_FILE%" (
    echo %BLUE%Creating environment configuration file...%NC%
    
    (
        echo # Enhanced RAG System Environment Configuration
        echo # Generated on %BUILD_DATE%
        echo.
        echo # Build information
        echo BUILD_DATE=%BUILD_DATE%
        echo BUILD_VERSION=%BUILD_VERSION%
        echo BUILD_COMMIT=%BUILD_COMMIT%
        echo.
        echo # Database Configuration
        echo POSTGRES_DB=agenticai
        echo POSTGRES_USER=postgres
        echo POSTGRES_PASSWORD=postgres_secure_password_change_me
        echo POSTGRES_HOST=localhost
        echo POSTGRES_PORT=5432
        echo.
        echo # Redis Configuration
        echo REDIS_PASSWORD=redis_secure_password_change_me
        echo.
        echo # API Keys ^(set these to your actual keys^)
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
        echo HUGGINGFACE_API_KEY=your_huggingface_api_key_here
        echo.
        echo # Security
        echo JWT_SECRET_KEY=your_jwt_secret_key_here_change_me
        echo ENCRYPTION_KEY=your_encryption_key_here_change_me
        echo.
        echo # MinIO Configuration
        echo MINIO_ROOT_USER=minioadmin
        echo MINIO_ROOT_PASSWORD=minioadmin_change_me
        echo.
        echo # Grafana Configuration
        echo GRAFANA_PASSWORD=admin_change_me
        echo.
        echo # RAG Service Configuration
        echo RAG_SERVICE_PORT=8005
        echo CHROMADB_PORT=8000
        echo ELASTICSEARCH_PORT=9200
        echo.
        echo # Performance Settings
        echo MAX_WORKERS=4
        echo MEMORY_LIMIT=4G
        echo CPU_LIMIT=2.0
        echo.
        echo # Feature Toggles
        echo ENABLE_DOCLING=true
        echo ENABLE_LANGGRAPH=true
        echo ENABLE_MCP=true
        echo ENABLE_MONITORING=true
    ) > "%ENV_FILE%"
    
    echo %GREEN%✓ Created environment file: .env.rag%NC%
    echo %YELLOW%⚠ Please edit .env.rag and set your actual API keys and passwords!%NC%
) else (
    echo %GREEN%✓ Environment file already exists%NC%
)
goto :eof

:create_monitoring_config
echo %BLUE%Creating monitoring configuration...%NC%

set PROMETHEUS_CONFIG=%PROJECT_ROOT%\monitoring\prometheus.yml

if not exist "%PROMETHEUS_CONFIG%" (
    (
        echo global:
        echo   scrape_interval: 15s
        echo   evaluation_interval: 15s
        echo.
        echo rule_files: []
        echo.
        echo scrape_configs:
        echo   - job_name: 'rag-enhanced'
        echo     static_configs:
        echo       - targets: ['rag-enhanced:8005']
        echo     metrics_path: '/metrics'
        echo     scrape_interval: 30s
        echo.
        echo   - job_name: 'chromadb'
        echo     static_configs:
        echo       - targets: ['chromadb:8000']
        echo     metrics_path: '/api/v1/metrics'
        echo     scrape_interval: 30s
    ) > "%PROMETHEUS_CONFIG%"
    
    echo %GREEN%✓ Created Prometheus configuration%NC%
)
goto :eof

:validate_compose
echo %BLUE%Validating Docker Compose configuration...%NC%

cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml config >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Docker Compose configuration is invalid%NC%
    docker-compose -f docker-compose.rag-enhanced.yml config
    exit /b 1
)

echo %GREEN%✓ Docker Compose configuration is valid%NC%
goto :eof

:build_images
echo %BLUE%Building Docker images...%NC%

cd /d "%PROJECT_ROOT%"

echo %YELLOW%Building Enhanced RAG Service...%NC%
docker build --build-arg BUILD_DATE="%BUILD_DATE%" --build-arg BUILD_VERSION="%BUILD_VERSION%" --build-arg BUILD_COMMIT="%BUILD_COMMIT%" -f backend\services\tools\Dockerfile.rag-enhanced -t agenticai/rag-enhanced:%BUILD_VERSION% -t agenticai/rag-enhanced:latest backend\services\tools\

if errorlevel 1 (
    echo %RED%✗ Failed to build Enhanced RAG Service image%NC%
    exit /b 1
)

echo %GREEN%✓ Enhanced RAG Service image built%NC%
goto :eof

:start_services
echo %BLUE%Starting Enhanced RAG System...%NC%

cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml up -d

echo %GREEN%✓ Services are starting up...%NC%

REM Wait for services to be ready
echo %YELLOW%Waiting for services to be ready...%NC%

set /a attempt=1
set /a max_attempts=30

:wait_loop
if %attempt% gtr %max_attempts% goto :wait_timeout

curl -f http://localhost:8005/health >nul 2>&1
if not errorlevel 1 goto :wait_success

echo|set /p=.
timeout /t 2 /nobreak >nul
set /a attempt+=1
goto :wait_loop

:wait_success
echo.
echo %GREEN%✓ Enhanced RAG Service is ready!%NC%
goto :eof

:wait_timeout
echo.
echo %YELLOW%⚠ Service health check timed out. Check logs with: docker-compose -f docker-compose.rag-enhanced.yml logs%NC%
goto :eof

:stop_services
cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml down
echo %GREEN%✓ Services stopped%NC%
goto :eof

:restart_services
cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml down
docker-compose -f docker-compose.rag-enhanced.yml up -d
echo %GREEN%✓ Services restarted%NC%
goto :eof

:show_status
echo %BLUE%Service Status:%NC%
echo.
cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml ps
echo.
echo %BLUE%Service URLs:%NC%
echo • Enhanced RAG API: http://localhost:8005
echo • ChromaDB: http://localhost:8000
echo • PostgreSQL: localhost:5432
echo • Redis: localhost:6379
echo • Elasticsearch: http://localhost:9200
echo • MinIO: http://localhost:9000 ^(Console: http://localhost:9001^)
echo • Prometheus: http://localhost:9090
echo • Grafana: http://localhost:3000
echo.
echo %BLUE%API Documentation:%NC%
echo • RAG API Docs: http://localhost:8005/docs
echo • RAG API Redoc: http://localhost:8005/redoc
goto :eof

:health_check
echo %BLUE%Running health checks...%NC%

curl -f http://localhost:8005/health >nul 2>&1
if not errorlevel 1 (
    echo %GREEN%✓ Enhanced RAG Service is healthy%NC%
) else (
    echo %YELLOW%⚠ Enhanced RAG Service health check failed%NC%
)

curl -f http://localhost:8000/api/v1/heartbeat >nul 2>&1
if not errorlevel 1 (
    echo %GREEN%✓ ChromaDB is healthy%NC%
) else (
    echo %YELLOW%⚠ ChromaDB health check failed%NC%
)

curl -f http://localhost:9200/_cluster/health >nul 2>&1
if not errorlevel 1 (
    echo %GREEN%✓ Elasticsearch is healthy%NC%
) else (
    echo %YELLOW%⚠ Elasticsearch health check failed%NC%
)

curl -f http://localhost:9000/minio/health/live >nul 2>&1
if not errorlevel 1 (
    echo %GREEN%✓ MinIO is healthy%NC%
) else (
    echo %YELLOW%⚠ MinIO health check failed%NC%
)
goto :eof

:show_logs
cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml logs -f
goto :eof

:clean_services
cd /d "%PROJECT_ROOT%"
docker-compose -f docker-compose.rag-enhanced.yml down -v --remove-orphans
docker system prune -f
echo %GREEN%✓ Cleanup completed%NC%
goto :eof

:show_usage
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   build     Build Docker images
echo   start     Start all services
echo   stop      Stop all services
echo   restart   Restart all services
echo   status    Show service status
echo   health    Run health checks
echo   logs      Show service logs
echo   clean     Clean up containers and volumes
echo   help      Show this help message
goto :eof