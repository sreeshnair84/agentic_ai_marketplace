#!/usr/bin/env python3
"""
Fix database schema mismatches with Python models

This script addresses the inconsistencies between the database schema 
and Python models that are causing API failures.
"""

import asyncio
import asyncpg
from datetime import datetime

DATABASE_URL = "postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform"

async def fix_schema_mismatches():
    """Fix schema mismatches between database and Python models"""
    
    print("🔧 Starting schema mismatch fixes...")
    print("================================================================================")
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Check current agents table structure
        print("📋 Checking current agents table structure...")
        schema = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            ORDER BY ordinal_position;
        """)
        
        columns = [row['column_name'] for row in schema]
        print(f"Current columns: {', '.join(columns)}")
        
        # Fix 1: Add agent_type column if missing and populate from category
        if 'agent_type' not in columns and 'category' in columns:
            print("\n🔄 Adding agent_type column and migrating from category...")
            
            # Add agent_type column
            await conn.execute("""
                ALTER TABLE agents 
                ADD COLUMN agent_type VARCHAR(50);
            """)
            
            # Migrate data from category to agent_type
            await conn.execute("""
                UPDATE agents 
                SET agent_type = category 
                WHERE category IS NOT NULL;
            """)
            
            print("✅ Added agent_type column and migrated data")
        
        # Fix 2: Ensure status column exists and has proper enum values
        if 'status' in columns:
            print("\n🔄 Checking status column values...")
            
            # Update any invalid status values to 'active'
            await conn.execute("""
                UPDATE agents 
                SET status = 'active' 
                WHERE status NOT IN ('active', 'inactive', 'busy', 'error', 'maintenance');
            """)
            
            print("✅ Cleaned up status column values")
        
        # Fix 3: Add missing columns from Python model if they don't exist
        missing_columns = {
            'ai_provider': 'VARCHAR(50) DEFAULT \'gemini\'',
            'model_name': 'VARCHAR(100) DEFAULT \'gemini-1.5-pro\'',
            'capabilities': 'JSONB DEFAULT \'[]\'',
            'system_prompt': 'TEXT',
            'max_tokens': 'INTEGER DEFAULT 2048',
            'temperature': 'DECIMAL DEFAULT 0.7',
            'a2a_enabled': 'BOOLEAN DEFAULT true',
            'a2a_address': 'VARCHAR(255)',
            'model_config_data': 'JSONB DEFAULT \'{}\'',
            'is_active': 'BOOLEAN DEFAULT true'
        }
        
        for col_name, col_def in missing_columns.items():
            if col_name not in columns:
                print(f"\n🔄 Adding missing column: {col_name}")
                await conn.execute(f"""
                    ALTER TABLE agents 
                    ADD COLUMN {col_name} {col_def};
                """)
                print(f"✅ Added {col_name} column")
        
        # Fix 4: Check and fix workflow-related tables
        print("\n🔄 Checking workflow tables...")
        
        # Check if workflow_definitions table exists (it should be referenced by workflow_agents)
        workflow_tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%workflow%';
        """)
        
        workflow_table_names = [row['table_name'] for row in workflow_tables]
        print(f"Workflow tables found: {', '.join(workflow_table_names)}")
        
        # Fix 5: Update agent data to match Python model expectations
        print("\n🔄 Updating agent data to match Python model expectations...")
        
        # Ensure test agent has proper values for new columns
        await conn.execute("""
            UPDATE agents 
            SET 
                ai_provider = COALESCE(ai_provider, 'gemini'),
                model_name = COALESCE(model_name, 'gemini-1.5-pro'),
                capabilities = COALESCE(capabilities, '["text_generation", "conversation", "analysis"]'::jsonb),
                max_tokens = COALESCE(max_tokens, 2048),
                temperature = COALESCE(temperature, 0.7),
                a2a_enabled = COALESCE(a2a_enabled, true),
                model_config_data = COALESCE(model_config_data, '{}'::jsonb),
                is_active = COALESCE(is_active, true),
                agent_type = COALESCE(agent_type, category, 'conversational')
            WHERE TRUE;
        """)
        
        print("✅ Updated agent data with proper defaults")
        
        # Fix 6: Check agents table final structure
        print("\n📋 Final agents table structure:")
        schema = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'agents' 
            ORDER BY ordinal_position;
        """)
        
        for row in schema:
            print(f"  {row['column_name']:<20} {row['data_type']:<15} {row['is_nullable']:<8} {row['column_default'] or ''}")
        
        # Verify agents data
        print("\n📊 Current agents in database:")
        agents = await conn.fetch("""
            SELECT id, name, agent_type, status, ai_provider, model_name, is_active 
            FROM agents;
        """)
        
        for agent in agents:
            print(f"  {agent['id']} | {agent['name']} | {agent['agent_type']} | {agent['status']} | {agent['ai_provider']} | {agent['model_name']} | {agent['is_active']}")
        
        print("\n✅ Schema mismatch fixes completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error fixing schema mismatches: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_schema_mismatches())
