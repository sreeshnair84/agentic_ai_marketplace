# Workflow Engine Specification

## Overview

The Workflow Engine is a core component of the Agentic AI Acceleration that orchestrates complex multi-step processes involving agents, tools, and external services. It provides visual workflow design, automated execution, error handling, and comprehensive monitoring capabilities.

## Workflow Definition Schema

### Enhanced Workflow Structure

```json
{
  "workflow_id": "workflow-unique-identifier",
  "name": "Customer Support Automation",
  "display_name": "Customer Support Processing Pipeline",
  "description": "Automated processing of customer inquiries with intelligent routing and response generation",
  "version": "2.1.0",
  "category": "customer-service",
  
  // Execution Metadata
  "execution_info": {
    "engine_url": "http://localhost:8007/workflows/execute",
    "dns_name": "workflow-engine.lcnc.local",
    "health_url": "http://localhost:8007/health",
    "status_endpoint": "http://localhost:8007/workflows/{workflow_id}/status",
    "logs_endpoint": "http://localhost:8007/workflows/{workflow_id}/logs"
  },
  
  // Input/Output Signatures
  "input_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "trigger_event": {
          "type": "object",
          "description": "Event that triggered the workflow",
          "properties": {
            "event_type": {
              "type": "string",
              "enum": ["webhook", "schedule", "manual", "api_call"],
              "description": "Type of trigger event"
            },
            "event_data": {
              "type": "object",
              "description": "Event-specific data",
              "example": {
                "customer_inquiry": "I need help with my billing",
                "customer_id": "cust-123",
                "channel": "email",
                "priority": "normal"
              }
            },
            "event_timestamp": {
              "type": "string",
              "format": "date-time",
              "description": "When the event occurred"
            }
          },
          "required": ["event_type", "event_data"]
        },
        "execution_parameters": {
          "type": "object",
          "description": "Workflow execution parameters",
          "properties": {
            "execution_mode": {
              "type": "string",
              "enum": ["sync", "async", "batch"],
              "default": "async",
              "description": "Execution mode"
            },
            "priority": {
              "type": "string",
              "enum": ["low", "normal", "high", "critical"],
              "default": "normal",
              "description": "Execution priority"
            },
            "timeout_seconds": {
              "type": "integer",
              "default": 300,
              "description": "Maximum execution time"
            },
            "retry_policy": {
              "type": "object",
              "properties": {
                "max_retries": {"type": "integer", "default": 3},
                "retry_delay": {"type": "integer", "default": 5},
                "backoff_multiplier": {"type": "number", "default": 2.0}
              }
            }
          }
        },
        "context": {
          "type": "object",
          "description": "Additional execution context",
          "properties": {
            "user_id": {"type": "string"},
            "session_id": {"type": "string"},
            "trace_id": {"type": "string"},
            "environment": {"type": "string", "enum": ["dev", "staging", "prod"]},
            "tenant_id": {"type": "string"}
          }
        }
      },
      "required": ["trigger_event"]
    },
    "examples": [
      {
        "name": "Email customer inquiry",
        "description": "Customer sent inquiry via email",
        "data": {
          "trigger_event": {
            "event_type": "webhook",
            "event_data": {
              "customer_inquiry": "I was charged twice for my subscription",
              "customer_id": "cust-456",
              "channel": "email",
              "priority": "high"
            }
          },
          "execution_parameters": {
            "execution_mode": "async",
            "priority": "high"
          }
        }
      }
    ]
  },
  
  "output_signature": {
    "schema": {
      "type": "object",
      "properties": {
        "execution_id": {
          "type": "string",
          "description": "Unique execution identifier"
        },
        "workflow_id": {
          "type": "string", 
          "description": "Workflow definition identifier"
        },
        "status": {
          "type": "string",
          "enum": ["pending", "running", "completed", "failed", "cancelled", "timeout"],
          "description": "Workflow execution status"
        },
        "result": {
          "type": "object",
          "description": "Workflow execution result",
          "properties": {
            "customer_response": {"type": "string"},
            "category": {"type": "string"},
            "resolution": {"type": "string"},
            "follow_up_required": {"type": "boolean"},
            "artifacts": {"type": "array"}
          }
        },
        "execution_metadata": {
          "type": "object",
          "properties": {
            "started_at": {"type": "string", "format": "date-time"},
            "completed_at": {"type": "string", "format": "date-time"},
            "execution_time": {"type": "number", "description": "Total execution time in seconds"},
            "steps_completed": {"type": "integer"},
            "total_steps": {"type": "integer"},
            "resources_used": {
              "type": "object",
              "properties": {
                "agents_called": {"type": "array"},
                "tools_executed": {"type": "array"},
                "ai_tokens_used": {"type": "integer"},
                "cost_usd": {"type": "number"}
              }
            }
          }
        },
        "step_results": {
          "type": "array",
          "description": "Results from each workflow step",
          "items": {
            "type": "object",
            "properties": {
              "step_id": {"type": "string"},
              "step_name": {"type": "string"},
              "status": {"type": "string"},
              "result": {"type": "object"},
              "execution_time": {"type": "number"},
              "error": {"type": "string"}
            }
          }
        },
        "errors": {
          "type": "array",
          "description": "Any errors encountered during execution",
          "items": {
            "type": "object",
            "properties": {
              "step_id": {"type": "string"},
              "error_code": {"type": "string"},
              "error_message": {"type": "string"},
              "error_details": {"type": "object"},
              "timestamp": {"type": "string", "format": "date-time"}
            }
          }
        }
      }
    }
  },
  
  // Workflow Steps Definition
  "steps": [
    {
      "step_id": "classify_inquiry",
      "step_name": "Classify Customer Inquiry",
      "step_type": "agent",
      "step_order": 1,
      "description": "Analyze and classify the customer inquiry",
      
      "agent_config": {
        "agent_id": "customer-classifier",
        "agent_url": "http://localhost:8002/a2a/agents/classifier",
        "dns_name": "agents.lcnc.local",
        "health_url": "http://localhost:8002/health"
      },
      
      "input_mapping": {
        "query": "$.trigger_event.event_data.customer_inquiry",
        "customer_context": {
          "customer_id": "$.trigger_event.event_data.customer_id",
          "channel": "$.trigger_event.event_data.channel"
        }
      },
      
      "output_mapping": {
        "category": "$.result.category",
        "urgency": "$.result.urgency", 
        "confidence": "$.result.confidence",
        "suggested_actions": "$.result.suggested_actions"
      },
      
      "error_handling": {
        "retry_count": 3,
        "retry_delay": 5,
        "timeout_seconds": 30,
        "on_failure": "continue|stop|retry|skip",
        "fallback_action": {
          "type": "default_classification",
          "params": {"category": "general", "urgency": "normal"}
        }
      },
      
      "conditions": {
        "skip_if": "$.trigger_event.event_data.category_override != null",
        "execute_if": "$.trigger_event.event_data.customer_inquiry != null"
      }
    },
    
    {
      "step_id": "sentiment_analysis",
      "step_name": "Analyze Customer Sentiment",
      "step_type": "tool",
      "step_order": 2,
      "description": "Analyze sentiment of customer inquiry",
      
      "tool_config": {
        "tool_id": "sentiment-analyzer",
        "tool_url": "http://localhost:8005/tools/sentiment-analyzer/execute",
        "dns_name": "tools.lcnc.local",
        "health_url": "http://localhost:8005/health"
      },
      
      "input_mapping": {
        "text": "$.trigger_event.event_data.customer_inquiry",
        "language": "en",
        "options": {
          "include_emotions": true,
          "confidence_threshold": 0.7
        }
      },
      
      "output_mapping": {
        "sentiment": "$.result.sentiment",
        "score": "$.result.score",
        "emotions": "$.result.emotions"
      },
      
      "parallel_execution": true,
      "depends_on": []
    },
    
    {
      "step_id": "knowledge_search",
      "step_name": "Search Knowledge Base",
      "step_type": "agent",
      "step_order": 3,
      "description": "Search for relevant information in knowledge base",
      
      "agent_config": {
        "agent_id": "rag-agent",
        "agent_url": "http://localhost:8004/rag/search",
        "dns_name": "rag.lcnc.local",
        "health_url": "http://localhost:8004/health"
      },
      
      "input_mapping": {
        "query": "$.trigger_event.event_data.customer_inquiry",
        "filters": {
          "category": "$.classify_inquiry.category",
          "language": "en"
        },
        "max_results": 5
      },
      
      "output_mapping": {
        "documents": "$.result.documents",
        "relevance_scores": "$.result.scores"
      },
      
      "depends_on": ["classify_inquiry"]
    },
    
    {
      "step_id": "generate_response",
      "step_name": "Generate Customer Response",
      "step_type": "agent",
      "step_order": 4,
      "description": "Generate personalized response for customer",
      
      "agent_config": {
        "agent_id": "response-generator",
        "agent_url": "http://localhost:8002/a2a/agents/response",
        "dns_name": "agents.lcnc.local"
      },
      
      "input_mapping": {
        "customer_inquiry": "$.trigger_event.event_data.customer_inquiry",
        "category": "$.classify_inquiry.category",
        "urgency": "$.classify_inquiry.urgency",
        "sentiment": "$.sentiment_analysis.sentiment",
        "knowledge_base_results": "$.knowledge_search.documents",
        "customer_context": {
          "customer_id": "$.trigger_event.event_data.customer_id",
          "channel": "$.trigger_event.event_data.channel"
        }
      },
      
      "output_mapping": {
        "response_text": "$.result.response",
        "confidence": "$.result.confidence",
        "follow_up_required": "$.result.follow_up_required",
        "escalation_needed": "$.result.escalation_needed"
      },
      
      "depends_on": ["classify_inquiry", "sentiment_analysis", "knowledge_search"]
    },
    
    {
      "step_id": "conditional_escalation",
      "step_name": "Conditional Escalation",
      "step_type": "condition",
      "step_order": 5,
      "description": "Escalate to human agent if needed",
      
      "condition": {
        "expression": "$.generate_response.escalation_needed == true OR $.classify_inquiry.urgency == 'critical'",
        "true_steps": ["escalate_to_human"],
        "false_steps": ["send_response"]
      }
    },
    
    {
      "step_id": "escalate_to_human",
      "step_name": "Escalate to Human Agent",
      "step_type": "workflow",
      "step_order": 6,
      "description": "Trigger human escalation workflow",
      
      "workflow_config": {
        "workflow_id": "human-escalation-workflow",
        "workflow_url": "http://localhost:8007/workflows/human-escalation/execute"
      },
      
      "input_mapping": {
        "customer_inquiry": "$.trigger_event.event_data.customer_inquiry",
        "analysis_results": {
          "category": "$.classify_inquiry.category",
          "sentiment": "$.sentiment_analysis.sentiment",
          "ai_response": "$.generate_response.response_text"
        }
      },
      
      "conditions": {
        "execute_if": "$.conditional_escalation.result == true"
      }
    },
    
    {
      "step_id": "send_response",
      "step_name": "Send Response to Customer",
      "step_type": "tool",
      "step_order": 6,
      "description": "Send the generated response to customer",
      
      "tool_config": {
        "tool_id": "communication-handler",
        "tool_url": "http://localhost:8005/tools/communication/send"
      },
      
      "input_mapping": {
        "customer_id": "$.trigger_event.event_data.customer_id",
        "channel": "$.trigger_event.event_data.channel",
        "response_text": "$.generate_response.response_text",
        "metadata": {
          "category": "$.classify_inquiry.category",
          "sentiment": "$.sentiment_analysis.sentiment"
        }
      },
      
      "conditions": {
        "execute_if": "$.conditional_escalation.result == false"
      }
    }
  ],
  
  // Workflow Triggers
  "triggers": [
    {
      "trigger_id": "email_webhook",
      "trigger_type": "webhook",
      "trigger_name": "Email Inquiry Webhook",
      "description": "Triggered when customer sends email inquiry",
      
      "webhook_config": {
        "endpoint": "/webhooks/customer-inquiry",
        "method": "POST",
        "authentication": {
          "type": "api_key",
          "header": "X-API-Key"
        }
      },
      
      "event_mapping": {
        "customer_inquiry": "$.body.message",
        "customer_id": "$.body.customer_id",
        "channel": "email"
      }
    },
    
    {
      "trigger_id": "scheduled_check",
      "trigger_type": "schedule",
      "trigger_name": "Daily Inquiry Review",
      "description": "Daily review of pending inquiries",
      
      "schedule_config": {
        "cron_expression": "0 9 * * MON-FRI",
        "timezone": "UTC",
        "enabled": true
      }
    },
    
    {
      "trigger_id": "manual_execution",
      "trigger_type": "manual",
      "trigger_name": "Manual Execution",
      "description": "Manual workflow execution via API or UI"
    }
  ],
  
  // Error Handling and Recovery
  "error_handling": {
    "global_timeout": 600,
    "global_retry_policy": {
      "max_retries": 2,
      "retry_delay": 10,
      "backoff_multiplier": 1.5
    },
    "failure_actions": [
      {
        "condition": "total_failures > 3",
        "action": "pause_workflow",
        "notification": ["admin@company.com"]
      },
      {
        "condition": "step_timeout",
        "action": "skip_step",
        "fallback": "default_response"
      }
    ],
    "circuit_breaker": {
      "failure_threshold": 5,
      "recovery_timeout": 300,
      "half_open_requests": 3
    }
  },
  
  // Performance and Resource Management
  "resource_limits": {
    "max_concurrent_executions": 10,
    "max_execution_time": 900,
    "memory_limit": "1GB",
    "cpu_limit": "2 cores"
  },
  
  // Monitoring and Observability
  "monitoring": {
    "metrics_enabled": true,
    "tracing_enabled": true,
    "logging_level": "INFO",
    "alert_thresholds": {
      "execution_time": 300,
      "error_rate": 0.05,
      "queue_depth": 100
    }
  },
  
  // Metadata
  "metadata": {
    "tags": ["customer-service", "automation", "ai", "nlp"],
    "author": "Platform Team",
    "organization": "LCNC Platform",
    "version_history": [
      {
        "version": "2.0.0",
        "changes": ["Added sentiment analysis", "Improved error handling"],
        "date": "2024-08-01T00:00:00Z"
      }
    ],
    "created_at": "2024-07-01T10:00:00Z",
    "updated_at": "2024-08-14T15:30:00Z",
    "status": "active|inactive|draft|deprecated"
  }
}
```

## Workflow Execution Engine

### Execution API Endpoints

```http
# Execute workflow
POST /api/v1/workflows/{workflow_id}/execute
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "trigger_event": {
    "event_type": "manual",
    "event_data": {
      "customer_inquiry": "I need help with my billing",
      "customer_id": "cust-123"
    }
  },
  "execution_parameters": {
    "execution_mode": "async",
    "priority": "normal"
  }
}

# Get execution status
GET /api/v1/workflows/executions/{execution_id}

# Cancel execution
DELETE /api/v1/workflows/executions/{execution_id}

# Get execution logs
GET /api/v1/workflows/executions/{execution_id}/logs

# List workflow executions
GET /api/v1/workflows/{workflow_id}/executions?status=running&limit=10
```

### Execution Response

```json
{
  "execution_id": "exec-uuid-123",
  "workflow_id": "customer-support-automation",
  "status": "completed",
  "started_at": "2024-08-14T15:30:00Z",
  "completed_at": "2024-08-14T15:32:15Z",
  "execution_time": 135.2,
  
  "result": {
    "customer_response": "Thank you for contacting us about your billing inquiry. I've reviewed your account and found that the duplicate charge was a processing error. The extra charge has been refunded and should appear in your account within 3-5 business days.",
    "category": "billing",
    "resolution": "refund_processed",
    "follow_up_required": false,
    "artifacts": [
      {
        "type": "refund_receipt",
        "url": "https://platform.com/receipts/refund-456"
      }
    ]
  },
  
  "execution_metadata": {
    "steps_completed": 6,
    "total_steps": 6,
    "resources_used": {
      "agents_called": ["customer-classifier", "response-generator"],
      "tools_executed": ["sentiment-analyzer", "communication-handler"],
      "ai_tokens_used": 450,
      "cost_usd": 0.005
    }
  },
  
  "step_results": [
    {
      "step_id": "classify_inquiry",
      "step_name": "Classify Customer Inquiry",
      "status": "completed",
      "result": {
        "category": "billing",
        "urgency": "high",
        "confidence": 0.95
      },
      "execution_time": 1.2,
      "started_at": "2024-08-14T15:30:01Z",
      "completed_at": "2024-08-14T15:30:02Z"
    }
  ]
}
```

## Visual Workflow Designer

### Workflow Designer Schema

```json
{
  "designer_config": {
    "canvas": {
      "width": 1200,
      "height": 800,
      "zoom_level": 1.0,
      "grid_enabled": true
    },
    
    "nodes": [
      {
        "node_id": "start",
        "node_type": "start",
        "position": {"x": 100, "y": 200},
        "size": {"width": 80, "height": 40},
        "label": "Start"
      },
      {
        "node_id": "classify_inquiry", 
        "node_type": "agent",
        "position": {"x": 250, "y": 200},
        "size": {"width": 150, "height": 80},
        "label": "Classify Inquiry",
        "config": {
          "agent_id": "customer-classifier",
          "icon": "classification",
          "color": "#3B82F6"
        }
      },
      {
        "node_id": "sentiment_analysis",
        "node_type": "tool", 
        "position": {"x": 250, "y": 320},
        "size": {"width": 150, "height": 80},
        "label": "Sentiment Analysis",
        "config": {
          "tool_id": "sentiment-analyzer",
          "icon": "sentiment",
          "color": "#10B981"
        }
      }
    ],
    
    "connections": [
      {
        "id": "conn-1",
        "source": "start",
        "target": "classify_inquiry",
        "source_port": "output",
        "target_port": "input",
        "style": {
          "stroke": "#6B7280",
          "stroke_width": 2
        }
      },
      {
        "id": "conn-2",
        "source": "start", 
        "target": "sentiment_analysis",
        "source_port": "output",
        "target_port": "input",
        "style": {
          "stroke": "#6B7280",
          "stroke_width": 2,
          "stroke_dasharray": "5,5"
        }
      }
    ]
  }
}
```

## Workflow Templates

### Template Definition

```json
{
  "template_id": "customer-support-template",
  "template_name": "Customer Support Processing Template",
  "description": "Template for automated customer support workflows",
  "category": "customer-service",
  "version": "1.0.0",
  
  "parameters": [
    {
      "name": "classification_agent",
      "type": "agent_reference",
      "description": "Agent to use for inquiry classification",
      "required": true,
      "default": "customer-classifier"
    },
    {
      "name": "response_tone",
      "type": "string",
      "description": "Tone for customer responses",
      "enum": ["formal", "friendly", "empathetic"],
      "default": "friendly"
    },
    {
      "name": "escalation_threshold",
      "type": "number",
      "description": "Confidence threshold for escalation",
      "minimum": 0,
      "maximum": 1,
      "default": 0.8
    }
  ],
  
  "workflow_definition": {
    // Workflow definition with parameter placeholders
    "steps": [
      {
        "step_id": "classify",
        "agent_config": {
          "agent_id": "{{classification_agent}}"
        }
      }
    ]
  },
  
  "usage_examples": [
    {
      "name": "E-commerce Support",
      "description": "Customer support for e-commerce platform",
      "parameters": {
        "classification_agent": "ecommerce-classifier",
        "response_tone": "friendly"
      }
    }
  ]
}
```

## Monitoring and Analytics

### Workflow Analytics

```json
{
  "analytics_dashboard": {
    "time_period": "last_7_days",
    
    "execution_metrics": {
      "total_executions": 1247,
      "successful_executions": 1189,
      "failed_executions": 58,
      "success_rate": 0.953,
      "average_execution_time": 125.3,
      "median_execution_time": 98.7
    },
    
    "performance_trends": [
      {
        "date": "2024-08-14",
        "executions": 178,
        "success_rate": 0.96,
        "avg_execution_time": 118.2
      }
    ],
    
    "step_performance": [
      {
        "step_id": "classify_inquiry",
        "step_name": "Classify Customer Inquiry",
        "executions": 1247,
        "success_rate": 0.98,
        "avg_execution_time": 1.2,
        "error_types": [
          {"error": "timeout", "count": 15},
          {"error": "ai_provider_error", "count": 8}
        ]
      }
    ],
    
    "resource_usage": {
      "total_ai_tokens": 156789,
      "total_cost_usd": 15.67,
      "agent_calls": 2847,
      "tool_executions": 1893
    },
    
    "top_errors": [
      {
        "error_code": "AGENT_TIMEOUT",
        "count": 23,
        "percentage": 0.018
      },
      {
        "error_code": "INVALID_INPUT", 
        "count": 18,
        "percentage": 0.014
      }
    ]
  }
}
```

This comprehensive Workflow Engine specification provides the foundation for building, executing, and monitoring complex multi-agent workflows with enterprise-grade reliability, observability, and scalability.
