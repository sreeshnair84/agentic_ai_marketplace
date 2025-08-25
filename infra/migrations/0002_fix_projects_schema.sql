-- Migration: Fix Projects Schema - Convert created_by and updated_by from UUID to VARCHAR
-- 
-- Problem: The original schema defined created_by and updated_by as UUID REFERENCES users(id)
-- but the application code expects to store string values like 'system', 'admin', etc.
-- 
-- Solution: Convert these columns to VARCHAR(255) to match the application expectations
-- and SQLAlchemy model definitions.

\echo 'Starting migration: Fix Projects Schema (UUID to VARCHAR conversion)'
\echo 'Timestamp:' $(date)

-- Step 1: Check current state
\echo '=== BEFORE MIGRATION ==='
\echo 'Current column types:'
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'projects' 
    AND column_name IN ('created_by', 'updated_by')
ORDER BY column_name;

\echo 'Current data sample:'
SELECT id, name, created_by, updated_by FROM projects LIMIT 3;

-- Step 2: Drop foreign key constraints first
\echo '=== DROPPING FOREIGN KEY CONSTRAINTS ==='

-- Find and drop the foreign key constraints
DO $$
DECLARE
    constraint_record RECORD;
BEGIN
    -- Find foreign key constraints on created_by and updated_by
    FOR constraint_record IN 
        SELECT 
            conname as constraint_name,
            conrelid::regclass as table_name,
            a.attname as column_name
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attnum = ANY(c.conkey)
        WHERE conrelid = 'projects'::regclass
        AND confrelid IS NOT NULL  -- Only foreign key constraints
        AND a.attname IN ('created_by', 'updated_by')
    LOOP
        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT IF EXISTS %s', 
                      constraint_record.table_name, 
                      constraint_record.constraint_name);
        RAISE NOTICE 'Dropped constraint: %', constraint_record.constraint_name;
    END LOOP;
END $$;

-- Step 3: Convert columns to VARCHAR
\echo '=== CONVERTING COLUMN TYPES ==='

\echo 'Converting created_by from UUID to VARCHAR(255)...'
ALTER TABLE projects 
ALTER COLUMN created_by TYPE VARCHAR(255) 
USING CASE 
    WHEN created_by IS NULL THEN NULL
    ELSE created_by::text 
END;

\echo 'Converting updated_by from UUID to VARCHAR(255)...'
ALTER TABLE projects 
ALTER COLUMN updated_by TYPE VARCHAR(255) 
USING CASE 
    WHEN updated_by IS NULL THEN NULL
    ELSE updated_by::text 
END;

-- Step 4: Update existing data with proper default values
\echo '=== UPDATING EXISTING DATA ==='

-- Convert any UUID strings to 'system' for consistency
UPDATE projects 
SET created_by = 'system' 
WHERE created_by IS NULL 
   OR created_by ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';

UPDATE projects 
SET updated_by = 'system' 
WHERE updated_by IS NULL 
   OR updated_by ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';

-- Step 5: Verify the migration
\echo '=== AFTER MIGRATION ==='
\echo 'New column types:'
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'projects' 
    AND column_name IN ('created_by', 'updated_by')
ORDER BY column_name;

\echo 'Updated data sample:'
SELECT id, name, created_by, updated_by,
       pg_typeof(created_by) as created_by_type,
       pg_typeof(updated_by) as updated_by_type
FROM projects 
LIMIT 5;

\echo 'Data validation:'
SELECT 
    COUNT(*) as total_projects,
    COUNT(created_by) as projects_with_created_by,
    COUNT(updated_by) as projects_with_updated_by
FROM projects;

\echo 'Migration completed successfully!'
\echo 'Timestamp:' $(date)