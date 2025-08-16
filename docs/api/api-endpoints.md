# API Endpoints Documentation

## Overview

This document provides comprehensive API endpoint specifications for the Agentic AI Acceleration. All endpoints follow RESTful conventions and return JSON responses.

## Base URLs

- **Gateway**: `http://localhost:3000/api`
- **Agent Service**: `http://localhost:3001/api`
- **Orchestrator**: `http://localhost:3002/api`
- **Tools Service**: `http://localhost:3003/api`
- **RAG Service**: `http://localhost:3004/api`
- **SQL Tool Service**: `http://localhost:3005/api`
- **Workflow Engine**: `http://localhost:3006/api`
- **Observability**: `http://localhost:3007/api`

## Authentication

All endpoints (except health checks and auth endpoints) require authentication via JWT Bearer token.

```http
Authorization: Bearer <jwt_token>
```

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

---

## 1. Gateway Service Endpoints

### Authentication

#### POST /api/auth/login
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "refresh_token_here",
    "expiresAt": "2024-01-01T01:00:00.000Z",
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "USER"
    }
  }
}
```

#### POST /api/auth/refresh
Refresh JWT token using refresh token.

**Request Body:**
```json
{
  "refreshToken": "refresh_token_here"
}
```

#### POST /api/auth/logout
Logout user and invalidate token.

**Request Body:**
```json
{
  "token": "jwt_token_here"
}
```

#### GET /api/auth/profile
Get current user profile.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_id",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "USER",
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
}
```

### Health Check

#### GET /api/health
System health check.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": [
      {
        "name": "orchestrator",
        "status": "healthy",
        "responseTime": 50
      },
      {
        "name": "agents",
        "status": "healthy",
        "responseTime": 30
      }
    ],
    "uptime": 3600,
    "timestamp": "2024-01-01T00:00:00.000Z"
  }
}
```

---

## 2. Agent Service Endpoints

### Agent Management

#### GET /api/agents
List all agents with optional filtering.

**Query Parameters:**
- `framework` (optional): Filter by framework (langchain, llamaindex, crewai, semantic-kernel)
- `status` (optional): Filter by status (active, inactive, error)
- `skill` (optional): Filter by skill
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": "agent_id",
        "name": "Data Analyst Agent",
        "description": "Analyzes data and generates insights",
        "framework": "langchain",
        "skills": ["data_analysis", "visualization"],
        "config": {
          "model": "gpt-4",
          "temperature": 0.7,
          "maxTokens": 2000
        },
        "status": "active",
        "createdAt": "2024-01-01T00:00:00.000Z",
        "updatedAt": "2024-01-01T00:00:00.000Z"
      }
    ],
    "pagination": {
      "total": 50,
      "page": 1,
      "limit": 20,
      "totalPages": 3
    }
  }
}
```

#### POST /api/agents
Create a new agent.

**Request Body:**
```json
{
  "name": "New Agent",
  "description": "Agent description",
  "framework": "langchain",
  "skills": ["skill1", "skill2"],
  "config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "maxTokens": 2000,
    "systemPrompt": "You are a helpful assistant",
    "tools": ["tool1", "tool2"],
    "memory": true,
    "streaming": false
  }
}
```

#### GET /api/agents/{id}
Get agent details by ID.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "agent_id",
    "name": "Data Analyst Agent",
    "description": "Analyzes data and generates insights",
    "framework": "langchain",
    "skills": ["data_analysis", "visualization"],
    "config": {
      "model": "gpt-4",
      "temperature": 0.7,
      "maxTokens": 2000,
      "systemPrompt": "You are a data analyst...",
      "tools": ["sql_tool", "visualization_tool"],
      "memory": true,
      "streaming": false
    },
    "status": "active",
    "createdAt": "2024-01-01T00:00:00.000Z",
    "updatedAt": "2024-01-01T00:00:00.000Z"
  }
}
```

#### PUT /api/agents/{id}
Update agent configuration.

**Request Body:**
```json
{
  "name": "Updated Agent Name",
  "description": "Updated description",
  "config": {
    "temperature": 0.8,
    "maxTokens": 3000
  },
  "skills": ["updated_skill1", "updated_skill2"]
}
```

#### DELETE /api/agents/{id}
Delete an agent.

#### POST /api/agents/{id}/test
Test agent with sample input.

**Request Body:**
```json
{
  "input": {
    "message": "Analyze the sales data for Q4 2023",
    "context": {
      "dataSource": "sales_db",
      "timeframe": "Q4 2023"
    }
  },
  "options": {
    "streaming": false,
    "includeTrace": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Based on the Q4 2023 sales data analysis...",
    "toolCalls": [
      {
        "tool": "sql_tool",
        "input": "SELECT * FROM sales WHERE quarter = 'Q4' AND year = 2023",
        "output": "sales data results"
      }
    ],
    "usage": {
      "promptTokens": 150,
      "completionTokens": 300,
      "totalTokens": 450
    },
    "executionTime": 2500,
    "traceId": "trace_id_here"
  }
}
```

### Agent Templates

#### GET /api/agents/templates
List available agent templates.

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "template_id",
        "name": "Data Analyst Template",
        "description": "Template for data analysis agents",
        "framework": "langchain",
        "category": "analytics",
        "skills": ["data_analysis", "sql", "visualization"],
        "defaultConfig": {
          "model": "gpt-4",
          "temperature": 0.7,
          "systemPrompt": "You are a data analyst..."
        }
      }
    ]
  }
}
```

#### POST /api/agents/templates
Create a new agent template.

#### GET /api/agents/templates/{id}
Get template details.

#### PUT /api/agents/templates/{id}
Update template.

#### DELETE /api/agents/templates/{id}
Delete template.

### Skills Management

#### GET /api/agents/{id}/skills
Get agent skills.

#### PUT /api/agents/{id}/skills
Update agent skills.

**Request Body:**
```json
{
  "skills": ["skill1", "skill2", "skill3"]
}
```

---

## 3. Orchestrator Service Endpoints

### Workflow Management

#### GET /api/workflows
List all workflows.

**Query Parameters:**
- `status` (optional): Filter by status
- `createdBy` (optional): Filter by creator
- `page`, `limit`: Pagination

**Response:**
```json
{
  "success": true,
  "data": {
    "workflows": [
      {
        "id": "workflow_id",
        "name": "Data Processing Workflow",
        "description": "Processes and analyzes customer data",
        "definition": {
          "nodes": [
            {
              "id": "node1",
              "type": "agent",
              "position": { "x": 100, "y": 100 },
              "data": {
                "label": "Data Extractor",
                "agentId": "agent_id"
              }
            }
          ],
          "edges": [
            {
              "id": "edge1",
              "source": "node1",
              "target": "node2",
              "type": "default"
            }
          ]
        },
        "status": "active",
        "createdBy": "user_id",
        "createdAt": "2024-01-01T00:00:00.000Z"
      }
    ]
  }
}
```

#### POST /api/workflows
Create new workflow.

**Request Body:**
```json
{
  "name": "New Workflow",
  "description": "Workflow description",
  "definition": {
    "nodes": [],
    "edges": [],
    "variables": [],
    "triggers": []
  }
}
```

#### GET /api/workflows/{id}
Get workflow details.

#### PUT /api/workflows/{id}
Update workflow.

#### DELETE /api/workflows/{id}
Delete workflow.

#### POST /api/workflows/{id}/execute
Execute workflow.

**Request Body:**
```json
{
  "input": {
    "data": "input data",
    "parameters": {
      "param1": "value1"
    }
  },
  "options": {
    "async": true,
    "timeout": 300000
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "executionId": "execution_id",
    "status": "running",
    "startTime": "2024-01-01T00:00:00.000Z",
    "traceId": "trace_id"
  }
}
```

#### GET /api/workflows/{id}/executions
Get workflow execution history.

### Multi-Agent Orchestration

#### POST /api/orchestrate
Start multi-agent orchestration.

**Request Body:**
```json
{
  "task": "Analyze customer feedback and generate insights",
  "requiredSkills": ["nlp", "sentiment_analysis", "data_visualization"],
  "context": {
    "dataSource": "feedback_db",
    "outputFormat": "dashboard"
  },
  "options": {
    "maxAgents": 3,
    "timeout": 600000,
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "orchestration_session_id",
    "selectedAgents": [
      {
        "agentId": "agent1",
        "skills": ["nlp", "sentiment_analysis"],
        "role": "primary"
      },
      {
        "agentId": "agent2",
        "skills": ["data_visualization"],
        "role": "secondary"
      }
    ],
    "status": "initialized",
    "traceId": "trace_id"
  }
}
```

#### GET /api/orchestrate/{sessionId}
Get orchestration session status.

#### POST /api/orchestrate/{sessionId}/stop
Stop orchestration session.

### Skill-Based Routing

#### GET /api/skills
List available skills.

**Response:**
```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "name": "data_analysis",
        "description": "Analyze structured and unstructured data",
        "category": "analytics",
        "agents": ["agent1", "agent2"]
      },
      {
        "name": "nlp",
        "description": "Natural language processing tasks",
        "category": "language",
        "agents": ["agent3", "agent4"]
      }
    ]
  }
}
```

#### POST /api/skills/route
Route request to appropriate agent based on skills.

**Request Body:**
```json
{
  "task": "Extract entities from customer emails",
  "requiredSkills": ["nlp", "entity_extraction"],
  "preferredFramework": "langchain",
  "priority": "high"
}
```

---

## 4. Tools Service Endpoints

### Tool Management

#### GET /api/tools
List all tools.

**Query Parameters:**
- `type`: Filter by type (mcp, sql, rag, standard)
- `status`: Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "tools": [
      {
        "id": "tool_id",
        "name": "SQL Query Tool",
        "description": "Execute SQL queries on databases",
        "type": "sql",
        "parameters": [
          {
            "name": "query",
            "type": "string",
            "required": true,
            "description": "SQL query to execute"
          },
          {
            "name": "connectionId",
            "type": "string",
            "required": true,
            "description": "Database connection ID"
          }
        ],
        "config": {
          "timeout": 30000,
          "maxRows": 1000
        },
        "status": "active"
      }
    ]
  }
}
```

#### POST /api/tools
Register new tool.

**Request Body:**
```json
{
  "name": "Custom Tool",
  "description": "Tool description",
  "type": "standard",
  "parameters": [
    {
      "name": "input",
      "type": "string",
      "required": true,
      "description": "Input parameter"
    }
  ],
  "config": {
    "endpoint": "https://api.example.com/tool",
    "apiKey": "api_key_here"
  }
}
```

#### GET /api/tools/{id}
Get tool details.

#### PUT /api/tools/{id}
Update tool configuration.

#### DELETE /api/tools/{id}
Delete tool.

#### POST /api/tools/{id}/test
Test tool functionality.

**Request Body:**
```json
{
  "parameters": {
    "query": "SELECT * FROM users LIMIT 10",
    "connectionId": "connection_id"
  }
}
```

### MCP Integration

#### GET /api/tools/mcp
List MCP tools.

#### POST /api/tools/mcp/connect
Connect to MCP server.

**Request Body:**
```json
{
  "name": "MCP Server Name",
  "url": "ws://localhost:8080",
  "apiKey": "optional_api_key"
}
```

#### GET /api/tools/mcp/{serverId}/tools
Get tools from specific MCP server.

### Standard Tools

#### GET /api/tools/standard
List standard tools.

#### POST /api/tools/standard/{toolId}/execute
Execute standard tool.

**Request Body:**
```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

---

## 5. RAG Service Endpoints

### Document Management

#### GET /api/rag/documents
List documents.

**Query Parameters:**
- `index`: Filter by index name
- `contentType`: Filter by content type
- `page`, `limit`: Pagination

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc_id",
        "filename": "document.pdf",
        "originalName": "Original Document.pdf",
        "contentType": "application/pdf",
        "size": 1024000,
        "metadata": {
          "author": "John Doe",
          "title": "Document Title"
        },
        "embeddingModel": "text-embedding-ada-002",
        "vectorIndex": "main_index",
        "chunkCount": 50,
        "uploadedAt": "2024-01-01T00:00:00.000Z"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "limit": 20
    }
  }
}
```

#### POST /api/rag/documents
Upload document.

**Request:** Multipart form data
- `file`: Document file
- `metadata`: JSON string with metadata
- `indexName`: Target index name
- `embeddingModel`: Embedding model to use

**Response:**
```json
{
  "success": true,
  "data": {
    "documentId": "doc_id",
    "filename": "document.pdf",
    "size": 1024000,
    "chunkCount": 50,
    "processingStatus": "completed"
  }
}
```

#### GET /api/rag/documents/{id}
Get document details.

#### DELETE /api/rag/documents/{id}
Delete document.

#### POST /api/rag/documents/bulk
Bulk upload documents.

### Index Management

#### GET /api/rag/indexes
List indexes.

#### POST /api/rag/indexes
Create new index.

**Request Body:**
```json
{
  "name": "knowledge_base",
  "description": "Company knowledge base",
  "embeddingModel": "text-embedding-ada-002",
  "dimensions": 1536,
  "vectorStore": "pinecone",
  "config": {
    "metric": "cosine",
    "replicas": 1
  }
}
```

#### GET /api/rag/indexes/{id}
Get index details.

#### PUT /api/rag/indexes/{id}
Update index configuration.

#### DELETE /api/rag/indexes/{id}
Delete index.

### Search & Retrieval

#### POST /api/rag/search
Search documents.

**Request Body:**
```json
{
  "query": "What is the company policy on remote work?",
  "indexName": "policy_documents",
  "topK": 5,
  "threshold": 0.7,
  "filters": {
    "department": "HR",
    "documentType": "policy"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "documentId": "doc_id",
        "chunkId": "chunk_id",
        "content": "Remote work policy content...",
        "score": 0.95,
        "metadata": {
          "filename": "remote_work_policy.pdf",
          "page": 2,
          "section": "Remote Work Guidelines"
        }
      }
    ],
    "totalResults": 5,
    "queryTime": 150
  }
}
```

#### POST /api/rag/similarity
Similarity search.

#### POST /api/rag/qa
Question answering.

**Request Body:**
```json
{
  "question": "What are the benefits of remote work?",
  "indexName": "company_docs",
  "context": {
    "department": "HR",
    "employee_level": "all"
  },
  "model": "gpt-4",
  "maxTokens": 500
}
```

### Configuration

#### GET /api/rag/models
List available embedding models.

#### PUT /api/rag/config
Update RAG configuration.

---

## 6. SQL Tool Service Endpoints

### Database Connections

#### GET /api/sqltool/connections
List database connections.

#### POST /api/sqltool/connections
Create database connection.

**Request Body:**
```json
{
  "name": "Production Database",
  "type": "postgres",
  "host": "localhost",
  "port": 5432,
  "database": "prod_db",
  "username": "dbuser",
  "password": "password123",
  "ssl": true,
  "connectionPool": {
    "min": 2,
    "max": 10
  }
}
```

#### GET /api/sqltool/connections/{id}
Get connection details.

#### PUT /api/sqltool/connections/{id}
Update connection.

#### DELETE /api/sqltool/connections/{id}
Delete connection.

#### POST /api/sqltool/connections/{id}/test
Test database connection.

### Query Execution

#### POST /api/sqltool/query
Execute SQL query.

**Request Body:**
```json
{
  "connectionId": "connection_id",
  "query": "SELECT * FROM users WHERE created_at > $1",
  "parameters": ["2024-01-01"],
  "options": {
    "limit": 100,
    "timeout": 30000,
    "explain": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "queryId": "query_id",
    "rows": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": "2024-01-01T00:00:00.000Z"
      }
    ],
    "rowCount": 1,
    "executionTime": 45,
    "columns": [
      {
        "name": "id",
        "type": "integer"
      },
      {
        "name": "name",
        "type": "varchar"
      }
    ]
  }
}
```

#### POST /api/sqltool/explain
Explain query execution plan.

### Schema Information

#### GET /api/sqltool/schema/{connectionId}
Get database schema.

#### GET /api/sqltool/tables/{connectionId}
List database tables.

**Response:**
```json
{
  "success": true,
  "data": {
    "tables": [
      {
        "schema": "public",
        "name": "users",
        "type": "table",
        "columns": [
          {
            "name": "id",
            "type": "integer",
            "nullable": false,
            "primaryKey": true
          },
          {
            "name": "email",
            "type": "varchar",
            "nullable": false,
            "unique": true
          }
        ],
        "rowCount": 1000
      }
    ]
  }
}
```

---

## 7. Workflow Engine Endpoints

### Workflow Execution

#### POST /api/workflow-engine/execute
Execute workflow.

**Request Body:**
```json
{
  "workflowId": "workflow_id",
  "input": {
    "data": "input data",
    "variables": {
      "var1": "value1"
    }
  },
  "options": {
    "timeout": 300000,
    "priority": "normal",
    "retryPolicy": {
      "maxRetries": 3,
      "backoff": "exponential"
    }
  }
}
```

#### GET /api/workflow-engine/status/{id}
Get execution status.

#### POST /api/workflow-engine/pause/{id}
Pause execution.

#### POST /api/workflow-engine/resume/{id}
Resume execution.

#### POST /api/workflow-engine/cancel/{id}
Cancel execution.

### Templates

#### GET /api/workflow-engine/templates
List workflow templates.

#### POST /api/workflow-engine/templates
Create workflow template.

---

## 8. Observability Service Endpoints

### Tracing

#### GET /api/observability/traces
List traces.

**Query Parameters:**
- `serviceName`: Filter by service
- `operationName`: Filter by operation
- `startTime`, `endTime`: Time range
- `status`: Filter by status
- `limit`: Number of traces to return

**Response:**
```json
{
  "success": true,
  "data": {
    "traces": [
      {
        "traceId": "trace_id",
        "operationName": "agent.execute",
        "serviceName": "agent-service",
        "startTime": "2024-01-01T00:00:00.000Z",
        "endTime": "2024-01-01T00:00:05.000Z",
        "duration": 5000,
        "status": "ok",
        "spanCount": 10,
        "tags": {
          "agent.id": "agent_id",
          "agent.framework": "langchain"
        }
      }
    ]
  }
}
```

#### GET /api/observability/traces/{id}
Get trace details with spans.

#### GET /api/observability/spans
List spans.

#### GET /api/observability/spans/{id}
Get span details.

### Metrics

#### GET /api/observability/metrics
Get system metrics.

**Query Parameters:**
- `metric`: Metric name
- `startTime`, `endTime`: Time range
- `labels`: Filter by labels
- `aggregation`: Aggregation function (sum, avg, max, min)

#### GET /api/observability/metrics/agents
Get agent-specific metrics.

#### GET /api/observability/metrics/workflows
Get workflow metrics.

### Events

#### GET /api/observability/events
List events.

#### POST /api/observability/events
Create event.

#### GET /api/observability/events/stream
Event stream (Server-Sent Events).

### Health Monitoring

#### GET /api/observability/health
Get system health status.

#### GET /api/observability/health/services
Get service health status.

---

## Error Codes

### Common Error Codes
- `AUTH_REQUIRED`: Authentication required
- `AUTH_INVALID`: Invalid authentication
- `AUTH_EXPIRED`: Token expired
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Request validation failed
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INTERNAL_ERROR`: Internal server error

### Service-Specific Error Codes
- `AGENT_NOT_FOUND`: Agent not found
- `AGENT_EXECUTION_FAILED`: Agent execution failed
- `WORKFLOW_INVALID`: Invalid workflow definition
- `TOOL_UNAVAILABLE`: Tool is unavailable
- `DATABASE_CONNECTION_FAILED`: Database connection failed
- `DOCUMENT_PROCESSING_FAILED`: Document processing failed

## Rate Limiting

All endpoints are subject to rate limiting:
- **Default**: 100 requests per 15 minutes per IP
- **Authenticated**: 1000 requests per 15 minutes per user
- **Premium**: 5000 requests per 15 minutes per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

This comprehensive API documentation provides all the endpoints needed for the Agentic AI Acceleration, allowing teams to implement both frontend and backend components effectively.
