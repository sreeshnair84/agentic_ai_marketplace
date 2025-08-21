#!/usr/bin/env python3
"""
Run clean MCP migration (drops and recreates tables)
"""
import sys
import os

try:
    import psycopg2
    
    # Database connection parameters
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'agenticai_platform',
        'user': 'agenticai_user', 
        'password': 'agenticai_password'
    }
    
    def run_clean_migration():
        """Run the clean MCP migration"""
        print("🚀 Running clean MCP migration (drop and recreate)...")
        print("⚠️  This will DROP existing MCP tables if they exist!")
        
        # Read the migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'clean_mcp_migration.sql')
        
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
        except FileNotFoundError:
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        # Connect to database
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Execute the migration
            cur.execute(migration_sql)
            conn.commit()
            
            print("✅ MCP tables created successfully!")
            print("📊 Created tables:")
            print("  - mcp_servers")
            print("  - mcp_tools_registry") 
            print("  - mcp_endpoints")
            print("  - mcp_execution_logs")
            print("🎯 Demo data inserted:")
            print("  - 2 sample MCP servers")
            print("  - 2 sample endpoints")
            print("  - 1 sample tool")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    if __name__ == "__main__":
        success = run_clean_migration()
        sys.exit(0 if success else 1)

except ImportError:
    print("❌ psycopg2 not available. Please install with: pip install psycopg2-binary")
    sys.exit(1)
