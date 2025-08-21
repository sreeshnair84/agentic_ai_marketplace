#!/usr/bin/env python3
"""
Comprehensive MCP System Test - Final Working Version
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
    
    def test_complete_mcp_workflow():
        """Test the complete MCP workflow"""
        print("🎯 Complete MCP System Test")
        print("=" * 60)
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # 1. Display current MCP servers
            print("\n📊 Current MCP Servers:")
            cur.execute("SELECT id, name, server_url, status, health_status FROM mcp_servers ORDER BY created_at")
            servers = cur.fetchall()
            for server in servers:
                print(f"  ✓ [{server['name']}] {server['server_url']} - {server['status']} ({server['health_status']})")
            
            # 2. Display current tools
            print("\n🔧 Current MCP Tools:")
            cur.execute("""
                SELECT t.id, t.tool_name, t.description, s.name as server_name 
                FROM mcp_tools_registry t 
                JOIN mcp_servers s ON t.server_id = s.id 
                ORDER BY t.created_at
            """)
            tools = cur.fetchall()
            for tool in tools:
                print(f"  ✓ [{tool['tool_name']}] {tool['description']} (Server: {tool['server_name']})")
            
            # 3. Display current endpoints  
            print("\n🌐 Current MCP Endpoints:")
            cur.execute("SELECT id, endpoint_name, endpoint_url, status FROM mcp_endpoints ORDER BY created_at")
            endpoints = cur.fetchall()
            for endpoint in endpoints:
                print(f"  ✓ [{endpoint['endpoint_name']}] {endpoint['endpoint_url']} - {endpoint['status']}")
            
            # 4. Add a comprehensive new tool
            if servers:
                server_id = servers[0]['id']
                print(f"\n➕ Adding comprehensive test tool to server: {servers[0]['name']}")
                
                tool_schema = {
                    "type": "function",
                    "function": {
                        "name": "data_analyzer",
                        "description": "Analyze data and provide insights",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "data": {
                                    "type": "array",
                                    "description": "Array of data points to analyze"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["statistical", "trend", "summary"],
                                    "description": "Type of analysis to perform"
                                }
                            },
                            "required": ["data", "analysis_type"]
                        }
                    }
                }
                
                cur.execute("""
                    INSERT INTO mcp_tools_registry (
                        server_id, tool_name, display_name, description, schema, 
                        capabilities, is_available
                    )
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
                    RETURNING id, tool_name
                """, (
                    server_id,
                    'data_analyzer',
                    'Data Analyzer',
                    'Comprehensive data analysis tool with multiple analysis types',
                    json.dumps(tool_schema),
                    ["statistical_analysis", "trend_detection", "summary_generation"],  # PostgreSQL array
                    True
                ))
                
                new_tool = cur.fetchone()
                print(f"   ✅ Created tool: {new_tool['tool_name']} (ID: {new_tool['id']})")
            
            # 5. Simulate tool execution with logging
            if endpoints and tools:
                endpoint_id = endpoints[0]['id']
                tool_id = tools[0]['id']
                
                print(f"\n📊 Simulating tool execution...")
                print(f"   Endpoint: {endpoints[0]['endpoint_name']}")
                print(f"   Tool: {tools[0]['tool_name']}")
                
                # Log successful execution
                cur.execute("""
                    INSERT INTO mcp_execution_logs (
                        endpoint_id, tool_id, execution_type, input_parameters, output_result, 
                        execution_status, execution_time_ms, created_at
                    )
                    VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, NOW())
                    RETURNING id
                """, (
                    endpoint_id,
                    tool_id,
                    'tool',  # Must be 'endpoint' or 'tool'
                    json.dumps({
                        "action": "test_execution",
                        "parameters": {"message": "Hello MCP!"}
                    }),
                    json.dumps({
                        "success": True,
                        "result": "Tool executed successfully",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }),
                    'success',
                    125
                ))
                
                log_id = cur.fetchone()['id']
                print(f"   ✅ Logged execution: ID {log_id}")
            
            # 6. Display execution statistics
            print(f"\n📈 MCP System Statistics:")
            
            cur.execute("SELECT COUNT(*) as count FROM mcp_servers WHERE status = 'active'")
            active_servers = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM mcp_tools_registry WHERE is_available = true")
            available_tools = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM mcp_endpoints WHERE status = 'active'")
            active_endpoints = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) as count FROM mcp_execution_logs WHERE execution_status = 'success'")
            successful_executions = cur.fetchone()['count']
            
            cur.execute("SELECT AVG(execution_time_ms) as avg_time FROM mcp_execution_logs WHERE execution_status = 'success'")
            avg_execution_time = cur.fetchone()['avg_time'] or 0
            
            print(f"   🟢 Active Servers: {active_servers}")
            print(f"   🔧 Available Tools: {available_tools}")
            print(f"   🌐 Active Endpoints: {active_endpoints}")
            print(f"   ✅ Successful Executions: {successful_executions}")
            print(f"   ⚡ Average Execution Time: {avg_execution_time:.1f}ms")
            
            conn.commit()
            
            print(f"\n🎉 MCP System Test Completed Successfully!")
            print(f"🚀 Frontend available at: http://localhost:3001/mcp")
            print(f"📚 Navigate to the MCP tab to test the full interface")
            
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
            conn.rollback()
            return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    if __name__ == "__main__":
        success = test_complete_mcp_workflow()
        sys.exit(0 if success else 1)

except ImportError:
    print("❌ psycopg2 not available. Please install with: pip install psycopg2-binary")
    sys.exit(1)
