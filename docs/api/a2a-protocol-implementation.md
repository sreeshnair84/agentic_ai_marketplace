# A2A Protocol Implementation Guide

## Overview

The Agent-to-Agent (A2A) Protocol implementation in the Agentic AI Acceleration provides standardized communication between agents, enabling seamless orchestration, tool execution, and workflow management across heterogeneous agent systems.

## A2A Protocol Specification

### Core Protocol Components

1. **Agent Cards**: Standardized agent descriptions and capabilities
2. **JSON-RPC Communication**: Message exchange protocol
3. **Session Management**: Context-aware conversations
4. **Streaming Support**: Real-time response handling
5. **Error Handling**: Robust error management and recovery

### Agent Card Structure (Enhanced)

```json
{
  "id": "agent-unique-identifier",
  "name": "Agent Display Name",
  "description": "Comprehensive agent description and capabilities",
  "version": "1.0.0",
  
  // A2A Protocol Endpoints
  "url": "http://localhost:8002/a2a/agents/{agent_type}",
  "card_url": "http://localhost:8002/a2a/cards/{agent_name}",
  "health_url": "http://localhost:8002/health",
  "dns_name": "agents.lcnc.local",
  
  // Communication Capabilities
  "default_input_modes": ["text", "json", "multipart"],
  "default_output_modes": ["text", "json", "stream"],
  
  "capabilities": {
    "streaming": true,
    "batch_processing": true,
    "multi_modal": true,
    "file_upload": true,
    "context_aware": true,
    "tool_calling": true
  },
  
  // Enhanced Input/Output Signatures
  "input_signature": {
    "message_format": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique message identifier",
          "example": "msg-uuid-123"
        },
        "sessionId": {
          "type": "string", 
          "description": "Session identifier for context",
          "example": "session-456"
        },
        "correlationId": {
          "type": "string",
          "description": "Correlation ID for tracking",
          "example": "corr-789"
        },
        "message": {
          "type": "object",
          "properties": {
            "role": {
              "type": "string",
              "enum": ["user", "assistant", "system"],
              "description": "Message role"
            },
            "parts": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "type": {"type": "string", "enum": ["text", "file", "image", "data"]},
                  "text": {"type": "string"},
                  "file_url": {"type": "string"},
                  "mime_type": {"type": "string"},
                  "data": {"type": "object"}
                }
              },
              "description": "Message content parts"
            }
          },
          "required": ["role", "parts"]
        },
        "acceptedOutputModes": {
          "type": "array",
          "items": {"type": "string"},
          "default": ["text"],
          "description": "Accepted response formats"
        },
        "context": {
          "type": "object",
          "description": "Additional context information",
          "properties": {
            "user_preferences": {"type": "object"},
            "session_history": {"type": "array"},
            "tool_results": {"type": "array"}
          }
        }
      },
      "required": ["id", "sessionId", "message"]
    },
    "content_types": ["application/json"],
    "size_limits": {
      "max_message_size": "10MB",
      "max_context_size": "1MB"
    }
  },
  
  "output_signature": {
    "response_format": {
      "type": "object",
      "properties": {
        "id": {"type": "string", "description": "Response message ID"},
        "correlationId": {"type": "string", "description": "Original correlation ID"},
        "sessionId": {"type": "string", "description": "Session identifier"},
        "message": {
          "type": "object",
          "properties": {
            "role": {"type": "string", "enum": ["assistant"]},
            "parts": {
              "type": "array",
              "items": {"type": "object"}
            }
          }
        },
        "metadata": {
          "type": "object",
          "properties": {
            "model_used": {"type": "string"},
            "tokens_used": {"type": "integer"},
            "confidence": {"type": "number"},
            "execution_time": {"type": "number"},
            "tool_calls": {"type": "array"}
          }
        },
        "status": {
          "type": "string",
          "enum": ["success", "partial", "error", "timeout"]
        }
      }
    },
    "streaming_format": {
      "type": "object",
      "description": "Server-Sent Events format",
      "properties": {
        "event": {"type": "string", "enum": ["message", "error", "done"]},
        "data": {"type": "object"}
      }
    }
  },
  
  // Agent Skills with Enhanced Metadata
  "skills": [
    {
      "id": "customer_analysis",
      "name": "Customer Inquiry Analysis",
      "description": "Analyzes customer inquiries and provides categorization",
      "category": "analysis",
      "tags": ["nlp", "classification", "customer-service"],
      
      "input_parameters": {
        "type": "object",
        "properties": {
          "inquiry_text": {
            "type": "string",
            "description": "Customer inquiry text",
            "example": "I need help with my billing"
          },
          "customer_context": {
            "type": "object",
            "description": "Customer profile information",
            "properties": {
              "tier": {"type": "string"},
              "history": {"type": "array"}
            }
          }
        },
        "required": ["inquiry_text"]
      },
      
      "output_format": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "enum": ["billing", "technical", "general", "complaint"],
            "description": "Inquiry category"
          },
          "urgency": {
            "type": "string", 
            "enum": ["low", "medium", "high", "critical"],
            "description": "Urgency level"
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Classification confidence"
          },
          "suggested_actions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recommended next steps"
          }
        }
      },
      
      "examples": [
        {
          "description": "Billing inquiry classification",
          "input": {
            "inquiry_text": "I was charged twice for my subscription",
            "customer_context": {"tier": "premium"}
          },
          "output": {
            "category": "billing",
            "urgency": "high", 
            "confidence": 0.95,
            "suggested_actions": ["review_billing", "contact_finance"]
          }
        }
      ],
      
      "performance_metrics": {
        "average_execution_time": 1.2,
        "accuracy_rate": 0.94,
        "usage_count": 1543,
        "last_updated": "2024-08-14T15:30:00Z"
      }
    }
  ],
  
  // AI Provider Configuration
  "ai_provider": "gemini",
  "model_name": "gemini-1.5-pro",
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9,
    "frequency_penalty": 0.1
  },
  
  // External Dependencies
  "external_dependencies": [
    {
      "name": "Google Gemini API",
      "type": "ai_provider",
      "dns_name": "generativelanguage.googleapis.com",
      "health_url": "https://generativelanguage.googleapis.com/v1/models",
      "required": true
    }
  ],
  
  // Metadata
  "tags": ["ai", "gemini", "customer-service", "classification"],
  "category": "Classification",
  "author": "LCNC Platform Team",
  "organization": "LCNC Platform",
  "created_at": "2024-08-14T10:00:00Z",
  "updated_at": "2024-08-14T15:30:00Z"
}
```

## A2A Message Protocol

### JSON-RPC 2.0 Message Format

#### Request Message

```json
{
  "jsonrpc": "2.0",
  "id": "request-uuid-123",
  "method": "message/send|message/stream|agent/execute",
  "params": {
    "id": "task-uuid-456",
    "sessionId": "session-789",
    "correlationId": "corr-abc",
    "acceptedOutputModes": ["text", "json"],
    "timeout": 30,
    "priority": "normal",
    
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Analyze this customer inquiry: 'I need help with my billing'"
        }
      ]
    },
    
    "context": {
      "user_id": "user-123",
      "conversation_history": [
        {
          "role": "user", 
          "content": "Previous message",
          "timestamp": "2024-08-14T15:25:00Z"
        }
      ],
      "user_preferences": {
        "language": "en",
        "response_style": "concise"
      }
    }
  }
}
```

#### Success Response

```json
{
  "jsonrpc": "2.0",
  "id": "request-uuid-123",
  "result": {
    "id": "response-uuid-789",
    "correlationId": "corr-abc",
    "sessionId": "session-789",
    "status": "success",
    
    "message": {
      "role": "assistant",
      "parts": [
        {
          "type": "text",
          "text": "Based on my analysis, this is a billing inquiry with high urgency."
        },
        {
          "type": "data",
          "data": {
            "category": "billing",
            "urgency": "high",
            "confidence": 0.95,
            "suggested_actions": ["review_billing", "contact_finance"]
          }
        }
      ]
    },
    
    "metadata": {
      "model_used": "gemini-1.5-pro",
      "tokens_used": 150,
      "execution_time": 1.2,
      "confidence": 0.95,
      "tool_calls": [],
      "timestamp": "2024-08-14T15:30:00Z"
    }
  }
}
```

#### Error Response

```json
{
  "jsonrpc": "2.0",
  "id": "request-uuid-123",
  "error": {
    "code": -32001,
    "message": "Agent execution failed",
    "data": {
      "error_type": "timeout",
      "details": "Request timed out after 30 seconds",
      "retry_after": 60,
      "correlation_id": "corr-abc",
      "session_id": "session-789"
    }
  }
}
```

### Streaming Response Format

For streaming responses, the server uses Server-Sent Events (SSE):

```
data: {"event": "start", "data": {"id": "response-uuid-789", "sessionId": "session-789"}}

data: {"event": "message", "data": {"type": "text", "text": "Based on my analysis"}}

data: {"event": "message", "data": {"type": "text", "text": ", this appears to be"}}

data: {"event": "message", "data": {"type": "text", "text": " a billing inquiry."}}

data: {"event": "data", "data": {"category": "billing", "confidence": 0.95}}

data: {"event": "done", "data": {"status": "success", "metadata": {"tokens_used": 150}}}
```

## A2A Protocol Endpoints

### Agent Discovery Endpoints

```http
# List all available agent cards
GET /a2a/cards
Response: Array of agent card objects

# Get specific agent card
GET /a2a/cards/{agent_name}
Response: Single agent card object

# Discover agents by query
POST /a2a/discover
{
  "query": "customer support classification",
  "capabilities": ["streaming", "multi_modal"],
  "tags": ["customer-service", "nlp"],
  "max_results": 5
}
Response: Array of matching agent cards

# Search agents by skills
POST /a2a/agents/search
{
  "skill_query": "analyze customer inquiries",
  "skill_categories": ["analysis", "classification"],
  "filters": {
    "ai_provider": "gemini",
    "response_time": "< 2s"
  }
}
```

### Message Communication Endpoints

```http
# Send synchronous message
POST /a2a/message/send
Content-Type: application/json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "method": "message/send",
  "params": {...}
}

# Send streaming message
POST /a2a/message/stream
Content-Type: application/json
Accept: text/event-stream
{
  "jsonrpc": "2.0", 
  "id": "req-456",
  "method": "message/stream",
  "params": {...}
}

# Execute agent-specific task
POST /a2a/agents/{agent_type}
Content-Type: application/json
{
  "id": "task-789",
  "sessionId": "session-123",
  "message": {...},
  "context": {...}
}
```

### Session Management Endpoints

```http
# Create new session
POST /a2a/sessions
{
  "user_id": "user-123",
  "agent_id": "customer-classifier",
  "context": {
    "language": "en",
    "domain": "customer-service"
  }
}

# Get session information
GET /a2a/sessions/{session_id}

# Update session context
PUT /a2a/sessions/{session_id}/context
{
  "additional_context": {
    "customer_tier": "premium"
  }
}

# End session
DELETE /a2a/sessions/{session_id}
```

## Agent Implementation Examples

### Basic Agent Implementation

```python
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import asyncio
import json

app = FastAPI(title="Customer Classifier Agent")

@app.post("/a2a/agents/classifier")
async def handle_a2a_message(request: Dict[str, Any]):
    """Handle A2A protocol message"""
    try:
        # Extract message content
        message = request.get("message", {})
        parts = message.get("parts", [])
        session_id = request.get("sessionId")
        
        # Find text content
        text_content = ""
        for part in parts:
            if part.get("type") == "text":
                text_content += part.get("text", "")
        
        # Process with AI provider (Gemini)
        result = await classify_inquiry(text_content)
        
        # Format A2A response
        response = {
            "id": f"response-{uuid.uuid4()}",
            "correlationId": request.get("correlationId"),
            "sessionId": session_id,
            "status": "success",
            "message": {
                "role": "assistant",
                "parts": [
                    {
                        "type": "text",
                        "text": f"Classification: {result['category']}"
                    },
                    {
                        "type": "data",
                        "data": result
                    }
                ]
            },
            "metadata": {
                "model_used": "gemini-1.5-pro",
                "execution_time": result.get("execution_time"),
                "confidence": result.get("confidence")
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def classify_inquiry(text: str) -> Dict[str, Any]:
    """Classify customer inquiry using Gemini"""
    # Implementation details...
    return {
        "category": "billing",
        "urgency": "high", 
        "confidence": 0.95,
        "execution_time": 1.2
    }
```

### Streaming Agent Implementation

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

@app.post("/a2a/message/stream")
async def stream_a2a_response(request: Dict[str, Any]):
    """Handle streaming A2A message"""
    
    async def generate_stream():
        session_id = request.get("sessionId")
        
        # Send start event
        yield f"data: {json.dumps({'event': 'start', 'data': {'sessionId': session_id}})}\n\n"
        
        # Process and stream response
        async for chunk in process_streaming_response(request):
            yield f"data: {json.dumps({'event': 'message', 'data': chunk})}\n\n"
        
        # Send completion event
        yield f"data: {json.dumps({'event': 'done', 'data': {'status': 'success'}})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

## Error Handling and Recovery

### Error Codes

```json
{
  "error_codes": {
    "-32001": "Agent execution failed",
    "-32002": "Invalid session",
    "-32003": "Timeout exceeded", 
    "-32004": "Rate limit exceeded",
    "-32005": "Agent unavailable",
    "-32006": "Invalid input format",
    "-32007": "Authentication required",
    "-32008": "Capability not supported"
  }
}
```

### Retry Logic

```python
async def send_a2a_message_with_retry(
    agent_url: str,
    message: Dict[str, Any],
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> Dict[str, Any]:
    """Send A2A message with exponential backoff retry"""
    
    for attempt in range(max_retries + 1):
        try:
            response = await send_a2a_message(agent_url, message)
            return response
            
        except TimeoutError:
            if attempt == max_retries:
                raise
            
            delay = backoff_factor ** attempt
            await asyncio.sleep(delay)
            
        except Exception as e:
            if attempt == max_retries:
                raise
                
            # Exponential backoff
            delay = backoff_factor ** attempt
            await asyncio.sleep(delay)
```

## Integration Patterns

### Orchestrator Integration

```python
class A2AOrchestrator:
    """Orchestrator for A2A agent communication"""
    
    async def execute_workflow(self, workflow_def: Dict[str, Any]):
        """Execute workflow using A2A agents"""
        
        results = {}
        
        for step in workflow_def["steps"]:
            if step["type"] == "agent":
                # Send A2A message to agent
                agent_card = await self.get_agent_card(step["agent_id"])
                
                message = {
                    "id": f"task-{uuid.uuid4()}",
                    "sessionId": workflow_def["session_id"],
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": step["input"]}]
                    }
                }
                
                result = await self.send_a2a_message(
                    agent_card["url"], 
                    message
                )
                
                results[step["id"]] = result
                
        return results
```

### Tool Integration

```python
class A2AToolAgent:
    """Agent that integrates with MCP tools"""
    
    async def handle_tool_request(self, request: Dict[str, Any]):
        """Handle request that requires tool execution"""
        
        # Extract tool requirements from message
        message_text = self.extract_text(request["message"])
        
        # Determine required tools
        tools = await self.select_tools(message_text)
        
        results = []
        for tool in tools:
            # Execute tool via MCP
            tool_result = await self.mcp_client.execute_tool(
                tool["server"], 
                tool["name"],
                tool["parameters"]
            )
            results.append(tool_result)
        
        # Generate response using tool results
        response = await self.generate_response(message_text, results)
        
        return self.format_a2a_response(request, response)
```

This comprehensive A2A Protocol implementation ensures standardized, reliable, and scalable communication between all agents in the Agentic AI Acceleration while maintaining compatibility with external A2A-compliant systems.
