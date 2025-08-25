"""
RAG MCP Server
Model Context Protocol server that exposes RAG pipeline functionality to external agents
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Sequence
from datetime import datetime
import uuid

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ListToolsRequest, ListToolsResult, ReadResourceRequest, ReadResourceResult
)

# Internal imports
from ..services.enhanced_rag_service_v2 import EnhancedRAGServiceV2, RAGConfiguration
from ..models.database import get_db

logger = logging.getLogger(__name__)

class RAGMCPServer:
    """MCP Server for RAG pipeline operations"""
    
    def __init__(self, database_url: str):
        self.server = Server("enhanced-rag-server")
        self.database_url = database_url
        self.rag_service = EnhancedRAGServiceV2(database_url)
        self.active_pipelines: Dict[str, RAGConfiguration] = {}
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """List available RAG pipeline resources"""
            resources = []
            
            try:
                # Get active pipelines from database
                # This is a simplified version - in real implementation, 
                # you'd query the database for active RAG pipelines
                for pipeline_id, config in self.active_pipelines.items():
                    resources.append(Resource(
                        uri=f"rag://pipeline/{pipeline_id}",
                        name=f"RAG Pipeline {pipeline_id}",
                        description=f"RAG pipeline with embedding model {config.embedding_model_name}",
                        mimeType="application/json"
                    ))
                
                # Add search results as resources
                resources.append(Resource(
                    uri="rag://search-results",
                    name="Recent Search Results",
                    description="Recent search results from all pipelines",
                    mimeType="application/json"
                ))
                
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
            
            return ListResourcesResult(resources=resources)
        
        @self.server.read_resource()
        async def handle_read_resource(request: ReadResourceRequest) -> ReadResourceResult:
            """Read a specific RAG resource"""
            
            try:
                if request.uri.startswith("rag://pipeline/"):
                    pipeline_id = request.uri.split("/")[-1]
                    config = await self.rag_service.get_rag_configuration(pipeline_id)
                    
                    if config:
                        content = {
                            "pipeline_id": pipeline_id,
                            "embedding_model": config.embedding_model_name,
                            "chunking_strategy": config.chunking_strategy.value,
                            "chunk_size": config.chunk_size,
                            "use_docling": config.use_docling,
                            "capabilities": {
                                "table_extraction": config.extract_tables,
                                "image_processing": config.extract_images,
                                "advanced_parsing": config.use_docling
                            }
                        }
                        
                        return ReadResourceResult(
                            contents=[
                                TextContent(
                                    type="text",
                                    text=json.dumps(content, indent=2)
                                )
                            ]
                        )
                
                elif request.uri == "rag://search-results":
                    # Return recent search results (mock data for demo)
                    results = {
                        "recent_searches": [
                            {
                                "timestamp": datetime.utcnow().isoformat(),
                                "query": "machine learning",
                                "results_count": 5,
                                "pipeline_id": "demo-pipeline"
                            }
                        ]
                    }
                    
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text", 
                                text=json.dumps(results, indent=2)
                            )
                        ]
                    )
                
                else:
                    return ReadResourceResult(
                        contents=[
                            TextContent(
                                type="text",
                                text=f"Resource not found: {request.uri}"
                            )
                        ]
                    )
                    
            except Exception as e:
                logger.error(f"Error reading resource {request.uri}: {e}")
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=f"Error reading resource: {str(e)}"
                        )
                    ]
                )
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available RAG tools"""
            
            tools = [
                Tool(
                    name="rag_search",
                    description="Search RAG knowledge base for relevant documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pipeline_id": {
                                "type": "string",
                                "description": "RAG pipeline ID to search"
                            },
                            "query": {
                                "type": "string", 
                                "description": "Search query"
                            },
                            "k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5
                            },
                            "include_tables": {
                                "type": "boolean",
                                "description": "Include table content in search",
                                "default": True
                            },
                            "include_images": {
                                "type": "boolean", 
                                "description": "Include image descriptions in search",
                                "default": True
                            }
                        },
                        "required": ["pipeline_id", "query"]
                    }
                ),
                Tool(
                    name="rag_upload",
                    description="Upload and process a document into RAG knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pipeline_id": {
                                "type": "string",
                                "description": "RAG pipeline ID to upload to"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to upload"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Document metadata",
                                "properties": {
                                    "title": {"type": "string"},
                                    "author": {"type": "string"},
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                    "category": {"type": "string"}
                                }
                            }
                        },
                        "required": ["pipeline_id", "file_path"]
                    }
                ),
                Tool(
                    name="rag_create_pipeline",
                    description="Create a new RAG pipeline with specified configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Pipeline name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Pipeline description"
                            },
                            "embedding_model_id": {
                                "type": "string",
                                "description": "ID of the embedding model to use"
                            },
                            "chunk_size": {
                                "type": "integer",
                                "description": "Chunk size for document splitting",
                                "default": 1000
                            },
                            "use_docling": {
                                "type": "boolean",
                                "description": "Use advanced Docling processing",
                                "default": True
                            }
                        },
                        "required": ["name", "embedding_model_id"]
                    }
                ),
                Tool(
                    name="rag_list_pipelines",
                    description="List all available RAG pipelines",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Filter by status (active, inactive, etc.)",
                                "enum": ["active", "inactive", "draft", "error"]
                            }
                        }
                    }
                ),
                Tool(
                    name="rag_pipeline_stats",
                    description="Get statistics for a RAG pipeline",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "pipeline_id": {
                                "type": "string",
                                "description": "RAG pipeline ID"
                            }
                        },
                        "required": ["pipeline_id"]
                    }
                )
            ]
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls"""
            
            try:
                if request.name == "rag_search":
                    return await self._handle_rag_search(request.arguments)
                elif request.name == "rag_upload":
                    return await self._handle_rag_upload(request.arguments)
                elif request.name == "rag_create_pipeline":
                    return await self._handle_create_pipeline(request.arguments)
                elif request.name == "rag_list_pipelines":
                    return await self._handle_list_pipelines(request.arguments)
                elif request.name == "rag_pipeline_stats":
                    return await self._handle_pipeline_stats(request.arguments)
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {request.name}"
                            )
                        ]
                    )
                    
            except Exception as e:
                logger.error(f"Error calling tool {request.name}: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error executing {request.name}: {str(e)}"
                        )
                    ],
                    isError=True
                )
    
    async def _handle_rag_search(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle RAG search tool call"""
        
        pipeline_id = args.get("pipeline_id")
        query = args.get("query")
        k = args.get("k", 5)
        include_tables = args.get("include_tables", True)
        include_images = args.get("include_images", True)
        
        if not pipeline_id or not query:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Missing required parameters: pipeline_id and query"
                    )
                ],
                isError=True
            )
        
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
                pipeline_id=pipeline_id,
                query=query,
                k=k,
                filters=filters
            )
            
            # Format results
            formatted_results = {
                "query": query,
                "pipeline_id": pipeline_id,
                "total_results": len(results),
                "results": [
                    {
                        "content": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"],
                        "score": result.get("score", 0),
                        "metadata": {
                            "filename": result.get("metadata", {}).get("filename", "Unknown"),
                            "content_type": result.get("metadata", {}).get("content_type", "text"),
                            "chunk_index": result.get("metadata", {}).get("chunk_index", 0)
                        }
                    }
                    for result in results
                ],
                "search_timestamp": datetime.utcnow().isoformat()
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(formatted_results, indent=2)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Search failed: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _handle_rag_upload(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle document upload tool call"""
        
        pipeline_id = args.get("pipeline_id")
        file_path = args.get("file_path")
        metadata = args.get("metadata", {})
        
        if not pipeline_id or not file_path:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Missing required parameters: pipeline_id and file_path"
                    )
                ],
                isError=True
            )
        
        try:
            # Process the document
            result = await self.rag_service.ingest_document(
                pipeline_id=pipeline_id,
                file_path=file_path,
                filename=file_path.split("/")[-1],
                metadata=metadata
            )
            
            upload_result = {
                "success": result.success,
                "pipeline_id": pipeline_id,
                "file_path": file_path,
                "processing_results": {
                    "chunks_created": result.chunks_created,
                    "tables_extracted": result.tables_extracted,
                    "images_extracted": result.images_extracted,
                    "processing_time": result.processing_time,
                    "method": result.metadata.get("processing_method", "unknown") if result.metadata else "unknown"
                },
                "error_message": result.error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(upload_result, indent=2)
                    )
                ]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Upload failed: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _handle_create_pipeline(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle create pipeline tool call"""
        
        # This would integrate with the actual pipeline creation logic
        # For now, return a mock response
        pipeline_config = {
            "pipeline_id": str(uuid.uuid4()),
            "name": args.get("name", "New Pipeline"),
            "description": args.get("description", ""),
            "embedding_model_id": args.get("embedding_model_id"),
            "configuration": {
                "chunk_size": args.get("chunk_size", 1000),
                "use_docling": args.get("use_docling", True),
                "created_via": "mcp",
                "created_at": datetime.utcnow().isoformat()
            },
            "status": "created"
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(pipeline_config, indent=2)
                )
            ]
        )
    
    async def _handle_list_pipelines(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle list pipelines tool call"""
        
        # Mock pipeline list - in real implementation, query database
        pipelines = [
            {
                "pipeline_id": "demo-pipeline-1",
                "name": "Document Knowledge Base",
                "description": "General document knowledge base with Docling processing",
                "status": "active",
                "embedding_model": "text-embedding-3-small",
                "document_count": 150,
                "chunk_count": 2340,
                "created_at": "2024-01-15T10:30:00Z",
                "last_updated": "2024-01-20T15:45:00Z"
            },
            {
                "pipeline_id": "demo-pipeline-2", 
                "name": "Technical Documentation",
                "description": "Technical documents with table extraction",
                "status": "active",
                "embedding_model": "text-embedding-3-large",
                "document_count": 75,
                "chunk_count": 1200,
                "created_at": "2024-01-10T09:15:00Z",
                "last_updated": "2024-01-18T14:20:00Z"
            }
        ]
        
        # Filter by status if provided
        status_filter = args.get("status")
        if status_filter:
            pipelines = [p for p in pipelines if p["status"] == status_filter]
        
        result = {
            "total_pipelines": len(pipelines),
            "pipelines": pipelines,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    async def _handle_pipeline_stats(self, args: Dict[str, Any]) -> CallToolResult:
        """Handle pipeline statistics tool call"""
        
        pipeline_id = args.get("pipeline_id")
        if not pipeline_id:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Missing required parameter: pipeline_id"
                    )
                ],
                isError=True
            )
        
        # Mock statistics - in real implementation, query database
        stats = {
            "pipeline_id": pipeline_id,
            "name": f"Pipeline {pipeline_id}",
            "status": "active",
            "statistics": {
                "total_documents": 150,
                "total_chunks": 2340,
                "total_searches": 1250,
                "avg_response_time": 0.85,
                "success_rate": 98.5,
                "storage_size_mb": 45.2
            },
            "recent_activity": {
                "documents_added_today": 5,
                "searches_today": 23,
                "last_document_uploaded": "2024-01-20T15:45:00Z",
                "last_search": "2024-01-20T16:30:00Z"
            },
            "configuration": {
                "embedding_model": "text-embedding-3-small",
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "uses_docling": True,
                "extracts_tables": True,
                "extracts_images": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(stats, indent=2)
                )
            ]
        )
    
    async def initialize(self):
        """Initialize the RAG service"""
        await self.rag_service.initialize()
        logger.info("RAG MCP Server initialized")
    
    async def run(self, transport_type: str = "stdio"):
        """Run the MCP server"""
        
        await self.initialize()
        
        if transport_type == "stdio":
            from mcp.server.stdio import stdio_server
            
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="enhanced-rag-server",
                        server_version="1.0.0",
                        capabilities={
                            "resources": True,
                            "tools": True
                        }
                    ),
                )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

# Entry point for running as standalone MCP server
async def main():
    """Main entry point for the RAG MCP server"""
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    
    server = RAGMCPServer(database_url)
    
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("RAG MCP Server stopped by user")
    except Exception as e:
        logger.error(f"RAG MCP Server error: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the server
    asyncio.run(main())