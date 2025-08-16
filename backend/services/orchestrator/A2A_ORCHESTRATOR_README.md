# A2A Protocol Orchestrator Implementation

This orchestrator service implements the A2A (Agent-to-Agent) protocol based on the samples from https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/multiagent.

## Overview

The LCNC Orchestrator is a multi-agent coordination service that follows the A2A protocol standard. It acts as a "host agent" that can discover, coordinate, and manage multiple remote agents to accomplish complex tasks.

## Key Features

### 🎯 A2A Protocol Compliance
- Full JSON-RPC 2.0 implementation
- Agent card discovery and registration
- Streaming and synchronous message handling
- A2A-compliant task management

### 🔍 Agent Discovery and Management
- Automatic agent discovery from configured endpoints
- Semantic agent matching based on queries
- Agent health monitoring and status tracking
- Dynamic agent addition and removal

### 🧠 Intelligent Orchestration
- Multi-agent task decomposition
- Parallel and sequential task execution
- Context-aware session management
- Workflow planning and execution

### 🔄 Communication Patterns
- **Synchronous**: `/a2a/message/send` - Direct request/response
- **Streaming**: `/a2a/message/stream` - Real-time streaming responses
- **Broadcast**: Send messages to multiple agents simultaneously

## Architecture

```
LCNC Orchestrator (Port 8003)
├── A2A Protocol Endpoints
│   ├── /a2a/cards - Agent card discovery
│   ├── /a2a/message/send - Synchronous messaging
│   ├── /a2a/message/stream - Streaming messaging
│   └── /a2a/discover - Agent discovery
├── Remote Agent Connections
│   ├── Agents Service (Port 8002)
│   ├── RAG Service (Port 8004)
│   └── Tools Service (Port 8005)
└── Orchestration Engine
    ├── Plan Creation
    ├── Task Distribution
    ├── Result Aggregation
    └── Session Management
```

## A2A Protocol Implementation

### Agent Card

The orchestrator exposes its capabilities through an A2A agent card:

```json
{
  "name": "LCNC Orchestrator Agent",
  "description": "Multi-agent orchestration and workflow coordination for LCNC platform",
  "version": "1.0.0",
  "url": "http://localhost:8003",
  "default_input_modes": ["text"],
  "default_output_modes": ["text"],
  "capabilities": {
    "streaming": true,
    "batch_processing": true,
    "multi_modal": true,
    "persistent_sessions": true
  },
  "skills": [
    {
      "id": "multi_agent_orchestration",
      "name": "Multi-Agent Orchestration",
      "description": "Coordinate multiple agents to complete complex tasks",
      "tags": ["orchestration", "coordination", "planning"]
    },
    {
      "id": "agent_discovery",
      "name": "Agent Discovery and Selection", 
      "description": "Discover and select appropriate agents for tasks",
      "tags": ["discovery", "selection", "routing"]
    }
  ]
}
```

### Message Flow

1. **Client Request** → Orchestrator receives user query
2. **Agent Discovery** → Find suitable agents for the task
3. **Plan Creation** → Create orchestration plan
4. **Task Distribution** → Send tasks to selected agents via A2A
5. **Result Aggregation** → Collect and synthesize results
6. **Response** → Return unified response to client

## API Endpoints

### A2A Protocol Endpoints

- `GET /a2a/cards` - Get orchestrator agent card
- `GET /a2a/cards/{agent_name}` - Get specific agent card
- `POST /a2a/discover` - Discover agents by query
- `POST /a2a/message/send` - Synchronous JSON-RPC messaging
- `POST /a2a/message/stream` - Streaming JSON-RPC messaging

### Management Endpoints

- `GET /a2a/agents` - List all connected agents
- `POST /a2a/agents/add` - Add new remote agent
- `DELETE /a2a/agents/{agent_name}` - Remove agent
- `GET /a2a/health/agents` - Health check all agents
- `GET /a2a/sessions` - List active sessions
- `POST /a2a/orchestrate` - Simple orchestration endpoint

## Usage Examples

### Basic Orchestration

```bash
# Simple query orchestration
curl -X POST "http://localhost:8003/a2a/orchestrate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the sales data and create a summary report",
    "stream": false
  }'
```

### A2A Message Send (JSON-RPC)

```bash
curl -X POST "http://localhost:8003/a2a/message/send" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "id": "task-123",
      "session_id": "session-456",
      "accepted_output_modes": ["text"],
      "message": {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Process this data and generate insights"
          }
        ]
      }
    }
  }'
```

### Agent Discovery

```bash
# Find agents for data analysis
curl "http://localhost:8003/a2a/discover?query=data%20analysis&max_results=3"
```

### Streaming Response

```bash
curl -X POST "http://localhost:8003/a2a/message/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1", 
    "method": "message/stream",
    "params": {
      "id": "task-123",
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Generate a detailed report"}]
      }
    }
  }'
```

## Orchestration Process

### 1. Query Analysis
The orchestrator analyzes incoming queries to understand:
- Required capabilities
- Task complexity
- Potential agent matches
- Execution strategy

### 2. Agent Selection
- Semantic matching based on agent skills and descriptions
- Capability-based filtering
- Tag-based discovery
- Load balancing considerations

### 3. Plan Creation
- Task decomposition
- Dependency analysis
- Resource allocation
- Execution ordering

### 4. Execution Coordination
- Parallel task distribution
- Progress monitoring
- Error handling and recovery
- Result collection

### 5. Response Synthesis
- Result aggregation
- Summary generation
- Context preservation
- Response formatting

## Integration with LCNC Services

### Connected Services

1. **Agents Service (Port 8002)**
   - GeneralAIAgent, TaskExecutorAgent, ConversationAgent
   - Specialized AI processing capabilities
   - Gemini-powered intelligent responses

2. **RAG Service (Port 8004)**
   - Document retrieval and analysis
   - Knowledge-augmented generation
   - Context-aware responses

3. **Tools Service (Port 8005)**
   - MCP protocol integration
   - External tool execution
   - System integration capabilities

### Orchestration Examples

```python
# Multi-agent data processing pipeline
query = "Analyze customer feedback, extract insights, and create visualization"

# Orchestrator coordinates:
# 1. RAG Service - Retrieves relevant documents
# 2. Agents Service - Analyzes sentiment and extracts insights  
# 3. Tools Service - Creates visualizations
# 4. Synthesizes final report
```

## Configuration

### Environment Variables

```bash
# Service configuration
HOST=localhost
PORT=8003

# Remote agent addresses (comma-separated)
REMOTE_AGENTS=http://localhost:8002,http://localhost:8004,http://localhost:8005

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/orchestrator

# Redis for session management
REDIS_URL=redis://localhost:6379

# AI Provider (for summary generation)
GOOGLE_API_KEY=your_api_key_here
```

### Agent Configuration

The orchestrator automatically discovers agents at startup from configured endpoints. Agents must implement the A2A protocol with agent cards at `/a2a/cards`.

## Development and Testing

### Running the Service

```bash
# Install dependencies
cd backend/services/orchestrator
pip install -r requirements.txt

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Testing A2A Endpoints

```bash
# Check orchestrator health
curl http://localhost:8003/health

# Get agent card
curl http://localhost:8003/a2a/cards

# List connected agents
curl http://localhost:8003/a2a/agents

# Test simple orchestration
curl -X POST "http://localhost:8003/a2a/orchestrate" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, can you help me?", "stream": false}'
```

## Security Considerations

Following A2A protocol security recommendations:

### Input Validation
- All agent responses treated as untrusted input
- Sanitization of agent card data before prompt construction
- Validation of message content and structure

### Communication Security
- HTTPS in production environments
- Agent authentication and authorization
- Message integrity verification
- Secure session management

### Error Handling
- Graceful degradation when agents are unavailable
- Timeout management for agent communications
- Circuit breaker patterns for failed agents
- Comprehensive error logging and monitoring

## Monitoring and Observability

### Metrics Tracked
- Agent response times
- Orchestration success rates
- Active session counts
- Agent health status
- Task completion metrics

### Logging
- Structured logging with correlation IDs
- Request/response tracking
- Agent communication logs
- Error and exception tracking

## Future Enhancements

- **Advanced Planning**: AI-powered orchestration planning
- **Agent Marketplace**: Dynamic agent discovery and registration
- **Workflow Templates**: Pre-defined orchestration patterns
- **Multi-tenant Support**: Isolated orchestration for different users
- **Performance Optimization**: Caching and load balancing
- **Security Enhancements**: Advanced authentication and encryption

The LCNC Orchestrator provides a robust foundation for multi-agent coordination while maintaining full compatibility with the A2A protocol standard.
