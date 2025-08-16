#!/usr/bin/env python3
"""
Check existing database schema
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform"

async def check_schema():
    """Check current database schema"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("📊 Current tables in database:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        for table in tables:
            print(f"  - {table['table_name']}")
        
        print("\n📊 Columns in tool_templates:")
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tool_templates'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_schema())
