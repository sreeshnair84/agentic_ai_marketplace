-- Fix any UUID values in created_by and updated_by fields
-- These fields should be strings, not UUIDs

-- First, let's see what we have
SELECT id, name, created_by, updated_by, 
       pg_typeof(created_by) as created_by_type,
       pg_typeof(updated_by) as updated_by_type
FROM projects 
LIMIT 5;

-- If there are any UUID values, convert them to strings
-- This handles cases where UUIDs were accidentally stored in string fields
UPDATE projects 
SET created_by = CASE 
    WHEN created_by ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' 
    THEN created_by::text
    ELSE created_by 
END
WHERE created_by IS NOT NULL;

UPDATE projects 
SET updated_by = CASE 
    WHEN updated_by ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' 
    THEN updated_by::text
    ELSE updated_by 
END
WHERE updated_by IS NOT NULL;

-- Clean up any NULL or problematic values by setting them to 'system'
UPDATE projects 
SET created_by = 'system' 
WHERE created_by IS NULL OR created_by = '';

UPDATE projects 
SET updated_by = 'system' 
WHERE updated_by IS NULL OR updated_by = '';

-- Verify the results
SELECT id, name, created_by, updated_by,
       pg_typeof(created_by) as created_by_type,
       pg_typeof(updated_by) as updated_by_type
FROM projects;