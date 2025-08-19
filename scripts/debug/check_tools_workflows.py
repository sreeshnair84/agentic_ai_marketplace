#!/usr/bin/env python3
"""
Check tools and workflows table schemas
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

async def check_schemas():
    """Check current schemas for tools and workflows"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("📊 Columns in tool_templates table:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'tool_templates'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        print(f"\n📊 Tool templates count:")
        count = await conn.fetchval("SELECT COUNT(*) FROM tool_templates")
        print(f"  Tools: {count}")
        
        print(f"\n📊 Columns in workflow_definitions table:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'workflow_definitions'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        print(f"\n📊 Workflow definitions count:")
        count = await conn.fetchval("SELECT COUNT(*) FROM workflow_definitions")
        print(f"  Workflows: {count}")
        
        # Check sample data
        print("\n📋 Sample tool templates:")
        tools = await conn.fetch("SELECT name, display_name, health_url, dns_name FROM tool_templates LIMIT 3")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['display_name']} @ {tool['dns_name']} (health: {tool['health_url']})")
        
        print("\n📋 Sample workflow definitions:")
        workflows = await conn.fetch("SELECT name, display_name, health_url, dns_name FROM workflow_definitions LIMIT 3")
        for workflow in workflows:
            print(f"  - {workflow['name']}: {workflow['display_name']} @ {workflow['dns_name']} (health: {workflow['health_url']})")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_schemas())
