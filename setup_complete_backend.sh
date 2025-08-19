#!/bin/bash

# Complete Setup Script for Backend Implementation
# This script sets up the entire system with project-based filtering

echo "🚀 Setting up Agentic AI Acceleration Backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if PostgreSQL is running
print_info "Checking PostgreSQL connection..."
if command -v psql >/dev/null 2>&1; then
    print_status "PostgreSQL CLI found"
else
    print_error "PostgreSQL CLI not found. Please install PostgreSQL."
    exit 1
fi

# Step 1: Database Setup
echo ""
print_info "Step 1: Setting up database..."
print_warning "Make sure PostgreSQL is running and you have a database ready"
print_info "Database migrations to run:"
echo "  - infra/migrations/0003_projects_system.sql"
echo "  - infra/migrations/0004_tools_workflows_system.sql"

read -p "Enter your database name: " DB_NAME
read -p "Enter your database username: " DB_USER

echo ""
print_info "Running database migrations..."

# Run migrations
echo "Running projects migration..."
if psql -d "$DB_NAME" -U "$DB_USER" -f infra/migrations/0003_projects_system.sql; then
    print_status "Projects migration completed"
else
    print_error "Projects migration failed"
    exit 1
fi

echo "Running tools & workflows migration..."
if psql -d "$DB_NAME" -U "$DB_USER" -f infra/migrations/0004_tools_workflows_system.sql; then
    print_status "Tools & workflows migration completed"
else
    print_error "Tools & workflows migration failed"
    exit 1
fi

# Step 2: Backend Services Setup
echo ""
print_info "Step 2: Setting up backend services..."

# Gateway Service
echo ""
print_info "Setting up Gateway Service..."
cd backend/services/gateway

if [ ! -f ".env" ]; then
    print_info "Creating .env file for gateway..."
    cat > .env << EOF
DATABASE_URL=postgresql://$DB_USER@localhost:5432/$DB_NAME
PROJECT_NAME=AgenticAI Gateway
VERSION=1.0.0
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Service URLs
ORCHESTRATOR_URL=http://localhost:8001
AGENTS_URL=http://localhost:8002
TOOLS_URL=http://localhost:8005
RAG_URL=http://localhost:8004
SQLTOOL_URL=http://localhost:8006
WORKFLOW_URL=http://localhost:8007
OBSERVABILITY_URL=http://localhost:8008
EOF
    print_status "Gateway .env file created"
else
    print_warning "Gateway .env file already exists"
fi

# Tools Service
echo ""
print_info "Setting up Tools Service..."
cd ../tools

if [ ! -f ".env" ]; then
    print_info "Creating .env file for tools service..."
    cat > .env << EOF
DATABASE_URL=postgresql://$DB_USER@localhost:5432/$DB_NAME
ENABLE_SYSTEM_TOOLS=true
MCP_SERVERS=[]
EOF
    print_status "Tools .env file created"
else
    print_warning "Tools .env file already exists"
fi

# Workflow Engine Service  
echo ""
print_info "Setting up Workflow Engine Service..."
cd ../workflow-engine

if [ ! -f ".env" ]; then
    print_info "Creating .env file for workflow engine..."
    cat > .env << EOF
DATABASE_URL=postgresql://$DB_USER@localhost:5432/$DB_NAME
REDIS_URL=redis://localhost:6379
EOF
    print_status "Workflow engine .env file created"
else
    print_warning "Workflow engine .env file already exists"
fi

# Return to root
cd ../../../

# Step 3: Install Dependencies
echo ""
print_info "Step 3: Installing dependencies..."

# Backend dependencies
print_info "Installing backend dependencies..."
echo "Please run the following commands to install backend dependencies:"
echo ""
echo "# Gateway service"
echo "cd backend/services/gateway && pip install -r requirements.txt"
echo ""
echo "# Tools service"  
echo "cd backend/services/tools && pip install -r requirements.txt"
echo ""
echo "# Workflow engine service"
echo "cd backend/services/workflow-engine && pip install -r requirements.txt"
echo ""

# Frontend dependencies
print_info "Installing frontend dependencies..."
cd frontend
if command -v pnpm >/dev/null 2>&1; then
    print_info "Installing frontend packages with pnpm..."
    pnpm install
    print_status "Frontend dependencies installed"
else
    print_warning "pnpm not found. Please install pnpm or use npm:"
    echo "npm install"
fi

cd ..

# Step 4: Start Services
echo ""
print_info "Step 4: Starting services..."
print_info "Use the following commands in separate terminals:"

echo ""
echo "Terminal 1 - Gateway Service:"
echo "cd backend/services/gateway"
echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo ""
echo "Terminal 2 - Tools Service:"
echo "cd backend/services/tools"  
echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8005"

echo ""
echo "Terminal 3 - Workflow Engine:"
echo "cd backend/services/workflow-engine"
echo "uvicorn app.main:app --reload --host 0.0.0.0 --port 8007"

echo ""
echo "Terminal 4 - Frontend:"
echo "cd frontend"
echo "pnpm dev"

# Step 5: Testing
echo ""
print_info "Step 5: Testing the setup..."
echo "Once all services are running, test with:"
echo ""
echo "# Test API connection"
echo "cd frontend && node test-api.js"
echo ""
echo "# Manual API tests"
echo "curl http://localhost:8000/api/v1/projects"
echo "curl http://localhost:8000/api/v1/services/tools/templates"
echo "curl http://localhost:8000/api/v1/services/workflow/workflows"

# Step 6: URLs
echo ""
print_status "🎉 Setup complete! Access your services at:"
echo ""
echo "Frontend:              http://localhost:3000"
echo "Gateway API:           http://localhost:8000"
echo "API Documentation:     http://localhost:8000/docs"
echo "Tools Service:         http://localhost:8005"
echo "Workflow Engine:       http://localhost:8007"

echo ""
print_info "📚 Documentation:"
echo "- Setup Guide: SETUP_BACKEND_FRONTEND.md"
echo "- Implementation Status: IMPLEMENTATION_STATUS.md"
echo "- Backend Status: BACKEND_STATUS.md"

echo ""
print_status "✨ Your project-based multi-agent platform is ready!"

echo ""
print_warning "Note: Make sure to start Redis if using workflow scheduling features:"
echo "redis-server"
