#!/bin/bash

# Enhanced RAG System Build and Deploy Script
# Builds and deploys the complete RAG system with all dependencies

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
BUILD_VERSION=${BUILD_VERSION:-"v2.0.0"}
BUILD_COMMIT=${BUILD_COMMIT:-$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")}

echo -e "${BLUE}🚀 Enhanced RAG System Build Script${NC}"
echo -e "${BLUE}====================================${NC}"
echo "Build Date: $BUILD_DATE"
echo "Version: $BUILD_VERSION"
echo "Commit: $BUILD_COMMIT"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if required tools are installed
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_status "All dependencies are installed"
}

# Function to create necessary directories
create_directories() {
    echo -e "${BLUE}Creating necessary directories...${NC}"
    
    local dirs=(
        "$PROJECT_ROOT/data/models"
        "$PROJECT_ROOT/data/cache"
        "$PROJECT_ROOT/data/vector_db"
        "$PROJECT_ROOT/data/logs"
        "$PROJECT_ROOT/data/uploads"
        "$PROJECT_ROOT/monitoring/prometheus"
        "$PROJECT_ROOT/monitoring/grafana/dashboards"
        "$PROJECT_ROOT/monitoring/grafana/datasources"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Function to create environment file if it doesn't exist
create_env_file() {
    local env_file="$PROJECT_ROOT/.env.rag"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${BLUE}Creating environment configuration file...${NC}"
        
        cat > "$env_file" << EOF
# Enhanced RAG System Environment Configuration
# Generated on $BUILD_DATE

# Build information
BUILD_DATE=$BUILD_DATE
BUILD_VERSION=$BUILD_VERSION
BUILD_COMMIT=$BUILD_COMMIT

# Database Configuration
POSTGRES_DB=agenticai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_secure_password_change_me
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=redis_secure_password_change_me

# API Keys (set these to your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here_change_me
ENCRYPTION_KEY=your_encryption_key_here_change_me

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin_change_me

# Grafana Configuration
GRAFANA_PASSWORD=admin_change_me

# RAG Service Configuration
RAG_SERVICE_PORT=8005
CHROMADB_PORT=8000
ELASTICSEARCH_PORT=9200

# Performance Settings
MAX_WORKERS=4
MEMORY_LIMIT=4G
CPU_LIMIT=2.0

# Feature Toggles
ENABLE_DOCLING=true
ENABLE_LANGGRAPH=true
ENABLE_MCP=true
ENABLE_MONITORING=true
EOF
        
        print_status "Created environment file: $env_file"
        print_warning "Please edit $env_file and set your actual API keys and passwords!"
    else
        print_status "Environment file already exists: $env_file"
    fi
}

# Function to create monitoring configuration
create_monitoring_config() {
    echo -e "${BLUE}Creating monitoring configuration...${NC}"
    
    # Prometheus configuration
    local prometheus_config="$PROJECT_ROOT/monitoring/prometheus.yml"
    if [ ! -f "$prometheus_config" ]; then
        cat > "$prometheus_config" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files: []

scrape_configs:
  - job_name: 'rag-enhanced'
    static_configs:
      - targets: ['rag-enhanced:8005']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'chromadb'
    static_configs:
      - targets: ['chromadb:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF
        print_status "Created Prometheus configuration"
    fi
}

# Function to validate Docker Compose file
validate_compose() {
    echo -e "${BLUE}Validating Docker Compose configuration...${NC}"
    
    cd "$PROJECT_ROOT"
    
    if docker-compose -f docker-compose.rag-enhanced.yml config > /dev/null 2>&1; then
        print_status "Docker Compose configuration is valid"
    else
        print_error "Docker Compose configuration is invalid"
        docker-compose -f docker-compose.rag-enhanced.yml config
        exit 1
    fi
}

# Function to build Docker images
build_images() {
    echo -e "${BLUE}Building Docker images...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Export build arguments
    export BUILD_DATE
    export BUILD_VERSION
    export BUILD_COMMIT
    
    # Build the enhanced RAG service
    echo -e "${YELLOW}Building Enhanced RAG Service...${NC}"
    docker build \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg BUILD_VERSION="$BUILD_VERSION" \
        --build-arg BUILD_COMMIT="$BUILD_COMMIT" \
        -f backend/services/tools/Dockerfile.rag-enhanced \
        -t agenticai/rag-enhanced:$BUILD_VERSION \
        -t agenticai/rag-enhanced:latest \
        backend/services/tools/
    
    print_status "Enhanced RAG Service image built"
    
    # Optionally build other services
    if [ "$BUILD_ALL_SERVICES" = "true" ]; then
        echo -e "${YELLOW}Building additional services...${NC}"
        
        # Tools service
        docker build \
            -f backend/services/tools/Dockerfile \
            -t agenticai/tools:$BUILD_VERSION \
            backend/services/tools/
            
        # RAG service (traditional)
        docker build \
            -f backend/services/rag/Dockerfile \
            -t agenticai/rag:$BUILD_VERSION \
            backend/services/rag/
        
        print_status "Additional services built"
    fi
}

# Function to start services
start_services() {
    echo -e "${BLUE}Starting Enhanced RAG System...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Load environment variables
    if [ -f ".env.rag" ]; then
        export $(cat .env.rag | xargs)
    fi
    
    # Start services with Docker Compose
    docker-compose -f docker-compose.rag-enhanced.yml up -d
    
    print_status "Services are starting up..."
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8005/health > /dev/null 2>&1; then
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo ""
    
    if [ $attempt -le $max_attempts ]; then
        print_status "Enhanced RAG Service is ready!"
    else
        print_warning "Service health check timed out. Check logs with: docker-compose -f docker-compose.rag-enhanced.yml logs"
    fi
}

# Function to show service status
show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.rag-enhanced.yml ps
    
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo "• Enhanced RAG API: http://localhost:8005"
    echo "• ChromaDB: http://localhost:8000"
    echo "• PostgreSQL: localhost:5432"
    echo "• Redis: localhost:6379"
    echo "• Elasticsearch: http://localhost:9200"
    echo "• MinIO: http://localhost:9000 (Console: http://localhost:9001)"
    echo "• Prometheus: http://localhost:9090"
    echo "• Grafana: http://localhost:3000"
    echo ""
    echo -e "${BLUE}API Documentation:${NC}"
    echo "• RAG API Docs: http://localhost:8005/docs"
    echo "• RAG API Redoc: http://localhost:8005/redoc"
}

# Function to run health checks
health_check() {
    echo -e "${BLUE}Running health checks...${NC}"
    
    local services=(
        "http://localhost:8005/health:Enhanced RAG Service"
        "http://localhost:8000/api/v1/heartbeat:ChromaDB"
        "http://localhost:9200/_cluster/health:Elasticsearch"
        "http://localhost:9000/minio/health/live:MinIO"
    )
    
    for service in "${services[@]}"; do
        local url="${service%%:*}"
        local name="${service##*:}"
        
        if curl -f "$url" > /dev/null 2>&1; then
            print_status "$name is healthy"
        else
            print_warning "$name health check failed"
        fi
    done
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  build     Build Docker images"
    echo "  start     Start all services"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  status    Show service status"
    echo "  health    Run health checks"
    echo "  logs      Show service logs"
    echo "  clean     Clean up containers and volumes"
    echo ""
    echo "Options:"
    echo "  --all-services    Build all services (not just RAG enhanced)"
    echo "  --no-cache        Build without using Docker cache"
    echo "  --help            Show this help message"
}

# Main script logic
main() {
    local command="${1:-build}"
    
    case "$command" in
        "build")
            check_dependencies
            create_directories
            create_env_file
            create_monitoring_config
            validate_compose
            build_images
            ;;
        "start")
            start_services
            show_status
            health_check
            ;;
        "stop")
            cd "$PROJECT_ROOT"
            docker-compose -f docker-compose.rag-enhanced.yml down
            print_status "Services stopped"
            ;;
        "restart")
            cd "$PROJECT_ROOT"
            docker-compose -f docker-compose.rag-enhanced.yml down
            docker-compose -f docker-compose.rag-enhanced.yml up -d
            print_status "Services restarted"
            ;;
        "status")
            show_status
            ;;
        "health")
            health_check
            ;;
        "logs")
            cd "$PROJECT_ROOT"
            docker-compose -f docker-compose.rag-enhanced.yml logs -f
            ;;
        "clean")
            cd "$PROJECT_ROOT"
            docker-compose -f docker-compose.rag-enhanced.yml down -v --remove-orphans
            docker system prune -f
            print_status "Cleanup completed"
            ;;
        "help"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all-services)
            BUILD_ALL_SERVICES=true
            shift
            ;;
        --no-cache)
            DOCKER_BUILD_OPTIONS="--no-cache"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

# Run main function
main "$@"