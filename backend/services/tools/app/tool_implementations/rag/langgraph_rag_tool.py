"""
Langgraph RAG Tool Implementation
Advanced RAG tool that integrates with Langgraph for agent-based workflows
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Langchain and Langgraph imports
from langchain.tools import BaseTool, Tool
from langchain.schema import Document
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel, Field

try:
    from langgraph import StateGraph, END
    from langgraph.graph import Graph
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    
from ...services.enhanced_rag_service_v2 import EnhancedRAGServiceV2

logger = logging.getLogger(__name__)

class RAGSearchInput(BaseModel):
    """Input schema for RAG search tool"""
    query: str = Field(description="The search query to find relevant documents")
    k: int = Field(default=5, description="Number of results to return")
    include_tables: bool = Field(default=True, description="Include table content in search")
    include_images: bool = Field(default=True, description="Include image descriptions in search")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity threshold for results")

class RAGUploadInput(BaseModel):
    """Input schema for document upload tool"""
    file_path: str = Field(description="Path to the file to upload")
    metadata: str = Field(default="{}", description="JSON string of metadata for the document")

class LanggraphRAGTool(BaseTool):
    """Advanced RAG tool for Langgraph integration"""
    
    name = "rag_search"
    description = "Search a RAG knowledge base for relevant documents and information"
    args_schema = RAGSearchInput
    
    def __init__(self, pipeline_id: str, rag_service: EnhancedRAGServiceV2, **kwargs):
        super().__init__(**kwargs)
        self.pipeline_id = pipeline_id
        self.rag_service = rag_service
        self.logger = logger
    
    async def _arun(
        self,
        query: str,
        k: int = 5,
        include_tables: bool = True,
        include_images: bool = True,
        similarity_threshold: float = 0.7,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Asynchronously search the RAG knowledge base"""
        
        try:
            # Build search filters
            filters = {}
            content_types = ['text']
            if include_tables:
                content_types.append('table')
            if include_images:
                content_types.append('image')
            
            filters['content_type'] = {'$in': content_types}
            
            # Perform search
            results = await self.rag_service.search_pipeline(
                pipeline_id=self.pipeline_id,
                query=query,
                k=k,
                filters=filters
            )
            
            if not results:
                return f"No relevant documents found for query: '{query}'"
            
            # Filter by similarity threshold
            filtered_results = [r for r in results if r.get('score', 0) >= similarity_threshold]
            
            if not filtered_results:
                return f"No documents found above similarity threshold {similarity_threshold} for query: '{query}'"
            
            # Format results for agent consumption
            formatted_results = []
            for i, result in enumerate(filtered_results[:k]):
                content_type = result.get('metadata', {}).get('content_type', 'text')
                source = result.get('metadata', {}).get('filename', 'Unknown')
                score = result.get('score', 0)
                
                formatted_result = f"""
Result {i+1} (Score: {score:.3f}, Type: {content_type}):
Source: {source}
Content: {result['content'][:500]}{'...' if len(result['content']) > 500 else ''}
"""
                formatted_results.append(formatted_result)
            
            summary = f"Found {len(filtered_results)} relevant documents for '{query}':\n\n"
            return summary + "\n".join(formatted_results)
            
        except Exception as e:
            error_msg = f"Error searching RAG knowledge base: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def _run(
        self,
        query: str,
        k: int = 5,
        include_tables: bool = True,
        include_images: bool = True,
        similarity_threshold: float = 0.7,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for the async search"""
        return asyncio.run(self._arun(query, k, include_tables, include_images, similarity_threshold, run_manager))

class LanggraphRAGUploadTool(BaseTool):
    """Document upload tool for RAG pipeline"""
    
    name = "rag_upload"
    description = "Upload and process a document into the RAG knowledge base"
    args_schema = RAGUploadInput
    
    def __init__(self, pipeline_id: str, rag_service: EnhancedRAGServiceV2, **kwargs):
        super().__init__(**kwargs)
        self.pipeline_id = pipeline_id
        self.rag_service = rag_service
        self.logger = logger
    
    async def _arun(
        self,
        file_path: str,
        metadata: str = "{}",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Asynchronously upload and process a document"""
        
        try:
            # Validate file exists
            if not Path(file_path).exists():
                return f"Error: File not found at path: {file_path}"
            
            # Parse metadata
            try:
                metadata_dict = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError:
                metadata_dict = {"raw_metadata": metadata}
            
            # Add upload metadata
            metadata_dict.update({
                "upload_timestamp": datetime.utcnow().isoformat(),
                "upload_tool": "langgraph_rag_upload"
            })
            
            # Process the document
            result = await self.rag_service.ingest_document(
                pipeline_id=self.pipeline_id,
                file_path=file_path,
                filename=Path(file_path).name,
                metadata=metadata_dict
            )
            
            if result.success:
                return f"""Document successfully processed:
- File: {Path(file_path).name}
- Chunks created: {result.chunks_created}
- Tables extracted: {result.tables_extracted}
- Images extracted: {result.images_extracted}
- Processing time: {result.processing_time:.2f} seconds
- Method: {'Docling' if result.metadata and result.metadata.get('processing_method') == 'docling' else 'Basic'}

The document is now searchable in the knowledge base."""
            else:
                return f"Error processing document {Path(file_path).name}: {result.error_message}"
                
        except Exception as e:
            error_msg = f"Error uploading document: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def _run(
        self,
        file_path: str,
        metadata: str = "{}",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for the async upload"""
        return asyncio.run(self._arun(file_path, metadata, run_manager))

class RAGAgentState:
    """State class for RAG agent workflows"""
    
    def __init__(self):
        self.messages: List[Dict] = []
        self.search_results: List[Dict] = []
        self.uploaded_documents: List[Dict] = []
        self.current_query: str = ""
        self.context: str = ""
        self.final_response: str = ""
        self.tools_used: List[str] = []
        self.error_messages: List[str] = []

class LanggraphRAGAgent:
    """Langgraph agent with RAG capabilities"""
    
    def __init__(self, pipeline_id: str, rag_service: EnhancedRAGServiceV2, llm_model=None):
        self.pipeline_id = pipeline_id
        self.rag_service = rag_service
        self.llm_model = llm_model
        self.logger = logger
        
        # Initialize tools
        self.search_tool = LanggraphRAGTool(pipeline_id, rag_service)
        self.upload_tool = LanggraphRAGUploadTool(pipeline_id, rag_service)
        self.tools = [self.search_tool, self.upload_tool]
        
        # Tool executor
        self.tool_executor = ToolExecutor(self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the Langgraph workflow graph"""
        
        if not LANGGRAPH_AVAILABLE:
            raise RuntimeError("Langgraph not available. Please install langgraph package.")
        
        # Define the graph
        workflow = StateGraph(RAGAgentState)
        
        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request_node)
        workflow.add_node("search_knowledge_base", self._search_node)
        workflow.add_node("upload_document", self._upload_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Add edges
        workflow.add_edge("analyze_request", "search_knowledge_base")
        workflow.add_edge("search_knowledge_base", "generate_response")
        workflow.add_edge("upload_document", "generate_response")
        workflow.add_edge("generate_response", END)
        workflow.add_edge("error_handler", END)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        # Compile the graph
        return workflow.compile()
    
    async def _analyze_request_node(self, state: RAGAgentState) -> RAGAgentState:
        """Analyze the user request to determine the appropriate action"""
        
        if not state.messages:
            state.error_messages.append("No messages provided")
            return state
        
        last_message = state.messages[-1]
        message_content = last_message.get("content", "").lower()
        
        # Simple intent detection
        if "upload" in message_content or "add document" in message_content:
            state.current_query = "upload_document"
        else:
            state.current_query = last_message.get("content", "")
        
        return state
    
    async def _search_node(self, state: RAGAgentState) -> RAGAgentState:
        """Perform RAG search"""
        
        try:
            if not state.current_query or state.current_query == "upload_document":
                return state
            
            # Use the search tool
            search_result = await self.search_tool._arun(state.current_query)
            
            state.search_results.append({
                "query": state.current_query,
                "result": search_result,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            state.context = search_result
            state.tools_used.append("rag_search")
            
        except Exception as e:
            state.error_messages.append(f"Search error: {str(e)}")
            self.logger.error(f"Search node error: {e}")
        
        return state
    
    async def _upload_node(self, state: RAGAgentState) -> RAGAgentState:
        """Handle document upload"""
        
        try:
            # This would typically extract file path from the message
            # For now, we'll skip actual upload in this demo node
            state.uploaded_documents.append({
                "status": "upload_node_called",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            state.tools_used.append("rag_upload")
            
        except Exception as e:
            state.error_messages.append(f"Upload error: {str(e)}")
            self.logger.error(f"Upload node error: {e}")
        
        return state
    
    async def _generate_response_node(self, state: RAGAgentState) -> RAGAgentState:
        """Generate the final response"""
        
        try:
            if state.error_messages:
                state.final_response = f"Errors occurred: {'; '.join(state.error_messages)}"
                return state
            
            if state.context:
                if self.llm_model:
                    # Use LLM to generate contextual response
                    prompt = f"""
Based on the following knowledge base search results, provide a helpful and accurate response to the user's query.

User Query: {state.current_query}

Search Results:
{state.context}

Please provide a clear, concise response based on the search results:"""
                    
                    # Note: This would call the actual LLM model
                    state.final_response = f"Based on the search results for '{state.current_query}':\n\n{state.context}"
                else:
                    state.final_response = f"Search completed for '{state.current_query}':\n\n{state.context}"
            else:
                state.final_response = f"Query processed: {state.current_query}"
            
            # Add tools used info
            if state.tools_used:
                state.final_response += f"\n\n[Tools used: {', '.join(state.tools_used)}]"
                
        except Exception as e:
            state.error_messages.append(f"Response generation error: {str(e)}")
            state.final_response = f"Error generating response: {str(e)}"
            self.logger.error(f"Response generation error: {e}")
        
        return state
    
    async def _error_handler_node(self, state: RAGAgentState) -> RAGAgentState:
        """Handle errors in the workflow"""
        
        error_summary = "; ".join(state.error_messages) if state.error_messages else "Unknown error"
        state.final_response = f"I encountered some issues while processing your request: {error_summary}"
        
        return state
    
    async def process_query(self, query: str) -> str:
        """Process a query through the RAG agent workflow"""
        
        try:
            # Initialize state
            initial_state = RAGAgentState()
            initial_state.messages = [{"content": query, "timestamp": datetime.utcnow().isoformat()}]
            
            # Run the workflow
            result = await self.graph.ainvoke(initial_state)
            
            return result.final_response
            
        except Exception as e:
            error_msg = f"Error processing query through RAG agent: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def get_tool_schemas(self) -> List[Dict]:
        """Get tool schemas for external integration"""
        
        schemas = []
        for tool in self.tools:
            schema = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.schema() if hasattr(tool, 'args_schema') else {}
            }
            schemas.append(schema)
        
        return schemas

# Factory function to create RAG tools for different contexts
async def create_rag_tools(pipeline_id: str, rag_service: EnhancedRAGServiceV2, context: str = "standalone") -> List[BaseTool]:
    """Factory function to create RAG tools for different contexts"""
    
    if context == "langgraph":
        return [
            LanggraphRAGTool(pipeline_id, rag_service),
            LanggraphRAGUploadTool(pipeline_id, rag_service)
        ]
    elif context == "simple":
        # Create simple function-based tools
        async def search_func(query: str, k: int = 5) -> str:
            tool = LanggraphRAGTool(pipeline_id, rag_service)
            return await tool._arun(query, k)
        
        async def upload_func(file_path: str, metadata: str = "{}") -> str:
            tool = LanggraphRAGUploadTool(pipeline_id, rag_service)
            return await tool._arun(file_path, metadata)
        
        return [
            Tool(
                name="rag_search",
                description="Search the RAG knowledge base for relevant documents",
                func=search_func
            ),
            Tool(
                name="rag_upload",
                description="Upload and process documents into the RAG knowledge base",
                func=upload_func
            )
        ]
    else:
        raise ValueError(f"Unknown context: {context}")

# Example usage and testing function
async def test_langgraph_rag_agent():
    """Test function for the Langgraph RAG agent"""
    
    try:
        # Initialize RAG service (this would use real database connection)
        rag_service = EnhancedRAGServiceV2()
        await rag_service.initialize("postgresql://test")
        
        # Create agent
        agent = LanggraphRAGAgent("test-pipeline", rag_service)
        
        # Test queries
        test_queries = [
            "What is machine learning?",
            "Search for information about neural networks",
            "Find documents related to data science"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            response = await agent.process_query(query)
            print(f"Response: {response}")
        
        # Print tool schemas
        schemas = agent.get_tool_schemas()
        print(f"\nTool schemas: {json.dumps(schemas, indent=2)}")
        
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_langgraph_rag_agent())