"""
Enhanced A2A Chat API with WebSocket support for real-time communication
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Request, Depends
from fastapi.responses import StreamingResponse
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

# Note: These imports would need to be created/imported based on your actual project structure
# from ..core.database import get_db
# from ..models.chat_models import ChatSession, ChatMessage
# from ..services.websocket_manager import WebSocketManager

# For now, using placeholder implementations
class ChatSession:
    def __init__(self, id: str, workflow_id: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None):
        self.id = id
        self.workflow_id = workflow_id
        self.user_id = user_id
        self.metadata = metadata or {}

class ChatMessage:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class WebSocketManager:
    def __init__(self):
        self.connections = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        return connection_id
    
    def disconnect(self, connection_id: str):
        if connection_id in self.connections:
            del self.connections[connection_id]
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        if connection_id in self.connections:
            websocket = self.connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logging.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)

def get_db():
    # Placeholder for database dependency
    return None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat/a2a", tags=["chat-a2a"])

# Initialize WebSocket manager for push notifications
ws_manager = WebSocketManager()

# A2A service URLs
A2A_AGENT_SERVICE_URL = "http://agents:8002/a2a"
A2A_ORCHESTRATOR_SERVICE_URL = "http://orchestrator:8003/a2a"


class A2AChatService:
    """Enhanced A2A Chat service with real-time capabilities"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> session_id mapping
    
    async def create_chat_session(
        self, 
        db: AsyncSession, 
        workflow_id: str, 
        user_id: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session with A2A capabilities"""
        
        session = ChatSession(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            user_id=user_id,
            metadata={
                "a2a_enabled": True,
                "push_notifications": True,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Initialize A2A session tracking
        self.active_sessions[session.id] = {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "connected_agents": [],
            "message_queue": [],
            "websocket_connections": []
        }
        
        logger.info(f"Created A2A chat session: {session.id}")
        return session
    
    async def send_a2a_message(
        self,
        session_id: str,
        message: str,
        message_type: str = "user",
        agent_target: Optional[str] = None,
        include_context: bool = True,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Send message through A2A protocol with real-time streaming"""
        
        try:
            # Prepare A2A JSON-RPC request
            a2a_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "message/stream" if stream else "message/send",
                "params": {
                    "id": str(uuid.uuid4()),
                    "sessionId": session_id,
                    "acceptedOutputModes": ["text", "attachments", "citations"],
                    "message": {
                        "role": message_type,
                        "parts": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    },
                    "context": {
                        "includeWorkflowContext": include_context,
                        "targetAgent": agent_target,
                        "enableA2ACommunication": True,
                        "enablePushNotifications": True
                    }
                }
            }
            
            # Choose endpoint based on agent target
            if agent_target:
                endpoint_url = f"{A2A_AGENT_SERVICE_URL}/agents/{agent_target.lower()}"
            else:
                endpoint_url = f"{A2A_ORCHESTRATOR_SERVICE_URL}/message/stream"
            
            # Send A2A request and stream response
            async with httpx.AsyncClient(timeout=60.0) as client:
                if stream:
                    async with client.stream(
                        "POST",
                        endpoint_url,
                        json=a2a_request,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "text/plain"
                        }
                    ) as response:
                        response.raise_for_status()
                        
                        async for line in response.aiter_lines():
                            if line.strip():
                                # Parse SSE data
                                if line.startswith("data: "):
                                    data_content = line[6:]  # Remove "data: " prefix
                                    
                                    if data_content == "[DONE]":
                                        # Send completion notification
                                        completion_data = {
                                            "type": "stream_complete",
                                            "session_id": session_id,
                                            "timestamp": datetime.utcnow().isoformat()
                                        }
                                        await self._notify_websocket_clients(session_id, completion_data)
                                        yield completion_data
                                        break
                                    
                                    try:
                                        chunk_data = json.loads(data_content)
                                        
                                        # Process A2A response chunk
                                        processed_chunk = await self._process_a2a_chunk(
                                            session_id, chunk_data
                                        )
                                        
                                        # Send real-time notification to WebSocket clients
                                        await self._notify_websocket_clients(session_id, processed_chunk)
                                        
                                        yield processed_chunk
                                        
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"Failed to parse A2A chunk: {e}")
                                        continue
                else:
                    # Non-streaming request
                    response = await client.post(
                        endpoint_url,
                        json=a2a_request,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    
                    result_data = response.json()
                    processed_result = await self._process_a2a_response(session_id, result_data)
                    
                    # Send notification
                    await self._notify_websocket_clients(session_id, processed_result)
                    yield processed_result
                    
        except httpx.HTTPError as e:
            error_data = {
                "type": "error",
                "session_id": session_id,
                "error": f"A2A communication error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            await self._notify_websocket_clients(session_id, error_data)
            yield error_data
            
        except Exception as e:
            logger.error(f"Error in A2A message send: {e}")
            error_data = {
                "type": "error",
                "session_id": session_id,
                "error": f"Internal error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            await self._notify_websocket_clients(session_id, error_data)
            yield error_data
    
    async def _process_a2a_chunk(self, session_id: str, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual A2A streaming chunk"""
        
        result = chunk_data.get("result", {})
        
        # Handle different A2A response types
        if result.get("type") == "task_status_update":
            status_info = result.get("status", {})
            
            if status_info.get("type") == "in_progress":
                # Extract streaming text
                message_parts = status_info.get("message", {}).get("parts", [])
                text_content = ""
                for part in message_parts:
                    if part.get("type") == "text":
                        text_content += part.get("text", "")
                
                return {
                    "type": "stream_chunk",
                    "session_id": session_id,
                    "content": text_content,
                    "agent_name": status_info.get("agent_name", "AI Assistant"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "chunk_id": result.get("task_id"),
                    "is_streaming": True
                }
                
            elif status_info.get("type") == "completed":
                # Handle completion with results
                result_data = status_info.get("result", {})
                
                return {
                    "type": "message_complete",
                    "session_id": session_id,
                    "content": result_data.get("content", ""),
                    "agent_name": result_data.get("agent_name", "AI Assistant"),
                    "citations": result_data.get("citations", []),
                    "tool_calls": result_data.get("tool_calls", []),
                    "scratchpad": result_data.get("scratchpad"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "is_complete": True
                }
                
        elif result.get("type") == "agent_communication":
            # Handle inter-agent communications
            return {
                "type": "a2a_communication",
                "session_id": session_id,
                "source_agent": result.get("source_agent"),
                "target_agent": result.get("target_agent"),
                "message": result.get("message"),
                "communication_type": result.get("message_type", "internal"),
                "latency_ms": result.get("latency_ms"),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Default processing
        return {
            "type": "unknown_chunk",
            "session_id": session_id,
            "raw_data": chunk_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _process_a2a_response(self, session_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete A2A response"""
        
        result = response_data.get("result", {})
        
        return {
            "type": "message_complete",
            "session_id": session_id,
            "content": result.get("content", ""),
            "agent_name": result.get("agent_name", "AI Assistant"),
            "success": result.get("success", True),
            "timestamp": datetime.utcnow().isoformat(),
            "is_complete": True,
            "metadata": result
        }
    
    async def _notify_websocket_clients(self, session_id: str, data: Dict[str, Any]):
        """Send push notification to WebSocket clients"""
        
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            
            # Send to all WebSocket connections for this session
            for connection_id in session_info.get("websocket_connections", []):
                await ws_manager.send_personal_message(connection_id, data)
    
    async def get_workflow_agents(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get available agents for a workflow from A2A service"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{A2A_AGENT_SERVICE_URL}/cards")
                response.raise_for_status()
                
                agent_cards = response.json()
                
                # Filter agents suitable for the workflow (simplified)
                return [
                    {
                        "id": card.get("name", "").lower().replace(" ", "_"),
                        "name": card.get("name"),
                        "description": card.get("description"),
                        "capabilities": card.get("skills", []),
                        "provider": card.get("ai_provider"),
                        "model": card.get("model_name")
                    }
                    for card in agent_cards
                ]
                
        except Exception as e:
            logger.error(f"Error fetching workflow agents: {e}")
            return []


# Initialize service
a2a_chat_service = A2AChatService()


@router.post("/sessions")
async def create_session(
    workflow_id: str,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new A2A chat session"""
    
    session = await a2a_chat_service.create_chat_session(
        db=db,
        workflow_id=workflow_id,
        user_id=user_id
    )
    
    # Get available agents for the workflow
    agents = await a2a_chat_service.get_workflow_agents(workflow_id)
    
    return {
        "session_id": session.id,
        "workflow_id": workflow_id,
        "agents": agents,
        "capabilities": {
            "streaming": True,
            "file_upload": True,
            "voice_input": True,
            "a2a_communication": True,
            "push_notifications": True
        }
    }


@router.post("/sessions/{session_id}/message/stream")
async def send_streaming_message(
    session_id: str,
    request: Request,
    agent_target: Optional[str] = None,
    include_context: bool = True
):
    """Send message with A2A streaming response"""
    
    try:
        body = await request.json()
        message = body.get("message", "")
        message_type = body.get("type", "user")
        
        if not message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content is required"
            )
        
        async def generate_stream():
            async for chunk in a2a_chat_service.send_a2a_message(
                session_id=session_id,
                message=message,
                message_type=message_type,
                agent_target=agent_target,
                include_context=include_context,
                stream=True
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: str,
    request: Request,
    agent_target: Optional[str] = None,
    include_context: bool = True
):
    """Send message with A2A non-streaming response"""
    
    try:
        body = await request.json()
        message = body.get("message", "")
        message_type = body.get("type", "user")
        
        # Get single response (non-streaming)
        responses = []
        async for response in a2a_chat_service.send_a2a_message(
            session_id=session_id,
            message=message,
            message_type=message_type,
            agent_target=agent_target,
            include_context=include_context,
            stream=False
        ):
            responses.append(response)
        
        return {
            "session_id": session_id,
            "responses": responses,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in message send: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time push notifications"""
    
    connection_id = await ws_manager.connect(websocket)
    
    # Associate connection with session
    if session_id in a2a_chat_service.active_sessions:
        session_info = a2a_chat_service.active_sessions[session_id]
        session_info["websocket_connections"].append(connection_id)
    
    try:
        # Send initial connection confirmation
        await ws_manager.send_personal_message(connection_id, {
            "type": "connection_established",
            "session_id": session_id,
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                if message_data.get("type") == "ping":
                    await ws_manager.send_personal_message(connection_id, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif message_data.get("type") == "send_message":
                    # Handle message sending through WebSocket
                    message_content = message_data.get("message", "")
                    if message_content:
                        async for response in a2a_chat_service.send_a2a_message(
                            session_id=session_id,
                            message=message_content,
                            stream=True
                        ):
                            await ws_manager.send_personal_message(connection_id, response)
                            
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {e}")
                await ws_manager.send_personal_message(connection_id, {
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    finally:
        # Clean up connection
        ws_manager.disconnect(connection_id)
        
        # Remove from session tracking
        if session_id in a2a_chat_service.active_sessions:
            session_info = a2a_chat_service.active_sessions[session_id]
            if connection_id in session_info["websocket_connections"]:
                session_info["websocket_connections"].remove(connection_id)


@router.get("/sessions/{session_id}/agents")
async def get_session_agents(session_id: str):
    """Get available agents for a session"""
    
    if session_id not in a2a_chat_service.active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session_info = a2a_chat_service.active_sessions[session_id]
    workflow_id = session_info["workflow_id"]
    
    agents = await a2a_chat_service.get_workflow_agents(workflow_id)
    
    return {
        "session_id": session_id,
        "workflow_id": workflow_id,
        "agents": agents,
        "connected_agents": session_info.get("connected_agents", [])
    }


@router.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session status and activity"""
    
    if session_id not in a2a_chat_service.active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session_info = a2a_chat_service.active_sessions[session_id]
    
    return {
        "session_id": session_id,
        "status": "active",
        "workflow_id": session_info["workflow_id"],
        "connected_agents": session_info.get("connected_agents", []),
        "websocket_connections": len(session_info.get("websocket_connections", [])),
        "message_queue_size": len(session_info.get("message_queue", [])),
        "last_activity": datetime.utcnow().isoformat()
    }
