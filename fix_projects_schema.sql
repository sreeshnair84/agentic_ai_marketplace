-- Fix Projects Table Schema: Convert UUID columns to VARCHAR
-- This addresses the datatype mismatch error where created_by and updated_by
-- are defined as UUID in the database but the application expects VARCHAR

\echo 'Starting Projects Schema Fix...'

-- Check current schema
\echo 'Current schema for created_by and updated_by:'
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'projects' 
    AND column_name IN ('created_by', 'updated_by')
ORDER BY column_name;

-- Check current data
\echo 'Current data in projects table:'
SELECT id, name, created_by, updated_by FROM projects LIMIT 3;

-- Step 1: Convert created_by from UUID to VARCHAR(255)
\echo 'Converting created_by column from UUID to VARCHAR(255)...'
ALTER TABLE projects 
ALTER COLUMN created_by TYPE VARCHAR(255) 
USING CASE 
    WHEN created_by IS NULL THEN NULL
    ELSE created_by::text 
END;

-- Step 2: Convert updated_by from UUID to VARCHAR(255)  
\echo 'Converting updated_by column from UUID to VARCHAR(255)...'
ALTER TABLE projects 
ALTER COLUMN updated_by TYPE VARCHAR(255) 
USING CASE 
    WHEN updated_by IS NULL THEN NULL
    ELSE updated_by::text 
END;

-- Step 3: Set default values for existing NULL records
\echo 'Setting default values for NULL created_by records...'
UPDATE projects 
SET created_by = 'system' 
WHERE created_by IS NULL;

\echo 'Setting default values for NULL updated_by records...'
UPDATE projects 
SET updated_by = 'system' 
WHERE updated_by IS NULL;

-- Step 4: Verify the changes
\echo 'Verifying schema changes:'
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

\echo 'Verifying data after conversion:'
SELECT id, name, created_by, updated_by, 
       pg_typeof(created_by) as created_by_type,
       pg_typeof(updated_by) as updated_by_type
FROM projects 
LIMIT 5;

\echo 'Projects Schema Fix Complete!'