"""
Physical Tools API Router
Provides endpoints for managing physical tool implementations
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
import logging

from ..physical_tool_loader import PhysicalToolManager
import os

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Physical Tools"])

# Initialize Physical Tool Manager
TOOLS_IMPLEMENTATION_DIR = os.path.join(os.path.dirname(__file__), "../tool_implementations")
physical_tool_manager = PhysicalToolManager(TOOLS_IMPLEMENTATION_DIR)

# ============================================================================
# PHYSICAL TOOL DISCOVERY ENDPOINTS
# ============================================================================

@router.get("/physical-tools/discover", response_model=List[Dict[str, Any]])
async def discover_physical_tools():
    """
    Discover all available physical tool implementations
    """
    try:
        tools = physical_tool_manager.list_tools()
        return tools
    except Exception as e:
        logger.error(f"Error discovering physical tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/physical-tools/{tool_name}/info", response_model=Dict[str, Any])
async def get_physical_tool_info(tool_name: str):
    """
    Get detailed information about a specific physical tool
    """
    try:
        tool_info = physical_tool_manager.get_tool_info(tool_name)
        
        if "error" in tool_info:
            raise HTTPException(status_code=404, detail=tool_info["error"])
        
        return tool_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool info for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/physical-tools/{tool_name}/schemas", response_model=Dict[str, Any])
async def get_physical_tool_schemas(tool_name: str):
    """
    Get configuration, input, and output schemas for a physical tool
    """
    try:
        schemas = physical_tool_manager.tool_loader.get_tool_schemas(tool_name)
        return schemas
    except Exception as e:
        logger.error(f"Error getting schemas for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PHYSICAL TOOL INSTANCE MANAGEMENT
# ============================================================================

@router.post("/physical-tools/{tool_name}/initialize", response_model=Dict[str, Any])
async def initialize_physical_tool(tool_name: str, config: Dict[str, Any]):
    """
    Initialize a physical tool with configuration
    """
    try:
        result = await physical_tool_manager.initialize_tool(tool_name, config)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/physical-tools/{tool_name}/execute/{operation}", response_model=Dict[str, Any])
async def execute_physical_tool_operation(
    tool_name: str, 
    operation: str, 
    parameters: Optional[Dict[str, Any]] = None
):
    """
    Execute an operation on a physical tool
    """
    try:
        if parameters is None:
            parameters = {}
        
        result = await physical_tool_manager.execute_tool(tool_name, operation, **parameters)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing {tool_name}.{operation}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/physical-tools/{tool_name}/cleanup", response_model=Dict[str, Any])
async def cleanup_physical_tool(tool_name: str):
    """
    Cleanup a physical tool instance
    """
    try:
        result = await physical_tool_manager.cleanup_tool(tool_name)
        return result
    except Exception as e:
        logger.error(f"Error cleaning up tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PHYSICAL TOOL VALIDATION
# ============================================================================

@router.post("/physical-tools/{tool_name}/validate-config", response_model=Dict[str, Any])
async def validate_physical_tool_config(tool_name: str, config: Dict[str, Any]):
    """
    Validate configuration for a physical tool
    """
    try:
        validation_result = physical_tool_manager.tool_loader.validate_tool_config(tool_name, config)
        return validation_result
    except Exception as e:
        logger.error(f"Error validating config for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOOL REGISTRY MANAGEMENT
# ============================================================================

@router.get("/physical-tools/registry/create", response_model=Dict[str, Any])
async def create_tool_registry():
    """
    Create a comprehensive tool registry from discovered tools
    """
    try:
        registry = physical_tool_manager.tool_loader.create_tool_registry()
        return registry
    except Exception as e:
        logger.error(f"Error creating tool registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/physical-tools/registry/save", response_model=Dict[str, str])
async def save_tool_registry(output_path: Optional[str] = None):
    """
    Save tool registry to a JSON file
    """
    try:
        if output_path is None:
            output_path = ""
        saved_path = physical_tool_manager.tool_loader.save_tool_registry(output_path)
        return {"registry_path": saved_path}
    except Exception as e:
        logger.error(f"Error saving tool registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOOL TESTING AND EXAMPLES
# ============================================================================

@router.post("/physical-tools/{tool_name}/test", response_model=Dict[str, Any])
async def test_physical_tool(tool_name: str, test_config: Dict[str, Any]):
    """
    Test a physical tool with sample configuration and operations
    """
    try:
        # Initialize tool with test config
        init_result = await physical_tool_manager.initialize_tool(tool_name, test_config)
        
        if init_result["status"] == "error":
            return {
                "status": "error",
                "phase": "initialization",
                "error": init_result["error"]
            }
        
        # Get tool info to find available operations
        tool_info = physical_tool_manager.get_tool_info(tool_name)
        methods = tool_info.get("methods", [])
        
        test_results = {
            "status": "success",
            "tool_name": tool_name,
            "initialization": init_result,
            "available_methods": methods,
            "test_operations": []
        }
        
        # Test basic operations if available
        test_operations = ["initialize"] if "initialize" in methods else []
        
        for operation in test_operations:
            try:
                op_result = await physical_tool_manager.execute_tool(tool_name, operation)
                test_results["test_operations"].append({
                    "operation": operation,
                    "status": op_result["status"],
                    "result": op_result.get("result", "No result")
                })
            except Exception as op_error:
                test_results["test_operations"].append({
                    "operation": operation,
                    "status": "error",
                    "error": str(op_error)
                })
        
        # Cleanup
        cleanup_result = await physical_tool_manager.cleanup_tool(tool_name)
        test_results["cleanup"] = cleanup_result
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# EXAMPLE CONFIGURATIONS
# ============================================================================

@router.get("/physical-tools/{tool_name}/example-config", response_model=Dict[str, Any])
async def get_example_config(tool_name: str):
    """
    Get example configuration for a physical tool
    """
    try:
        # Get the tool's config schema
        schemas = physical_tool_manager.tool_loader.get_tool_schemas(tool_name)
        config_schema = schemas.get("config_schema", {})
        
        if not config_schema:
            return {"error": "No configuration schema available"}
        
        # Generate example config based on schema
        example_config = _generate_example_config(config_schema)
        
        return {
            "tool_name": tool_name,
            "example_config": example_config,
            "schema": config_schema
        }
        
    except Exception as e:
        logger.error(f"Error getting example config for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_example_config(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate example configuration from JSON schema
    """
    example = {}
    properties = schema.get("properties", {})
    
    for field_name, field_schema in properties.items():
        field_type = field_schema.get("type", "string")
        default_value = field_schema.get("default")
        
        if default_value is not None:
            example[field_name] = default_value
        elif field_type == "string":
            if "enum" in field_schema:
                example[field_name] = field_schema["enum"][0]
            else:
                example[field_name] = f"example_{field_name}"
        elif field_type == "integer":
            example[field_name] = field_schema.get("minimum", 1)
        elif field_type == "number":
            example[field_name] = field_schema.get("minimum", 1.0)
        elif field_type == "boolean":
            example[field_name] = True
        elif field_type == "array":
            example[field_name] = []
        elif field_type == "object":
            example[field_name] = {}
    
    return example

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/physical-tools/health", response_model=Dict[str, Any])
async def check_physical_tools_health():
    """
    Check the health of the physical tools system
    """
    try:
        discovered_tools = physical_tool_manager.list_tools()
        
        health_info = {
            "status": "healthy",
            "tools_directory": TOOLS_IMPLEMENTATION_DIR,
            "discovered_tools_count": len(discovered_tools),
            "active_tools_count": len(physical_tool_manager.active_tools),
            "active_tools": list(physical_tool_manager.active_tools.keys()),
            "available_categories": list(set(tool["category"] for tool in discovered_tools))
        }
        
        return health_info
        
    except Exception as e:
        logger.error(f"Error checking physical tools health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "tools_directory": TOOLS_IMPLEMENTATION_DIR
        }
