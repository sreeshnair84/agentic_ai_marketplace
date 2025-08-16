"""
A2A Protocol Remote Agent Connection
Based on https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/multiagent
"""

import asyncio
import httpx
import logging
from typing import Dict, Any, Optional, Callable, List
import json

from ..models.a2a_models import (
    A2AAgentCard, A2AMessage, A2ATask, A2ATaskRequest, 
    TaskState, JsonRpcRequest, JsonRpcSuccessResponse,
    MessageSendParams, Role, A2AMessagePart, A2APartType
)

logger = logging.getLogger(__name__)

# Type for task update callbacks
TaskUpdateCallback = Callable[[str, A2ATask], None]


class RemoteAgentConnection:
    """Manages connection to a remote A2A agent"""
    
    def __init__(
        self, 
        agent_card: A2AAgentCard,
        http_client: Optional[httpx.AsyncClient] = None,
        timeout: float = 30.0
    ):
        self.agent_card = agent_card
        self.http_client = http_client or httpx.AsyncClient()
        self.timeout = timeout
        self.base_url = agent_card.url
        self._own_client = http_client is None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_client:
            await self.http_client.aclose()
    
    async def send_message(
        self,
        message: A2AMessage,
        session_id: Optional[str] = None,
        context_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> A2ATask:
        """Send a message to the remote agent (synchronous)"""
        
        # Prepare JSON-RPC request
        params = MessageSendParams(
            id=task_id or message.message_id,
            session_id=session_id,
            context_id=context_id,
            accepted_output_modes=["text"],
            message=message
        )
        
        rpc_request = JsonRpcRequest(
            id=message.message_id,
            method="message/send",
            params=params.model_dump()
        )
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/a2a/message/send",
                json=rpc_request.model_dump(),
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            if "result" in response_data:
                # Parse the task result
                task_data = response_data["result"]
                return A2ATask(**task_data)
            else:
                # Handle error response
                error = response_data.get("error", {})
                raise Exception(f"Agent error: {error.get('message', 'Unknown error')}")
                
        except httpx.TimeoutException:
            logger.error(f"Timeout communicating with agent {self.agent_card.name}")
            raise Exception(f"Timeout communicating with agent {self.agent_card.name}")
        except httpx.RequestError as e:
            logger.error(f"Request error communicating with agent {self.agent_card.name}: {e}")
            raise Exception(f"Communication error with agent {self.agent_card.name}: {e}")
        except Exception as e:
            logger.error(f"Error communicating with agent {self.agent_card.name}: {e}")
            raise
    
    async def send_message_stream(
        self,
        message: A2AMessage,
        session_id: Optional[str] = None,
        context_id: Optional[str] = None,
        task_id: Optional[str] = None
    ):
        """Send a message to the remote agent (streaming)"""
        
        # Prepare JSON-RPC request
        params = MessageSendParams(
            id=task_id or message.message_id,
            session_id=session_id,
            context_id=context_id,
            accepted_output_modes=["text"],
            message=message
        )
        
        rpc_request = JsonRpcRequest(
            id=message.message_id,
            method="message/stream",
            params=params.model_dump()
        )
        
        try:
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/a2a/message/stream",
                json=rpc_request.model_dump(),
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            # Parse SSE data
                            if line.startswith("data: "):
                                data = line[6:]  # Remove "data: " prefix
                                if data.strip() == "[DONE]":
                                    break
                                
                                chunk_data = json.loads(data)
                                yield chunk_data
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in stream: {line}")
                            continue
                            
        except httpx.TimeoutException:
            logger.error(f"Timeout streaming from agent {self.agent_card.name}")
            raise Exception(f"Timeout streaming from agent {self.agent_card.name}")
        except httpx.RequestError as e:
            logger.error(f"Request error streaming from agent {self.agent_card.name}: {e}")
            raise Exception(f"Communication error with agent {self.agent_card.name}: {e}")
        except Exception as e:
            logger.error(f"Error streaming from agent {self.agent_card.name}: {e}")
            raise
    
    async def get_agent_card(self) -> A2AAgentCard:
        """Get the agent card from the remote agent"""
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/a2a/cards",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            card_data = response.json()
            return A2AAgentCard(**card_data)
            
        except httpx.RequestError as e:
            logger.error(f"Error getting agent card from {self.agent_card.name}: {e}")
            raise Exception(f"Failed to get agent card: {e}")
    
    async def health_check(self) -> bool:
        """Check if the remote agent is healthy"""
        
        try:
            response = await self.http_client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
            
        except Exception:
            return False


class RemoteAgentConnections:
    """Manages multiple remote agent connections"""
    
    def __init__(
        self,
        http_client: Optional[httpx.AsyncClient] = None,
        task_callback: Optional[TaskUpdateCallback] = None
    ):
        self.http_client = http_client or httpx.AsyncClient()
        self.task_callback = task_callback
        self.connections: Dict[str, RemoteAgentConnection] = {}
        self.agent_cards: Dict[str, A2AAgentCard] = {}
        self._own_client = http_client is None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_client:
            await self.http_client.aclose()
    
    async def add_agent(self, agent_url: str) -> A2AAgentCard:
        """Add a remote agent by discovering its card"""
        
        try:
            # Discover agent card
            response = await self.http_client.get(
                f"{agent_url}/a2a/cards",
                timeout=10.0
            )
            response.raise_for_status()
            
            card_data = response.json()
            # Handle both single card and list of cards
            if isinstance(card_data, list):
                if card_data:
                    card_data = card_data[0]  # Take first card
                else:
                    raise Exception("No agent cards found")
            
            agent_card = A2AAgentCard(**card_data)
            
            # Create connection
            connection = RemoteAgentConnection(
                agent_card=agent_card,
                http_client=self.http_client
            )
            
            self.connections[agent_card.name] = connection
            self.agent_cards[agent_card.name] = agent_card
            
            logger.info(f"Added remote agent: {agent_card.name} at {agent_url}")
            return agent_card
            
        except Exception as e:
            logger.error(f"Failed to add remote agent at {agent_url}: {e}")
            raise Exception(f"Failed to add remote agent: {e}")
    
    async def remove_agent(self, agent_name: str):
        """Remove a remote agent"""
        
        if agent_name in self.connections:
            del self.connections[agent_name]
            del self.agent_cards[agent_name]
            logger.info(f"Removed remote agent: {agent_name}")
    
    async def send_message_to_agent(
        self,
        agent_name: str,
        message: A2AMessage,
        session_id: Optional[str] = None,
        context_id: Optional[str] = None,
        task_id: Optional[str] = None
    ):
        """Send a message to a specific agent"""
        
        if agent_name not in self.connections:
            raise Exception(f"Agent {agent_name} not found")
        
        connection = self.connections[agent_name]
        
        task = await connection.send_message(
            message=message,
            session_id=session_id,
            context_id=context_id,
            task_id=task_id
        )
        
        # Trigger callback if provided
        if self.task_callback:
            self.task_callback(agent_name, task)
        
        return task
    
    async def send_message_to_agent_stream(
        self,
        agent_name: str,
        message: A2AMessage,
        session_id: Optional[str] = None,
        context_id: Optional[str] = None,
        task_id: Optional[str] = None
    ):
        """Send a streaming message to a specific agent"""
        
        if agent_name not in self.connections:
            raise Exception(f"Agent {agent_name} not found")
        
        connection = self.connections[agent_name]
        
        async for chunk in connection.send_message_stream(
            message=message,
            session_id=session_id,
            context_id=context_id,
            task_id=task_id
        ):
            yield chunk
    
    async def broadcast_message(
        self,
        message: A2AMessage,
        agent_names: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> Dict[str, A2ATask]:
        """Broadcast a message to multiple agents"""
        
        targets = agent_names or list(self.connections.keys())
        results = {}
        
        async def send_to_agent(agent_name: str):
            try:
                task = await self.send_message_to_agent(
                    agent_name=agent_name,
                    message=message,
                    session_id=session_id,
                    context_id=context_id
                )
                results[agent_name] = task
            except Exception as e:
                logger.error(f"Failed to send message to {agent_name}: {e}")
                # Create error task
                from ..models.a2a_models import A2ATaskStatus
                error_task = A2ATask(
                    id=f"error_{agent_name}",
                    status=A2ATaskStatus(state=TaskState.failed, error=str(e))
                )
                results[agent_name] = error_task
        
        # Send messages concurrently
        await asyncio.gather(*[send_to_agent(name) for name in targets])
        
        return results
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Health check all connected agents"""
        
        results = {}
        
        async def check_agent(agent_name: str, connection: RemoteAgentConnection):
            results[agent_name] = await connection.health_check()
        
        await asyncio.gather(*[
            check_agent(name, conn) 
            for name, conn in self.connections.items()
        ])
        
        return results
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all connected agents with their capabilities"""
        
        return [
            {
                "name": card.name,
                "description": card.description,
                "url": card.url,
                "capabilities": card.capabilities.model_dump(),
                "skills": [skill.model_dump() for skill in card.skills],
                "tags": card.tags
            }
            for card in self.agent_cards.values()
        ]
    
    def create_text_message(
        self, 
        text: str, 
        role: Role = Role.user,
        message_id: Optional[str] = None,
        context_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> A2AMessage:
        """Helper to create a text message"""
        
        return A2AMessage(
            role=role,
            parts=[A2AMessagePart(type=A2APartType.text, text=text)],
            message_id=message_id,
            context_id=context_id,
            task_id=task_id
        )
