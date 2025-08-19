#!/usr/bin/env python3
"""
Minimal data insertion for testing
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

async def insert_minimal_data():
    """Insert minimal test data"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("📊 Inserting minimal test data...")
        
        # Insert default admin user
        await conn.execute("""
            INSERT INTO users (username, email, first_name, last_name, hashed_password, role, is_active, is_verified) 
            VALUES ('admin', 'admin@agenticai.local', 'Admin', 'User', 
                   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LKO8F3ZH9VdGQ1oC6',
                   'ADMIN', true, true)
        """)
        print("✅ Inserted admin user")
        
        # Insert default project
        await conn.execute("""
            INSERT INTO projects (name, description, tags, is_default, created_by) 
            VALUES ('Default Project', 'The default project for general use', 
                   ARRAY['general', 'default'], true, 'system')
        """)
        print("✅ Inserted default project")
        
        # Insert sample agent
        await conn.execute("""
            INSERT INTO agents (name, display_name, description, url, health_url, category, 
                               ai_provider, model_name, tags, project_tags, author, organization, 
                               environment, created_by) 
            VALUES ('test-agent', 'Test Agent', 'A test agent for validation', 
                   'http://localhost:8002/agents/test', 'http://localhost:8002/health',
                   'testing', 'openai', 'gpt-4', ARRAY['test'], ARRAY['default'],
                   'Platform Team', 'Agentic AI Accelerator', 'development', 'system')
        """)
        print("✅ Inserted test agent")
        
        # Insert sample LLM model
        await conn.execute("""
            INSERT INTO llm_models (name, display_name, provider, model_type, 
                                  supports_streaming, supports_functions, is_active, project_tags) 
            VALUES ('gpt-4', 'GPT-4', 'openai', 'chat', true, true, true, ARRAY['default'])
        """)
        print("✅ Inserted test LLM model")
        
        await conn.close()
        print("🎉 Minimal data insertion complete!")
        return True
        
    except Exception as e:
        print(f"❌ Data insertion failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(insert_minimal_data())
    if not success:
        exit(1)
