-- Migration: Drop embedding_models table and migrate data to models table
-- Date: 2025-08-22

-- 1. Migrate data from embedding_models to models (if any rows exist)
INSERT INTO models (
    id, name, display_name, provider, model_type, api_endpoint, status, capabilities, pricing_info, model_config, is_default, created_at, updated_at
)
SELECT 
    id, name, display_name, provider, 'embedding' AS model_type, endpoint_url, 
    CASE WHEN is_active THEN 'active' ELSE 'inactive' END AS status,
    jsonb_build_object('dimensions', dimensions, 'max_input_tokens', max_input_tokens),
    COALESCE(pricing_info, '{}'::jsonb),
    '{}'::jsonb, -- model_config placeholder, adjust if needed
    FALSE AS is_default,
    created_at,
    updated_at
FROM embedding_models
ON CONFLICT (id) DO NOTHING;

-- 2. Drop embedding_models table
DROP TABLE IF EXISTS embedding_models CASCADE;

-- 3. Drop related indexes if not already dropped
DROP INDEX IF EXISTS idx_embedding_models_project_tags;
DROP INDEX IF EXISTS idx_embedding_models_provider;
DROP INDEX IF EXISTS idx_embedding_models_is_active;

-- 4. (Optional) Remove references in other tables if any
-- (Add ALTER TABLE ... DROP CONSTRAINT ... if needed)

-- End of migration
