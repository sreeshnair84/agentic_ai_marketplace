"""
A2A Protocol API endpoints for Orchestrator
Based on https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/multiagent
"""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
import json
import logging
import asyncio
import httpx

from ..models.a2a_models import (
    A2AAgentCard, A2AMessage, A2ATask, A2ATaskRequest,
    JsonRpcRequest, JsonRpcSuccessResponse, JsonRpcErrorResponse,
    MessageSendParams, MessageStreamParams, A2AAgentCardBuilder,
    Role, A2AMessagePart, A2APartType
)
from ..services.a2a_orchestrator import A2AOrchestratorAgent
from ..core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Global orchestrator instance
_orchestrator: Optional[A2AOrchestratorAgent] = None


async def get_orchestrator() -> A2AOrchestratorAgent:
    """Get or create the global orchestrator instance"""
    global _orchestrator
    
    if _orchestrator is None:
        settings = get_settings()
        
        # Initialize with known agent addresses
        remote_agents = [
            "http://localhost:8002",  # Agents service
            "http://localhost:8004",  # RAG service  
            "http://localhost:8005",  # Tools service
        ]
        
        _orchestrator = A2AOrchestratorAgent(
            remote_agent_addresses=remote_agents,
            http_client=httpx.AsyncClient()
        )
    
    return _orchestrator


@router.get("/cards")
async def get_agent_cards():
    """Get orchestrator agent card(s)"""
    try:
        orchestrator = await get_orchestrator()
        card = orchestrator.get_agent_card()
        return card.model_dump()
        
    except Exception as e:
        logger.error(f"Error getting agent cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/{agent_name}")
async def get_specific_agent_card(agent_name: str):
    """Get specific agent card"""
    try:
        orchestrator = await get_orchestrator()
        
        if agent_name.lower() in ["orchestrator", "lcnc_orchestrator_agent"]:
            card = orchestrator.get_agent_card()
            return card.model_dump()
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent card for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover")
async def discover_agents(
    query: str,
    max_results: int = 5,
    tags: Optional[List[str]] = None
):
    """Discover agents suitable for a query"""
    try:
        orchestrator = await get_orchestrator()
        agents = await orchestrator.discover_agents(
            query=query,
            max_results=max_results,
            tags=tags
        )
        
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "url": agent.url,
                "capabilities": agent.card.capabilities.model_dump(),
                "skills": [skill.model_dump() for skill in agent.card.skills],
                "tags": agent.card.tags
            }
            for agent in agents
        ]
        
    except Exception as e:
        logger.error(f"Error discovering agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/send")
async def send_message(request: Request):
    """Handle A2A message/send (JSON-RPC 2.0) - synchronous"""
    try:
        # Parse JSON-RPC request
        body = await request.json()
        rpc_request = JsonRpcRequest(**body)
        
        if rpc_request.method != "message/send":
            return JsonRpcErrorResponse(
                id=rpc_request.id,
                error={
                    "code": -32601,
                    "message": "Method not found",
                    "data": f"Method {rpc_request.method} not supported"
                }
            ).model_dump()
        
        # Parse message parameters
        params = MessageSendParams(**rpc_request.params)
        
        # Get orchestrator and handle message
        orchestrator = await get_orchestrator()
        
        # Convert A2A message to user query
        user_query = ""
        for part in params.message.parts:
            if part.type == A2APartType.text and part.text:
                user_query += part.text + " "
        user_query = user_query.strip()
        
        # Handle the message (non-streaming)
        result = None
        async for response in orchestrator.handle_user_message(
            user_query=user_query,
            session_id=params.session_id,
            context_id=params.context_id,
            stream=False
        ):
            result = response
            break  # Get first (and only) result for non-streaming
        
        if result is None:
            return JsonRpcErrorResponse(
                id=rpc_request.id,
                error={
                    "code": -32000,
                    "message": "No result from orchestration"
                }
            ).model_dump()
        
        # Create task response
        from ..models.a2a_models import A2ATaskStatus, TaskState
        task_response = A2ATask(
            id=params.id,
            context_id=params.context_id,
            status=A2ATaskStatus(
                state=TaskState.completed,
                message=A2AMessage(
                    role=Role.assistant,
                    parts=[A2AMessagePart(
                        type=A2APartType.text,
                        text=result.summary if hasattr(result, 'summary') else str(result)
                    )]
                )
            )
        )
        
        return JsonRpcSuccessResponse(
            id=rpc_request.id,
            result=task_response.model_dump()
        ).model_dump()
        
    except Exception as e:
        logger.error(f"Error in message/send: {e}")
        return JsonRpcErrorResponse(
            id=getattr(rpc_request, 'id', "unknown"),
            error={
                "code": -32000,
                "message": "Internal error",
                "data": str(e)
            }
        ).model_dump()


@router.post("/message/stream")
async def stream_message(request: Request):
    """Handle A2A message/stream (JSON-RPC 2.0) - streaming"""
    try:
        # Parse JSON-RPC request
        body = await request.json()
        rpc_request = JsonRpcRequest(**body)
        
        if rpc_request.method != "message/stream":
            error_response = JsonRpcErrorResponse(
                id=rpc_request.id,
                error={
                    "code": -32601,
                    "message": "Method not found",
                    "data": f"Method {rpc_request.method} not supported"
                }
            )
            return Response(
                content=f"data: {json.dumps(error_response.model_dump())}\n\n",
                media_type="text/plain"
            )
        
        # Parse message parameters
        params = MessageStreamParams(**rpc_request.params)
        
        # Convert A2A message to user query
        user_query = ""
        for part in params.message.parts:
            if part.type == A2APartType.text and part.text:
                user_query += part.text + " "
        user_query = user_query.strip()
        
        async def generate_stream():
            try:
                orchestrator = await get_orchestrator()
                
                async for response in orchestrator.handle_user_message(
                    user_query=user_query,
                    session_id=params.session_id,
                    context_id=params.context_id,
                    stream=True
                ):
                    # Format as JSON-RPC success response
                    rpc_response = JsonRpcSuccessResponse(
                        id=rpc_request.id,
                        result=response
                    )
                    
                    yield f"data: {json.dumps(rpc_response.model_dump())}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream generation: {e}")
                error_response = JsonRpcErrorResponse(
                    id=rpc_request.id,
                    error={
                        "code": -32000,
                        "message": "Stream error",
                        "data": str(e)
                    }
                )
                yield f"data: {json.dumps(error_response.model_dump())}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in message/stream: {e}")
        error_response = JsonRpcErrorResponse(
            id=getattr(rpc_request, 'id', "unknown"),
            error={
                "code": -32000,
                "message": "Internal error",
                "data": str(e)
            }
        )
        return Response(
            content=f"data: {json.dumps(error_response.model_dump())}\n\n",
            media_type="text/plain"
        )


# Additional orchestrator-specific endpoints

@router.get("/agents")
async def list_available_agents():
    """List all available agents"""
    try:
        orchestrator = await get_orchestrator()
        agents = await orchestrator.list_available_agents()
        return {"agents": agents}
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/add")
async def add_remote_agent(agent_url: str):
    """Add a new remote agent"""
    try:
        orchestrator = await get_orchestrator()
        agent_card = await orchestrator.add_remote_agent(agent_url)
        return {
            "message": f"Added agent {agent_card.name}",
            "agent_card": agent_card.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Error adding agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_name}")
async def remove_remote_agent(agent_name: str):
    """Remove a remote agent"""
    try:
        orchestrator = await get_orchestrator()
        await orchestrator.remove_remote_agent(agent_name)
        return {"message": f"Removed agent {agent_name}"}
        
    except Exception as e:
        logger.error(f"Error removing agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/agents")
async def health_check_agents():
    """Health check all connected agents"""
    try:
        orchestrator = await get_orchestrator()
        health_status = await orchestrator.health_check_agents()
        return {"agent_health": health_status}
        
    except Exception as e:
        logger.error(f"Error checking agent health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_active_sessions():
    """List active orchestration sessions"""
    try:
        orchestrator = await get_orchestrator()
        sessions = orchestrator.list_active_sessions()
        return {"active_sessions": sessions}
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session_context(session_id: str):
    """Get session context"""
    try:
        orchestrator = await get_orchestrator()
        context = orchestrator.get_session_context(session_id)
        
        if context is None:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return context.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Simple orchestration endpoint for testing
@router.post("/orchestrate")
async def orchestrate_query(
    query: str,
    session_id: Optional[str] = None,
    stream: bool = False
):
    """Simple orchestration endpoint for testing"""
    try:
        orchestrator = await get_orchestrator()
        
        if stream:
            async def generate_response():
                async for result in orchestrator.handle_user_message(
                    user_query=query,
                    session_id=session_id,
                    stream=True
                ):
                    yield f"data: {json.dumps(result)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_response(),
                media_type="text/plain"
            )
        else:
            results = []
            async for result in orchestrator.handle_user_message(
                user_query=query,
                session_id=session_id,
                stream=False
            ):
                results.append(result)
            
            return {"results": results}
            
    except Exception as e:
        logger.error(f"Error in orchestration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
