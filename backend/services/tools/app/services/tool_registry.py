"""
Tool registry system for managing available tools
"""

from typing import Dict, Any, List, Optional, Callable, Type
from datetime import datetime
import logging
import inspect
from dataclasses import dataclass, field

from ..services.standard_tools import WebTools, FileTools, DataTools, SystemTools

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of a tool"""
    name: str
    description: str
    category: str
    function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    is_async: bool = True
    timeout: Optional[int] = None


class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self._initialize_standard_tools()
    
    def _initialize_standard_tools(self):
        """Initialize standard tools"""
        
        # Web tools
        self.register_tool(
            "web_fetch",
            "Fetch content from a URL",
            "web",
            WebTools.fetch_url,
            {
                "url": {"type": "string", "required": True, "description": "URL to fetch"},
                "headers": {"type": "object", "required": False, "description": "HTTP headers"}
            }
        )
        
        self.register_tool(
            "web_scrape",
            "Scrape content from a webpage",
            "web",
            WebTools.scrape_webpage,
            {
                "url": {"type": "string", "required": True, "description": "URL to scrape"},
                "selector": {"type": "string", "required": False, "description": "CSS selector for content"}
            }
        )
        
        self.register_tool(
            "web_search",
            "Perform web search",
            "web",
            WebTools.web_search,
            {
                "query": {"type": "string", "required": True, "description": "Search query"},
                "num_results": {"type": "integer", "required": False, "description": "Number of results", "default": 10}
            }
        )
        
        # File tools
        self.register_tool(
            "file_read",
            "Read content from a file",
            "file",
            FileTools.read_file,
            {
                "file_path": {"type": "string", "required": True, "description": "Path to file"},
                "encoding": {"type": "string", "required": False, "description": "File encoding", "default": "utf-8"}
            },
            required_permissions=["file_read"]
        )
        
        self.register_tool(
            "file_write",
            "Write content to a file",
            "file",
            FileTools.write_file,
            {
                "file_path": {"type": "string", "required": True, "description": "Path to file"},
                "content": {"type": "string", "required": True, "description": "Content to write"},
                "encoding": {"type": "string", "required": False, "description": "File encoding", "default": "utf-8"},
                "create_dirs": {"type": "boolean", "required": False, "description": "Create directories", "default": True}
            },
            required_permissions=["file_write"]
        )
        
        self.register_tool(
            "directory_list",
            "List contents of a directory",
            "file",
            FileTools.list_directory,
            {
                "directory_path": {"type": "string", "required": True, "description": "Path to directory"}
            },
            required_permissions=["file_read"]
        )
        
        # Data tools
        self.register_tool(
            "csv_to_json",
            "Convert CSV content to JSON",
            "data",
            DataTools.csv_to_json,
            {
                "csv_content": {"type": "string", "required": True, "description": "CSV content to convert"}
            }
        )
        
        self.register_tool(
            "json_to_csv",
            "Convert JSON data to CSV",
            "data",
            DataTools.json_to_csv,
            {
                "json_data": {"type": "array", "required": True, "description": "JSON data to convert"}
            }
        )
        
        self.register_tool(
            "data_summary",
            "Generate summary statistics for data",
            "data",
            DataTools.data_summary,
            {
                "data": {"type": "array", "required": True, "description": "Data to summarize"}
            }
        )
        
        # System tools (restricted)
        self.register_tool(
            "system_execute",
            "Execute system command (restricted)",
            "system",
            SystemTools.execute_command,
            {
                "command": {"type": "string", "required": True, "description": "Command to execute"},
                "timeout": {"type": "integer", "required": False, "description": "Timeout in seconds", "default": 30},
                "allowed_commands": {"type": "array", "required": False, "description": "List of allowed commands"}
            },
            required_permissions=["system_execute"],
            timeout=30
        )
    
    def register_tool(
        self,
        name: str,
        description: str,
        category: str,
        function: Callable,
        parameters: Optional[Dict[str, Any]] = None,
        required_permissions: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> None:
        """Register a new tool"""
        
        is_async = inspect.iscoroutinefunction(function)
        
        tool_def = ToolDefinition(
            name=name,
            description=description,
            category=category,
            function=function,
            parameters=parameters or {},
            required_permissions=required_permissions or [],
            is_async=is_async,
            timeout=timeout
        )
        
        self.tools[name] = tool_def
        logger.info(f"Registered tool: {name} ({category})")
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """List all tools or tools in a specific category"""
        
        if category:
            return [tool for tool in self.tools.values() if tool.category == category]
        return list(self.tools.values())
    
    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool schema for validation"""
        
        tool = self.get_tool(name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "parameters": tool.parameters,
            "required_permissions": tool.required_permissions,
            "is_async": tool.is_async,
            "timeout": tool.timeout
        }
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(set(tool.category for tool in self.tools.values()))
    
    def validate_permissions(self, tool_name: str, user_permissions: List[str]) -> bool:
        """Check if user has required permissions for tool"""
        
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        
        return all(perm in user_permissions for perm in tool.required_permissions)


# Global tool registry instance
tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return tool_registry
