#!/usr/bin/env python3
"""
Test script to verify the backend authentication API
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_health():
    """Test health endpoint"""
    try:
        print("⏳ Testing health endpoint...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📋 Health Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        print("\n⏳ Testing user registration...")
        register_data = {
            "first_name": "Test",
            "last_name": "User", 
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"📝 Registration Status: {response.status_code}")
        print(f"📋 Registration Response: {response.text}")
        
        return response.status_code in [200, 201]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration test failed: {e}")
        return False

def test_login_admin():
    """Test login with default admin credentials"""
    try:
        print("\n⏳ Testing login with admin credentials...")
        login_data = {
            "email": "admin@lcnc.com",
            "password": "secret123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"🔐 Login Status: {response.status_code}")
        print(f"📋 Login Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("auth_token")
            print(f"🎉 Admin login successful! Token: {token[:20] if token else 'None'}...")
            return token
        else:
            print("❌ Admin login failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login test failed: {e}")
        return None

def test_login_user():
    """Test login with test user credentials"""
    try:
        print("\n⏳ Testing login with test user credentials...")
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"🔐 User Login Status: {response.status_code}")
        print(f"📋 User Login Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("auth_token")
            print(f"🎉 User login successful! Token: {token[:20] if token else 'None'}...")
            return token
        else:
            print("❌ User login failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ User login test failed: {e}")
        return None

def test_protected_endpoint(token, user_type="user"):
    """Test accessing a protected endpoint"""
    try:
        print(f"\n⏳ Testing protected endpoint with {user_type} token...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
        print(f"🔒 Protected endpoint status: {response.status_code}")
        print(f"📋 Protected endpoint response: {response.text}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ {user_type.title()} info: {user_data.get('email')} - Role: {user_data.get('role')}")
            return True
        else:
            print(f"❌ Protected endpoint access failed for {user_type}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Protected endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LCNC Backend Authentication...")
    print("=" * 60)
    
    # Test health
    print("1️⃣ Health Check")
    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ Backend server is not responding. Make sure it's running on port 8000!")
        print("Start it with: python run.py from the gateway directory")
        sys.exit(1)
    
    # Test registration
    print("\n2️⃣ User Registration")
    register_ok = test_register()
    
    # Test admin login
    print("\n3️⃣ Admin Login")
    admin_token = test_login_admin()
    
    # Test user login
    print("\n4️⃣ User Login")
    user_token = test_login_user()
    
    # Test protected endpoints
    if admin_token:
        print("\n5️⃣ Admin Protected Access")
        test_protected_endpoint(admin_token, "admin")
    
    if user_token:
        print("\n6️⃣ User Protected Access")
        test_protected_endpoint(user_token, "user")
    
    print("\n" + "=" * 60)
    print("� AUTHENTICATION GUIDE:")
    print("=" * 60)
    
    if health_ok:
        print("✅ Backend API is running at: http://127.0.0.1:8000")
        print("📱 Frontend should be at: http://localhost:3000")
        print()
        print("🔐 LOGIN OPTIONS:")
        print("   1. Default Admin Account:")
        print("      Email: admin@lcnc.com")
        print("      Password: secret123")
        print()
        if register_ok:
            print("   2. Test User Account:")
            print("      Email: test@example.com") 
            print("      Password: testpass123")
            print()
        print("   3. Create New Account:")
        print("      Use the registration form on the frontend")
        print()
        print("🌐 ENDPOINTS:")
        print("   • Health: GET /api/v1/health")
        print("   • Login: POST /api/v1/auth/login")
        print("   • Register: POST /api/v1/auth/register")
        print("   • Profile: GET /api/v1/auth/me")
        print("   • Logout: POST /api/v1/auth/logout")
    
    print("=" * 60)
