#!/usr/bin/env python3
"""
Test script for LLM Models API endpoints
Run this to verify the backend API is working correctly
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_get_models():
    """Test GET /api/tools/llm-models"""
    print("Testing GET /api/tools/llm-models...")
    try:
        response = requests.get(f"{API_BASE}/api/tools/llm-models")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data)} models")
            if data:
                print("Sample model:")
                print(json.dumps(data[0], indent=2))
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_model():
    """Test POST /api/tools/llm-models"""
    print("\nTesting POST /api/tools/llm-models...")
    test_model = {
        "name": "test-model",
        "display_name": "Test Model",
        "provider": "test-provider",
        "model_type": "text",
        "api_endpoint": "https://api.test.com/v1",
        "status": "inactive",
        "capabilities": {
            "max_tokens": 4000,
            "supports_streaming": True,
            "supports_function_calling": False
        },
        "pricing_info": {
            "input_cost_per_token": 0.001,
            "output_cost_per_token": 0.002,
            "currency": "USD"
        },
        "model_config": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/tools/llm-models",
            json=test_model,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Model created successfully:")
            print(json.dumps(data, indent=2))
            return data.get("id")
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_update_model(model_id):
    """Test PUT /api/tools/llm-models/{id}"""
    if not model_id:
        print("\nSkipping update test - no model ID")
        return False
        
    print(f"\nTesting PUT /api/tools/llm-models/{model_id}...")
    update_data = {
        "name": "test-model-updated",
        "display_name": "Test Model Updated",
        "provider": "test-provider",
        "model_type": "text",
        "status": "active"
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/api/tools/llm-models/{model_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Model updated successfully")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_single_model(model_id):
    """Test GET /api/tools/llm-models/{id}"""
    if not model_id:
        print("\nSkipping single model test - no model ID")
        return False
        
    print(f"\nTesting GET /api/tools/llm-models/{model_id}...")
    try:
        response = requests.get(f"{API_BASE}/api/tools/llm-models/{model_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Retrieved model:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_test_model(model_id):
    """Test POST /api/tools/llm-models/{id}/test"""
    if not model_id:
        print("\nSkipping test model - no model ID")
        return False
        
    print(f"\nTesting POST /api/tools/llm-models/{model_id}/test...")
    try:
        response = requests.post(f"{API_BASE}/api/tools/llm-models/{model_id}/test")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Test result:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_delete_model(model_id):
    """Test DELETE /api/tools/llm-models/{id}"""
    if not model_id:
        print("\nSkipping delete test - no model ID")
        return False
        
    print(f"\nTesting DELETE /api/tools/llm-models/{model_id}...")
    try:
        response = requests.delete(f"{API_BASE}/api/tools/llm-models/{model_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Model deleted successfully")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Models API Test Suite ===")
    
    # Test basic functionality
    success = test_get_models()
    if not success:
        print("❌ Basic GET test failed. Check if backend is running.")
        sys.exit(1)
    
    # Test CRUD operations
    model_id = test_create_model()
    test_update_model(model_id)
    test_get_single_model(model_id)
    test_test_model(model_id)
    test_delete_model(model_id)
    
    print("\n=== Test Complete ===")
    print("✅ All API endpoints tested")

if __name__ == "__main__":
    main()
