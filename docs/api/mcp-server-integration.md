# MCP Server Integration Guide

## Overview

The Model Context Protocol (MCP) server integration enables seamless discovery and execution of external tools within the Agentic AI Acceleration. This guide provides comprehensive information for registering, discovering, and utilizing MCP servers and their tools.

## MCP Server Architecture

### Core Components

1. **MCP Registry Service**: Central registry for MCP server management
2. **Tool Discovery Engine**: Automated tool discovery and cataloging
3. **Execution Proxy**: Secure tool execution with monitoring
4. **Health Monitor**: Continuous health checking and status reporting

### Protocol Support

- **Transport Layers**: stdio, HTTP, WebSocket
- **Protocol Versions**: 1.0+
- **Capabilities**: tools, resources, prompts, sampling
- **Authentication**: API Key, OAuth 2.0, mTLS, None

## MCP Server Registration

### Registration Schema

```json
{
  "server_id": "unique-server-identifier",
  "name": "Human Readable Server Name",
  "description": "Comprehensive server description",
  "version": "1.0.0",
  
  // Connection Information
  "server_url": "mcp://hostname:port",
  "dns_name": "mcp-server.domain.com",
  "transport": "stdio|http|websocket",
  "protocol_version": "1.0",
  
  // Health and Monitoring
  "health_url": "https://mcp-server.domain.com/health",
  "status_url": "https://mcp-server.domain.com/status", 
  "metrics_url": "https://mcp-server.domain.com/metrics",
  
  // Capabilities Declaration
  "capabilities": {
    "tools": {
      "listChanged": true,
      "supportsProgress": true
    },
    "resources": {
      "subscribe": true,
      "listChanged": true
    },
    "prompts": {
      "listChanged": false
    },
    "sampling": {},
    "experimental": {
      "customProtocol": true
    }
  },
  
  // Authentication Configuration
  "authentication": {
    "type": "api_key|oauth|mtls|none",
    "config": {
      "api_key_header": "X-API-Key",
      "api_key_env_var": "MCP_SERVER_API_KEY",
      "oauth_endpoint": "https://auth.server.com/oauth/token",
      "client_id_env": "MCP_CLIENT_ID",
      "client_secret_env": "MCP_CLIENT_SECRET",
      "scopes": ["tools:read", "tools:execute"]
    }
  },
  
  // Discovery Configuration  
  "discovery": {
    "auto_discover_tools": true,
    "discovery_interval_seconds": 300,
    "tool_categories": ["data", "ai", "integration", "utility"],
    "max_tools": 100
  },
  
  // Execution Settings
  "execution": {
    "timeout_seconds": 300,
    "max_concurrent_executions": 10,
    "retry_policy": {
      "max_retries": 3,
      "retry_delay_seconds": 5,
      "backoff_multiplier": 2.0
    },
    "rate_limiting": {
      "requests_per_minute": 60,
      "burst_size": 10
    }
  },
  
  // Health Check Configuration
  "health_check": {
    "enabled": true,
    "endpoint": "/health",
    "method": "GET", 
    "interval_seconds": 30,
    "timeout_seconds": 10,
    "failure_threshold": 3,
    "success_threshold": 2,
    "expected_response": {
      "status_code": 200,
      "required_fields": ["status", "version"]
    }
  },
  
  // Metadata
  "tags": ["external", "mcp", "tools"],
  "organization": "External Provider",
  "contact_email": "support@provider.com",
  "documentation_url": "https://docs.provider.com/mcp",
  "created_at": "2024-08-14T10:00:00Z",
  "updated_at": "2024-08-14T15:30:00Z",
  "status": "active|inactive|error|testing"
}
```

### Registration API

```http
POST /api/v1/mcp/servers
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "name": "External Data Tools",
  "server_url": "mcp://data-tools.company.com:8080",
  "dns_name": "data-tools.company.com",
  "authentication": {
    "type": "api_key",
    "config": {
      "api_key_header": "X-API-Key",
      "api_key_env_var": "DATA_TOOLS_API_KEY"
    }
  }
}
```

## Tool Discovery and Cataloging

### Automatic Tool Discovery

When an MCP server is registered, the system automatically discovers available tools:

```json
{
  "discovery_request": {
    "jsonrpc": "2.0",
    "id": "discovery-123",
    "method": "tools/list",
    "params": {}
  },
  
  "discovery_response": {
    "jsonrpc": "2.0", 
    "id": "discovery-123",
    "result": {
      "tools": [
        {
          "name": "data_processor",
          "description": "Process and transform structured data",
          "inputSchema": {
            "type": "object",
            "properties": {
              "data": {
                "type": "array",
                "description": "Array of data objects to process",
                "example": [{"id": 1, "value": "test"}]
              },
              "operation": {
                "type": "string",
                "enum": ["filter", "transform", "aggregate"],
                "description": "Processing operation to perform",
                "example": "transform"
              },
              "options": {
                "type": "object",
                "properties": {
                  "format": {"type": "string", "default": "json"},
                  "include_metadata": {"type": "boolean", "default": false}
                }
              }
            },
            "required": ["data", "operation"]
          }
        }
      ]
    }
  }
}
```

### Tool Metadata Enhancement

Discovered tools are enhanced with additional metadata:

```json
{
  "tool_id": "mcp-server-name::tool-name",
  "server_id": "external-data-tools",
  "original_name": "data_processor",
  "display_name": "Data Processor",
  "description": "Process and transform structured data",
  
  // Enhanced Input/Output Signatures
  "input_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "data": {
          "type": "array",
          "description": "Array of data objects to process",
          "example": [{"id": 1, "value": "test"}],
          "validation": {
            "min_items": 1,
            "max_items": 1000
          }
        },
        "operation": {
          "type": "string",
          "enum": ["filter", "transform", "aggregate"],
          "description": "Processing operation to perform"
        }
      },
      "required": ["data", "operation"]
    },
    "content_types": ["application/json"],
    "size_limits": {
      "max_payload_size": "10MB"
    },
    "examples": [
      {
        "name": "Transform customer data",
        "input": {
          "data": [{"name": "John", "age": 30}],
          "operation": "transform",
          "options": {"format": "csv"}
        }
      }
    ]
  },
  
  "output_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "result": {
          "type": "array|object|string",
          "description": "Processed data result"
        },
        "metadata": {
          "type": "object",
          "properties": {
            "processed_count": {"type": "integer"},
            "processing_time": {"type": "number"},
            "format": {"type": "string"}
          }
        },
        "errors": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "content_types": ["application/json", "text/csv", "text/plain"]
  },
  
  // Execution Metadata
  "execution_info": {
    "average_execution_time": 2.5,
    "success_rate": 0.95,
    "last_executed": "2024-08-14T15:45:00Z",
    "total_executions": 1523
  },
  
  // Discovery Metadata
  "discovered_at": "2024-08-14T10:00:00Z",
  "last_updated": "2024-08-14T15:30:00Z",
  "discovery_source": "auto|manual",
  "tags": ["data", "processing", "transform"],
  "category": "data-processing",
  "status": "available|unavailable|deprecated"
}
```

## Tool Execution

### Execution Request

```http
POST /api/v1/mcp/tools/{tool_id}/execute
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "execution_id": "exec-uuid-123",
  "parameters": {
    "data": [{"customer": "John", "order": 100}],
    "operation": "transform",
    "options": {"format": "json"}
  },
  "context": {
    "user_id": "user-123",
    "session_id": "session-456", 
    "trace_id": "trace-789"
  },
  "execution_options": {
    "timeout_seconds": 60,
    "async": false,
    "callback_url": "https://platform.com/callbacks/tool-execution"
  }
}
```

### Execution Response

```json
{
  "execution_id": "exec-uuid-123",
  "tool_id": "external-data-tools::data_processor",
  "status": "completed|running|failed|timeout",
  "started_at": "2024-08-14T15:30:00Z",
  "completed_at": "2024-08-14T15:30:02Z",
  "execution_time": 2.1,
  
  "result": {
    "success": true,
    "data": [
      {"customer": "John", "order": 100, "processed": true}
    ],
    "metadata": {
      "processed_count": 1,
      "processing_time": 2.1,
      "format": "json"
    }
  },
  
  "trace_info": {
    "trace_id": "trace-789",
    "span_id": "span-abc",
    "logs": [
      {"level": "INFO", "message": "Starting data processing", "timestamp": "2024-08-14T15:30:00Z"},
      {"level": "INFO", "message": "Processing completed successfully", "timestamp": "2024-08-14T15:30:02Z"}
    ]
  },
  
  "usage_metrics": {
    "tokens_used": 150,
    "cost_usd": 0.001,
    "rate_limit_remaining": 59
  },
  
  "error": null
}
```

## Health Monitoring and Status

### Health Check Implementation

```json
{
  "health_check_result": {
    "server_id": "external-data-tools",
    "status": "healthy|degraded|unhealthy",
    "checked_at": "2024-08-14T15:30:00Z",
    "response_time_ms": 45,
    
    "checks": {
      "connectivity": {
        "status": "healthy",
        "details": "Successfully connected to MCP server"
      },
      "authentication": {
        "status": "healthy", 
        "details": "API key authentication successful"
      },
      "tools_availability": {
        "status": "healthy",
        "details": "All 5 tools responding normally"
      },
      "resource_usage": {
        "status": "healthy",
        "details": {
          "cpu_usage": 0.3,
          "memory_usage": 0.6,
          "active_connections": 2
        }
      }
    },
    
    "capabilities_check": {
      "tools": {"available": true, "count": 5},
      "resources": {"available": true, "count": 3},
      "prompts": {"available": false, "count": 0}
    },
    
    "historical_metrics": {
      "uptime_percentage": 99.9,
      "average_response_time": 2.3,
      "success_rate": 0.95,
      "last_failure": "2024-08-10T08:15:00Z"
    }
  }
}
```

### Status Dashboard Data

```json
{
  "dashboard_data": {
    "total_servers": 12,
    "active_servers": 11,
    "total_tools": 47,
    "available_tools": 45,
    
    "servers": [
      {
        "id": "external-data-tools",
        "name": "External Data Tools",
        "status": "healthy",
        "tools_count": 5,
        "last_check": "2024-08-14T15:30:00Z",
        "uptime": "99.9%",
        "response_time": "45ms"
      }
    ],
    
    "recent_executions": [
      {
        "tool_name": "data_processor",
        "server_name": "External Data Tools", 
        "status": "completed",
        "execution_time": 2.1,
        "timestamp": "2024-08-14T15:30:00Z"
      }
    ],
    
    "metrics_summary": {
      "total_executions_today": 156,
      "success_rate_today": 0.97,
      "average_execution_time": 2.8,
      "most_used_tool": "data_processor"
    }
  }
}
```

## API Endpoints

### MCP Server Management

```http
# List all MCP servers
GET /api/v1/mcp/servers?status=active&capabilities=tools

# Get specific server details
GET /api/v1/mcp/servers/{server_id}

# Register new MCP server
POST /api/v1/mcp/servers

# Update server configuration 
PUT /api/v1/mcp/servers/{server_id}

# Delete server registration
DELETE /api/v1/mcp/servers/{server_id}

# Test server connectivity
POST /api/v1/mcp/servers/{server_id}/test

# Get server health status
GET /api/v1/mcp/servers/{server_id}/health

# Trigger tool discovery
POST /api/v1/mcp/servers/{server_id}/discover
```

### Tool Discovery and Execution

```http
# List discovered tools
GET /api/v1/mcp/tools?server_id={server_id}&category=data

# Get tool details and schema
GET /api/v1/mcp/tools/{tool_id}

# Execute tool
POST /api/v1/mcp/tools/{tool_id}/execute

# Get execution status
GET /api/v1/mcp/executions/{execution_id}

# Get execution history
GET /api/v1/mcp/tools/{tool_id}/executions?limit=10

# Search tools by capability
POST /api/v1/mcp/tools/search
{
  "query": "data processing",
  "capabilities": ["batch_processing"],
  "servers": ["external-data-tools"]
}
```

### Monitoring and Analytics

```http
# Get system metrics
GET /api/v1/mcp/metrics

# Get server-specific metrics  
GET /api/v1/mcp/servers/{server_id}/metrics

# Get tool usage analytics
GET /api/v1/mcp/analytics/tools?period=7d

# Export execution logs
GET /api/v1/mcp/logs/export?format=json&start_date=2024-08-01
```

## Error Handling and Troubleshooting

### Common Error Scenarios

1. **Connection Failures**
   - DNS resolution issues
   - Network timeouts
   - Authentication failures
   - Protocol version mismatches

2. **Tool Execution Errors**
   - Invalid input parameters
   - Tool unavailable
   - Execution timeouts
   - Rate limiting

3. **Discovery Issues**
   - Server not responding to discovery requests
   - Malformed tool definitions
   - Capability mismatches

### Error Response Format

```json
{
  "error": {
    "code": "MCP_CONNECTION_FAILED",
    "message": "Failed to connect to MCP server",
    "details": {
      "server_id": "external-data-tools",
      "server_url": "mcp://data-tools.company.com:8080",
      "error_type": "connection_timeout",
      "retry_count": 3,
      "last_attempt": "2024-08-14T15:30:00Z"
    },
    "resolution_steps": [
      "Check network connectivity",
      "Verify server URL and port",
      "Check authentication credentials",
      "Contact server administrator"
    ]
  }
}
```

## Security Considerations

### Authentication and Authorization
- Secure API key management using environment variables
- OAuth 2.0 flow support for enterprise integrations
- mTLS for high-security environments
- Role-based access control for tool execution

### Data Protection
- Encrypted communication channels (TLS 1.3+)
- Input validation and sanitization
- Output data filtering and redaction
- Audit logging for all operations

### Rate Limiting and Quotas
- Per-server execution limits
- User-based quotas
- Tool-specific rate limiting
- Circuit breaker patterns for failing services

This comprehensive guide ensures robust and secure integration of external MCP servers, providing full visibility into tool capabilities, health status, and execution metrics while maintaining high standards for security and reliability.
