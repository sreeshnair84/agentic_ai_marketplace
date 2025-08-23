"""
A2A Agent Executor
Manages A2A agent execution lifecycle following the patterns from a2a-samples
"""

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator, List
from datetime import datetime
import uuid

try:
    from a2a_sdk import Task, TaskUpdater
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    # Mock classes for when A2A is not available
    class Task:
        def __init__(self, task_id: str, status: str = "created"):
            self.task_id = task_id
            self.status = status
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    class TaskUpdater:
        def __init__(self, task: Task):
            self.task = task
        
        async def update_status(self, status: str, message: str = None):
            self.task.status = status
            self.task.updated_at = datetime.utcnow()

from .a2a_agent_service import A2AAgentService, AgentResponse, AgentState

logger = logging.getLogger(__name__)

class A2AAgentExecutor:
    """
    Executor for A2A agents that manages the execution lifecycle
    and integrates with A2A protocol task management
    """
    
    def __init__(self, agent_service: A2AAgentService):
        self.agent_service = agent_service
        self.active_tasks: Dict[str, Task] = {}
        
        logger.info("A2A Agent Executor initialized")
    
    async def execute(
        self, 
        agent_id: str, 
        message: str, 
        task_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute an agent and manage the task lifecycle
        
        Args:
            agent_id: ID of the agent to execute
            message: Message to send to the agent
            task_id: Optional task ID for tracking
            thread_id: Optional thread ID for conversation continuity
        """
        
        # Generate IDs if not provided
        if not task_id:
            task_id = str(uuid.uuid4())
        if not thread_id:
            thread_id = f"thread_{task_id}"
        
        # Create task
        task = await self._create_task(task_id)
        task_updater = TaskUpdater(task) if A2A_AVAILABLE else TaskUpdater(task)
        
        try:
            # Validate agent exists
            agent = await self.agent_service.get_agent(agent_id)
            if not agent:
                error_msg = f"Agent {agent_id} not found"
                await task_updater.update_status("error", error_msg)
                yield {
                    "task_id": task_id,
                    "status": "error",
                    "message": error_msg,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return
            
            # Start task execution
            await task_updater.update_status("working", "Starting agent execution")
            yield {
                "task_id": task_id,
                "status": "working",
                "message": "Agent execution started",
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Execute agent and stream responses
            async for response in self.agent_service.execute_agent(agent_id, message, thread_id):
                # Convert agent response to task update
                task_status = self._map_agent_state_to_task_status(response.state)
                
                # Update task status
                await task_updater.update_status(task_status, response.message)
                
                # Yield response
                yield {
                    "task_id": task_id,
                    "status": task_status,
                    "message": response.message,
                    "agent_id": agent_id,
                    "state": response.state.value,
                    "requires_input": response.requires_input,
                    "data": response.data,
                    "error": response.error,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Handle state transitions
                if response.state == AgentState.INPUT_REQUIRED:
                    # Agent needs more input from user
                    await task_updater.update_status("input_required", response.message)
                    break
                
                elif response.state == AgentState.COMPLETED:
                    # Task completed successfully
                    await task_updater.update_status("completed", response.message)
                    break
                
                elif response.state == AgentState.ERROR:
                    # Task failed
                    await task_updater.update_status("error", response.message)
                    break
            
            # Final status update
            final_status = self._get_final_task_status(task.status)
            yield {
                "task_id": task_id,
                "status": final_status,
                "message": "Agent execution completed",
                "agent_id": agent_id,
                "final": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing agent {agent_id}: {str(e)}")
            
            # Update task with error
            await task_updater.update_status("error", f"Execution error: {str(e)}")
            
            yield {
                "task_id": task_id,
                "status": "error",
                "message": f"Execution error: {str(e)}",
                "agent_id": agent_id,
                "error": str(e),
                "final": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        finally:
            # Clean up task tracking
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def execute_default_chat(
        self, 
        message: str, 
        task_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute default chat agent (used when no specific agent is selected)
        """
        
        # Generate IDs if not provided
        if not task_id:
            task_id = str(uuid.uuid4())
        if not thread_id:
            thread_id = f"chat_{task_id}"
        
        # Create task
        task = await self._create_task(task_id)
        task_updater = TaskUpdater(task) if A2A_AVAILABLE else TaskUpdater(task)
        
        try:
            # Start task execution
            await task_updater.update_status("working", "Starting default chat")
            yield {
                "task_id": task_id,
                "status": "working",
                "message": "Starting chat session",
                "agent_id": "default_chat",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Execute default chat agent
            async for response in self.agent_service.chat_with_default_agent(message, thread_id):
                # Convert agent response to task update
                task_status = self._map_agent_state_to_task_status(response.state)
                
                # Update task status
                await task_updater.update_status(task_status, response.message)
                
                # Yield response
                yield {
                    "task_id": task_id,
                    "status": task_status,
                    "message": response.message,
                    "agent_id": "default_chat",
                    "state": response.state.value,
                    "requires_input": response.requires_input,
                    "data": response.data,
                    "error": response.error,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Handle completion
                if response.state in [AgentState.COMPLETED, AgentState.ERROR]:
                    break
            
            # Final status
            yield {
                "task_id": task_id,
                "status": "completed",
                "message": "Chat session completed",
                "agent_id": "default_chat",
                "final": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in default chat execution: {str(e)}")
            
            await task_updater.update_status("error", f"Chat error: {str(e)}")
            
            yield {
                "task_id": task_id,
                "status": "error",
                "message": f"Chat error: {str(e)}",
                "agent_id": "default_chat",
                "error": str(e),
                "final": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        finally:
            # Clean up task tracking
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task"""
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task_id,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
    
    async def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks"""
        tasks = []
        for task_id, task in self.active_tasks.items():
            tasks.append({
                "task_id": task_id,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            })
        return tasks
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "cancelled"
            task.updated_at = datetime.utcnow()
            del self.active_tasks[task_id]
            return True
        return False
    
    async def _create_task(self, task_id: str) -> Task:
        """Create a new task"""
        task = Task(task_id, "created")
        self.active_tasks[task_id] = task
        
        logger.info(f"Created task: {task_id}")
        return task
    
    def _map_agent_state_to_task_status(self, agent_state: AgentState) -> str:
        """Map agent state to A2A task status"""
        mapping = {
            AgentState.WORKING: "working",
            AgentState.INPUT_REQUIRED: "input_required",
            AgentState.COMPLETED: "completed",
            AgentState.ERROR: "error"
        }
        return mapping.get(agent_state, "working")
    
    def _get_final_task_status(self, current_status: str) -> str:
        """Get the final status for task completion"""
        if current_status in ["error", "cancelled"]:
            return current_status
        return "completed"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the executor"""
        return {
            "status": "healthy",
            "a2a_available": A2A_AVAILABLE,
            "active_tasks": len(self.active_tasks),
            "agent_service_status": self.agent_service.get_health_status(),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global A2A agent executor instance
_a2a_agent_executor: Optional[A2AAgentExecutor] = None

async def get_a2a_agent_executor() -> A2AAgentExecutor:
    """Get A2A agent executor instance"""
    global _a2a_agent_executor
    if _a2a_agent_executor is None:
        from .a2a_agent_service import get_a2a_agent_service
        agent_service = await get_a2a_agent_service()
        _a2a_agent_executor = A2AAgentExecutor(agent_service)
    return _a2a_agent_executor