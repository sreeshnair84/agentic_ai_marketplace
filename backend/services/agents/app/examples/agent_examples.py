"""
Agent Examples for Chat Interface Testing
"""

from typing import Dict, Any, List
from ..models.a2a_models import A2AAgentCard, AgentSkill, AgentCapabilities, InputOutputSignature, HealthCheckConfig, UsageMetrics

class AgentExamples:
    """Collection of example agents for testing and demonstration"""
    
    @staticmethod
    def get_customer_service_agent() -> Dict[str, Any]:
        """Customer Service Agent Example"""
        return {
            "id": "customer-service-agent",
            "name": "CustomerServiceAgent",
            "description": "AI agent specialized in customer service interactions, complaint handling, and support ticket resolution",
            "version": "1.2.0",
            "category": "customer-service",
            "url": "http://localhost:8002/a2a/agents/customer-service",
            "health_url": "http://localhost:8002/health",
            "dns_name": "customer-service.agenticai.local",
            "card_url": "http://localhost:8002/a2a/cards/customer-service-agent",
            "default_input_modes": ["text", "json", "voice"],
            "default_output_modes": ["text", "json", "stream"],
            "capabilities": {
                "streaming": True,
                "batch_processing": True,
                "file_upload": True,
                "multi_modal": True,
                "external_apis": True
            },
            "input_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "customer_inquiry": {
                            "type": "string",
                            "description": "Customer's inquiry or complaint",
                            "example": "I'm having trouble with my order #12345"
                        },
                        "customer_context": {
                            "type": "object",
                            "description": "Customer information and history",
                            "properties": {
                                "customer_id": {"type": "string"},
                                "order_history": {"type": "array"},
                                "previous_tickets": {"type": "array"},
                                "account_status": {"type": "string"}
                            }
                        },
                        "urgency_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "default": "medium"
                        }
                    },
                    "required": ["customer_inquiry"]
                },
                "content_types": ["application/json", "text/plain", "multipart/form-data"]
            },
            "output_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "response": {
                            "type": "string",
                            "description": "Customer service response"
                        },
                        "sentiment_analysis": {
                            "type": "object",
                            "properties": {
                                "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                            }
                        },
                        "suggested_actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string"},
                                    "priority": {"type": "string"},
                                    "department": {"type": "string"}
                                }
                            }
                        },
                        "escalation_needed": {"type": "boolean"},
                        "resolution_status": {
                            "type": "string",
                            "enum": ["resolved", "pending", "escalated", "requires_human"]
                        }
                    }
                }
            },
            "skills": [
                {
                    "id": "complaint_handling",
                    "name": "Complaint Handling",
                    "description": "Handles customer complaints with empathy and resolution focus",
                    "tags": ["complaints", "resolution", "empathy", "customer-satisfaction"],
                    "examples": [
                        {
                            "description": "Handle billing dispute",
                            "input": {
                                "customer_inquiry": "I was charged twice for the same item",
                                "customer_context": {"customer_id": "CUST001", "account_status": "active"}
                            },
                            "output": {
                                "response": "I understand your concern about the duplicate charge. Let me look into this immediately and ensure we resolve this for you today.",
                                "suggested_actions": [{"action": "refund_duplicate_charge", "priority": "high", "department": "billing"}],
                                "resolution_status": "pending"
                            }
                        }
                    ],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "empathy_level": {"type": "string", "enum": ["standard", "high", "maximum"], "default": "high"},
                            "escalation_threshold": {"type": "number", "default": 0.8}
                        }
                    }
                },
                {
                    "id": "order_tracking",
                    "name": "Order Tracking",
                    "description": "Provides order status and tracking information",
                    "tags": ["orders", "tracking", "logistics", "status"],
                    "examples": [
                        {
                            "description": "Track order status",
                            "input": {
                                "customer_inquiry": "Where is my order #12345?",
                                "customer_context": {"customer_id": "CUST001"}
                            },
                            "output": {
                                "response": "Your order #12345 is currently in transit and expected to arrive tomorrow between 2-6 PM. You can track it real-time using tracking number TR789.",
                                "resolution_status": "resolved"
                            }
                        }
                    ]
                }
            ],
            "tags": ["customer-service", "support", "gemini", "complaints", "orders"],
            "search_keywords": ["customer", "support", "service", "complaints", "orders", "help"],
            "ai_provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "model_config": {
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9,
                "safety_settings": {
                    "harassment": "BLOCK_MEDIUM_AND_ABOVE",
                    "hate_speech": "BLOCK_MEDIUM_AND_ABOVE"
                }
            },
            "external_services": [
                {
                    "name": "CRM API",
                    "dns_name": "crm-api.company.com",
                    "health_url": "https://crm-api.company.com/health",
                    "api_version": "v2",
                    "authentication": "api_key"
                },
                {
                    "name": "Order Management System",
                    "dns_name": "orders.company.com",
                    "health_url": "https://orders.company.com/health",
                    "api_version": "v1",
                    "authentication": "oauth"
                }
            ],
            "health_check": {
                "endpoint": "/health",
                "interval_seconds": 30,
                "timeout_seconds": 5,
                "required_fields": ["status", "version", "dependencies", "external_services"]
            },
            "usage_metrics": {
                "total_executions": 15623,
                "success_rate": 0.94,
                "avg_execution_time": 2.1,
                "last_executed": "2024-08-14T15:45:00Z"
            },
            "author": "Customer Success Team",
            "organization": "Agentic AI Accelerator",
            "environment": "production",
            "created_at": "2024-06-01T10:00:00Z",
            "updated_at": "2024-08-14T15:30:00Z"
        }
    
    @staticmethod
    def get_data_analyst_agent() -> Dict[str, Any]:
        """Data Analysis Agent Example"""
        return {
            "id": "data-analyst-agent",
            "name": "DataAnalystAgent",
            "description": "AI agent specialized in data analysis, visualization, and insights generation from various data sources",
            "version": "2.0.0",
            "category": "analytics",
            "url": "http://localhost:8002/a2a/agents/data-analyst",
            "health_url": "http://localhost:8002/health",
            "dns_name": "data-analyst.agenticai.local",
            "card_url": "http://localhost:8002/a2a/cards/data-analyst-agent",
            "default_input_modes": ["text", "json", "file"],
            "default_output_modes": ["text", "json", "stream", "file"],
            "capabilities": {
                "streaming": True,
                "batch_processing": True,
                "file_upload": True,
                "multi_modal": True,
                "external_apis": True
            },
            "input_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "analysis_request": {
                            "type": "string",
                            "description": "Description of the analysis to perform",
                            "example": "Analyze sales trends for Q3 2024 and identify key patterns"
                        },
                        "data_sources": {
                            "type": "array",
                            "description": "Data sources to analyze",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["csv", "json", "database", "api"]},
                                    "source": {"type": "string"},
                                    "filters": {"type": "object"}
                                }
                            }
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["descriptive", "diagnostic", "predictive", "prescriptive"],
                            "default": "descriptive"
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["report", "dashboard", "charts", "summary"],
                            "default": "report"
                        }
                    },
                    "required": ["analysis_request", "data_sources"]
                },
                "content_types": ["application/json", "multipart/form-data"],
                "size_limits": {
                    "max_payload_size": "100MB",
                    "max_file_size": "50MB"
                }
            },
            "output_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "analysis_results": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "key_insights": {"type": "array", "items": {"type": "string"}},
                                "statistics": {"type": "object"},
                                "trends": {"type": "array"}
                            }
                        },
                        "visualizations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "title": {"type": "string"},
                                    "data_url": {"type": "string"},
                                    "image_url": {"type": "string"}
                                }
                            }
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string"},
                                    "impact": {"type": "string"},
                                    "priority": {"type": "string"}
                                }
                            }
                        },
                        "data_quality_report": {
                            "type": "object",
                            "properties": {
                                "completeness": {"type": "number"},
                                "accuracy": {"type": "number"},
                                "issues": {"type": "array"}
                            }
                        }
                    }
                },
                "content_types": ["application/json", "text/html", "application/pdf"]
            },
            "skills": [
                {
                    "id": "statistical_analysis",
                    "name": "Statistical Analysis",
                    "description": "Performs comprehensive statistical analysis on datasets",
                    "tags": ["statistics", "analysis", "trends", "patterns"],
                    "examples": [
                        {
                            "description": "Sales trend analysis",
                            "input": {
                                "analysis_request": "Analyze monthly sales trends",
                                "data_sources": [{"type": "csv", "source": "sales_data.csv"}],
                                "analysis_type": "descriptive"
                            },
                            "output": {
                                "analysis_results": {
                                    "summary": "Sales show 15% growth with seasonal peaks in Q4",
                                    "key_insights": ["December shows highest sales", "Mobile sales increasing"],
                                    "trends": [{"period": "monthly", "direction": "upward", "rate": 0.15}]
                                }
                            }
                        }
                    ]
                },
                {
                    "id": "data_visualization",
                    "name": "Data Visualization",
                    "description": "Creates charts, graphs, and dashboards from data",
                    "tags": ["visualization", "charts", "dashboards", "reporting"],
                    "examples": [
                        {
                            "description": "Create sales dashboard",
                            "input": {
                                "analysis_request": "Create a sales performance dashboard",
                                "output_format": "dashboard"
                            },
                            "output": {
                                "visualizations": [
                                    {"type": "line_chart", "title": "Monthly Sales Trend"},
                                    {"type": "pie_chart", "title": "Sales by Category"},
                                    {"type": "bar_chart", "title": "Top Performers"}
                                ]
                            }
                        }
                    ]
                }
            ],
            "tags": ["analytics", "data-science", "visualization", "insights", "gemini"],
            "search_keywords": ["data", "analysis", "analytics", "visualization", "insights", "trends"],
            "ai_provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "external_services": [
                {
                    "name": "Data Warehouse",
                    "dns_name": "warehouse.company.com",
                    "health_url": "https://warehouse.company.com/health",
                    "api_version": "v3",
                    "authentication": "token"
                }
            ],
            "usage_metrics": {
                "total_executions": 8934,
                "success_rate": 0.97,
                "avg_execution_time": 12.5,
                "last_executed": "2024-08-14T14:20:00Z"
            },
            "author": "Data Science Team",
            "organization": "Agentic AI Accelerator",
            "environment": "production"
        }

    @staticmethod
    def get_code_review_agent() -> Dict[str, Any]:
        """Code Review Agent Example"""
        return {
            "id": "code-review-agent",
            "name": "CodeReviewAgent", 
            "description": "AI agent specialized in code review, security analysis, and best practices recommendations",
            "version": "1.5.0",
            "category": "development",
            "url": "http://localhost:8002/a2a/agents/code-review",
            "health_url": "http://localhost:8002/health",
            "dns_name": "code-review.agenticai.local",
            "card_url": "http://localhost:8002/a2a/cards/code-review-agent",
            "default_input_modes": ["text", "json", "file"],
            "default_output_modes": ["text", "json", "stream"],
            "capabilities": {
                "streaming": True,
                "batch_processing": True,
                "file_upload": True,
                "multi_modal": False,
                "external_apis": True
            },
            "input_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "code_content": {
                            "type": "string",
                            "description": "Code to review",
                            "example": "def process_data(data):\\n    return data.process()"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "enum": ["python", "javascript", "java", "csharp", "go", "rust"]
                        },
                        "review_type": {
                            "type": "string",
                            "enum": ["security", "performance", "best_practices", "comprehensive"],
                            "default": "comprehensive"
                        },
                        "context": {
                            "type": "object",
                            "properties": {
                                "project_type": {"type": "string"},
                                "framework": {"type": "string"},
                                "team_standards": {"type": "object"}
                            }
                        }
                    },
                    "required": ["code_content", "language"]
                }
            },
            "output_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "review_summary": {
                            "type": "object",
                            "properties": {
                                "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
                                "quality_rating": {"type": "string", "enum": ["excellent", "good", "fair", "poor"]},
                                "total_issues": {"type": "integer"}
                            }
                        },
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["security", "performance", "style", "logic", "maintenance"]},
                                    "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
                                    "line_number": {"type": "integer"},
                                    "description": {"type": "string"},
                                    "suggestion": {"type": "string"},
                                    "example_fix": {"type": "string"}
                                }
                            }
                        },
                        "improvements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string"},
                                    "description": {"type": "string"},
                                    "impact": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "skills": [
                {
                    "id": "security_analysis",
                    "name": "Security Analysis",
                    "description": "Identifies security vulnerabilities and risks in code",
                    "tags": ["security", "vulnerabilities", "owasp", "analysis"],
                    "examples": [
                        {
                            "description": "SQL injection detection",
                            "input": {
                                "code_content": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
                                "language": "python",
                                "review_type": "security"
                            },
                            "output": {
                                "issues": [
                                    {
                                        "type": "security",
                                        "severity": "critical",
                                        "description": "Potential SQL injection vulnerability",
                                        "suggestion": "Use parameterized queries",
                                        "example_fix": "query = \"SELECT * FROM users WHERE id = %s\"; cursor.execute(query, (user_id,))"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ],
            "tags": ["development", "code-review", "security", "quality", "gemini"],
            "ai_provider": "gemini",
            "model_name": "gemini-1.5-pro",
            "usage_metrics": {
                "total_executions": 5672,
                "success_rate": 0.98,
                "avg_execution_time": 4.2,
                "last_executed": "2024-08-14T16:15:00Z"
            },
            "author": "Development Team",
            "organization": "Agentic AI Accelerator",
            "environment": "production"
        }
