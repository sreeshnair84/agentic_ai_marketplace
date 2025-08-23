-- Migration to add 'url' column to workflow_definitions table
ALTER TABLE workflow_definitions ADD COLUMN url TEXT;
ALTER TABLE workflow_definitions ADD COLUMN capabilities JSONB DEFAULT '[]';
ALTER TABLE workflow_definitions ADD COLUMN default_input_modes JSONB DEFAULT '[]';
ALTER TABLE workflow_definitions ADD COLUMN default_output_modes JSONB DEFAULT '[]';

ALTER TABLE agents ADD COLUMN default_input_modes JSONB DEFAULT '[]';
ALTER TABLE agents ADD COLUMN default_output_modes JSONB DEFAULT '[]';
ALTER TABLE tool_templates ADD COLUMN capabilities JSONB DEFAULT '[]';
ALTER TABLE tool_templates ADD COLUMN default_input_modes JSONB DEFAULT '[]';
ALTER TABLE tool_templates ADD COLUMN default_output_modes JSONB DEFAULT '[]';

