"""
Enhanced RAG Pipeline Management API
Provides comprehensive RAG pipeline operations including document management,
embedding model selection, and collection operations
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Dict, Any, Optional
import json
import uuid
import logging
from datetime import datetime
import aiofiles
import tempfile
from pathlib import Path

from ..models.tool_management import RAGPipeline, RAGPipelineRun, ToolInstance
from ..models.database import get_db
from ..schemas.tool_schemas import (
    RAGPipelineCreate, RAGPipelineUpdate, RAGPipelineResponse,
    DocumentIngestionRequest, DocumentIngestionResponse
)
from ..services.rag_service import EnhancedRAGService

router = APIRouter(prefix="/rag-pipelines", tags=["RAG Pipelines"])
logger = logging.getLogger(__name__)

# Initialize RAG service
rag_service = EnhancedRAGService()

@router.get("/", response_model=List[RAGPipelineResponse])
async def list_rag_pipelines(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all RAG pipelines with optional filtering"""
    
    query = select(RAGPipeline)
    
    if status:
        query = query.where(RAGPipeline.status == status)
    
    query = query.offset(skip).limit(limit).order_by(RAGPipeline.created_at.desc())
    
    result = await db.execute(query)
    pipelines = result.scalars().all()
    
    return [RAGPipelineResponse.model_validate(pipeline) for pipeline in pipelines]

@router.post("/", response_model=RAGPipelineResponse)
async def create_rag_pipeline(
    pipeline: RAGPipelineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new RAG pipeline"""
    
    # Verify tool instance exists and is of RAG type
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
    
    # Create pipeline
    db_pipeline = RAGPipeline(
        id=uuid.uuid4(),
        name=pipeline.name,
        description=pipeline.description,
        data_sources=[source.dict() for source in pipeline.data_sources],
        processing_config=pipeline.ingestion_config,
        vectorization_config=pipeline.vectorization_config,
        status="inactive",
        created_by=pipeline.created_by
    )
    
    db.add(db_pipeline)
    await db.commit()
    await db.refresh(db_pipeline)
    
    logger.info(f"Created RAG pipeline: {pipeline.name}")
    return RAGPipelineResponse.model_validate(db_pipeline)

@router.get("/{pipeline_id}", response_model=RAGPipelineResponse)
async def get_rag_pipeline(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific RAG pipeline"""
    
    pipeline = await db.execute(
        select(RAGPipeline).where(RAGPipeline.id == pipeline_id)
    )
    pipeline = pipeline.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG pipeline not found"
        )
    
    return RAGPipelineResponse.model_validate(pipeline)

@router.put("/{pipeline_id}", response_model=RAGPipelineResponse)
async def update_rag_pipeline(
    pipeline_id: str,
    pipeline_update: RAGPipelineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a RAG pipeline"""
    
    pipeline = await db.execute(
        select(RAGPipeline).where(RAGPipeline.id == pipeline_id)
    )
    pipeline = pipeline.scalar_one_or_none()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG pipeline not found"
        )
    
    # Update fields
    update_data = pipeline_update.dict(exclude_unset=True)
    
    if "data_sources" in update_data:
        update_data["data_sources"] = [source.dict() for source in update_data["data_sources"]]
    
    for field, value in update_data.items():
        setattr(pipeline, field, value)
    
    pipeline.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(pipeline)
    
    logger.info(f"Updated RAG pipeline: {pipeline.name}")
    return RAGPipelineResponse.model_validate(pipeline)

@router.delete("/{pipeline_id}")
async def delete_rag_pipeline(
    pipeline_id: str,
    force: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Delete a RAG pipeline"""
    
    # Check if pipeline has runs
    if not force:
        runs = await db.execute(
            select(RAGPipelineRun).where(RAGPipelineRun.pipeline_id == pipeline_id)
        )
        if runs.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete pipeline with existing runs. Use force=true to override."
            )
    
    # Delete pipeline
    result = await db.execute(
        delete(RAGPipeline).where(RAGPipeline.id == pipeline_id)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RAG pipeline not found"
        )
    
    await db.commit()
    logger.info(f"Deleted RAG pipeline: {pipeline_id}")
    return {"message": "RAG pipeline deleted successfully"}

@router.post("/{pipeline_id}/documents/upload")
async def upload_documents(
    pipeline_id: str,
    files: List[UploadFile] = File(...),
    metadata: Optional[str] = Form(None),
    processing_options: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload documents to a RAG pipeline"""
    
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
    
    # Process uploaded files
    processed_files = []
    total_chunks = 0
    
    for file in files:
        try:
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Process file with RAG service
            result = await rag_service.ingest_document(
                pipeline_id=pipeline_id,
                file_path=temp_file_path,
                filename=file.filename,
                metadata=doc_metadata,
                processing_options=proc_options
            )
            
            processed_files.append({
                "filename": file.filename,
                "status": result["status"],
                "chunks_created": result.get("chunks_created", 0),
                "file_size": len(content)
            })
            
            total_chunks += result.get("chunks_created", 0)
            
            # Clean up temp file
            Path(temp_file_path).unlink(missing_ok=True)
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            processed_files.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "pipeline_id": pipeline_id,
        "files_processed": len(processed_files),
        "total_chunks_created": total_chunks,
        "results": processed_files
    }

@router.post("/{pipeline_id}/documents/ingest-text")
async def ingest_text_content(
    pipeline_id: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Ingest text content directly into a RAG pipeline"""
    
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
    
    # Process text content
    result = await rag_service.ingest_text(
        pipeline_id=pipeline_id,
        content=content,
        metadata=metadata or {}
    )
    
    return result

@router.post("/{pipeline_id}/search")
async def search_pipeline(
    pipeline_id: str,
    query: str,
    k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Search documents in a RAG pipeline"""
    
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
    
    # Perform search
    results = await rag_service.search(
        pipeline_id=pipeline_id,
        query=query,
        k=k,
        filters=filters or {}
    )
    
    return results

@router.post("/{pipeline_id}/collections/{collection_name}/rebuild")
async def rebuild_collection(
    pipeline_id: str,
    collection_name: str,
    embedding_model: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Rebuild a collection with a new embedding model"""
    
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
    
    # Rebuild collection
    result = await rag_service.rebuild_collection(
        pipeline_id=pipeline_id,
        collection_name=collection_name,
        new_embedding_model=embedding_model
    )
    
    return result

@router.delete("/{pipeline_id}/collections/{collection_name}")
async def delete_collection(
    pipeline_id: str,
    collection_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a collection and all its documents"""
    
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
    
    # Delete collection
    result = await rag_service.delete_collection(
        pipeline_id=pipeline_id,
        collection_name=collection_name
    )
    
    return result

@router.get("/{pipeline_id}/collections")
async def list_collections(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all collections in a RAG pipeline"""
    
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
    
    # List collections
    collections = await rag_service.list_collections(pipeline_id)
    
    return collections

@router.get("/{pipeline_id}/collections/{collection_name}/stats")
async def get_collection_stats(
    pipeline_id: str,
    collection_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a collection"""
    
    # Get collection stats
    stats = await rag_service.get_collection_stats(
        pipeline_id=pipeline_id,
        collection_name=collection_name
    )
    
    return stats

@router.post("/{pipeline_id}/embedding-models/change")
async def change_embedding_model(
    pipeline_id: str,
    new_model: str,
    migrate_existing: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Change the embedding model for a RAG pipeline"""
    
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
    
    # Change embedding model
    result = await rag_service.change_embedding_model(
        pipeline_id=pipeline_id,
        new_model=new_model,
        migrate_existing=migrate_existing
    )
    
    # Update pipeline configuration
    vectorization_config = pipeline.vectorization_config or {}
    vectorization_config["embedding_model"] = new_model
    pipeline.vectorization_config = vectorization_config
    pipeline.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return result

@router.get("/embedding-models")
async def list_embedding_models():
    """List available embedding models"""
    
    return {
        "embedding_models": [
            {
                "name": "text-embedding-3-small",
                "provider": "OpenAI",
                "dimensions": 1536,
                "description": "OpenAI's latest small embedding model"
            },
            {
                "name": "text-embedding-3-large",
                "provider": "OpenAI", 
                "dimensions": 3072,
                "description": "OpenAI's latest large embedding model"
            },
            {
                "name": "text-embedding-ada-002",
                "provider": "OpenAI",
                "dimensions": 1536,
                "description": "OpenAI's previous generation embedding model"
            },
            {
                "name": "embed-english-v3.0",
                "provider": "Cohere",
                "dimensions": 1024,
                "description": "Cohere's English embedding model"
            },
            {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "provider": "HuggingFace",
                "dimensions": 384,
                "description": "Lightweight sentence transformer model"
            },
            {
                "name": "sentence-transformers/all-mpnet-base-v2",
                "provider": "HuggingFace",
                "dimensions": 768,
                "description": "High-quality sentence transformer model"
            }
        ]
    }

@router.post("/{pipeline_id}/run")
async def run_pipeline(
    pipeline_id: str,
    run_type: str = "manual",
    parameters: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Execute a RAG pipeline run"""
    
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
    
    # Create pipeline run
    run_id = uuid.uuid4()
    pipeline_run = RAGPipelineRun(
        id=run_id,
        pipeline_id=pipeline_id,
        run_type=run_type,
        status="running",
        input_data=parameters or {},
        started_at=datetime.utcnow()
    )
    
    db.add(pipeline_run)
    await db.commit()
    
    try:
        # Execute pipeline
        result = await rag_service.execute_pipeline(
            pipeline_id=pipeline_id,
            parameters=parameters or {}
        )
        
        # Update run status
        pipeline_run.status = "completed"
        pipeline_run.output_summary = result
        pipeline_run.completed_at = datetime.utcnow()
        pipeline_run.duration_seconds = int(
            (pipeline_run.completed_at - pipeline_run.started_at).total_seconds()
        )
        
    except Exception as e:
        logger.error(f"Pipeline run failed: {e}")
        pipeline_run.status = "failed"
        pipeline_run.error_details = str(e)
        pipeline_run.completed_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "run_id": str(run_id),
        "status": pipeline_run.status,
        "result": pipeline_run.output_summary,
        "error": pipeline_run.error_details
    }

@router.get("/{pipeline_id}/runs")
async def list_pipeline_runs(
    pipeline_id: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List runs for a RAG pipeline"""
    
    runs = await db.execute(
        select(RAGPipelineRun)
        .where(RAGPipelineRun.pipeline_id == pipeline_id)
        .order_by(RAGPipelineRun.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    return runs.scalars().all()

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
