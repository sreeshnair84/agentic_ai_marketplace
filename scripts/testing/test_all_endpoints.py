#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Suite
Tests all endpoints across all 8 microservices in the LCNC Multi-Agent Platform

Services tested:
- Gateway Service (Port 8000)
- Agents Service (Port 8002) 
- Orchestrator Service (Port 8003)
- RAG Service (Port 8004)
- Tools Service (Port 8005)
- SQLTool Service (Port 8006)
- Workflow Engine (Port 8007)
- Observability Service (Port 8008)
"""

import asyncio
import aiohttp
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    endpoint: str
    method: str
    service: str
    status_code: int
    success: bool
    response_time_ms: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class EndpointTester:
    """Comprehensive endpoint testing class"""
    
    def __init__(self):
        self.base_urls = {
            'gateway': 'http://localhost:8000',
            'agents': 'http://localhost:8002', 
            'orchestrator': 'http://localhost:8003',
            'rag': 'http://localhost:8004',
            'tools': 'http://localhost:8005',
            'sqltool': 'http://localhost:8006',
            'workflow': 'http://localhost:8007',
            'observability': 'http://localhost:8008'
        }
        self.results: List[TestResult] = []
        self.test_data = self._prepare_test_data()
        
    def _prepare_test_data(self) -> Dict[str, Any]:
        """Prepare test data for POST requests"""
        return {
            'agent_create': {
                "name": f"test-agent-{uuid.uuid4().hex[:8]}",
                "type": "text_processor",
                "description": "Test agent for API testing",
                "capabilities": ["text_processing", "analysis"],
                "configuration": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "framework": "gemini",
                "ai_provider": "google",
                "status": "active"
            },
            'workflow_create': {
                "name": f"test-workflow-{uuid.uuid4().hex[:8]}",
                "description": "Test workflow for API testing",
                "definition": {
                    "steps": [
                        {"id": "step1", "type": "agent_task", "name": "Process Input"},
                        {"id": "step2", "type": "validation", "name": "Validate Result"}
                    ],
                    "connections": [{"from": "step1", "to": "step2"}]
                },
                "trigger_type": "manual",
                "status": "active"
            },
            'project_create': {
                "name": f"test-project-{uuid.uuid4().hex[:8]}",
                "description": "Test project for API testing",
                "settings": {"environment": "test"}
            },
            'task_create': {
                "type": "text_processing",
                "input": {"text": "Test input for API testing"},
                "agent_id": "test-agent",
                "priority": "normal"
            },
            'message_send': {
                "content": "Hello, this is a test message",
                "sender": "api-test",
                "recipient": "test-agent",
                "message_type": "text"
            },
            'search_request': {
                "query": "test search query",
                "namespace": "default",
                "n_results": 5
            },
            'document_create': {
                "content": "This is test document content for API testing. It contains sample text to test the RAG functionality.",
                "metadata": {
                    "title": "Test Document",
                    "source": "API Test",
                    "document_type": "text",
                    "tags": ["test", "api"]
                }
            },
            'rag_request': {
                "query": "What is this document about?",
                "namespace": "default",
                "n_context": 3,
                "model": "gpt-4o"
            },
            'tool_execute': {
                "tool_name": "echo",
                "parameters": {"text": "Hello from API test"}
            },
            'user_register': {
                "username": f"testuser{uuid.uuid4().hex[:8]}",
                "email": f"test{uuid.uuid4().hex[:8]}@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User"
            },
            'login_request': {
                "username": "admin",
                "password": "admin123"
            }
        }
    
    async def test_endpoint(self, session: aiohttp.ClientSession, service: str, method: str, 
                          endpoint: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None) -> TestResult:
        """Test a single endpoint"""
        
        url = f"{self.base_urls[service]}{endpoint}"
        start_time = time.time()
        
        try:
            # Default headers
            default_headers = {'Content-Type': 'application/json'}
            if headers:
                default_headers.update(headers)
            
            # Make request
            async with session.request(
                method=method,
                url=url,
                json=data if data else None,
                headers=default_headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_time_ms = (time.time() - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                success = response.status < 400
                
                result = TestResult(
                    endpoint=endpoint,
                    method=method,
                    service=service,
                    status_code=response.status,
                    success=success,
                    response_time_ms=response_time_ms,
                    response_data=response_data if success else None,
                    error_message=None if success else f"HTTP {response.status}: {response_data}"
                )
                
                status_emoji = "✅" if success else "❌"
                logger.info(f"{status_emoji} {service.upper()}: {method} {endpoint} -> {response.status} ({response_time_ms:.1f}ms)")
                
                return result
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            result = TestResult(
                endpoint=endpoint,
                method=method,
                service=service,
                status_code=0,
                success=False,
                response_time_ms=response_time_ms,
                error_message=str(e)
            )
            
            logger.error(f"❌ {service.upper()}: {method} {endpoint} -> ERROR: {e}")
            return result
    
    async def test_gateway_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test Gateway Service endpoints (Port 8000)"""
        
        logger.info("🔄 Testing Gateway Service (Port 8000)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/health'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/health/detailed'))
        
        # Authentication endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'POST', '/api/v1/auth/register', 
                                              self.test_data['user_register']))
        results.append(await self.test_endpoint(session, 'gateway', 'POST', '/api/v1/auth/login', 
                                              self.test_data['login_request']))
        
        # Project endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/projects'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/projects/default'))
        results.append(await self.test_endpoint(session, 'gateway', 'POST', '/api/v1/projects', 
                                              self.test_data['project_create']))
        
        # Sample queries endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/sample-queries'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/sample-queries/featured'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/sample-queries/agents'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/sample-queries/search'))
        
        # Agent proxy endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/agents'))
        
        # Tools proxy endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/tools'))
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/tools'))  # Legacy endpoint
        
        # Workflow proxy endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/workflows'))
        
        # Statistics endpoints
        results.append(await self.test_endpoint(session, 'gateway', 'GET', '/api/v1/stats'))
        
        return results
    
    async def test_agents_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test Agents Service endpoints (Port 8002)"""
        
        logger.info("🔄 Testing Agents Service (Port 8002)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/health'))
        
        # Agent management endpoints
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/agents'))
        results.append(await self.test_endpoint(session, 'agents', 'POST', '/agents', 
                                              self.test_data['agent_create']))
        
        # Registry endpoints  
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/registry/agents'))
        results.append(await self.test_endpoint(session, 'agents', 'POST', '/registry/agents', 
                                              self.test_data['agent_create']))
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/registry/capabilities'))
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/registry/sample-queries'))
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/registry/sample-queries/quick-start'))
        
        # A2A Protocol endpoints
        results.append(await self.test_endpoint(session, 'agents', 'GET', '/a2a/cards'))
        results.append(await self.test_endpoint(session, 'agents', 'POST', '/a2a/message/send', 
                                              self.test_data['message_send']))
        results.append(await self.test_endpoint(session, 'agents', 'POST', '/a2a/discover'))
        
        return results
    
    async def test_orchestrator_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test Orchestrator Service endpoints (Port 8003)"""
        
        logger.info("🔄 Testing Orchestrator Service (Port 8003)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/health'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/ready'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/live'))
        
        # Workflow management endpoints
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/api/v1/workflows'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'POST', '/api/v1/workflows', 
                                              self.test_data['workflow_create']))
        
        # Agent management endpoints
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/api/v1/agents'))
        
        # Task management endpoints  
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/api/v1/tasks'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'POST', '/api/v1/tasks', 
                                              self.test_data['task_create']))
        
        # A2A Protocol endpoints
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/a2a/cards'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'POST', '/a2a/discover'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'POST', '/a2a/message/send', 
                                              self.test_data['message_send']))
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/a2a/agents'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'GET', '/a2a/sessions'))
        results.append(await self.test_endpoint(session, 'orchestrator', 'POST', '/a2a/orchestrate'))
        
        return results
    
    async def test_rag_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test RAG Service endpoints (Port 8004)"""
        
        logger.info("🔄 Testing RAG Service (Port 8004)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'rag', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'rag', 'GET', '/health'))
        
        # Model management endpoints
        results.append(await self.test_endpoint(session, 'rag', 'GET', '/models'))
        results.append(await self.test_endpoint(session, 'rag', 'POST', '/models/reload'))
        
        # Document management endpoints
        results.append(await self.test_endpoint(session, 'rag', 'POST', '/documents', 
                                              self.test_data['document_create']))
        
        # Search endpoints
        results.append(await self.test_endpoint(session, 'rag', 'POST', '/search', 
                                              self.test_data['search_request']))
        
        # Generation endpoints
        results.append(await self.test_endpoint(session, 'rag', 'POST', '/generate', 
                                              self.test_data['rag_request']))
        
        return results
    
    async def test_tools_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test Tools Service endpoints (Port 8005)"""
        
        logger.info("🔄 Testing Tools Service (Port 8005)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/health'))
        
        # Tool management endpoints
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools'))
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools/templates'))
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools/instances'))
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools/categories'))
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools/llm-models'))
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools/embedding-models'))
        
        # Tool execution endpoints
        results.append(await self.test_endpoint(session, 'tools', 'POST', '/tools/execute', 
                                              self.test_data['tool_execute']))
        
        # MCP endpoints
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/tools/mcp'))
        
        # Sample queries endpoints
        results.append(await self.test_endpoint(session, 'tools', 'GET', '/sample-queries/tools'))
        
        return results
    
    async def test_sqltool_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test SQLTool Service endpoints (Port 8006)"""
        
        logger.info("🔄 Testing SQLTool Service (Port 8006)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'sqltool', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'sqltool', 'GET', '/health'))
        
        # Database endpoints
        results.append(await self.test_endpoint(session, 'sqltool', 'GET', '/databases'))
        results.append(await self.test_endpoint(session, 'sqltool', 'GET', '/connections'))
        
        return results
    
    async def test_workflow_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test Workflow Engine endpoints (Port 8007)"""
        
        logger.info("🔄 Testing Workflow Engine Service (Port 8007)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/health'))
        
        # Workflow management endpoints
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/workflows'))
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/executions'))
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/templates'))
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/schedules'))
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/registry/search'))
        
        # Sample queries endpoints
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/sample-queries/workflows'))
        results.append(await self.test_endpoint(session, 'workflow', 'GET', '/sample-queries/quick-start'))
        
        return results
    
    async def test_observability_service(self, session: aiohttp.ClientSession) -> List[TestResult]:
        """Test Observability Service endpoints (Port 8008)"""
        
        logger.info("🔄 Testing Observability Service (Port 8008)...")
        results = []
        
        # Basic endpoints
        results.append(await self.test_endpoint(session, 'observability', 'GET', '/'))
        results.append(await self.test_endpoint(session, 'observability', 'GET', '/health'))
        
        # Monitoring endpoints
        results.append(await self.test_endpoint(session, 'observability', 'GET', '/metrics'))
        results.append(await self.test_endpoint(session, 'observability', 'GET', '/logs'))
        results.append(await self.test_endpoint(session, 'observability', 'GET', '/traces'))
        results.append(await self.test_endpoint(session, 'observability', 'GET', '/services'))
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all endpoint tests across all services"""
        
        logger.info("🚀 Starting Comprehensive Endpoint Testing...")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Test all services
            test_functions = [
                self.test_gateway_service,
                self.test_agents_service,
                self.test_orchestrator_service,
                self.test_rag_service,
                self.test_tools_service,
                self.test_sqltool_service,
                self.test_workflow_service,
                self.test_observability_service
            ]
            
            all_results = []
            for test_func in test_functions:
                try:
                    service_results = await test_func(session)
                    all_results.extend(service_results)
                    self.results.extend(service_results)
                except Exception as e:
                    logger.error(f"Error testing service: {e}")
                
                # Brief pause between services
                await asyncio.sleep(0.5)
        
        total_time = time.time() - start_time
        
        # Generate summary report
        return self._generate_summary_report(total_time)
    
    def _generate_summary_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test summary report"""
        
        # Calculate statistics
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by service
        service_stats = {}
        for result in self.results:
            if result.service not in service_stats:
                service_stats[result.service] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'avg_response_time': 0,
                    'endpoints': []
                }
            
            stats = service_stats[result.service]
            stats['total'] += 1
            stats['endpoints'].append({
                'endpoint': result.endpoint,
                'method': result.method,
                'status': result.status_code,
                'success': result.success,
                'response_time_ms': result.response_time_ms,
                'error': result.error_message
            })
            
            if result.success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
        
        # Calculate average response times
        for service in service_stats:
            response_times = [e['response_time_ms'] for e in service_stats[service]['endpoints']]
            service_stats[service]['avg_response_time'] = sum(response_times) / len(response_times) if response_times else 0
            service_stats[service]['success_rate'] = (service_stats[service]['successful'] / service_stats[service]['total'] * 100) if service_stats[service]['total'] > 0 else 0
        
        # Generate report
        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'total_time_seconds': total_time,
                'timestamp': datetime.now().isoformat()
            },
            'service_statistics': service_stats,
            'failed_endpoints': [
                {
                    'service': r.service,
                    'endpoint': r.endpoint,
                    'method': r.method,
                    'status_code': r.status_code,
                    'error': r.error_message
                }
                for r in self.results if not r.success
            ]
        }
        
        return report
    
    def print_summary_report(self, report: Dict[str, Any]):
        """Print formatted summary report to console"""
        
        summary = report['summary']
        
        print("\n" + "=" * 80)
        print("🔍 COMPREHENSIVE ENDPOINT TESTING SUMMARY")
        print("=" * 80)
        
        print(f"📊 Overall Statistics:")
        print(f"   Total Tests:      {summary['total_tests']}")
        print(f"   Successful:       {summary['successful_tests']} ✅")
        print(f"   Failed:           {summary['failed_tests']} ❌")
        print(f"   Success Rate:     {summary['success_rate']:.1f}%")
        print(f"   Total Time:       {summary['total_time_seconds']:.2f}s")
        print(f"   Timestamp:        {summary['timestamp']}")
        
        print(f"\n🔧 Service-by-Service Results:")
        print("-" * 80)
        
        for service_name, stats in report['service_statistics'].items():
            status_emoji = "✅" if stats['success_rate'] >= 80 else "⚠️" if stats['success_rate'] >= 50 else "❌"
            print(f"{status_emoji} {service_name.upper():<15} | Tests: {stats['total']:<3} | Success: {stats['successful']:<3} | Failed: {stats['failed']:<3} | Rate: {stats['success_rate']:.1f}% | Avg Time: {stats['avg_response_time']:.1f}ms")
        
        # Show failed endpoints if any
        if report['failed_endpoints']:
            print(f"\n❌ Failed Endpoints ({len(report['failed_endpoints'])}):")
            print("-" * 80)
            for failure in report['failed_endpoints']:
                print(f"   {failure['service']:<12} | {failure['method']:<6} {failure['endpoint']:<40} | Status: {failure['status_code']:<3} | Error: {failure['error'][:50]}")
        
        print("\n" + "=" * 80)
        
        if summary['success_rate'] >= 90:
            print("🎉 EXCELLENT! All services are operating optimally.")
        elif summary['success_rate'] >= 75:
            print("✅ GOOD! Most services are working well, minor issues detected.")
        elif summary['success_rate'] >= 50:
            print("⚠️  WARNING! Several endpoints are failing, investigation needed.")
        else:
            print("❌ CRITICAL! Many endpoints are failing, immediate attention required.")
        
        print("=" * 80)

async def main():
    """Main execution function"""
    
    print("🚀 LCNC Multi-Agent Platform - Comprehensive Endpoint Testing")
    print("Testing all 8 microservices and their API endpoints...")
    print("=" * 80)
    
    tester = EndpointTester()
    
    try:
        # Run all tests
        report = await tester.run_all_tests()
        
        # Print summary
        tester.print_summary_report(report)
        
        # Save detailed report to file
        report_filename = f"endpoint_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Exit with appropriate code
        if report['summary']['success_rate'] >= 75:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
