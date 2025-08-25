"""
A2A Agent Service
Implements A2A-compatible agents using LangGraph following the patterns from a2a-samples
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from a2a_sdk import AgentCard, AgentSkill, DefaultRequestHandler
    from langgraph.prebuilt import create_react_agent
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.language_models import BaseLanguageModel
    A2A_AVAILABLE = True
except ImportError as e:
    A2A_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"A2A SDK not available: {e}")
    
    # Mock classes for when A2A/LangChain is not available
    class BaseLanguageModel:
        pass
    
    class BaseMessage:
        pass
        
    class HumanMessage(BaseMessage):
        def __init__(self, content):
            self.content = content
            
    class AIMessage(BaseMessage):
        def __init__(self, content):
            self.content = content
            
    class SystemMessage(BaseMessage):
        def __init__(self, content):
            self.content = content

from .langgraph_model_service import LangGraphModelService
from .dynamic_tool_loader import get_dynamic_tool_loader
from ..core.database import get_database
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AgentState(str, Enum):
    """Agent execution states"""
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentResponse:
    """Standard agent response structure"""
    state: AgentState
    message: str
    data: Optional[Dict[str, Any]] = None
    requires_input: bool = False
    error: Optional[str] = None

class A2AAgentBase:
    """Base class for A2A-compatible agents"""
    
    def __init__(self, agent_id: str, name: str, description: str, llm_model: BaseLanguageModel, capabilities: List[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.llm_model = llm_model
        self.capabilities = capabilities or []
        self.memory = MemorySaver() if A2A_AVAILABLE else None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangGraph agent"""
        if not A2A_AVAILABLE:
            logger.warning("A2A not available, using mock agent")
            return
        
        # Schedule async initialization
        asyncio.create_task(self._async_initialize())
    
    async def _async_initialize(self):
        """Async initialization for loading tools"""
        try:
            # Get agent tools (including dynamic tools from capabilities)
            tools = await self._get_tools()
            
            # Create the agent with LangGraph
            self.agent = create_react_agent(
                model=self.llm_model,
                tools=tools,
                checkpointer=self.memory,
                system_prompt=self._get_system_prompt()
            )
            
            logger.info(f"Initialized A2A agent: {self.agent_id} with {len(tools)} tools")
            
        except Exception as e:
            logger.error(f"Error initializing agent {self.agent_id}: {str(e)}")
            self.agent = None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return f"""You are {self.name}, an AI assistant.

{self.description}

Instructions:
- Be helpful and accurate in your responses
- Use available tools when needed to provide better assistance
- If you need additional information from the user, clearly state what you need
- Provide clear, concise responses
- When a task is completed, summarize what was accomplished
"""
    
    async def _get_tools(self) -> List:
        """Get the tools available to this agent including dynamic tools from capabilities"""
        tools = []
        
        # Add basic tools
        tools.extend(self._get_basic_tools())
        
        # Load dynamic tools based on capabilities
        if self.capabilities:
            try:
                tool_loader = get_dynamic_tool_loader()
                dynamic_tools = await tool_loader.load_tools_for_agent(self.capabilities)
                tools.extend(dynamic_tools)
                logger.info(f"Loaded {len(dynamic_tools)} dynamic tools for agent {self.agent_id}")
            except Exception as e:
                logger.error(f"Failed to load dynamic tools for agent {self.agent_id}: {str(e)}")
        
        return tools
    
    def _get_basic_tools(self) -> List:
        """Get basic tools available to all agents (override in subclasses)"""
        return []
    
    async def execute(self, message: str, thread_id: str = "default") -> AsyncGenerator[AgentResponse, None]:
        """Execute the agent with a message and stream responses"""
        if not self.agent:
            yield AgentResponse(
                state=AgentState.ERROR,
                message="Agent not properly initialized",
                error="Agent initialization failed"
            )
            return
        
        try:
            yield AgentResponse(
                state=AgentState.WORKING,
                message="Processing your request..."
            )
            
            # Create config for the agent
            config = {"configurable": {"thread_id": thread_id}}
            
            # Stream the agent execution
            async for chunk in self.agent.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config
            ):
                # Process agent responses
                if "agent" in chunk:
                    agent_message = chunk["agent"]["messages"][-1]
                    if hasattr(agent_message, "content") and agent_message.content:
                        yield AgentResponse(
                            state=AgentState.WORKING,
                            message=agent_message.content
                        )
                
                # Process tool calls
                if "tools" in chunk:
                    for tool_call in chunk["tools"]["messages"]:
                        if hasattr(tool_call, "content"):
                            yield AgentResponse(
                                state=AgentState.WORKING,
                                message=f"Using tool: {tool_call.content}"
                            )
            
            # Final completion message
            yield AgentResponse(
                state=AgentState.COMPLETED,
                message="Task completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error executing agent {self.agent_id}: {str(e)}")
            yield AgentResponse(
                state=AgentState.ERROR,
                message=f"Error during execution: {str(e)}",
                error=str(e)
            )

class GeneralAssistantAgent(A2AAgentBase):
    """General purpose assistant agent"""
    
    def __init__(self, llm_model: BaseLanguageModel, capabilities: List[str] = None):
        super().__init__(
            agent_id="general_assistant",
            name="General Assistant",
            description="A helpful AI assistant that can answer questions and help with various tasks.",
            llm_model=llm_model,
            capabilities=capabilities
        )
    
    def _get_basic_tools(self) -> List:
        """Get tools for the general assistant"""
        return [
            self._get_current_time_tool(),
            self._get_calculation_tool()
        ]
    
    def _get_current_time_tool(self):
        """Tool to get current time"""
        @tool
        def get_current_time() -> str:
            """Get the current date and time."""
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return get_current_time
    
    def _get_calculation_tool(self):
        """Tool for basic calculations"""
        @tool
        def calculate(expression: str) -> str:
            """Perform basic mathematical calculations. Use this for math problems.
            
            Args:
                expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
            """
            try:
                # Simple and safe evaluation for basic math
                allowed_chars = set("0123456789+-*/(). ")
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    return f"Result: {result}"
                else:
                    return "Error: Invalid characters in expression"
            except Exception as e:
                return f"Error calculating: {str(e)}"
        
        return calculate

class DataAnalysisAgent(A2AAgentBase):
    """Data analysis focused agent"""
    
    def __init__(self, llm_model: BaseLanguageModel, capabilities: List[str] = None):
        super().__init__(
            agent_id="data_analyst",
            name="Data Analyst",
            description="An AI agent specialized in data analysis, statistics, and providing insights from data.",
            llm_model=llm_model,
            capabilities=capabilities
        )
    
    def _get_basic_tools(self) -> List:
        """Get tools for data analysis"""
        return [
            self._get_data_summary_tool(),
            self._get_statistics_tool()
        ]
    
    def _get_data_summary_tool(self):
        """Tool to analyze data"""
        @tool
        def analyze_data_summary(data_description: str) -> str:
            """Analyze and summarize data based on description.
            
            Args:
                data_description: Description of the data to analyze
            """
            return f"Analysis of {data_description}: This appears to be a request for data analysis. I would need the actual data to provide specific insights."
        
        return analyze_data_summary
    
    def _get_statistics_tool(self):
        """Tool for statistical operations"""
        @tool
        def calculate_statistics(numbers: str) -> str:
            """Calculate basic statistics for a list of numbers.
            
            Args:
                numbers: Comma-separated list of numbers
            """
            try:
                num_list = [float(x.strip()) for x in numbers.split(",")]
                mean = sum(num_list) / len(num_list)
                sorted_nums = sorted(num_list)
                median = sorted_nums[len(sorted_nums)//2]
                return f"Mean: {mean:.2f}, Median: {median:.2f}, Count: {len(num_list)}"
            except Exception as e:
                return f"Error calculating statistics: {str(e)}"
        
        return calculate_statistics

class DatabaseAgent(A2AAgentBase):
    """Agent loaded from database configuration with dynamic capabilities"""
    
    def __init__(self, agent_id: str, name: str, description: str, llm_model: BaseLanguageModel, 
                 capabilities: List[str] = None, system_prompt: str = None, 
                 temperature: float = None, max_tokens: int = None,
                 a2a_address: str = None, url: str = None):
        self.system_prompt_override = system_prompt
        self.temperature_override = temperature
        self.max_tokens_override = max_tokens
        self.a2a_address = a2a_address
        self.url = url
        
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            llm_model=llm_model,
            capabilities=capabilities or []
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt with override support"""
        if self.system_prompt_override:
            return self.system_prompt_override
        
        return f"""You are {self.name}, an AI assistant.

{self.description}

Your available tools and capabilities: {', '.join(self.capabilities) if self.capabilities else 'basic conversation'}

Instructions:
- Be helpful and accurate in your responses
- Use available tools when needed to provide better assistance
- If you need additional information from the user, clearly state what you need
- Provide clear, concise responses
- When a task is completed, summarize what was accomplished
"""
    
    def _get_basic_tools(self) -> List:
        """Database agents don't have predefined basic tools"""
        return []

class A2AAgentService:
    """Service for managing A2A-compatible agents"""
    
    def __init__(self, model_service: LangGraphModelService):
        self.model_service = model_service
        self.agents: Dict[str, A2AAgentBase] = {}
        self.agent_cards: Dict[str, Any] = {}
        
        if not A2A_AVAILABLE:
            logger.warning("A2A SDK not available, using mock implementation")
        
        logger.info("A2A Agent Service initialized")
    
    async def initialize_default_agents(self):
        """Initialize default agents with available models"""
        try:
            # Get default LLM model
            default_llm = await self.model_service.get_default_llm()
            if not default_llm:
                logger.warning("No default LLM configured, cannot initialize agents")
                return
            
            llm_instance = await self.model_service.get_model_instance(
                self.model_service.default_llm_id
            )
            
            if not llm_instance:
                logger.warning("Could not get LLM instance for agents")
                return
            
            # Initialize default agents
            await self._create_agent("general_assistant", GeneralAssistantAgent, llm_instance)
            await self._create_agent("data_analyst", DataAnalysisAgent, llm_instance)
            
            # Load database agents
            await self._load_database_agents()
            
            logger.info(f"Initialized {len(self.agents)} total agents")
            
        except Exception as e:
            logger.error(f"Error initializing default agents: {str(e)}")
    
    async def _load_database_agents(self):
        """Load agents from database with their configured capabilities"""
        try:
            async for db in get_database():
                # Get agents with a2a_enabled from database
                result = await db.execute(
                    text("""
                        SELECT id, name, display_name, description, capabilities, 
                               system_prompt, llm_model_id, temperature, max_tokens,
                               a2a_enabled, a2a_address, url
                        FROM agents 
                        WHERE status = 'active' AND a2a_enabled = true
                    """)
                )
                
                agents_data = result.fetchall()
                
                for agent_data in agents_data:
                    try:
                        # Parse capabilities from database
                        capabilities = []
                        if agent_data.capabilities:
                            if isinstance(agent_data.capabilities, str):
                                capabilities = json.loads(agent_data.capabilities)
                            elif isinstance(agent_data.capabilities, list):
                                capabilities = agent_data.capabilities
                        
                        # Get appropriate LLM instance
                        llm_instance = await self.model_service.get_model_instance(
                            agent_data.llm_model_id or self.model_service.default_llm_id
                        )
                        
                        if not llm_instance:
                            logger.warning(f"Could not get LLM for agent {agent_data.id}")
                            continue
                        
                        # Create database agent
                        db_agent = DatabaseAgent(
                            agent_id=agent_data.id,
                            name=agent_data.display_name or agent_data.name,
                            description=agent_data.description or "Custom agent",
                            llm_model=llm_instance,
                            capabilities=capabilities,
                            system_prompt=agent_data.system_prompt,
                            temperature=agent_data.temperature,
                            max_tokens=agent_data.max_tokens,
                            a2a_address=agent_data.a2a_address,
                            url=agent_data.url
                        )
                        
                        self.agents[agent_data.id] = db_agent
                        
                        # Create agent card for A2A protocol
                        if A2A_AVAILABLE:
                            agent_card = self._create_agent_card(db_agent)
                            self.agent_cards[agent_data.id] = agent_card
                        
                        logger.info(f"Loaded database agent: {agent_data.id} with {len(capabilities)} capabilities")
                        
                    except Exception as e:
                        logger.error(f"Error loading agent {agent_data.id}: {str(e)}")
                        continue
                
                logger.info(f"Loaded {len(agents_data)} agents from database")
                break  # Exit the async generator
                
        except Exception as e:
            logger.error(f"Error loading database agents: {str(e)}")
    
    async def _create_agent(self, agent_id: str, agent_class: type, llm_instance: BaseLanguageModel):
        """Create and register an agent"""
        try:
            agent = agent_class(llm_instance)
            self.agents[agent_id] = agent
            
            # Create agent card for A2A protocol
            if A2A_AVAILABLE:
                agent_card = self._create_agent_card(agent)
                self.agent_cards[agent_id] = agent_card
            
            logger.info(f"Created agent: {agent_id}")
            
        except Exception as e:
            logger.error(f"Error creating agent {agent_id}: {str(e)}")
    
    def _create_agent_card(self, agent: A2AAgentBase) -> Dict[str, Any]:
        """Create an A2A agent card"""
        if not A2A_AVAILABLE:
            return {}
        
        try:
            # Create agent skills
            skills = [
                AgentSkill(
                    name=agent.name,
                    description=agent.description,
                    input_content_types=["text/plain"],
                    output_content_types=["text/plain"]
                )
            ]
            
            # Create agent card
            agent_card = AgentCard(
                agent_id=agent.agent_id,
                name=agent.name,
                description=agent.description,
                skills=skills,
                supports_streaming=True,
                supports_push_notifications=False
            )
            
            return agent_card
            
        except Exception as e:
            logger.error(f"Error creating agent card for {agent.agent_id}: {str(e)}")
            return {}
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        agent_list = []
        
        for agent_id, agent in self.agents.items():
            agent_info = {
                "id": agent_id,
                "name": agent.name,
                "description": agent.description,
                "status": "active" if agent.agent else "inactive",
                "capabilities": ["chat", "streaming"],
                "created_at": datetime.utcnow().isoformat()
            }
            agent_list.append(agent_info)
        
        return agent_list
    
    async def get_agent(self, agent_id: str) -> Optional[A2AAgentBase]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    async def execute_agent(
        self, 
        agent_id: str, 
        message: str, 
        thread_id: str = "default"
    ) -> AsyncGenerator[AgentResponse, None]:
        """Execute an agent with a message"""
        agent = await self.get_agent(agent_id)
        
        if not agent:
            yield AgentResponse(
                state=AgentState.ERROR,
                message=f"Agent {agent_id} not found",
                error="Agent not found"
            )
            return
        
        async for response in agent.execute(message, thread_id):
            yield response
    
    async def chat_with_default_agent(
        self, 
        message: str, 
        thread_id: str = "default"
    ) -> AsyncGenerator[AgentResponse, None]:
        """Chat with the default general assistant agent"""
        # Use general assistant as default
        default_agent_id = "general_assistant"
        
        if default_agent_id not in self.agents:
            # Try to initialize if not available
            await self.initialize_default_agents()
        
        async for response in self.execute_agent(default_agent_id, message, thread_id):
            yield response
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the agent service"""
        return {
            "status": "healthy",
            "a2a_available": A2A_AVAILABLE,
            "agents_count": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.agent is not None]),
            "default_llm_configured": self.model_service.default_llm_id is not None,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global A2A agent service instance
_a2a_agent_service: Optional[A2AAgentService] = None

async def get_a2a_agent_service() -> A2AAgentService:
    """Get A2A agent service instance"""
    global _a2a_agent_service
    if _a2a_agent_service is None:
        from .langgraph_model_service import LangGraphModelService
        # This would need to be injected properly
        logger.warning("Model service not provided, creating new instance")
        model_service = LangGraphModelService(None)  # This needs proper DB session
        _a2a_agent_service = A2AAgentService(model_service)
        await _a2a_agent_service.initialize_default_agents()
    return _a2a_agent_service