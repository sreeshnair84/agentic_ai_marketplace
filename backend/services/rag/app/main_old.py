"""
RAG (Retrieval Augmented Generation) Service with PGVector
"""

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
import json
import uuid
import os
import tempfile
from contextlib import asynccontextmanager
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import google.generativeai as genai
import openai
import httpx
import aiofiles
from pathlib import Path
import numpy as np

# Document processing imports
import pypdf
from docx import Document as DocxDocument

# Local imports
from .config import rag_config
from .vector_store import vector_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))

# Global variables
async_engine = None
async_session_maker = None

# Pydantic models
class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    source: Optional[str] = None
    document_type: Optional[str] = None
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    file_size: Optional[int] = None
    tags: List[str] = Field(default_factory=list)

class DocumentCreate(BaseModel):
    content: str = Field(..., description="Document content")
    metadata: Optional[DocumentMetadata] = Field(default_factory=DocumentMetadata)

class DocumentResponse(BaseModel):
    id: str
    content: str
    metadata: DocumentMetadata
    chunks_count: int
    indexed_at: datetime

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    collection_name: str = Field(default="default", description="Collection to search")
    n_results: int = Field(default=5, description="Number of results to return")
    include_content: bool = Field(default=True, description="Include document content")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")

class SearchResult(BaseModel):
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]

class RAGRequest(BaseModel):
    query: str = Field(..., description="User query")
    collection_name: str = Field(default="default", description="Collection to search")
    n_context: int = Field(default=3, description="Number of context documents")
    model: str = Field(default="gemini-1.5-pro", description="Model to use for generation")
    max_tokens: int = Field(default=1000, description="Maximum tokens in response")

class RAGResponse(BaseModel):
    query: str
    generated_response: str
    context_documents: List[SearchResult]
    model_used: str
    generation_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global async_engine, async_session_maker
    
    # Startup
    logger.info("Starting RAG service with PGVector...")
    
    try:
        # Initialize database connection
        async_engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_size=20,
            max_overflow=30
        )
        
        # Create async session maker
        async_session_maker = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        
        # Test database connection
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("Connected to PostgreSQL with PGVector")
        
        # Load configuration from database
        async with async_session_maker() as session:
            await rag_config.load_config(session)
        
        logger.info("RAG configuration loaded from database")
        
        # Create upload directory
        UPLOAD_DIR.mkdir(exist_ok=True)
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG service...")
    if async_engine:
        await async_engine.dispose()


app = FastAPI(
    title="RAG Service",
    description="Retrieval Augmented Generation service with PGVector and database-driven configuration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_db_session():
    """Dependency to get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """Health check endpoint"""
    
    # Refresh configuration if needed
    await rag_config.refresh_if_needed(db)
    
    pgvector_status = "disconnected"
    if async_engine:
        try:
            async with async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            pgvector_status = "connected"
        except Exception:
            pgvector_status = "error"
    
    # Get status based on loaded configuration
    embedding_status = "configured" if rag_config.embedding_config else "not_configured"
    llm_status = "configured" if rag_config.llm_config else "not_configured"
    
    return {
        "status": "healthy", 
        "service": "rag",
        "version": "1.0.0",
        "features": {
            "pgvector": pgvector_status,
            "embedding_model": embedding_status,
            "llm_model": llm_status,
            "document_indexing": True,
            "semantic_search": True,
            "vector_database": True,
            "file_upload": True
        },
        "config": {
            "embedding_model": rag_config.get_embedding_model_name(),
            "llm_model": rag_config.get_llm_model_name(),
            "embedding_dimensions": rag_config.get_embedding_dimensions(),
            "similarity_threshold": rag_config.get_similarity_threshold(),
            "last_config_refresh": rag_config.last_refresh.isoformat() if rag_config.last_refresh else None
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RAG Service",
        "version": "1.0.0",
        "description": "Retrieval Augmented Generation service with ChromaDB and Gemini integration",
        "endpoints": {
            "documents": "/documents",
            "upload": "/documents/upload",
            "search": "/search",
            "generate": "/generate",
            "collections": "/collections",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/collections")
async def list_collections(db: AsyncSession = Depends(get_db_session)):
    """List all collections (namespaces)"""
    
    try:
        namespaces = await vector_store.list_namespaces(db)
        
        return {
            "collections": namespaces,
            "total": len(namespaces)
        }
        
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list collections: {str(e)}"
        )


@app.post("/collections", status_code=201)
async def create_collection(
    name: str = Form(...),
    metadata: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new collection (namespace)"""
    
    try:
        result = await vector_store.create_namespace(name, db)
        
        return {
            "name": result["name"],
            "document_count": result["document_count"],
            "status": result["status"],
            "message": f"Collection '{name}' ready for use"
        }
        
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create collection: {str(e)}"
        )


@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str, db: AsyncSession = Depends(get_db_session)):
    """Delete a collection (namespace)"""
    
    try:
        result = await vector_store.delete_namespace(collection_name, db)
        
        return {
            "message": f"Collection '{collection_name}' deleted successfully",
            "deleted_documents": result["deleted_documents"]
        }
        
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to delete collection: {str(e)}"
        )


@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_name: str = Form(default="default"),
    title: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Upload and index a document"""
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix.lower() if file.filename else ""
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Extract text content based on file type
        if file_extension == ".pdf":
            text_content = extract_pdf_text(file_path)
        elif file_extension in [".docx", ".doc"]:
            text_content = extract_docx_text(file_path)
        elif file_extension == ".txt":
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                text_content = await f.read()
        else:
            # Try to read as text
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    text_content = await f.read()
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file_extension}"
                )
        
        # Create metadata
        metadata = DocumentMetadata(
            title=title or file.filename,
            source=file.filename,
            document_type=file_extension.lstrip('.'),
            file_size=len(content),
            tags=tags.split(',') if tags else []
        )
        
        # Index document
        doc_response = await index_document_content(
            file_id, text_content, metadata, collection_name
        )
        
        return doc_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@app.post("/documents", response_model=DocumentResponse)
async def index_document(
    document: DocumentCreate,
    collection_name: str = "default"
):
    """Index a document from provided content"""
    
    try:
        doc_id = str(uuid.uuid4())
        
        doc_response = await index_document_content(
            doc_id, document.content, document.metadata, collection_name
        )
        
        return doc_response
        
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(e)}"
        )


async def index_document_content(
    doc_id: str,
    content: str,
    metadata: DocumentMetadata,
    collection_name: str
) -> DocumentResponse:
    """Index document content in ChromaDB"""
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except Exception:
        collection = chroma_client.create_collection(name=collection_name)
    
    # Split content into chunks
    chunks = chunk_text(content, chunk_size=1000, overlap=200)
    
    # Prepare data for ChromaDB
    chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    chunk_metadata = []
    
    for i, chunk in enumerate(chunks):
        chunk_meta = {
            "document_id": doc_id,
            "chunk_index": i,
            "title": metadata.title,
            "source": metadata.source,
            "document_type": metadata.document_type,
            "upload_date": metadata.upload_date.isoformat(),
            "tags": ",".join(metadata.tags)
        }
        chunk_metadata.append(chunk_meta)
    
    # Add to collection
    collection.add(
        documents=chunks,
        metadatas=chunk_metadata,
        ids=chunk_ids
    )
    
    logger.info(f"Indexed document {doc_id} with {len(chunks)} chunks")
    
    return DocumentResponse(
        id=doc_id,
        content=content[:500] + "..." if len(content) > 500 else content,
        metadata=metadata,
        chunks_count=len(chunks),
        indexed_at=datetime.utcnow()
    )


@app.post("/search")
async def semantic_search(request: SearchRequest):
    """Perform semantic search on indexed documents"""
    
    try:
        # Get collection
        collection = chroma_client.get_collection(name=request.collection_name)
        
        # Prepare query
        where_filter = request.filter_metadata if request.filter_metadata else None
        
        # Perform search
        results = collection.query(
            query_texts=[request.query],
            n_results=request.n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        search_results = []
        
        if results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                search_results.append(SearchResult(
                    id=results["ids"][0][i],
                    content=doc if request.include_content else "",
                    score=1.0 - distance,  # Convert distance to similarity score
                    metadata=metadata
                ))
        
        return {
            "query": request.query,
            "collection": request.collection_name,
            "results": search_results,
            "total_results": len(search_results),
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {str(e)}"
        )


@app.post("/generate", response_model=RAGResponse)
async def rag_generate(request: RAGRequest):
    """Generate response using RAG (Retrieval + Generation)"""
    
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google AI API key not configured"
        )
    
    start_time = datetime.utcnow()
    
    try:
        # First, perform semantic search to get context
        search_request = SearchRequest(
            query=request.query,
            collection_name=request.collection_name,
            n_results=request.n_context,
            include_content=True
        )
        
        search_response = await semantic_search(search_request)
        context_docs = search_response["results"]
        
        # Prepare context for generation
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc.content}"
            for i, doc in enumerate(context_docs)
        ])
        
        # Generate response using Gemini
        model = genai.GenerativeModel(request.model)
        
        prompt = f"""Based on the following context documents, please answer the user's question. If the answer cannot be found in the context, please say so.

Context:
{context_text}

Question: {request.query}

Answer:"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=request.max_tokens,
                temperature=0.7
            )
        )
        
        end_time = datetime.utcnow()
        generation_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return RAGResponse(
            query=request.query,
            generated_response=response.text,
            context_documents=context_docs,
            model_used=request.model,
            generation_time_ms=generation_time_ms
        )
        
    except Exception as e:
        logger.error(f"Error in RAG generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )


def extract_pdf_text(file_path: Path) -> str:
    """Extract text from PDF file"""
    
    try:
        reader = pypdf.PdfReader(str(file_path))
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise Exception(f"Failed to extract PDF text: {e}")


def extract_docx_text(file_path: Path) -> str:
    """Extract text from DOCX file"""
    
    try:
        doc = DocxDocument(str(file_path))
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        raise Exception(f"Failed to extract DOCX text: {e}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence or word boundary
        if end < len(text):
            # Look for sentence end
            last_period = text.rfind('.', start, end)
            last_question = text.rfind('?', start, end)
            last_exclamation = text.rfind('!', start, end)
            
            sentence_end = max(last_period, last_question, last_exclamation)
            
            if sentence_end > start:
                end = sentence_end + 1
            else:
                # Look for word boundary
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = max(start + 1, end - overlap)
        
        # Avoid infinite loop
        if start >= len(text):
            break
    
    return chunks


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
