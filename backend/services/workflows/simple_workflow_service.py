"""
Simple Workflow Service for testing
FastAPI service that provides A2A protocol endpoints without LangGraph
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
import uuid
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple Workflow Service",
    description="Simple workflow orchestration for testing A2A integration",
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

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Simple Workflow Service",
        "version": "1.0.0",
        "status": "running",
        "langraph_enabled": False
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/a2a/card")
async def get_a2a_card():
    """Return A2A agent card for service discovery"""
    return {
        "id": "simple-workflow-agent",
        "name": "Simple Workflow Agent",
        "description": "Simple workflow orchestration for testing",
        "version": "1.0.0",
        "category": "workflow",
        "capabilities": {
            "planning": True,
            "execution": True,
            "memory": False,
            "context_aware": True,
            "multi_step": True
        },
        "default_input_modes": ["text", "json"],
        "default_output_modes": ["text", "json"],
        "endpoints": {
            "message": "/a2a/message",
            "stream": "/a2a/message/stream"
        },
        "health_url": "/health",
        "card_url": "/a2a/card"
    }

def analyze_query_and_context(user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Simple query analysis"""
    query_lower = user_query.lower()
    
    # Simulate intelligent analysis
    if "create" in query_lower or "build" in query_lower:
        task_type = "creation"
    elif "analyze" in query_lower or "find" in query_lower:
        task_type = "analysis"
    elif "help" in query_lower or "support" in query_lower:
        task_type = "assistance"
    else:
        task_type = "general"
    
    # Determine response based on context
    if context.get("type") == "workflow":
        workflow_name = context.get("workflow", {}).get("display_name", "Unknown Workflow")
        response = f"✅ Routing your {task_type} request to **{workflow_name}**. This workflow specializes in handling {task_type} tasks with advanced capabilities."
    elif context.get("type") == "agent":
        agent_name = context.get("agent", {}).get("display_name", "Unknown Agent")
        response = f"✅ Connecting you to **{agent_name}**. This agent is optimized for {task_type} tasks and will provide specialized assistance."
    elif context.get("type") == "tools":
        tool_count = len(context.get("tools", []))
        tool_names = ", ".join([t.get("display_name", t.get("name", "Unknown")) for t in context.get("tools", [])[:3]])
        response = f"✅ Using **{tool_count} specialized tools** ({tool_names}{'...' if tool_count > 3 else ''}) to handle your {task_type} request with enhanced capabilities."
    else:
        response = f"✅ Using **Smart Plan & Execute** workflow to analyze your {task_type} request and select the optimal approach from available resources."
    
    return {
        "task_type": task_type,
        "response": response,
        "context_used": context.get("type", "default"),
        "steps": [
            "Query analysis completed",
            "Context evaluation finished", 
            "Optimal approach selected",
            "Ready for execution"
        ]
    }

@app.post("/a2a/message")
async def process_a2a_message(request: A2ARequest):
    """Process A2A message (synchronous)"""
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
        
        # Process query with simple analysis
        result = analyze_query_and_context(user_query, context)
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        # Return A2A response
        return A2AResponse(
            id=request.id,
            result={
                "type": "task_completion",
                "status": "completed",
                "message": {
                    "role": "assistant",
                    "parts": [{"type": "text", "text": result["response"]}]
                },
                "execution_id": execution_id,
                "step_results": {
                    "analysis": {"status": "completed", "result": result["task_type"]},
                    "context_evaluation": {"status": "completed", "result": result["context_used"]},
                    "response_generation": {"status": "completed", "result": "success"}
                },
                "errors": []
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
                yield f"data: {json.dumps({'error': 'No text content found in message'})}\\n\\n"
                return
            
            # Send initial status
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'started', 'execution_id': execution_id}}})}\\n\\n"
            
            # Simulate planning phase
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'planning', 'message': {'parts': [{'type': 'text', 'text': '🤖 Analyzing your request and determining the best approach...'}]}}}})}\\n\\n"
            
            await asyncio.sleep(0.5)
            
            # Simulate context analysis
            context_desc = "default workflow"
            if context.get("type") == "workflow":
                context_desc = f"workflow: {context.get('workflow', {}).get('display_name', 'Unknown')}"
            elif context.get("type") == "agent":
                context_desc = f"agent: {context.get('agent', {}).get('display_name', 'Unknown')}"
            elif context.get("type") == "tools":
                tool_count = len(context.get("tools", []))
                context_desc = f"generic agent with {tool_count} tools"
            
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'context_analysis', 'message': {'parts': [{'type': 'text', 'text': f'📊 Evaluating context: {context_desc}'}]}}}})}\\n\\n"
            
            await asyncio.sleep(0.4)
            
            # Process with analysis
            result = analyze_query_and_context(user_query, context)
            
            # Simulate execution steps
            for i, step in enumerate(result["steps"]):
                yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'execution', 'step': f'step_{i+1}', 'message': {'parts': [{'type': 'text', 'text': f'⚡ {step}'}]}}}})}\\n\\n"
                await asyncio.sleep(0.3)
            
            # Send final response
            final_response = result["response"]
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': {'type': 'task_status_update', 'status': {'type': 'in_progress', 'phase': 'completion', 'message': {'parts': [{'type': 'text', 'text': final_response}]}}}})}\\n\\n"
            
            # Send completion status
            completion_result = {
                "type": "task_status_update",
                "status": {
                    "type": "completed",
                    "result": {
                        "content": final_response,
                        "execution_id": execution_id,
                        "step_results": {
                            "analysis": {"status": "completed", "result": result["task_type"]},
                            "context_evaluation": {"status": "completed", "result": result["context_used"]},
                            "response_generation": {"status": "completed", "result": "success"}
                        },
                        "success": True
                    }
                }
            }
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': request.id, 'result': completion_result})}\\n\\n"
            
            # Send done signal
            yield "data: [DONE]\\n\\n"
            
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
            yield f"data: {json.dumps(error_response)}\\n\\n"
            yield "data: [DONE]\\n\\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)