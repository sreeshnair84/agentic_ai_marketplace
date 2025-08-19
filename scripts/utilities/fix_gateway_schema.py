#!/usr/bin/env python3
"""
Fix gateway service database schema mismatches
"""

import asyncio
import asyncpg
import sys

async def fix_gateway_schema():
    """Fix schema mismatches for gateway service tables"""
    
    print("🔧 Starting gateway schema fixes...")
    print("=" * 80)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            'postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform'
        )
        
        print("📋 Checking and fixing tool_templates table...")
        
        # Check if columns exist in tool_templates
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tool_templates'
        """)
        existing_columns = {row['column_name'] for row in columns}
        
        # Add missing columns to tool_templates
        required_columns = {
            'dns_name': 'TEXT',
            'execution_count': 'INTEGER DEFAULT 0',
            'success_rate': 'DECIMAL(5,2) DEFAULT 0.0'
        }
        
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                print(f"🔄 Adding missing column: {column_name}")
                await conn.execute(f"""
                    ALTER TABLE tool_templates 
                    ADD COLUMN {column_name} {column_def}
                """)
                print(f"✅ Added {column_name} column")
            else:
                print(f"✅ Column {column_name} already exists")
        
        print("\n📋 Checking and fixing workflow_definitions table...")
        
        # Check if columns exist in workflow_definitions  
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'workflow_definitions'
        """)
        existing_columns = {row['column_name'] for row in columns}
        
        # Add missing columns to workflow_definitions
        workflow_columns = {
            'dns_name': 'TEXT',
            'execution_count': 'INTEGER DEFAULT 0',
            'success_rate': 'DECIMAL(5,2) DEFAULT 0.0'
        }
        
        for column_name, column_def in workflow_columns.items():
            if column_name not in existing_columns:
                print(f"🔄 Adding missing column: {column_name}")
                await conn.execute(f"""
                    ALTER TABLE workflow_definitions 
                    ADD COLUMN {column_name} {column_def}
                """)
                print(f"✅ Added {column_name} column")
            else:
                print(f"✅ Column {column_name} already exists")
        
        print("\n📋 Final table structures:")
        
        # Show final tool_templates structure
        print("\n=== TOOL_TEMPLATES FINAL STRUCTURE ===")
        schema = await conn.fetch('''
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'tool_templates' 
            ORDER BY ordinal_position;
        ''')
        for row in schema:
            default = row[3] or ''
            print(f"  {row[0]:<20} {row[1]:<15} {row[2]:<5} {default}")
        
        # Show final workflow_definitions structure
        print("\n=== WORKFLOW_DEFINITIONS FINAL STRUCTURE ===")
        schema = await conn.fetch('''
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'workflow_definitions' 
            ORDER BY ordinal_position;
        ''')
        for row in schema:
            default = row[3] or ''
            print(f"  {row[0]:<20} {row[1]:<15} {row[2]:<5} {default}")
        
        await conn.close()
        print("\n✅ Gateway schema fixes completed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing gateway schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(fix_gateway_schema())
    sys.exit(0 if success else 1)
