"""
LangGraph Agent Manager for Agent Templates and Instances
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentWorkflowResult:
    success: bool
    message: str
    session_id: str
    response: Optional[str] = None
    tools_used: List[str] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None

class LangGraphAgentManager:
    """Manages LangGraph workflows for agent instances"""
    
    def __init__(self):
        self.active_agents: Dict[str, Any] = {}
        self.workflows: Dict[str, Any] = {}
        
    async def create_agent_workflow(self, agent_instance):
        """Create a LangGraph workflow from an agent instance"""
        try:
            agent_id = str(agent_instance.id)
            template = agent_instance.template
            
            # Create workflow based on framework
            if template.framework == "langgraph":
                workflow = await self._create_langgraph_workflow(agent_instance)
            elif template.framework == "crewai":
                workflow = await self._create_crewai_workflow(agent_instance)
            elif template.framework == "autogen":
                workflow = await self._create_autogen_workflow(agent_instance)
            elif template.framework == "semantic_kernel":
                workflow = await self._create_semantic_kernel_workflow(agent_instance)
            else:
                workflow = await self._create_custom_workflow(agent_instance)
            
            self.workflows[agent_id] = workflow
            logger.info(f"Created workflow for agent {agent_instance.name}")
            
        except Exception as e:
            logger.error(f"Failed to create workflow for agent {agent_instance.name}: {e}")
            raise
    
    async def update_agent_workflow(self, agent_instance):
        """Update an existing agent workflow"""
        agent_id = str(agent_instance.id)
        if agent_id in self.workflows:
            await self.remove_agent_workflow(agent_id)
        await self.create_agent_workflow(agent_instance)
    
    async def remove_agent_workflow(self, agent_instance_id: str):
        """Remove an agent workflow"""
        if agent_instance_id in self.workflows:
            del self.workflows[agent_instance_id]
        if agent_instance_id in self.active_agents:
            del self.active_agents[agent_instance_id]
        logger.info(f"Removed workflow for agent {agent_instance_id}")
    
    async def start_agent(self, agent_instance):
        """Start an agent instance"""
        agent_id = str(agent_instance.id)
        
        if agent_id not in self.workflows:
            await self.create_agent_workflow(agent_instance)
        
        # Initialize agent state
        self.active_agents[agent_id] = {
            "instance": agent_instance,
            "workflow": self.workflows[agent_id],
            "sessions": {},
            "status": "active"
        }
        
        logger.info(f"Started agent {agent_instance.name}")
    
    async def stop_agent(self, agent_instance_id: str):
        """Stop an agent instance"""
        if agent_instance_id in self.active_agents:
            # Clean up active sessions
            agent_data = self.active_agents[agent_instance_id]
            for session_id in agent_data.get("sessions", {}):
                # Clean up session resources
                pass
            
            del self.active_agents[agent_instance_id]
        
        logger.info(f"Stopped agent {agent_instance_id}")
    
    async def execute_agent(self, agent_instance_id: str, message: str, session_id: str = None, context: Dict[str, Any] = None) -> AgentWorkflowResult:
        """Execute an agent with a message"""
        if agent_instance_id not in self.active_agents:
            return AgentWorkflowResult(
                success=False,
                message="Agent not active",
                session_id=session_id or "unknown",
                error_message="Agent instance is not running"
            )
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            agent_data = self.active_agents[agent_instance_id]
            workflow = agent_data["workflow"]
            
            # Prepare input state
            input_state = {
                "message": message,
                "session_id": session_id,
                "context": context or {},
                "agent_instance_id": agent_instance_id
            }
            
            # Execute workflow
            start_time = asyncio.get_event_loop().time()
            result = await workflow.ainvoke(input_state)
            end_time = asyncio.get_event_loop().time()
            
            execution_time_ms = int((end_time - start_time) * 1000)
            
            return AgentWorkflowResult(
                success=True,
                message="Agent executed successfully",
                session_id=session_id,
                response=result.get("response", ""),
                tools_used=result.get("tools_used", []),
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            logger.error(f"Agent execution failed for {agent_instance_id}: {e}")
            return AgentWorkflowResult(
                success=False,
                message=f"Agent execution failed: {str(e)}",
                session_id=session_id,
                error_message=str(e)
            )
    
    # Framework-specific workflow creation methods
    
    async def _create_langgraph_workflow(self, agent_instance):
        """Create a LangGraph workflow"""
        template = agent_instance.template
        workflow_config = template.workflow_config
        tool_bindings = agent_instance.tool_instance_bindings
        
        # Mock LangGraph workflow implementation
        async def workflow_executor(state):
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            # Mock processing with tool bindings
            tools_used = []
            response = f"LangGraph agent response to: {message}"
            
            # Simulate tool usage based on bindings
            for role, tool_instance_id in tool_bindings.items():
                tools_used.append(f"{role}_{tool_instance_id}")
            
            return {
                "response": response,
                "tools_used": tools_used,
                "session_id": session_id
            }
        
        return MockWorkflow(workflow_executor)
    
    async def _create_crewai_workflow(self, agent_instance):
        """Create a CrewAI workflow"""
        async def workflow_executor(state):
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            response = f"CrewAI agent response to: {message}"
            
            return {
                "response": response,
                "tools_used": ["crewai_tool"],
                "session_id": session_id
            }
        
        return MockWorkflow(workflow_executor)
    
    async def _create_autogen_workflow(self, agent_instance):
        """Create an AutoGen workflow"""
        async def workflow_executor(state):
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            response = f"AutoGen agent response to: {message}"
            
            return {
                "response": response,
                "tools_used": ["autogen_tool"],
                "session_id": session_id
            }
        
        return MockWorkflow(workflow_executor)
    
    async def _create_semantic_kernel_workflow(self, agent_instance):
        """Create a Semantic Kernel workflow"""
        async def workflow_executor(state):
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            response = f"Semantic Kernel agent response to: {message}"
            
            return {
                "response": response,
                "tools_used": ["semantic_kernel_tool"],
                "session_id": session_id
            }
        
        return MockWorkflow(workflow_executor)
    
    async def _create_custom_workflow(self, agent_instance):
        """Create a custom workflow"""
        async def workflow_executor(state):
            message = state.get("message", "")
            session_id = state.get("session_id", "")
            
            response = f"Custom agent response to: {message}"
            
            return {
                "response": response,
                "tools_used": ["custom_tool"],
                "session_id": session_id
            }
        
        return MockWorkflow(workflow_executor)

class MockWorkflow:
    """Mock workflow implementation for testing"""
    
    def __init__(self, executor_func):
        self.executor_func = executor_func
    
    async def ainvoke(self, state):
        """Invoke the workflow asynchronously"""
        return await self.executor_func(state)
