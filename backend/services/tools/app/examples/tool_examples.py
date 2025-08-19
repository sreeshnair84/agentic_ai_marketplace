"""
Tool Examples for Chat Interface Testing
"""

from typing import Dict, Any, List

class ToolExamples:
    """Collection of example tools for testing and demonstration"""
    
    @staticmethod
    def get_email_parser_tool() -> Dict[str, Any]:
        """Email Parser Tool Example"""
        return {
            "id": "email-parser-tool",
            "name": "EmailParser",
            "display_name": "Email Content Parser",
            "description": "Advanced email parsing tool that extracts structured information from email content including attachments, metadata, and sentiment analysis",
            "category": "mcp",
            "type": "email_processing",
            "version": "2.1.0",
            "endpoint_url": "https://tools.agenticai.local/v1/email-parser",
            "dns_name": "email-parser.tools.agenticai.local",
            "health_url": "https://tools.agenticai.local/health",
            "documentation_url": "https://docs.agenticai.local/tools/email-parser",
            "input_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "email_content": {
                            "type": "string",
                            "description": "Raw email content to parse",
                            "example": "From: customer@example.com\\nSubject: Order Issue\\nDear Support..."
                        },
                        "parse_options": {
                            "type": "object",
                            "description": "Parsing configuration options",
                            "properties": {
                                "extract_attachments": {"type": "boolean", "default": True},
                                "sentiment_analysis": {"type": "boolean", "default": True},
                                "extract_entities": {"type": "boolean", "default": True},
                                "priority_detection": {"type": "boolean", "default": True}
                            }
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context for parsing",
                            "properties": {
                                "sender_history": {"type": "array"},
                                "thread_context": {"type": "object"},
                                "business_rules": {"type": "object"}
                            }
                        }
                    },
                    "required": ["email_content"]
                },
                "content_types": ["application/json", "text/plain", "multipart/form-data"],
                "size_limits": {
                    "max_payload_size": "10MB",
                    "max_file_size": "5MB"
                }
            },
            "output_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "parsed_data": {
                            "type": "object",
                            "properties": {
                                "headers": {
                                    "type": "object",
                                    "properties": {
                                        "from": {"type": "string"},
                                        "to": {"type": "array", "items": {"type": "string"}},
                                        "subject": {"type": "string"},
                                        "date": {"type": "string"},
                                        "message_id": {"type": "string"}
                                    }
                                },
                                "body": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "html": {"type": "string"},
                                        "cleaned_text": {"type": "string"}
                                    }
                                },
                                "attachments": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "filename": {"type": "string"},
                                            "content_type": {"type": "string"},
                                            "size": {"type": "integer"},
                                            "url": {"type": "string"}
                                        }
                                    }
                                },
                                "sentiment": {
                                    "type": "object",
                                    "properties": {
                                        "polarity": {"type": "number", "minimum": -1, "maximum": 1},
                                        "subjectivity": {"type": "number", "minimum": 0, "maximum": 1},
                                        "label": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                                        "confidence": {"type": "number"}
                                    }
                                },
                                "entities": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string"},
                                            "type": {"type": "string"},
                                            "confidence": {"type": "number"},
                                            "start": {"type": "integer"},
                                            "end": {"type": "integer"}
                                        }
                                    }
                                },
                                "priority": {
                                    "type": "object",
                                    "properties": {
                                        "level": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                                        "score": {"type": "number"},
                                        "indicators": {"type": "array", "items": {"type": "string"}}
                                    }
                                }
                            }
                        },
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "processing_time": {"type": "number"},
                                "model_version": {"type": "string"},
                                "confidence_scores": {"type": "object"}
                            }
                        },
                        "errors": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "content_types": ["application/json"]
            },
            "mcp_config": {
                "server_name": "email-parser-mcp",
                "server_url": "mcp://email-parser:8080",
                "protocol_version": "1.0",
                "transport": "http",
                "capabilities": ["tools", "resources"]
            },
            "configuration_fields": [
                {
                    "name": "api_key",
                    "type": "password",
                    "required": True,
                    "description": "API key for email parsing service",
                    "validation": "^[a-zA-Z0-9]{32}$"
                },
                {
                    "name": "sentiment_provider",
                    "type": "select",
                    "required": False,
                    "options": ["textblob", "vader", "transformers"],
                    "default": "textblob",
                    "description": "Sentiment analysis provider"
                },
                {
                    "name": "entity_extraction_model",
                    "type": "select",
                    "required": False,
                    "options": ["spacy_en", "spacy_multilingual", "custom"],
                    "default": "spacy_en",
                    "description": "Entity extraction model"
                }
            ],
            "runtime": {
                "environment": "python",
                "requirements": ["python>=3.8", "spacy>=3.4.0", "textblob>=0.17.0"],
                "timeout_seconds": 120,
                "memory_limit": "1GB",
                "cpu_limit": "500m"
            },
            "health_check": {
                "enabled": True,
                "endpoint": "/health",
                "method": "GET",
                "expected_status": 200,
                "interval_seconds": 60,
                "timeout_seconds": 10
            },
            "usage_metrics": {
                "total_executions": 12456,
                "success_rate": 0.96,
                "avg_execution_time": 3.2,
                "last_executed": "2024-08-14T16:30:00Z"
            },
            "tags": ["email", "parsing", "nlp", "sentiment", "entities"],
            "status": "active",
            "created_at": "2024-05-15T10:00:00Z",
            "updated_at": "2024-08-14T15:30:00Z"
        }
    
    @staticmethod
    def get_database_query_tool() -> Dict[str, Any]:
        """Database Query Tool Example"""
        return {
            "id": "database-query-tool",
            "name": "DatabaseQueryTool",
            "display_name": "Intelligent Database Query Tool",
            "description": "Advanced database query tool with natural language to SQL conversion, query optimization, and security validation",
            "category": "custom",
            "type": "database_tool",
            "version": "3.0.0",
            "endpoint_url": "https://tools.agenticai.local/v1/database-query",
            "dns_name": "db-query.tools.agenticai.local",
            "health_url": "https://tools.agenticai.local/health",
            "documentation_url": "https://docs.agenticai.local/tools/database-query",
            "input_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "query_input": {
                            "type": "string",
                            "description": "Natural language query or SQL statement",
                            "example": "Show me all customers who purchased more than $1000 in the last month"
                        },
                        "query_type": {
                            "type": "string",
                            "enum": ["natural_language", "sql", "assisted"],
                            "default": "natural_language",
                            "description": "Type of query input"
                        },
                        "database_config": {
                            "type": "object",
                            "description": "Database connection configuration",
                            "properties": {
                                "connection_id": {"type": "string"},
                                "schema": {"type": "string"},
                                "timeout": {"type": "integer", "default": 30}
                            },
                            "required": ["connection_id"]
                        },
                        "output_options": {
                            "type": "object",
                            "description": "Output formatting options",
                            "properties": {
                                "format": {"type": "string", "enum": ["json", "csv", "table"], "default": "json"},
                                "limit": {"type": "integer", "default": 100, "maximum": 10000},
                                "include_metadata": {"type": "boolean", "default": True}
                            }
                        },
                        "safety_options": {
                            "type": "object",
                            "description": "Query safety and validation options",
                            "properties": {
                                "dry_run": {"type": "boolean", "default": False},
                                "explain_plan": {"type": "boolean", "default": False},
                                "validate_syntax": {"type": "boolean", "default": True},
                                "check_permissions": {"type": "boolean", "default": True}
                            }
                        }
                    },
                    "required": ["query_input", "database_config"]
                },
                "content_types": ["application/json"],
                "size_limits": {
                    "max_payload_size": "1MB"
                }
            },
            "output_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "query_analysis": {
                            "type": "object",
                            "properties": {
                                "original_query": {"type": "string"},
                                "generated_sql": {"type": "string"},
                                "query_type": {"type": "string"},
                                "estimated_cost": {"type": "number"},
                                "affected_tables": {"type": "array", "items": {"type": "string"}},
                                "security_warnings": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "execution_results": {
                            "type": "object",
                            "properties": {
                                "data": {"type": "array"},
                                "row_count": {"type": "integer"},
                                "execution_time": {"type": "number"},
                                "columns": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "type": {"type": "string"},
                                            "nullable": {"type": "boolean"}
                                        }
                                    }
                                }
                            }
                        },
                        "performance_metrics": {
                            "type": "object",
                            "properties": {
                                "query_plan": {"type": "object"},
                                "index_usage": {"type": "array"},
                                "optimization_suggestions": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "database_version": {"type": "string"},
                                "schema_info": {"type": "object"},
                                "user_permissions": {"type": "array"}
                            }
                        }
                    }
                },
                "content_types": ["application/json", "text/csv", "text/html"]
            },
            "configuration_fields": [
                {
                    "name": "default_database_url",
                    "type": "text",
                    "required": True,
                    "description": "Default database connection URL",
                    "validation": "^(postgresql|mysql|sqlite)://.+"
                },
                {
                    "name": "max_query_timeout",
                    "type": "number",
                    "required": False,
                    "default": "300",
                    "description": "Maximum query timeout in seconds"
                },
                {
                    "name": "enable_query_caching",
                    "type": "boolean",
                    "required": False,
                    "default": "true",
                    "description": "Enable query result caching"
                },
                {
                    "name": "allowed_operations",
                    "type": "multiselect",
                    "required": True,
                    "options": ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"],
                    "default": ["SELECT"],
                    "description": "Allowed SQL operations"
                }
            ],
            "runtime": {
                "environment": "python",
                "requirements": ["python>=3.9", "sqlalchemy>=1.4.0", "psycopg2>=2.9.0"],
                "timeout_seconds": 300,
                "memory_limit": "2GB",
                "cpu_limit": "1000m"
            },
            "health_check": {
                "enabled": True,
                "endpoint": "/health",
                "method": "GET",
                "expected_status": 200,
                "interval_seconds": 30,
                "timeout_seconds": 5
            },
            "usage_metrics": {
                "total_executions": 8923,
                "success_rate": 0.94,
                "avg_execution_time": 5.7,
                "last_executed": "2024-08-14T16:25:00Z"
            },
            "tags": ["database", "sql", "query", "analytics", "nlp"],
            "status": "active",
            "created_at": "2024-04-10T14:00:00Z",
            "updated_at": "2024-08-14T15:30:00Z"
        }
    
    @staticmethod
    def get_file_processor_tool() -> Dict[str, Any]:
        """File Processing Tool Example"""
        return {
            "id": "file-processor-tool",
            "name": "FileProcessor",
            "display_name": "Universal File Processor",
            "description": "Comprehensive file processing tool supporting multiple formats, conversions, analysis, and content extraction",
            "category": "api",
            "type": "file_processing",
            "version": "2.3.0",
            "endpoint_url": "https://tools.agenticai.local/v1/file-processor",
            "dns_name": "file-processor.tools.agenticai.local",
            "health_url": "https://tools.agenticai.local/health",
            "documentation_url": "https://docs.agenticai.local/tools/file-processor",
            "input_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["convert", "extract", "analyze", "validate", "compress", "merge"],
                            "description": "Operation to perform on the file(s)"
                        },
                        "files": {
                            "type": "array",
                            "description": "Files to process",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string"},
                                    "filename": {"type": "string"},
                                    "content_type": {"type": "string"},
                                    "size": {"type": "integer"}
                                },
                                "required": ["url", "filename"]
                            },
                            "minItems": 1,
                            "maxItems": 10
                        },
                        "operation_config": {
                            "type": "object",
                            "description": "Configuration for the specific operation",
                            "properties": {
                                "output_format": {"type": "string"},
                                "quality_settings": {"type": "object"},
                                "extraction_options": {"type": "object"},
                                "analysis_depth": {"type": "string", "enum": ["basic", "detailed", "comprehensive"]}
                            }
                        },
                        "processing_options": {
                            "type": "object",
                            "description": "General processing options",
                            "properties": {
                                "async_processing": {"type": "boolean", "default": False},
                                "notify_completion": {"type": "boolean", "default": False},
                                "preserve_metadata": {"type": "boolean", "default": True},
                                "output_location": {"type": "string"}
                            }
                        }
                    },
                    "required": ["operation", "files"]
                },
                "content_types": ["application/json", "multipart/form-data"],
                "size_limits": {
                    "max_payload_size": "500MB",
                    "max_file_size": "100MB"
                }
            },
            "output_signature": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "operation_id": {"type": "string"},
                        "processing_results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "input_file": {"type": "string"},
                                    "status": {"type": "string", "enum": ["success", "failed", "processing"]},
                                    "output_files": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "filename": {"type": "string"},
                                                "url": {"type": "string"},
                                                "format": {"type": "string"},
                                                "size": {"type": "integer"}
                                            }
                                        }
                                    },
                                    "extracted_content": {
                                        "type": "object",
                                        "properties": {
                                            "text": {"type": "string"},
                                            "metadata": {"type": "object"},
                                            "images": {"type": "array"},
                                            "tables": {"type": "array"}
                                        }
                                    },
                                    "analysis_results": {
                                        "type": "object",
                                        "properties": {
                                            "file_type": {"type": "string"},
                                            "encoding": {"type": "string"},
                                            "language": {"type": "string"},
                                            "word_count": {"type": "integer"},
                                            "readability_score": {"type": "number"},
                                            "sentiment": {"type": "object"}
                                        }
                                    },
                                    "validation_results": {
                                        "type": "object",
                                        "properties": {
                                            "is_valid": {"type": "boolean"},
                                            "format_compliance": {"type": "boolean"},
                                            "security_scan": {"type": "object"},
                                            "issues": {"type": "array"}
                                        }
                                    }
                                }
                            }
                        },
                        "summary": {
                            "type": "object",
                            "properties": {
                                "total_files": {"type": "integer"},
                                "successful": {"type": "integer"},
                                "failed": {"type": "integer"},
                                "total_processing_time": {"type": "number"},
                                "output_size": {"type": "integer"}
                            }
                        }
                    }
                },
                "content_types": ["application/json", "application/zip"]
            },
            "configuration_fields": [
                {
                    "name": "storage_backend",
                    "type": "select",
                    "required": True,
                    "options": ["local", "s3", "azure_blob", "gcs"],
                    "default": "local",
                    "description": "Storage backend for processed files"
                },
                {
                    "name": "max_concurrent_jobs",
                    "type": "number",
                    "required": False,
                    "default": "5",
                    "description": "Maximum concurrent processing jobs"
                },
                {
                    "name": "enable_virus_scanning",
                    "type": "boolean",
                    "required": False,
                    "default": "true",
                    "description": "Enable virus scanning for uploaded files"
                }
            ],
            "runtime": {
                "environment": "docker",
                "requirements": ["python>=3.9", "pillow>=8.0.0", "pypdf2>=2.0.0"],
                "timeout_seconds": 600,
                "memory_limit": "4GB",
                "cpu_limit": "2000m"
            },
            "usage_metrics": {
                "total_executions": 15234,
                "success_rate": 0.92,
                "avg_execution_time": 8.4,
                "last_executed": "2024-08-14T16:20:00Z"
            },
            "tags": ["files", "processing", "conversion", "extraction", "analysis"],
            "status": "active",
            "created_at": "2024-03-20T09:00:00Z",
            "updated_at": "2024-08-14T15:30:00Z"
        }
