-- Migration: Tool Management System Schema
-- Description: Adds comprehensive tool and agent template/instance management
-- Version: 0003
-- Date: 2025-08-18

BEGIN;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Drop existing indexes that might conflict
DROP INDEX IF EXISTS idx_tools_name;
DROP INDEX IF EXISTS idx_agents_name;

-- 1. Tool Templates Table
CREATE TABLE IF NOT EXISTS tool_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(100) NOT NULL, -- 'rag', 'sql_agent', 'mcp', 'code_interpreter', 'web_scraper', 'file_processor', 'api_integration'
    description TEXT,
    schema_definition JSONB NOT NULL, -- JSON schema for configuration validation
    default_config JSONB DEFAULT '{}', -- Default configuration values
    version VARCHAR(50) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    tags TEXT[] DEFAULT '{}',
    documentation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT valid_tool_type CHECK (type IN ('rag', 'sql_agent', 'mcp', 'code_interpreter', 'web_scraper', 'file_processor', 'api_integration', 'custom'))
);

-- 2. Tool Instances Table
CREATE TABLE IF NOT EXISTS tool_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES tool_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL DEFAULT '{}', -- Instance-specific configuration
    credentials JSONB DEFAULT '{}', -- Encrypted credentials and secrets
    environment VARCHAR(50) DEFAULT 'development', -- 'development', 'staging', 'production'
    status VARCHAR(50) DEFAULT 'inactive', -- 'active', 'inactive', 'error', 'maintenance'
    resource_limits JSONB DEFAULT '{}', -- Memory, CPU, timeout limits
    health_check_config JSONB DEFAULT '{}',
    last_health_check TIMESTAMP WITH TIME ZONE,
    health_status VARCHAR(50) DEFAULT 'unknown',
    metrics JSONB DEFAULT '{}', -- Performance and usage metrics
    error_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT valid_environment CHECK (environment IN ('development', 'staging', 'production')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'error', 'maintenance', 'deploying')),
    CONSTRAINT valid_health_status CHECK (health_status IN ('healthy', 'unhealthy', 'unknown', 'warning')),
    CONSTRAINT unique_instance_name_per_template UNIQUE (template_id, name)
);

-- 3. RAG Pipelines Table
CREATE TABLE IF NOT EXISTS rag_pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    data_sources JSONB NOT NULL DEFAULT '[]', -- Array of data source configurations
    processing_config JSONB NOT NULL DEFAULT '{}', -- Document processing configuration
    chunking_strategy JSONB NOT NULL DEFAULT '{}', -- Chunking configuration
    vectorization_config JSONB NOT NULL DEFAULT '{}', -- Embedding and vectorization settings
    storage_config JSONB NOT NULL DEFAULT '{}', -- Vector database and storage settings
    retrieval_config JSONB NOT NULL DEFAULT '{}', -- Retrieval strategy configuration
    quality_config JSONB DEFAULT '{}', -- Quality validation settings
    schedule_config JSONB DEFAULT '{}', -- Automated execution schedule
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- 4. RAG Pipeline Runs Table
CREATE TABLE IF NOT EXISTS rag_pipeline_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID NOT NULL REFERENCES rag_pipelines(id) ON DELETE CASCADE,
    run_type VARCHAR(50) DEFAULT 'manual', -- 'manual', 'scheduled', 'triggered'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    progress JSONB DEFAULT '{}', -- Progress tracking information
    metrics JSONB DEFAULT '{}', -- Execution metrics (documents processed, vectors created, etc.)
    logs TEXT,
    error_details TEXT,
    input_data JSONB DEFAULT '{}', -- Input parameters for this run
    output_summary JSONB DEFAULT '{}', -- Summary of results
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_run_type CHECK (run_type IN ('manual', 'scheduled', 'triggered')),
    CONSTRAINT valid_run_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

-- 5. Agent Templates Table
CREATE TABLE IF NOT EXISTS agent_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    framework VARCHAR(100) DEFAULT 'langgraph', -- 'langgraph', 'crewai', 'autogen', 'semantic_kernel'
    workflow_config JSONB NOT NULL DEFAULT '{}', -- LangGraph workflow definition
    persona_config JSONB DEFAULT '{}', -- System prompts, role definitions
    capabilities TEXT[] DEFAULT '{}', -- List of supported capabilities
    constraints JSONB DEFAULT '{}', -- Security and operational constraints
    tool_template_requirements JSONB DEFAULT '[]', -- Required tool templates with configurations
    optional_tool_templates JSONB DEFAULT '[]', -- Optional tool templates
    default_tool_bindings JSONB DEFAULT '{}', -- Default tool instance bindings
    version VARCHAR(50) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    tags TEXT[] DEFAULT '{}',
    documentation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT valid_framework CHECK (framework IN ('langgraph', 'crewai', 'autogen', 'semantic_kernel', 'custom'))
);

-- 6. Agent Instances Table
CREATE TABLE IF NOT EXISTS agent_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tool_instance_bindings JSONB NOT NULL DEFAULT '{}', -- Mapping of tool roles to instance IDs
    runtime_config JSONB DEFAULT '{}', -- Runtime-specific configuration
    state_config JSONB DEFAULT '{}', -- State management configuration
    conversation_history JSONB DEFAULT '[]', -- Recent conversation history
    performance_metrics JSONB DEFAULT '{}', -- Usage and performance statistics
    security_config JSONB DEFAULT '{}', -- Access controls and security settings
    status VARCHAR(50) DEFAULT 'inactive', -- 'active', 'inactive', 'error', 'maintenance', 'deploying'
    environment VARCHAR(50) DEFAULT 'development',
    last_activity TIMESTAMP WITH TIME ZONE,
    error_log TEXT,
    deployment_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT valid_agent_status CHECK (status IN ('active', 'inactive', 'error', 'maintenance', 'deploying')),
    CONSTRAINT valid_agent_environment CHECK (environment IN ('development', 'staging', 'production')),
    CONSTRAINT unique_agent_instance_name UNIQUE (name, environment)
);

-- 7. Tool Template - Agent Template Associations
CREATE TABLE IF NOT EXISTS tool_template_agent_template_associations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_template_id UUID NOT NULL REFERENCES tool_templates(id) ON DELETE CASCADE,
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    role_name VARCHAR(255) NOT NULL, -- Role of the tool in the agent (e.g., 'primary_rag', 'sql_executor')
    configuration JSONB DEFAULT '{}', -- Tool-specific configuration for this association
    is_required BOOLEAN DEFAULT true,
    execution_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_tool_role_per_agent UNIQUE (agent_template_id, role_name)
);

-- 8. Tool Instance Execution Logs
CREATE TABLE IF NOT EXISTS tool_instance_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_instance_id UUID NOT NULL REFERENCES tool_instances(id) ON DELETE CASCADE,
    agent_instance_id UUID REFERENCES agent_instances(id) ON DELETE SET NULL,
    execution_type VARCHAR(100) NOT NULL, -- Type of operation performed
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    error_details TEXT,
    execution_time_ms INTEGER,
    resource_usage JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_execution_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout'))
);

-- 9. Agent Instance Conversations
CREATE TABLE IF NOT EXISTS agent_instance_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_instance_id UUID NOT NULL REFERENCES agent_instances(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(255) NOT NULL,
    conversation_data JSONB NOT NULL DEFAULT '{}', -- Complete conversation thread
    metadata JSONB DEFAULT '{}', -- Additional context and metadata
    tools_used JSONB DEFAULT '[]', -- List of tools used in this conversation
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_session_per_agent UNIQUE (agent_instance_id, session_id)
);

-- Update existing tables to support new system

-- 10. Extend existing tools table
ALTER TABLE tools ADD COLUMN IF NOT EXISTS template_id UUID REFERENCES tool_templates(id);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS instance_id UUID REFERENCES tool_instances(id);
ALTER TABLE tools ADD COLUMN IF NOT EXISTS is_template_based BOOLEAN DEFAULT false;

-- 11. Extend existing agents table
ALTER TABLE agents ADD COLUMN IF NOT EXISTS template_id UUID REFERENCES agent_templates(id);
ALTER TABLE agents ADD COLUMN IF NOT EXISTS instance_id UUID REFERENCES agent_instances(id);
ALTER TABLE agents ADD COLUMN IF NOT EXISTS is_template_based BOOLEAN DEFAULT false;

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_tool_templates_type ON tool_templates(type);
CREATE INDEX IF NOT EXISTS idx_tool_templates_active ON tool_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_tool_templates_name_search ON tool_templates USING gin(to_tsvector('english', name || ' ' || coalesce(description, '')));

CREATE INDEX IF NOT EXISTS idx_tool_instances_template ON tool_instances(template_id);
CREATE INDEX IF NOT EXISTS idx_tool_instances_status ON tool_instances(status);
CREATE INDEX IF NOT EXISTS idx_tool_instances_environment ON tool_instances(environment);
CREATE INDEX IF NOT EXISTS idx_tool_instances_health ON tool_instances(health_status);

CREATE INDEX IF NOT EXISTS idx_rag_pipelines_active ON rag_pipelines(is_active);
CREATE INDEX IF NOT EXISTS idx_rag_pipeline_runs_pipeline ON rag_pipeline_runs(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_rag_pipeline_runs_status ON rag_pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_rag_pipeline_runs_created ON rag_pipeline_runs(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_templates_framework ON agent_templates(framework);
CREATE INDEX IF NOT EXISTS idx_agent_templates_active ON agent_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_agent_templates_name_search ON agent_templates USING gin(to_tsvector('english', name || ' ' || coalesce(description, '')));

CREATE INDEX IF NOT EXISTS idx_agent_instances_template ON agent_instances(template_id);
CREATE INDEX IF NOT EXISTS idx_agent_instances_status ON agent_instances(status);
CREATE INDEX IF NOT EXISTS idx_agent_instances_environment ON agent_instances(environment);
CREATE INDEX IF NOT EXISTS idx_agent_instances_activity ON agent_instances(last_activity);

CREATE INDEX IF NOT EXISTS idx_tool_agent_associations_tool ON tool_template_agent_template_associations(tool_template_id);
CREATE INDEX IF NOT EXISTS idx_tool_agent_associations_agent ON tool_template_agent_template_associations(agent_template_id);

CREATE INDEX IF NOT EXISTS idx_tool_executions_instance ON tool_instance_executions(tool_instance_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_agent ON tool_instance_executions(agent_instance_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_status ON tool_instance_executions(status);
CREATE INDEX IF NOT EXISTS idx_tool_executions_time ON tool_instance_executions(started_at);

CREATE INDEX IF NOT EXISTS idx_conversations_agent ON agent_instance_conversations(agent_instance_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON agent_instance_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON agent_instance_conversations(session_id);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tool_templates_updated_at BEFORE UPDATE ON tool_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tool_instances_updated_at BEFORE UPDATE ON tool_instances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rag_pipelines_updated_at BEFORE UPDATE ON rag_pipelines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_templates_updated_at BEFORE UPDATE ON agent_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_instances_updated_at BEFORE UPDATE ON agent_instances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_conversations_updated_at BEFORE UPDATE ON agent_instance_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default tool templates
INSERT INTO tool_templates (name, type, description, schema_definition, default_config, documentation) VALUES
(
    'RAG Tool Template',
    'rag',
    'Retrieval-Augmented Generation tool for semantic search and knowledge retrieval',
    '{
        "type": "object",
        "properties": {
            "vector_database": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["pgvector", "chroma", "pinecone", "weaviate"]},
                    "connection_string": {"type": "string"},
                    "collection_name": {"type": "string"}
                },
                "required": ["provider", "connection_string", "collection_name"]
            },
            "embedding_model": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["openai", "cohere", "huggingface"]},
                    "model_name": {"type": "string"},
                    "dimensions": {"type": "integer"}
                },
                "required": ["provider", "model_name"]
            },
            "retrieval_strategy": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["similarity", "mmr", "similarity_score_threshold"]},
                    "k": {"type": "integer", "minimum": 1, "maximum": 50},
                    "score_threshold": {"type": "number", "minimum": 0, "maximum": 1}
                }
            }
        },
        "required": ["vector_database", "embedding_model", "retrieval_strategy"]
    }',
    '{
        "vector_database": {
            "provider": "pgvector",
            "collection_name": "documents"
        },
        "embedding_model": {
            "provider": "openai",
            "model_name": "text-embedding-ada-002",
            "dimensions": 1536
        },
        "retrieval_strategy": {
            "method": "similarity",
            "k": 5
        }
    }',
    'RAG tool for semantic search and knowledge retrieval using vector databases'
),
(
    'SQL Agent Tool Template',
    'sql_agent',
    'Natural language to SQL conversion and database querying agent',
    '{
        "type": "object",
        "properties": {
            "database": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["postgresql", "mysql", "sqlite", "mssql"]},
                    "connection_string": {"type": "string"},
                    "schema": {"type": "string"}
                },
                "required": ["type", "connection_string"]
            },
            "safety": {
                "type": "object",
                "properties": {
                    "read_only": {"type": "boolean"},
                    "allowed_operations": {"type": "array", "items": {"type": "string"}},
                    "restricted_tables": {"type": "array", "items": {"type": "string"}}
                }
            },
            "llm_config": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string"},
                    "model": {"type": "string"},
                    "temperature": {"type": "number", "minimum": 0, "maximum": 2}
                }
            }
        },
        "required": ["database", "safety"]
    }',
    '{
        "database": {
            "type": "postgresql"
        },
        "safety": {
            "read_only": true,
            "allowed_operations": ["SELECT", "WITH"],
            "restricted_tables": []
        },
        "llm_config": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0
        }
    }',
    'SQL agent for natural language database querying with safety controls'
),
(
    'MCP Tool Template',
    'mcp',
    'Model Context Protocol integration for enhanced agent capabilities',
    '{
        "type": "object",
        "properties": {
            "server_config": {
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string"},
                    "authentication": {"type": "object"},
                    "timeout": {"type": "integer"}
                },
                "required": ["endpoint"]
            },
            "resource_config": {
                "type": "object",
                "properties": {
                    "resource_types": {"type": "array", "items": {"type": "string"}},
                    "access_level": {"type": "string", "enum": ["read", "write", "admin"]}
                }
            },
            "tool_discovery": {
                "type": "object",
                "properties": {
                    "auto_discover": {"type": "boolean"},
                    "whitelist": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["server_config"]
    }',
    '{
        "server_config": {
            "timeout": 30
        },
        "resource_config": {
            "access_level": "read"
        },
        "tool_discovery": {
            "auto_discover": true,
            "whitelist": []
        }
    }',
    'MCP integration for enhanced agent context and capabilities'
),
(
    'Code Interpreter Tool Template',
    'code_interpreter',
    'Secure code execution environment for multiple programming languages',
    '{
        "type": "object",
        "properties": {
            "runtime": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "enum": ["python", "javascript", "bash", "sql"]},
                    "version": {"type": "string"},
                    "packages": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["language"]
            },
            "security": {
                "type": "object",
                "properties": {
                    "sandbox": {"type": "boolean"},
                    "network_access": {"type": "boolean"},
                    "file_system_access": {"type": "string", "enum": ["none", "read", "write"]},
                    "resource_limits": {
                        "type": "object",
                        "properties": {
                            "memory_mb": {"type": "integer"},
                            "cpu_time_seconds": {"type": "integer"},
                            "execution_timeout": {"type": "integer"}
                        }
                    }
                }
            }
        },
        "required": ["runtime", "security"]
    }',
    '{
        "runtime": {
            "language": "python",
            "version": "3.11",
            "packages": ["pandas", "numpy", "matplotlib"]
        },
        "security": {
            "sandbox": true,
            "network_access": false,
            "file_system_access": "read",
            "resource_limits": {
                "memory_mb": 512,
                "cpu_time_seconds": 30,
                "execution_timeout": 60
            }
        }
    }',
    'Secure code execution environment with configurable language support'
);

-- Insert default agent templates
INSERT INTO agent_templates (name, description, framework, workflow_config, persona_config, tool_template_requirements) VALUES
(
    'Research Assistant Agent',
    'An AI agent specialized in research tasks using RAG and web search capabilities',
    'langgraph',
    '{
        "nodes": [
            {"id": "question_analysis", "type": "llm", "prompt": "analyze_research_question"},
            {"id": "rag_search", "type": "tool", "tool_role": "primary_rag"},
            {"id": "web_search", "type": "tool", "tool_role": "web_scraper"},
            {"id": "synthesis", "type": "llm", "prompt": "synthesize_research"}
        ],
        "edges": [
            {"from": "question_analysis", "to": "rag_search"},
            {"from": "rag_search", "to": "web_search", "condition": "insufficient_info"},
            {"from": ["rag_search", "web_search"], "to": "synthesis"}
        ]
    }',
    '{
        "role": "Research Assistant",
        "personality": "Thorough, analytical, and precise researcher",
        "system_prompt": "You are a research assistant that helps users find and synthesize information from multiple sources.",
        "capabilities": ["research", "analysis", "synthesis", "fact_checking"],
        "communication_style": "Professional and detailed"
    }',
    '[
        {"template_name": "RAG Tool Template", "role": "primary_rag", "required": true},
        {"template_name": "Web Scraper Tool Template", "role": "web_scraper", "required": false}
    ]'
),
(
    'Data Analysis Agent',
    'An AI agent for data analysis and SQL querying with code execution capabilities',
    'langgraph',
    '{
        "nodes": [
            {"id": "query_understanding", "type": "llm", "prompt": "understand_data_query"},
            {"id": "sql_execution", "type": "tool", "tool_role": "sql_agent"},
            {"id": "data_analysis", "type": "tool", "tool_role": "code_interpreter"},
            {"id": "visualization", "type": "tool", "tool_role": "code_interpreter"},
            {"id": "report_generation", "type": "llm", "prompt": "generate_report"}
        ],
        "edges": [
            {"from": "query_understanding", "to": "sql_execution"},
            {"from": "sql_execution", "to": "data_analysis"},
            {"from": "data_analysis", "to": "visualization", "condition": "needs_visualization"},
            {"from": ["data_analysis", "visualization"], "to": "report_generation"}
        ]
    }',
    '{
        "role": "Data Analyst",
        "personality": "Methodical, detail-oriented, and insight-driven",
        "system_prompt": "You are a data analyst that helps users explore and understand their data through SQL queries and statistical analysis.",
        "capabilities": ["data_analysis", "sql_querying", "visualization", "statistical_analysis"],
        "communication_style": "Clear and data-driven"
    }',
    '[
        {"template_name": "SQL Agent Tool Template", "role": "sql_agent", "required": true},
        {"template_name": "Code Interpreter Tool Template", "role": "code_interpreter", "required": true}
    ]'
);

COMMIT;
