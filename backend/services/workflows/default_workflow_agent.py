"""
Default Workflow Agent with LangGraph Plan and Execute Architecture
Implements intelligent workflow/agent/tool selection based on user queries
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime, timedelta
import logging

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

# Database and storage
import redis
import asyncpg
from pgvector.asyncpg import register_vector

# HTTP client for A2A communication
import httpx

# Configuration
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WorkflowConfig:
    """Configuration for the default workflow agent"""
    redis_url: str = "redis://localhost:6379"
    postgres_url: str = "postgresql://user:pass@localhost:5432/enterprise_ai"
    gateway_url: str = "http://localhost:8000"
    agents_url: str = "http://localhost:8002" 
    tools_url: str = "http://localhost:8001"
    default_llm_provider: str = "openai"
    memory_ttl_hours: int = 24
    max_execution_steps: int = 10

class AgentState(TypedDict):
    """State maintained throughout workflow execution"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    session_id: str
    execution_id: str
    available_workflows: List[Dict[str, Any]]
    available_agents: List[Dict[str, Any]]
    available_tools: List[Dict[str, Any]]
    selected_context: Dict[str, Any]
    execution_plan: List[Dict[str, Any]]
    current_step: int
    step_results: Dict[str, Any]
    short_term_memory: List[Dict[str, Any]]
    long_term_memory: List[Dict[str, Any]]
    error_messages: List[str]
    is_complete: bool
    final_response: str

class MemoryManager:
    """Manages short and long-term memory using Redis and PGVector"""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.redis_client = None
        self.postgres_pool = None
    
    async def initialize(self):
        """Initialize Redis and PostgreSQL connections"""
        try:
            # Redis for short-term memory and state
            self.redis_client = redis.from_url(self.config.redis_url, decode_responses=True)
            
            # PostgreSQL with PGVector for long-term memory
            self.postgres_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            
            # Register vector extension
            async with self.postgres_pool.acquire() as conn:
                await register_vector(conn)
                
                # Create memory tables if not exist
                await self._create_memory_tables(conn)
            
            logger.info("Memory manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory manager: {e}")
            raise
    
    async def _create_memory_tables(self, conn):
        """Create memory tables with vector support"""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_short_memory (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id TEXT NOT NULL,
                execution_id TEXT,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_short_memory_session 
            ON workflow_short_memory(session_id, created_at);
            
            CREATE INDEX IF NOT EXISTS idx_short_memory_embedding 
            ON workflow_short_memory USING ivfflat (embedding vector_cosine_ops);
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_long_memory (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id TEXT NOT NULL,
                user_id TEXT,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                embedding vector(1536),
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT NOW(),
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_long_memory_session 
            ON workflow_long_memory(session_id, last_accessed);
            
            CREATE INDEX IF NOT EXISTS idx_long_memory_embedding 
            ON workflow_long_memory USING ivfflat (embedding vector_cosine_ops);
        """)
    
    async def store_short_term_memory(
        self, 
        session_id: str, 
        execution_id: str,
        memory_type: str,
        content: str,
        metadata: Dict = None,
        ttl_hours: int = None
    ):
        """Store short-term memory with TTL"""
        try:
            # Store in Redis for fast access
            redis_key = f"short_memory:{session_id}:{execution_id}"
            memory_item = {
                "type": memory_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self.redis_client.lpush(redis_key, json.dumps(memory_item))
            await self.redis_client.expire(
                redis_key, 
                (ttl_hours or self.config.memory_ttl_hours) * 3600
            )
            
            # Also store in PostgreSQL for persistence
            expires_at = datetime.now() + timedelta(
                hours=ttl_hours or self.config.memory_ttl_hours
            )
            
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO workflow_short_memory 
                    (session_id, execution_id, memory_type, content, metadata, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, session_id, execution_id, memory_type, content, 
                    json.dumps(metadata or {}), expires_at)
            
            logger.debug(f"Stored short-term memory: {memory_type}")
            
        except Exception as e:
            logger.error(f"Failed to store short-term memory: {e}")
    
    async def get_short_term_memory(
        self, 
        session_id: str, 
        execution_id: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve short-term memory"""
        try:
            if execution_id:
                redis_key = f"short_memory:{session_id}:{execution_id}"
            else:
                # Get all for session
                redis_key = f"short_memory:{session_id}:*"
            
            # Try Redis first
            if execution_id:
                memory_items = await self.redis_client.lrange(redis_key, 0, limit-1)
                if memory_items:
                    return [json.loads(item) for item in memory_items]
            
            # Fallback to PostgreSQL
            async with self.postgres_pool.acquire() as conn:
                query = """
                    SELECT memory_type, content, metadata, created_at
                    FROM workflow_short_memory 
                    WHERE session_id = $1 
                    AND (expires_at IS NULL OR expires_at > NOW())
                """
                params = [session_id]
                
                if execution_id:
                    query += " AND execution_id = $2"
                    params.append(execution_id)
                
                query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1)
                params.append(limit)
                
                rows = await conn.fetch(query, *params)
                return [{
                    "type": row["memory_type"],
                    "content": row["content"],
                    "metadata": json.loads(row["metadata"]),
                    "timestamp": row["created_at"].isoformat()
                } for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get short-term memory: {e}")
            return []
    
    async def store_long_term_memory(
        self,
        session_id: str,
        memory_type: str,
        content: str,
        metadata: Dict = None,
        user_id: str = None
    ):
        """Store long-term memory with vector embedding"""
        try:
            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO workflow_long_memory 
                    (session_id, user_id, memory_type, content, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                """, session_id, user_id, memory_type, content, 
                    json.dumps(metadata or {}))
            
            logger.debug(f"Stored long-term memory: {memory_type}")
            
        except Exception as e:
            logger.error(f"Failed to store long-term memory: {e}")
    
    async def cleanup_expired_memory(self):
        """Clean up expired short-term memory"""
        try:
            async with self.postgres_pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM workflow_short_memory 
                    WHERE expires_at IS NOT NULL AND expires_at < NOW()
                """)
                logger.debug(f"Cleaned up {result} expired memory records")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired memory: {e}")

class MetadataFetcher:
    """Fetches available workflows, agents, and tools from gateway"""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def get_default_llm_model(self) -> Dict[str, Any]:
        """Get default LLM model from gateway"""
        try:
            response = await self.http_client.get(f"{self.config.gateway_url}/api/v1/tools/llm-models")
            if response.status_code == 200:
                models = response.json()
                # Find active model with preferred provider
                for model in models:
                    if (model.get("status") == "active" and 
                        model.get("provider", "").lower() == self.config.default_llm_provider):
                        return model
                
                # Fallback to any active model
                for model in models:
                    if model.get("status") == "active":
                        return model
                        
            logger.warning("No active LLM models found, using default configuration")
            return {
                "name": "default-gpt-4",
                "provider": "openai",
                "model_name": "gpt-4",
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch default LLM model: {e}")
            return {"name": "fallback", "provider": "openai", "model_name": "gpt-3.5-turbo"}
    
    async def get_metadata_options(self) -> Dict[str, List[Dict]]:
        """Get available workflows, agents, and tools"""
        try:
            response = await self.http_client.get(f"{self.config.gateway_url}/api/v1/metadata/chat-options")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("Failed to fetch metadata options")
                return {"workflows": [], "agents": [], "tools": []}
                
        except Exception as e:
            logger.error(f"Failed to fetch metadata options: {e}")
            return {"workflows": [], "agents": [], "tools": []}

class DefaultWorkflowAgent:
    """Main workflow agent implementing Plan and Execute pattern"""
    
    def __init__(self, config: WorkflowConfig = None):
        self.config = config or WorkflowConfig()
        self.memory_manager = MemoryManager(self.config)
        self.metadata_fetcher = MetadataFetcher(self.config)
        self.graph = None
        self.llm = None
        
    async def initialize(self):
        """Initialize the workflow agent"""
        await self.memory_manager.initialize()
        
        # Get default LLM model
        default_model = await self.metadata_fetcher.get_default_llm_model()
        logger.info(f"Using LLM model: {default_model}")
        
        # Initialize LLM (simplified - would use actual LangChain LLM)
        self.llm = default_model  # Placeholder
        
        # Build the LangGraph
        self.graph = self._build_plan_execute_graph()
        
    def _build_plan_execute_graph(self) -> StateGraph:
        """Build the Plan and Execute LangGraph"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("load_metadata", self._load_metadata_node)
        workflow.add_node("analyze_query", self._analyze_query_node)
        workflow.add_node("create_plan", self._create_plan_node)
        workflow.add_node("execute_step", self._execute_step_node)
        workflow.add_node("evaluate_result", self._evaluate_result_node)
        workflow.add_node("finalize_response", self._finalize_response_node)
        
        # Define edges
        workflow.add_edge(START, "load_metadata")
        workflow.add_edge("load_metadata", "analyze_query")
        workflow.add_edge("analyze_query", "create_plan")
        workflow.add_edge("create_plan", "execute_step")
        workflow.add_conditional_edges(
            "execute_step",
            self._should_continue_execution,
            {
                "continue": "evaluate_result",
                "complete": "finalize_response"
            }
        )
        workflow.add_edge("evaluate_result", "execute_step")
        workflow.add_edge("finalize_response", END)
        
        return workflow.compile()
    
    async def _load_metadata_node(self, state: AgentState) -> Dict[str, Any]:
        """Load available workflows, agents, and tools"""
        try:
            metadata = await self.metadata_fetcher.get_metadata_options()
            
            await self.memory_manager.store_short_term_memory(
                state["session_id"],
                state["execution_id"],
                "metadata_loaded",
                f"Loaded {len(metadata['workflows'])} workflows, {len(metadata['agents'])} agents, {len(metadata['tools'])} tools",
                {"counts": {k: len(v) for k, v in metadata.items()}}
            )
            
            return {
                "available_workflows": metadata.get("workflows", []),
                "available_agents": metadata.get("agents", []),
                "available_tools": metadata.get("tools", [])
            }
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {
                "available_workflows": [],
                "available_agents": [],
                "available_tools": [],
                "error_messages": [f"Failed to load metadata: {str(e)}"]
            }
    
    async def _analyze_query_node(self, state: AgentState) -> Dict[str, Any]:
        """Analyze user query to understand intent"""
        try:
            query = state["user_query"]
            
            # Simple intent analysis (would use LLM in real implementation)
            analysis = {
                "intent": "general_assistance",
                "entities": [],
                "complexity": "medium",
                "requires_tools": "tools" in query.lower(),
                "requires_agents": "agent" in query.lower(),
                "requires_workflow": "workflow" in query.lower()
            }
            
            await self.memory_manager.store_short_term_memory(
                state["session_id"],
                state["execution_id"],
                "query_analysis",
                f"Analyzed query: {query}",
                analysis
            )
            
            return {"query_analysis": analysis}
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {"error_messages": [f"Failed to analyze query: {str(e)}"]}
    
    async def _create_plan_node(self, state: AgentState) -> Dict[str, Any]:
        """Create execution plan based on query analysis"""
        try:
            # Simple planning logic (would use LLM for complex planning)
            plan = [
                {
                    "step": 1,
                    "action": "select_context",
                    "description": "Select appropriate workflow/agent/tools",
                    "status": "pending"
                },
                {
                    "step": 2,
                    "action": "execute_context",
                    "description": "Execute selected context",
                    "status": "pending"
                },
                {
                    "step": 3,
                    "action": "format_response",
                    "description": "Format final response",
                    "status": "pending"
                }
            ]
            
            await self.memory_manager.store_short_term_memory(
                state["session_id"],
                state["execution_id"],
                "execution_plan",
                f"Created plan with {len(plan)} steps",
                {"plan": plan}
            )
            
            return {"execution_plan": plan, "current_step": 0}
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return {"error_messages": [f"Failed to create plan: {str(e)}"]}
    
    async def _execute_step_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute current step in the plan"""
        try:
            current_step = state.get("current_step", 0)
            plan = state.get("execution_plan", [])
            
            if current_step >= len(plan):
                return {"is_complete": True}
            
            step = plan[current_step]
            step_result = await self._execute_plan_step(step, state)
            
            # Update step results
            step_results = state.get("step_results", {})
            step_results[f"step_{current_step}"] = step_result
            
            await self.memory_manager.store_short_term_memory(
                state["session_id"],
                state["execution_id"],
                f"step_{current_step}_result",
                f"Executed step {current_step}: {step['action']}",
                step_result
            )
            
            return {
                "step_results": step_results,
                "current_step": current_step + 1
            }
            
        except Exception as e:
            logger.error(f"Error executing step: {e}")
            return {"error_messages": [f"Failed to execute step: {str(e)}"]}
    
    async def _execute_plan_step(self, step: Dict, state: AgentState) -> Dict[str, Any]:
        """Execute a specific plan step"""
        action = step["action"]
        
        if action == "select_context":
            return await self._select_optimal_context(state)
        elif action == "execute_context":
            return await self._execute_selected_context(state)
        elif action == "format_response":
            return await self._format_final_response(state)
        else:
            return {"status": "unknown_action", "message": f"Unknown action: {action}"}
    
    async def _select_optimal_context(self, state: AgentState) -> Dict[str, Any]:
        """Select optimal workflow/agent/tools based on query"""
        try:
            query = state["user_query"]
            workflows = state.get("available_workflows", [])
            agents = state.get("available_agents", [])
            tools = state.get("available_tools", [])
            
            # Simple selection logic (would use LLM for intelligent selection)
            selected_context = {
                "type": "default",
                "workflow": None,
                "agent": None,
                "tools": []
            }
            
            # Basic keyword matching
            if "workflow" in query.lower() and workflows:
                selected_context["type"] = "workflow"
                selected_context["workflow"] = workflows[0]  # Select first available
            elif "agent" in query.lower() and agents:
                selected_context["type"] = "agent" 
                selected_context["agent"] = agents[0]  # Select first available
            elif tools:
                selected_context["type"] = "tools"
                selected_context["tools"] = tools[:3]  # Select first 3 tools
            
            return {
                "status": "success",
                "selected_context": selected_context,
                "message": f"Selected context type: {selected_context['type']}"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Context selection failed: {str(e)}"}
    
    async def _execute_selected_context(self, state: AgentState) -> Dict[str, Any]:
        """Execute the selected context via A2A protocol"""
        try:
            step_results = state.get("step_results", {})
            context_result = step_results.get("step_0", {})
            selected_context = context_result.get("selected_context", {})
            
            # Prepare A2A request
            a2a_request = {
                "jsonrpc": "2.0",
                "id": f"exec_{uuid.uuid4().hex[:8]}",
                "method": "message/stream",
                "params": {
                    "sessionId": state["session_id"],
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": state["user_query"]}]
                    },
                    "context": selected_context,
                    "accepted_output_modes": ["text", "json"]
                }
            }
            
            # Execute via appropriate endpoint (simplified)
            result = f"Executed {selected_context['type']} context for query: {state['user_query']}"
            
            return {
                "status": "success",
                "execution_result": result,
                "a2a_request": a2a_request
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Context execution failed: {str(e)}"}
    
    async def _format_final_response(self, state: AgentState) -> Dict[str, Any]:
        """Format the final response"""
        try:
            step_results = state.get("step_results", {})
            execution_result = step_results.get("step_1", {}).get("execution_result", "No result")
            
            final_response = f"Completed workflow execution: {execution_result}"
            
            # Store in long-term memory
            await self.memory_manager.store_long_term_memory(
                state["session_id"],
                "workflow_completion",
                final_response,
                {"query": state["user_query"], "execution_id": state["execution_id"]}
            )
            
            return {
                "status": "success",
                "final_response": final_response
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Response formatting failed: {str(e)}"}
    
    async def _evaluate_result_node(self, state: AgentState) -> Dict[str, Any]:
        """Evaluate if execution should continue"""
        try:
            current_step = state.get("current_step", 0)
            max_steps = self.config.max_execution_steps
            
            if current_step >= max_steps:
                return {"is_complete": True}
            
            # Check if there are any errors
            errors = state.get("error_messages", [])
            if errors:
                return {"is_complete": True, "has_errors": True}
            
            return {"continue_execution": True}
            
        except Exception as e:
            logger.error(f"Error evaluating result: {e}")
            return {"is_complete": True, "has_errors": True}
    
    async def _finalize_response_node(self, state: AgentState) -> Dict[str, Any]:
        """Finalize the workflow response"""
        try:
            step_results = state.get("step_results", {})
            final_step = step_results.get("step_2", {})
            final_response = final_step.get("final_response", "Workflow completed successfully")
            
            return {
                "final_response": final_response,
                "is_complete": True
            }
            
        except Exception as e:
            logger.error(f"Error finalizing response: {e}")
            return {
                "final_response": f"Workflow completed with errors: {str(e)}",
                "is_complete": True,
                "has_errors": True
            }
    
    def _should_continue_execution(self, state: AgentState) -> str:
        """Determine if execution should continue"""
        if state.get("is_complete", False):
            return "complete"
        
        current_step = state.get("current_step", 0)
        plan = state.get("execution_plan", [])
        
        if current_step >= len(plan):
            return "complete"
        
        return "continue"
    
    async def process_query(
        self, 
        user_query: str, 
        session_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user query through the Plan and Execute workflow"""
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=user_query)],
            user_query=user_query,
            session_id=session_id,
            execution_id=execution_id,
            available_workflows=[],
            available_agents=[],
            available_tools=[],
            selected_context=context or {},
            execution_plan=[],
            current_step=0,
            step_results={},
            short_term_memory=[],
            long_term_memory=[],
            error_messages=[],
            is_complete=False,
            final_response=""
        )
        
        try:
            # Execute the graph
            config = RunnableConfig(
                configurable={
                    "session_id": session_id,
                    "execution_id": execution_id
                }
            )
            
            final_state = await self.graph.ainvoke(initial_state, config)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "final_response": final_state.get("final_response", "No response generated"),
                "step_results": final_state.get("step_results", {}),
                "errors": final_state.get("error_messages", [])
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e),
                "final_response": f"Workflow execution failed: {str(e)}"
            }

# Export the main class
__all__ = ["DefaultWorkflowAgent", "WorkflowConfig", "MemoryManager"]