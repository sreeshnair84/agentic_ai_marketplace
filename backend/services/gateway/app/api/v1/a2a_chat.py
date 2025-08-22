"""
A2A Chat API
Endpoints for A2A agent chat functionality with streaming support
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import json

from ...services.a2a_agent_service import get_a2a_agent_service, A2AAgentService
from ...services.a2a_agent_executor import get_a2a_agent_executor, A2AAgentExecutor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/a2a", tags=["A2A Chat"])

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    agent_id: Optional[str] = Field(None, description="Specific agent ID (optional)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    conversation_history: List[ChatMessage] = Field(default=[], description="Previous messages")
    stream: bool = Field(default=False, description="Enable streaming response")

class ChatResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None

class StreamChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    agent_id: Optional[str] = Field(None, description="Specific agent ID (optional)")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    conversation_history: List[ChatMessage] = Field(default=[], description="Previous messages")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    updated_at: str

@router.get("/agents")
async def list_a2a_agents(
    agent_service: A2AAgentService = Depends(get_a2a_agent_service)
):
    """List all available A2A agents"""
    try:
        agents = await agent_service.list_agents()
        return {
            "success": True,
            "agents": agents,
            "count": len(agents),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing A2A agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")

@router.get("/agents/{agent_id}")
async def get_a2a_agent(
    agent_id: str,
    agent_service: A2AAgentService = Depends(get_a2a_agent_service)
):
    """Get details of a specific A2A agent"""
    try:
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "success": True,
            "agent": {
                "id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "status": "active" if agent.agent else "inactive"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting agent: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_a2a_agent(
    request: ChatRequest,
    executor: A2AAgentExecutor = Depends(get_a2a_agent_executor)
):
    """Chat with A2A agents (non-streaming)"""
    try:
        if request.stream:
            raise HTTPException(
                status_code=400, 
                detail="Use /chat/stream endpoint for streaming responses"
            )
        
        messages = []
        
        if request.agent_id:
            # Chat with specific agent
            async for response in executor.execute(
                agent_id=request.agent_id,
                message=request.message,
                thread_id=request.session_id
            ):
                messages.append(response)
                if response.get("final", False):
                    break
        else:
            # Chat with default agent
            async for response in executor.execute_default_chat(
                message=request.message,
                thread_id=request.session_id
            ):
                messages.append(response)
                if response.get("final", False):
                    break
        
        # Get the final message
        final_message = messages[-1] if messages else {
            "message": "No response generated",
            "status": "error"
        }
        
        return ChatResponse(
            success=final_message.get("status") != "error",
            message=final_message.get("message", ""),
            task_id=final_message.get("task_id"),
            agent_id=final_message.get("agent_id"),
            session_id=request.session_id,
            timestamp=datetime.utcnow(),
            data={
                "conversation_history": messages,
                "state": final_message.get("state"),
                "requires_input": final_message.get("requires_input", False)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in A2A chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/chat/stream")
async def stream_chat_with_a2a_agent(
    request: StreamChatRequest,
    executor: A2AAgentExecutor = Depends(get_a2a_agent_executor)
):
    """Stream chat responses from A2A agents"""
    
    async def generate_stream():
        try:
            if request.agent_id:
                # Stream with specific agent
                agent_stream = executor.execute(
                    agent_id=request.agent_id,
                    message=request.message,
                    thread_id=request.session_id
                )
            else:
                # Stream with default agent
                agent_stream = executor.execute_default_chat(
                    message=request.message,
                    thread_id=request.session_id
                )
            
            async for response in agent_stream:
                # Format as Server-Sent Event
                data = json.dumps(response)
                yield f"data: {data}\n\n"
                
                # End stream on final message
                if response.get("final", False):
                    break
                    
        except Exception as e:
            logger.error(f"Error in streaming chat: {str(e)}")
            error_response = {
                "error": str(e),
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "final": True
            }
            yield f"data: {json.dumps(error_response)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/tasks")
async def list_active_tasks(
    executor: A2AAgentExecutor = Depends(get_a2a_agent_executor)
):
    """List all active A2A tasks"""
    try:
        tasks = await executor.list_active_tasks()
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    executor: A2AAgentExecutor = Depends(get_a2a_agent_executor)
):
    """Get status of a specific task"""
    try:
        task_status = await executor.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return {
            "success": True,
            "task": task_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    executor: A2AAgentExecutor = Depends(get_a2a_agent_executor)
):
    """Cancel a running task"""
    try:
        cancelled = await executor.cancel_task(task_id)
        
        if not cancelled:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found or not cancellable")
        
        return {
            "success": True,
            "message": f"Task {task_id} cancelled successfully",
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")

@router.get("/health")
async def a2a_health_check(
    executor: A2AAgentExecutor = Depends(get_a2a_agent_executor)
):
    """Get health status of A2A system"""
    try:
        health_status = executor.get_health_status()
        return {
            "success": True,
            "health": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting A2A health status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")

@router.get("/config")
async def get_a2a_config(
    agent_service: A2AAgentService = Depends(get_a2a_agent_service)
):
    """Get A2A system configuration"""
    try:
        config = {
            "system_info": {
                "version": "1.0.0",
                "protocol": "A2A",
                "framework": "LangGraph",
                "capabilities": [
                    "agent_execution",
                    "streaming_responses", 
                    "task_management",
                    "multi_agent_support"
                ]
            },
            "agents": await agent_service.list_agents(),
            "health": agent_service.get_health_status()
        }
        
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting A2A config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Config error: {str(e)}")