# Agent Registry Specification

## Overview

The Agent Registry is a comprehensive system for discovering and managing agents, tools, and workflows within the Agentic AI Acceleration. It provides standardized interfaces for agent registration, discovery, and execution with enhanced metadata for input/output signatures, health monitoring, and external service integration.

## Core Components

### 1. Agent Card Schema (A2A Protocol Enhanced)

#### Standard Agent Card Structure
```json
{
  "id": "unique-agent-identifier",
  "name": "Agent Display Name",
  "description": "Detailed agent description and purpose",
  "version": "1.0.0",
  "category": "Classification|Conversational|Analytics|Content|Development|Orchestration",
  
  // Communication Endpoints
  "url": "http://localhost:8002/a2a/agents/type",
  "health_url": "http://localhost:8002/health",
  "dns_name": "agent-service.domain.com",
  "card_url": "http://localhost:8002/a2a/cards/agent-name",
  
  // A2A Protocol Compliance
  "default_input_modes": ["text", "json", "file"],
  "default_output_modes": ["text", "json", "stream"],
  
  // Enhanced Capability Metadata
  "capabilities": {
    "streaming": true,
    "batch_processing": true,
    "multi_modal": true,
    "file_upload": true,
    "external_apis": true
  },
  
  // Input/Output Signatures
  "input_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Primary input query or command",
          "example": "Analyze the customer feedback data"
        },
        "context": {
          "type": "object",
          "description": "Additional context data",
          "properties": {
            "session_id": {"type": "string"},
            "user_preferences": {"type": "object"}
          }
        },
        "files": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Array of file URLs or data"
        }
      },
      "required": ["query"]
    },
    "content_types": ["application/json", "text/plain", "multipart/form-data"]
  },
  
  "output_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "result": {
          "type": "string",
          "description": "Primary response content"
        },
        "confidence": {
          "type": "number",
          "description": "Confidence score (0-1)"
        },
        "metadata": {
          "type": "object",
          "description": "Additional response metadata"
        },
        "artifacts": {
          "type": "array",
          "items": {"type": "object"},
          "description": "Generated files or data artifacts"
        }
      }
    },
    "content_types": ["application/json", "text/plain", "text/event-stream"]
  },
  
  // Skill Definitions with Enhanced Metadata
  "skills": [
    {
      "id": "skill-identifier",
      "name": "Skill Name",
      "description": "Detailed skill description",
      "tags": ["nlp", "classification", "analysis"],
      "examples": [
        {
          "description": "Classify customer inquiry",
          "input": {"query": "I need help with my billing"},
          "output": {"category": "billing", "confidence": 0.95}
        }
      ],
      "parameters": {
        "type": "object",
        "properties": {
          "mode": {
            "type": "string",
            "enum": ["fast", "accurate"],
            "default": "accurate",
            "description": "Processing mode"
          }
        }
      }
    }
  ],
  
  // Discovery and Categorization
  "tags": ["ai", "gemini", "classification", "customer-service"],
  "search_keywords": ["customer", "support", "inquiry", "routing"],
  
  // AI Provider Configuration
  "ai_provider": "gemini",
  "model_name": "gemini-1.5-pro",
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9
  },
  
  // External Service Integration
  "external_services": [
    {
      "name": "External AI Service",
      "dns_name": "api.external-service.com",
      "health_url": "https://api.external-service.com/health",
      "api_version": "v1",
      "authentication": "api_key"
    }
  ],
  
  // Health and Monitoring
  "health_check": {
    "endpoint": "/health",
    "interval_seconds": 30,
    "timeout_seconds": 5,
    "required_fields": ["status", "version", "dependencies"]
  },
  
  // Metadata
  "created_at": "2024-08-14T10:00:00Z",
  "updated_at": "2024-08-14T15:30:00Z",
  "created_by": "system",
  "organization": "LCNC Platform",
  "environment": "production"
}
```

### 2. Tool Registry Schema

#### Enhanced Tool Definition
```json
{
  "id": "tool-unique-id",
  "name": "Tool Name",
  "display_name": "Human Readable Tool Name",
  "description": "Comprehensive tool description",
  "category": "mcp|custom|api|llm|rag|workflow",
  "type": "specific-tool-type",
  "version": "1.0.0",
  
  // Endpoints and Discovery
  "endpoint_url": "https://api.tool-service.com/v1/execute",
  "dns_name": "tool-service.domain.com",
  "health_url": "https://api.tool-service.com/health",
  "documentation_url": "https://docs.tool-service.com",
  
  // Input/Output Signatures
  "input_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "description": "Action to perform",
          "enum": ["analyze", "process", "generate"],
          "example": "analyze"
        },
        "data": {
          "type": "object|string|array",
          "description": "Input data for processing",
          "example": {"text": "Sample input text"}
        },
        "options": {
          "type": "object",
          "description": "Processing options",
          "properties": {
            "format": {"type": "string", "default": "json"},
            "timeout": {"type": "integer", "default": 30}
          }
        }
      },
      "required": ["action", "data"]
    },
    "content_types": ["application/json", "text/plain", "multipart/form-data"],
    "size_limits": {
      "max_payload_size": "10MB",
      "max_file_size": "100MB"
    }
  },
  
  "output_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "success": {"type": "boolean"},
        "result": {
          "type": "object|string|array",
          "description": "Tool execution result"
        },
        "metadata": {
          "type": "object",
          "properties": {
            "execution_time": {"type": "number"},
            "tokens_used": {"type": "integer"},
            "cost": {"type": "number"}
          }
        },
        "errors": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "content_types": ["application/json", "text/plain", "application/octet-stream"]
  },
  
  // MCP Integration (if applicable)
  "mcp_config": {
    "server_name": "tool-mcp-server",
    "server_url": "mcp://tool-server:8080",
    "protocol_version": "1.0",
    "transport": "stdio|http|websocket",
    "capabilities": ["tools", "resources", "prompts"]
  },
  
  // Configuration Fields
  "configuration_fields": [
    {
      "name": "api_key",
      "type": "password",
      "required": true,
      "description": "API key for external service",
      "validation": "^[a-zA-Z0-9]{32}$"
    },
    {
      "name": "endpoint_region",
      "type": "select",
      "required": false,
      "options": ["us-east-1", "eu-west-1", "ap-southeast-1"],
      "default": "us-east-1",
      "description": "Service region"
    }
  ],
  
  // Execution Environment
  "runtime": {
    "environment": "python|nodejs|docker|native",
    "requirements": ["python>=3.8", "requests>=2.25.0"],
    "timeout_seconds": 300,
    "memory_limit": "512MB",
    "cpu_limit": "1000m"
  },
  
  // Health and Monitoring
  "health_check": {
    "enabled": true,
    "endpoint": "/health",
    "method": "GET",
    "expected_status": 200,
    "interval_seconds": 60,
    "timeout_seconds": 10
  },
  
  // Usage Statistics
  "usage_metrics": {
    "total_executions": 1523,
    "success_rate": 0.98,
    "avg_execution_time": 2.3,
    "last_executed": "2024-08-14T15:45:00Z"
  },
  
  "tags": ["nlp", "analysis", "external-api"],
  "status": "active|inactive|error|testing",
  "created_at": "2024-08-14T10:00:00Z",
  "updated_at": "2024-08-14T15:30:00Z"
}
```

### 3. Workflow Registry Schema

#### Enhanced Workflow Definition
```json
{
  "id": "workflow-unique-id",
  "name": "Workflow Name",
  "display_name": "Human Readable Workflow Name",
  "description": "Comprehensive workflow description",
  "category": "automation|data-processing|ai-pipeline|integration",
  "version": "1.0.0",
  
  // Execution Endpoints
  "execution_url": "http://localhost:8007/workflows/execute",
  "dns_name": "workflow-engine.domain.com",
  "health_url": "http://localhost:8007/health",
  "status_url": "http://localhost:8007/workflows/{id}/status",
  
  // Input/Output Signatures
  "input_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "trigger_data": {
          "type": "object",
          "description": "Data that triggered the workflow",
          "example": {"event": "user_signup", "user_id": "123"}
        },
        "parameters": {
          "type": "object",
          "description": "Workflow execution parameters",
          "properties": {
            "mode": {"type": "string", "enum": ["sync", "async"]},
            "priority": {"type": "string", "enum": ["low", "normal", "high"]}
          }
        },
        "context": {
          "type": "object",
          "description": "Execution context",
          "properties": {
            "user_id": {"type": "string"},
            "session_id": {"type": "string"},
            "trace_id": {"type": "string"}
          }
        }
      },
      "required": ["trigger_data"]
    }
  },
  
  "output_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "execution_id": {"type": "string"},
        "status": {
          "type": "string",
          "enum": ["pending", "running", "completed", "failed", "cancelled"]
        },
        "result": {
          "type": "object",
          "description": "Workflow execution result"
        },
        "steps_completed": {"type": "integer"},
        "total_steps": {"type": "integer"},
        "execution_time": {"type": "number"},
        "artifacts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "type": {"type": "string"},
              "url": {"type": "string"}
            }
          }
        },
        "errors": {
          "type": "array",
          "items": {"type": "object"}
        }
      }
    }
  },
  
  // Workflow Steps with Enhanced Metadata
  "steps": [
    {
      "id": "step-1",
      "name": "Data Validation",
      "type": "agent|tool|workflow|condition",
      "agent_id": "validator-agent",
      "input_mapping": {
        "data": "$.trigger_data",
        "schema": "$.parameters.validation_schema"
      },
      "output_mapping": {
        "validated_data": "$.result.data",
        "validation_errors": "$.result.errors"
      },
      "error_handling": {
        "retry_count": 3,
        "retry_delay": 5,
        "on_failure": "skip|fail|retry"
      },
      "timeout_seconds": 30
    }
  ],
  
  // Triggers and Scheduling
  "triggers": [
    {
      "type": "webhook|schedule|event|manual",
      "config": {
        "webhook_url": "/webhooks/workflow-id",
        "cron_schedule": "0 9 * * MON-FRI",
        "event_pattern": "user.created"
      }
    }
  ],
  
  // Dependencies and Requirements
  "dependencies": {
    "agents": ["customer-classifier", "support-assistant"],
    "tools": ["email-parser", "sentiment-analyzer"],
    "external_services": ["crm-api", "notification-service"]
  },
  
  "tags": ["customer-service", "automation", "ai"],
  "status": "active|inactive|draft|testing",
  "created_at": "2024-08-14T10:00:00Z",
  "updated_at": "2024-08-14T15:30:00Z"
}
```

## API Endpoints for Registry Operations

### Agent Registry Endpoints

```http
# List all agents with filtering
GET /api/v1/registry/agents?category=classification&tags=nlp,ai&status=active

# Get specific agent card
GET /api/v1/registry/agents/{agent_id}/card

# Register new agent
POST /api/v1/registry/agents
Content-Type: application/json

# Update agent registration
PUT /api/v1/registry/agents/{agent_id}

# Health check for agent
GET /api/v1/registry/agents/{agent_id}/health

# Search agents by capabilities
POST /api/v1/registry/agents/search
{
  "query": "customer support classification",
  "capabilities": ["streaming", "multi_modal"],
  "max_results": 10
}
```

### Tool Registry Endpoints

```http
# List all tools
GET /api/v1/registry/tools?category=mcp&status=active

# Get tool schema
GET /api/v1/registry/tools/{tool_id}/schema

# Test tool execution
POST /api/v1/registry/tools/{tool_id}/test
{
  "parameters": {"query": "test input"}
}

# Register MCP tool
POST /api/v1/registry/tools/mcp
{
  "server_url": "mcp://external-server:8080",
  "tool_name": "external_tool"
}
```

### Workflow Registry Endpoints

```http
# List workflows
GET /api/v1/registry/workflows?category=automation

# Get workflow definition
GET /api/v1/registry/workflows/{workflow_id}

# Execute workflow
POST /api/v1/registry/workflows/{workflow_id}/execute
{
  "trigger_data": {...},
  "parameters": {...}
}

# Get workflow execution status
GET /api/v1/registry/workflows/executions/{execution_id}/status
```

## MCP Server Discovery and Integration

### MCP Server Registration

```json
{
  "server_name": "external-tools-server",
  "server_url": "mcp://tools.external.com:8080",
  "dns_name": "tools.external.com",
  "protocol_version": "1.0",
  "transport": "stdio|http|websocket",
  
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": false
  },
  
  "authentication": {
    "type": "api_key|oauth|none",
    "config": {
      "api_key_header": "X-API-Key",
      "api_key_env": "EXTERNAL_TOOLS_API_KEY"
    }
  },
  
  "health_check": {
    "endpoint": "/health",
    "method": "GET",
    "interval_seconds": 60
  },
  
  "discovered_tools": [
    {
      "name": "data_processor",
      "description": "Process structured data",
      "input_schema": {...},
      "output_schema": {...}
    }
  ]
}
```

### MCP Tool Discovery Endpoint

```http
POST /api/v1/registry/mcp/discover
{
  "server_url": "mcp://server:8080",
  "query": "data processing tools",
  "filters": {
    "category": ["data", "analysis"],
    "capabilities": ["batch_processing"]
  }
}
```

## Discovery and Search Features

### Semantic Search
- Natural language queries for finding appropriate agents, tools, and workflows
- Embedding-based similarity matching
- Capability-based filtering
- Usage pattern analysis

### Health Monitoring
- Continuous health checks for all registered services
- Service dependency tracking
- Performance metrics collection
- Automated failover and retry logic

### Integration Patterns
- Standardized API contracts for external services
- DNS-based service discovery
- A2A protocol compliance verification
- MCP server auto-discovery and registration

This specification provides a comprehensive framework for managing all discoverable entities within the Agentic AI Acceleration, ensuring standardized interfaces, robust health monitoring, and seamless integration capabilities.
