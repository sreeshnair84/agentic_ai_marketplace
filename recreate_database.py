#!/usr/bin/env python3
"""
Drop and recreate database for fresh setup
"""
import asyncio
import asyncpg
import sys

POSTGRES_ADMIN_URL = "postgresql://postgres:password@localhost:5432/postgres"
DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

async def recreate_database():
    """Drop and recreate database"""
    try:
        print("🗑️ Dropping existing database...")
        # Connect to postgres admin database
        admin_conn = await asyncpg.connect(POSTGRES_ADMIN_URL)
        
        # Terminate existing connections
        await admin_conn.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = 'agenticai_platform' AND pid <> pg_backend_pid()
        """)
        
        # Drop database
        await admin_conn.execute("DROP DATABASE IF EXISTS agenticai_platform")
        print("✅ Database dropped")
        
        # Recreate database
        await admin_conn.execute("CREATE DATABASE agenticai_platform")
        print("✅ Database created")
        
        await admin_conn.close()
        
        # Create user and grant permissions
        print("👤 Setting up user permissions...")
        admin_conn = await asyncpg.connect(POSTGRES_ADMIN_URL)
        
        # Create user if not exists
        await admin_conn.execute("""
            DO $$ 
            BEGIN
                CREATE USER agenticai_user WITH PASSWORD 'agenticai_password';
            EXCEPTION 
                WHEN duplicate_object THEN 
                    RAISE NOTICE 'User already exists';
            END
            $$;
        """)
        
        # Grant permissions
        await admin_conn.execute("GRANT ALL PRIVILEGES ON DATABASE agenticai_platform TO agenticai_user")
        await admin_conn.close()
        
        # Connect to new database and grant schema permissions
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("GRANT ALL ON SCHEMA public TO agenticai_user")
        await conn.close()
        
        print("✅ Database recreation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database recreation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(recreate_database())
    if not success:
        sys.exit(1)
