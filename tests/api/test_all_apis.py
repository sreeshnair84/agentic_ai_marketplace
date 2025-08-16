"""
Comprehensive API Testing Suite for Agentic AI Acceleration Platform

This module provides automated testing for all documented API endpoints,
including authentication, service health, and functional testing.
"""

import pytest
import httpx
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
import logging
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    base_url: str
    port: int
    health_endpoint: str = "/health"
    docs_endpoint: str = "/docs"

class APITestSuite:
    """Main API testing suite"""
    
    def __init__(self, base_gateway_url: str = "http://localhost:8000"):
        self.base_gateway_url = base_gateway_url
        self.auth_token: Optional[str] = None
        self.test_results: Dict[str, Any] = {}
        
        # Service configurations based on docker-compose.yml
        self.services = {
            "gateway": ServiceConfig("Gateway", "http://localhost:8000", 8000),
            "agents": ServiceConfig("Agents", "http://localhost:8002", 8002),
            "orchestrator": ServiceConfig("Orchestrator", "http://localhost:8003", 8003),
            "rag": ServiceConfig("RAG", "http://localhost:8004", 8004),
            "tools": ServiceConfig("Tools", "http://localhost:8005", 8005),
            "sqltool": ServiceConfig("SQL Tool", "http://localhost:8006", 8006),
            "workflow": ServiceConfig("Workflow Engine", "http://localhost:8007", 8007),
            "observability": ServiceConfig("Observability", "http://localhost:8008", 8008),
        }
        
        # Test data
        self.test_user = {
            "email": "test@example.com",
            "password": "test123",
            "firstName": "Test",
            "lastName": "User"
        }
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive API tests"""
        logger.info("🚀 Starting comprehensive API testing suite...")
        
        start_time = time.time()
        
        # Test sequence
        await self.test_service_health()
        await self.test_authentication()
        await self.test_gateway_endpoints()
        await self.test_agents_service()
        await self.test_orchestrator_service()
        await self.test_tools_service()
        await self.test_rag_service()
        await self.test_sqltool_service()
        await self.test_workflow_service()
        await self.test_observability_service()
        
        end_time = time.time()
        self.test_results["total_duration"] = end_time - start_time
        self.test_results["completed_at"] = datetime.now().isoformat()
        
        # Generate report
        self.generate_test_report()
        
        return self.test_results
    
    async def test_service_health(self):
        """Test health endpoints for all services"""
        logger.info("🏥 Testing service health endpoints...")
        
        health_results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, config in self.services.items():
                try:
                    response = await client.get(f"{config.base_url}{config.health_endpoint}")
                    health_results[service_name] = {
                        "status": response.status_code,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.status_code == 200 else None,
                        "error": None
                    }
                    logger.info(f"✅ {config.name}: {response.status_code} ({response.elapsed.total_seconds() * 1000:.0f}ms)")
                    
                except Exception as e:
                    health_results[service_name] = {
                        "status": "error",
                        "response_time": 0,
                        "data": None,
                        "error": str(e)
                    }
                    logger.error(f"❌ {config.name}: {str(e)}")
        
        self.test_results["health_checks"] = health_results
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        logger.info("🔐 Testing authentication endpoints...")
        
        auth_results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Test login endpoint
                login_response = await client.post(
                    f"{self.base_gateway_url}/api/v1/auth/login",
                    json=self.test_user
                )
                
                auth_results["login"] = {
                    "status": login_response.status_code,
                    "success": login_response.status_code in [200, 401, 422],  # Expected responses
                    "data": login_response.json() if login_response.status_code < 500 else None
                }
                
                # If login successful, store token and test other auth endpoints
                if login_response.status_code == 200:
                    data = login_response.json()
                    if "data" in data and "token" in data["data"]:
                        self.auth_token = data["data"]["token"]
                        
                        # Test profile endpoint
                        headers = {"Authorization": f"Bearer {self.auth_token}"}
                        profile_response = await client.get(
                            f"{self.base_gateway_url}/api/v1/auth/profile",
                            headers=headers
                        )
                        
                        auth_results["profile"] = {
                            "status": profile_response.status_code,
                            "success": profile_response.status_code == 200,
                            "data": profile_response.json() if profile_response.status_code < 500 else None
                        }
                
                logger.info(f"✅ Authentication tests completed")
                
            except Exception as e:
                auth_results["error"] = str(e)
                logger.error(f"❌ Authentication tests failed: {str(e)}")
        
        self.test_results["authentication"] = auth_results
    
    async def test_gateway_endpoints(self):
        """Test gateway-specific endpoints"""
        logger.info("🌐 Testing gateway endpoints...")
        
        gateway_results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("/", "Root endpoint"),
                ("/api/v1", "API v1 root"),
                ("/health", "Health check"),
                ("/health/detailed", "Detailed health"),
                ("/ready", "Readiness probe"),
                ("/live", "Liveness probe"),
            ]
            
            for endpoint, description in endpoints:
                try:
                    response = await client.get(f"{self.base_gateway_url}{endpoint}", headers=headers)
                    gateway_results[endpoint] = {
                        "description": description,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    gateway_results[endpoint] = {
                        "description": description,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["gateway"] = gateway_results
    
    async def test_agents_service(self):
        """Test agents service endpoints"""
        logger.info("🤖 Testing agents service endpoints...")
        
        agents_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            # Test agents endpoints
            endpoints = [
                ("GET", "/api/v1/agents", "List agents"),
                ("GET", "/api/v1/agents/templates", "List agent templates"),
                ("GET", "/api/v1/skills", "List skills"),
                ("GET", "/a2a/cards", "A2A agent cards"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['agents'].base_url}{endpoint}"
                    
                    if method == "GET":
                        response = await client.get(url, headers=headers)
                    elif method == "POST":
                        response = await client.post(url, headers=headers, json={})
                    
                    agents_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    agents_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["agents"] = agents_results
    
    async def test_orchestrator_service(self):
        """Test orchestrator service endpoints"""
        logger.info("🎭 Testing orchestrator service endpoints...")
        
        orchestrator_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("GET", "/api/v1/workflows", "List workflows"),
                ("GET", "/api/v1/skills", "List skills"),
                ("GET", "/api/v1/orchestrate", "List orchestration sessions"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['orchestrator'].base_url}{endpoint}"
                    response = await client.get(url, headers=headers)
                    
                    orchestrator_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    orchestrator_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["orchestrator"] = orchestrator_results
    
    async def test_tools_service(self):
        """Test tools service endpoints"""
        logger.info("🔧 Testing tools service endpoints...")
        
        tools_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("GET", "/api/v1/tools", "List tools"),
                ("GET", "/api/v1/tools/mcp", "List MCP tools"),
                ("GET", "/api/v1/tools/standard", "List standard tools"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['tools'].base_url}{endpoint}"
                    response = await client.get(url, headers=headers)
                    
                    tools_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    tools_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["tools"] = tools_results
    
    async def test_rag_service(self):
        """Test RAG service endpoints"""
        logger.info("📚 Testing RAG service endpoints...")
        
        rag_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("GET", "/api/v1/rag/documents", "List documents"),
                ("GET", "/api/v1/rag/indexes", "List indexes"),
                ("GET", "/api/v1/rag/models", "List embedding models"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['rag'].base_url}{endpoint}"
                    response = await client.get(url, headers=headers)
                    
                    rag_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    rag_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["rag"] = rag_results
    
    async def test_sqltool_service(self):
        """Test SQL Tool service endpoints"""
        logger.info("🗄️ Testing SQL Tool service endpoints...")
        
        sqltool_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("GET", "/api/v1/sqltool/connections", "List database connections"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['sqltool'].base_url}{endpoint}"
                    response = await client.get(url, headers=headers)
                    
                    sqltool_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    sqltool_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["sqltool"] = sqltool_results
    
    async def test_workflow_service(self):
        """Test workflow engine endpoints"""
        logger.info("⚡ Testing workflow engine endpoints...")
        
        workflow_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("GET", "/api/v1/workflow-engine/templates", "List workflow templates"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['workflow'].base_url}{endpoint}"
                    response = await client.get(url, headers=headers)
                    
                    workflow_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    workflow_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["workflow"] = workflow_results
    
    async def test_observability_service(self):
        """Test observability service endpoints"""
        logger.info("👁️ Testing observability service endpoints...")
        
        observability_results = {}
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            endpoints = [
                ("GET", "/api/v1/observability/traces", "List traces"),
                ("GET", "/api/v1/observability/metrics", "Get metrics"),
                ("GET", "/api/v1/observability/health", "System health"),
                ("GET", "/health", "Service health"),
            ]
            
            for method, endpoint, description in endpoints:
                try:
                    url = f"{self.services['observability'].base_url}{endpoint}"
                    response = await client.get(url, headers=headers)
                    
                    observability_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": response.status_code,
                        "success": response.status_code < 500,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    }
                    
                except Exception as e:
                    observability_results[endpoint] = {
                        "description": description,
                        "method": method,
                        "status": "error",
                        "success": False,
                        "error": str(e)
                    }
        
        self.test_results["observability"] = observability_results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating test report...")
        
        # Calculate summary statistics
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        error_tests = 0
        
        for service_name, service_results in self.test_results.items():
            if service_name in ["total_duration", "completed_at"]:
                continue
                
            if isinstance(service_results, dict):
                for endpoint, result in service_results.items():
                    if isinstance(result, dict) and "success" in result:
                        total_tests += 1
                        if result.get("success", False):
                            successful_tests += 1
                        elif result.get("status") == "error":
                            error_tests += 1
                        else:
                            failed_tests += 1
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        self.test_results["summary"] = summary
        
        # Print summary
        logger.info(f"📈 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Successful: {successful_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Errors: {error_tests}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"   Duration: {self.test_results.get('total_duration', 0):.2f}s")

async def main():
    """Main test runner"""
    tester = APITestSuite()
    results = await tester.run_all_tests()
    
    # Save results to file
    output_file = "api_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"📝 Test results saved to {output_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
