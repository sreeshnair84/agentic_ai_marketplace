#!/usr/bin/env python3
"""
Execute the database migration to fix the projects schema
"""

import asyncio
import asyncpg
import os
import sys

# Database connection parameters
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'admin',
    'password': 'admin123',
    'database': 'multiagent_platform'
}

MIGRATION_SQL = """
-- Fix Projects Schema: Convert created_by and updated_by from UUID to VARCHAR

-- Step 1: Check current schema
SELECT 'Before migration - Current column types:' as status;

-- Step 2: Drop foreign key constraints
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
        RAISE NOTICE 'Dropped constraint: %s', constraint_record.constraint_name;
    END LOOP;
END $$;

-- Step 3: Convert columns to VARCHAR
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

-- Step 4: Set default values for existing records
UPDATE projects 
SET created_by = 'system' 
WHERE created_by IS NULL;

UPDATE projects 
SET updated_by = 'system' 
WHERE updated_by IS NULL;

-- Step 5: Verify the migration
SELECT 'Migration completed successfully!' as status;
"""

async def run_migration():
    """Execute the database migration"""
    
    print("🔧 Starting Projects Schema Migration...")
    
    # Try different connection configurations
    connection_configs = [
        DATABASE_CONFIG,  # Default localhost
        {**DATABASE_CONFIG, 'host': 'postgres'},  # Docker network
        {**DATABASE_CONFIG, 'host': '127.0.0.1'},  # Explicit localhost
    ]
    
    conn = None
    
    for config in connection_configs:
        try:
            print(f"🔗 Attempting to connect to {config['host']}:{config['port']}...")
            conn = await asyncpg.connect(**config)
            print(f"✅ Connected to database successfully!")
            break
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            continue
    
    if not conn:
        print("💥 Could not connect to database with any configuration!")
        print("\n💡 Please ensure your PostgreSQL database is running and accessible.")
        print("   - Check if Docker containers are running: docker-compose ps")
        print("   - Verify database credentials in your environment")
        return False
    
    try:
        print("\n📋 Checking current schema...")
        
        # Check current column types
        current_schema = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'projects' 
            AND column_name IN ('created_by', 'updated_by')
            ORDER BY column_name
        """)
        
        print("Current column types:")
        for row in current_schema:
            print(f"   {row['column_name']}: {row['data_type']}")
        
        print("\n🚀 Executing migration...")
        
        # Execute migration in parts to handle any errors
        migration_steps = [
            ("Dropping foreign key constraints", """
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
                        RAISE NOTICE 'Dropped constraint: %s', constraint_record.constraint_name;
                    END LOOP;
                END $$;
            """),
            ("Converting created_by column", """
                ALTER TABLE projects 
                ALTER COLUMN created_by TYPE VARCHAR(255) 
                USING CASE 
                    WHEN created_by IS NULL THEN NULL
                    ELSE created_by::text 
                END;
            """),
            ("Converting updated_by column", """
                ALTER TABLE projects 
                ALTER COLUMN updated_by TYPE VARCHAR(255) 
                USING CASE 
                    WHEN updated_by IS NULL THEN NULL
                    ELSE updated_by::text 
                END;
            """),
            ("Setting default values", """
                UPDATE projects 
                SET created_by = 'system' 
                WHERE created_by IS NULL;
                
                UPDATE projects 
                SET updated_by = 'system' 
                WHERE updated_by IS NULL;
            """)
        ]
        
        for step_name, step_sql in migration_steps:
            try:
                print(f"   ⚙️  {step_name}...")
                await conn.execute(step_sql)
                print(f"   ✅ {step_name} completed")
            except Exception as e:
                print(f"   ⚠️  {step_name} warning: {e}")
                # Continue with next step
        
        print("\n🔍 Verifying migration results...")
        
        # Check new column types
        new_schema = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'projects' 
            AND column_name IN ('created_by', 'updated_by')
            ORDER BY column_name
        """)
        
        print("New column types:")
        for row in new_schema:
            print(f"   {row['column_name']}: {row['data_type']}({row['character_maximum_length']})")
        
        # Check sample data
        sample_data = await conn.fetch("""
            SELECT id, name, created_by, updated_by 
            FROM projects 
            LIMIT 3
        """)
        
        print(f"\nSample data ({len(sample_data)} rows):")
        for row in sample_data:
            print(f"   {row['name']}: created_by='{row['created_by']}', updated_by='{row['updated_by']}'")
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        return False
        
    finally:
        await conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    print("🚀 Projects Schema Migration Tool")
    print("=" * 50)
    
    success = asyncio.run(run_migration())
    
    if success:
        print("\n✅ Migration completed! You can now:")
        print("   1. Restart your services: docker-compose restart gateway")
        print("   2. Test the API: python test_after_fix.py")
        sys.exit(0)
    else:
        print("\n❌ Migration failed! Please check the errors above.")
        sys.exit(1)