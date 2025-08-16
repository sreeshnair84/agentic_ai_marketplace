"""
Agent service for orchestrator - communicates with agents service
"""

import httpx
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class AgentService:
    """Service for communicating with the Agents service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.AGENTS_SERVICE_URL
        self.timeout = 30.0
    
    async def execute_task(
        self,
        agent_id: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a task using a specific agent"""
        
        payload = {
            "agent_id": agent_id,
            "task_data": task_data,
            "context": context or {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/execution/execute",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Timeout executing task with agent {agent_id}")
            raise Exception("Agent execution timeout")
        except httpx.RequestError as e:
            logger.error(f"Error executing task with agent {agent_id}: {e}")
            raise Exception(f"Agent communication error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing task with agent {agent_id}: {e}")
            raise
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool via the tools service"""
        
        payload = {
            "tool_name": tool_name,
            "parameters": parameters,
            "context": context or {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use tools service URL
                tools_url = self.settings.TOOLS_SERVICE_URL
                response = await client.post(
                    f"{tools_url}/api/v1/tools/execute",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Timeout executing tool {tool_name}")
            raise Exception("Tool execution timeout")
        except httpx.RequestError as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise Exception(f"Tool communication error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing tool {tool_name}: {e}")
            raise
    
    async def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities of a specific agent"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/registry/agents/{agent_id}"
                )
                response.raise_for_status()
                agent_data = response.json()
                return agent_data.get("capabilities", [])
                
        except httpx.RequestError as e:
            logger.error(f"Error getting agent capabilities for {agent_id}: {e}")
            return []
    
    async def list_available_agents(
        self, 
        agent_type: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List available agents"""
        
        params = {}
        if agent_type:
            params["agent_type"] = agent_type
        if capabilities:
            params["capabilities"] = ",".join(capabilities)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/registry/agents",
                    params=params
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Error listing agents: {e}")
            return []
    
    async def send_a2a_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send A2A (Agent-to-Agent) message"""
        
        message_payload = {
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "message_type": message_type,
            "payload": payload,
            "correlation_id": correlation_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/a2a/send",
                    json=message_payload
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Error sending A2A message: {e}")
            raise Exception(f"A2A communication error: {e}")


class TaskQueue:
    """Simple task queue implementation using Redis"""
    
    def __init__(self):
        self.settings = get_settings()
        # Note: This is a simplified implementation
        # In production, use Celery, RQ, or similar
    
    async def enqueue_task(self, task_data: Dict[str, Any]) -> str:
        """Enqueue a task for processing"""
        
        # Simplified implementation
        # In production, integrate with Redis/Celery
        task_id = f"task_{datetime.utcnow().timestamp()}"
        logger.info(f"Enqueued task {task_id}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> str:
        """Get task status"""
        
        # Simplified implementation
        return "completed"
