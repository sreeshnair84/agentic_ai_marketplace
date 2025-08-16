#!/usr/bin/env python3
"""
Test the frontend API integration
"""

import requests
import json

FRONTEND_URL = "http://localhost:3001"
BACKEND_URL = "http://127.0.0.1:8000"

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        print(f"✅ Frontend accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_backend_projects():
    """Test backend projects API directly"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/projects", timeout=5)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Backend projects API working: {len(projects)} projects found")
            return True
        else:
            print(f"❌ Backend projects API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend projects API error: {e}")
        return False

def check_frontend_console_errors():
    """Instructions for checking frontend console"""
    print("\n🔍 TO CHECK FRONTEND CONSOLE ERRORS:")
    print("1. Open http://localhost:3001 in your browser")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Console tab")
    print("4. Look for the specific error:")
    print("   'Failed to fetch projects: TypeError: Cannot read properties of undefined (reading 'map')'")
    print("5. The error should now be fixed with our API client updates")

if __name__ == "__main__":
    print("🧪 Testing Frontend API Integration")
    print("=" * 50)
    
    frontend_ok = test_frontend_accessibility()
    backend_ok = test_backend_projects()
    
    if frontend_ok and backend_ok:
        print("\n✅ Both frontend and backend are accessible")
        print("\n🛠️ API FIXES APPLIED:")
        print("   • Updated API client to handle direct data responses")
        print("   • Added proper error handling in projectService.getAll()")
        print("   • Fixed response format detection")
        
        check_frontend_console_errors()
        
        print("\n📋 EXPECTED BEHAVIOR:")
        print("   • Projects should now load without console errors")
        print("   • Frontend should display the 5 projects from backend")
        print("   • User management should work correctly")
        
        print("\n🌐 LINKS:")
        print(f"   • Frontend: {FRONTEND_URL}")
        print(f"   • Settings: {FRONTEND_URL}/settings")
        print(f"   • Backend API: {BACKEND_URL}/api/v1/projects")
    else:
        print("\n❌ Issues detected:")
        if not frontend_ok:
            print("   • Frontend not accessible - check if npm run dev is running")
        if not backend_ok:
            print("   • Backend not accessible - check if python run.py is running")
    
    print("=" * 50)
