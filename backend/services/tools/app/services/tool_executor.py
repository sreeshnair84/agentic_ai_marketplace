"""
Tool execution engine
"""

import asyncio
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import traceback
import json

from .tool_registry import get_tool_registry, ToolDefinition
from .mcp_client import MCPClient
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class ToolExecutionResult:
    """Result of tool execution"""
    
    def __init__(
        self,
        tool_name: str,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
        timestamp: Optional[str] = None
    ):
        self.tool_name = tool_name
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.timestamp = timestamp or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }


class ToolExecutor:
    """Executor for running tools"""
    
    def __init__(self):
        self.registry = get_tool_registry()
        self.mcp_client = MCPClient()
        self.settings = get_settings()
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_permissions: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> ToolExecutionResult:
        """Execute a tool with given parameters"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get tool definition
            tool = self.registry.get_tool(tool_name)
            if not tool:
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    error=f"Tool '{tool_name}' not found"
                )
            
            # Check permissions
            if user_permissions is not None:
                if not self.registry.validate_permissions(tool_name, user_permissions):
                    return ToolExecutionResult(
                        tool_name=tool_name,
                        success=False,
                        error=f"Insufficient permissions for tool '{tool_name}'"
                    )
            
            # Validate parameters
            validation_error = self._validate_parameters(tool, parameters)
            if validation_error:
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    error=validation_error
                )
            
            # Set timeout
            execution_timeout = timeout or tool.timeout or self.settings.MAX_EXECUTION_TIME
            
            # Execute tool
            if tool.is_async:
                result = await asyncio.wait_for(
                    tool.function(**parameters),
                    timeout=execution_timeout
                )
            else:
                # Run sync function in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: tool.function(**parameters)
                )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool execution timed out after {execution_timeout} seconds",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Error executing tool '{tool_name}': {e}")
            logger.error(traceback.format_exc())
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def execute_mcp_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        server_name: Optional[str] = None
    ) -> ToolExecutionResult:
        """Execute an MCP tool"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Default to first available server if none specified
            if server_name is None:
                servers = await self.mcp_client.list_servers()
                if servers:
                    server_name = next(iter(servers.keys()))
                else:
                    return ToolExecutionResult(
                        tool_name=tool_name,
                        success=False,
                        error="No MCP servers available"
                    )
            
            result = await self.mcp_client.execute_tool(
                server_name=server_name,
                tool_name=tool_name,
                parameters=parameters
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=result.success,
                result=result.result,
                error=result.error,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Error executing MCP tool '{tool_name}': {e}")
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def batch_execute(
        self,
        tool_requests: List[Dict[str, Any]],
        user_permissions: Optional[List[str]] = None,
        max_concurrent: int = 5
    ) -> List[ToolExecutionResult]:
        """Execute multiple tools concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single(request: Dict[str, Any]) -> ToolExecutionResult:
            async with semaphore:
                tool_name = request.get("tool_name")
                if not tool_name:
                    return ToolExecutionResult(
                        tool_name="unknown",
                        success=False,
                        error="tool_name is required"
                    )
                
                parameters = request.get("parameters", {})
                timeout = request.get("timeout")
                
                if request.get("is_mcp", False):
                    return await self.execute_mcp_tool(
                        tool_name=tool_name,
                        parameters=parameters,
                        server_name=request.get("server_name")
                    )
                else:
                    return await self.execute_tool(
                        tool_name=tool_name,
                        parameters=parameters,
                        user_permissions=user_permissions,
                        timeout=timeout
                    )
        
        tasks = [execute_single(request) for request in tool_requests]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def _validate_parameters(self, tool: ToolDefinition, parameters: Dict[str, Any]) -> Optional[str]:
        """Validate tool parameters"""
        
        try:
            # Check required parameters
            for param_name, param_def in tool.parameters.items():
                if param_def.get("required", False) and param_name not in parameters:
                    return f"Missing required parameter: {param_name}"
            
            # Type validation (basic)
            for param_name, value in parameters.items():
                if param_name in tool.parameters:
                    param_def = tool.parameters[param_name]
                    expected_type = param_def.get("type")
                    
                    if expected_type == "string" and not isinstance(value, str):
                        return f"Parameter '{param_name}' must be a string"
                    elif expected_type == "integer" and not isinstance(value, int):
                        return f"Parameter '{param_name}' must be an integer"
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        return f"Parameter '{param_name}' must be a boolean"
                    elif expected_type == "array" and not isinstance(value, list):
                        return f"Parameter '{param_name}' must be an array"
                    elif expected_type == "object" and not isinstance(value, dict):
                        return f"Parameter '{param_name}' must be an object"
            
            return None
            
        except Exception as e:
            return f"Parameter validation error: {str(e)}"
    
    def get_available_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        
        tools = self.registry.list_tools(category)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "parameters": tool.parameters,
                "required_permissions": tool.required_permissions
            }
            for tool in tools
        ]
    
    async def get_mcp_tools(self, server_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available MCP tools"""
        
        try:
            mcp_tools = await self.mcp_client.discover_tools(server_name)
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                    "server_name": tool.server_name,
                    "server_url": tool.server_url
                }
                for tool in mcp_tools
            ]
        except Exception as e:
            logger.error(f"Error getting MCP tools: {e}")
            return []
