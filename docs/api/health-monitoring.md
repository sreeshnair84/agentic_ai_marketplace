# Health Monitoring and Service Discovery

## Overview

The Agentic AI Acceleration implements comprehensive health monitoring and service discovery capabilities to ensure system reliability, performance tracking, and automated service management. This system provides real-time visibility into all platform components, external services, and their interconnections.

## Health Check Framework

### Health Check Standards

All services in the platform implement standardized health checks following the Health Check Response Format for HTTP APIs specification.

#### Standard Health Response Format

```json
{
  "status": "pass|fail|warn",
  "version": "1.0.0",
  "releaseId": "v1.2.3-abc123",
  "notes": ["Human readable notes about the health check"],
  "output": "Optional output for debugging",
  "serviceId": "service-unique-identifier",
  "description": "Service description and purpose",
  "checks": {
    "component-name": [
      {
        "componentId": "database",
        "componentType": "datastore",
        "status": "pass|fail|warn",
        "time": "2024-08-14T15:30:00Z",
        "output": "Connection successful",
        "links": {
          "documentation": "https://docs.platform.com/db"
        },
        "observedValue": 5,
        "observedUnit": "connections",
        "metricName": "database.active_connections"
      }
    ]
  },
  "links": {
    "about": "https://platform.com/services/gateway",
    "documentation": "https://docs.platform.com/gateway",
    "metrics": "https://platform.com/metrics/gateway"
  }
}
```

### Service-Specific Health Implementations

#### Gateway Service Health (`http://localhost:8000/health`)

```json
{
  "status": "pass",
  "version": "1.0.0",
  "serviceId": "api-gateway",
  "description": "LCNC Platform API Gateway",
  "checks": {
    "database": [
      {
        "componentId": "postgresql",
        "componentType": "datastore", 
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "observedValue": 5,
        "observedUnit": "connections",
        "metricName": "db.pool.active_connections"
      }
    ],
    "redis": [
      {
        "componentId": "redis-cache",
        "componentType": "cache",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "observedValue": 2,
        "observedUnit": "connections",
        "metricName": "redis.active_connections"
      }
    ],
    "downstream_services": [
      {
        "componentId": "agents-service",
        "componentType": "service",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "links": {
          "health": "http://localhost:8002/health"
        }
      },
      {
        "componentId": "tools-service", 
        "componentType": "service",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "links": {
          "health": "http://localhost:8005/health"
        }
      }
    ]
  }
}
```

#### Agents Service Health (`http://localhost:8002/health`)

```json
{
  "status": "pass",
  "version": "1.0.0",
  "serviceId": "agents-service",
  "description": "A2A Protocol Agent Service",
  "checks": {
    "a2a_protocol": [
      {
        "componentId": "a2a-messaging",
        "componentType": "messaging",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "observedValue": 12,
        "observedUnit": "active_sessions",
        "metricName": "a2a.active_sessions"
      }
    ],
    "ai_providers": [
      {
        "componentId": "gemini-api",
        "componentType": "external",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "observedValue": 250,
        "observedUnit": "ms",
        "metricName": "gemini.response_time"
      }
    ],
    "agent_cards": [
      {
        "componentId": "agent-registry",
        "componentType": "registry",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "observedValue": 8,
        "observedUnit": "registered_agents",
        "metricName": "agents.registered_count"
      }
    ]
  }
}
```

#### Tools Service Health (`http://localhost:8005/health`)

```json
{
  "status": "pass",
  "version": "1.0.0", 
  "serviceId": "tools-service",
  "description": "MCP Tools Integration Service",
  "checks": {
    "mcp_servers": [
      {
        "componentId": "external-data-tools",
        "componentType": "mcp_server",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "links": {
          "server": "mcp://data-tools.company.com:8080"
        },
        "observedValue": 5,
        "observedUnit": "available_tools",
        "metricName": "mcp.tools.available"
      }
    ],
    "tool_execution": [
      {
        "componentId": "execution-engine",
        "componentType": "compute",
        "status": "pass",
        "time": "2024-08-14T15:30:00Z",
        "observedValue": 3,
        "observedUnit": "running_executions",
        "metricName": "tools.executions.active"
      }
    ],
    "external_apis": [
      {
        "componentId": "api-rate-limiter",
        "componentType": "rate_limiter",
        "status": "warn",
        "time": "2024-08-14T15:30:00Z",
        "output": "Approaching rate limit threshold",
        "observedValue": 85,
        "observedUnit": "percent",
        "metricName": "rate_limit.usage_percentage"
      }
    ]
  }
}
```

## Service Discovery

### DNS-Based Discovery

Each service registers with DNS for service discovery:

```yaml
# DNS Records for Service Discovery
services:
  gateway:
    dns_name: "gateway.lcnc.local"
    internal_port: 8000
    health_endpoint: "/health"
    
  agents:
    dns_name: "agents.lcnc.local"  
    internal_port: 8002
    health_endpoint: "/health"
    a2a_endpoint: "/a2a"
    
  tools:
    dns_name: "tools.lcnc.local"
    internal_port: 8005
    health_endpoint: "/health"
    mcp_endpoint: "/mcp"
    
  orchestrator:
    dns_name: "orchestrator.lcnc.local"
    internal_port: 8003
    health_endpoint: "/health"
    
  rag:
    dns_name: "rag.lcnc.local"
    internal_port: 8004
    health_endpoint: "/health"
    
  workflow-engine:
    dns_name: "workflow.lcnc.local"
    internal_port: 8007
    health_endpoint: "/health"
    
  observability:
    dns_name: "observability.lcnc.local"
    internal_port: 8008
    health_endpoint: "/health"
```

### Service Registry Schema

```json
{
  "service_registry": {
    "services": [
      {
        "service_id": "agents-service",
        "service_name": "Agents Service", 
        "service_type": "microservice",
        "version": "1.0.0",
        
        "endpoints": {
          "base_url": "http://localhost:8002",
          "dns_name": "agents.lcnc.local",
          "health_url": "http://localhost:8002/health",
          "metrics_url": "http://localhost:8002/metrics",
          "docs_url": "http://localhost:8002/docs"
        },
        
        "a2a_endpoints": {
          "cards_list": "http://localhost:8002/a2a/cards",
          "message_send": "http://localhost:8002/a2a/message/send",
          "message_stream": "http://localhost:8002/a2a/message/stream",
          "discover": "http://localhost:8002/a2a/discover"
        },
        
        "capabilities": [
          "a2a_protocol",
          "agent_execution", 
          "streaming",
          "multi_modal"
        ],
        
        "dependencies": [
          {
            "service": "postgresql",
            "type": "database",
            "required": true
          },
          {
            "service": "redis",
            "type": "cache", 
            "required": true
          },
          {
            "service": "gemini-api",
            "type": "external",
            "required": true
          }
        ],
        
        "health_check": {
          "interval_seconds": 30,
          "timeout_seconds": 5,
          "failure_threshold": 3,
          "success_threshold": 2
        },
        
        "status": "healthy|unhealthy|unknown",
        "last_health_check": "2024-08-14T15:30:00Z",
        "uptime_percentage": 99.9,
        "registered_at": "2024-08-14T10:00:00Z"
      }
    ]
  }
}
```

## Monitoring Dashboard

### Real-Time Status Dashboard

```json
{
  "dashboard_data": {
    "system_overview": {
      "total_services": 8,
      "healthy_services": 7,
      "unhealthy_services": 0,
      "warning_services": 1,
      "system_uptime": "99.8%",
      "last_updated": "2024-08-14T15:30:00Z"
    },
    
    "service_status": [
      {
        "service_id": "gateway",
        "name": "API Gateway",
        "status": "healthy",
        "response_time": "15ms",
        "uptime": "99.9%",
        "last_check": "2024-08-14T15:30:00Z",
        "active_connections": 25,
        "requests_per_minute": 150
      },
      {
        "service_id": "agents",
        "name": "Agents Service", 
        "status": "healthy",
        "response_time": "45ms",
        "uptime": "99.7%",
        "last_check": "2024-08-14T15:30:00Z",
        "active_sessions": 12,
        "agents_registered": 8
      },
      {
        "service_id": "tools",
        "name": "Tools Service",
        "status": "warning",
        "response_time": "120ms",
        "uptime": "98.5%",
        "last_check": "2024-08-14T15:30:00Z",
        "active_executions": 3,
        "mcp_servers_connected": 4
      }
    ],
    
    "external_dependencies": [
      {
        "dependency_id": "gemini-api",
        "name": "Google Gemini API",
        "type": "ai_provider",
        "status": "healthy",
        "response_time": "250ms",
        "rate_limit_remaining": 850,
        "last_check": "2024-08-14T15:30:00Z"
      },
      {
        "dependency_id": "external-mcp-server",
        "name": "External MCP Server",
        "type": "mcp_server",
        "status": "healthy", 
        "response_time": "80ms",
        "tools_available": 5,
        "last_check": "2024-08-14T15:30:00Z"
      }
    ],
    
    "performance_metrics": {
      "system_cpu_usage": 0.35,
      "system_memory_usage": 0.68,
      "database_connections": {
        "active": 15,
        "idle": 5,
        "max": 50
      },
      "redis_memory_usage": "256MB",
      "total_requests_today": 12547,
      "error_rate_today": 0.02
    },
    
    "recent_alerts": [
      {
        "id": "alert-123",
        "service": "tools-service",
        "level": "warning",
        "message": "High response time detected",
        "timestamp": "2024-08-14T15:25:00Z",
        "resolved": false
      }
    ]
  }
}
```

## Health Check API Endpoints

### Core Health Endpoints

```http
# System-wide health aggregation
GET /api/v1/health

# Detailed system health with all components
GET /api/v1/health/detailed

# Service-specific health checks
GET /api/v1/health/services/{service_id}

# External dependency health
GET /api/v1/health/dependencies

# Health check history
GET /api/v1/health/history?service={service_id}&hours=24

# Service discovery information
GET /api/v1/discovery/services

# Register service for discovery
POST /api/v1/discovery/services

# Update service information
PUT /api/v1/discovery/services/{service_id}
```

### Health Aggregation Response

```json
{
  "overall_status": "pass|fail|warn",
  "services": {
    "gateway": "pass",
    "agents": "pass", 
    "tools": "warn",
    "orchestrator": "pass",
    "rag": "pass",
    "workflow-engine": "pass",
    "observability": "pass"
  },
  "external_dependencies": {
    "postgresql": "pass",
    "redis": "pass",
    "chromadb": "pass",
    "gemini-api": "pass",
    "external-mcp-servers": "warn"
  },
  "summary": {
    "total_checks": 15,
    "passing": 13,
    "warning": 2,
    "failing": 0
  },
  "timestamp": "2024-08-14T15:30:00Z"
}
```

## Alerting and Notifications

### Alert Configuration

```json
{
  "alert_rules": [
    {
      "rule_id": "service-down",
      "name": "Service Down Alert",
      "condition": "service.status == 'fail'",
      "severity": "critical",
      "notification_channels": ["email", "slack", "webhook"],
      "throttle_minutes": 5
    },
    {
      "rule_id": "high-response-time",
      "name": "High Response Time",
      "condition": "service.response_time > 1000ms",
      "severity": "warning", 
      "notification_channels": ["slack"],
      "throttle_minutes": 15
    },
    {
      "rule_id": "rate-limit-approaching",
      "name": "API Rate Limit Warning",
      "condition": "external_service.rate_limit_usage > 0.8",
      "severity": "warning",
      "notification_channels": ["email"],
      "throttle_minutes": 30
    }
  ]
}
```

### Alert Notifications

```json
{
  "alert": {
    "id": "alert-456",
    "rule_id": "high-response-time",
    "service": "tools-service",
    "severity": "warning",
    "status": "firing|resolved",
    "message": "Tools service response time is 1.2s, exceeding threshold of 1.0s",
    "details": {
      "current_value": 1200,
      "threshold": 1000,
      "unit": "milliseconds",
      "duration": "5 minutes"
    },
    "timestamp": "2024-08-14T15:25:00Z",
    "resolved_at": null,
    "actions": [
      {
        "type": "investigate_logs",
        "url": "https://platform.com/logs?service=tools&time=15:25"
      },
      {
        "type": "check_dependencies", 
        "url": "https://platform.com/health/tools/dependencies"
      }
    ]
  }
}
```

## Observability Integration

### Metrics Collection

```http
# Prometheus metrics endpoints
GET /metrics                    # Gateway metrics
GET /agents/metrics            # Agents service metrics  
GET /tools/metrics             # Tools service metrics
GET /orchestrator/metrics      # Orchestrator metrics
```

### Tracing Integration

```json
{
  "tracing": {
    "jaeger_endpoint": "http://localhost:16686",
    "trace_sampling": 0.1,
    "service_traces": [
      {
        "service": "gateway",
        "trace_id": "trace-123",
        "spans": [
          {
            "span_id": "span-456",
            "operation": "proxy_request",
            "duration": "45ms",
            "tags": {
              "service.name": "gateway",
              "http.method": "POST",
              "http.status_code": 200
            }
          }
        ]
      }
    ]
  }
}
```

## Automated Remediation

### Self-Healing Capabilities

```json
{
  "remediation_actions": [
    {
      "trigger": "service.status == 'fail'",
      "action": "restart_service",
      "parameters": {
        "max_retries": 3,
        "retry_delay": "30s"
      }
    },
    {
      "trigger": "database.connections > 0.9 * max_connections",
      "action": "scale_connection_pool",
      "parameters": {
        "increase_by": 10
      }
    },
    {
      "trigger": "external_service.rate_limit_usage > 0.9",
      "action": "enable_rate_limiting",
      "parameters": {
        "requests_per_minute": 30
      }
    }
  ]
}
```

This comprehensive health monitoring and service discovery system ensures high availability, performance optimization, and automated issue resolution across the entire Agentic AI Acceleration.
