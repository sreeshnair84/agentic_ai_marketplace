#!/usr/bin/env python3
"""
Simple database setup script for debugging
"""
import asyncio
import asyncpg
from pathlib import Path

DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

async def setup_database():
    """Setup database with migrations"""
    try:
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Execute migration files
        migrations_dir = Path("infra/migrations")
        migration_files = sorted([f for f in migrations_dir.glob("*.sql")])
        
        for migration_file in migration_files:
            print(f"📄 Executing migration: {migration_file.name}")
            migration_sql = migration_file.read_text(encoding='utf-8')
            
            try:
                await conn.execute(migration_sql)
                print(f"✅ Applied migration: {migration_file.name}")
            except Exception as e:
                print(f"❌ Migration failed: {migration_file.name}")
                print(f"   Error: {e}")
                await conn.close()
                return False
        
        await conn.close()
        print("✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    if not success:
        exit(1)
