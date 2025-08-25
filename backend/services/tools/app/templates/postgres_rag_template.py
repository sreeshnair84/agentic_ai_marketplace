"""
PostgreSQL Enhanced RAG Tool Template
Template definition for creating PostgreSQL-based RAG tool instances
"""

from typing import Dict, Any, List
import uuid
from datetime import datetime

# Template definition for PostgreSQL RAG Tool
POSTGRES_RAG_TEMPLATE = {
    "id": str(uuid.uuid4()),
    "name": "postgres_enhanced_rag",
    "display_name": "PostgreSQL Enhanced RAG System",
    "type": "rag",
    "category": "rag",
    "description": "Advanced RAG system with PostgreSQL/pgvector backend, supporting document processing with Docling, table/image extraction, and semantic search",
    "long_description": """
    This template creates a comprehensive RAG (Retrieval-Augmented Generation) system using PostgreSQL with pgvector extension for vector storage and similarity search.
    
    Key Features:
    - Advanced document processing with Docling integration
    - Support for PDF, DOCX, TXT, MD file formats
    - Table and image extraction from documents
    - Multiple chunking strategies (recursive, character, semantic)
    - Multiple embedding providers (OpenAI, HuggingFace)
    - PostgreSQL with pgvector for efficient vector storage
    - Semantic search with metadata filtering
    - Document deduplication and management
    - Comprehensive analytics and statistics
    """,
    "version": "2.0.0",
    "tags": ["rag", "postgres", "vector-search", "docling", "document-processing"],
    "is_active": True,
    "documentation": """
    ## PostgreSQL Enhanced RAG System

    ### Prerequisites
    - PostgreSQL database with pgvector extension installed
    - OpenAI API key (if using OpenAI embeddings)
    - Docling installed for advanced document processing

    ### Configuration Fields

    **Database Configuration:**
    - `database_url`: PostgreSQL connection URL with pgvector support
    - `table_name`: Base table name for RAG data storage

    **Embedding Configuration:**
    - `embedding_model`: Choose from various embedding models
    - `embedding_provider`: OpenAI or HuggingFace
    - `openai_api_key`: Required if using OpenAI embeddings

    **Processing Configuration:**
    - `chunk_size`: Size of text chunks (100-8000 characters)
    - `chunk_overlap`: Overlap between chunks
    - `chunking_strategy`: recursive, character, or semantic
    - `use_docling`: Enable advanced document processing
    - `extract_tables`: Extract table content from documents
    - `extract_images`: Extract image descriptions
    - `quality_threshold`: Content quality filtering threshold

    ### Operations Supported

    1. **ingest_document**: Upload and process documents
    2. **search**: Semantic search with advanced filtering
    3. **get_statistics**: Retrieve system statistics
    4. **delete_document**: Remove documents from the system
    5. **health_check**: Check system health and connectivity

    ### Example Usage

    ```python
    # Ingest a document
    {
        "operation": "ingest_document",
        "file_path": "/path/to/document.pdf",
        "metadata": {"category": "research", "tags": ["ml", "ai"]}
    }

    # Search documents
    {
        "operation": "search",
        "query": "machine learning algorithms",
        "top_k": 10,
        "content_types": ["text", "table"],
        "filters": {"category": "research"}
    }
    ```
    """,
    "schema_definition": {
        "type": "object",
        "properties": {
            # Database Configuration
            "database_url": {
                "type": "string",
                "title": "Database URL",
                "description": "PostgreSQL connection URL with pgvector support",
                "default": "postgresql://username:password@localhost:5432/ragdb",
                "examples": [
                    "postgresql://user:pass@localhost:5432/ragdb",
                    "postgresql://user:pass@postgres:5432/agenticai?sslmode=require"
                ]
            },
            "table_name": {
                "type": "string", 
                "title": "Table Name",
                "description": "Base table name for storing RAG documents",
                "default": "rag_documents",
                "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$"
            },
            
            # Embedding Configuration
            "embedding_model": {
                "type": "string",
                "title": "Embedding Model",
                "description": "Model for text vectorization",
                "default": "text-embedding-3-small",
                "enum": [
                    "text-embedding-3-small",
                    "text-embedding-3-large", 
                    "text-embedding-ada-002",
                    "all-MiniLM-L6-v2",
                    "all-mpnet-base-v2"
                ]
            },
            "embedding_provider": {
                "type": "string",
                "title": "Embedding Provider",
                "description": "Provider for embedding models",
                "default": "openai",
                "enum": ["openai", "huggingface"]
            },
            "openai_api_key": {
                "type": "string",
                "title": "OpenAI API Key",
                "description": "OpenAI API key for embeddings (required if using OpenAI provider)",
                "format": "password"
            },
            
            # Text Processing Configuration
            "chunk_size": {
                "type": "integer",
                "title": "Chunk Size",
                "description": "Size of text chunks in characters",
                "default": 1000,
                "minimum": 100,
                "maximum": 8000
            },
            "chunk_overlap": {
                "type": "integer",
                "title": "Chunk Overlap",
                "description": "Character overlap between chunks",
                "default": 200,
                "minimum": 0,
                "maximum": 1000
            },
            "chunking_strategy": {
                "type": "string",
                "title": "Chunking Strategy", 
                "description": "Method for splitting text into chunks",
                "default": "recursive",
                "enum": ["recursive", "character", "semantic"],
                "enum_descriptions": {
                    "recursive": "Hierarchical splitting by paragraphs, sentences, then words",
                    "character": "Simple character-based splitting",
                    "semantic": "Semantic similarity-based chunking"
                }
            },
            
            # Advanced Processing Options
            "use_docling": {
                "type": "boolean",
                "title": "Use Docling Processing",
                "description": "Enable advanced document processing with Docling",
                "default": True
            },
            "extract_tables": {
                "type": "boolean", 
                "title": "Extract Tables",
                "description": "Extract and process table content from documents",
                "default": True
            },
            "extract_images": {
                "type": "boolean",
                "title": "Extract Images",
                "description": "Extract and generate descriptions for images",
                "default": True
            },
            "quality_threshold": {
                "type": "number",
                "title": "Quality Threshold",
                "description": "Minimum quality score for content inclusion",
                "default": 0.7,
                "minimum": 0.0,
                "maximum": 1.0
            }
        },
        "required": ["database_url", "embedding_model", "embedding_provider"],
        "dependencies": {
            "embedding_provider": {
                "properties": {
                    "embedding_provider": {"const": "openai"}
                },
                "required": ["openai_api_key"]
            }
        }
    },
    "default_config": {
        "database_url": "postgresql://postgres:password@postgres:5432/agenticai",
        "table_name": "rag_documents", 
        "embedding_model": "text-embedding-3-small",
        "embedding_provider": "openai",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "chunking_strategy": "recursive",
        "use_docling": True,
        "extract_tables": True,
        "extract_images": True,
        "quality_threshold": 0.7
    },
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "ingest_document",
                    "search", 
                    "get_statistics",
                    "delete_document",
                    "health_check"
                ],
                "description": "Operation to perform"
            },
            "file_path": {
                "type": "string",
                "description": "Path to document file (for ingest_document)"
            },
            "query": {
                "type": "string",
                "description": "Search query (for search)"
            },
            "top_k": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 5,
                "description": "Number of search results to return"
            },
            "content_types": {
                "type": "array",
                "items": {"type": "string", "enum": ["text", "table", "image"]},
                "description": "Filter results by content type"
            },
            "filters": {
                "type": "object",
                "description": "Additional search filters based on metadata"
            },
            "document_id": {
                "type": "string",
                "description": "Document ID (for delete_document or specific statistics)"
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata for document ingestion"
            }
        },
        "required": ["operation"]
    },
    "output_schema": {
        "type": "object", 
        "properties": {
            "status": {
                "type": "string",
                "enum": ["success", "error", "duplicate"]
            },
            "result": {
                "type": "object",
                "description": "Operation result data"
            },
            "error": {
                "type": "string",
                "description": "Error message if operation failed"
            },
            "processing_time": {
                "type": "number",
                "description": "Time taken to complete the operation"
            }
        },
        "required": ["status"]
    },
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

# Template fields for the UI form
POSTGRES_RAG_TEMPLATE_FIELDS = [
    {
        "id": str(uuid.uuid4()),
        "field_name": "database_url",
        "field_label": "Database URL",
        "field_description": "PostgreSQL connection URL with pgvector extension enabled",
        "field_type": "string",
        "is_required": True,
        "validation_rules": {
            "pattern": r"^postgresql://.*$",
            "message": "Must be a valid PostgreSQL connection URL"
        },
        "default_value": "postgresql://postgres:password@postgres:5432/agenticai",
        "display_order": 1
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "table_name", 
        "field_label": "Table Name",
        "field_description": "Base table name for storing document chunks and embeddings",
        "field_type": "string",
        "is_required": False,
        "default_value": "rag_documents",
        "display_order": 2
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "embedding_model",
        "field_label": "Embedding Model",
        "field_description": "Model used for text vectorization", 
        "field_type": "select",
        "is_required": True,
        "field_options": [
            {"value": "text-embedding-3-small", "label": "OpenAI text-embedding-3-small (Recommended)"},
            {"value": "text-embedding-3-large", "label": "OpenAI text-embedding-3-large (High Performance)"},
            {"value": "text-embedding-ada-002", "label": "OpenAI text-embedding-ada-002 (Legacy)"},
            {"value": "all-MiniLM-L6-v2", "label": "HuggingFace all-MiniLM-L6-v2 (Open Source)"},
            {"value": "all-mpnet-base-v2", "label": "HuggingFace all-mpnet-base-v2 (High Quality)"}
        ],
        "default_value": "text-embedding-3-small",
        "display_order": 3
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "embedding_provider",
        "field_label": "Embedding Provider",
        "field_description": "Service provider for embedding models",
        "field_type": "select", 
        "is_required": True,
        "field_options": [
            {"value": "openai", "label": "OpenAI (Requires API Key)"},
            {"value": "huggingface", "label": "HuggingFace (Local/Free)"}
        ],
        "default_value": "openai",
        "display_order": 4
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "openai_api_key",
        "field_label": "OpenAI API Key", 
        "field_description": "API key for OpenAI embeddings (required if using OpenAI provider)",
        "field_type": "password",
        "is_required": False,
        "conditional_logic": {
            "show_when": {"field": "embedding_provider", "value": "openai"}
        },
        "display_order": 5
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "chunk_size",
        "field_label": "Chunk Size",
        "field_description": "Maximum size of text chunks in characters",
        "field_type": "number",
        "is_required": False,
        "validation_rules": {
            "min": 100,
            "max": 8000
        },
        "default_value": 1000,
        "display_order": 6
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "chunk_overlap",
        "field_label": "Chunk Overlap",
        "field_description": "Number of overlapping characters between chunks",
        "field_type": "number",
        "is_required": False,
        "validation_rules": {
            "min": 0,
            "max": 1000
        },
        "default_value": 200,
        "display_order": 7
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "chunking_strategy",
        "field_label": "Chunking Strategy",
        "field_description": "Method for splitting documents into chunks",
        "field_type": "select",
        "is_required": False,
        "field_options": [
            {"value": "recursive", "label": "Recursive (Recommended) - Smart hierarchical splitting"},
            {"value": "character", "label": "Character - Simple fixed-size splitting"},
            {"value": "semantic", "label": "Semantic - AI-powered semantic splitting"}
        ],
        "default_value": "recursive",
        "display_order": 8
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "use_docling",
        "field_label": "Enable Advanced Processing",
        "field_description": "Use Docling for advanced PDF processing with table and image extraction",
        "field_type": "boolean",
        "is_required": False,
        "default_value": True,
        "display_order": 9
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "extract_tables",
        "field_label": "Extract Tables",
        "field_description": "Extract and process table content from documents",
        "field_type": "boolean",
        "is_required": False,
        "default_value": True,
        "conditional_logic": {
            "show_when": {"field": "use_docling", "value": True}
        },
        "display_order": 10
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "extract_images", 
        "field_label": "Extract Images",
        "field_description": "Extract and generate descriptions for images and figures",
        "field_type": "boolean",
        "is_required": False,
        "default_value": True,
        "conditional_logic": {
            "show_when": {"field": "use_docling", "value": True}
        },
        "display_order": 11
    },
    {
        "id": str(uuid.uuid4()),
        "field_name": "quality_threshold",
        "field_label": "Quality Threshold", 
        "field_description": "Minimum quality score for including content (0.0-1.0)",
        "field_type": "number",
        "is_required": False,
        "validation_rules": {
            "min": 0.0,
            "max": 1.0,
            "step": 0.1
        },
        "default_value": 0.7,
        "display_order": 12
    }
]

# Helper function to create template
def get_postgres_rag_template() -> Dict[str, Any]:
    """Get the PostgreSQL RAG template definition"""
    return POSTGRES_RAG_TEMPLATE

def get_postgres_rag_template_fields() -> List[Dict[str, Any]]:
    """Get the template fields for the UI"""
    return POSTGRES_RAG_TEMPLATE_FIELDS