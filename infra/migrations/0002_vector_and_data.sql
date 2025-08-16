-- =====================================================
-- LCNC PLATFORM - VECTOR STORAGE AND SAMPLE DATA
-- Consolidated Migration: RAG capabilities and initial data
-- =====================================================

-- =====================================================
-- VECTOR STORAGE FOR RAG CAPABILITIES
-- =====================================================

-- Document embeddings table for RAG
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-small dimension
    metadata JSONB,
    namespace VARCHAR(255) DEFAULT 'default',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation embeddings for context retrieval
CREATE TABLE IF NOT EXISTS conversation_embeddings (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    message_content TEXT NOT NULL,
    embedding vector(1536),
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base embeddings
CREATE TABLE IF NOT EXISTS knowledge_base_embeddings (
    id SERIAL PRIMARY KEY,
    knowledge_item_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    content TEXT NOT NULL,
    embedding vector(1536),
    category VARCHAR(255),
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VECTOR INDEXES AND FUNCTIONS
-- =====================================================

-- Vector search indexes
CREATE INDEX IF NOT EXISTS idx_document_embeddings_embedding ON document_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings (document_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_namespace ON document_embeddings (namespace);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_metadata ON document_embeddings USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_embedding ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_conversation_id ON conversation_embeddings (conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_role ON conversation_embeddings (role);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_embedding ON knowledge_base_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_knowledge_item_id ON knowledge_base_embeddings (knowledge_item_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_category ON knowledge_base_embeddings (category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_tags ON knowledge_base_embeddings USING GIN (tags);

-- Cosine similarity function
CREATE OR REPLACE FUNCTION cosine_similarity(vec1 vector, vec2 vector)
RETURNS float
LANGUAGE sql
IMMUTABLE STRICT
AS $$
    SELECT 1 - (vec1 <=> vec2);
$$;

-- Search similar documents function
CREATE OR REPLACE FUNCTION search_similar_documents(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10,
    target_namespace varchar DEFAULT 'default'
)
RETURNS TABLE (
    id integer,
    document_id varchar,
    content text,
    similarity float,
    metadata jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT 
        de.id,
        de.document_id,
        de.content,
        cosine_similarity(de.embedding, query_embedding) as similarity,
        de.metadata
    FROM document_embeddings de
    WHERE de.namespace = target_namespace
    AND cosine_similarity(de.embedding, query_embedding) > similarity_threshold
    ORDER BY similarity DESC
    LIMIT max_results;
$$;

-- Search knowledge base function
CREATE OR REPLACE FUNCTION search_knowledge_base(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10,
    target_category varchar DEFAULT NULL
)
RETURNS TABLE (
    id integer,
    knowledge_item_id varchar,
    title varchar,
    content text,
    category varchar,
    similarity float,
    metadata jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT 
        kbe.id,
        kbe.knowledge_item_id,
        kbe.title,
        kbe.content,
        kbe.category,
        cosine_similarity(kbe.embedding, query_embedding) as similarity,
        kbe.metadata
    FROM knowledge_base_embeddings kbe
    WHERE cosine_similarity(kbe.embedding, query_embedding) > similarity_threshold
    AND (target_category IS NULL OR kbe.category = target_category)
    ORDER BY similarity DESC
    LIMIT max_results;
$$;

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Insert default admin user
INSERT INTO users (
    email, username, first_name, last_name, hashed_password, role, is_active, is_verified
) VALUES (
    'admin@lcnc.local',
    'admin',
    'System',
    'Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LKO8F3ZH9VdGQ1oC6', -- password: admin123
    'ADMIN',
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert default project
INSERT INTO projects (name, description, tags, is_default, created_by) VALUES
('Default Project', 'The default project for general use', ARRAY['general', 'default'], true, 'system')
ON CONFLICT (name) DO NOTHING;

-- Insert essential sample projects
INSERT INTO projects (name, description, tags, created_by) VALUES
('Customer Support', 'Customer service and support automation', ARRAY['support', 'customer', 'automation'], 'system'),
('Data Analytics', 'Data analysis and reporting workflows', ARRAY['analytics', 'data', 'reporting'], 'system')
ON CONFLICT (name) DO NOTHING;

-- Insert essential sample agents
INSERT INTO agents (name, display_name, description, url, health_url, category, ai_provider, model_name, tags, project_tags, author, organization, environment, created_by) VALUES
('customer-service-agent', 'Customer Service Agent', 'AI agent for customer service interactions', 'http://localhost:8002/a2a/agents/customer-service', 'http://localhost:8002/health', 'customer-service', 'gemini', 'gemini-1.5-pro', ARRAY['customer', 'support', 'service'], ARRAY['support', 'customer'], 'Platform Team', 'LCNC Platform', 'development', 'system'),
('data-analyst-agent', 'Data Analyst Agent', 'AI agent for data analysis tasks', 'http://localhost:8002/a2a/agents/data-analyst', 'http://localhost:8002/health', 'analytics', 'gemini', 'gemini-1.5-pro', ARRAY['data', 'analysis', 'analytics'], ARRAY['analytics', 'data'], 'Platform Team', 'LCNC Platform', 'development', 'system')
ON CONFLICT (name) DO NOTHING;

-- Insert essential tool templates
INSERT INTO tool_templates (name, display_name, description, category, type, project_tags, tags, status, created_by) VALUES
('email-parser', 'Email Parser', 'Parses and extracts information from emails', 'Communication', 'nlp', ARRAY['support', 'customer'], ARRAY['email', 'parsing', 'nlp'], 'active', 'system'),
('sentiment-analyzer', 'Sentiment Analyzer', 'Analyzes sentiment in customer feedback', 'Analytics', 'nlp', ARRAY['support', 'customer'], ARRAY['sentiment', 'nlp', 'analysis'], 'active', 'system'),
('api-monitor', 'API Monitor', 'Monitors API endpoints and performance', 'Monitoring', 'system', ARRAY['general', 'default'], ARRAY['monitoring', 'api', 'performance'], 'active', 'system')
ON CONFLICT (name) DO NOTHING;

-- Insert essential LLM models
INSERT INTO llm_models (name, display_name, provider, model_type, supports_streaming, supports_functions, is_active, project_tags) VALUES
('gpt-4o', 'GPT-4o', 'openai', 'chat', true, true, true, ARRAY['general', 'default']),
('gemini-1.5-pro', 'Gemini 1.5 Pro', 'google', 'chat', true, false, true, ARRAY['general', 'default'])
ON CONFLICT (name) DO NOTHING;

-- Insert essential embedding model
INSERT INTO embedding_models (name, display_name, provider, dimensions, max_input_tokens, is_active, project_tags) VALUES
('text-embedding-3-small', 'OpenAI Text Embedding 3 Small', 'openai', 1536, 8191, true, ARRAY['general', 'default'])
ON CONFLICT (name) DO NOTHING;

-- Insert essential workflow definitions
INSERT INTO workflow_definitions (name, display_name, description, category, tags, project_tags, steps, variables, created_by) VALUES
('customer-support-pipeline', 'Customer Support Pipeline', 'Automated customer inquiry processing', 'customer-service', ARRAY['support', 'automation'], ARRAY['support', 'customer'], '[{"step": "classify", "agent": "customer-service-agent"}, {"step": "respond", "agent": "customer-service-agent"}]', '{"max_retries": 3}', 'system'),
('data-analysis-pipeline', 'Data Analysis Pipeline', 'Automated data analysis workflow', 'analytics', ARRAY['data', 'analysis'], ARRAY['analytics', 'data'], '[{"step": "analyze", "agent": "data-analyst-agent"}, {"step": "report", "tool": "report-generator"}]', '{"batch_size": 1000}', 'system')
ON CONFLICT (name) DO NOTHING;

-- Insert essential demo queries
INSERT INTO demo_sample_queries (service_type, category, query_text, description, complexity_level, is_featured, sort_order) VALUES
('agents', 'discovery', 'List all available agents', 'Get overview of available AI agents', 'beginner', true, 1),
('tools', 'discovery', 'Show available tool templates', 'Display tool templates for integration', 'beginner', true, 2),
('workflows', 'creation', 'Create basic workflow', 'Design a simple automation workflow', 'intermediate', true, 3),
('rag', 'search', 'Search knowledge base', 'Semantic search through documents', 'beginner', true, 4)
ON CONFLICT DO NOTHING;

-- Link agents to workflows
INSERT INTO workflow_agents (workflow_id, agent_id, role, sequence_order)
SELECT 
    wd.id as workflow_id,
    a.id as agent_id,
    'primary' as role,
    1 as sequence_order
FROM workflow_definitions wd
CROSS JOIN agents a
WHERE 
    (wd.name = 'customer-support-pipeline' AND a.name = 'customer-service-agent') OR
    (wd.name = 'data-analysis-pipeline' AND a.name = 'data-analyst-agent')
ON CONFLICT DO NOTHING;

-- Update execution statistics with sample data
UPDATE agents SET 
    execution_count = FLOOR(RANDOM() * 500 + 50),
    success_rate = ROUND((RANDOM() * 10 + 90)::numeric, 1),
    avg_response_time = FLOOR(RANDOM() * 2000 + 500),
    last_executed = CURRENT_TIMESTAMP - (RANDOM() * INTERVAL '7 days')
WHERE name IN ('customer-service-agent', 'data-analyst-agent');

UPDATE workflow_definitions SET 
    status = 'active'
WHERE name IN ('customer-support-pipeline', 'data-analysis-pipeline');

-- Insert sample knowledge base content
INSERT INTO knowledge_base_embeddings (knowledge_item_id, title, content, category, tags, metadata) VALUES
('kb-001', 'Platform Overview', 'The LCNC Platform is a low-code/no-code multi-agent AI platform that enables users to create, deploy, and manage AI agents, tools, and workflows.', 'platform', ARRAY['overview', 'platform', 'introduction'], '{"type": "documentation", "version": "1.0"}'),
('kb-002', 'Agent Management', 'Agents are AI-powered entities that can perform specific tasks. They can be configured with different models, capabilities, and integration points.', 'agents', ARRAY['agents', 'management', 'configuration'], '{"type": "documentation", "section": "agents"}'),
('kb-003', 'Workflow Automation', 'Workflows enable the orchestration of multiple agents and tools to create complex automation pipelines with conditional logic and error handling.', 'workflows', ARRAY['workflows', 'automation', 'orchestration'], '{"type": "documentation", "section": "workflows"}')
ON CONFLICT (knowledge_item_id) DO NOTHING;
