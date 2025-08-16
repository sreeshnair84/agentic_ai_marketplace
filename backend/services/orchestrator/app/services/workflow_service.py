"""
Workflow service implementation
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
import uuid

from ..core.database import Workflow, WorkflowExecution, Task
from ..core.config import get_settings
from .agent_service import AgentService
from .task_queue import TaskQueue

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for managing workflows and their execution"""
    
    def __init__(self):
        self.settings = get_settings()
        self.agent_service = AgentService()
        self.task_queue = TaskQueue()
        self.running_executions: Dict[str, asyncio.Task] = {}
    
    async def create_workflow(
        self,
        db: AsyncSession,
        name: str,
        definition: Dict[str, Any],
        created_by: str,
        description: Optional[str] = None
    ) -> Workflow:
        """Create a new workflow"""
        
        # Validate workflow definition
        self._validate_workflow_definition(definition)
        
        workflow = Workflow(
            name=name,
            description=description,
            definition=definition,
            created_by=created_by,
            status="created"
        )
        
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        logger.info(f"Created workflow {workflow.id}: {name}")
        return workflow
    
    async def execute_workflow(
        self,
        db: AsyncSession,
        workflow_id: str,
        created_by: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """Execute a workflow"""
        
        # Get workflow
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if not workflow.is_active:
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            input_data=input_data,
            created_by=created_by,
            status="pending"
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Start execution asynchronously
        execution_task = asyncio.create_task(
            self._execute_workflow_async(db, execution.id, workflow.definition, input_data)
        )
        self.running_executions[execution.id] = execution_task
        
        logger.info(f"Started execution {execution.id} for workflow {workflow_id}")
        return execution
    
    async def _execute_workflow_async(
        self,
        db: AsyncSession,
        execution_id: str,
        definition: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None
    ):
        """Execute workflow asynchronously"""
        
        try:
            # Update execution status
            await self._update_execution_status(db, execution_id, "running", started_at=datetime.utcnow())
            
            # Execute workflow steps
            output_data = await self._execute_workflow_steps(db, execution_id, definition, input_data)
            
            # Update execution as completed
            await self._update_execution_status(
                db, 
                execution_id, 
                "completed", 
                output_data=output_data,
                completed_at=datetime.utcnow()
            )
            
            logger.info(f"Completed execution {execution_id}")
            
        except Exception as e:
            logger.error(f"Error in execution {execution_id}: {e}")
            
            # Update execution as failed
            await self._update_execution_status(
                db, 
                execution_id, 
                "failed", 
                error_message=str(e),
                completed_at=datetime.utcnow()
            )
        
        finally:
            # Clean up
            self.running_executions.pop(execution_id, None)
    
    async def _execute_workflow_steps(
        self,
        db: AsyncSession,
        execution_id: str,
        definition: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the workflow steps"""
        
        steps = definition.get("steps", [])
        context = {"input": input_data or {}}
        
        for step in steps:
            step_type = step.get("type")
            step_config = step.get("config", {})
            
            if step_type == "agent_task":
                result = await self._execute_agent_task(db, execution_id, step_config, context)
            elif step_type == "tool_call":
                result = await self._execute_tool_call(db, execution_id, step_config, context)
            elif step_type == "parallel":
                result = await self._execute_parallel_tasks(db, execution_id, step_config, context)
            elif step_type == "conditional":
                result = await self._execute_conditional(db, execution_id, step_config, context)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
            
            # Update context with step result
            context[step.get("name", f"step_{len(context)}")] = result
        
        return {"output": context}
    
    async def _execute_agent_task(
        self,
        db: AsyncSession,
        execution_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an agent task"""
        
        agent_id = config.get("agent_id")
        task_data = config.get("task_data", {})
        
        # Create task record
        task = Task(
            execution_id=execution_id,
            task_type="agent_task",
            agent_id=agent_id,
            input_data={"config": config, "context": context},
            status="pending"
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        try:
            # Execute agent task
            result = await self.agent_service.execute_task(
                agent_id=agent_id,
                task_data=task_data,
                context=context
            )
            
            # Update task as completed
            task.status = "completed"
            task.output_data = result
            task.completed_at = datetime.utcnow()
            await db.commit()
            
            return result
            
        except Exception as e:
            # Update task as failed
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await db.commit()
            raise
    
    async def _execute_tool_call(
        self,
        db: AsyncSession,
        execution_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call"""
        
        tool_name = config.get("tool_name")
        tool_params = config.get("parameters", {})
        
        # Create task record
        task = Task(
            execution_id=execution_id,
            task_type="tool_call",
            tool_name=tool_name,
            input_data={"config": config, "context": context},
            status="pending"
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        try:
            # Execute tool call via agent service
            result = await self.agent_service.execute_tool(
                tool_name=tool_name,
                parameters=tool_params,
                context=context
            )
            
            # Update task as completed
            task.status = "completed"
            task.output_data = result
            task.completed_at = datetime.utcnow()
            await db.commit()
            
            return result
            
        except Exception as e:
            # Update task as failed
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await db.commit()
            raise
    
    async def _execute_parallel_tasks(
        self,
        db: AsyncSession,
        execution_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute parallel tasks"""
        
        tasks = config.get("tasks", [])
        
        # Execute tasks in parallel
        async_tasks = []
        for task_config in tasks:
            if task_config.get("type") == "agent_task":
                async_tasks.append(
                    self._execute_agent_task(db, execution_id, task_config, context)
                )
            elif task_config.get("type") == "tool_call":
                async_tasks.append(
                    self._execute_tool_call(db, execution_id, task_config, context)
                )
        
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Process results
        task_results = {}
        for i, result in enumerate(results):
            task_name = tasks[i].get("name", f"task_{i}")
            if isinstance(result, Exception):
                task_results[task_name] = {"error": str(result)}
            else:
                task_results[task_name] = result
        
        return task_results
    
    async def _execute_conditional(
        self,
        db: AsyncSession,
        execution_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute conditional logic"""
        
        condition = config.get("condition")
        if_true = config.get("if_true")
        if_false = config.get("if_false")
        
        # Evaluate condition (simple implementation)
        condition_result = self._evaluate_condition(condition, context)
        
        if condition_result:
            if if_true:
                return await self._execute_workflow_steps(db, execution_id, {"steps": [if_true]}, context)
        else:
            if if_false:
                return await self._execute_workflow_steps(db, execution_id, {"steps": [if_false]}, context)
        
        return {"condition_result": condition_result}
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple condition (basic implementation)"""
        
        # Basic condition evaluation
        # In production, use a more sophisticated expression evaluator
        try:
            # Replace context variables
            for key, value in context.items():
                condition = condition.replace(f"${key}", str(value))
            
            # Simple evaluation (unsafe - replace with safe evaluator)
            return eval(condition)
        except:
            return False
    
    async def _update_execution_status(
        self,
        db: AsyncSession,
        execution_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update execution status"""
        
        result = await db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        
        if execution:
            execution.status = status
            if output_data is not None:
                execution.output_data = output_data
            if error_message is not None:
                execution.error_message = error_message
            if started_at is not None:
                execution.started_at = started_at
            if completed_at is not None:
                execution.completed_at = completed_at
            
            await db.commit()
    
    def _validate_workflow_definition(self, definition: Dict[str, Any]):
        """Validate workflow definition"""
        
        if "steps" not in definition:
            raise ValueError("Workflow definition must include 'steps'")
        
        steps = definition["steps"]
        if not isinstance(steps, list):
            raise ValueError("Workflow steps must be a list")
        
        for step in steps:
            if "type" not in step:
                raise ValueError("Each step must have a 'type'")
            
            step_type = step["type"]
            if step_type not in ["agent_task", "tool_call", "parallel", "conditional"]:
                raise ValueError(f"Invalid step type: {step_type}")


# Global workflow service instance
workflow_service = WorkflowService()
