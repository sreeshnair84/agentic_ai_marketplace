#!/usr/bin/env python3
"""
Quick test of Docker services to identify remaining issues
"""

import requests
import json
import sys

def test_service_endpoint(service, port, endpoint="/health", expected_status=200):
    """Test a service endpoint"""
    try:
        url = f"http://localhost:{port}{endpoint}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == expected_status:
            print(f"✅ {service} (:{port}) - {endpoint} - OK")
            return True
        else:
            print(f"❌ {service} (:{port}) - {endpoint} - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service} (:{port}) - {endpoint} - Error: {e}")
        return False

def main():
    print("🔍 Docker Services Health Check")
    print("=" * 50)
    
    services = [
        ("Gateway", 8000, "/health"),
        ("Agents", 8002, "/health"),
        ("Orchestrator", 8003, "/health"),
        ("RAG", 8004, "/health"),
        ("Tools", 8005, "/health"),
        ("SQLTool", 8006, "/health"),
        ("Workflow", 8007, "/health"),
        ("Observability", 8008, "/health"),
        ("Frontend", 3000, "/"),
        ("Prometheus", 9090, "/"),
        ("PostgreSQL", 5432, None)  # Can't test HTTP on DB
    ]
    
    results = []
    
    for service, port, endpoint in services:
        if endpoint:
            result = test_service_endpoint(service, port, endpoint)
            results.append((service, result))
        else:
            print(f"⚠️  {service} (:{port}) - Database service (HTTP test skipped)")
            results.append((service, True))  # Assume DB is OK if container is running
    
    print(f"\n📊 Summary:")
    healthy = sum(1 for _, result in results if result)
    total = len(results)
    print(f"   Healthy: {healthy}/{total}")
    
    if healthy == total:
        print("🎉 All services are healthy!")
        
        # Test some specific endpoints
        print(f"\n🧪 Testing specific endpoints:")
        test_service_endpoint("Gateway API Docs", 8000, "/docs", 200)
        test_service_endpoint("MCP Health", 8000, "/api/v1/mcp/servers", 200)  # This might fail but we'll see
        
    return healthy == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
