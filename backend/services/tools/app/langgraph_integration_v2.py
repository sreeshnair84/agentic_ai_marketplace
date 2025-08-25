"""
Langgraph Integration for RAG System
Comprehensive integration of RAG functionality with Langgraph workflows
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union, TypedDict
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Langgraph imports
try:
    from langgraph import StateGraph, END
    from langgraph.graph import Graph
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    from langgraph.prebuilt.chat_agent_executor import create_chat_agent_executor
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("Langgraph not available. Install with: pip install langgraph")

# LangChain imports
from langchain.tools import BaseTool, Tool
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.callbacks.manager import CallbackManagerForToolRun

# Internal imports
from .services.enhanced_rag_service_v2 import EnhancedRAGServiceV2, RAGConfiguration
from .tool_implementations.rag.langgraph_rag_tool import (
    LanggraphRAGTool, LanggraphRAGUploadTool, RAGAgentState, create_rag_tools
)

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of RAG workflows available"""
    SIMPLE_QA = "simple_qa"
    RESEARCH = "research"
    DOCUMENT_ANALYSIS = "document_analysis"
    MULTI_PIPELINE = "multi_pipeline"
    CONVERSATIONAL = "conversational"

class AgentState(TypedDict):
    """State for Langgraph RAG agents"""
    messages: List[BaseMessage]
    pipeline_id: Optional[str]
    search_results: List[Dict[str, Any]]
    documents_processed: List[Dict[str, Any]]
    context: str
    current_step: str
    tools_used: List[str]
    intermediate_results: List[Dict[str, Any]]
    final_response: str
    metadata: Dict[str, Any]

@dataclass
class RAGWorkflowConfig:
    """Configuration for RAG workflows"""
    name: str
    description: str
    workflow_type: WorkflowType
    pipeline_ids: List[str]
    llm_model_id: Optional[str] = None
    max_search_results: int = 10
    enable_multi_turn: bool = True
    enable_document_upload: bool = True
    enable_pipeline_creation: bool = False
    system_prompt: Optional[str] = None
    custom_instructions: List[str] = None

class LanggraphRAGIntegration:
    """Main integration class for RAG and Langgraph"""
    
    def __init__(self, rag_service: EnhancedRAGServiceV2):
        self.rag_service = rag_service
        self.active_workflows: Dict[str, Graph] = {}
        self.active_configs: Dict[str, RAGWorkflowConfig] = {}
        self.logger = logger
        
        if not LANGGRAPH_AVAILABLE:
            raise RuntimeError("Langgraph is not available. Please install langgraph package.")
    
    async def create_simple_qa_workflow(
        self, 
        config: RAGWorkflowConfig
    ) -> Graph:
        """Create a simple Q&A workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Define nodes
        async def parse_question_node(state: AgentState) -> AgentState:
            """Parse and understand the user's question"""
            
            if not state["messages"]:
                state["final_response"] = "No question provided"
                return state
            
            last_message = state["messages"][-1]
            if isinstance(last_message, HumanMessage):
                question = last_message.content
                state["current_step"] = "question_parsed"
                state["metadata"]["original_question"] = question
                
                # Simple intent detection
                if "upload" in question.lower() or "add document" in question.lower():
                    state["metadata"]["intent"] = "upload"
                else:
                    state["metadata"]["intent"] = "search"
            
            return state
        
        async def search_knowledge_base_node(state: AgentState) -> AgentState:
            """Search the RAG knowledge base"""
            
            try:
                last_message = state["messages"][-1]
                query = last_message.content if isinstance(last_message, HumanMessage) else ""
                
                if not query or state["metadata"].get("intent") == "upload":
                    return state
                
                # Use the first available pipeline
                pipeline_id = config.pipeline_ids[0] if config.pipeline_ids else None
                if not pipeline_id:
                    state["final_response"] = "No RAG pipeline configured"
                    return state
                
                # Perform search
                results = await self.rag_service.search_pipeline(
                    pipeline_id=pipeline_id,
                    query=query,
                    k=config.max_search_results
                )
                
                state["search_results"] = results
                state["tools_used"].append("rag_search")
                state["current_step"] = "search_completed"
                
                # Build context from results
                context_parts = []
                for i, result in enumerate(results[:5]):  # Top 5 results
                    source = result.get("metadata", {}).get("filename", "Unknown")
                    content = result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"]
                    context_parts.append(f"Source {i+1} ({source}): {content}")
                
                state["context"] = "\n\n".join(context_parts)
                
            except Exception as e:
                self.logger.error(f"Error in search node: {e}")
                state["final_response"] = f"Search failed: {str(e)}"
                
            return state
        
        async def generate_answer_node(state: AgentState) -> AgentState:
            """Generate the final answer based on search results"""
            
            try:
                if state["metadata"].get("intent") == "upload":
                    state["final_response"] = "I can help you upload documents. Please provide the file path and I'll process it for you."
                    return state
                
                if not state["context"]:
                    state["final_response"] = "I couldn't find relevant information to answer your question."
                    return state
                
                # Create a comprehensive response
                last_message = state["messages"][-1]
                question = last_message.content if isinstance(last_message, HumanMessage) else ""
                
                response = f"Based on my search through the knowledge base, here's what I found:\n\n"
                response += state["context"]
                response += f"\n\nThis information comes from {len(state['search_results'])} relevant documents in the knowledge base."
                
                state["final_response"] = response
                state["current_step"] = "answer_generated"
                
            except Exception as e:
                self.logger.error(f"Error in answer generation: {e}")
                state["final_response"] = f"Failed to generate answer: {str(e)}"
            
            return state
        
        # Add nodes to workflow
        workflow.add_node("parse_question", parse_question_node)
        workflow.add_node("search_knowledge_base", search_knowledge_base_node)
        workflow.add_node("generate_answer", generate_answer_node)
        
        # Define edges
        workflow.add_edge("parse_question", "search_knowledge_base")
        workflow.add_edge("search_knowledge_base", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        # Set entry point
        workflow.set_entry_point("parse_question")
        
        # Compile and return
        compiled_workflow = workflow.compile()
        return compiled_workflow
    
    async def register_workflow(
        self,
        workflow_id: str,
        config: RAGWorkflowConfig
    ) -> str:
        """Register a new RAG workflow"""
        
        try:
            if config.workflow_type == WorkflowType.SIMPLE_QA:
                workflow = await self.create_simple_qa_workflow(config)
            else:
                raise ValueError(f"Unsupported workflow type: {config.workflow_type}")
            
            self.active_workflows[workflow_id] = workflow
            self.active_configs[workflow_id] = config
            
            self.logger.info(f"Registered RAG workflow {workflow_id} of type {config.workflow_type}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to register workflow {workflow_id}: {e}")
            raise
    
    async def execute_workflow(
        self,
        workflow_id: str,
        user_message: str,
        conversation_history: Optional[List[BaseMessage]] = None
    ) -> str:
        """Execute a registered workflow"""
        
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        config = self.active_configs[workflow_id]
        
        # Prepare initial state
        messages = conversation_history or []
        messages.append(HumanMessage(content=user_message))
        
        initial_state: AgentState = {
            "messages": messages,
            "pipeline_id": config.pipeline_ids[0] if config.pipeline_ids else None,
            "search_results": [],
            "documents_processed": [],
            "context": "",
            "current_step": "initialized",
            "tools_used": [],
            "intermediate_results": [],
            "final_response": "",
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_type": config.workflow_type.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        try:
            # Execute workflow
            result = await workflow.ainvoke(initial_state)
            
            self.logger.info(f"Workflow {workflow_id} executed successfully")
            return result["final_response"]
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            self.logger.error(f"Error executing workflow {workflow_id}: {e}")
            return error_msg
    
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """List all registered workflows"""
        
        workflow_info = {}
        for workflow_id, config in self.active_configs.items():
            workflow_info[workflow_id] = {
                "name": config.name,
                "description": config.description,
                "type": config.workflow_type.value,
                "pipeline_ids": config.pipeline_ids,
                "llm_model_id": config.llm_model_id,
                "capabilities": {
                    "multi_turn": config.enable_multi_turn,
                    "document_upload": config.enable_document_upload,
                    "pipeline_creation": config.enable_pipeline_creation
                }
            }
        
        return workflow_info

# Utility functions for easy integration
async def create_default_rag_integration(database_url: str) -> LanggraphRAGIntegration:
    """Create a default RAG integration with common workflows"""
    
    # Initialize RAG service
    rag_service = EnhancedRAGServiceV2()
    await rag_service.initialize(database_url)
    
    # Create integration
    integration = LanggraphRAGIntegration(rag_service)
    
    # Register default workflows
    await integration.register_workflow(
        "simple-qa",
        RAGWorkflowConfig(
            name="Simple Q&A",
            description="Simple question-answering using RAG",
            workflow_type=WorkflowType.SIMPLE_QA,
            pipeline_ids=["default-pipeline"]
        )
    )
    
    return integration

# Example usage
async def example_usage():
    """Example of how to use the Langgraph RAG integration"""
    
    try:
        # Create integration
        integration = await create_default_rag_integration("postgresql://user:pass@localhost/db")
        
        # Execute workflows
        response1 = await integration.execute_workflow(
            "simple-qa",
            "What is machine learning?"
        )
        print(f"Q&A Response: {response1}")
        
        # List workflows
        workflows = integration.list_workflows()
        print(f"Available workflows: {json.dumps(workflows, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if LANGGRAPH_AVAILABLE:
        asyncio.run(example_usage())
    else:
        print("Langgraph not available. Please install langgraph package.")