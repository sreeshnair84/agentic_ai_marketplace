#!/usr/bin/env python3
"""
Test script for agent lifecycle functionality
Tests create, read, update, delete, and metadata retrieval for agents
"""

import requests
import json
import time
import sys

# Configuration
AGENTS_SERVICE_URL = "http://localhost:8002"
GATEWAY_SERVICE_URL = "http://localhost:8000"
FRONTEND_API_URL = "http://localhost:3000"

def test_agents_service():
    """Test agents service directly"""
    print("Testing Agents Service...")
    
    # Test health check
    try:
        response = requests.get(f"{AGENTS_SERVICE_URL}/agents/health")
        print(f"Agents service health: {response.status_code}")
        if response.ok:
            print(f"Health response: {response.json()}")
    except Exception as e:
        print(f"Failed to connect to agents service: {e}")
        return False
    
    # Test list agents
    try:
        response = requests.get(f"{AGENTS_SERVICE_URL}/agents/")
        print(f"List agents: {response.status_code}")
        if response.ok:
            agents = response.json()
            print(f"Found {len(agents) if isinstance(agents, list) else 0} agents")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to list agents: {e}")
    
    # Test create agent
    test_agent = {
        "name": "test-agent",
        "display_name": "Test Agent",
        "description": "A test agent for validation",
        "framework": "langgraph",
        "capabilities": ["test", "validation"],
        "systemPrompt": "You are a test agent for validation purposes.",
        "llm_model_id": None,
        "temperature": 0.7,
        "maxTokens": 2000,
        "category": "test",
        "agent_type": "autonomous",
        "version": "1.0.0",
        "a2a_enabled": True,
        "tags": ["test"],
        "project_tags": ["validation"]
    }
    
    try:
        response = requests.post(f"{AGENTS_SERVICE_URL}/agents/", json=test_agent)
        print(f"Create agent: {response.status_code}")
        if response.ok:
            created_agent = response.json()
            print(f"Created agent ID: {created_agent.get('id')}")
            agent_id = created_agent.get('id')
            
            # Test get agent
            response = requests.get(f"{AGENTS_SERVICE_URL}/agents/{agent_id}")
            print(f"Get agent: {response.status_code}")
            if response.ok:
                agent = response.json()
                print(f"Retrieved agent: {agent.get('name')}")
            
            # Test update agent
            update_data = {
                "description": "Updated test agent description"
            }
            response = requests.put(f"{AGENTS_SERVICE_URL}/agents/{agent_id}", json=update_data)
            print(f"Update agent: {response.status_code}")
            
            # Test delete agent (cleanup)
            response = requests.delete(f"{AGENTS_SERVICE_URL}/agents/{agent_id}")
            print(f"Delete agent: {response.status_code}")
            
        else:
            print(f"Failed to create agent: {response.text}")
    except Exception as e:
        print(f"Failed agent CRUD operations: {e}")
    
    return True

def test_gateway_metadata():
    """Test gateway metadata endpoints"""
    print("\nTesting Gateway Metadata...")
    
    try:
        response = requests.get(f"{GATEWAY_SERVICE_URL}/api/v1/metadata/chat-options")
        print(f"Metadata chat-options: {response.status_code}")
        if response.ok:
            metadata = response.json()
            print(f"Workflows: {len(metadata.get('workflows', []))}")
            print(f"Agents: {len(metadata.get('agents', []))}")
            print(f"Tools: {len(metadata.get('tools', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to get metadata: {e}")

def test_frontend_apis():
    """Test frontend API routes"""
    print("\nTesting Frontend APIs...")
    
    # Test agents API route
    try:
        response = requests.get(f"{FRONTEND_API_URL}/api/agents")
        print(f"Frontend agents API: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Frontend agents count: {len(data.get('agents', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to get frontend agents: {e}")
    
    # Test sidebar stats
    try:
        response = requests.get(f"{FRONTEND_API_URL}/api/sidebar")
        print(f"Sidebar stats: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Sidebar agent badge: {data.get('badges', {}).get('agents', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to get sidebar stats: {e}")

def main():
    print("=== Agent Lifecycle Test ===\n")
    
    print("Testing complete agent lifecycle from backend to frontend...")
    print("Make sure all services are running:")
    print("- Agents service on port 8002")
    print("- Gateway service on port 8000") 
    print("- Frontend on port 3000")
    print("- PostgreSQL database")
    print()
    
    success = test_agents_service()
    if not success:
        print("Agents service test failed, skipping other tests")
        sys.exit(1)
    
    test_gateway_metadata()
    test_frontend_apis()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()