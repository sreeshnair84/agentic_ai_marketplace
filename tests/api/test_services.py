"""
Individual Service Testing Script

This script can test individual backend services without requiring
the full Docker environment to be running.
"""

import httpx
import asyncio
import json
import sys
import argparse
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceTester:
    """Test individual services"""
    
    def __init__(self, service_url: str):
        self.service_url = service_url.rstrip('/')
        
    async def test_service(self) -> Dict[str, Any]:
        """Test a single service"""
        results = {
            "service_url": self.service_url,
            "tests": {},
            "summary": {}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            await self._test_endpoint(client, "/health", "Health Check", results)
            
            # Test root endpoint
            await self._test_endpoint(client, "/", "Root Endpoint", results)
            
            # Test docs endpoint
            await self._test_endpoint(client, "/docs", "API Documentation", results)
            
            # Test common API endpoints
            api_endpoints = [
                "/api/v1",
                "/api/v1/health",
                "/ready",
                "/live"
            ]
            
            for endpoint in api_endpoints:
                await self._test_endpoint(client, endpoint, f"API Endpoint {endpoint}", results)
        
        # Calculate summary
        total_tests = len(results["tests"])
        successful_tests = sum(1 for test in results["tests"].values() if test.get("success", False))
        
        results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return results
    
    async def _test_endpoint(self, client: httpx.AsyncClient, endpoint: str, description: str, results: Dict[str, Any]):
        """Test a single endpoint"""
        try:
            url = f"{self.service_url}{endpoint}"
            response = await client.get(url)
            
            results["tests"][endpoint] = {
                "description": description,
                "url": url,
                "status_code": response.status_code,
                "success": response.status_code < 500,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "content_type": response.headers.get("content-type", ""),
                "error": None
            }
            
            # Try to parse JSON response
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    json_data = response.json()
                    results["tests"][endpoint]["data"] = json_data
                except:
                    results["tests"][endpoint]["data"] = None
            
            status_emoji = "✅" if response.status_code < 500 else "❌"
            logger.info(f"{status_emoji} {description}: {response.status_code} ({response.elapsed.total_seconds() * 1000:.0f}ms)")
            
        except Exception as e:
            results["tests"][endpoint] = {
                "description": description,
                "url": f"{self.service_url}{endpoint}",
                "status_code": None,
                "success": False,
                "response_time_ms": 0,
                "content_type": "",
                "error": str(e)
            }
            logger.error(f"❌ {description}: {str(e)}")

async def test_gateway_service():
    """Test the gateway service running locally"""
    logger.info("🌐 Testing Gateway Service (Local)")
    
    # Test if gateway is running locally (common development scenario)
    tester = ServiceTester("http://localhost:8000")
    results = await tester.test_service()
    
    # Additional gateway-specific tests
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test authentication endpoints
        auth_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/profile"
        ]
        
        for endpoint in auth_endpoints:
            try:
                url = f"http://localhost:8000{endpoint}"
                
                if endpoint == "/api/v1/auth/login":
                    # Test with invalid credentials (should return 401 or 422)
                    response = await client.post(url, json={"email": "test@test.com", "password": "invalid"})
                else:
                    # Test without authentication (should return 401)
                    response = await client.get(url)
                
                results["tests"][f"POST_{endpoint}" if endpoint.endswith("login") else f"GET_{endpoint}"] = {
                    "description": f"Auth endpoint {endpoint}",
                    "url": url,
                    "status_code": response.status_code,
                    "success": response.status_code in [401, 422, 200],  # Expected responses
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "content_type": response.headers.get("content-type", ""),
                    "error": None
                }
                
                logger.info(f"✅ Auth {endpoint}: {response.status_code}")
                
            except Exception as e:
                logger.error(f"❌ Auth {endpoint}: {str(e)}")
    
    return results

async def test_specific_service(service_name: str, port: int):
    """Test a specific service by name and port"""
    logger.info(f"🔧 Testing {service_name} Service on port {port}")
    
    tester = ServiceTester(f"http://localhost:{port}")
    results = await tester.test_service()
    
    return results

async def test_all_local_services():
    """Test all services that might be running locally"""
    logger.info("🚀 Testing all local services...")
    
    services = {
        "gateway": 8000,
        "agents": 8002,
        "orchestrator": 8003,
        "rag": 8004,
        "tools": 8005,
        "sqltool": 8006,
        "workflow": 8007,
        "observability": 8008
    }
    
    all_results = {}
    
    for service_name, port in services.items():
        logger.info(f"\n--- Testing {service_name} service ---")
        try:
            results = await test_specific_service(service_name, port)
            all_results[service_name] = results
        except Exception as e:
            logger.error(f"Failed to test {service_name}: {str(e)}")
            all_results[service_name] = {"error": str(e)}
    
    # Generate overall summary
    total_services = len(services)
    healthy_services = sum(1 for results in all_results.values() 
                          if isinstance(results, dict) and 
                          results.get("summary", {}).get("success_rate", 0) > 50)
    
    logger.info(f"\n📊 Overall Summary:")
    logger.info(f"   Services tested: {total_services}")
    logger.info(f"   Healthy services: {healthy_services}")
    logger.info(f"   Service health rate: {(healthy_services / total_services * 100):.1f}%")
    
    return all_results

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Agentic AI Acceleration API services")
    parser.add_argument("--service", help="Specific service to test (gateway, agents, etc.)")
    parser.add_argument("--port", type=int, help="Port number for the service")
    parser.add_argument("--url", help="Full URL of the service to test")
    parser.add_argument("--output", help="Output file for results", default="service_test_results.json")
    
    args = parser.parse_args()
    
    results = None
    
    if args.url:
        # Test specific URL
        tester = ServiceTester(args.url)
        results = await tester.test_service()
        
    elif args.service and args.port:
        # Test specific service
        results = await test_specific_service(args.service, args.port)
        
    elif args.service == "gateway":
        # Test gateway service specifically
        results = await test_gateway_service()
        
    else:
        # Test all services
        results = await test_all_local_services()
    
    # Save results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📝 Results saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
