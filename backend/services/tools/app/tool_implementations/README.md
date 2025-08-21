# Physical Tool Implementations

This directory contains physical implementations of tools as Python classes, replacing the previous string-based tool configurations.

## Directory Structure

```
tool_implementations/
├── rag/
│   └── advanced_rag_tool.py          # RAG Pipeline with document processing
├── sql_agent/
│   └── intelligent_sql_agent.py      # Natural language to SQL converter
├── web_scraper/
│   └── advanced_web_scraper.py       # Web scraping with JS rendering
├── api_integration/
│   └── universal_api_integration.py  # Universal API client
└── README.md                         # This file
```

## Tool Categories

### 1. RAG (Retrieval-Augmented Generation)
- **File**: `rag/advanced_rag_tool.py`
- **Class**: `AdvancedRAGTool`
- **Description**: Comprehensive RAG pipeline with document processing, multiple embedding models, and chunking strategies
- **Features**:
  - Document ingestion (PDF, DOCX, TXT)
  - Multiple embedding models (OpenAI, Sentence Transformers)
  - Chunking strategies (fixed_size, sentence, recursive)
  - Vector search with similarity scoring
  - Cache management

### 2. SQL Agent
- **File**: `sql_agent/intelligent_sql_agent.py`
- **Class**: `IntelligentSQLAgent`
- **Description**: Natural language to SQL converter with safety controls
- **Features**:
  - Natural language query processing
  - SQL query generation using AI
  - Safety validation and injection prevention
  - Query optimization suggestions
  - Database schema introspection
  - Multiple database support (PostgreSQL, MySQL, etc.)

### 3. Web Scraper
- **File**: `web_scraper/advanced_web_scraper.py`
- **Class**: `AdvancedWebScraper`
- **Description**: Intelligent web scraping with JavaScript rendering
- **Features**:
  - HTTP and browser-based scraping
  - JavaScript rendering support
  - Rate limiting and robots.txt respect
  - Content extraction and cleaning
  - Structured data extraction
  - Table data extraction

### 4. API Integration
- **File**: `api_integration/universal_api_integration.py`
- **Class**: `UniversalAPIIntegration`
- **Description**: Universal API client with authentication and transformation
- **Features**:
  - Multiple authentication methods (Bearer, API Key, OAuth2, etc.)
  - Request/response transformation
  - Rate limiting and retry logic
  - Pagination handling
  - Webhook support
  - Response caching

## Usage

### 1. Discovery and Loading

```python
from backend.services.tools.app.physical_tool_loader import PhysicalToolManager

# Initialize the tool manager
tool_manager = PhysicalToolManager("path/to/tool_implementations")

# Discover available tools
tools = tool_manager.list_tools()
print(f"Found {len(tools)} tools")

# Get tool information
tool_info = tool_manager.get_tool_info("advanced_rag_tool")
```

### 2. Tool Initialization

```python
# Initialize a RAG tool
rag_config = {
    "openai_api_key": "your-api-key",
    "embedding_model": "text-embedding-3-small",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "vector_store_path": "./vectors"
}

result = await tool_manager.initialize_tool("advanced_rag_tool", rag_config)
if result["status"] == "success":
    print("RAG tool initialized successfully")
```

### 3. Tool Execution

```python
# Execute RAG operations
ingest_result = await tool_manager.execute_tool(
    "advanced_rag_tool", 
    "ingest_document",
    file_path="document.pdf",
    metadata={"source": "research_paper"}
)

search_result = await tool_manager.execute_tool(
    "advanced_rag_tool",
    "semantic_search",
    query="What are the main findings?",
    top_k=5
)
```

### 4. SQL Agent Usage

```python
# Initialize SQL Agent
sql_config = {
    "database_url": "postgresql://user:pass@localhost:5432/db",
    "safety_mode": "strict",
    "max_rows": 1000,
    "llm_model": "gpt-4"
}

await tool_manager.initialize_tool("intelligent_sql_agent", sql_config)

# Natural language query
result = await tool_manager.execute_tool(
    "intelligent_sql_agent",
    "natural_language_query",
    question="Show me the top 10 customers by revenue this year"
)

print(f"Generated SQL: {result['result']['sql_query']}")
print(f"Results: {result['result']['results']}")
```

### 5. Web Scraper Usage

```python
# Initialize Web Scraper
scraper_config = {
    "javascript_enabled": True,
    "respect_robots_txt": True,
    "delay_between_requests": 1.0,
    "max_pages": 10
}

await tool_manager.initialize_tool("advanced_web_scraper", scraper_config)

# Scrape a single URL
result = await tool_manager.execute_tool(
    "advanced_web_scraper",
    "scrape_url",
    url="https://example.com",
    extraction_config={
        "extract_links": True,
        "extract_images": True,
        "extract_main_content": True
    }
)

# Crawl a website
crawl_result = await tool_manager.execute_tool(
    "advanced_web_scraper",
    "crawl_website",
    start_url="https://example.com",
    crawl_config={
        "max_depth": 2,
        "same_domain_only": True,
        "max_pages": 20
    }
)
```

### 6. API Integration Usage

```python
# Initialize API Integration
api_config = {
    "base_url": "https://api.example.com",
    "authentication": {
        "type": "bearer",
        "token": "your-bearer-token"
    },
    "rate_limit": 100,
    "timeout": 30
}

await tool_manager.initialize_tool("universal_api_integration", api_config)

# Make API requests
result = await tool_manager.execute_tool(
    "universal_api_integration",
    "make_request",
    method="GET",
    endpoint="/users",
    params={"limit": 10},
    transform_config={
        "type": "jmespath",
        "expression": "data[].{id: id, name: name, email: email}"
    }
)

# Paginated requests
paginated_result = await tool_manager.execute_tool(
    "universal_api_integration",
    "paginated_request",
    method="GET",
    endpoint="/posts",
    pagination_config={
        "type": "page",
        "page_param": "page",
        "size_param": "limit",
        "page_size": 50,
        "max_pages": 5
    }
)
```

## API Endpoints

The physical tools are exposed through REST API endpoints:

### Discovery
- `GET /api/physical-tools/discover` - List all available tools
- `GET /api/physical-tools/{tool_name}/info` - Get tool details
- `GET /api/physical-tools/{tool_name}/schemas` - Get tool schemas

### Management
- `POST /api/physical-tools/{tool_name}/initialize` - Initialize a tool
- `POST /api/physical-tools/{tool_name}/execute/{operation}` - Execute tool operation
- `DELETE /api/physical-tools/{tool_name}/cleanup` - Cleanup tool instance

### Validation
- `POST /api/physical-tools/{tool_name}/validate-config` - Validate configuration
- `POST /api/physical-tools/{tool_name}/test` - Test tool with sample config

### Registry
- `GET /api/physical-tools/registry/create` - Create tool registry
- `POST /api/physical-tools/registry/save` - Save registry to file

### Examples
- `GET /api/physical-tools/{tool_name}/example-config` - Get example configuration

### Health
- `GET /api/physical-tools/health` - Check system health

## Tool Schemas

Each tool implements three JSON schemas:

1. **Config Schema**: Defines the tool's configuration parameters
2. **Input Schema**: Defines the input format for tool operations
3. **Output Schema**: Defines the output format for tool results

Example for RAG tool:
```python
TOOL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "openai_api_key": {"type": "string"},
        "embedding_model": {
            "type": "string",
            "enum": ["text-embedding-3-small", "text-embedding-3-large"],
            "default": "text-embedding-3-small"
        },
        "chunk_size": {
            "type": "integer",
            "minimum": 100,
            "maximum": 8000,
            "default": 1000
        }
    },
    "required": ["openai_api_key"]
}
```

## Adding New Tools

To add a new tool:

1. Create a new directory under `tool_implementations/`
2. Create a Python file with your tool class
3. Implement required methods (at minimum `__init__`)
4. Define the three schemas: `TOOL_CONFIG_SCHEMA`, `INPUT_SCHEMA`, `OUTPUT_SCHEMA`
5. Add an `initialize()` method if needed
6. Add operation methods as needed
7. Add a `cleanup()` method for resource cleanup

Example structure:
```python
class MyNewTool:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def initialize(self):
        # Initialize resources
        pass
    
    async def my_operation(self, param1: str, param2: int) -> Dict[str, Any]:
        # Implement your operation
        return {"status": "success", "result": "operation completed"}
    
    async def cleanup(self):
        # Cleanup resources
        pass

# Define schemas
TOOL_CONFIG_SCHEMA = {...}
INPUT_SCHEMA = {...}
OUTPUT_SCHEMA = {...}
```

## Best Practices

1. **Error Handling**: Always wrap operations in try-catch blocks
2. **Logging**: Use the logger for debugging and monitoring
3. **Resource Management**: Implement proper cleanup methods
4. **Configuration Validation**: Use JSON schema validation
5. **Async Operations**: Use async/await for I/O operations
6. **Type Hints**: Use proper type hints for better IDE support
7. **Documentation**: Document your tool class and methods
8. **Testing**: Include test configurations and examples

## Dependencies

Common dependencies used across tools:
- `aiohttp` - Async HTTP client
- `openai` - OpenAI API client
- `sqlalchemy` - Database toolkit
- `beautifulsoup4` - HTML parsing
- `selenium` - Browser automation
- `pandas` - Data manipulation
- `numpy` - Numerical computations
- `jsonschema` - Schema validation

Install dependencies:
```bash
pip install aiohttp openai sqlalchemy beautifulsoup4 selenium pandas numpy jsonschema
```

## Troubleshooting

### Import Errors
- Ensure all required dependencies are installed
- Check Python path and module imports
- Verify tool file structure and naming

### Tool Not Found
- Check tool discovery with `/api/physical-tools/discover`
- Verify tool file is in correct directory
- Check tool class naming conventions

### Configuration Errors
- Validate configuration against schema
- Use `/api/physical-tools/{tool_name}/example-config` for examples
- Check required vs optional parameters

### Execution Errors
- Check tool initialization status
- Verify operation names and parameters
- Review tool logs for detailed error messages

## Migration from String-based Tools

The physical tool implementations replace the previous string-based tool configurations:

**Before**: Tools were defined as string configurations in the database
**After**: Tools are implemented as Python classes with proper structure

Benefits:
- Better code organization and maintainability
- IDE support with autocompletion and type checking
- Proper error handling and logging
- Schema validation
- Version control and collaboration
- Testing capabilities
- Resource management
