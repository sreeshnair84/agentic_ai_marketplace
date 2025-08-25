#!/usr/bin/env python3
"""
Test script for different agent configurations
Tests agents with various tool capabilities including templates, instances, and MCP tools
"""

import requests
import json
import time
import sys

# Configuration
AGENTS_SERVICE_URL = "http://localhost:8002"
GATEWAY_SERVICE_URL = "http://localhost:8000"
TOOLS_SERVICE_URL = "http://localhost:8005"

def test_create_agent_with_tools():
    """Create test agents with different tool configurations"""
    print("=== Creating Test Agents with Different Tool Configurations ===\n")
    
    # Test Agent 1: Basic agent with template tools
    agent1_data = {
        "name": "template-agent-test",
        "display_name": "Template Tool Agent", 
        "description": "Agent with tool template capabilities",
        "framework": "langgraph",
        "capabilities": [
            "template:RAG Tool Template",
            "template:SQL Query Tool"
        ],
        "system_prompt": "You are a template tool agent with access to RAG and SQL tools.",
        "llm_model_id": None,
        "temperature": 0.7,
        "maxTokens": 2000,
        "a2a_enabled": True,
        "tags": ["test", "template"],
        "project_tags": ["testing"]
    }
    
    # Test Agent 2: Agent with tool instances
    agent2_data = {
        "name": "instance-agent-test",
        "display_name": "Instance Tool Agent",
        "description": "Agent with tool instance capabilities", 
        "framework": "langgraph",
        "capabilities": [
            "instance:production-rag-tool",
            "instance:analytics-tool"
        ],
        "system_prompt": "You are an instance tool agent with access to production tools.",
        "llm_model_id": None,
        "temperature": 0.5,
        "maxTokens": 1500,
        "a2a_enabled": True,
        "tags": ["test", "instance"],
        "project_tags": ["testing"]
    }
    
    # Test Agent 3: Agent with MCP tools
    agent3_data = {
        "name": "mcp-agent-test",
        "display_name": "MCP Tool Agent",
        "description": "Agent with MCP tool and endpoint capabilities",
        "framework": "langgraph", 
        "capabilities": [
            "mcp:weather-tool",
            "mcp:search-tool",
            "mcp-endpoint:api-gateway"
        ],
        "system_prompt": "You are an MCP agent with access to external services and APIs.",
        "llm_model_id": None,
        "temperature": 0.8,
        "maxTokens": 3000,
        "a2a_enabled": True,
        "tags": ["test", "mcp"],
        "project_tags": ["testing"]
    }
    
    # Test Agent 4: Mixed capabilities agent
    agent4_data = {
        "name": "mixed-agent-test",
        "display_name": "Mixed Capability Agent",
        "description": "Agent with mixed tool types for comprehensive testing",
        "framework": "langgraph",
        "capabilities": [
            "template:RAG Tool Template",
            "instance:production-rag-tool", 
            "mcp:weather-tool",
            "mcp-endpoint:api-gateway"
        ],
        "system_prompt": "You are a comprehensive agent with access to templates, instances, and MCP tools.",
        "llm_model_id": None,
        "temperature": 0.7,
        "maxTokens": 2500,
        "a2a_enabled": True,
        "tags": ["test", "mixed", "comprehensive"],
        "project_tags": ["testing"]
    }
    
    test_agents = [
        ("Template Tools Agent", agent1_data),
        ("Instance Tools Agent", agent2_data),
        ("MCP Tools Agent", agent3_data),
        ("Mixed Capabilities Agent", agent4_data)
    ]
    
    created_agents = []
    
    for agent_name, agent_data in test_agents:
        try:
            print(f"Creating {agent_name}...")
            response = requests.post(f"{AGENTS_SERVICE_URL}/agents/", json=agent_data, timeout=10)
            
            if response.status_code in [200, 201]:
                agent_result = response.json()
                print(f"[OK] Created {agent_name} (ID: {agent_result.get('id')})")
                print(f"   Capabilities: {len(agent_data['capabilities'])} tools")
                created_agents.append((agent_name, agent_result.get('id')))
            else:
                print(f"[ERROR] Failed to create {agent_name}: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"[ERROR] Exception creating {agent_name}: {str(e)}")
        
        print()
    
    return created_agents

def test_agent_metadata_retrieval():
    """Test if agents appear in metadata with their capabilities"""
    print("=== Testing Agent Metadata Retrieval ===\n")
    
    try:
        response = requests.get(f"{GATEWAY_SERVICE_URL}/api/v1/metadata/chat-options", timeout=10)
        
        if response.ok:
            metadata = response.json()
            agents = metadata.get('agents', [])
            
            print(f"Total agents in metadata: {len(agents)}")
            
            test_agents = [agent for agent in agents if 'test' in agent.get('name', '').lower()]
            
            print(f"Test agents found: {len(test_agents)}")
            
            for agent in test_agents:
                print(f"\nAgent: {agent.get('display_name', agent.get('name'))}")
                print(f"   ID: {agent.get('id')}")
                print(f"   Description: {agent.get('description', 'N/A')}")
                print(f"   Status: {agent.get('status', 'N/A')}")
                print(f"   A2A Enabled: {agent.get('a2a_enabled', False)}")
                print(f"   Capabilities: {len(agent.get('capabilities', []))}")
                
                if agent.get('capabilities'):
                    for cap in agent.get('capabilities', [])[:3]:  # Show first 3
                        print(f"     - {cap}")
                    if len(agent.get('capabilities', [])) > 3:
                        print(f"     ... and {len(agent.get('capabilities', [])) - 3} more")
        else:
            print(f"[ERROR] Failed to get metadata: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Exception getting metadata: {str(e)}")

def test_agent_chat_functionality(agent_ids):
    """Test chat functionality with different agents"""
    print("\n=== Testing Agent Chat Functionality ===\n")
    
    test_messages = [
        "Hello, can you introduce yourself and tell me about your capabilities?",
        "What tools do you have access to?",
        "Can you help me with a data analysis task?"
    ]
    
    for agent_name, agent_id in agent_ids:
        if not agent_id:
            continue
            
        print(f"Testing chat with {agent_name} (ID: {agent_id})")
        
        for message in test_messages[:1]:  # Test just the first message
            try:
                chat_request = {
                    "message": message,
                    "agent_id": agent_id,
                    "stream": False,
                    "context": {
                        "type": "agent",
                        "agent": {"id": agent_id, "name": agent_name}
                    }
                }
                
                print(f"  Sending: {message[:50]}...")
                response = requests.post(
                    f"{GATEWAY_SERVICE_URL}/api/v1/a2a/chat", 
                    json=chat_request,
                    timeout=15
                )
                
                if response.ok:
                    result = response.json()
                    print(f"  [OK] Response received (success: {result.get('success')})")
                    if result.get('message'):
                        preview = result['message'][:100] + "..." if len(result.get('message', '')) > 100 else result.get('message', '')
                        print(f"     Preview: {preview}")
                else:
                    print(f"  [ERROR] Chat failed: {response.status_code}")
                    print(f"     Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"  [ERROR] Exception during chat: {str(e)}")
        
        print()

def test_a2a_agent_service_status():
    """Test A2A agent service status"""
    print("=== Testing A2A Agent Service Status ===\n")
    
    try:
        # Test A2A agent list endpoint  
        response = requests.get(f"{GATEWAY_SERVICE_URL}/api/v1/a2a/agents", timeout=10)
        
        if response.ok:
            agents_data = response.json()
            print(f"A2A Service Status: [OK] Healthy")
            print(f"Total A2A agents: {len(agents_data.get('agents', []))}")
            
            for agent in agents_data.get('agents', []):
                print(f"  - {agent.get('name')} (Status: {agent.get('status')})")
                
        else:
            print(f"A2A Service Status: [ERROR] Error {response.status_code}")
            
    except Exception as e:
        print(f"A2A Service Status: [ERROR] Exception {str(e)}")

def cleanup_test_agents(agent_ids):
    """Clean up created test agents"""
    print("\n=== Cleaning Up Test Agents ===\n")
    
    for agent_name, agent_id in agent_ids:
        if not agent_id:
            continue
            
        try:
            response = requests.delete(f"{AGENTS_SERVICE_URL}/agents/{agent_id}")
            if response.ok:
                print(f"[OK] Deleted {agent_name}")
            else:
                print(f"[ERROR] Failed to delete {agent_name}: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] Exception deleting {agent_name}: {str(e)}")

def main():
    print("Testing Agent Configurations with Different Tool Capabilities\n")
    print("This test will:")
    print("1. Create agents with different tool configurations")
    print("2. Verify they appear in metadata")
    print("3. Test chat functionality")
    print("4. Clean up test agents")
    print("\nMake sure all services are running (agents:8002, gateway:8000, tools:8005)\n")
    
    input("Press Enter to continue...")
    
    # Step 1: Create test agents
    created_agents = test_create_agent_with_tools()
    
    # Wait for agents to be loaded
    print("Waiting for agents to be loaded...")
    time.sleep(5)
    
    # Step 2: Test metadata retrieval
    test_agent_metadata_retrieval()
    
    # Step 3: Test A2A service status
    test_a2a_agent_service_status()
    
    # Step 4: Test chat functionality (limited to prevent timeout)
    if created_agents:
        test_agent_chat_functionality(created_agents[:2])  # Test first 2 agents only
    
    # Step 5: Cleanup
    cleanup_choice = input("\nCleanup test agents? (y/N): ").strip().lower()
    if cleanup_choice == 'y':
        cleanup_test_agents(created_agents)
    else:
        print("\nTest agents left for manual inspection:")
        for agent_name, agent_id in created_agents:
            print(f"  - {agent_name}: {agent_id}")
    
    print("\nAgent Configuration Testing Complete!")

if __name__ == "__main__":
    main()