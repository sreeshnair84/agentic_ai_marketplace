"""
Enhanced RAG Pipeline API with Docling Integration and Langgraph Support
Provides comprehensive RAG operations with advanced document processing
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text
from typing import List, Dict, Any, Optional
import json
import uuid
import logging
import tempfile
import aiofiles
from datetime import datetime
from pathlib import Path

from ..models.tool_management import RAGPipeline, RAGPipelineRun, ToolInstance
from ..models.database import get_db
from ..services.enhanced_rag_service_v2 import EnhancedRAGServiceV2, ProcessingResult
from ..schemas.tool_schemas import (
    RAGPipelineCreate, RAGPipelineUpdate, RAGPipelineResponse,
    DocumentIngestionRequest, DocumentIngestionResponse
)

router = APIRouter(prefix="/rag-pipelines-v2", tags=["Enhanced RAG Pipelines"])
logger = logging.getLogger(__name__)

# Initialize enhanced RAG service
enhanced_rag_service = EnhancedRAGServiceV2()

# Background task to initialize the service
async def initialize_rag_service():
    """Initialize RAG service with database connection"""
    try:
        # Use database URL from environment or default
        import os
        database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
        await enhanced_rag_service.initialize(database_url)
        logger.info("Enhanced RAG Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Enhanced RAG Service: {e}")

@router.on_event("startup")
async def startup_event():
    await initialize_rag_service()

@router.get("/", response_model=List[RAGPipelineResponse])
async def list_enhanced_rag_pipelines(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all enhanced RAG pipelines with filtering"""
    
    query = select(RAGPipeline)
    
    if status:
        query = query.where(RAGPipeline.status == status)
    
    query = query.offset(skip).limit(limit).order_by(RAGPipeline.created_at.desc())
    
    result = await db.execute(query)
    pipelines = result.scalars().all()
    
    # Enhance with health status
    enhanced_pipelines = []
    for pipeline in pipelines:
        pipeline_dict = RAGPipelineResponse.model_validate(pipeline).model_dump()
        
        # Add health check information
        try:
            health = await enhanced_rag_service.health_check(str(pipeline.id))
            pipeline_dict['health_status'] = health['status']
            pipeline_dict['last_health_check'] = health['timestamp']
        except Exception as e:
            pipeline_dict['health_status'] = 'unknown'
            pipeline_dict['last_health_check'] = None
            logger.warning(f"Health check failed for pipeline {pipeline.id}: {e}")
        
        enhanced_pipelines.append(pipeline_dict)
    
    return enhanced_pipelines

@router.post("/", response_model=RAGPipelineResponse)
async def create_enhanced_rag_pipeline(
    pipeline: RAGPipelineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new enhanced RAG pipeline with Docling support"""
    
    # Verify tool instance exists
    tool_instance = await db.execute(
        select(ToolInstance).where(ToolInstance.id == pipeline.tool_instance_id)
    )
    tool_instance = tool_instance.scalar_one_or_none()
    
    if not tool_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool instance not found"
        )
    
    # Check if pipeline name already exists
    existing = await db.execute(
        select(RAGPipeline).where(RAGPipeline.name == pipeline.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RAG pipeline with name '{pipeline.name}' already exists"
        )
    
    # Enhanced processing configuration with Docling options
    enhanced_processing_config = {
        **pipeline.ingestion_config,
        'use_docling': True,
        'extract_tables': True,
        'extract_images': True,
        'llm_preprocessing': True,
        'quality_threshold': 0.7,
        'chunking_strategy': 'recursive',
        'preprocessing_rules': []
    }
    
    # Enhanced vectorization configuration
    enhanced_vectorization_config = {
        **pipeline.vectorization_config,
        'semantic_chunking': True,
        'metadata_extraction': True,
        'quality_scoring': True
    }
    
    # Create pipeline
    db_pipeline = RAGPipeline(
        id=uuid.uuid4(),
        name=pipeline.name,
        description=pipeline.description,
        data_sources=[source.dict() for source in pipeline.data_sources],
        processing_config=enhanced_processing_config,
        vectorization_config=enhanced_vectorization_config,
        status="inactive",
        created_by=pipeline.created_by
    )
    
    db.add(db_pipeline)
    await db.commit()
    await db.refresh(db_pipeline)
    
    logger.info(f"Created enhanced RAG pipeline: {pipeline.name} with Docling support")
    return RAGPipelineResponse.model_validate(db_pipeline)

@router.post("/{pipeline_id}/documents/upload-advanced")
async def upload_documents_with_docling(
    pipeline_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    metadata: Optional[str] = Form(None),
    processing_options: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload documents with advanced Docling processing"""
    
    # Get pipeline
    pipeline = await db.execute(
        select(RAGPipeline).where(RAGPipeline.id == pipeline_id)
    )
    pipeline = pipeline.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG pipeline not found"
        )
    
    # Parse metadata and options
    doc_metadata = json.loads(metadata) if metadata else {}
    proc_options = json.loads(processing_options) if processing_options else {}
    
    # Process files in background
    async def process_files_background():
        """Background task to process uploaded files"""
        processed_files = []
        
        for file in files:
            try:
                # Save file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                # Process file with enhanced RAG service
                result = await enhanced_rag_service.ingest_document(
                    pipeline_id=pipeline_id,
                    file_path=temp_file_path,
                    filename=file.filename,
                    metadata={
                        **doc_metadata,
                        'original_filename': file.filename,
                        'file_size': len(content),
                        'upload_timestamp': datetime.utcnow().isoformat()
                    }
                )
                
                processed_files.append({
                    "filename": file.filename,
                    "success": result.success,
                    "chunks_created": result.chunks_created,
                    "tables_extracted": result.tables_extracted,
                    "images_extracted": result.images_extracted,
                    "processing_time": result.processing_time,
                    "error_message": result.error_message,
                    "file_size": len(content)
                })
                
                # Clean up temp file
                Path(temp_file_path).unlink(missing_ok=True)
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                processed_files.append({
                    "filename": file.filename,
                    "success": False,
                    "error_message": str(e)
                })
        
        # Update pipeline status
        total_successful = sum(1 for f in processed_files if f['success'])
        total_chunks = sum(f.get('chunks_created', 0) for f in processed_files)
        
        logger.info(f"Processed {total_successful}/{len(files)} files for pipeline {pipeline_id}, created {total_chunks} chunks")
    
    # Start background processing
    background_tasks.add_task(process_files_background)
    
    return {
        "message": f"Started processing {len(files)} files in background",
        "pipeline_id": pipeline_id,
        "files_queued": len(files),
        "status": "processing"
    }

@router.post("/{pipeline_id}/search-advanced")
async def advanced_search_pipeline(
    pipeline_id: str,
    query: str,
    k: int = 5,
    search_strategy: str = "semantic",
    include_tables: bool = True,
    include_images: bool = True,
    filters: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Advanced search with content type filtering and enhanced results"""
    
    # Get pipeline
    pipeline = await db.execute(
        select(RAGPipeline).where(RAGPipeline.id == pipeline_id)
    )
    pipeline = pipeline.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG pipeline not found"
        )
    
    # Build search filters
    search_filters = filters or {}
    
    # Add content type filters
    content_types = ['text']
    if include_tables:
        content_types.append('table')
    if include_images:
        content_types.append('image')
    
    search_filters['content_type'] = {'$in': content_types}
    
    # Perform enhanced search
    try:
        results = await enhanced_rag_service.search_pipeline(
            pipeline_id=pipeline_id,
            query=query,
            k=k,
            filters=search_filters
        )
        
        # Enhance results with additional metadata
        enhanced_results = []
        for result in results:
            enhanced_result = {
                **result,
                'content_preview': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                'content_type': result['metadata'].get('content_type', 'text'),
                'source_info': {
                    'filename': result['metadata'].get('filename', 'Unknown'),
                    'chunk_index': result['metadata'].get('chunk_index', 0),
                    'created_at': result['metadata'].get('created_at')
                }
            }
            enhanced_results.append(enhanced_result)
        
        return {
            "query": query,
            "pipeline_id": pipeline_id,
            "total_results": len(enhanced_results),
            "search_strategy": search_strategy,
            "results": enhanced_results,
            "search_metadata": {
                "include_tables": include_tables,
                "include_images": include_images,
                "filters_applied": search_filters,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in advanced search for pipeline {pipeline_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/{pipeline_id}/langgraph-tools")
async def get_langgraph_tools(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Langgraph-compatible tools for this RAG pipeline"""
    
    try:
        tools = await enhanced_rag_service.create_rag_tools_for_langgraph(pipeline_id)
        
        # Convert tools to serializable format
        tool_definitions = []
        for tool in tools:
            tool_def = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query or input text"
                        }
                    },
                    "required": ["query"]
                }
            }
            tool_definitions.append(tool_def)
        
        return {
            "pipeline_id": pipeline_id,
            "tools": tool_definitions,
            "total_tools": len(tool_definitions),
            "langgraph_compatible": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Langgraph tools for pipeline {pipeline_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Langgraph tools: {str(e)}"
        )

@router.post("/{pipeline_id}/create-langgraph-agent")
async def create_langgraph_agent(
    pipeline_id: str,
    llm_model_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a Langgraph agent for this RAG pipeline"""
    
    try:
        # Get LLM model if specified
        llm_model = None
        if llm_model_id:
            llm_query = await db.execute(
                select(text("SELECT * FROM llm_models WHERE id = :model_id")),
                {"model_id": llm_model_id}
            )
            llm_row = llm_query.fetchone()
            if llm_row:
                # Here you would initialize the actual LLM model
                # For now, we'll just pass the configuration
                llm_model = {
                    "id": llm_model_id,
                    "name": llm_row.name,
                    "provider": llm_row.provider
                }
        
        # Create Langgraph agent
        agent_app = await enhanced_rag_service.create_langgraph_rag_agent(
            pipeline_id=pipeline_id,
            llm_model=llm_model
        )
        
        # For demonstration, we'll return the agent configuration
        # In a real implementation, you'd register this agent for use
        agent_config = {
            "pipeline_id": pipeline_id,
            "agent_id": f"rag_agent_{pipeline_id}",
            "llm_model_id": llm_model_id,
            "capabilities": [
                "document_search",
                "knowledge_retrieval",
                "context_aware_responses"
            ],
            "status": "created",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return agent_config
        
    except Exception as e:
        logger.error(f"Error creating Langgraph agent for pipeline {pipeline_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Langgraph agent: {str(e)}"
        )

@router.get("/{pipeline_id}/mcp-config")
async def get_mcp_configuration(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get MCP (Model Context Protocol) configuration for this RAG pipeline"""
    
    try:
        mcp_config = await enhanced_rag_service.create_mcp_endpoint(pipeline_id)
        
        return {
            "pipeline_id": pipeline_id,
            "mcp_configuration": mcp_config,
            "integration_ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting MCP config for pipeline {pipeline_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get MCP configuration: {str(e)}"
        )

@router.get("/{pipeline_id}/health-detailed")
async def detailed_health_check(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Detailed health check for RAG pipeline"""
    
    try:
        health_status = await enhanced_rag_service.health_check(pipeline_id)
        
        # Add database-level checks
        pipeline_query = await db.execute(
            select(RAGPipeline).where(RAGPipeline.id == pipeline_id)
        )
        pipeline = pipeline_query.scalar_one_or_none()
        
        if pipeline:
            health_status['pipeline_status'] = pipeline.status
            health_status['last_updated'] = pipeline.updated_at.isoformat() if pipeline.updated_at else None
        else:
            health_status['pipeline_status'] = 'not_found'
        
        # Add system capabilities
        health_status['system_capabilities'] = {
            'docling_available': health_status.get('docling_available', False),
            'langgraph_available': health_status.get('langgraph_available', False),
            'advanced_chunking': True,
            'table_extraction': True,
            'image_processing': True,
            'semantic_search': True
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in detailed health check for pipeline {pipeline_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/{pipeline_id}/stats")
async def get_pipeline_statistics(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive statistics for a RAG pipeline"""
    
    try:
        # Get pipeline info
        pipeline_query = await db.execute(
            select(RAGPipeline).where(RAGPipeline.id == pipeline_id)
        )
        pipeline = pipeline_query.scalar_one_or_none()
        
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RAG pipeline not found"
            )
        
        # Get pipeline run statistics
        runs_query = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_runs,
                    COUNT(*) FILTER (WHERE status = 'completed') as successful_runs,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_runs,
                    AVG(duration_seconds) as avg_duration,
                    MAX(completed_at) as last_run
                FROM rag_pipeline_runs 
                WHERE pipeline_id = :pipeline_id
            """),
            {"pipeline_id": pipeline_id}
        )
        runs_stats = runs_query.fetchone()
        
        # Compile statistics
        stats = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.name,
            "pipeline_status": pipeline.status,
            "created_at": pipeline.created_at.isoformat(),
            "updated_at": pipeline.updated_at.isoformat() if pipeline.updated_at else None,
            "processing_stats": {
                "total_runs": runs_stats[0] if runs_stats else 0,
                "successful_runs": runs_stats[1] if runs_stats else 0,
                "failed_runs": runs_stats[2] if runs_stats else 0,
                "success_rate": (runs_stats[1] / runs_stats[0] * 100) if runs_stats and runs_stats[0] > 0 else 0,
                "avg_duration_seconds": float(runs_stats[3]) if runs_stats and runs_stats[3] else 0,
                "last_run": runs_stats[4].isoformat() if runs_stats and runs_stats[4] else None
            },
            "configuration": {
                "data_sources": len(pipeline.data_sources) if pipeline.data_sources else 0,
                "processing_config": pipeline.processing_config,
                "vectorization_config": pipeline.vectorization_config
            },
            "capabilities": {
                "docling_processing": pipeline.processing_config.get('use_docling', False) if pipeline.processing_config else False,
                "table_extraction": pipeline.processing_config.get('extract_tables', False) if pipeline.processing_config else False,
                "image_extraction": pipeline.processing_config.get('extract_images', False) if pipeline.processing_config else False,
                "semantic_chunking": pipeline.vectorization_config.get('semantic_chunking', False) if pipeline.vectorization_config else False
            }
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics for pipeline {pipeline_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipeline statistics: {str(e)}"
        )

@router.get("/health")
async def service_health():
    """Overall service health check"""
    return {
        "service": "enhanced-rag-pipelines",
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "docling_integration": True,
            "langgraph_support": True,
            "mcp_compatibility": True,
            "advanced_chunking": True,
            "table_extraction": True,
            "image_processing": True,
            "semantic_search": True,
            "background_processing": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }