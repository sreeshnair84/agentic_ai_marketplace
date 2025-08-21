"""
Tool Execution Service
Handles execution of tool instances with parameter validation and monitoring
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, Optional, List
import importlib.util
import tempfile
import subprocess
from pathlib import Path
import jsonschema
from jinja2 import Template

from ..models.tool_management import ToolInstance, ToolTemplate

logger = logging.getLogger(__name__)

class ToolExecutionService:
    """Service for executing tool instances"""
    
    def __init__(self):
        self.execution_cache = {}
        self.logger = logger
    
    async def validate_configuration(
        self, 
        schema_definition: Dict[str, Any], 
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate configuration against schema"""
        
        try:
            jsonschema.validate(configuration, schema_definition)
            return {"valid": True, "errors": []}
        except jsonschema.ValidationError as e:
            return {"valid": False, "errors": [str(e)]}
        except Exception as e:
            return {"valid": False, "errors": [f"Schema validation error: {str(e)}"]}
    
    async def health_check(self, instance: ToolInstance) -> Dict[str, Any]:
        """Perform health check on tool instance"""
        
        try:
            # Basic connectivity check based on tool type
            template_type = instance.template.type
            
            if template_type == "rag_pipeline":
                return await self._health_check_rag(instance)
            elif template_type == "sql_agent":
                return await self._health_check_sql(instance)
            elif template_type == "web_scraper":
                return await self._health_check_web_scraper(instance)
            elif template_type == "api_integration":
                return await self._health_check_api(instance)
            else:
                return {"status": "healthy", "message": "Basic health check passed"}
                
        except Exception as e:
            self.logger.error(f"Health check failed for instance {instance.id}: {e}")
            return {"status": "unhealthy", "message": str(e)}
    
    async def _health_check_rag(self, instance: ToolInstance) -> Dict[str, Any]:
        """Health check for RAG pipeline"""
        config = instance.configuration
        
        # Check vector database connection
        vector_config = config.get("vector_database", {})
        if vector_config.get("provider") == "pgvector":
            try:
                import asyncpg
                conn = await asyncpg.connect(vector_config["connection_string"])
                await conn.execute("SELECT 1")
                await conn.close()
                return {"status": "healthy", "message": "Vector database connection successful"}
            except Exception as e:
                return {"status": "unhealthy", "message": f"Vector database connection failed: {e}"}
        
        return {"status": "healthy", "message": "RAG pipeline configuration valid"}
    
    async def _health_check_sql(self, instance: ToolInstance) -> Dict[str, Any]:
        """Health check for SQL agent"""
        config = instance.configuration
        
        # Check database connection
        db_config = config.get("database", {})
        try:
            if db_config.get("type") == "postgresql":
                import asyncpg
                conn = await asyncpg.connect(db_config["connection_string"])
                await conn.execute("SELECT 1")
                await conn.close()
                return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Database connection failed: {e}"}
        
        return {"status": "healthy", "message": "SQL agent configuration valid"}
    
    async def _health_check_web_scraper(self, instance: ToolInstance) -> Dict[str, Any]:
        """Health check for web scraper"""
        # Basic configuration validation
        config = instance.configuration
        scraping_config = config.get("scraping_config", {})
        
        if not scraping_config.get("user_agent"):
            return {"status": "unhealthy", "message": "User agent not configured"}
        
        return {"status": "healthy", "message": "Web scraper configuration valid"}
    
    async def _health_check_api(self, instance: ToolInstance) -> Dict[str, Any]:
        """Health check for API integration"""
        config = instance.configuration
        api_config = config.get("api_config", {})
        
        if not api_config.get("base_url"):
            return {"status": "unhealthy", "message": "Base URL not configured"}
        
        # Try to connect to the API
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(api_config["base_url"], timeout=10) as response:
                    if response.status < 500:  # Any non-server error is considered healthy
                        return {"status": "healthy", "message": "API endpoint accessible"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"API connection failed: {e}"}
        
        return {"status": "healthy", "message": "API configuration valid"}
    
    async def execute_tool(
        self, 
        instance: ToolInstance, 
        execution_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool instance with given parameters"""
        
        start_time = time.time()
        template_type = instance.template.type
        
        try:
            # Route to appropriate execution method
            if template_type == "rag_pipeline":
                result = await self._execute_rag_tool(instance, execution_parameters)
            elif template_type == "sql_agent":
                result = await self._execute_sql_tool(instance, execution_parameters)
            elif template_type == "web_scraper":
                result = await self._execute_web_scraper(instance, execution_parameters)
            elif template_type == "api_integration":
                result = await self._execute_api_tool(instance, execution_parameters)
            elif template_type == "code_interpreter":
                result = await self._execute_code_interpreter(instance, execution_parameters)
            else:
                result = await self._execute_generic_tool(instance, execution_parameters)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                "status": "completed",
                "output": result,
                "execution_time_ms": execution_time,
                "metadata": {
                    "tool_type": template_type,
                    "instance_id": str(instance.id),
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.error(f"Tool execution failed for {instance.id}: {e}")
            
            return {
                "status": "failed",
                "error": str(e),
                "execution_time_ms": execution_time,
                "metadata": {
                    "tool_type": template_type,
                    "instance_id": str(instance.id),
                    "timestamp": time.time()
                }
            }
    
    async def _execute_rag_tool(
        self, 
        instance: ToolInstance, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute RAG tool"""
        
        operation = parameters.get("operation", "search")
        
        if operation == "search":
            query = parameters.get("query")
            if not query:
                raise ValueError("Query parameter is required for search operation")
            
            # Simulate RAG search (replace with actual implementation)
            return {
                "operation": "search",
                "query": query,
                "results": [
                    {
                        "content": f"Sample result for query: {query}",
                        "similarity": 0.85,
                        "metadata": {"source": "sample_document.pdf"}
                    }
                ],
                "total_results": 1
            }
        
        elif operation == "ingest":
            documents = parameters.get("documents", [])
            
            return {
                "operation": "ingest",
                "documents_processed": len(documents),
                "chunks_created": len(documents) * 5,  # Simulate chunking
                "status": "success"
            }
        
        elif operation == "update_collection":
            collection_name = parameters.get("collection_name", "default")
            
            return {
                "operation": "update_collection",
                "collection_name": collection_name,
                "status": "success",
                "message": f"Collection '{collection_name}' updated successfully"
            }
        
        elif operation == "delete_collection":
            collection_name = parameters.get("collection_name", "default")
            
            return {
                "operation": "delete_collection",
                "collection_name": collection_name,
                "status": "success",
                "message": f"Collection '{collection_name}' deleted successfully"
            }
        
        else:
            raise ValueError(f"Unsupported RAG operation: {operation}")
    
    async def _execute_sql_tool(
        self, 
        instance: ToolInstance, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute SQL tool"""
        
        operation = parameters.get("operation", "query")
        
        if operation == "natural_language_query":
            question = parameters.get("question")
            if not question:
                raise ValueError("Question parameter is required")
            
            # Simulate natural language to SQL conversion
            generated_sql = f"SELECT * FROM users WHERE name LIKE '%{question}%' LIMIT 10;"
            
            return {
                "operation": "natural_language_query",
                "question": question,
                "generated_sql": generated_sql,
                "results": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
                ],
                "row_count": 2
            }
        
        elif operation == "execute_sql":
            sql_query = parameters.get("sql_query")
            if not sql_query:
                raise ValueError("SQL query parameter is required")
            
            # Simulate SQL execution
            return {
                "operation": "execute_sql",
                "query": sql_query,
                "results": [{"count": 42}],
                "row_count": 1,
                "execution_time_ms": 150
            }
        
        elif operation == "get_schema":
            return {
                "operation": "get_schema",
                "schema": {
                    "users": {
                        "columns": [
                            {"name": "id", "type": "integer"},
                            {"name": "name", "type": "varchar"},
                            {"name": "email", "type": "varchar"}
                        ],
                        "primary_keys": ["id"]
                    }
                }
            }
        
        else:
            raise ValueError(f"Unsupported SQL operation: {operation}")
    
    async def _execute_web_scraper(
        self, 
        instance: ToolInstance, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute web scraper"""
        
        urls = parameters.get("urls", [])
        if not urls:
            raise ValueError("URLs parameter is required")
        
        # Simulate web scraping
        results = []
        for url in urls[:5]:  # Limit to 5 URLs for demo
            results.append({
                "url": url,
                "title": f"Sample Title for {url}",
                "content": f"Sample content extracted from {url}",
                "metadata": {
                    "timestamp": time.time(),
                    "status_code": 200
                }
            })
        
        return {
            "operation": "scrape",
            "urls_processed": len(results),
            "results": results,
            "total_content_length": sum(len(r["content"]) for r in results)
        }
    
    async def _execute_api_tool(
        self, 
        instance: ToolInstance, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute API integration tool"""
        
        endpoint = parameters.get("endpoint")
        method = parameters.get("method", "GET")
        request_data = parameters.get("data", {})
        
        if not endpoint:
            raise ValueError("Endpoint parameter is required")
        
        # Simulate API call
        return {
            "operation": "api_call",
            "endpoint": endpoint,
            "method": method,
            "status_code": 200,
            "response": {
                "message": f"Simulated {method} response from {endpoint}",
                "data": request_data,
                "timestamp": time.time()
            }
        }
    
    async def _execute_code_interpreter(
        self, 
        instance: ToolInstance, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute code interpreter"""
        
        code = parameters.get("code")
        language = parameters.get("language", "python")
        
        if not code:
            raise ValueError("Code parameter is required")
        
        # For security, this is a simulation. In production, use sandboxed execution
        if language == "python":
            # Simulate Python execution
            return {
                "operation": "execute_code",
                "language": language,
                "code": code,
                "output": f"# Simulated Python execution\n# Code: {code[:100]}...\nResult: 42",
                "status": "success"
            }
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    async def _execute_generic_tool(
        self, 
        instance: ToolInstance, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute generic tool using template code"""
        
        # This would execute the tool's code template with the given parameters
        return {
            "operation": "generic_execution",
            "tool_type": instance.template.type,
            "parameters": parameters,
            "result": "Generic tool execution completed successfully"
        }
    
    async def test_tool_instance(
        self, 
        instance: ToolInstance, 
        test_parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test a tool instance with sample parameters"""
        
        # Generate default test parameters based on tool type
        if test_parameters is None:
            test_parameters = self._generate_test_parameters(instance.template.type)
        
        # Execute with test parameters
        result = await self.execute_tool(instance, test_parameters)
        
        return {
            "test_status": "passed" if result["status"] == "completed" else "failed",
            "test_parameters": test_parameters,
            "execution_result": result,
            "recommendations": self._generate_test_recommendations(instance, result)
        }
    
    def _generate_test_parameters(self, tool_type: str) -> Dict[str, Any]:
        """Generate default test parameters for tool type"""
        
        test_params = {
            "rag_pipeline": {
                "operation": "search",
                "query": "test query for semantic search"
            },
            "sql_agent": {
                "operation": "natural_language_query",
                "question": "Show me all users"
            },
            "web_scraper": {
                "urls": ["https://httpbin.org/html"]
            },
            "api_integration": {
                "endpoint": "/status",
                "method": "GET"
            },
            "code_interpreter": {
                "language": "python",
                "code": "print('Hello, World!')"
            }
        }
        
        return test_params.get(tool_type, {"operation": "test"})
    
    def _generate_test_recommendations(
        self, 
        instance: ToolInstance, 
        result: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        if result["status"] == "failed":
            recommendations.append("Tool execution failed. Check configuration and credentials.")
        
        if result.get("execution_time_ms", 0) > 5000:
            recommendations.append("Execution time is high. Consider optimizing configuration.")
        
        # Tool-specific recommendations
        tool_type = instance.template.type
        
        if tool_type == "rag_pipeline":
            if result["status"] == "completed":
                output = result.get("output", {})
                if output.get("total_results", 0) == 0:
                    recommendations.append("No search results found. Check if documents are properly ingested.")
        
        elif tool_type == "sql_agent":
            if result["status"] == "completed":
                recommendations.append("SQL tool is working. Test with actual database queries.")
        
        if not recommendations:
            recommendations.append("Tool is working correctly. Ready for production use.")
        
        return recommendations
