# A2A Protocol Implementation for Agentic AI Acceleration

This implementation follows the A2A (Agent-to-Agent) protocol standard based on the samples from https://github.com/a2aproject/a2a-samples, specifically the `a2a_mcp` implementation.

## Overview

Our AgenticAI platform now supports the A2A protocol, enabling standardized communication between agents across different frameworks and systems. This implementation includes:

- **A2A Agent Cards**: Standardized agent descriptions following the A2A protocol
- **JSON-RPC Communication**: Standard A2A message format with streaming support
- **MCP Integration**: Model Context Protocol for agent discovery and tool access
- **Gemini AI Integration**: All agents powered by Google Gemini as the default AI provider

## Architecture

### Agent Cards Structure

Agent cards follow the A2A protocol specification and include:

```json
{
  "name": "AgentName",
  "description": "Agent description and purpose",
  "version": "1.0.0",
  "url": "http://localhost:8002/a2a/agents/type",
  "default_input_modes": ["text"],
  "default_output_modes": ["text"],
  "capabilities": {
    "streaming": true,
    "batch_processing": true,
    "multi_modal": true
  },
  "skills": [
    {
      "id": "skill_id",
      "name": "Skill Name", 
      "description": "Skill description",
      "tags": ["tag1", "tag2"],
      "examples": ["Example usage"]
    }
  ],
  "tags": ["ai", "gemini", "category"],
  "ai_provider": "gemini",
  "model_name": "gemini-1.5-pro"
}
```

### Available Agents

1. **GeneralAIAgent** - General purpose AI assistant
   - Endpoint: `/a2a/agents/general`
   - Capabilities: General assistance, analysis, reasoning

2. **TaskExecutorAgent** - Specialized task execution
   - Endpoint: `/a2a/agents/task`
   - Capabilities: Structured tasks, data processing, workflows

3. **ConversationAgent** - Context-aware conversations
   - Endpoint: `/a2a/agents/conversation`
   - Capabilities: Dialogue management, context awareness

4. **ToolsAgent** - Tool execution and MCP integration
   - Endpoint: `/tools` (Tools service)
   - Capabilities: Tool execution, MCP protocol, file operations

5. **RAGAgent** - Retrieval Augmented Generation
   - Endpoint: Port 8004 (RAG service)
   - Capabilities: Document retrieval, knowledge search, augmented generation

## A2A Protocol Endpoints

### Agent Discovery

- `GET /a2a/cards` - List all available agent cards
- `GET /a2a/cards/{agent_name}` - Get specific agent card
- `POST /a2a/discover` - Discover agents by query and tags

### Message Communication

- `POST /a2a/message/send` - Synchronous message handling (JSON-RPC)
- `POST /a2a/message/stream` - Streaming message handling (JSON-RPC)
- `POST /a2a/agents/{agent_type}` - Agent-specific endpoints

### JSON-RPC Message Format

```json
{
  "jsonrpc": "2.0",
  "id": "unique-id",
  "method": "message/stream",
  "params": {
    "id": "task-id",
    "sessionId": "session-id",
    "acceptedOutputModes": ["text"],
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text", 
          "text": "Your message here"
        }
      ]
    }
  }
}
```

## MCP Server Integration

The MCP server provides agent discovery and tool access:

- **Agent Registry**: Serves agent cards as MCP resources
- **Tool Discovery**: `find_agent` tool for semantic agent matching
- **Tool Execution**: Various tools like flight search, hotel search, etc.

### MCP Resources

- `resource://agent_cards/list` - List of all agent card URIs
- `resource://agent_cards/{card_name}` - Specific agent card data

### MCP Tools

- `find_agent(query)` - Find best matching agent for a query
- `search_flights(origin, destination, date)` - Flight search tool
- `search_hotels(location, checkin, checkout)` - Hotel search tool
- `query_db(query)` - Database query tool

## Usage Examples

### Direct A2A Communication

```bash
curl -X POST http://localhost:8002/a2a/message/stream \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1", 
    "method": "message/stream",
    "params": {
      "id": "task-1",
      "sessionId": "session-123",
      "acceptedOutputModes": ["text"],
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Hello, I need help with analysis"}]
      }
    }
  }'
```

### Agent Discovery

```bash
curl "http://localhost:8002/a2a/discover?query=data%20analysis&max_results=3"
```

### List Agent Cards

```bash
curl "http://localhost:8002/a2a/cards"
```

## Integration with Other Services

### Orchestrator Service

The orchestrator service can discover and communicate with agents using A2A:

```python
from services.a2a_handler import A2AProtocolHandler

handler = A2AProtocolHandler()
cards = await handler.list_agent_cards(tags=["analysis"])
message = create_a2a_message("Analyze this data", "session-123")

async for response in handler.send_a2a_message(
    target_agent_url="http://localhost:8002/a2a/agents/task",
    message=message,
    stream=True
):
    print(response)
```

### Tools Service Integration

The tools service provides MCP-compatible tools that can be discovered and executed by agents.

## Key Features

1. **Standardized Communication**: All agents follow A2A protocol standards
2. **Gemini AI Integration**: Default AI provider with streaming support
3. **Semantic Discovery**: Find agents based on natural language queries
4. **Multi-modal Support**: Text, data, and file handling capabilities
5. **Streaming Responses**: Real-time response streaming for better UX
6. **Error Handling**: Robust error handling and timeout management
7. **Context Awareness**: Session and conversation context management

## Development Notes

- All agents are Gemini-powered by default (configurable)
- Agent cards are stored in JSON format for easy modification
- MCP server provides embeddings-based semantic search
- Streaming responses use Server-Sent Events format
- Full JSON-RPC 2.0 compliance for message handling

## Security Considerations

Following A2A protocol recommendations:
- Validate all incoming agent data as untrusted input
- Sanitize agent card fields before using in prompts
- Implement proper authentication and authorization
- Use secure communication channels in production
- Validate message signatures and integrity

## Future Enhancements

- Vector database integration for better semantic search
- Authentication and authorization for agent access
- Agent capability negotiation
- Multi-language support
- Enhanced monitoring and observability
- Agent marketplace integration
