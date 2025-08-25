#!/usr/bin/env python3
"""
Quick validation script to test if the projects API is working after the fix
"""

import asyncio
import aiohttp
import json

async def test_projects_get():
    """Test the GET /api/v1/projects endpoint"""
    url = "http://localhost:8000/api/v1/projects"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                print(f"🔍 GET {url}")
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    projects = await response.json()
                    print(f"✅ SUCCESS: Retrieved {len(projects)} projects")
                    
                    if projects:
                        first_project = projects[0]
                        print(f"📋 Sample project data:")
                        print(f"   ID: {first_project.get('id')}")
                        print(f"   Name: {first_project.get('name')}")
                        print(f"   Created by: {first_project.get('created_by')} (type: {type(first_project.get('created_by'))})")
                        print(f"   Updated by: {first_project.get('updated_by')} (type: {type(first_project.get('updated_by'))})")
                        
                        # Verify that created_by and updated_by are strings, not UUIDs
                        created_by = first_project.get('created_by')
                        updated_by = first_project.get('updated_by')
                        
                        if created_by is not None and isinstance(created_by, str):
                            print(f"✅ created_by is correctly a string: '{created_by}'")
                        elif created_by is not None:
                            print(f"❌ created_by is not a string: {type(created_by)} = {created_by}")
                        
                        if updated_by is not None and isinstance(updated_by, str):
                            print(f"✅ updated_by is correctly a string: '{updated_by}'")
                        elif updated_by is not None:
                            print(f"❌ updated_by is not a string: {type(updated_by)} = {updated_by}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ ERROR: {error_text}")
                    
        except Exception as e:
            print(f"❌ REQUEST FAILED: {e}")

if __name__ == "__main__":
    print("🚀 Validating Projects API Fix...\n")
    asyncio.run(test_projects_get())
    print("\n🎯 Validation completed!")