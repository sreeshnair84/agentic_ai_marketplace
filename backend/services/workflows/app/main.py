"""
Default Workflow Service with LangGraph Plan and Execute
FastAPI service that provides A2A protocol endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import uuid
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from default_workflow_agent import DefaultWorkflowAgent, WorkflowConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Default Workflow Service",
    description="LangGraph-based workflow orchestration with Plan and Execute",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow agent instance
workflow_agent: Optional[DefaultWorkflowAgent] = None

# Pydantic models for A2A protocol
class A2AMessagePart(BaseModel):
    type: str  # 'text', 'file', 'audio', 'image'
    text: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    data: Optional[str] = None  # base64 encoded

class A2AMessage(BaseModel):
    role: str  # 'user', 'assistant', 'system'
    parts: List[A2AMessagePart]

class A2AContext(BaseModel):
    type: Optional[str] = None  # 'workflow', 'agent', 'tools'
    workflow: Optional[Dict[str, Any]] = None
    agent: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None

class A2ARequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Dict[str, Any]

class A2AResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the workflow agent on startup"""
    global workflow_agent
    try:
        config = WorkflowConfig()
        workflow_agent = DefaultWorkflowAgent(config)
        await workflow_agent.initialize()
        logger.info("Default Workflow Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize workflow agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Default Workflow Service")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Default Workflow Service",
        "version": "1.0.0",
        "status": "running",
        "langraph_enabled": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if workflow_agent is None:
        raise HTTPException(status_code=503, detail="Workflow agent not initialized")
    
    return {
        "status": "healthy",
        "agent_initialized": workflow_agent is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/a2a/card")
async def get_a2a_card():
    """Return A2A agent card for service discovery"""
    return {
        "id": "default-workflow-agent",
        "name": "Default Workflow Agent",
        "description": "LangGraph-based Plan and Execute workflow orchestration",
        "version": "1.0.0",
        "category": "workflow",
        "capabilities": {
            "planning": True,
            "execution": True,
            "memory": True,
            "context_aware": True,
            "multi_step": True
        },
        "default_input_modes": ["text", "json"],
        "default_output_modes": ["text", "json"],
        "skills": [
            {
                "name": "workflow_planning",
                "description": "Create execution plans for complex tasks",
                "input_types": ["text"],
                "output_types": ["json"]
            },
            {
                "name": "context_selection",
                "description": "Select optimal workflows/agents/tools based on query",
                "input_types": ["text", "json"],
                "output_types": ["json"]
            },
            {
                "name": "memory_management",
                "description": "Manage short and long-term memory",
                "input_types": ["json"],
                "output_types": ["json"]
            }
        ],
        "endpoints": {
            "message": "/a2a/message",
            "stream": "/a2a/message/stream"
        },
        "health_url": "/health",
        "card_url": "/a2a/card"
    }

@app.post("/a2a/message")
async def process_a2a_message(request: A2ARequest):
    """Process A2A message (synchronous)"""
    if workflow_agent is None:
        raise HTTPException(status_code=503, detail="Workflow agent not initialized")
    
    try:
        # Extract message and context from request
        params = request.params
        message = params.get("message", {})
        context = params.get("context", {})
        session_id = params.get("sessionId", f"session_{uuid.uuid4().hex[:8]}")
        
        # Get user query from message parts
        user_query = ""
        for part in message.get("parts", []):
            if part.get("type") == "text":
                user_query += part.get("text", "")
        
        if not user_query:
            raise HTTPException(status_code=400, detail="No text content found in message")
        
        # Process through workflow agent
        result = await workflow_agent.process_query(
            user_query=user_query,
            session_id=session_id,
            context=context
        )
        
        # Return A2A response
        return A2AResponse(
            id=request.id,
            result={
                "type": "task_completion",
                "status": "completed" if result["success"] else "error",
                "message": {
                    "role": "assistant",
                    "parts": [{"type": "text", "text": result["final_response"]}]
                },
                "execution_id": result["execution_id"],
                "step_results": result.get("step_results", {}),
                "errors": result.get("errors", [])
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing A2A message: {e}")
        return A2AResponse(
            id=request.id,
            error={
                "code": -32000,
                "message": "Workflow execution failed",
                "data": {"detail": str(e)}
            }
        )

@app.post("/a2a/message/stream")
async def stream_a2a_message(request: A2ARequest):
    """Process A2A message with streaming response"""
    if workflow_agent is None:
        raise HTTPException(status_code=503, detail="Workflow agent not initialized")
    
    async def generate_stream():
        try:
            # Extract message and context from request
            params = request.params
            message = params.get("message", {})
            context = params.get("context", {})
            session_id = params.get("sessionId", f"session_{uuid.uuid4().hex[:8]}")
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            
            # Get user query from message parts
            user_query = ""
            for part in message.get("parts", []):
                if part.get("type") == "text":
                    user_query += part.get("text", "")
            
            if not user_query:
                yield f"data: {json.dumps({'error': 'No text content found in message'})}\n\n"
                return
            
            # Send initial status
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'started', 'execution_id': execution_id}}})}\n\n"
            
            # Simulate planning phase
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'planning', 'message': {'parts': [{'type': 'text', 'text': 'Analyzing query and creating execution plan...'}]}}}})}\n\n"
            
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Simulate metadata loading
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'metadata_loading', 'message': {'parts': [{'type': 'text', 'text': 'Loading available workflows, agents, and tools...'}]}}}})}\n\n"
            
            await asyncio.sleep(0.3)
            
            # Simulate context selection
            selected_context_desc = "default orchestrator"
            if context.get("type") == "workflow":
                selected_context_desc = f"workflow: {context.get('workflow', {}).get('display_name', 'Unknown')}"
            elif context.get("type") == "agent":
                selected_context_desc = f"agent: {context.get('agent', {}).get('display_name', 'Unknown')}"
            elif context.get("type") == "tools":
                tool_count = len(context.get("tools", []))
                selected_context_desc = f"generic agent with {tool_count} tools"
            
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'context_selection', 'message': {'parts': [{'type': 'text', 'text': f'Selected context: {selected_context_desc}'}]}}}})}\n\n"
            
            await asyncio.sleep(0.3)
            
            # Process through workflow agent
            result = await workflow_agent.process_query(
                user_query=user_query,
                session_id=session_id,
                context=context
            )
            
            # Simulate execution steps
            steps = result.get("step_results", {})
            for step_key, step_data in steps.items():
                step_message = f"Executed {step_key}: {step_data.get('status', 'completed')}"
                yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'execution', 'step': step_key, 'message': {'parts': [{'type': 'text', 'text': step_message}]}}}})}\n\n"
                await asyncio.sleep(0.2)
            
            # Send final response
            final_response = result["final_response"]
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'completion', 'message': {'parts': [{'type': 'text', 'text': final_response}]}}}})}\n\n"
            
            # Send completion status
            completion_result = {
                "type": "task_status_update",
                "status": {
                    "type": "completed",
                    "result": {
                        "content": final_response,
                        "execution_id": result["execution_id"],
                        "step_results": result.get("step_results", {}),
                        "success": result["success"]
                    }
                }
            }
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': completion_result})}\n\n"
            
            # Send done signal
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming A2A message: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {
                    "code": -32000,
                    "message": "Workflow execution failed",
                    "data": {"detail": str(e)}
                }
            }
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/memory/sessions/{session_id}/stats")
async def get_session_memory_stats(session_id: str):
    """Get memory statistics for a session"""
    if workflow_agent is None:
        raise HTTPException(status_code=503, detail="Workflow agent not initialized")
    
    try:
        # Get memory stats from the agent's memory manager
        short_term = await workflow_agent.memory_manager.get_short_term_memory(session_id)
        
        return {
            "session_id": session_id,
            "short_term_count": len(short_term),
            "long_term_count": 0,  # Placeholder
            "total_executions": 1,  # Placeholder
            "memory_types": ["execution_plan", "step_result", "completion"],
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)