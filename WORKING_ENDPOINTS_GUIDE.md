# LCNC Multi-Agent Platform - Working Endpoints Quick Reference

## 🟢 Confirmed Working Endpoints

### Gateway Service (Port 8000)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /health/detailed           # Detailed health
GET  /api/v1/projects           # List projects
GET  /api/v1/projects/default   # Get default project
POST /api/v1/projects           # Create project
GET  /api/v1/projects/{id}      # Get specific project
GET  /api/v1/tools              # List tools (proxy)
GET  /api/tools                 # List tools (legacy)
```

### Agents Service (Port 8002)  
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /a2a/cards                 # A2A agent cards
```

### Orchestrator Service (Port 8003)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /ready                     # Readiness probe
GET  /live                      # Liveness probe
GET  /api/v1/workflows          # List workflows
GET  /api/v1/agents             # List agents
GET  /api/v1/tasks              # List tasks
POST /api/v1/tasks              # Create task
GET  /a2a/agents                # A2A agents
GET  /a2a/sessions              # A2A sessions
```

### RAG Service (Port 8004)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /models                    # List models
POST /models/reload             # Reload models
POST /documents                 # Index document
```

### Tools Service (Port 8005)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /tools                     # List tools
GET  /tools/templates           # Tool templates
GET  /tools/categories          # Tool categories
GET  /tools/mcp                 # MCP tools
```

### SQLTool Service (Port 8006)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /connections               # Database connections
```

### Workflow Engine (Port 8007)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /workflows                 # List workflows
GET  /executions                # List executions
```

### Observability Service (Port 8008)
```
GET  /                          # Service info
GET  /health                    # Health check
GET  /metrics                   # Prometheus metrics
GET  /logs                      # Service logs
GET  /traces                    # Trace data
```

## 🔧 Usage Examples

### Create a Project
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Test project",
    "settings": {"environment": "development"}
  }'
```

### Get Available Tools  
```bash
curl http://localhost:8000/api/v1/tools
# or
curl http://localhost:8005/tools
```

### Check Service Health
```bash
# Individual services
curl http://localhost:8000/health  # Gateway
curl http://localhost:8002/health  # Agents
curl http://localhost:8003/health  # Orchestrator
curl http://localhost:8004/health  # RAG
curl http://localhost:8005/health  # Tools
curl http://localhost:8006/health  # SQLTool
curl http://localhost:8007/health  # Workflow
curl http://localhost:8008/health  # Observability

# Detailed gateway health
curl http://localhost:8000/health/detailed
```

### Create a Task
```bash
curl -X POST http://localhost:8003/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text_processing",
    "input": {"text": "Hello World"},
    "priority": "normal"
  }'
```

### Index a Document (RAG)
```bash
curl -X POST http://localhost:8004/documents \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test document for indexing.",
    "metadata": {
      "title": "Test Document",
      "source": "API",
      "tags": ["test"]
    }
  }'
```

### Get A2A Agent Cards
```bash
curl http://localhost:8002/a2a/cards
```

### Get System Metrics
```bash
curl http://localhost:8008/metrics
```

## 📊 Service Feature Matrix

| Service | Health | List | Create | Update | Delete | Special Features |
|---------|--------|------|--------|--------|--------|------------------|
| Gateway | ✅ | ✅ Projects | ✅ Projects | 🔄 | 🔄 | Proxy, Routing |
| Agents | ✅ | 🔄 | 🔄 | 🔄 | 🔄 | A2A Cards |
| Orchestrator | ✅ | ✅ Multi | ✅ Tasks | 🔄 | 🔄 | Ready/Live Probes |
| RAG | ✅ | ✅ Models | ✅ Documents | 🔄 | 🔄 | Model Management |
| Tools | ✅ | ✅ Tools | 🔄 | 🔄 | 🔄 | MCP Integration |
| SQLTool | ✅ | ✅ Connections | 🔄 | 🔄 | 🔄 | DB Management |
| Workflow | ✅ | ✅ Basic | 🔄 | 🔄 | 🔄 | Execution Tracking |
| Observability | ✅ | ✅ Logs/Metrics | 🔄 | 🔄 | 🔄 | Monitoring Stack |

**Legend:**
- ✅ Fully working
- 🔄 Partially working or needs attention
- ❌ Not working

## 🚀 Quick Test Commands

Test all core endpoints quickly:
```bash
# Basic health check across all services
for port in 8000 8002 8003 8004 8005 8006 8007 8008; do
  echo "Testing port $port..."
  curl -s http://localhost:$port/health | jq '.status' || echo "Failed"
done

# Test basic functionality
curl -s http://localhost:8000/api/v1/projects | jq 'length'
curl -s http://localhost:8005/tools | jq 'length'  
curl -s http://localhost:8003/api/v1/workflows | jq 'length'
curl -s http://localhost:8004/models | jq '.llm_models | keys | length'
```

## 📝 Notes

- All endpoints support CORS
- JSON content-type required for POST requests
- Most services return JSON responses
- Health endpoints provide service-specific status information
- Services are designed for development/testing (CORS: "*")

---

*Last updated: 2025-08-16*  
*Platform status: Core functionality operational*
