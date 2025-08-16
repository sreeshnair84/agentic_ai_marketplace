"""
Agent service implementation with Gemini integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import logging
import uuid

from ..core.database import Agent, AgentExecution, AgentSession, A2AMessage, AgentStatus, AgentType, AIProvider
from ..core.config import get_settings
from .gemini_service import gemini_service

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agents and their execution"""
    
    def __init__(self):
        self.settings = get_settings()
        self.running_executions: Dict[str, asyncio.Task] = {}
    
    async def list_agents(
        self,
        db: AsyncSession,
        status: Optional[AgentStatus] = None,
        agent_type: Optional[AgentType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Agent]:
        """List agents with optional filtering"""
        
        query = select(Agent)
        
        if status:
            query = query.where(Agent.status == status)
        if agent_type:
            query = query.where(Agent.agent_type == agent_type)
        
        query = query.limit(limit).offset(offset).order_by(Agent.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_agent(self, db: AsyncSession, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()
    
    async def update_agent(
        self,
        db: AsyncSession,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        status: Optional[AgentStatus] = None
    ) -> Optional[Agent]:
        """Update agent"""
        
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            return None
        
        if name is not None:
            agent.name = name
        if description is not None:
            agent.description = description
        if config is not None:
            agent.model_config_data = config
        if status is not None:
            agent.status = status
        
        agent.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(agent)
        
        return agent
    
    async def delete_agent(self, db: AsyncSession, agent_id: str) -> bool:
        """Delete agent"""
        
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            return False
        
        await db.delete(agent)
        await db.commit()
        return True

    async def create_agent(
        self,
        db: AsyncSession,
        name: str,
        agent_type: AgentType,
        created_by: str,
        description: Optional[str] = None,
        ai_provider: AIProvider = AIProvider.GEMINI,
        model_name: str = "gemini-1.5-pro",
        system_prompt: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        model_config: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """Create a new agent"""
        
        # Default system prompt if not provided
        if not system_prompt:
            system_prompt = self._get_default_system_prompt(agent_type)
        
        # Default capabilities if not provided
        if not capabilities:
            capabilities = self._get_default_capabilities(agent_type)
        
        agent = Agent(
            name=name,
            description=description,
            agent_type=agent_type,
            ai_provider=ai_provider,
            model_name=model_name,
            model_config_data=model_config or {},
            capabilities=capabilities,
            system_prompt=system_prompt,
            created_by=created_by,
            status=AgentStatus.INACTIVE,
            a2a_address=f"agent://{uuid.uuid4().hex[:8]}"
        )
        
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"Created agent {agent.id}: {name} ({agent_type.value})")
        return agent
    
    async def execute_task(
        self,
        db: AsyncSession,
        agent_id: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> AgentExecution:
        """Execute a task with an agent"""
        
        # Get agent
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        if not agent.is_active:
            raise ValueError(f"Agent {agent_id} is not active")
        
        # Create execution record
        execution = AgentExecution(
            agent_id=agent_id,
            task_id=task_id,
            input_data=task_data,
            context=context or {},
            status="pending"
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Start execution asynchronously
        execution_task = asyncio.create_task(
            self._execute_task_async(db, execution.id, agent, task_data, context)
        )
        self.running_executions[execution.id] = execution_task
        
        logger.info(f"Started execution {execution.id} for agent {agent_id}")
        return execution
    
    async def _execute_task_async(
        self,
        db: AsyncSession,
        execution_id: str,
        agent: Agent,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        """Execute task asynchronously"""
        
        try:
            # Update execution status
            await self._update_execution_status(db, execution_id, "running", started_at=datetime.utcnow())
            
            # Update agent status
            await self._update_agent_status(db, agent.id, AgentStatus.BUSY)
            
            # Prepare prompt
            prompt = self._prepare_prompt(task_data, context or {})
            
            # Get conversation history if session exists
            conversation_history = None
            session_id = task_data.get("session_id")
            if session_id:
                conversation_history = await self._get_conversation_history(db, session_id)
            
            # Execute with appropriate AI provider
            if agent.ai_provider == AIProvider.GEMINI:
                result = await self._execute_with_gemini(agent, prompt, conversation_history)
            else:
                raise ValueError(f"Unsupported AI provider: {agent.ai_provider}")
            
            # Update session if exists
            if session_id:
                await self._update_session(db, session_id, prompt, result["content"])
            
            # Update execution as completed
            await self._update_execution_status(
                db,
                execution_id,
                "completed",
                output_data=result,
                completed_at=datetime.utcnow(),
                input_tokens=result.get("usage", {}).get("prompt_tokens", 0),
                output_tokens=result.get("usage", {}).get("completion_tokens", 0),
                total_cost=self._calculate_cost(result.get("usage", {}), agent.model_name)
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
            # Update agent status back to active
            await self._update_agent_status(db, agent.id, AgentStatus.ACTIVE)
            
            # Clean up
            self.running_executions.pop(execution_id, None)
    
    async def _execute_with_gemini(
        self,
        agent: Agent,
        prompt: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Execute task using Gemini"""
        
        return await gemini_service.generate_response(
            prompt=prompt,
            model_name=agent.model_name,
            system_prompt=agent.system_prompt,
            conversation_history=conversation_history,
            custom_config=agent.model_config
        )
    
    def _prepare_prompt(self, task_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Prepare prompt from task data and context"""
        
        prompt_parts = []
        
        # Add main task instruction
        if "instruction" in task_data:
            prompt_parts.append(f"Task: {task_data['instruction']}")
        
        # Add input data
        if "input" in task_data:
            prompt_parts.append(f"Input: {task_data['input']}")
        
        # Add context information
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            prompt_parts.append(f"Context:\n{context_str}")
        
        # Add any additional parameters
        for key, value in task_data.items():
            if key not in ["instruction", "input", "session_id"]:
                prompt_parts.append(f"{key}: {value}")
        
        return "\n\n".join(prompt_parts)
    
    async def create_session(
        self,
        db: AsyncSession,
        agent_id: str,
        user_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> AgentSession:
        """Create a new agent session"""
        
        # Check if agent exists
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        session = AgentSession(
            agent_id=agent_id,
            user_id=user_id,
            context=initial_context or {},
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24-hour session
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        return session
    
    async def send_a2a_message(
        self,
        db: AsyncSession,
        from_agent_id: str,
        to_agent_id: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> A2AMessage:
        """Send A2A (Agent-to-Agent) message"""
        
        message = A2AMessage(
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id,
            expires_at=datetime.utcnow() + timedelta(seconds=self.settings.A2A_MESSAGE_TTL_SECONDS)
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        # Process message asynchronously
        asyncio.create_task(self._process_a2a_message(db, message.id))
        
        return message
    
    async def _process_a2a_message(self, db: AsyncSession, message_id: str):
        """Process A2A message"""
        
        try:
            # Get message
            result = await db.execute(
                select(A2AMessage).where(A2AMessage.id == message_id)
            )
            message = result.scalar_one_or_none()
            
            if not message:
                return
            
            # Update message status
            message.status = "processing"
            message.sent_at = datetime.utcnow()
            await db.commit()
            
            # Get target agent
            result = await db.execute(
                select(Agent).where(Agent.id == message.to_agent_id)
            )
            target_agent = result.scalar_one_or_none()
            
            if not target_agent or not target_agent.a2a_enabled:
                message.status = "failed"
                message.error_message = "Target agent not available for A2A communication"
                await db.commit()
                return
            
            # Process based on message type
            if message.message_type == "task_request":
                await self._handle_a2a_task_request(db, message, target_agent)
            elif message.message_type == "collaboration_request":
                await self._handle_a2a_collaboration_request(db, message, target_agent)
            else:
                message.status = "failed"
                message.error_message = f"Unknown message type: {message.message_type}"
                await db.commit()
                return
            
            # Update message as processed
            message.status = "completed"
            message.processed_at = datetime.utcnow()
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error processing A2A message {message_id}: {e}")
            
            # Update message as failed
            if message:
                message.status = "failed"
                message.error_message = str(e)
                await db.commit()
    
    async def _handle_a2a_task_request(self, db: AsyncSession, message: A2AMessage, target_agent: Agent):
        """Handle A2A task request"""
        
        task_data = message.payload.get("task_data", {})
        context = message.payload.get("context", {})
        
        # Add A2A context
        context["a2a_request"] = True
        context["requesting_agent"] = message.from_agent_id
        context["correlation_id"] = message.correlation_id
        
        # Execute task
        await self.execute_task(
            db=db,
            agent_id=target_agent.id,
            task_data=task_data,
            context=context,
            task_id=f"a2a_{message.id}"
        )
    
    async def _handle_a2a_collaboration_request(self, db: AsyncSession, message: A2AMessage, target_agent: Agent):
        """Handle A2A collaboration request"""
        
        # Implementation for collaboration requests
        # This would involve setting up collaborative workflows
        logger.info(f"Collaboration request from {message.from_agent_id} to {target_agent.id}")
    
    def _get_default_system_prompt(self, agent_type: AgentType) -> str:
        """Get default system prompt for agent type"""
        
        prompts = {
            AgentType.CONVERSATIONAL: """You are a helpful conversational AI assistant. 
You engage in natural, helpful conversations with users. 
Provide clear, accurate, and contextually appropriate responses.""",
            
            AgentType.TASK_ORIENTED: """You are a task-oriented AI assistant focused on completing specific objectives.
You analyze tasks, break them down into steps, and execute them efficiently.
Always provide clear status updates and results.""",
            
            AgentType.REACTIVE: """You are a reactive AI agent that responds to specific triggers and events.
You monitor conditions and react appropriately when thresholds are met.
Provide timely and accurate responses to detected events.""",
            
            AgentType.PROACTIVE: """You are a proactive AI agent that anticipates needs and takes initiative.
You identify opportunities for improvement and suggest actionable recommendations.
Think ahead and provide valuable insights.""",
            
            AgentType.COLLABORATIVE: """You are a collaborative AI agent designed to work with other agents and systems.
You communicate effectively, share information appropriately, and coordinate actions.
Focus on teamwork and achieving collective goals."""
        }
        
        return prompts.get(agent_type, prompts[AgentType.CONVERSATIONAL])
    
    def _get_default_capabilities(self, agent_type: AgentType) -> List[str]:
        """Get default capabilities for agent type"""
        
        base_capabilities = ["text_generation", "conversation", "analysis"]
        
        type_capabilities = {
            AgentType.CONVERSATIONAL: ["dialogue_management", "context_awareness"],
            AgentType.TASK_ORIENTED: ["task_planning", "step_execution", "result_reporting"],
            AgentType.REACTIVE: ["event_monitoring", "trigger_detection", "alert_generation"],
            AgentType.PROACTIVE: ["pattern_recognition", "prediction", "recommendation"],
            AgentType.COLLABORATIVE: ["agent_communication", "coordination", "information_sharing"]
        }
        
        return base_capabilities + type_capabilities.get(agent_type, [])
    
    async def _get_conversation_history(self, db: AsyncSession, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history from session"""
        
        result = await db.execute(
            select(AgentSession).where(AgentSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session and session.conversation_history:
            return session.conversation_history
        
        return []
    
    async def _update_session(self, db: AsyncSession, session_id: str, user_message: str, agent_response: str):
        """Update session with new conversation turn"""
        
        result = await db.execute(
            select(AgentSession).where(AgentSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            if not session.conversation_history:
                session.conversation_history = []
            
            session.conversation_history.extend([
                {"role": "user", "content": user_message, "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "content": agent_response, "timestamp": datetime.utcnow().isoformat()}
            ])
            
            session.updated_at = datetime.utcnow()
            await db.commit()
    
    async def _update_execution_status(
        self,
        db: AsyncSession,
        execution_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_cost: Optional[float] = None
    ):
        """Update execution status"""
        
        update_data = {"status": status}
        
        if output_data is not None:
            update_data["output_data"] = output_data
        if error_message is not None:
            update_data["error_message"] = error_message
        if started_at is not None:
            update_data["started_at"] = started_at
        if completed_at is not None:
            update_data["completed_at"] = completed_at
        if input_tokens is not None:
            update_data["input_tokens"] = input_tokens
        if output_tokens is not None:
            update_data["output_tokens"] = output_tokens
        if total_cost is not None:
            update_data["total_cost"] = total_cost
        
        await db.execute(
            update(AgentExecution)
            .where(AgentExecution.id == execution_id)
            .values(**update_data)
        )
        await db.commit()
    
    async def _update_agent_status(self, db: AsyncSession, agent_id: str, status: AgentStatus):
        """Update agent status"""
        
        await db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(status=status)
        )
        await db.commit()
    
    def _calculate_cost(self, usage: Dict[str, Any], model_name: str) -> float:
        """Calculate cost based on token usage"""
        
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        
        return gemini_service.estimate_cost(input_tokens, output_tokens, model_name)


# Global agent service instance
agent_service = AgentService()
