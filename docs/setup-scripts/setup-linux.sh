#!/bin/bash
# Enterprise AI Platform - Linux Setup Script
# This script sets up the complete platform without Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
SKIP_PYTHON=false
SKIP_NODE=false
SKIP_DATABASE=false
SKIP_REDIS=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-python)
            SKIP_PYTHON=true
            shift
            ;;
        --skip-node)
            SKIP_NODE=true
            shift
            ;;
        --skip-database)
            SKIP_DATABASE=true
            shift
            ;;
        --skip-redis)
            SKIP_REDIS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-python     Skip Python installation"
            echo "  --skip-node       Skip Node.js installation"
            echo "  --skip-database   Skip PostgreSQL installation"
            echo "  --skip-redis      Skip Redis installation"
            echo "  --verbose         Enable verbose output"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Utility functions
log_section() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

log_step() {
    echo -e "${GREEN}→ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

port_in_use() {
    netstat -tuln | grep -q ":$1 "
}

check_os() {
    log_section "Detecting Operating System"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            OS="ubuntu"
            PACKAGE_MANAGER="apt"
            log_step "Detected Ubuntu/Debian system"
        elif command_exists yum; then
            OS="centos"
            PACKAGE_MANAGER="yum"
            log_step "Detected CentOS/RHEL system"
        elif command_exists dnf; then
            OS="fedora"
            PACKAGE_MANAGER="dnf"
            log_step "Detected Fedora system"
        else
            log_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
        log_step "Detected macOS system"
        if ! command_exists brew; then
            log_error "Homebrew is required on macOS. Please install it first."
            exit 1
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

update_package_manager() {
    log_step "Updating package manager..."
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get update
            ;;
        yum)
            sudo yum update -y
            ;;
        dnf)
            sudo dnf update -y
            ;;
        brew)
            brew update
            ;;
    esac
}

install_python() {
    if [[ "$SKIP_PYTHON" == true ]]; then
        log_warning "Skipping Python installation"
        return
    fi
    
    log_section "Installing Python 3.11"
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_step "Python already installed: Python $PYTHON_VERSION"
        
        # Check if version is 3.11+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            log_step "Python version is compatible (3.11+)"
        else
            log_warning "Python version is older than 3.11. Consider upgrading."
        fi
    else
        log_step "Installing Python 3.11..."
        case $PACKAGE_MANAGER in
            apt)
                sudo apt-get install -y python3.11 python3.11-pip python3.11-venv python3.11-dev
                # Create symlinks
                sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
                ;;
            yum)
                sudo yum install -y python311 python311-pip python311-devel
                ;;
            dnf)
                sudo dnf install -y python3.11 python3.11-pip python3.11-devel
                ;;
            brew)
                brew install python@3.11
                ;;
        esac
    fi
    
    # Ensure pip is available
    if ! command_exists pip3; then
        log_step "Installing pip..."
        python3 -m ensurepip --upgrade
    fi
    
    # Upgrade pip and install essential packages
    log_step "Upgrading pip and installing essential packages..."
    python3 -m pip install --upgrade pip
    python3 -m pip install virtualenv uvicorn fastapi
}

install_nodejs() {
    if [[ "$SKIP_NODE" == true ]]; then
        log_warning "Skipping Node.js installation"
        return
    fi
    
    log_section "Installing Node.js and pnpm"
    
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log_step "Node.js already installed: $NODE_VERSION"
        
        # Check if version is 18+
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [[ $NODE_MAJOR -ge 18 ]]; then
            log_step "Node.js version is compatible (18+)"
        else
            log_warning "Node.js version is older than 18. Consider upgrading."
        fi
    else
        log_step "Installing Node.js LTS..."
        
        # Install Node.js via NodeSource repository
        case $PACKAGE_MANAGER in
            apt)
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            yum)
                curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
                sudo yum install -y nodejs npm
                ;;
            dnf)
                curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
                sudo dnf install -y nodejs npm
                ;;
            brew)
                brew install node
                ;;
        esac
    fi
    
    # Install pnpm
    if command_exists pnpm; then
        log_step "pnpm already installed"
    else
        log_step "Installing pnpm..."
        npm install -g pnpm
    fi
}

install_postgresql() {
    if [[ "$SKIP_DATABASE" == true ]]; then
        log_warning "Skipping PostgreSQL installation"
        return
    fi
    
    log_section "Installing PostgreSQL"
    
    if command_exists psql; then
        log_step "PostgreSQL already installed"
    else
        log_step "Installing PostgreSQL 16..."
        case $PACKAGE_MANAGER in
            apt)
                # Add PostgreSQL official APT repository
                sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
                wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
                sudo apt-get update
                sudo apt-get install -y postgresql-16 postgresql-client-16 postgresql-contrib-16
                ;;
            yum)
                sudo yum install -y postgresql16-server postgresql16 postgresql16-contrib
                sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
                ;;
            dnf)
                sudo dnf install -y postgresql16-server postgresql16 postgresql16-contrib
                sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
                ;;
            brew)
                brew install postgresql@16
                ;;
        esac
    fi
    
    # Start and enable PostgreSQL service
    log_step "Starting PostgreSQL service..."
    case $OS in
        ubuntu)
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        centos|fedora)
            sudo systemctl start postgresql-16
            sudo systemctl enable postgresql-16
            ;;
        macos)
            brew services start postgresql@16
            ;;
    esac
    
    # Wait for PostgreSQL to start
    log_step "Waiting for PostgreSQL to start..."
    sleep 5
    
    # Test connection
    local attempts=0
    local max_attempts=30
    
    while [[ $attempts -lt $max_attempts ]]; do
        if port_in_use 5432; then
            log_step "PostgreSQL is running on port 5432"
            break
        fi
        
        ((attempts++))
        echo "Waiting for PostgreSQL to start... ($attempts/$max_attempts)"
        sleep 2
    done
    
    if [[ $attempts -eq $max_attempts ]]; then
        log_error "PostgreSQL failed to start after $max_attempts attempts"
        exit 1
    fi
    
    # Install pgvector extension
    log_step "Installing pgvector extension..."
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get install -y postgresql-16-pgvector
            ;;
        yum)
            sudo yum install -y pgvector_16
            ;;
        dnf)
            sudo dnf install -y pgvector_16
            ;;
        brew)
            brew install pgvector
            ;;
    esac
}

install_redis() {
    if [[ "$SKIP_REDIS" == true ]]; then
        log_warning "Skipping Redis installation"
        return
    fi
    
    log_section "Installing Redis"
    
    if port_in_use 6379; then
        log_step "Redis already running on port 6379"
    else
        log_step "Installing Redis..."
        case $PACKAGE_MANAGER in
            apt)
                sudo apt-get install -y redis-server
                ;;
            yum)
                sudo yum install -y redis
                ;;
            dnf)
                sudo dnf install -y redis
                ;;
            brew)
                brew install redis
                ;;
        esac
        
        # Start and enable Redis service
        log_step "Starting Redis service..."
        case $OS in
            ubuntu|centos|fedora)
                sudo systemctl start redis
                sudo systemctl enable redis
                ;;
            macos)
                brew services start redis
                ;;
        esac
    fi
}

setup_database() {
    log_section "Setting up Database"
    
    # Set PostgreSQL password for postgres user
    log_step "Setting up PostgreSQL user and database..."
    
    # Switch to postgres user and run commands
    sudo -u postgres psql << EOF
-- Create user and database
CREATE USER agenticai_user WITH PASSWORD 'agenticai_password';
CREATE DATABASE agenticai_platform OWNER agenticai_user;
GRANT ALL PRIVILEGES ON DATABASE agenticai_platform TO agenticai_user;

-- Connect to the new database and create extensions
\c agenticai_platform;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
\q
EOF
    
    log_step "Database setup completed successfully"
}

setup_backend_services() {
    log_section "Setting up Backend Services"
    
    local services=(
        "gateway:8000"
        "agents:8002"
        "orchestrator:8003"
        "rag:8004"
        "tools:8005"
        "sqltool:8006"
        "workflow-engine:8007"
        "observability:8008"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name service_port <<< "$service_info"
        local service_path="backend/services/$service_name"
        
        if [[ -d "$service_path" ]]; then
            log_step "Setting up $service_name service..."
            
            pushd "$service_path" > /dev/null
            
            # Create virtual environment
            if [[ ! -d "venv" ]]; then
                log_step "Creating virtual environment for $service_name..."
                python3 -m venv venv
            fi
            
            # Activate virtual environment and install dependencies
            log_step "Installing dependencies for $service_name..."
            source venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
            deactivate
            
            log_step "$service_name service setup completed"
            popd > /dev/null
        else
            log_warning "Service directory not found: $service_path"
        fi
    done
}

setup_frontend() {
    log_section "Setting up Frontend"
    
    local frontend_path="frontend"
    
    if [[ -d "$frontend_path" ]]; then
        pushd "$frontend_path" > /dev/null
        
        log_step "Installing frontend dependencies..."
        pnpm install
        
        log_step "Building frontend..."
        pnpm build
        
        log_step "Frontend setup completed"
        popd > /dev/null
    else
        log_error "Frontend directory not found: $frontend_path"
        exit 1
    fi
}

run_database_migrations() {
    log_section "Running Database Migrations"
    
    local migration_path="infra/migrations/0001_complete_schema.sql"
    
    if [[ -f "$migration_path" ]]; then
        log_step "Running database migrations..."
        
        export PGPASSWORD="agenticai_password"
        psql -h localhost -U agenticai_user -d agenticai_platform -f "$migration_path"
        
        log_step "Database migrations completed successfully"
    else
        log_warning "Migration file not found: $migration_path"
    fi
}

create_environment_files() {
    log_section "Creating Environment Files"
    
    # Backend environment file
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql+asyncpg://agenticai_user:agenticai_password@localhost:5432/agenticai_platform

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
EOF
    
    # Frontend environment file
    cat > frontend/.env.local << 'EOF'
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
EOF
    
    log_step "Environment files created successfully"
    log_warning "Please update the API keys in the .env files before running the services"
}

create_startup_scripts() {
    log_section "Creating Startup Scripts"
    
    # Backend startup script
    cat > start-backend.sh << 'EOF'
#!/bin/bash
# Start Backend Services

services=(
    "gateway:8000:backend/services/gateway"
    "agents:8002:backend/services/agents"
    "orchestrator:8003:backend/services/orchestrator"
    "rag:8004:backend/services/rag"
    "tools:8005:backend/services/tools"
    "sqltool:8006:backend/services/sqltool"
    "workflow-engine:8007:backend/services/workflow-engine"
    "observability:8008:backend/services/observability"
)

echo -e "\033[0;32mStarting Backend Services...\033[0m"

for service_info in "${services[@]}"; do
    IFS=':' read -r service_name service_port service_dir <<< "$service_info"
    echo -e "\033[1;33mStarting $service_name on port $service_port...\033[0m"
    
    # Start service in background
    (
        cd "$service_dir"
        source venv/bin/activate
        uvicorn app.main:app --host 0.0.0.0 --port "$service_port" --reload
    ) &
    
    sleep 2
done

echo -e "\033[0;32mAll backend services started!\033[0m"
echo -e "\033[0;36mGateway API: http://localhost:8000\033[0m"
echo -e "\033[0;36mAPI Docs: http://localhost:8000/docs\033[0m"

# Keep script running
wait
EOF
    
    # Frontend startup script
    cat > start-frontend.sh << 'EOF'
#!/bin/bash
# Start Frontend Service

echo -e "\033[0;32mStarting Frontend Service...\033[0m"

cd frontend
pnpm dev

echo -e "\033[0;32mFrontend started!\033[0m"
echo -e "\033[0;36mFrontend URL: http://localhost:3000\033[0m"
EOF
    
    # All-in-one startup script
    cat > start-platform.sh << 'EOF'
#!/bin/bash
# Start All Services

echo -e "\033[0;32mStarting Enterprise AI Platform...\033[0m"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\033[1;33mStopping services...\033[0m"
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend services
echo -e "\033[1;33mStarting backend services...\033[0m"
./start-backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to initialize
sleep 10

# Start frontend
echo -e "\033[1;33mStarting frontend...\033[0m"
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo -e "\033[0;32mEnterprise AI Platform is running!\033[0m"
echo -e "\033[0;36mFrontend: http://localhost:3000\033[0m"
echo -e "\033[0;36mBackend API: http://localhost:8000\033[0m"
echo -e "\033[0;36mAPI Documentation: http://localhost:8000/docs\033[0m"
echo ""
echo -e "\033[1;33mDefault Admin Credentials:\033[0m"
echo "Email: admin@agenticai.local"
echo "Password: admin123"
echo ""
echo -e "\033[1;33mPress Ctrl+C to stop all services\033[0m"

# Wait for background processes
wait
EOF
    
    # Make scripts executable
    chmod +x start-backend.sh start-frontend.sh start-platform.sh
    
    log_step "Startup scripts created successfully"
}

test_installation() {
    log_section "Testing Installation"
    
    local errors=()
    
    # Test Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        log_step "✓ Python: $PYTHON_VERSION"
    else
        errors+=("Python not found")
    fi
    
    # Test Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        log_step "✓ Node.js: $NODE_VERSION"
    else
        errors+=("Node.js not found")
    fi
    
    # Test pnpm
    if command_exists pnpm; then
        PNPM_VERSION=$(pnpm --version)
        log_step "✓ pnpm: v$PNPM_VERSION"
    else
        errors+=("pnpm not found")
    fi
    
    # Test PostgreSQL
    if port_in_use 5432; then
        log_step "✓ PostgreSQL: Running on port 5432"
    else
        errors+=("PostgreSQL not running on port 5432")
    fi
    
    # Test Redis
    if port_in_use 6379; then
        log_step "✓ Redis: Running on port 6379"
    else
        errors+=("Redis not running on port 6379")
    fi
    
    # Test database connection
    if PGPASSWORD="agenticai_password" psql -h localhost -U agenticai_user -d agenticai_platform -c "SELECT 1;" > /dev/null 2>&1; then
        log_step "✓ Database: Connection successful"
    else
        errors+=("Database connection failed")
    fi
    
    if [[ ${#errors[@]} -eq 0 ]]; then
        echo -e "${GREEN}🎉 Installation test completed successfully!${NC}"
    else
        log_error "Installation test failed with errors:"
        for error in "${errors[@]}"; do
            log_error "  - $error"
        done
        exit 1
    fi
}

show_summary() {
    log_section "Installation Summary"
    
    echo -e "${GREEN}✅ Enterprise AI Platform setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Update API keys in .env and frontend/.env.local files"
    echo "2. Run: ./start-platform.sh to start all services"
    echo "3. Open http://localhost:3000 in your browser"
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo "• Frontend:      http://localhost:3000"
    echo "• API Gateway:   http://localhost:8000"
    echo "• API Docs:      http://localhost:8000/docs"
    echo "• Agents:        http://localhost:8002"
    echo "• Orchestrator:  http://localhost:8003"
    echo "• RAG Service:   http://localhost:8004"
    echo "• Tools:         http://localhost:8005"
    echo ""
    echo -e "${YELLOW}Default Admin Credentials:${NC}"
    echo "Email: admin@agenticai.local"
    echo "Password: admin123"
    echo ""
    echo -e "${BLUE}Support:${NC}"
    echo "• Documentation: docs/"
    echo "• Scripts: scripts/"
    echo "• Issues: Check logs in service directories"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Enterprise AI Platform Linux Setup${NC}"
    echo -e "${BLUE}This script will set up the complete platform without Docker${NC}"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Detect OS and package manager
    check_os
    
    # Update package manager
    update_package_manager
    
    # Install prerequisites
    install_python
    install_nodejs
    install_postgresql
    install_redis
    
    # Setup database
    setup_database
    
    # Setup application
    setup_backend_services
    setup_frontend
    run_database_migrations
    
    # Create configuration
    create_environment_files
    create_startup_scripts
    
    # Test installation
    test_installation
    
    # Show summary
    show_summary
}

# Run main function
main "$@"
