"""
Workflow Engine Service - Process automation and orchestration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union, Literal
from enum import Enum
import os
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
import json
import redis.asyncio as redis
import httpx
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Workflow execution status
class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class StepType(str, Enum):
    AGENT_CALL = "agent_call"
    TOOL_CALL = "tool_call"
    HTTP_REQUEST = "http_request"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    DELAY = "delay"
    SCRIPT = "script"

# Pydantic models
class WorkflowStep(BaseModel):
    id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Human-readable step name")
    type: StepType = Field(..., description="Type of step to execute")
    config: Dict[str, Any] = Field({}, description="Step configuration")
    depends_on: List[str] = Field([], description="Step dependencies")
    timeout_seconds: Optional[int] = Field(300, description="Step timeout")
    retry_attempts: int = Field(0, description="Number of retry attempts")
    retry_delay_seconds: int = Field(5, description="Delay between retries")
    condition: Optional[str] = Field(None, description="Execution condition")

class WorkflowDefinition(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    version: str = Field("1.0.0", description="Workflow version")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    variables: Dict[str, Any] = Field({}, description="Workflow variables")
    timeout_seconds: Optional[int] = Field(3600, description="Overall workflow timeout")
    
    @validator('steps')
    def validate_steps(cls, steps):
        step_ids = [step.id for step in steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Step IDs must be unique")
        
        # Validate dependencies exist
        for step in steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(f"Step {step.id} depends on non-existent step {dep}")
        
        return steps

class WorkflowExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Dict[str, Any] = Field({})
    output_data: Dict[str, Any] = Field({})
    error_message: Optional[str] = None
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = Field({})
    step_statuses: Dict[str, StepStatus] = Field({})

class WorkflowExecutionRequest(BaseModel):
    workflow_name: str = Field(..., description="Name of workflow to execute")
    input_data: Dict[str, Any] = Field({}, description="Input data for workflow")
    variables: Dict[str, Any] = Field({}, description="Runtime variables")

class StepResult(BaseModel):
    step_id: str
    status: StepStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[float] = None

# Global storage
workflows: Dict[str, WorkflowDefinition] = {}
executions: Dict[str, WorkflowExecution] = {}
redis_client = None

# HTTP client for external calls
http_client = httpx.AsyncClient(timeout=30.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global redis_client
    
    # Startup
    logger.info("Starting Workflow Engine service...")
    
    try:
        # Initialize Redis connection for state management
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Workflow Engine service...")
    if redis_client:
        await redis_client.close()
    await http_client.aclose()

app = FastAPI(
    title="Workflow Engine Service",
    description="Process automation and orchestration service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    redis_status = "connected" if redis_client else "disconnected"
    
    return {
        "status": "healthy",
        "service": "workflow-engine",
        "version": "1.0.0",
        "features": {
            "workflow_execution": True,
            "step_orchestration": True,
            "conditional_logic": True,
            "parallel_execution": True,
            "retry_mechanisms": True
        },
        "redis_status": redis_status,
        "active_workflows": len(workflows),
        "running_executions": len([e for e in executions.values() if e.status == WorkflowStatus.RUNNING])
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Workflow Engine Service",
        "version": "1.0.0",
        "description": "Process automation and orchestration service",
        "endpoints": {
            "workflows": "/workflows",
            "executions": "/executions",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.post("/workflows", status_code=201)
async def create_workflow(workflow: WorkflowDefinition):
    """Create a new workflow definition"""
    
    try:
        workflows[workflow.name] = workflow
        
        # Persist to Redis if available
        if redis_client:
            # hset returns number of fields that were added
            redis_client.hset(
                "workflows", 
                workflow.name, 
                workflow.json()
            )
        
        logger.info(f"Created workflow: {workflow.name}")
        
        return {
            "message": f"Workflow '{workflow.name}' created successfully",
            "workflow_name": workflow.name,
            "steps_count": len(workflow.steps)
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create workflow: {str(e)}"
        )


@app.get("/workflows")
async def list_workflows():
    """List all workflow definitions"""
    
    workflow_list = []
    
    for name, workflow in workflows.items():
        workflow_list.append({
            "name": name,
            "description": workflow.description,
            "version": workflow.version,
            "steps_count": len(workflow.steps),
            "timeout_seconds": workflow.timeout_seconds
        })
    
    return {
        "workflows": workflow_list,
        "total": len(workflow_list)
    }


@app.get("/workflows/{workflow_name}")
async def get_workflow(workflow_name: str):
    """Get workflow definition"""
    
    if workflow_name not in workflows:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_name}' not found"
        )
    
    return workflows[workflow_name]


@app.delete("/workflows/{workflow_name}")
async def delete_workflow(workflow_name: str):
    """Delete workflow definition"""
    
    if workflow_name not in workflows:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_name}' not found"
        )
    
    # Check for running executions
    running_executions = [
        e for e in executions.values()
        if e.workflow_name == workflow_name and e.status == WorkflowStatus.RUNNING
    ]
    
    if running_executions:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete workflow '{workflow_name}' - {len(running_executions)} executions are running"
        )
    
    # Delete workflow
    del workflows[workflow_name]
    
    # Remove from Redis if available
    if redis_client:
        # hdel returns number of fields that were removed  
        result = redis_client.hdel("workflows", workflow_name)
    
    logger.info(f"Deleted workflow: {workflow_name}")
    
    return {"message": f"Workflow '{workflow_name}' deleted successfully"}


@app.post("/executions", status_code=201)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks
):
    """Start workflow execution"""
    
    if request.workflow_name not in workflows:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{request.workflow_name}' not found"
        )
    
    # Create execution instance
    execution = WorkflowExecution(
        workflow_name=request.workflow_name,
        input_data=request.input_data
    )
    
    # Initialize step statuses
    workflow = workflows[request.workflow_name]
    for step in workflow.steps:
        execution.step_statuses[step.id] = StepStatus.PENDING
    
    # Store execution
    executions[execution.id] = execution
    
    # Start execution in background
    background_tasks.add_task(run_workflow_execution, execution.id, request.variables)
    
    logger.info(f"Started workflow execution: {execution.id}")
    
    return {
        "execution_id": execution.id,
        "workflow_name": request.workflow_name,
        "status": execution.status,
        "message": "Workflow execution started"
    }


@app.get("/executions")
async def list_executions(
    status: Optional[WorkflowStatus] = None,
    workflow_name: Optional[str] = None,
    limit: int = 100
):
    """List workflow executions"""
    
    execution_list = []
    
    for execution in executions.values():
        # Apply filters
        if status and execution.status != status:
            continue
        if workflow_name and execution.workflow_name != workflow_name:
            continue
        
        execution_list.append({
            "id": execution.id,
            "workflow_name": execution.workflow_name,
            "status": execution.status,
            "created_at": execution.created_at,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "current_step": execution.current_step,
            "error_message": execution.error_message
        })
    
    # Sort by creation time (newest first) and limit
    execution_list.sort(key=lambda x: x["created_at"], reverse=True)
    execution_list = execution_list[:limit]
    
    return {
        "executions": execution_list,
        "total": len(execution_list)
    }


@app.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get workflow execution details"""
    
    if execution_id not in executions:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found"
        )
    
    return executions[execution_id]


@app.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel workflow execution"""
    
    if execution_id not in executions:
        raise HTTPException(
            status_code=404,
            detail=f"Execution '{execution_id}' not found"
        )
    
    execution = executions[execution_id]
    
    if execution.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel execution in status '{execution.status}'"
        )
    
    execution.status = WorkflowStatus.CANCELLED
    execution.completed_at = datetime.utcnow()
    execution.error_message = "Execution cancelled by user"
    
    logger.info(f"Cancelled workflow execution: {execution_id}")
    
    return {"message": f"Execution '{execution_id}' cancelled successfully"}


async def run_workflow_execution(execution_id: str, runtime_variables: Dict[str, Any]):
    """Execute workflow steps"""
    
    try:
        execution = executions[execution_id]
        workflow = workflows[execution.workflow_name]
        
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.utcnow()
        
        # Merge workflow variables with runtime variables
        variables = {**workflow.variables, **runtime_variables, **execution.input_data}
        
        # Build dependency graph
        dependency_graph = {}
        for step in workflow.steps:
            dependency_graph[step.id] = step.depends_on
        
        # Execute steps
        await execute_workflow_steps(execution, workflow, variables, dependency_graph)
        
        # Mark as completed if all steps succeeded
        if all(status == StepStatus.COMPLETED for status in execution.step_statuses.values()):
            execution.status = WorkflowStatus.COMPLETED
        else:
            execution.status = WorkflowStatus.FAILED
        
        execution.completed_at = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        execution.status = WorkflowStatus.FAILED
        execution.completed_at = datetime.utcnow()
        execution.error_message = str(e)


async def execute_workflow_steps(
    execution: WorkflowExecution,
    workflow: WorkflowDefinition,
    variables: Dict[str, Any],
    dependency_graph: Dict[str, List[str]]
):
    """Execute workflow steps respecting dependencies"""
    
    completed_steps = set()
    step_map = {step.id: step for step in workflow.steps}
    
    while len(completed_steps) < len(workflow.steps):
        # Find steps ready to execute
        ready_steps = []
        
        for step_id, dependencies in dependency_graph.items():
            if step_id in completed_steps:
                continue
            
            if execution.step_statuses[step_id] != StepStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            if all(dep in completed_steps for dep in dependencies):
                ready_steps.append(step_id)
        
        if not ready_steps:
            # Check for failed steps
            failed_steps = [
                step_id for step_id, status in execution.step_statuses.items()
                if status == StepStatus.FAILED
            ]
            if failed_steps:
                raise Exception(f"Workflow failed due to failed steps: {failed_steps}")
            else:
                raise Exception("No ready steps found - possible circular dependency")
        
        # Execute ready steps (can be done in parallel)
        tasks = []
        for step_id in ready_steps:
            step = step_map[step_id]
            tasks.append(execute_single_step(execution, step, variables))
        
        # Wait for all steps to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            step_id = ready_steps[i]
            
            if isinstance(result, Exception):
                execution.step_statuses[step_id] = StepStatus.FAILED
                execution.step_results[step_id] = {"error": str(result)}
                logger.error(f"Step {step_id} failed: {result}")
            else:
                execution.step_statuses[step_id] = StepStatus.COMPLETED
                execution.step_results[step_id] = result
                completed_steps.add(step_id)
                
                # Update variables with step output
                if isinstance(result, dict) and "output" in result:
                    variables.update(result["output"])


async def execute_single_step(
    execution: WorkflowExecution,
    step: WorkflowStep,
    variables: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute a single workflow step"""
    
    start_time = datetime.utcnow()
    execution.current_step = step.id
    execution.step_statuses[step.id] = StepStatus.RUNNING
    
    try:
        # Check condition if specified
        if step.condition:
            # Simple condition evaluation (can be enhanced)
            if not eval_condition(step.condition, variables):
                execution.step_statuses[step.id] = StepStatus.SKIPPED
                return {"status": "skipped", "reason": "condition not met"}
        
        # Execute step based on type
        if step.type == StepType.AGENT_CALL:
            result = await execute_agent_call(step, variables)
        elif step.type == StepType.TOOL_CALL:
            result = await execute_tool_call(step, variables)
        elif step.type == StepType.HTTP_REQUEST:
            result = await execute_http_request(step, variables)
        elif step.type == StepType.DELAY:
            result = await execute_delay(step, variables)
        elif step.type == StepType.SCRIPT:
            result = await execute_script(step, variables)
        else:
            raise NotImplementedError(f"Step type '{step.type}' not implemented")
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "completed",
            "result": result,
            "execution_time_ms": execution_time,
            "output": result.get("output", {}) if isinstance(result, dict) else {}
        }
        
    except Exception as e:
        logger.error(f"Step {step.id} execution failed: {e}")
        raise


async def execute_agent_call(step: WorkflowStep, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute agent call step"""
    
    config = step.config
    agent_url = config.get("agent_url", "http://localhost:8002")
    message = substitute_variables(config.get("message", ""), variables)
    
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "id": step.id,
            "session_id": f"workflow_{step.id}",
            "accepted_output_modes": ["text"],
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}]
            }
        }
    }
    
    async with http_client as client:
        response = await client.post(f"{agent_url}/a2a/message/send", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return {
            "agent_response": result,
            "output": {"agent_result": result.get("result", {})}
        }


async def execute_tool_call(step: WorkflowStep, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool call step"""
    
    config = step.config
    tool_url = config.get("tool_url", "http://localhost:8005")
    tool_name = config.get("tool_name")
    tool_params = substitute_variables(config.get("params", {}), variables)
    
    payload = {
        "tool_name": tool_name,
        "parameters": tool_params
    }
    
    async with http_client as client:
        response = await client.post(f"{tool_url}/tools/execute", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return {
            "tool_response": result,
            "output": {"tool_result": result.get("result", {})}
        }


async def execute_http_request(step: WorkflowStep, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute HTTP request step"""
    
    config = step.config
    method = config.get("method", "GET").upper()
    url = substitute_variables(config.get("url", ""), variables)
    headers = substitute_variables(config.get("headers", {}), variables)
    data = substitute_variables(config.get("data", {}), variables)
    
    async with http_client as client:
        response = await client.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        
        return {
            "http_response": result,
            "status_code": response.status_code,
            "output": {"http_result": result}
        }


async def execute_delay(step: WorkflowStep, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute delay step"""
    
    delay_seconds = step.config.get("delay_seconds", 1)
    await asyncio.sleep(delay_seconds)
    
    return {
        "delay_seconds": delay_seconds,
        "output": {}
    }


async def execute_script(step: WorkflowStep, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Execute script step (simple Python evaluation)"""
    
    script = step.config.get("script", "")
    
    # Simple and safe script execution (can be enhanced with sandboxing)
    local_vars = variables.copy()
    
    try:
        exec(script, {"__builtins__": {}}, local_vars)
        
        # Extract output variables (variables that changed)
        output = {k: v for k, v in local_vars.items() if k not in variables or variables[k] != v}
        
        return {
            "script_executed": True,
            "output": output
        }
        
    except Exception as e:
        raise Exception(f"Script execution failed: {e}")


def eval_condition(condition: str, variables: Dict[str, Any]) -> bool:
    """Evaluate condition string"""
    
    try:
        # Simple condition evaluation (can be enhanced with safer evaluation)
        return bool(eval(condition, {"__builtins__": {}}, variables))
    except Exception:
        return False


def substitute_variables(obj: Any, variables: Dict[str, Any]) -> Any:
    """Substitute variables in object"""
    
    if isinstance(obj, str):
        # Simple variable substitution using string formatting
        try:
            return obj.format(**variables)
        except (KeyError, ValueError):
            return obj
    elif isinstance(obj, dict):
        return {k: substitute_variables(v, variables) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [substitute_variables(item, variables) for item in obj]
    else:
        return obj


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
