import asyncio
import asyncpg

async def insert_sample_data():
    try:
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'user': 'agenticai_user',
            'password': 'agenticai_password',
            'database': 'agenticai_platform'
        }
        
        print('Connecting to database...')
        conn = await asyncpg.connect(**db_config)
        
        # Sample tool instances
        await conn.execute("""
            INSERT INTO tool_instances (name, display_name, template_name, status, configuration, created_by) 
            VALUES ('postgres-prod', 'Production PostgreSQL', 'postgres-query-tool', 'active', '{"host": "prod-db.example.com", "port": 5432}', 'admin@agenticai.com')
            ON CONFLICT (name) DO NOTHING
        """)
        
        await conn.execute("""
            INSERT INTO tool_instances (name, display_name, template_name, status, configuration, created_by) 
            VALUES ('redis-cache', 'Redis Cache Instance', 'redis-tool', 'active', '{"host": "redis.example.com", "port": 6379}', 'admin@agenticai.com')
            ON CONFLICT (name) DO NOTHING
        """)
        
        await conn.execute("""
            INSERT INTO tool_instances (name, display_name, template_name, status, configuration, created_by) 
            VALUES ('email-service', 'Email Service Instance', 'email-sender-tool', 'active', '{"smtp_host": "smtp.example.com", "port": 587}', 'admin@agenticai.com')
            ON CONFLICT (name) DO NOTHING
        """)
        print('✅ Inserted tool instances')
        
        # Sample LLM model
        await conn.execute(""" 
            INSERT INTO llm_models (name, display_name, provider, model_type, endpoint_url, is_active, model_config, health_url, dns_name) 
            VALUES ('gpt-4o', 'GPT-4 Omni', 'OpenAI', 'text-generation', 'https://api.openai.com/v1/chat/completions', true, 
                   '{"capabilities": {"max_tokens": 128000, "supports_functions": true}, "pricing_info": {}}', 'https://status.openai.com/api/v2/status.json', 'api.openai.com')
            ON CONFLICT (name) DO NOTHING
        """)
        print('✅ Inserted LLM models')

        # Sample embedding model  
        await conn.execute(""" 
            INSERT INTO embedding_models (name, display_name, provider, model_type, endpoint_url, is_active, model_config, health_url, dns_name) 
            VALUES ('text-embedding-3-large', 'OpenAI Text Embedding 3 Large', 'OpenAI', 'embedding', 'https://api.openai.com/v1/embeddings', true,
                   '{"capabilities": {"dimensions": 3072, "max_input_tokens": 8191}, "pricing_info": {}}', 'https://status.openai.com/api/v2/status.json', 'api.openai.com')
            ON CONFLICT (name) DO NOTHING
        """)
        print('✅ Inserted embedding models')
        
        await conn.close()
        
    except Exception as e:
        print(f'❌ Data insertion failed: {e}')

if __name__ == "__main__":
    asyncio.run(insert_sample_data())
