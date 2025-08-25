# Enhanced RAG System with Docling and Langgraph

This document describes the enhanced RAG (Retrieval-Augmented Generation) system that provides advanced document processing capabilities with Docling integration, Langgraph workflows, and MCP (Model Context Protocol) support.

## 🚀 Features

### Advanced Document Processing
- **Docling Integration**: State-of-the-art PDF parsing with table and image extraction
- **Multi-format Support**: PDF, DOCX, TXT, MD, CSV, HTML processing
- **OCR Capabilities**: Multi-language text extraction from images and scanned documents
- **Table Extraction**: Preserves table structure and enables table-specific search
- **Image Processing**: Generates descriptions for images and figures using vision models
- **Metadata Extraction**: Automatic document property and structure analysis

### RAG Pipeline Features
- **Multiple Chunking Strategies**: Semantic, recursive, character-based, and custom chunking
- **Hybrid Search**: Combines semantic and keyword search for optimal retrieval
- **Vector Databases**: Support for FAISS, ChromaDB, PGVector, and Elasticsearch
- **Embedding Models**: OpenAI, HuggingFace, Azure OpenAI, and local models
- **Quality Scoring**: Automatic relevance and quality assessment of chunks

### Agent Integration
- **Langgraph Workflows**: Multi-step agent workflows with state management
- **MCP Server**: Standard protocol for external agent integration
- **Tool Creation**: Dynamic tool generation for agent ecosystems
- **Background Processing**: Non-blocking document upload and processing

### Monitoring and Observability
- **Health Checks**: Comprehensive system health monitoring
- **Metrics Collection**: Performance and usage metrics via Prometheus
- **Grafana Dashboards**: Visual monitoring of RAG pipeline performance
- **Logging**: Structured logging with multiple levels and outputs

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Enhanced RAG    │    │  Vector Store   │
│   Upload UI     │───▶│   Service        │───▶│   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Docling        │
                    │   Processor      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Langgraph      │
                    │   Workflows      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   MCP Gateway    │
                    │   (Agents)       │
                    └──────────────────┘
```

### Service Architecture

- **Enhanced RAG Service** (Port 8005): Main service handling document processing and search
- **ChromaDB** (Port 8000): Vector database for embeddings storage
- **PostgreSQL** (Port 5432): Metadata and configuration storage with PGVector extension
- **Redis** (Port 6379): Caching and session management
- **Elasticsearch** (Port 9200): Optional hybrid search capabilities
- **MinIO** (Port 9000/9001): Document storage and management
- **Prometheus** (Port 9090): Metrics collection
- **Grafana** (Port 3000): Monitoring dashboards

## 🛠️ Installation and Setup

### Prerequisites

- Docker Desktop
- Docker Compose
- Git
- At least 8GB RAM (recommended 16GB)
- 20GB+ free disk space

### Quick Start

1. **Clone the repository** (if not already cloned):
   ```bash
   git clone <repository-url>
   cd lcnc-multiagent-platform
   ```

2. **Run the build script**:

   **Linux/macOS:**
   ```bash
   ./scripts/build-rag-enhanced.sh build
   ```

   **Windows:**
   ```cmd
   scripts\build-rag-enhanced.bat build
   ```

3. **Configure environment variables**:
   Edit `.env.rag` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   ```

4. **Start the services**:
   ```bash
   ./scripts/build-rag-enhanced.sh start
   ```

5. **Verify installation**:
   ```bash
   ./scripts/build-rag-enhanced.sh health
   ```

### Manual Docker Compose Setup

If you prefer manual setup:

```bash
# Build the enhanced RAG service
docker build -f backend/services/tools/Dockerfile.rag-enhanced \
  -t agenticai/rag-enhanced:latest \
  backend/services/tools/

# Start all services
docker-compose -f docker-compose.rag-enhanced.yml up -d

# Check status
docker-compose -f docker-compose.rag-enhanced.yml ps
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env.rag`:

#### Database Configuration
```env
POSTGRES_DB=agenticai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://postgres:password@postgres:5432/agenticai
```

#### RAG Service Configuration
```env
# Feature toggles
DOCLING_ENABLED=true
LANGGRAPH_ENABLED=true
MCP_SERVER_ENABLED=true
ENABLE_TABLE_EXTRACTION=true
ENABLE_IMAGE_PROCESSING=true
ENABLE_OCR=true

# Performance settings
MAX_UPLOAD_SIZE_MB=500
CHUNK_SIZE_DEFAULT=1000
CHUNK_OVERLAP_DEFAULT=200
EMBEDDING_BATCH_SIZE=32
SEARCH_RESULTS_LIMIT=100
```

#### API Keys
```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

### Vector Database Configuration

The system supports multiple vector databases:

#### ChromaDB (Default)
```yaml
chromadb:
  image: ghcr.io/chroma-core/chroma:latest
  ports:
    - "8000:8000"
  environment:
    CHROMA_SERVER_HOST: 0.0.0.0
    CHROMA_SERVER_HTTP_PORT: 8000
```

#### PGVector
```env
# In your tool instance configuration
VECTOR_DB_TYPE=pgvector
VECTOR_DB_CONNECTION_STRING=postgresql://user:pass@postgres:5432/dbname
```

#### FAISS (In-Memory)
```env
VECTOR_DB_TYPE=faiss
VECTOR_DB_PERSIST_PATH=/app/vector_db/faiss_index
```

## 📝 Usage Guide

### 1. Creating a RAG Pipeline

**Via API:**
```bash
curl -X POST "http://localhost:8005/rag-pipelines-v2/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Document Knowledge Base",
    "description": "Advanced RAG pipeline with Docling processing",
    "tool_instance_id": "your-tool-instance-id",
    "data_sources": [],
    "vectorization_config": {
      "embedding_model": "text-embedding-3-small",
      "chunk_size": 1000,
      "chunk_overlap": 200,
      "text_splitter": "semantic"
    },
    "ingestion_config": {
      "use_docling": true,
      "extract_tables": true,
      "extract_images": true,
      "llm_preprocessing": true
    }
  }'
```

**Via Frontend:**
1. Navigate to Tools → RAG Pipelines
2. Click "Create Pipeline"
3. Configure advanced settings including Docling options
4. Save the pipeline

### 2. Uploading Documents

**Advanced Upload with Processing Options:**
```bash
curl -X POST "http://localhost:8005/rag-pipelines-v2/{pipeline_id}/documents/upload-advanced" \
  -F "files=@document.pdf" \
  -F "metadata={\"title\":\"Important Document\",\"tags\":[\"research\"]}" \
  -F "processing_options={\"use_docling\":true,\"extract_tables\":true,\"extract_images\":true}"
```

**Via Frontend Enhanced Upload Component:**
1. Go to your RAG pipeline
2. Use the enhanced document upload interface
3. Configure processing options (Docling, table extraction, etc.)
4. Upload files with real-time progress tracking

### 3. Searching Documents

**Advanced Search with Content Types:**
```bash
curl -X POST "http://localhost:8005/rag-pipelines-v2/{pipeline_id}/search-advanced" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "k": 10,
    "search_strategy": "semantic",
    "include_tables": true,
    "include_images": true,
    "filters": {
      "content_type": ["text", "table"]
    }
  }'
```

**Response includes:**
- Text chunks with context
- Table data with structure preserved
- Image descriptions and metadata
- Relevance scores and source information

### 4. Langgraph Workflows

**Create a Simple Q&A Workflow:**
```python
from langgraph_integration_v2 import create_default_rag_integration

# Initialize integration
integration = await create_default_rag_integration("postgresql://...")

# Execute workflow
response = await integration.execute_workflow(
    "simple-qa",
    "What are the main findings in the research documents?"
)
```

**Available Workflow Types:**
- `simple-qa`: Basic question-answering
- `research`: Comprehensive research across multiple sources
- `document-analysis`: Upload and analyze documents

### 5. MCP Integration

**Get MCP Configuration:**
```bash
curl "http://localhost:8005/rag-pipelines-v2/{pipeline_id}/mcp-config"
```

**Use with MCP Clients:**
The RAG system exposes tools that can be used by MCP-compatible agents:
- `rag_search`: Search knowledge base
- `rag_upload`: Upload and process documents
- `rag_pipeline_stats`: Get pipeline statistics

## 🔍 Monitoring and Maintenance

### Health Checks

**System Health:**
```bash
curl "http://localhost:8005/health"
curl "http://localhost:8005/rag-pipelines-v2/health"
```

**Detailed Pipeline Health:**
```bash
curl "http://localhost:8005/rag-pipelines-v2/{pipeline_id}/health-detailed"
```

### Monitoring Dashboards

- **Grafana**: http://localhost:3000 (admin/admin_change_me)
- **Prometheus**: http://localhost:9090
- **Service Metrics**: http://localhost:8005/metrics

### Log Management

**View Service Logs:**
```bash
# All services
docker-compose -f docker-compose.rag-enhanced.yml logs -f

# Specific service
docker-compose -f docker-compose.rag-enhanced.yml logs -f rag-enhanced
```

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning conditions
- `ERROR`: Error conditions

### Performance Tuning

**Memory Optimization:**
```env
# Adjust based on available resources
MEMORY_LIMIT=4G
OMP_NUM_THREADS=4
EMBEDDING_BATCH_SIZE=32
```

**Concurrent Processing:**
```env
CONCURRENT_UPLOADS=5
VECTOR_INDEX_THREADS=4
MAX_WORKERS=4
```

## 🛡️ Security Considerations

### API Key Management
- Store API keys in environment variables
- Use strong, unique passwords for all services
- Regularly rotate credentials

### Network Security
- Services communicate within isolated Docker network
- External access only through specified ports
- Consider using reverse proxy for production

### Data Privacy
- Document content is processed locally by default
- Configure encryption for data at rest
- Implement access controls for sensitive documents

## 🔧 Troubleshooting

### Common Issues

**1. Service Won't Start**
```bash
# Check Docker resources
docker system df
docker system prune

# Check logs
docker-compose -f docker-compose.rag-enhanced.yml logs rag-enhanced
```

**2. Memory Issues**
```bash
# Reduce memory usage
export MEMORY_LIMIT=2G
export EMBEDDING_BATCH_SIZE=16
```

**3. Document Processing Fails**
```bash
# Check Docling installation
docker exec rag-enhanced python -c "import docling; print('Docling OK')"

# Check file permissions
docker exec rag-enhanced ls -la /app/temp_uploads
```

**4. Vector Database Connection Issues**
```bash
# Check ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Check network connectivity
docker exec rag-enhanced ping chromadb
```

### Performance Issues

**Slow Document Processing:**
- Reduce `CHUNK_SIZE_DEFAULT`
- Increase `EMBEDDING_BATCH_SIZE`
- Use smaller embedding models
- Enable `SEMANTIC_CHUNKING_ENABLED=false` for faster processing

**High Memory Usage:**
- Reduce `MAX_WORKERS`
- Limit `CONCURRENT_UPLOADS`
- Use `FAISS_NO_AVX2=1` for CPU-only processing

## 📚 API Reference

### Enhanced RAG Endpoints

**Pipeline Management:**
- `GET /rag-pipelines-v2/` - List pipelines
- `POST /rag-pipelines-v2/` - Create pipeline
- `GET /rag-pipelines-v2/{id}` - Get pipeline details
- `PUT /rag-pipelines-v2/{id}` - Update pipeline
- `DELETE /rag-pipelines-v2/{id}` - Delete pipeline

**Document Operations:**
- `POST /rag-pipelines-v2/{id}/documents/upload-advanced` - Advanced upload
- `POST /rag-pipelines-v2/{id}/search-advanced` - Advanced search
- `GET /rag-pipelines-v2/{id}/documents` - List documents
- `DELETE /rag-pipelines-v2/{id}/documents/{doc_id}` - Delete document

**Langgraph Integration:**
- `GET /rag-pipelines-v2/{id}/langgraph-tools` - Get available tools
- `POST /rag-pipelines-v2/{id}/create-langgraph-agent` - Create agent
- `GET /rag-pipelines-v2/{id}/mcp-config` - Get MCP configuration

**Health and Monitoring:**
- `GET /rag-pipelines-v2/health` - Service health
- `GET /rag-pipelines-v2/{id}/health-detailed` - Detailed health check
- `GET /rag-pipelines-v2/{id}/stats` - Pipeline statistics

### Frontend Components

**Enhanced Document Upload:**
```typescript
import EnhancedDocumentUpload from '@/app/tools/components/EnhancedDocumentUpload';

<EnhancedDocumentUpload
  pipelineId="your-pipeline-id"
  onUploadComplete={(results) => console.log('Upload completed:', results)}
  onUploadError={(error) => console.error('Upload failed:', error)}
/>
```

## 🤝 Contributing

### Development Setup

1. **Clone and setup:**
   ```bash
   git clone <repo>
   cd lcnc-multiagent-platform
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r backend/services/tools/requirements-rag.txt
   pip install -r requirements-dev.txt  # If exists
   ```

3. **Run in development mode:**
   ```bash
   # Set development environment
   export NODE_ENV=development
   export PYTHON_ENV=development
   
   # Start services
   docker-compose -f docker-compose.rag-enhanced.yml up -d
   ```

### Testing

```bash
# Run backend tests
cd backend/services/tools
python -m pytest tests/

# Run frontend tests
cd frontend
npm test
```

### Adding New Features

1. **Document Processing:** Extend `enhanced_rag_service_v2.py`
2. **Workflows:** Add to `langgraph_integration_v2.py`
3. **API Endpoints:** Update `enhanced_rag_pipeline.py`
4. **Frontend Components:** Extend React components in `/components`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please:
1. Check this README and troubleshooting section
2. Review service logs for error messages
3. Open an issue with detailed error information and reproduction steps

---

## 🔄 Updates and Changelog

### Version 2.0.0
- Added Docling integration for advanced PDF processing
- Implemented Langgraph workflows for complex agent interactions
- Added MCP server support for external agent integration
- Enhanced document upload with real-time processing
- Added comprehensive monitoring and observability
- Improved performance and scalability

### Version 1.x
- Basic RAG functionality
- Simple document upload and search
- PostgreSQL and vector database integration