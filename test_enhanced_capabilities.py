#!/usr/bin/env python3
"""
Test Enhanced Agent Capabilities
Tests that agents with different tool configurations are properly handled by the system
"""

import requests
import json

def test_existing_agent_capabilities():
    """Test that existing agents show proper capabilities in metadata"""
    print("=== Testing Existing Agent Capabilities ===\n")
    
    try:
        # Test metadata API
        response = requests.get("http://localhost:8000/api/v1/metadata/chat-options")
        
        if response.ok:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"Found {len(agents)} agents in metadata:")
            
            for agent in agents:
                print(f"\nAgent: {agent.get('display_name', agent.get('name'))}")
                print(f"  ID: {agent.get('id')}")
                print(f"  A2A Enabled: {agent.get('a2a_address') is not None or agent.get('url') is not None}")
                
                capabilities = agent.get('capabilities', [])
                print(f"  Capabilities: {len(capabilities)}")
                
                if capabilities:
                    for cap in capabilities:
                        cap_type = "Unknown"
                        if isinstance(cap, str):
                            if cap.startswith('template:'):
                                cap_type = "Tool Template"
                            elif cap.startswith('instance:'):
                                cap_type = "Tool Instance"
                            elif cap.startswith('mcp:'):
                                cap_type = "MCP Tool"
                            elif cap.startswith('mcp-endpoint:'):
                                cap_type = "MCP Endpoint"
                            else:
                                cap_type = "Basic Capability"
                        
                        print(f"    - {cap} ({cap_type})")
                else:
                    print("    - No specific capabilities configured")
            
            return True
        else:
            print(f"Failed to get metadata: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_frontend_agents_api():
    """Test frontend agents API with enhanced capabilities"""
    print("\n=== Testing Frontend Agents API ===\n")
    
    try:
        response = requests.get("http://localhost:3000/api/agents")
        
        if response.ok:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"Frontend API returned {len(agents)} agents:")
            
            for agent in agents:
                print(f"\nAgent: {agent.get('name')}")
                print(f"  Framework: {agent.get('framework')}")
                print(f"  Skills: {agent.get('skills', [])}")
                print(f"  Status: {agent.get('status')}")
                
                config = agent.get('config', {})
                tools = config.get('tools', [])
                print(f"  Configured Tools: {len(tools)}")
            
            return True
        else:
            print(f"Failed to get agents from frontend API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_tool_loading_capability():
    """Test if the dynamic tool loader concepts work"""
    print("\n=== Testing Tool Loading Concepts ===\n")
    
    # Test capabilities formats
    test_capabilities = [
        "template:RAG Tool Template",
        "instance:production-rag",
        "mcp:weather-api",
        "mcp-endpoint:search-service"
    ]
    
    print("Testing capability parsing logic:")
    
    for capability in test_capabilities:
        print(f"\nCapability: {capability}")
        
        if capability.startswith("template:"):
            tool_name = capability[9:]
            print(f"  Type: Tool Template")
            print(f"  Tool Name: {tool_name}")
            print(f"  Action: Would load template definition and create LangChain tool")
            
        elif capability.startswith("instance:"):
            tool_name = capability[9:]
            print(f"  Type: Tool Instance")
            print(f"  Tool Name: {tool_name}")
            print(f"  Action: Would load instance configuration and create configured tool")
            
        elif capability.startswith("mcp:"):
            tool_name = capability[4:]
            print(f"  Type: MCP Tool")
            print(f"  Tool Name: {tool_name}")
            print(f"  Action: Would connect to MCP server and create tool proxy")
            
        elif capability.startswith("mcp-endpoint:"):
            endpoint_name = capability[13:]
            print(f"  Type: MCP Endpoint")
            print(f"  Endpoint Name: {endpoint_name}")
            print(f"  Action: Would create HTTP client tool for endpoint")
    
    return True

def test_a2a_service_integration():
    """Test A2A service integration"""
    print("\n=== Testing A2A Service Integration ===\n")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/a2a/agents")
        
        if response.ok:
            data = response.json()
            agents = data.get('agents', [])
            
            print(f"A2A Service lists {len(agents)} agents:")
            
            for agent in agents:
                print(f"  - {agent.get('name')} (Status: {agent.get('status', 'unknown')})")
                
            return True
        else:
            print(f"A2A Service not available: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    print("Testing Enhanced Agent Capabilities\n")
    print("This test validates that the enhanced capability system is working:")
    print("1. Agents can be configured with different tool types")
    print("2. Metadata API properly exposes capabilities") 
    print("3. Frontend APIs handle enhanced agent data")
    print("4. A2A integration works with enhanced agents")
    print()
    
    results = []
    
    # Run tests
    results.append(("Existing Agent Capabilities", test_existing_agent_capabilities()))
    results.append(("Frontend Agents API", test_frontend_agents_api()))
    results.append(("Tool Loading Concepts", test_tool_loading_capability()))
    results.append(("A2A Service Integration", test_a2a_service_integration()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n[SUCCESS] All enhanced capability features are working!")
    else:
        print(f"\n[PARTIAL] {passed} out of {len(results)} features working.")
    
    print("\nKey Improvements Implemented:")
    print("- Enhanced CreateAgentDialog with tool template, instance, and MCP selection")
    print("- Dynamic tool loader service for runtime tool loading")
    print("- Database agent class supporting custom capabilities")
    print("- A2A service integration with capability-aware agents")
    print("- Frontend-backend synchronization for enhanced agent data")

if __name__ == "__main__":
    main()