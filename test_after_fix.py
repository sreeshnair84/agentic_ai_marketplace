#!/usr/bin/env python3
"""
Test script to validate Projects API after schema fix
"""

import asyncio
import aiohttp
import json
import time

API_BASE_URL = "http://localhost:8000/api/v1"

async def comprehensive_projects_test():
    """Comprehensive test of all projects endpoints"""
    
    async with aiohttp.ClientSession() as session:
        test_results = {
            "get_projects": False,
            "create_project": False,
            "get_project": False,
            "get_default": False,
            "update_project": False
        }
        
        created_project_id = None
        
        print("Starting Comprehensive Projects API Test")
        print("=" * 60)
        
        # Test 1: GET all projects
        print("\n1. Testing GET /projects")
        try:
            async with session.get(f"{API_BASE_URL}/projects") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    projects = await response.json()
                    print(f"   SUCCESS: Found {len(projects)} projects")
                    if projects:
                        sample = projects[0]
                        print(f"   Sample: {sample.get('name')} (created_by: {sample.get('created_by')})")
                    test_results["get_projects"] = True
                else:
                    error_text = await response.text()
                    print(f"   FAILED: {error_text}")
        except Exception as e:
            print(f"   EXCEPTION: {e}")
        
        # Test 2: CREATE a new project
        print("\n2. Testing POST /projects")
        test_project = {
            "name": f"Test Project {int(time.time())}",
            "description": "Test project created after schema fix",
            "tags": ["test", "schema-fix", "validation"],
            "is_default": False
        }
        
        try:
            async with session.post(
                f"{API_BASE_URL}/projects",
                json=test_project,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 201:
                    new_project = await response.json()
                    created_project_id = new_project.get('id')
                    print(f"   SUCCESS: Created project {new_project.get('name')}")
                    print(f"   ID: {created_project_id}")
                    print(f"   Created by: {new_project.get('created_by')}")
                    print(f"   Data types check:")
                    print(f"      - created_by is {type(new_project.get('created_by'))}: {new_project.get('created_by')}")
                    print(f"      - updated_by is {type(new_project.get('updated_by'))}: {new_project.get('updated_by')}")
                    test_results["create_project"] = True
                else:
                    error_text = await response.text()
                    print(f"   FAILED: {error_text}")
        except Exception as e:
            print(f"   EXCEPTION: {e}")
        
        # Test 3: GET specific project
        if created_project_id:
            print(f"\n3. Testing GET /projects/{created_project_id}")
            try:
                async with session.get(f"{API_BASE_URL}/projects/{created_project_id}") as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        project = await response.json()
                        print(f"   SUCCESS: Retrieved {project.get('name')}")
                        test_results["get_project"] = True
                    else:
                        error_text = await response.text()
                        print(f"   FAILED: {error_text}")
            except Exception as e:
                print(f"   EXCEPTION: {e}")
        
        # Test 4: GET default project
        print("\n4. Testing GET /projects/default")
        try:
            async with session.get(f"{API_BASE_URL}/projects/default") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    default_project = await response.json()
                    print(f"   SUCCESS: Default project is {default_project.get('name')}")
                    test_results["get_default"] = True
                elif response.status == 404:
                    print("   No default project found (this is OK)")
                    test_results["get_default"] = True  # 404 is acceptable
                else:
                    error_text = await response.text()
                    print(f"   FAILED: {error_text}")
        except Exception as e:
            print(f"   EXCEPTION: {e}")
        
        # Test 5: UPDATE project (if we created one)
        if created_project_id:
            print(f"\n5. Testing PUT /projects/{created_project_id}")
            update_data = {
                "name": f"Updated Test Project {int(time.time())}",
                "description": "Updated description after schema fix"
            }
            
            try:
                async with session.put(
                    f"{API_BASE_URL}/projects/{created_project_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        updated_project = await response.json()
                        print(f"   SUCCESS: Updated to {updated_project.get('name')}")
                        test_results["update_project"] = True
                    else:
                        error_text = await response.text()
                        print(f"   FAILED: {error_text}")
            except Exception as e:
                print(f"   EXCEPTION: {e}")
        
        # Results Summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            print(f"   {test_name:<20}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("ALL TESTS PASSED! The schema fix was successful!")
        else:
            print("Some tests failed. Check the database schema migration.")
        
        return passed == total

if __name__ == "__main__":
    success = asyncio.run(comprehensive_projects_test())
    exit(0 if success else 1)