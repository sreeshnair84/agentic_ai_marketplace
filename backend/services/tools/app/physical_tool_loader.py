"""
Physical Tool Loader
Loads tool implementations from physical files instead of string configurations
"""

import os
import importlib.util
import inspect
import logging
from typing import Dict, Any, List, Optional, Type
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class PhysicalToolLoader:
    """
    Loads and manages tool implementations from physical files
    """
    
    def __init__(self, tools_directory: str):
        """
        Initialize the physical tool loader
        
        Args:
            tools_directory: Path to the tool implementations directory
        """
        self.tools_directory = Path(tools_directory)
        self.loaded_tools = {}
        self.tool_configs = {}
        
        logger.info(f"Initialized PhysicalToolLoader with directory: {tools_directory}")
    
    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover all available tools in the tools directory
        
        Returns:
            List of discovered tool information
        """
        discovered_tools = []
        
        try:
            # Iterate through tool category directories
            for tool_category_dir in self.tools_directory.iterdir():
                if tool_category_dir.is_dir() and not tool_category_dir.name.startswith('.'):
                    category_tools = self._discover_tools_in_category(tool_category_dir)
                    discovered_tools.extend(category_tools)
            
            logger.info(f"Discovered {len(discovered_tools)} tools")
            return discovered_tools
            
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
            return []
    
    def _discover_tools_in_category(self, category_dir: Path) -> List[Dict[str, Any]]:
        """
        Discover tools in a specific category directory
        
        Args:
            category_dir: Path to the category directory
            
        Returns:
            List of tools in the category
        """
        category_tools = []
        category_name = category_dir.name
        
        try:
            # Look for Python files in the category directory
            for python_file in category_dir.glob("*.py"):
                if python_file.name.startswith('__'):
                    continue
                
                tool_info = self._analyze_tool_file(python_file, category_name)
                if tool_info:
                    category_tools.append(tool_info)
            
            return category_tools
            
        except Exception as e:
            logger.error(f"Error discovering tools in category {category_name}: {e}")
            return []
    
    def _analyze_tool_file(self, tool_file: Path, category: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a tool file to extract tool information
        
        Args:
            tool_file: Path to the tool file
            category: Tool category
            
        Returns:
            Tool information dictionary or None
        """
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(
                f"{category}.{tool_file.stem}", 
                tool_file
            )
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the main tool class
            tool_class = self._find_tool_class(module)
            if not tool_class:
                return None
            
            # Extract schemas
            config_schema = getattr(module, 'TOOL_CONFIG_SCHEMA', {})
            input_schema = getattr(module, 'INPUT_SCHEMA', {})
            output_schema = getattr(module, 'OUTPUT_SCHEMA', {})
            
            # Extract tool metadata
            tool_name = tool_file.stem
            tool_info = {
                "name": tool_name,
                "category": category,
                "file_path": str(tool_file),
                "class_name": tool_class.__name__,
                "description": self._extract_description(tool_class),
                "config_schema": config_schema,
                "input_schema": input_schema,
                "output_schema": output_schema,
                "methods": self._extract_public_methods(tool_class),
                "version": "1.0.0",  # Could be extracted from docstring or metadata
                "module": module
            }
            
            return tool_info
            
        except Exception as e:
            logger.error(f"Error analyzing tool file {tool_file}: {e}")
            return None
    
    def _find_tool_class(self, module) -> Optional[Type]:
        """
        Find the main tool class in a module
        
        Args:
            module: Imported module
            
        Returns:
            Tool class or None
        """
        # Look for classes that might be the main tool class
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                # Check if it's likely a tool class
                if (name.endswith('Tool') or 
                    name.endswith('Agent') or 
                    name.endswith('Scraper') or 
                    name.endswith('Integration') or
                    hasattr(obj, 'initialize') or
                    hasattr(obj, 'execute')):
                    return obj
        
        return None
    
    def _extract_description(self, tool_class: Type) -> str:
        """
        Extract description from tool class docstring
        
        Args:
            tool_class: Tool class
            
        Returns:
            Tool description
        """
        docstring = inspect.getdoc(tool_class)
        if docstring:
            # Get first line or paragraph as description
            lines = docstring.strip().split('\n')
            return lines[0].strip()
        
        return f"{tool_class.__name__} tool"
    
    def _extract_public_methods(self, tool_class: Type) -> List[str]:
        """
        Extract public methods from tool class
        
        Args:
            tool_class: Tool class
            
        Returns:
            List of public method names
        """
        methods = []
        for name, method in inspect.getmembers(tool_class, inspect.isfunction):
            if not name.startswith('_') and hasattr(method, '__self__') is False:
                methods.append(name)
        
        # Also check for async methods
        for name, method in inspect.getmembers(tool_class, inspect.iscoroutinefunction):
            if not name.startswith('_'):
                methods.append(name)
        
        return methods
    
    def load_tool(self, tool_name: str, config: Dict[str, Any]) -> Any:
        """
        Load and instantiate a tool
        
        Args:
            tool_name: Name of the tool to load
            config: Tool configuration
            
        Returns:
            Tool instance
        """
        try:
            # Find tool info
            discovered_tools = self.discover_tools()
            tool_info = None
            
            for tool in discovered_tools:
                if tool["name"] == tool_name:
                    tool_info = tool
                    break
            
            if not tool_info:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Load the module if not already loaded
            if tool_name not in self.loaded_tools:
                spec = importlib.util.spec_from_file_location(
                    f"{tool_info['category']}.{tool_name}", 
                    tool_info["file_path"]
                )
                if not spec or not spec.loader:
                    raise ImportError(f"Could not load tool module: {tool_info['file_path']}")
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                tool_class = self._find_tool_class(module)
                if not tool_class:
                    raise ValueError(f"No tool class found in {tool_info['file_path']}")
                
                self.loaded_tools[tool_name] = tool_class
            
            # Instantiate the tool
            tool_class = self.loaded_tools[tool_name]
            tool_instance = tool_class(config)
            
            logger.info(f"Successfully loaded tool: {tool_name}")
            return tool_instance
            
        except Exception as e:
            logger.error(f"Error loading tool {tool_name}: {e}")
            raise
    
    def get_tool_config_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Get configuration schema for a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Configuration schema
        """
        try:
            discovered_tools = self.discover_tools()
            
            for tool in discovered_tools:
                if tool["name"] == tool_name:
                    return tool.get("config_schema", {})
            
            raise ValueError(f"Tool '{tool_name}' not found")
            
        except Exception as e:
            logger.error(f"Error getting config schema for {tool_name}: {e}")
            return {}
    
    def get_tool_schemas(self, tool_name: str) -> Dict[str, Any]:
        """
        Get all schemas for a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with config, input, and output schemas
        """
        try:
            discovered_tools = self.discover_tools()
            
            for tool in discovered_tools:
                if tool["name"] == tool_name:
                    return {
                        "config_schema": tool.get("config_schema", {}),
                        "input_schema": tool.get("input_schema", {}),
                        "output_schema": tool.get("output_schema", {})
                    }
            
            raise ValueError(f"Tool '{tool_name}' not found")
            
        except Exception as e:
            logger.error(f"Error getting schemas for {tool_name}: {e}")
            return {}
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools with their metadata
        
        Returns:
            List of tool metadata
        """
        try:
            discovered_tools = self.discover_tools()
            
            # Return simplified tool list
            tool_list = []
            for tool in discovered_tools:
                tool_list.append({
                    "name": tool["name"],
                    "category": tool["category"],
                    "description": tool["description"],
                    "version": tool["version"],
                    "methods": tool["methods"]
                })
            
            return tool_list
            
        except Exception as e:
            logger.error(f"Error listing available tools: {e}")
            return []
    
    def validate_tool_config(self, tool_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool configuration against schema
        
        Args:
            tool_name: Name of the tool
            config: Configuration to validate
            
        Returns:
            Validation result
        """
        try:
            from jsonschema import validate, ValidationError
            
            config_schema = self.get_tool_config_schema(tool_name)
            
            if not config_schema:
                return {"valid": True, "message": "No schema available for validation"}
            
            validate(instance=config, schema=config_schema)
            
            return {"valid": True, "message": "Configuration is valid"}
            
        except ValidationError as e:
            return {
                "valid": False, 
                "message": f"Configuration validation failed: {e.message}",
                "path": list(e.path) if e.path else []
            }
        except Exception as e:
            logger.error(f"Error validating config for {tool_name}: {e}")
            return {
                "valid": False,
                "message": f"Validation error: {str(e)}"
            }
    
    def create_tool_registry(self) -> Dict[str, Any]:
        """
        Create a tool registry with all discovered tools
        
        Returns:
            Tool registry dictionary
        """
        try:
            discovered_tools = self.discover_tools()
            
            registry = {
                "tools": {},
                "categories": {},
                "total_tools": len(discovered_tools),
                "generated_at": str(Path(__file__).parent / "tool_registry.json")
            }
            
            # Organize tools by category
            for tool in discovered_tools:
                category = tool["category"]
                
                if category not in registry["categories"]:
                    registry["categories"][category] = []
                
                registry["categories"][category].append(tool["name"])
                registry["tools"][tool["name"]] = {
                    "category": category,
                    "description": tool["description"],
                    "file_path": tool["file_path"],
                    "class_name": tool["class_name"],
                    "config_schema": tool["config_schema"],
                    "input_schema": tool["input_schema"],
                    "output_schema": tool["output_schema"],
                    "methods": tool["methods"],
                    "version": tool["version"]
                }
            
            return registry
            
        except Exception as e:
            logger.error(f"Error creating tool registry: {e}")
            return {"tools": {}, "categories": {}, "total_tools": 0}
    
    def save_tool_registry(self, output_path: str = None) -> str:
        """
        Save tool registry to JSON file
        
        Args:
            output_path: Path to save the registry file
            
        Returns:
            Path to the saved registry file
        """
        try:
            if not output_path:
                output_path = str(self.tools_directory.parent / "tool_registry.json")
            
            registry = self.create_tool_registry()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Tool registry saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving tool registry: {e}")
            raise

# Tool management integration
class PhysicalToolManager:
    """
    Enhanced tool manager that works with physical tool implementations
    """
    
    def __init__(self, tools_directory: str):
        self.tool_loader = PhysicalToolLoader(tools_directory)
        self.active_tools = {}
    
    async def initialize_tool(self, tool_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize a tool with the given configuration
        
        Args:
            tool_name: Name of the tool to initialize
            config: Tool configuration
            
        Returns:
            Initialization result
        """
        try:
            # Validate configuration
            validation_result = self.tool_loader.validate_tool_config(tool_name, config)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "error": f"Configuration validation failed: {validation_result['message']}"
                }
            
            # Load and initialize tool
            tool_instance = self.tool_loader.load_tool(tool_name, config)
            
            # Initialize if the tool has an initialize method
            if hasattr(tool_instance, 'initialize'):
                await tool_instance.initialize()
            
            # Store active tool
            self.active_tools[tool_name] = tool_instance
            
            return {
                "status": "success",
                "message": f"Tool '{tool_name}' initialized successfully",
                "tool_name": tool_name
            }
            
        except Exception as e:
            logger.error(f"Error initializing tool {tool_name}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_name": tool_name
            }
    
    async def execute_tool(self, tool_name: str, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool operation
        
        Args:
            tool_name: Name of the tool
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Execution result
        """
        try:
            if tool_name not in self.active_tools:
                return {
                    "status": "error",
                    "error": f"Tool '{tool_name}' is not initialized"
                }
            
            tool_instance = self.active_tools[tool_name]
            
            # Check if the operation exists
            if not hasattr(tool_instance, operation):
                return {
                    "status": "error",
                    "error": f"Operation '{operation}' not found in tool '{tool_name}'"
                }
            
            # Execute the operation
            operation_method = getattr(tool_instance, operation)
            
            if inspect.iscoroutinefunction(operation_method):
                result = await operation_method(**kwargs)
            else:
                result = operation_method(**kwargs)
            
            return {
                "status": "success",
                "tool_name": tool_name,
                "operation": operation,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}.{operation}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_name": tool_name,
                "operation": operation
            }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return self.tool_loader.list_available_tools()
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed information about a tool"""
        try:
            discovered_tools = self.tool_loader.discover_tools()
            
            for tool in discovered_tools:
                if tool["name"] == tool_name:
                    return tool
            
            return {"error": f"Tool '{tool_name}' not found"}
            
        except Exception as e:
            logger.error(f"Error getting tool info for {tool_name}: {e}")
            return {"error": str(e)}
    
    async def cleanup_tool(self, tool_name: str) -> Dict[str, Any]:
        """
        Cleanup a tool instance
        
        Args:
            tool_name: Name of the tool to cleanup
            
        Returns:
            Cleanup result
        """
        try:
            if tool_name in self.active_tools:
                tool_instance = self.active_tools[tool_name]
                
                # Call cleanup if available
                if hasattr(tool_instance, 'cleanup'):
                    await tool_instance.cleanup()
                
                # Remove from active tools
                del self.active_tools[tool_name]
                
                return {
                    "status": "success",
                    "message": f"Tool '{tool_name}' cleaned up successfully"
                }
            else:
                return {
                    "status": "warning",
                    "message": f"Tool '{tool_name}' was not active"
                }
                
        except Exception as e:
            logger.error(f"Error cleaning up tool {tool_name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
