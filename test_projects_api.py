#!/usr/bin/env python3
"""
Test script for the Projects API endpoints
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"

async def test_projects_api():
    """Test the projects API endpoints"""
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Get all projects
        print("🔍 Testing GET /api/v1/projects...")
        try:
            async with session.get(f"{API_BASE_URL}/projects") as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    projects = await response.json()
                    print(f"✅ Found {len(projects)} projects")
                    for project in projects:
                        print(f"   - {project.get('name', 'Unknown')} ({project.get('id', 'No ID')})")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 2: Create a new project
        print("➕ Testing POST /api/v1/projects...")
        test_project = {
            "name": f"Test Project {asyncio.get_event_loop().time()}",
            "description": "A test project created by the test script",
            "tags": ["test", "api", "demo"],
            "is_default": False
        }
        
        try:
            async with session.post(
                f"{API_BASE_URL}/projects", 
                json=test_project,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"Status: {response.status}")
                if response.status == 201:
                    new_project = await response.json()
                    print(f"✅ Created project: {new_project.get('name')} (ID: {new_project.get('id')})")
                    print(f"   Created by: {new_project.get('created_by')}")
                    print(f"   Created at: {new_project.get('created_at')}")
                    project_id = new_project.get('id')
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
                    project_id = None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            project_id = None
        
        print("\n" + "="*50 + "\n")
        
        # Test 3: Get the created project
        if project_id:
            print(f"🔍 Testing GET /api/v1/projects/{project_id}...")
            try:
                async with session.get(f"{API_BASE_URL}/projects/{project_id}") as response:
                    print(f"Status: {response.status}")
                    if response.status == 200:
                        project = await response.json()
                        print(f"✅ Retrieved project: {project.get('name')}")
                        print(f"   Description: {project.get('description')}")
                        print(f"   Tags: {project.get('tags')}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error: {error_text}")
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 4: Get default project
        print("🔍 Testing GET /api/v1/projects/default...")
        try:
            async with session.get(f"{API_BASE_URL}/projects/default") as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    default_project = await response.json()
                    print(f"✅ Default project: {default_project.get('name')} (ID: {default_project.get('id')})")
                elif response.status == 404:
                    print("ℹ️ No default project found")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Projects API Test\n")
    asyncio.run(test_projects_api())
    print("\n✅ Test completed!")