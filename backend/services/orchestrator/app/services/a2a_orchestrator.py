"""
A2A Protocol Orchestrator Agent
Based on https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/multiagent
"""

import asyncio
import httpx
import logging
from typing import Dict, Any, Optional, List
import json
import uuid
from datetime import datetime

from ..models.a2a_models import (
    A2AAgentCard, A2AMessage, A2ATask, A2ATaskRequest, A2AMessagePart, A2APartType,
    TaskState, Role, RemoteAgentInfo, OrchestrationContext, OrchestrationPlan,
    OrchestrationResult, A2AAgentCardBuilder
)
from .remote_agent_connection import RemoteAgentConnections, TaskUpdateCallback
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class A2AOrchestratorAgent:
    """
    A2A Protocol Orchestrator Agent
    
    This is the main orchestrator that coordinates multiple remote agents
    following the A2A protocol standard.
    """
    
    def __init__(
        self,
        remote_agent_addresses: Optional[List[str]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        task_callback: Optional[TaskUpdateCallback] = None
    ):
        self.settings = get_settings()
        self.http_client = http_client or httpx.AsyncClient()
        self.task_callback = task_callback
        self._own_client = http_client is None
        
        # Initialize remote agent connections
        self.remote_agents = RemoteAgentConnections(
            http_client=self.http_client,
            task_callback=self.task_callback
        )
        
        # Agent discovery and management
        self.available_agents: Dict[str, RemoteAgentInfo] = {}
        self.active_sessions: Dict[str, OrchestrationContext] = {}
        self.orchestration_plans: Dict[str, OrchestrationPlan] = {}
        
        # Initialize with known agents
        if remote_agent_addresses:
            asyncio.create_task(self._initialize_remote_agents(remote_agent_addresses))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_client:
            await self.http_client.aclose()
    
    async def _initialize_remote_agents(self, addresses: List[str]):
        """Initialize connections to remote agents"""
        
        for address in addresses:
            try:
                agent_card = await self.remote_agents.add_agent(address)
                agent_info = RemoteAgentInfo(
                    name=agent_card.name,
                    description=agent_card.description,
                    url=agent_card.url,
                    card=agent_card,
                    status="active"
                )
                self.available_agents[agent_card.name] = agent_info
                logger.info(f"Initialized remote agent: {agent_card.name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize agent at {address}: {e}")
    
    def get_agent_card(self) -> A2AAgentCard:
        """Get the orchestrator's agent card"""
        return A2AAgentCardBuilder.create_orchestrator_card(
            host=self.settings.HOST,
            port=self.settings.PORT
        )
    
    async def discover_agents(
        self, 
        query: str,
        max_results: int = 5,
        tags: Optional[List[str]] = None
    ) -> List[RemoteAgentInfo]:
        """
        Discover agents suitable for a given query
        
        This is a simplified implementation. In production, this would use
        semantic search, embeddings, or other sophisticated matching.
        """
        
        # Simple keyword-based matching
        query_lower = query.lower()
        matched_agents = []
        
        for agent_info in self.available_agents.values():
            score = 0
            
            # Check description
            if any(word in agent_info.description.lower() for word in query_lower.split()):
                score += 2
            
            # Check skills
            for skill in agent_info.card.skills:
                if any(word in skill.description.lower() for word in query_lower.split()):
                    score += 3
                if any(word in skill.name.lower() for word in query_lower.split()):
                    score += 2
            
            # Check tags
            if tags:
                common_tags = set(tags) & set(agent_info.card.tags)
                score += len(common_tags) * 2
            
            if score > 0:
                matched_agents.append((score, agent_info))
        
        # Sort by score and return top results
        matched_agents.sort(key=lambda x: x[0], reverse=True)
        return [agent_info for _, agent_info in matched_agents[:max_results]]
    
    async def create_orchestration_plan(
        self,
        session_id: str,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationPlan:
        """
        Create an orchestration plan for a user query
        
        This analyzes the query and determines which agents to involve
        and in what order.
        """
        
        # Discover suitable agents
        discovered_agents = await self.discover_agents(user_query, max_results=3)
        
        # Create orchestration steps (simplified logic)
        steps = []
        selected_agents = []
        
        for agent_info in discovered_agents:
            steps.append({
                "agent": agent_info.name,
                "action": "process_query",
                "query": user_query,
                "dependencies": []  # No dependencies for simple parallel execution
            })
            selected_agents.append(agent_info.name)
        
        # If no specific agents found, use general agent
        if not selected_agents and "GeneralAIAgent" in self.available_agents:
            steps.append({
                "agent": "GeneralAIAgent",
                "action": "process_query", 
                "query": user_query,
                "dependencies": []
            })
            selected_agents.append("GeneralAIAgent")
        
        plan = OrchestrationPlan(
            session_id=session_id,
            query=user_query,
            steps=steps,
            selected_agents=selected_agents,
            dependencies={},  # Simplified - no dependencies
            estimated_duration=len(steps) * 5.0  # Rough estimate
        )
        
        self.orchestration_plans[plan.id] = plan
        logger.info(f"Created orchestration plan {plan.id} with {len(selected_agents)} agents")
        
        return plan
    
    async def execute_orchestration_plan(
        self,
        plan: OrchestrationPlan,
        stream: bool = False
    ):
        """Execute an orchestration plan"""
        
        start_time = datetime.utcnow()
        results = []
        
        # Create session context
        context = OrchestrationContext(
            session_id=plan.session_id,
            user_query=plan.query,
            available_agents=list(self.available_agents.values())
        )
        self.active_sessions[plan.session_id] = context
        
        try:
            if stream:
                # For streaming, we'll yield results as they come
                async for result in self._execute_plan_streaming(plan, context):
                    yield result
                return  # End generator
            else:
                # Execute steps (simplified parallel execution)
                tasks = []
                for step in plan.steps:
                    agent_name = step["agent"]
                    query = step["query"]
                    
                    if agent_name in self.available_agents:
                        message = self.remote_agents.create_text_message(
                            text=query,
                            context_id=plan.session_id
                        )
                        
                        task = self.remote_agents.send_message_to_agent(
                            agent_name=agent_name,
                            message=message,
                            session_id=plan.session_id,
                            context_id=plan.session_id
                        )
                        tasks.append((agent_name, task))
                
                # Wait for all tasks to complete
                for agent_name, task_coroutine in tasks:
                    try:
                        task_result = await task_coroutine
                        results.append(task_result)
                        context.active_tasks[task_result.id] = task_result
                        
                    except Exception as e:
                        logger.error(f"Error executing task with {agent_name}: {e}")
                        # Create error task
                        from ..models.a2a_models import A2ATaskStatus
                        error_task = A2ATask(
                            id=f"error_{agent_name}_{uuid.uuid4()}",
                            status=A2ATaskStatus(state=TaskState.failed, error=str(e))
                        )
                        results.append(error_task)
                
                # Create summary
                summary = await self._create_summary(results, plan.query)
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Determine overall status
                failed_tasks = [r for r in results if r.status.state == TaskState.failed]
                completed_tasks = [r for r in results if r.status.state == TaskState.completed]
                
                if len(completed_tasks) > 0:
                    overall_status = TaskState.completed
                elif len(failed_tasks) == len(results):
                    overall_status = TaskState.failed
                else:
                    overall_status = TaskState.completed  # Partial success
                
                result = OrchestrationResult(
                    plan_id=plan.id,
                    session_id=plan.session_id,
                    status=overall_status,
                    results=results,
                    summary=summary,
                    execution_time=execution_time
                )
                
                yield result  # Return as generator for consistency
                
        finally:
            # Clean up session
            if plan.session_id in self.active_sessions:
                del self.active_sessions[plan.session_id]
    
    async def _execute_plan_streaming(self, plan: OrchestrationPlan, context: OrchestrationContext):
        """Execute plan with streaming results"""
        
        for step in plan.steps:
            agent_name = step["agent"]
            query = step["query"]
            
            if agent_name in self.available_agents:
                message = self.remote_agents.create_text_message(
                    text=query,
                    context_id=plan.session_id
                )
                
                try:
                    async for chunk in self.remote_agents.send_message_to_agent(
                        agent_name=agent_name,
                        message=message,
                        session_id=plan.session_id,
                        context_id=plan.session_id,
                        stream=True
                    ):
                        yield {
                            "agent": agent_name,
                            "type": "chunk",
                            "data": chunk
                        }
                        
                except Exception as e:
                    yield {
                        "agent": agent_name,
                        "type": "error",
                        "error": str(e)
                    }
    
    async def _create_summary(self, results: List[A2ATask], original_query: str) -> str:
        """Create a summary of orchestration results"""
        
        # This is a simplified summary generation
        # In production, use Gemini or another LLM to create intelligent summaries
        
        completed_results = [r for r in results if r.status.state == TaskState.completed]
        failed_results = [r for r in results if r.status.state == TaskState.failed]
        
        summary_parts = []
        summary_parts.append(f"Query: {original_query}")
        summary_parts.append(f"Executed {len(results)} tasks")
        summary_parts.append(f"Completed: {len(completed_results)}")
        
        if failed_results:
            summary_parts.append(f"Failed: {len(failed_results)}")
        
        # Add result content (simplified)
        for result in completed_results[:3]:  # Show up to 3 results
            if result.status.message and result.status.message.parts:
                for part in result.status.message.parts:
                    if part.type == A2APartType.text and part.text:
                        summary_parts.append(f"Result: {part.text[:100]}...")
                        break
        
        return "\n".join(summary_parts)
    
    async def handle_user_message(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        context_id: Optional[str] = None,
        stream: bool = False
    ):
        """
        Handle a user message with full orchestration
        
        This is the main entry point for processing user requests.
        """
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Create orchestration plan
            plan = await self.create_orchestration_plan(
                session_id=session_id,
                user_query=user_query
            )
            
            # Execute plan
            async for result in self.execute_orchestration_plan(plan, stream=stream):
                if stream:
                    yield result
                else:
                    # For non-streaming, return the final result
                    yield result
                    return
                
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            raise Exception(f"Orchestration failed: {e}")
    
    async def add_remote_agent(self, agent_url: str) -> A2AAgentCard:
        """Add a new remote agent"""
        
        agent_card = await self.remote_agents.add_agent(agent_url)
        agent_info = RemoteAgentInfo(
            name=agent_card.name,
            description=agent_card.description,
            url=agent_card.url,
            card=agent_card,
            status="active"
        )
        self.available_agents[agent_card.name] = agent_info
        
        return agent_card
    
    async def remove_remote_agent(self, agent_name: str):
        """Remove a remote agent"""
        
        await self.remote_agents.remove_agent(agent_name)
        if agent_name in self.available_agents:
            del self.available_agents[agent_name]
    
    async def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        
        return [
            {
                "name": info.name,
                "description": info.description,
                "url": info.url,
                "status": info.status,
                "last_seen": info.last_seen.isoformat(),
                "capabilities": info.card.capabilities.model_dump(),
                "skills": [skill.model_dump() for skill in info.card.skills],
                "tags": info.card.tags
            }
            for info in self.available_agents.values()
        ]
    
    async def health_check_agents(self) -> Dict[str, bool]:
        """Health check all connected agents"""
        
        return await self.remote_agents.health_check_all()
    
    def get_session_context(self, session_id: str) -> Optional[OrchestrationContext]:
        """Get session context"""
        
        return self.active_sessions.get(session_id)
    
    def list_active_sessions(self) -> List[str]:
        """List active session IDs"""
        
        return list(self.active_sessions.keys())
