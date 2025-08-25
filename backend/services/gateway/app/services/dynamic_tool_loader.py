"""
Dynamic Tool Loader Service
Loads tools based on agent capabilities including templates, instances, and MCP integrations
"""

import logging
import json
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
import httpx
import asyncio

logger = logging.getLogger(__name__)

class DynamicToolLoader:
    """Loads tools dynamically based on agent capability configuration"""
    
    def __init__(self):
        self.tools_service_url = "http://tools:8005"
        self.mcp_service_url = "http://gateway:8000"
        
    async def load_tools_for_agent(self, capabilities: List[str]) -> List:
        """Load all tools specified in agent capabilities"""
        loaded_tools = []
        
        for capability in capabilities:
            try:
                if capability.startswith("template:"):
                    tool_name = capability[9:]  # Remove "template:" prefix
                    tool_obj = await self._load_tool_template(tool_name)
                    if tool_obj:
                        loaded_tools.append(tool_obj)
                        
                elif capability.startswith("instance:"):
                    tool_name = capability[9:]  # Remove "instance:" prefix
                    tool_obj = await self._load_tool_instance(tool_name)
                    if tool_obj:
                        loaded_tools.append(tool_obj)
                        
                elif capability.startswith("mcp:"):
                    tool_name = capability[4:]  # Remove "mcp:" prefix
                    tool_obj = await self._load_mcp_tool(tool_name)
                    if tool_obj:
                        loaded_tools.append(tool_obj)
                        
                elif capability.startswith("mcp-endpoint:"):
                    endpoint_name = capability[13:]  # Remove "mcp-endpoint:" prefix
                    tool_obj = await self._load_mcp_endpoint(endpoint_name)
                    if tool_obj:
                        loaded_tools.append(tool_obj)
                        
            except Exception as e:
                logger.error(f"Failed to load capability {capability}: {str(e)}")
                continue
                
        logger.info(f"Loaded {len(loaded_tools)} tools from {len(capabilities)} capabilities")
        return loaded_tools
    
    async def _load_tool_template(self, tool_name: str):
        """Load a tool from template definition"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.tools_service_url}/tool-templates/{tool_name}")
                if response.status_code == 200:
                    template_data = response.json()
                    return self._create_tool_from_template(template_data)
        except Exception as e:
            logger.error(f"Failed to load tool template {tool_name}: {str(e)}")
        return None
    
    async def _load_tool_instance(self, tool_name: str):
        """Load a configured tool instance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.tools_service_url}/tool-instances/{tool_name}")
                if response.status_code == 200:
                    instance_data = response.json()
                    return self._create_tool_from_instance(instance_data)
        except Exception as e:
            logger.error(f"Failed to load tool instance {tool_name}: {str(e)}")
        return None
    
    async def _load_mcp_tool(self, tool_name: str):
        """Load an MCP tool"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.mcp_service_url}/api/v1/mcp/tools")
                if response.status_code == 200:
                    tools_data = response.json()
                    for mcp_tool in tools_data:
                        if mcp_tool.get("tool_name") == tool_name:
                            return self._create_mcp_tool(mcp_tool)
        except Exception as e:
            logger.error(f"Failed to load MCP tool {tool_name}: {str(e)}")
        return None
    
    async def _load_mcp_endpoint(self, endpoint_name: str):
        """Load an MCP endpoint as a tool"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.mcp_service_url}/api/v1/mcp-gateway/endpoints/{endpoint_name}")
                if response.status_code == 200:
                    endpoint_data = response.json()
                    return self._create_mcp_endpoint_tool(endpoint_data)
        except Exception as e:
            logger.error(f"Failed to load MCP endpoint {endpoint_name}: {str(e)}")
        return None
    
    def _create_tool_from_template(self, template_data: Dict[str, Any]):
        """Create a LangChain tool from template definition"""
        tool_name = template_data.get("name", "unknown_tool")
        tool_description = template_data.get("description", "Tool from template")
        
        @tool
        def template_tool(input_data: str) -> str:
            f"""Execute {tool_name}: {tool_description}"""
            return f"Executed template tool {tool_name} with input: {input_data}"
        
        template_tool.name = tool_name
        template_tool.description = tool_description
        return template_tool
    
    def _create_tool_from_instance(self, instance_data: Dict[str, Any]):
        """Create a LangChain tool from tool instance"""
        tool_name = instance_data.get("name", "unknown_instance")
        tool_description = instance_data.get("description", "Tool instance")
        configuration = instance_data.get("configuration", {})
        
        @tool
        def instance_tool(input_data: str) -> str:
            f"""Execute {tool_name}: {tool_description}"""
            # In a real implementation, this would use the configuration
            # to connect to the actual tool service
            return f"Executed tool instance {tool_name} with config {configuration} and input: {input_data}"
        
        instance_tool.name = tool_name
        instance_tool.description = tool_description
        return instance_tool
    
    def _create_mcp_tool(self, mcp_tool_data: Dict[str, Any]):
        """Create a LangChain tool from MCP tool definition"""
        tool_name = mcp_tool_data.get("tool_name", "unknown_mcp_tool")
        tool_description = mcp_tool_data.get("description", "MCP tool")
        server_id = mcp_tool_data.get("server_id")
        
        @tool
        def mcp_tool(input_data: str) -> str:
            f"""Execute MCP tool {tool_name}: {tool_description}"""
            # In a real implementation, this would call the MCP server
            return f"Executed MCP tool {tool_name} from server {server_id} with input: {input_data}"
        
        mcp_tool.name = tool_name
        mcp_tool.description = tool_description
        return mcp_tool
    
    def _create_mcp_endpoint_tool(self, endpoint_data: Dict[str, Any]):
        """Create a LangChain tool from MCP endpoint"""
        endpoint_name = endpoint_data.get("endpoint_name", "unknown_endpoint")
        endpoint_description = endpoint_data.get("description", "MCP endpoint")
        endpoint_url = endpoint_data.get("endpoint_url")
        
        @tool
        def mcp_endpoint_tool(input_data: str) -> str:
            f"""Execute MCP endpoint {endpoint_name}: {endpoint_description}"""
            # In a real implementation, this would make HTTP calls to the endpoint
            return f"Executed MCP endpoint {endpoint_name} at {endpoint_url} with input: {input_data}"
        
        mcp_endpoint_tool.name = endpoint_name
        mcp_endpoint_tool.description = endpoint_description
        return mcp_endpoint_tool

# Singleton instance
_dynamic_tool_loader = None

def get_dynamic_tool_loader() -> DynamicToolLoader:
    """Get the dynamic tool loader singleton"""
    global _dynamic_tool_loader
    if _dynamic_tool_loader is None:
        _dynamic_tool_loader = DynamicToolLoader()
    return _dynamic_tool_loader