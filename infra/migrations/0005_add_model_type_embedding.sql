-- Migration: add model_type to embedding_models
-- Adds a model_type column and populates existing rows with 'embedding'

ALTER TABLE embedding_models
ADD COLUMN IF NOT EXISTS model_type VARCHAR(50) DEFAULT 'embedding';

-- Ensure existing rows have the model_type set
UPDATE embedding_models SET model_type = 'embedding' WHERE model_type IS NULL;
