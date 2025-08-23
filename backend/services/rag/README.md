# RAG Backend Service

## Overview
This service provides Retrieval Augmented Generation (RAG) capabilities, including document ingestion, semantic search, and context-augmented generation using PGVector. It is designed to be modular and configurable via tool templates and instances, supporting multiple embedding and LLM providers.

---

## Key Features
- **Tool Template Driven**: Users select a RAG tool template from the UI and provide connection/configuration details. Tool templates define the vector DB, embedding model, chunking, and retrieval strategies.
- **Document Ingestion**:
  - Upload documents (PDF, DOCX, TXT, etc.) via API
  - Trigger ingestion from a configured path (if set in the tool instance)
- **Embedding Model Management**: Embedding models are managed centrally and associated with tool templates/instances. The correct model is always used for chunk embedding.
- **Docling Integration**: (Planned/Required) Use Docling for robust document parsing, chunking, and preprocessing, replacing or extending the current chunking logic.
- **Semantic Search & RAG**: Query indexed documents using semantic similarity and generate answers with context using the selected LLM.

---

## API Endpoints
- `POST /documents/upload` — Upload and index a document (file upload)
- `POST /documents` — Index a document from provided content
- `POST /search` — Semantic search on indexed documents
- `POST /generate` — RAG (retrieval + generation) endpoint
- `GET /models` — List available LLMs, embedding models, and tool instances
- `POST /models/reload` — Reload model configs from DB
- `GET /health` — Health check

### (Planned) Path-based Ingestion
- Endpoint to trigger ingestion from a configured path, as set in the tool instance configuration. (To be implemented if not present.)

---

## Tool Templates & Instances
- **Tool Templates**: Define reusable configurations for RAG, including vector DB, embedding model, chunking, and retrieval strategies.
- **Tool Instances**: Concrete instantiations of templates with actual connection details, credentials, and runtime parameters. Selected by the user in the UI.
- **Model Association**: Each tool instance references the embedding model to use for chunking and search.

---

## Document Processing & Docling
- **Current**: PDF, DOCX, TXT supported with custom chunking logic.
- **Planned**: Integrate [Docling](https://github.com/docling/docling) for advanced document parsing, chunking, and preprocessing. This will improve chunk quality, support more formats, and enable better metadata extraction.
- **Chunking**: Text is split into overlapping chunks for embedding and search. Docling will replace/extend this logic for more robust handling.

---

## Example Flow
1. **User selects a RAG tool template** in the UI and provides connection/configuration details.
2. **User uploads a document** or triggers ingestion from a configured path.
3. **Backend parses and chunks the document** (Docling planned), generates embeddings using the associated model, and stores them in the vector DB.
4. **User queries** via semantic search or RAG endpoint; the backend retrieves relevant chunks and generates a context-augmented answer using the selected LLM.

---

## Configuration
- All model and tool instance configuration is loaded from the database, not just environment variables.
- Embedding and LLM API keys are securely managed and associated with tool instances.

---

## Future Work
- [ ] Integrate Docling for document parsing and chunking
- [ ] Add/clarify endpoint for path-based ingestion
- [ ] Expand support for additional document formats and chunking strategies
- [ ] Enhance error handling and observability

---

## References
- [Tool Management System Requirements](../../../docs/requirements/tool-management-system.md)
- [Backend Technical Specifications](../../../docs/backend-services/technical-specifications.md)
- [System Architecture](../../../docs/architecture/system-architecture.md)
