# Enterprise AI Multi-Agent Platform Documentation

Welcome to the comprehensive documentation for the Enterprise AI Multi-Agent Platform. This platform provides a sophisticated microservices architecture for building, managing, and orchestrating AI agents using multiple frameworks.

## 📋 Documentation Overview

This documentation is organized into four main categories:

### 🏗️ [Architecture](./architecture/)
- **[System Architecture](./architecture/system-architecture.md)** - Complete technical overview of the platform architecture, service communication patterns, and core components

### 🔧 [Backend Services](./backend-services/)
- **[Technical Specifications](./backend-services/technical-specifications.md)** - Detailed documentation of all 8 microservices, APIs, A2A protocol, and service interactions

### 🎨 [Frontend UI](./frontend-ui/)
- **[Technical Specifications](./frontend-ui/technical-specifications.md)** - Frontend architecture, React components, state management, and user interface design

### 🚀 [Infrastructure](./infrastructure/)
- **[Database and Deployment](./infrastructure/database-and-deployment.md)** - Database schema, deployment configurations, Kubernetes, Terraform, and DevOps practices

### ⚙️ [Setup Scripts](./setup-scripts/)
- **[setup-windows.ps1](./setup-scripts/setup-windows.ps1)** - PowerShell script for automated Windows setup without Docker
- **[setup-linux.sh](./setup-scripts/setup-linux.sh)** - Bash script for automated Linux/macOS setup without Docker

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - Primary backend language
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 16+** - Primary database with PGVector extension
- **Redis 7+** - Caching and A2A protocol communication

### Option 1: Docker Compose (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd lcnc-multiagent-platform

# Start all services
docker-compose up -d

# Access the platform
# Frontend: http://localhost:3000
# API: http://localhost:8000
```

### Option 2: Native Setup (No Docker)

#### Windows
```powershell
# Run the automated setup script
powershell -ExecutionPolicy Bypass -File docs/setup-scripts/setup-windows.ps1

# Start the platform
./start-platform.ps1
```

#### Linux/macOS
```bash
# Make the script executable
chmod +x docs/setup-scripts/setup-linux.sh

# Run the automated setup script
./docs/setup-scripts/setup-linux.sh

# Start the platform
./start-platform.sh
```

## 🏛️ Platform Architecture

### Service Overview
The platform consists of 8 core microservices:

| Service | Port | Purpose |
|---------|------|---------|
| **Gateway** | 8000 | API Gateway, Authentication, Request Routing |
| **Agents** | 8002 | Agent Lifecycle Management, Multi-Framework Support |
| **Orchestrator** | 8003 | Workflow Orchestration, Agent Coordination |
| **RAG** | 8004 | Retrieval-Augmented Generation, Vector Search |
| **Tools** | 8005 | External Tool Integration, Function Calling |
| **SQL Tool** | 8006 | Database Operations, Query Execution |
| **Workflow Engine** | 8007 | Complex Workflow Execution, State Management |
| **Observability** | 8008 | Monitoring, Logging, Performance Metrics |

### Key Features
- **Multi-Framework AI Support**: LangChain, CrewAI, Semantic Kernel, AutoGen
- **A2A Protocol**: JSON-RPC 2.0 based Agent-to-Agent communication
- **MCP Integration**: Model Context Protocol for enhanced agent capabilities
- **Vector Search**: PGVector for semantic search and RAG operations
- **Real-time UI**: Live agent status, workflow visualization, performance monitoring
- **Comprehensive Monitoring**: OpenTelemetry, Jaeger tracing, Prometheus metrics

## 🔗 Core Protocols

### A2A (Agent-to-Agent) Protocol
- **Standard**: JSON-RPC 2.0
- **Transport**: HTTP/WebSocket with Redis pub/sub
- **Features**: Type-safe communication, error handling, async messaging
- **Security**: JWT-based authentication, role-based access control

### MCP (Model Context Protocol)
- **Purpose**: Enhanced agent context and capabilities
- **Integration**: Seamless with existing AI frameworks
- **Features**: Context sharing, tool discovery, resource management

## 📊 Database Schema

### Core Tables
- **agents**: Agent definitions and configurations
- **agent_executions**: Execution history and results
- **workflows**: Workflow definitions and templates
- **tools**: External tool registrations and configurations
- **users**: User management and authentication
- **a2a_messages**: Agent communication logs

### Advanced Features
- **Vector Storage**: PGVector extension for embeddings
- **JSON Columns**: Flexible configuration storage
- **Performance Indexes**: Optimized for query performance
- **Audit Trail**: Comprehensive logging and tracking

## 🔧 Development

### API Testing
```bash
# Test all endpoints
cd scripts/testing
python test_all_endpoints.py

# Test specific service
python test_backend.py --service gateway
```

### Database Operations
```bash
# Run migrations
python scripts/utilities/fix_schema_mismatch.py

# Check database health
python scripts/debug/check_db.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

## 🌐 Deployment

### Local Development
- Use Docker Compose for easy local development
- All services auto-restart on code changes
- Pre-configured with sample data

### Production Deployment
- **Kubernetes**: Full K8s manifests in `infra/k8s/`
- **Terraform**: Infrastructure as Code in `infra/terraform/`
- **Monitoring**: Prometheus, Grafana, Jaeger integration
- **Security**: JWT authentication, RBAC, CORS configuration

## 🔐 Default Credentials

### Development Environment
- **Admin User**: 
  - Email: `admin@lcnc.local`
  - Password: `admin123`
- **Database**: 
  - User: `lcnc_user`
  - Password: `lcnc_password`
  - Database: `lcnc_platform`

> ⚠️ **Security Warning**: Change all default credentials in production environments!

## 📝 Configuration

### Environment Variables
Key configuration files:
- **Backend**: `.env` - Database, Redis, JWT, AI provider keys
- **Frontend**: `frontend/.env.local` - API URLs, NextAuth configuration

### AI Provider Setup
The platform supports multiple AI providers:
```bash
# OpenAI
OPENAI_API_KEY=your-openai-key

# Google AI
GOOGLE_API_KEY=your-google-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-key
```

## 🆘 Troubleshooting

### Common Issues
1. **Port Conflicts**: Ensure ports 3000, 5432, 6379, 8000-8008 are available
2. **Database Connection**: Verify PostgreSQL is running and credentials are correct
3. **Redis Connection**: Ensure Redis is running on port 6379
4. **Missing Dependencies**: Run setup scripts to install all prerequisites

### Debug Tools
- **Health Checks**: `scripts/debug/check_*.py`
- **Service Testing**: `scripts/testing/test_*.py`
- **Database Utilities**: `scripts/utilities/`

### Logs and Monitoring
- **Service Logs**: Check individual service directories
- **Database Logs**: PostgreSQL logs for query issues
- **API Monitoring**: Use `/docs` endpoints for API testing

## 📧 Support

For technical support and questions:
- Review the detailed documentation in each category
- Check the `scripts/debug/` utilities for diagnostics
- Examine service logs for specific error messages
- Use the `/docs` API endpoints for testing

## 🔄 Updates and Maintenance

### Regular Tasks
- Update AI provider API keys
- Monitor database performance
- Review agent execution logs
- Update dependencies

### Backup Procedures
- Database: Regular PostgreSQL backups
- Configuration: Version control all config files
- Logs: Rotate and archive service logs

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Platform**: Cross-platform (Windows, Linux, macOS)  
**License**: Enterprise License
