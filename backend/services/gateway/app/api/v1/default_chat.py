"""
Default Chat API
REST endpoints for default chat functionality when no specific agents/workflows are selected
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json
import asyncio

from ...services.default_chat_service import DefaultChatService
from ...services.langgraph_model_service import LangGraphModelService
from ...core.dependencies import get_current_user
from ...core.database import get_db_session

router = APIRouter(prefix="/default-chat", tags=["Default Chat"])

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ChatRequest(BaseModel):
    """Request model for chat"""
    message: str = Field(..., description="User message")
    conversation_history: Optional[List[ChatMessage]] = Field([], description="Previous conversation messages")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    stream: bool = Field(False, description="Whether to stream the response")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    temperature: Optional[float] = Field(None, description="Temperature for response generation")

class ChatResponse(BaseModel):
    """Response model for chat"""
    success: bool
    message: str
    role: str
    timestamp: str
    user_id: Optional[str]
    session_id: Optional[str]
    model_info: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None

class ConversationSummaryRequest(BaseModel):
    """Request model for conversation summary"""
    conversation_history: List[ChatMessage] = Field(..., description="Conversation to summarize")
    max_length: int = Field(200, description="Maximum length of summary")

async def get_chat_service(db_session=Depends(get_db_session)) -> DefaultChatService:
    """Dependency to get the chat service"""
    model_service = LangGraphModelService(db_session)
    return DefaultChatService(model_service)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: DefaultChatService = Depends(get_chat_service),
    current_user = Depends(get_current_user)
):
    """
    Send a message to the default chat service
    Returns a single response when streaming is disabled
    """
    try:
        if request.stream:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use /chat/stream endpoint for streaming responses"
            )
        
        # Convert ChatMessage objects to dict
        history = []
        if request.conversation_history:
            history = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "metadata": msg.metadata
                }
                for msg in request.conversation_history
            ]
        
        response = await chat_service.chat(
            message=request.message,
            conversation_history=history,
            user_id=current_user.get("id") if current_user else None,
            session_id=request.session_id,
            stream=False
        )
        
        if not response.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.get("error", "Chat request failed")
            )
        
        return ChatResponse(**response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    chat_service: DefaultChatService = Depends(get_chat_service),
    current_user = Depends(get_current_user)
):
    """
    Send a message to the default chat service with streaming response
    Returns Server-Sent Events (SSE) stream
    """
    try:
        # Convert ChatMessage objects to dict
        history = []
        if request.conversation_history:
            history = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "metadata": msg.metadata
                }
                for msg in request.conversation_history
            ]
        
        async def generate_stream():
            try:
                async for chunk in chat_service.chat(
                    message=request.message,
                    conversation_history=history,
                    user_id=current_user.get("id") if current_user else None,
                    session_id=request.session_id,
                    stream=True
                ):
                    # Format as Server-Sent Events
                    data = json.dumps(chunk)
                    yield f"data: {data}\n\n"
                
                # Send final event to close stream
                yield f"data: {json.dumps({'final': True, 'success': True})}\n\n"
                
            except Exception as e:
                error_data = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "final": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming chat error: {str(e)}"
        )

@router.get("/health")
async def get_chat_health(
    chat_service: DefaultChatService = Depends(get_chat_service),
    current_user = Depends(get_current_user)
):
    """Get health status of the default chat service"""
    try:
        health_status = chat_service.get_health_status()
        return health_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get health status: {str(e)}"
        )

@router.post("/conversation/summary")
async def get_conversation_summary(
    request: ConversationSummaryRequest,
    chat_service: DefaultChatService = Depends(get_chat_service),
    current_user = Depends(get_current_user)
):
    """Generate a summary of the conversation"""
    try:
        # Convert ChatMessage objects to dict
        history = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "metadata": msg.metadata
            }
            for msg in request.conversation_history
        ]
        
        summary = await chat_service.get_conversation_summary(
            conversation_history=history,
            max_length=request.max_length
        )
        
        if summary is None:
            return {
                "success": False,
                "error": "Could not generate summary - no default model configured",
                "summary": None
            }
        
        return {
            "success": True,
            "summary": summary,
            "message_count": len(history),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )

@router.get("/models/default")
async def get_default_model_info(
    chat_service: DefaultChatService = Depends(get_chat_service),
    current_user = Depends(get_current_user)
):
    """Get information about the current default model"""
    try:
        default_llm = await chat_service.model_service.get_default_llm()
        if not default_llm:
            return {
                "success": False,
                "error": "No default model configured",
                "model": None,
                "message": "Please configure a default LLM model in the Models section"
            }
        
        model_info = await chat_service._get_model_info(default_llm)
        
        return {
            "success": True,
            "model": model_info,
            "default_llm_id": chat_service.model_service.default_llm_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get default model info: {str(e)}"
        )

@router.post("/test")
async def test_default_chat(
    test_message: str = "Hello, this is a test message",
    chat_service: DefaultChatService = Depends(get_chat_service),
    current_user = Depends(get_current_user)
):
    """Test the default chat service with a simple message"""
    try:
        response = await chat_service.chat(
            message=test_message,
            conversation_history=[],
            user_id=current_user.get("id") if current_user else None,
            session_id="test-session",
            stream=False
        )
        
        return {
            "test_successful": response.get("success", False),
            "response": response,
            "test_message": test_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e),
            "test_message": test_message,
            "timestamp": datetime.utcnow().isoformat()
        }