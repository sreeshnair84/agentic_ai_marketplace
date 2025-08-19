#!/usr/bin/env python3
"""
Check agents table schema
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

async def check_agents():
    """Check agents table schema and data"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("📊 Columns in agents table:")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'agents'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        print(f"\n📊 Current agents count:")
        count = await conn.fetchval("SELECT COUNT(*) FROM agents")
        print(f"  Agents: {count}")
        
        print(f"\n📊 Current demo queries count:")
        count = await conn.fetchval("SELECT COUNT(*) FROM demo_sample_queries")
        print(f"  Demo queries: {count}")
        
        if count > 0:
            print("\n📋 Sample demo queries:")
            queries = await conn.fetch("SELECT service_type, category, query_text FROM demo_sample_queries LIMIT 3")
            for query in queries:
                print(f"  - {query['service_type']}/{query['category']}: {query['query_text']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_agents())
