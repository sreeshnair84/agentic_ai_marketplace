#!/usr/bin/env python3
"""
Test MCP database functionality directly
"""
import sys
import os
import json

try:
    import psycopg2
    import psycopg2.extras
    
    # Database connection parameters
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'agenticai_platform',
        'user': 'agenticai_user', 
        'password': 'agenticai_password'
    }
    
    def test_mcp_tables():
        """Test that MCP tables exist and have data"""
        print("🔍 Testing MCP database tables...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Test mcp_servers table
            print("\n📊 MCP Servers:")
            cur.execute("SELECT id, name, server_url, status FROM mcp_servers ORDER BY created_at")
            servers = cur.fetchall()
            for server in servers:
                print(f"  [{server['id']}] {server['name']} - {server['server_url']} ({server['status']})")
            
            # Test mcp_tools_registry table
            print("\n🔧 MCP Tools:")
            cur.execute("SELECT id, tool_name, server_id, schema FROM mcp_tools_registry ORDER BY created_at")
            tools = cur.fetchall()
            for tool in tools:
                schema_preview = str(tool['schema'])[:50] + "..." if tool['schema'] else "No schema"
                print(f"  [{tool['id']}] {tool['tool_name']} (Server {tool['server_id']}) - {schema_preview}")
            
            # Test mcp_endpoints table
            print("\n🌐 MCP Endpoints:")
            cur.execute("SELECT id, endpoint_name, endpoint_url, status FROM mcp_endpoints ORDER BY created_at")
            endpoints = cur.fetchall()
            for endpoint in endpoints:
                print(f"  [{endpoint['id']}] {endpoint['endpoint_name']} - {endpoint['endpoint_url']} ({endpoint['status']})")
            
            # Test mcp_execution_logs table
            print("\n📝 MCP Execution Logs:")
            cur.execute("SELECT COUNT(*) as count FROM mcp_execution_logs")
            log_count = cur.fetchone()['count']
            print(f"  Total execution logs: {log_count}")
            
            print(f"\n✅ All MCP tables are working correctly!")
            print(f"📈 Summary: {len(servers)} servers, {len(tools)} tools, {len(endpoints)} endpoints")
            
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            cur.close()
            conn.close()
    
    def simulate_mcp_operations():
        """Simulate some MCP operations"""
        print("\n🚀 Simulating MCP operations...")
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Get the first server's ID for testing
            cur.execute("SELECT id FROM mcp_servers LIMIT 1")
            server_id = cur.fetchone()['id']
            
            # Add a new tool to the registry
            print("➕ Adding new tool to registry...")
            cur.execute("""
                INSERT INTO mcp_tools_registry (server_id, tool_name, description, schema)
                VALUES (%s, 'test_calculator', 'A test calculator tool', %s)
                RETURNING id, tool_name
            """, (server_id, json.dumps({
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform basic calculations",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "expression": {"type": "string", "description": "Math expression to evaluate"}
                        },
                        "required": ["expression"]
                    }
                }
            })))
            
            new_tool = cur.fetchone()
            print(f"   Created tool: {new_tool['tool_name']} (ID: {new_tool['id']})")
            
            # Get the first endpoint's ID for testing
            cur.execute("SELECT id FROM mcp_endpoints LIMIT 1")
            endpoint_id = cur.fetchone()['id']
            
            # Create endpoint binding
            print("🔗 Creating endpoint binding...")
            cur.execute("""
                INSERT INTO mcp_endpoint_tool_bindings (endpoint_id, tool_id, binding_config)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (endpoint_id, new_tool['id'], json.dumps({"enabled": True, "timeout": 30})))
            
            binding_id = cur.fetchone()['id']
            print(f"   Created binding: ID {binding_id}")
            
            # Log a simulated execution
            print("📊 Logging simulated execution...")
            cur.execute("""
                INSERT INTO mcp_execution_logs (endpoint_id, tool_id, request_data, response_data, status, execution_time_ms)
                VALUES (%s, %s, %s, %s, 'success', 150)
                RETURNING id
            """, (
                endpoint_id,
                new_tool['id'],
                json.dumps({"expression": "2 + 2"}),
                json.dumps({"result": 4})
            ))
            
            log_id = cur.fetchone()['id']
            print(f"   Created execution log: ID {log_id}")
            
            log_id = cur.fetchone()['id']
            print(f"   Created execution log: ID {log_id}")
            
            conn.commit()
            print("✅ MCP operations completed successfully!")
            
        except psycopg2.Error as e:
            print(f"❌ Operation failed: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
        
        return True
    
    if __name__ == "__main__":
        print("🧪 MCP Database Test Suite")
        print("=" * 50)
        
        # Test basic functionality
        if not test_mcp_tables():
            sys.exit(1)
        
        # Test operations
        if not simulate_mcp_operations():
            sys.exit(1)
        
        print("\n🎉 All MCP database tests passed!")
        sys.exit(0)

except ImportError:
    print("❌ psycopg2 not available. Please install with: pip install psycopg2-binary")
    sys.exit(1)
