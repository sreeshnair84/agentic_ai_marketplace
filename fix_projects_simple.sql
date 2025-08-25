-- Simple Projects Schema Fix
-- Convert created_by and updated_by columns from UUID to VARCHAR(255)

-- Drop foreign key constraints (if they exist)
DO $$
DECLARE
    constraint_record RECORD;
BEGIN
    FOR constraint_record IN 
        SELECT conname as constraint_name
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attnum = ANY(c.conkey)
        WHERE conrelid = 'projects'::regclass
        AND confrelid IS NOT NULL
        AND a.attname IN ('created_by', 'updated_by')
    LOOP
        EXECUTE format('ALTER TABLE projects DROP CONSTRAINT IF EXISTS %s', 
                      constraint_record.constraint_name);
    END LOOP;
END $$;

-- Convert columns to VARCHAR
ALTER TABLE projects 
ALTER COLUMN created_by TYPE VARCHAR(255) 
USING CASE 
    WHEN created_by IS NULL THEN NULL
    ELSE created_by::text 
END;

ALTER TABLE projects 
ALTER COLUMN updated_by TYPE VARCHAR(255) 
USING CASE 
    WHEN updated_by IS NULL THEN NULL
    ELSE updated_by::text 
END;

-- Set default values for existing records
UPDATE projects 
SET created_by = 'system' 
WHERE created_by IS NULL;

UPDATE projects 
SET updated_by = 'system' 
WHERE updated_by IS NULL;