#!/usr/bin/env python3
"""
Test script to demonstrate user management functionality
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def login_admin():
    """Login as admin and get token"""
    print("🔐 Logging in as admin...")
    login_data = {
        "email": "admin@agenticai.com",
        "password": "secret123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["auth_token"]
        print(f"✅ Admin login successful")
        return token
    else:
        print(f"❌ Admin login failed: {response.text}")
        return None

def get_users(token):
    """Get list of all users"""
    print("\n📋 Fetching all users...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   • {user['email']} - {user['role']} - {user.get('firstName', '')} {user.get('lastName', '')}")
        return users
    else:
        print(f"❌ Failed to fetch users: {response.text}")
        return []

def update_user_role(token, user_id, new_role):
    """Update a user's role"""
    print(f"\n🔄 Updating user role to {new_role}...")
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"role": new_role}
    
    response = requests.put(f"{BASE_URL}/auth/users/{user_id}", json=update_data, headers=headers)
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ User role updated successfully")
        print(f"   • Email: {updated_user['email']}")
        print(f"   • New Role: {updated_user['role']}")
        return updated_user
    else:
        print(f"❌ Failed to update user role: {response.text}")
        return None

def demonstrate_user_management():
    """Demonstrate complete user management workflow"""
    print("🧪 AgenticAI User Management Demonstration")
    print("=" * 50)
    
    # Step 1: Login as admin
    token = login_admin()
    if not token:
        return
    
    # Step 2: Get all users
    users = get_users(token)
    if not users:
        return
    
    # Step 3: Find a non-admin user to modify
    test_user = None
    for user in users:
        if user['role'] != 'ADMIN':
            test_user = user
            break
    
    if not test_user:
        print("\n❌ No non-admin users found to demonstrate role change")
        return
    
    print(f"\n🎯 Selected user for demonstration: {test_user['email']} (current role: {test_user['role']})")
    
    # Step 4: Change role to a different one
    current_role = test_user['role']
    new_role = 'ADMIN' if current_role != 'ADMIN' else 'USER'
    
    updated_user = update_user_role(token, test_user['id'], new_role)
    if updated_user:
        time.sleep(1)  # Brief pause
        
        # Step 5: Verify the change
        print(f"\n🔍 Verifying role change...")
        updated_users = get_users(token)
        
        # Step 6: Change back to original role
        print(f"\n↩️ Changing role back to original ({current_role})...")
        update_user_role(token, test_user['id'], current_role)
        
        time.sleep(1)
        print(f"\n✅ Final verification...")
        get_users(token)
    
    print("\n" + "=" * 50)
    print("🎉 User Management Demonstration Complete!")
    print("\n💡 Frontend Usage:")
    print("   1. Open http://localhost:3001/settings")
    print("   2. Navigate to 'User Management' section")
    print("   3. Use dropdown to change user roles")
    print("   4. Changes are applied immediately via API")
    print("\n🔐 API Endpoints Used:")
    print("   • POST /api/v1/auth/login - Admin login")
    print("   • GET /api/v1/auth/users - List all users")
    print("   • PUT /api/v1/auth/users/{id} - Update user role")

if __name__ == "__main__":
    demonstrate_user_management()
