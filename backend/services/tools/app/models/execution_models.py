"""
Pydantic models for tool execution endpoints
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class ToolExecutionRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool execution parameters")
    user_permissions: Optional[List[str]] = Field(default=None, description="User permissions for execution")
    timeout: Optional[int] = Field(default=None, description="Execution timeout in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "tool_name": "calculator",
                "parameters": {"operation": "add", "a": 5, "b": 3},
                "user_permissions": ["read", "execute"],
                "timeout": 30
            }
        }

class BatchToolExecutionRequest(BaseModel):
    """Request model for batch tool execution"""
    tool_requests: List[Dict[str, Any]] = Field(..., description="List of tool execution requests")
    user_permissions: Optional[List[str]] = Field(default=None, description="User permissions for execution")
    max_concurrent: int = Field(default=5, description="Maximum concurrent executions")
    
    class Config:
        schema_extra = {
            "example": {
                "tool_requests": [
                    {"tool_name": "calculator", "parameters": {"operation": "add", "a": 1, "b": 2}},
                    {"tool_name": "calculator", "parameters": {"operation": "multiply", "a": 3, "b": 4}}
                ],
                "user_permissions": ["read", "execute"],
                "max_concurrent": 3
            }
        }

class MCPToolExecutionRequest(BaseModel):
    """Request model for MCP tool execution"""
    server_name: str = Field(..., description="MCP server name")
    tool_name: str = Field(..., description="Tool name on the MCP server")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool execution parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "server_name": "filesystem_server",
                "tool_name": "read_file",
                "parameters": {"path": "/path/to/file.txt"}
            }
        }

class ToolExecutionResponse(BaseModel):
    """Response model for tool execution"""
    success: bool = Field(..., description="Whether execution was successful")
    result: Optional[Any] = Field(default=None, description="Execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    tool_name: Optional[str] = Field(default=None, description="Name of the executed tool")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "result": {"answer": 8},
                "error": None,
                "execution_time": 0.123,
                "tool_name": "calculator"
            }
        }
