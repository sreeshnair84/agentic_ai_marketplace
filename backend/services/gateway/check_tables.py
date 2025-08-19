import asyncio
import asyncpg

async def check_tables():
    try:
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'agenticai_user', 
            'password': 'agenticai_password',
            'database': 'agenticai_platform'
        }
        
        conn = await asyncpg.connect(**db_config)
        
        # Check if tables exist
        tables = ['tool_instances', 'llm_models', 'embedding_models']
        for table in tables:
            exists = await conn.fetchval('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)', table)
            count = 0
            if exists:
                count = await conn.fetchval(f'SELECT COUNT(*) FROM {table}')
            print(f'{table}: exists={exists}, rows={count}')
        
        await conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_tables())
