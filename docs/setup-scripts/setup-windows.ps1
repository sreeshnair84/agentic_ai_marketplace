#!/usr/bin/env pwsh
# Enterprise AI Platform - Windows Setup Script
# This script sets up the complete platform without Docker

param(
    [switch]$SkipPython,
    [switch]$SkipNode,
    [switch]$SkipDatabase,
    [switch]$SkipRedis,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "${Color}${Message}${Reset}"
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "=" * 60 $Blue
    Write-ColorOutput $Title $Blue
    Write-ColorOutput "=" * 60 $Blue
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "→ $Message" $Green
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ WARNING: $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ ERROR: $Message" $Red
}

function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

function Install-Chocolatey {
    if (Test-Command "choco") {
        Write-Step "Chocolatey already installed"
        return
    }
    
    Write-Step "Installing Chocolatey package manager..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Install-Python {
    if ($SkipPython) {
        Write-Warning "Skipping Python installation"
        return
    }
    
    Write-Section "Installing Python 3.11"
    
    if (Test-Command "python") {
        $pythonVersion = python --version 2>&1
        Write-Step "Python already installed: $pythonVersion"
        
        # Check if version is 3.11+
        $version = [version]($pythonVersion -replace "Python ", "")
        if ($version -ge [version]"3.11.0") {
            Write-Step "Python version is compatible (3.11+)"
        } else {
            Write-Warning "Python version is older than 3.11. Consider upgrading."
        }
    } else {
        Write-Step "Installing Python 3.11..."
        choco install python311 -y
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    # Install pip if not available
    if (-not (Test-Command "pip")) {
        Write-Step "Installing pip..."
        python -m ensurepip --upgrade
    }
    
    # Upgrade pip and install essential packages
    Write-Step "Upgrading pip and installing essential packages..."
    python -m pip install --upgrade pip
    python -m pip install virtualenv uvicorn fastapi
}

function Install-NodeJS {
    if ($SkipNode) {
        Write-Warning "Skipping Node.js installation"
        return
    }
    
    Write-Section "Installing Node.js and pnpm"
    
    if (Test-Command "node") {
        $nodeVersion = node --version
        Write-Step "Node.js already installed: $nodeVersion"
        
        # Check if version is 18+
        $version = [version]($nodeVersion -replace "v", "")
        if ($version -ge [version]"18.0.0") {
            Write-Step "Node.js version is compatible (18+)"
        } else {
            Write-Warning "Node.js version is older than 18. Consider upgrading."
        }
    } else {
        Write-Step "Installing Node.js LTS..."
        choco install nodejs-lts -y
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    # Install pnpm
    if (Test-Command "pnpm") {
        Write-Step "pnpm already installed"
    } else {
        Write-Step "Installing pnpm..."
        npm install -g pnpm
    }
}

function Install-PostgreSQL {
    if ($SkipDatabase) {
        Write-Warning "Skipping PostgreSQL installation"
        return
    }
    
    Write-Section "Installing PostgreSQL"
    
    if (Test-Command "psql") {
        Write-Step "PostgreSQL already installed"
    } else {
        Write-Step "Installing PostgreSQL 16..."
        choco install postgresql16 --params '/Password:lcnc_password' -y
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    # Wait for PostgreSQL to start
    Write-Step "Waiting for PostgreSQL to start..."
    Start-Sleep -Seconds 10
    
    # Test connection
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        if (Test-Port 5432) {
            Write-Step "PostgreSQL is running on port 5432"
            break
        }
        
        $attempt++
        Write-Host "Waiting for PostgreSQL to start... ($attempt/$maxAttempts)"
        Start-Sleep -Seconds 2
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Error "PostgreSQL failed to start after $maxAttempts attempts"
        throw "PostgreSQL startup failed"
    }
}

function Install-Redis {
    if ($SkipRedis) {
        Write-Warning "Skipping Redis installation"
        return
    }
    
    Write-Section "Installing Redis"
    
    # Redis is not officially supported on Windows, we'll use Memurai (Redis-compatible)
    if (Test-Port 6379) {
        Write-Step "Redis-compatible service already running on port 6379"
    } else {
        Write-Step "Installing Memurai (Redis-compatible for Windows)..."
        
        # Download and install Memurai
        $memuriUrl = "https://www.memurai.com/get-memurai"
        Write-Step "Please download and install Memurai from: $memuriUrl"
        Write-Step "Or install Redis using WSL2"
        
        # Alternative: Install Redis via chocolatey (uses Memurai)
        try {
            choco install redis-64 -y
        } catch {
            Write-Warning "Could not install Redis via Chocolatey. Please install manually."
        }
    }
}

function Setup-Database {
    Write-Section "Setting up Database"
    
    # Set PostgreSQL environment variables
    $env:PGUSER = "postgres"
    $env:PGPASSWORD = "lcnc_password"
    
    Write-Step "Creating database and user..."
    
    # Create database and user
    $createDbScript = @"
CREATE USER lcnc_user WITH PASSWORD 'lcnc_password';
CREATE DATABASE lcnc_platform OWNER lcnc_user;
GRANT ALL PRIVILEGES ON DATABASE lcnc_platform TO lcnc_user;
\q
"@
    
    # Write script to temp file
    $tempScript = [System.IO.Path]::GetTempFileName() + ".sql"
    $createDbScript | Out-File -FilePath $tempScript -Encoding UTF8
    
    try {
        Write-Step "Executing database creation script..."
        psql -h localhost -U postgres -f $tempScript
        
        # Install pgvector extension
        Write-Step "Installing pgvector extension..."
        psql -h localhost -U postgres -d lcnc_platform -c "CREATE EXTENSION IF NOT EXISTS vector;"
        
        Write-Step "Database setup completed successfully"
    }
    catch {
        Write-Error "Database setup failed: $($_.Exception.Message)"
        throw
    }
    finally {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}

function Setup-BackendServices {
    Write-Section "Setting up Backend Services"
    
    $services = @(
        @{Name="gateway"; Port=8000},
        @{Name="agents"; Port=8002},
        @{Name="orchestrator"; Port=8003},
        @{Name="rag"; Port=8004},
        @{Name="tools"; Port=8005},
        @{Name="sqltool"; Port=8006},
        @{Name="workflow-engine"; Port=8007},
        @{Name="observability"; Port=8008}
    )
    
    foreach ($service in $services) {
        $servicePath = "backend\services\$($service.Name)"
        
        if (Test-Path $servicePath) {
            Write-Step "Setting up $($service.Name) service..."
            
            Push-Location $servicePath
            try {
                # Create virtual environment
                if (-not (Test-Path "venv")) {
                    Write-Step "Creating virtual environment for $($service.Name)..."
                    python -m venv venv
                }
                
                # Activate virtual environment and install dependencies
                Write-Step "Installing dependencies for $($service.Name)..."
                .\venv\Scripts\Activate.ps1
                python -m pip install --upgrade pip
                python -m pip install -r requirements.txt
                deactivate
                
                Write-Step "$($service.Name) service setup completed"
            }
            catch {
                Write-Error "Failed to setup $($service.Name): $($_.Exception.Message)"
            }
            finally {
                Pop-Location
            }
        } else {
            Write-Warning "Service directory not found: $servicePath"
        }
    }
}

function Setup-Frontend {
    Write-Section "Setting up Frontend"
    
    $frontendPath = "frontend"
    
    if (Test-Path $frontendPath) {
        Push-Location $frontendPath
        try {
            Write-Step "Installing frontend dependencies..."
            pnpm install
            
            Write-Step "Building frontend..."
            pnpm build
            
            Write-Step "Frontend setup completed"
        }
        catch {
            Write-Error "Frontend setup failed: $($_.Exception.Message)"
        }
        finally {
            Pop-Location
        }
    } else {
        Write-Error "Frontend directory not found: $frontendPath"
    }
}

function Run-DatabaseMigrations {
    Write-Section "Running Database Migrations"
    
    $migrationPath = "infra\migrations\0001_complete_schema.sql"
    
    if (Test-Path $migrationPath) {
        Write-Step "Running database migrations..."
        $env:PGPASSWORD = "lcnc_password"
        
        try {
            psql -h localhost -U lcnc_user -d lcnc_platform -f $migrationPath
            Write-Step "Database migrations completed successfully"
        }
        catch {
            Write-Error "Database migration failed: $($_.Exception.Message)"
        }
    } else {
        Write-Warning "Migration file not found: $migrationPath"
    }
}

function Create-EnvironmentFiles {
    Write-Section "Creating Environment Files"
    
    # Backend environment file
    $backendEnv = @"
# Database Configuration
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@localhost:5432/lcnc_platform

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# CORS Configuration
CORS_ORIGINS_STR=http://localhost:3000,http://127.0.0.1:3000

# AI Provider Keys (Add your actual keys)
GOOGLE_API_KEY=your-google-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Service URLs
ORCHESTRATOR_URL=http://localhost:8003
AGENTS_URL=http://localhost:8002
TOOLS_URL=http://localhost:8005
RAG_URL=http://localhost:8004
SQLTOOL_URL=http://localhost:8006
WORKFLOW_URL=http://localhost:8007
OBSERVABILITY_URL=http://localhost:8008

# A2A Protocol
A2A_PROTOCOL_ENABLED=true
MCP_SERVER_ENABLED=true

# Environment
ENVIRONMENT=development
"@
    
    # Frontend environment file
    $frontendEnv = @"
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000

# NextAuth Configuration
NEXTAUTH_SECRET=your-nextauth-secret-key
NEXTAUTH_URL=http://localhost:3000

# OAuth Providers (Optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
"@
    
    # Create .env files
    Write-Step "Creating backend .env file..."
    $backendEnv | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Step "Creating frontend .env.local file..."
    $frontendEnv | Out-File -FilePath "frontend\.env.local" -Encoding UTF8
    
    Write-Step "Environment files created successfully"
    Write-Warning "Please update the API keys in the .env files before running the services"
}

function Create-StartupScripts {
    Write-Section "Creating Startup Scripts"
    
    # Backend startup script
    $backendScript = @"
#!/usr/bin/env pwsh
# Start Backend Services

`$services = @(
    @{Name="gateway"; Port=8000; Dir="backend\services\gateway"},
    @{Name="agents"; Port=8002; Dir="backend\services\agents"},
    @{Name="orchestrator"; Port=8003; Dir="backend\services\orchestrator"},
    @{Name="rag"; Port=8004; Dir="backend\services\rag"},
    @{Name="tools"; Port=8005; Dir="backend\services\tools"},
    @{Name="sqltool"; Port=8006; Dir="backend\services\sqltool"},
    @{Name="workflow-engine"; Port=8007; Dir="backend\services\workflow-engine"},
    @{Name="observability"; Port=8008; Dir="backend\services\observability"}
)

Write-Host "Starting Backend Services..." -ForegroundColor Green

foreach (`$service in `$services) {
    Write-Host "Starting `$(`$service.Name) on port `$(`$service.Port)..." -ForegroundColor Yellow
    
    Start-Process powershell -ArgumentList @(
        "-Command",
        "cd '`$(`$service.Dir)'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port `$(`$service.Port) --reload"
    ) -WindowStyle Normal
    
    Start-Sleep -Seconds 2
}

Write-Host "All backend services started!" -ForegroundColor Green
Write-Host "Gateway API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
"@
    
    # Frontend startup script
    $frontendScript = @"
#!/usr/bin/env pwsh
# Start Frontend Service

Write-Host "Starting Frontend Service..." -ForegroundColor Green

cd frontend
pnpm dev

Write-Host "Frontend started!" -ForegroundColor Green
Write-Host "Frontend URL: http://localhost:3000" -ForegroundColor Cyan
"@
    
    # All-in-one startup script
    $allScript = @"
#!/usr/bin/env pwsh
# Start All Services

Write-Host "Starting Enterprise AI Platform..." -ForegroundColor Green

# Start backend services
Write-Host "Starting backend services..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @("-File", "start-backend.ps1") -WindowStyle Normal

# Wait a bit for backend to initialize
Start-Sleep -Seconds 10

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @("-File", "start-frontend.ps1") -WindowStyle Normal

Write-Host ""
Write-Host "Enterprise AI Platform is starting up!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default Admin Credentials:" -ForegroundColor Yellow
Write-Host "Email: admin@lcnc.local" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
"@
    
    Write-Step "Creating startup scripts..."
    $backendScript | Out-File -FilePath "start-backend.ps1" -Encoding UTF8
    $frontendScript | Out-File -FilePath "start-frontend.ps1" -Encoding UTF8
    $allScript | Out-File -FilePath "start-platform.ps1" -Encoding UTF8
    
    Write-Step "Startup scripts created successfully"
}

function Test-Installation {
    Write-Section "Testing Installation"
    
    $errors = @()
    
    # Test Python
    if (Test-Command "python") {
        $pythonVersion = python --version 2>&1
        Write-Step "✓ Python: $pythonVersion"
    } else {
        $errors += "Python not found"
    }
    
    # Test Node.js
    if (Test-Command "node") {
        $nodeVersion = node --version
        Write-Step "✓ Node.js: $nodeVersion"
    } else {
        $errors += "Node.js not found"
    }
    
    # Test pnpm
    if (Test-Command "pnpm") {
        $pnpmVersion = pnpm --version
        Write-Step "✓ pnpm: v$pnpmVersion"
    } else {
        $errors += "pnpm not found"
    }
    
    # Test PostgreSQL
    if (Test-Port 5432) {
        Write-Step "✓ PostgreSQL: Running on port 5432"
    } else {
        $errors += "PostgreSQL not running on port 5432"
    }
    
    # Test Redis
    if (Test-Port 6379) {
        Write-Step "✓ Redis: Running on port 6379"
    } else {
        $errors += "Redis not running on port 6379"
    }
    
    # Test database connection
    try {
        $env:PGPASSWORD = "lcnc_password"
        $result = psql -h localhost -U lcnc_user -d lcnc_platform -c "SELECT 1;" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Step "✓ Database: Connection successful"
        } else {
            $errors += "Database connection failed"
        }
    } catch {
        $errors += "Database connection test failed"
    }
    
    if ($errors.Count -eq 0) {
        Write-ColorOutput "🎉 Installation test completed successfully!" $Green
    } else {
        Write-Error "Installation test failed with errors:"
        foreach ($error in $errors) {
            Write-Error "  - $error"
        }
        throw "Installation validation failed"
    }
}

function Show-Summary {
    Write-Section "Installation Summary"
    
    Write-ColorOutput "✅ Enterprise AI Platform setup completed successfully!" $Green
    Write-Host ""
    Write-ColorOutput "Next Steps:" $Blue
    Write-Host "1. Update API keys in .env and frontend\.env.local files"
    Write-Host "2. Run: .\start-platform.ps1 to start all services"
    Write-Host "3. Open http://localhost:3000 in your browser"
    Write-Host ""
    Write-ColorOutput "Service URLs:" $Blue
    Write-Host "• Frontend:      http://localhost:3000"
    Write-Host "• API Gateway:   http://localhost:8000"
    Write-Host "• API Docs:      http://localhost:8000/docs"
    Write-Host "• Agents:        http://localhost:8002"
    Write-Host "• Orchestrator:  http://localhost:8003"
    Write-Host "• RAG Service:   http://localhost:8004"
    Write-Host "• Tools:         http://localhost:8005"
    Write-Host ""
    Write-ColorOutput "Default Admin Credentials:" $Yellow
    Write-Host "Email: admin@lcnc.local"
    Write-Host "Password: admin123"
    Write-Host ""
    Write-ColorOutput "Support:" $Blue
    Write-Host "• Documentation: docs/"
    Write-Host "• Scripts: scripts/"
    Write-Host "• Issues: Check logs in service directories"
}

# Main execution
try {
    Write-ColorOutput "🚀 Enterprise AI Platform Windows Setup" $Blue
    Write-ColorOutput "This script will set up the complete platform without Docker" $Blue
    
    # Check if running as administrator
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Warning "Running without administrator privileges. Some installations may fail."
        Write-Host "Consider running as administrator for best results."
        Read-Host "Press Enter to continue or Ctrl+C to cancel"
    }
    
    # Install prerequisites
    Install-Chocolatey
    Install-Python
    Install-NodeJS
    Install-PostgreSQL
    Install-Redis
    
    # Setup database
    Setup-Database
    
    # Setup application
    Setup-BackendServices
    Setup-Frontend
    Run-DatabaseMigrations
    
    # Create configuration
    Create-EnvironmentFiles
    Create-StartupScripts
    
    # Test installation
    Test-Installation
    
    # Show summary
    Show-Summary
    
} catch {
    Write-Error "Setup failed: $($_.Exception.Message)"
    Write-Host "Please check the error messages above and try again."
    exit 1
}
