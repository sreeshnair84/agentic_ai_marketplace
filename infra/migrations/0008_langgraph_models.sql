-- Migration: Add LangGraph model management tables
-- Description: Create tables for managing LLM and embedding models with LangGraph integration
-- Date: 2025-01-15

-- Create models table for storing LLM and embedding model configurations
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('openai', 'azure_openai', 'google_gemini', 'ollama')),
    model_type VARCHAR(20) NOT NULL CHECK (model_type IN ('llm', 'embedding')),
    api_endpoint TEXT,
    api_key_encrypted TEXT, -- Store encrypted API keys
    status VARCHAR(20) NOT NULL DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'testing', 'error')),
    capabilities JSONB DEFAULT '{}',
    pricing_info JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    model_config JSONB DEFAULT '{}',
    health_url TEXT,
    dns_name VARCHAR(255),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Unique constraints
    CONSTRAINT unique_model_name_provider UNIQUE (name, provider),
    CONSTRAINT unique_default_per_type EXCLUDE (model_type WITH =) WHERE (is_default = TRUE)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_models_provider ON models(provider);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);
CREATE INDEX IF NOT EXISTS idx_models_status ON models(status);
CREATE INDEX IF NOT EXISTS idx_models_default ON models(model_type) WHERE is_default = TRUE;
CREATE INDEX IF NOT EXISTS idx_models_created_at ON models(created_at);
CREATE INDEX IF NOT EXISTS idx_models_updated_at ON models(updated_at);

-- Create model usage tracking table
CREATE TABLE IF NOT EXISTS model_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    usage_type VARCHAR(50) NOT NULL CHECK (usage_type IN ('chat', 'embedding', 'completion', 'test')),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    latency_ms INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for analytics
    INDEX (model_id, timestamp),
    INDEX (user_id, timestamp),
    INDEX (usage_type, timestamp),
    INDEX (success, timestamp)
);

-- Create model configuration history table for audit trail
CREATE TABLE IF NOT EXISTS model_config_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('created', 'updated', 'deleted', 'activated', 'deactivated')),
    old_config JSONB,
    new_config JSONB,
    changed_fields TEXT[],
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    change_reason TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on model_config_history
CREATE INDEX IF NOT EXISTS idx_model_config_history_model_timestamp ON model_config_history(model_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_model_config_history_change_type ON model_config_history(change_type);

-- Insert default model templates (examples)
INSERT INTO models (
    name, 
    display_name, 
    provider, 
    model_type, 
    capabilities,
    pricing_info,
    model_config,
    status,
    is_default
) VALUES 
(
    'gpt-4', 
    'GPT-4', 
    'openai', 
    'llm',
    '{"max_tokens": 8192, "supports_streaming": true, "supports_function_calling": true, "input_modalities": ["text"], "output_modalities": ["text"]}',
    '{"input_cost_per_token": 0.00003, "output_cost_per_token": 0.00006, "currency": "USD"}',
    '{"temperature": 0.7, "max_tokens": 4096, "top_p": 1.0, "frequency_penalty": 0.0, "presence_penalty": 0.0}',
    'inactive',
    false
),
(
    'text-embedding-ada-002',
    'OpenAI Ada v2',
    'openai',
    'embedding',
    '{"dimensions": 1536, "max_input_tokens": 8191, "supports_batching": true, "supported_languages": ["en", "es", "fr", "de", "it", "pt"]}',
    '{"cost_per_token": 0.0000001, "currency": "USD"}',
    '{"dimensions": 1536, "batch_size": 512, "normalize": true}',
    'inactive',
    false
),
(
    'gemini-pro',
    'Gemini Pro',
    'google_gemini',
    'llm',
    '{"max_tokens": 30720, "supports_streaming": true, "supports_function_calling": false, "input_modalities": ["text", "image"], "output_modalities": ["text"]}',
    '{"input_cost_per_token": 0.000125, "output_cost_per_token": 0.000375, "currency": "USD"}',
    '{"temperature": 0.7, "max_tokens": 4096, "top_p": 1.0}',
    'inactive',
    false
),
(
    'models/embedding-001',
    'Gemini Embedding',
    'google_gemini',
    'embedding',
    '{"dimensions": 768, "max_input_tokens": 2048, "supports_batching": true, "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"]}',
    '{"cost_per_token": 0.0000001, "currency": "USD"}',
    '{"dimensions": 768, "batch_size": 100, "normalize": true}',
    'inactive',
    false
)
ON CONFLICT (name, provider) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for models table
DROP TRIGGER IF EXISTS update_models_updated_at ON models;
CREATE TRIGGER update_models_updated_at
    BEFORE UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to log model configuration changes
CREATE OR REPLACE FUNCTION log_model_config_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO model_config_history (
            model_id, 
            change_type, 
            new_config, 
            changed_by
        ) VALUES (
            NEW.id, 
            'created', 
            row_to_json(NEW), 
            NEW.created_by
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO model_config_history (
            model_id, 
            change_type, 
            old_config, 
            new_config, 
            changed_by
        ) VALUES (
            NEW.id, 
            CASE 
                WHEN OLD.status != NEW.status AND NEW.status = 'active' THEN 'activated'
                WHEN OLD.status != NEW.status AND NEW.status = 'inactive' THEN 'deactivated'
                ELSE 'updated'
            END, 
            row_to_json(OLD), 
            row_to_json(NEW), 
            NEW.updated_by
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO model_config_history (
            model_id, 
            change_type, 
            old_config
        ) VALUES (
            OLD.id, 
            'deleted', 
            row_to_json(OLD)
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create trigger for model configuration logging
DROP TRIGGER IF EXISTS log_model_changes ON models;
CREATE TRIGGER log_model_changes
    AFTER INSERT OR UPDATE OR DELETE ON models
    FOR EACH ROW
    EXECUTE FUNCTION log_model_config_changes();

-- Create function to ensure only one default per model type
CREATE OR REPLACE FUNCTION ensure_single_default()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = TRUE THEN
        -- Unset other defaults for the same model type
        UPDATE models 
        SET is_default = FALSE 
        WHERE model_type = NEW.model_type 
          AND id != NEW.id 
          AND is_default = TRUE;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for default model enforcement
DROP TRIGGER IF EXISTS ensure_single_default_trigger ON models;
CREATE TRIGGER ensure_single_default_trigger
    BEFORE INSERT OR UPDATE ON models
    FOR EACH ROW
    EXECUTE FUNCTION ensure_single_default();

-- Create view for model analytics
CREATE OR REPLACE VIEW model_usage_analytics AS
SELECT 
    m.id,
    m.name,
    m.display_name,
    m.provider,
    m.model_type,
    m.status,
    COUNT(mul.id) as total_requests,
    COUNT(CASE WHEN mul.success THEN 1 END) as successful_requests,
    COUNT(CASE WHEN NOT mul.success THEN 1 END) as failed_requests,
    ROUND(AVG(mul.latency_ms)) as avg_latency_ms,
    SUM(mul.input_tokens) as total_input_tokens,
    SUM(mul.output_tokens) as total_output_tokens,
    SUM(mul.total_tokens) as total_tokens,
    SUM(mul.cost_usd) as total_cost_usd,
    MIN(mul.timestamp) as first_used,
    MAX(mul.timestamp) as last_used
FROM models m
LEFT JOIN model_usage_logs mul ON m.id = mul.model_id
GROUP BY m.id, m.name, m.display_name, m.provider, m.model_type, m.status;

-- Create view for active models
CREATE OR REPLACE VIEW active_models AS
SELECT 
    id,
    name,
    display_name,
    provider,
    model_type,
    capabilities,
    pricing_info,
    model_config,
    is_default,
    created_at,
    updated_at
FROM models
WHERE status = 'active';

-- Grant permissions (adjust based on your user roles)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON models TO application_user;
-- GRANT SELECT, INSERT ON model_usage_logs TO application_user;
-- GRANT SELECT ON model_config_history TO application_user;
-- GRANT SELECT ON model_usage_analytics TO application_user;
-- GRANT SELECT ON active_models TO application_user;