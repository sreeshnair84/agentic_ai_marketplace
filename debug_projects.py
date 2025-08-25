#!/usr/bin/env python3
"""
Debug script to check the actual data in the projects table
"""

import asyncio
import asyncpg
import os
from typing import List, Dict, Any

async def debug_projects_table():
    """Debug what's actually in the projects table"""
    
    # Database connection string (adjust as needed)
    database_url = os.getenv('DATABASE_URL', 'postgresql://admin:admin123@localhost:5432/multiagent_platform')
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        print("🔍 Checking projects table schema...")
        
        # Check table schema
        schema_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'projects'
        ORDER BY ordinal_position;
        """
        
        schema_rows = await conn.fetch(schema_query)
        print("\n📋 Table Schema:")
        for row in schema_rows:
            print(f"  - {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
        
        print("\n" + "="*50 + "\n")
        
        # Check actual data
        data_query = """
        SELECT id, name, created_by, updated_by, created_at
        FROM projects
        LIMIT 5;
        """
        
        data_rows = await conn.fetch(data_query)
        print(f"📊 Found {len(data_rows)} projects:")
        
        for i, row in enumerate(data_rows, 1):
            print(f"\n  Project {i}:")
            print(f"    ID: {row['id']} (type: {type(row['id'])})")
            print(f"    Name: {row['name']}")
            print(f"    Created By: {row['created_by']} (type: {type(row['created_by'])})")
            print(f"    Updated By: {row['updated_by']} (type: {type(row['updated_by'])})")
            print(f"    Created At: {row['created_at']}")
        
        print("\n" + "="*50 + "\n")
        
        # Check for UUID values in created_by field
        uuid_check_query = """
        SELECT id, name, created_by, updated_by
        FROM projects
        WHERE created_by ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
           OR updated_by ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';
        """
        
        uuid_rows = await conn.fetch(uuid_check_query)
        print(f"🆔 Found {len(uuid_rows)} projects with UUID-like strings in created_by/updated_by:")
        
        for row in uuid_rows:
            print(f"  - {row['name']}: created_by='{row['created_by']}', updated_by='{row['updated_by']}'")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Trying alternative connection...")
        
        # Try with Docker network
        alt_database_url = 'postgresql://admin:admin123@postgres:5432/multiagent_platform'
        try:
            conn = await asyncpg.connect(alt_database_url)
            print("✅ Connected with alternative URL")
            await conn.close()
        except Exception as e2:
            print(f"❌ Alternative connection also failed: {e2}")

if __name__ == "__main__":
    print("🚀 Starting Projects Table Debug\n")
    asyncio.run(debug_projects_table())
    print("\n✅ Debug completed!")