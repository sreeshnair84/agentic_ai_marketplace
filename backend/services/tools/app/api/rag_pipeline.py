"""
RAG Pipeline API Router
Provides endpoints for managing RAG pipelines, data ingestion, and vectorization
Integrates with tool instances for configurable RAG workflows
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import logging
import os
import tempfile

from ..models.database import get_db
from ..models.tool_management import RAGPipeline, ToolInstance
from ..schemas.tool_management import (
    RAGPipelineCreate, RAGPipelineUpdate, RAGPipelineResponse,
    RAGPipelineStatus, DataSource, IngestionMethod,
    DataIngestionRequest, VectorizationRequest
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["RAG Pipelines"])

# ============================================================================
# RAG PIPELINE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=RAGPipelineResponse)
async def create_rag_pipeline(
    pipeline: RAGPipelineCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new RAG pipeline
    """
    try:
        # Validate that tool instance exists and is RAG type
        tool_instance = db.query(ToolInstance).filter(
            ToolInstance.id == pipeline.tool_instance_id
        ).first()
        
        if not tool_instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        if tool_instance.template.template_type.value != "rag_pipeline":
            raise HTTPException(
                status_code=400, 
                detail="Tool instance must be of type 'rag_pipeline'"
            )
        
        # Create RAG pipeline
        db_pipeline = RAGPipeline(
            id=str(uuid.uuid4()),
            tool_instance_id=pipeline.tool_instance_id,
            name=pipeline.name,
            description=pipeline.description,
            data_sources=pipeline.data_sources,
            ingestion_config=pipeline.ingestion_config,
            vectorization_config=pipeline.vectorization_config,
            status=RAGPipelineStatus.INACTIVE,
            metadata=pipeline.metadata or {},
            created_by="system",  # TODO: Get from auth context
            created_at=datetime.utcnow()
        )
        
        db.add(db_pipeline)
        db.commit()
        db.refresh(db_pipeline)
        
        logger.info(f"Created RAG pipeline: {db_pipeline.name} ({db_pipeline.id})")
        return db_pipeline
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating RAG pipeline: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[RAGPipelineResponse])
async def list_rag_pipelines(
    tool_instance_id: Optional[str] = None,
    status: Optional[RAGPipelineStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List RAG pipelines with optional filtering
    """
    try:
        query = db.query(RAGPipeline)
        
        if tool_instance_id:
            query = query.filter(RAGPipeline.tool_instance_id == tool_instance_id)
        if status:
            query = query.filter(RAGPipeline.status == status)
            
        pipelines = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(pipelines)} RAG pipelines")
        return pipelines
        
    except Exception as e:
        logger.error(f"Error listing RAG pipelines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pipeline_id}", response_model=RAGPipelineResponse)
async def get_rag_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific RAG pipeline by ID
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
            
        return pipeline
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving RAG pipeline {pipeline_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{pipeline_id}", response_model=RAGPipelineResponse)
async def update_rag_pipeline(
    pipeline_id: str,
    pipeline_update: RAGPipelineUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a RAG pipeline
    """
    try:
        db_pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not db_pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Update fields
        update_data = pipeline_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_pipeline, field, value)
        
        db_pipeline.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_pipeline)
        
        logger.info(f"Updated RAG pipeline: {pipeline_id}")
        return db_pipeline
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating RAG pipeline {pipeline_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{pipeline_id}")
async def delete_rag_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Check if pipeline is active
        if pipeline.status in [RAGPipelineStatus.ACTIVE, RAGPipelineStatus.PROCESSING]:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete active or processing pipeline"
            )
        
        db.delete(pipeline)
        db.commit()
        
        logger.info(f"Deleted RAG pipeline: {pipeline_id}")
        return {"message": "RAG pipeline deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting RAG pipeline {pipeline_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DATA INGESTION ENDPOINTS
# ============================================================================

@router.post("/{pipeline_id}/ingest-text")
async def ingest_text_data(
    pipeline_id: str,
    text_data: str = Form(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingest text data into a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Process text ingestion
        result = await _process_text_ingestion(pipeline, text_data, parsed_metadata)
        
        logger.info(f"Successfully ingested text data into pipeline: {pipeline_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting text data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{pipeline_id}/ingest-file")
async def ingest_file_data(
    pipeline_id: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingest file data into a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process file ingestion
            result = await _process_file_ingestion(pipeline, temp_file_path, file.filename, parsed_metadata)
            
            logger.info(f"Successfully ingested file {file.filename} into pipeline: {pipeline_id}")
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting file data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{pipeline_id}/ingest-url")
async def ingest_url_data(
    pipeline_id: str,
    ingestion_request: DataIngestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest data from a URL into a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Process URL ingestion
        result = await _process_url_ingestion(
            pipeline, 
            ingestion_request.source_url, 
            ingestion_request.ingestion_method,
            ingestion_request.metadata or {}
        )
        
        logger.info(f"Successfully ingested URL data into pipeline: {pipeline_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting URL data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VECTORIZATION ENDPOINTS
# ============================================================================

@router.post("/{pipeline_id}/vectorize")
async def vectorize_pipeline_data(
    pipeline_id: str,
    vectorization_request: VectorizationRequest,
    db: Session = Depends(get_db)
):
    """
    Vectorize data in a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Process vectorization
        result = await _process_vectorization(pipeline, vectorization_request)
        
        logger.info(f"Successfully vectorized data in pipeline: {pipeline_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error vectorizing pipeline data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pipeline_id}/vector-stats")
async def get_vector_statistics(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Get vector statistics for a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Get vector statistics
        stats = await _get_vector_statistics(pipeline)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vector statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SEARCH AND RETRIEVAL ENDPOINTS
# ============================================================================

@router.post("/{pipeline_id}/search")
async def search_pipeline(
    pipeline_id: str,
    query: str,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Search a RAG pipeline using vector similarity
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        if pipeline.status != RAGPipelineStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Pipeline is not active")
        
        # Perform search
        results = await _perform_pipeline_search(pipeline, query, top_k, filters or {})
        
        return {
            "query": query,
            "pipeline_id": pipeline_id,
            "results": results,
            "total_results": len(results),
            "search_time": 0.1  # Mock timing
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PIPELINE LIFECYCLE ENDPOINTS
# ============================================================================

@router.post("/{pipeline_id}/activate")
async def activate_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Activate a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Activate pipeline
        success = await _activate_pipeline(pipeline)
        
        if success:
            pipeline.status = RAGPipelineStatus.ACTIVE
            pipeline.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Activated RAG pipeline: {pipeline_id}")
            return {"message": "Pipeline activated successfully", "status": "active"}
        else:
            raise HTTPException(status_code=500, detail="Failed to activate pipeline")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating pipeline: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{pipeline_id}/deactivate")
async def deactivate_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db)
):
    """
    Deactivate a RAG pipeline
    """
    try:
        pipeline = db.query(RAGPipeline).filter(RAGPipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(status_code=404, detail="RAG pipeline not found")
        
        # Deactivate pipeline
        success = await _deactivate_pipeline(pipeline)
        
        if success:
            pipeline.status = RAGPipelineStatus.INACTIVE
            pipeline.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Deactivated RAG pipeline: {pipeline_id}")
            return {"message": "Pipeline deactivated successfully", "status": "inactive"}
        else:
            raise HTTPException(status_code=500, detail="Failed to deactivate pipeline")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating pipeline: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _process_text_ingestion(
    pipeline: RAGPipeline, 
    text_data: str, 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Process text data ingestion"""
    try:
        # Mock text processing
        chunks = _chunk_text(text_data, pipeline.ingestion_config)
        
        return {
            "ingestion_type": "text",
            "chunks_created": len(chunks),
            "total_characters": len(text_data),
            "metadata": metadata,
            "processing_time": 0.5,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing text ingestion: {str(e)}")
        raise

async def _process_file_ingestion(
    pipeline: RAGPipeline, 
    file_path: str, 
    filename: str, 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Process file data ingestion"""
    try:
        # Mock file processing
        file_size = os.path.getsize(file_path)
        
        # Simulate text extraction based on file type
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension in ['txt', 'md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # Mock extraction for other file types
            content = f"Mock extracted content from {filename}"
        
        chunks = _chunk_text(content, pipeline.ingestion_config)
        
        return {
            "ingestion_type": "file",
            "filename": filename,
            "file_size": file_size,
            "file_type": file_extension,
            "chunks_created": len(chunks),
            "total_characters": len(content),
            "metadata": metadata,
            "processing_time": 1.2,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing file ingestion: {str(e)}")
        raise

async def _process_url_ingestion(
    pipeline: RAGPipeline, 
    url: str, 
    method: IngestionMethod, 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Process URL data ingestion"""
    try:
        # Mock URL processing
        if method == IngestionMethod.WEB_SCRAPING:
            content = f"Mock scraped content from {url}"
        elif method == IngestionMethod.API_EXTRACTION:
            content = f"Mock API content from {url}"
        else:
            content = f"Mock RSS content from {url}"
        
        chunks = _chunk_text(content, pipeline.ingestion_config)
        
        return {
            "ingestion_type": "url",
            "source_url": url,
            "ingestion_method": method.value,
            "chunks_created": len(chunks),
            "total_characters": len(content),
            "metadata": metadata,
            "processing_time": 2.0,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing URL ingestion: {str(e)}")
        raise

async def _process_vectorization(
    pipeline: RAGPipeline, 
    request: VectorizationRequest
) -> Dict[str, Any]:
    """Process data vectorization"""
    try:
        # Mock vectorization process
        return {
            "vectorization_model": request.embedding_model,
            "vectors_created": request.batch_size or 100,
            "dimensions": 1536,  # Mock OpenAI embedding dimensions
            "processing_time": 5.0,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error processing vectorization: {str(e)}")
        raise

async def _get_vector_statistics(pipeline: RAGPipeline) -> Dict[str, Any]:
    """Get vector statistics for pipeline"""
    try:
        # Mock vector statistics
        return {
            "total_vectors": 1500,
            "vector_dimensions": 1536,
            "last_updated": datetime.utcnow().isoformat(),
            "storage_size_mb": 45.2,
            "index_status": "ready",
            "embedding_model": pipeline.vectorization_config.get("embedding_model", "text-embedding-ada-002")
        }
        
    except Exception as e:
        logger.error(f"Error getting vector statistics: {str(e)}")
        raise

async def _perform_pipeline_search(
    pipeline: RAGPipeline, 
    query: str, 
    top_k: int, 
    filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Perform vector search in pipeline"""
    try:
        # Mock search results
        results = []
        for i in range(min(top_k, 5)):
            results.append({
                "content": f"Mock search result {i+1} for query: {query}",
                "score": 0.95 - (i * 0.1),
                "metadata": {
                    "source": f"document_{i+1}",
                    "chunk_index": i,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error performing pipeline search: {str(e)}")
        raise

async def _activate_pipeline(pipeline: RAGPipeline) -> bool:
    """Activate a RAG pipeline"""
    try:
        # Mock activation process
        logger.info(f"Activating pipeline: {pipeline.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error activating pipeline: {str(e)}")
        return False

async def _deactivate_pipeline(pipeline: RAGPipeline) -> bool:
    """Deactivate a RAG pipeline"""
    try:
        # Mock deactivation process
        logger.info(f"Deactivating pipeline: {pipeline.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deactivating pipeline: {str(e)}")
        return False

def _chunk_text(text: str, config: Dict[str, Any]) -> List[str]:
    """Split text into chunks based on configuration"""
    chunk_size = config.get("chunk_size", 1000)
    chunk_overlap = config.get("chunk_overlap", 200)
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap if end < len(text) else end
    
    return chunks

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for RAG pipeline service
    """
    return {
        "status": "healthy",
        "service": "rag-pipelines",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "text_ingestion": True,
            "file_ingestion": True,
            "url_ingestion": True,
            "vectorization": True,
            "vector_search": True,
            "pipeline_management": True
        }
    }
