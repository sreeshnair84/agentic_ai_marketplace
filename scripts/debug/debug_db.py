#!/usr/bin/env python3
"""
Debug database structure and API query
"""

import asyncio
import asyncpg
from sqlalchemy import text

async def debug_db():
    try:
        # Connect to database
        conn = await asyncpg.connect('postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform')
        
        # Check table structure
        print("=== LLM_MODELS TABLE STRUCTURE ===")
        result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'llm_models' 
            ORDER BY ordinal_position
        """)
        
        for row in result:
            print(f"  {row['column_name']}: {row['data_type']} ({'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check actual data
        print("\n=== LLM_MODELS DATA ===")
        models = await conn.fetch("SELECT * FROM llm_models LIMIT 3")
        print(f"Found {len(models)} models")
        
        for model in models:
            print(f"  ID: {model['id']}")
            print(f"  Name: {model['name']}")
            print(f"  Display Name: {model['display_name']}")
            print(f"  Provider: {model['provider']}")
            print(f"  Status: {model['status']}")
            print("  ---")
        
        # Test the exact query from the API
        print("\n=== TESTING API QUERY ===")
        try:
            api_query = """
                SELECT id, name, display_name, provider, model_type, api_endpoint, 
                       status, capabilities, pricing_info, performance_metrics,
                       model_config, api_key, health_url, dns_name,
                       created_at, updated_at
                FROM llm_models
            """
            api_result = await conn.fetch(api_query)
            print(f"API query returned {len(api_result)} rows")
            
            if api_result:
                print("Sample result:")
                sample = dict(api_result[0])
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"API query failed: {e}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Debug failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_db())
