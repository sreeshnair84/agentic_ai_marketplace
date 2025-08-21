-- Migration: add pricing_info JSON column to llm_models and embedding_models
ALTER TABLE llm_models ADD COLUMN IF NOT EXISTS pricing_info JSONB DEFAULT '{}'::jsonb;
ALTER TABLE embedding_models ADD COLUMN IF NOT EXISTS pricing_info JSONB DEFAULT '{}'::jsonb;
