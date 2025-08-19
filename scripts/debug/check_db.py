#!/usr/bin/env python3
"""
Quick database check script
"""

import asyncio
import asyncpg
import os
import sys

async def check_database():
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/agenticai_platform')
        
        # Check if tables exist
        result = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('llm_models', 'embedding_models', 'tool_templates')
        """)
        
        tables_found = [row['table_name'] for row in result]
        print('Tables found:', tables_found)
        
        # Check count of records in each table
        for table in ['llm_models', 'embedding_models', 'tool_templates']:
            if table in tables_found:
                try:
                    count = await conn.fetchval(f'SELECT COUNT(*) FROM {table}')
                    print(f'{table}: {count} records')
                    
                    # Show sample data
                    if count > 0:
                        sample = await conn.fetch(f'SELECT * FROM {table} LIMIT 2')
                        print(f'  Sample data: {len(sample)} rows')
                        for row in sample:
                            print(f'    {dict(row)}')
                except Exception as e:
                    print(f'{table}: Error - {e}')
            else:
                print(f'{table}: Table does not exist')
        
        await conn.close()
        
    except Exception as e:
        print(f'Database connection error: {e}')
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(check_database())
    if not success:
        sys.exit(1)
