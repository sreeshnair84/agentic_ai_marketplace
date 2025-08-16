"""
A2A Protocol API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import logging
import json
import asyncio

from ..models.a2a_models import (
    A2AAgentCard, 
    A2AMessage, 
    A2ATaskRequest, 
    A2ATaskResponse,
    A2AAgentCardBuilder,
    AgentSkill,
    create_a2a_message
)
from ..services.a2a_handler import A2AProtocolHandler
from ..services.agent_service import AgentService
from ..core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/a2a", tags=["a2a"])

# Initialize A2A handler
a2a_handler = A2AProtocolHandler()


@router.on_event("startup")
async def initialize_a2a_cards():
    """Initialize default A2A agent cards on startup"""
    
    settings = get_settings()
    
    # Create default agent cards for our system
    
    # 1. General AI Assistant Agent
    general_skills = [
        AgentSkill(
            id="general_ai_assistant",
            name="General AI Assistant",
            description="Provides general AI assistance using Gemini AI",
            tags=["ai", "general", "assistant", "gemini"],
            examples=[
                {
                    "description": "Answer questions on various topics",
                    "input": {"query": "What is the capital of France?"},
                    "output": {"answer": "The capital of France is Paris."}
                },
                {
                    "description": "Help with analysis and reasoning",
                    "input": {"query": "Analyze the pros and cons of remote work"},
                    "output": {"analysis": "Remote work offers flexibility and cost savings but may impact collaboration and work-life balance."}
                },
                {
                    "description": "Provide explanations and summaries",
                    "input": {"query": "Summarize the benefits of AI in healthcare"},
                    "output": {"summary": "AI in healthcare improves diagnosis accuracy, enables personalized treatment, and enhances operational efficiency."}
                }
            ]
        )
    ]
    
    general_agent_card = A2AAgentCardBuilder.create_gemini_agent_card(
        name="GeneralAIAgent",
        description="General purpose AI assistant powered by Gemini AI for various tasks and queries",
        agent_type="general",
        endpoint_url=f"http://localhost:{settings.PORT}/a2a/agents/general",
        skills=general_skills,
        tags=["ai", "general", "gemini", "assistant"]
    )
    
    # 2. Specialized Task Agent
    task_skills = [
        AgentSkill(
            id="task_execution",
            name="Task Execution",
            description="Executes specialized tasks with Gemini AI capabilities",
            tags=["tasks", "execution", "specialized", "gemini"],
            examples=[
                {
                    "description": "Execute complex multi-step tasks",
                    "input": {"task": "Analyze customer feedback and create action plan"},
                    "output": {"plan": "Step-by-step action plan with recommendations"}
                },
                {
                    "description": "Process structured data",
                    "input": {"data": "CSV file with sales data"},
                    "output": {"analysis": "Processed insights and trends"}
                },
                {
                    "description": "Perform analysis and computation",
                    "input": {"request": "Calculate ROI for marketing campaigns"},
                    "output": {"result": "Detailed ROI analysis with metrics"}
                }
            ]
        )
    ]
    
    task_agent_card = A2AAgentCardBuilder.create_gemini_agent_card(
        name="TaskExecutorAgent",
        description="Specialized agent for executing complex tasks using Gemini AI",
        agent_type="task_executor",
        endpoint_url=f"http://localhost:{settings.PORT}/a2a/agents/task",
        skills=task_skills,
        tags=["tasks", "execution", "gemini", "specialized"]
    )
    
    # 3. Conversation Agent
    conversation_skills = [
        AgentSkill(
            id="conversation_management",
            name="Conversation Management",
            description="Manages conversational interactions with context awareness",
            tags=["conversation", "dialogue", "context", "gemini"],
            examples=[
                {
                    "description": "Maintain conversation context",
                    "input": {"message": "What did we discuss earlier?"},
                    "output": {"response": "Based on our previous conversation about..."}
                },
                {
                    "description": "Provide contextual responses",
                    "input": {"message": "How does this relate to the topic we covered?"},
                    "output": {"response": "This connects to our earlier discussion about..."}
                },
                {
                    "description": "Handle multi-turn dialogues",
                    "input": {"message": "Can you elaborate on that point?"},
                    "output": {"response": "Certainly, let me expand on the previous explanation..."}
                }
            ]
        )
    ]
    
    conversation_agent_card = A2AAgentCardBuilder.create_gemini_agent_card(
        name="ConversationAgent",
        description="Conversational AI agent with context awareness powered by Gemini",
        agent_type="conversation",
        endpoint_url=f"http://localhost:{settings.PORT}/a2a/agents/conversation",
        skills=conversation_skills,
        tags=["conversation", "dialogue", "gemini", "context"]
    )
    
    # Register all agent cards
    await a2a_handler.register_agent_card(general_agent_card)
    await a2a_handler.register_agent_card(task_agent_card)
    await a2a_handler.register_agent_card(conversation_agent_card)
    
    logger.info("Initialized A2A agent cards")


@router.get("/cards", response_model=List[Dict[str, Any]])
async def list_agent_cards(tags: Optional[str] = None):
    """List available A2A agent cards"""
    
    try:
        tag_list = tags.split(",") if tags else None
        cards = await a2a_handler.list_agent_cards(tag_list)
        
        return [card.dict() for card in cards]
        
    except Exception as e:
        logger.error(f"Error listing agent cards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agent cards: {str(e)}"
        )


@router.get("/cards/{agent_name}", response_model=Dict[str, Any])
async def get_agent_card(agent_name: str):
    """Get specific A2A agent card"""
    
    try:
        card = await a2a_handler.get_agent_card(agent_name)
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent card '{agent_name}' not found"
            )
        
        return card.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent card: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent card: {str(e)}"
        )


@router.post("/message/send")
async def handle_a2a_message_send(request: Request):
    """Handle A2A synchronous message send (JSON-RPC)"""
    
    try:
        # Parse JSON-RPC request
        body = await request.json()
        
        if body.get("jsonrpc") != "2.0":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON-RPC version"
            )
        
        method = body.get("method")
        if method != "message/send":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported method: {method}"
            )
        
        params = body.get("params", {})
        
        # Create A2A task request
        message = A2AMessage(
            session_id=params.get("sessionId", "default"),
            role=params.get("message", {}).get("role", "user"),
            parts=params.get("message", {}).get("parts", []),
            accepted_output_modes=params.get("acceptedOutputModes", ["text"])
        )
        
        task_request = A2ATaskRequest(
            id=params.get("id", body.get("id")),
            session_id=message.session_id,
            task_type="general",
            message=message
        )
        
        # Use default general agent card
        agent_card = await a2a_handler.get_agent_card("GeneralAIAgent")
        if not agent_card:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default agent not available"
            )
        
        # Handle the request
        response = await a2a_handler.handle_message_send(task_request, agent_card)
        
        # Return JSON-RPC response
        return {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "task_id": response.task_id,
                "success": response.success,
                "status": response.status,
                "message": response.message.dict() if response.message else None,
                "result": response.result
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in A2A message send: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process A2A message: {str(e)}"
        )


@router.post("/message/stream")
async def handle_a2a_message_stream(request: Request):
    """Handle A2A streaming message send (JSON-RPC with streaming)"""
    
    try:
        # Parse JSON-RPC request
        body = await request.json()
        
        if body.get("jsonrpc") != "2.0":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON-RPC version"
            )
        
        method = body.get("method")
        if method != "message/stream":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported method: {method}"
            )
        
        params = body.get("params", {})
        
        # Create A2A task request
        message = A2AMessage(
            session_id=params.get("sessionId", "default"),
            role=params.get("message", {}).get("role", "user"),
            parts=params.get("message", {}).get("parts", []),
            accepted_output_modes=params.get("acceptedOutputModes", ["text"])
        )
        
        task_request = A2ATaskRequest(
            id=params.get("id", body.get("id")),
            session_id=message.session_id,
            task_type="general",
            message=message
        )
        
        # Use default general agent card
        agent_card = await a2a_handler.get_agent_card("GeneralAIAgent")
        if not agent_card:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default agent not available"
            )
        
        # Create streaming response generator
        async def stream_generator():
            async for chunk in a2a_handler.handle_message_stream(task_request, agent_card):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in A2A message stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process A2A streaming message: {str(e)}"
        )


@router.post("/agents/{agent_type}")
async def handle_agent_specific_message(agent_type: str, request: Request):
    """Handle A2A message for specific agent type"""
    
    try:
        # Parse JSON-RPC request
        body = await request.json()
        
        # Map agent types to agent cards
        agent_mapping = {
            "general": "GeneralAIAgent",
            "task": "TaskExecutorAgent",
            "conversation": "ConversationAgent"
        }
        
        agent_name = agent_mapping.get(agent_type)
        if not agent_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent type '{agent_type}' not found"
            )
        
        agent_card = await a2a_handler.get_agent_card(agent_name)
        if not agent_card:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent '{agent_name}' not available"
            )
        
        # Handle streaming by default for agent-specific endpoints
        params = body.get("params", {})
        
        message = A2AMessage(
            session_id=params.get("sessionId", "default"),
            role=params.get("message", {}).get("role", "user"),
            parts=params.get("message", {}).get("parts", []),
            accepted_output_modes=params.get("acceptedOutputModes", ["text"])
        )
        
        task_request = A2ATaskRequest(
            id=params.get("id", body.get("id")),
            session_id=message.session_id,
            task_type=agent_type,
            message=message
        )
        
        # Create streaming response
        async def stream_generator():
            async for chunk in a2a_handler.handle_message_stream(task_request, agent_card):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent-specific A2A message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process agent message: {str(e)}"
        )


@router.post("/discover")
async def discover_agents(
    query: str,
    tags: Optional[List[str]] = None,
    max_results: int = 5
):
    """Discover agents based on query and tags (A2A discovery protocol)"""
    
    try:
        # Get available cards
        cards = await a2a_handler.list_agent_cards(tags)
        
        # Simple scoring based on query match in description and skills
        scored_cards = []
        query_lower = query.lower()
        
        for card in cards:
            score = 0
            
            # Check description match
            if query_lower in card.description.lower():
                score += 10
            
            # Check tag matches
            for tag in card.tags:
                if query_lower in tag.lower():
                    score += 5
            
            # Check skill matches
            for skill in card.skills:
                if query_lower in skill.description.lower():
                    score += 8
                if query_lower in skill.name.lower():
                    score += 6
            
            if score > 0:
                scored_cards.append((score, card))
        
        # Sort by score and return top results
        scored_cards.sort(key=lambda x: x[0], reverse=True)
        top_cards = [card for _, card in scored_cards[:max_results]]
        
        return {
            "query": query,
            "results": [card.dict() for card in top_cards],
            "count": len(top_cards)
        }
        
    except Exception as e:
        logger.error(f"Error discovering agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover agents: {str(e)}"
        )
