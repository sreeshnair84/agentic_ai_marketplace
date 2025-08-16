"""
A2A Protocol handler for agent communication
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import httpx
import uuid

from ..models.a2a_models import (
    A2AAgentCard, 
    A2AMessage, 
    A2ATaskRequest, 
    A2ATaskResponse,
    create_a2a_message,
    create_text_part
)
from ..services.gemini_service import GeminiService
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class A2AProtocolHandler:
    """
    A2A Protocol handler implementing the Agent-to-Agent communication standard
    Based on https://github.com/a2aproject/a2a-samples
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.gemini_service = GeminiService()
        self.agent_cards: Dict[str, A2AAgentCard] = {}
    
    async def register_agent_card(self, agent_card: A2AAgentCard) -> None:
        """Register an agent card for A2A discovery"""
        
        self.agent_cards[agent_card.name] = agent_card
        logger.info(f"Registered A2A agent card: {agent_card.name}")
    
    async def get_agent_card(self, agent_name: str) -> Optional[A2AAgentCard]:
        """Get agent card by name"""
        return self.agent_cards.get(agent_name)
    
    async def list_agent_cards(self, tags: Optional[List[str]] = None) -> List[A2AAgentCard]:
        """List available agent cards, optionally filtered by tags"""
        
        cards = list(self.agent_cards.values())
        
        if tags:
            filtered_cards = []
            for card in cards:
                if any(tag in card.tags for tag in tags):
                    filtered_cards.append(card)
            return filtered_cards
        
        return cards
    
    async def handle_message_send(
        self,
        request: A2ATaskRequest,
        agent_card: A2AAgentCard
    ) -> A2ATaskResponse:
        """Handle synchronous A2A message send"""
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Extract message content
            message_text = self._extract_text_from_message(request.message)
            
            # Prepare context for Gemini
            system_prompt = self._build_system_prompt(agent_card, request.context)
            
            # Generate response using Gemini
            response = await self.gemini_service.generate_response(
                prompt=message_text,
                system_prompt=system_prompt,
                model_name=agent_card.model_name
            )
            
            # Create response message
            response_message = create_a2a_message(
                text=response.get("response", ""),
                session_id=request.session_id,
                role="assistant"
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return A2ATaskResponse(
                task_id=request.id,
                session_id=request.session_id,
                success=True,
                status="completed",
                message=response_message,
                result={
                    "response_type": "text",
                    "agent_name": agent_card.name,
                    "ai_provider": agent_card.ai_provider,
                    "model_used": agent_card.model_name
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in A2A message send: {e}")
            
            return A2ATaskResponse(
                task_id=request.id,
                session_id=request.session_id,
                success=False,
                status="failed",
                error=str(e)
            )
    
    async def handle_message_stream(
        self,
        request: A2ATaskRequest,
        agent_card: A2AAgentCard
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Handle streaming A2A message send"""
        
        try:
            # Extract message content
            message_text = self._extract_text_from_message(request.message)
            
            # Prepare context for Gemini
            system_prompt = self._build_system_prompt(agent_card, request.context)
            
            # Start streaming response
            yield {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "type": "task_status_update",
                    "task_id": request.id,
                    "status": {
                        "type": "in_progress",
                        "message": {
                            "role": "assistant",
                            "parts": [{"type": "text", "text": f"Starting task with {agent_card.name}..."}]
                        }
                    }
                }
            }
            
            # Generate streaming response using Gemini
            full_response = ""
            async for chunk in self.gemini_service.generate_streaming_response(
                prompt=message_text,
                system_prompt=system_prompt,
                model_name=agent_card.model_name
            ):
                full_response += chunk
                
                # Send chunk as A2A streaming update
                yield {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "result": {
                        "type": "task_status_update",
                        "task_id": request.id,
                        "status": {
                            "type": "in_progress",
                            "message": {
                                "role": "assistant",
                                "parts": [{"type": "text", "text": chunk}]
                            }
                        }
                    }
                }
            
            # Send completion
            yield {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "type": "task_status_update",
                    "task_id": request.id,
                    "status": {
                        "type": "completed",
                        "message": {
                            "role": "assistant",
                            "parts": [{"type": "text", "text": "Task completed successfully"}]
                        },
                        "result": {
                            "response_type": "text",
                            "content": full_response,
                            "agent_name": agent_card.name,
                            "ai_provider": agent_card.ai_provider
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error in A2A message stream: {e}")
            
            # Send error response
            yield {
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {
                    "code": -32000,
                    "message": "Internal server error",
                    "data": {
                        "task_id": request.id,
                        "error": str(e)
                    }
                }
            }
    
    async def send_a2a_message(
        self,
        target_agent_url: str,
        message: A2AMessage,
        task_type: str = "general",
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Send A2A message to another agent"""
        
        try:
            # Create task request
            task_request = A2ATaskRequest(
                session_id=message.session_id,
                task_type=task_type,
                message=message
            )
            
            # Choose endpoint based on streaming preference
            endpoint = "message/stream" if stream else "message/send"
            
            # Prepare JSON-RPC request
            rpc_request = {
                "jsonrpc": "2.0",
                "id": task_request.id,
                "method": endpoint,
                "params": {
                    "id": task_request.id,
                    "sessionId": task_request.session_id,
                    "acceptedOutputModes": message.accepted_output_modes,
                    "message": {
                        "role": message.role,
                        "parts": message.parts
                    }
                }
            }
            
            # Send request
            async with httpx.AsyncClient(timeout=30.0) as client:
                if stream:
                    # Handle streaming response
                    async with client.stream(
                        "POST",
                        target_agent_url,
                        json=rpc_request,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    chunk_data = json.loads(line)
                                    yield chunk_data
                                except json.JSONDecodeError:
                                    continue
                else:
                    # Handle synchronous response
                    response = await client.post(
                        target_agent_url,
                        json=rpc_request,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    yield response.json()
                    
        except Exception as e:
            logger.error(f"Error sending A2A message to {target_agent_url}: {e}")
            yield {
                "jsonrpc": "2.0",
                "id": task_request.id,
                "error": {
                    "code": -32000,
                    "message": "Communication error",
                    "data": {"error": str(e)}
                }
            }
    
    def _extract_text_from_message(self, message: A2AMessage) -> str:
        """Extract text content from A2A message parts"""
        
        text_parts = []
        for part in message.parts:
            if part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        
        return " ".join(text_parts)
    
    def _build_system_prompt(
        self, 
        agent_card: A2AAgentCard, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build system prompt based on agent card and context"""
        
        system_prompt = f"""
You are {agent_card.name}, {agent_card.description}

Agent Capabilities:
- AI Provider: {agent_card.ai_provider}
- Model: {agent_card.model_name}
- Streaming: {agent_card.capabilities.streaming}
- Multi-modal: {agent_card.capabilities.multi_modal}

Skills:
{self._format_skills_for_prompt(agent_card.skills)}

Categories: {', '.join(agent_card.tags)}

Communication Protocol: A2A (Agent-to-Agent)
Response Format: Provide helpful, accurate responses as this specialized agent.
"""
        
        if context:
            system_prompt += f"\nAdditional Context: {json.dumps(context, indent=2)}"
        
        return system_prompt.strip()
    
    def _format_skills_for_prompt(self, skills: List) -> str:
        """Format skills for system prompt"""
        
        if not skills:
            return "- General AI assistance"
        
        skill_descriptions = []
        for skill in skills:
            skill_descriptions.append(f"- {skill.name}: {skill.description}")
            if skill.examples:
                skill_descriptions.append(f"  Examples: {', '.join(skill.examples[:2])}")
        
        return "\n".join(skill_descriptions)
