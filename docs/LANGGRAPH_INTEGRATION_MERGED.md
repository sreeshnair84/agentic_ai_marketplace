# LangGraph Integration - Merged with Existing Tools

This document describes how the LangGraph framework has been integrated with the existing LLM and embedding model functionality in the Tools service.

## Overview

The enhanced implementation merges:
- **Existing Tools Service**: Current LLM/embedding model management with database tables
- **LangGraph Integration**: Enhanced model capabilities with LangGraph framework support
- **Unified API**: Single set of endpoints that work with both existing and new functionality
- **Backward Compatibility**: Existing models and UI continue to work while gaining new features

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend (UI)     │    │   Tools Service     │    │  Enhanced Services  │
│                     │    │                     │    │                     │
│ - Existing Forms    │◄──►│ - Enhanced API      │◄──►│ - Enhanced Models   │
│ - Model Management  │    │ - Tools Endpoints   │    │ - LangGraph Chat    │
│ - Chat Interface    │    │ - Chat Endpoints    │    │ - Model Instances   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                       │
                                       ▼
                           ┌─────────────────────┐
                           │  Existing Database  │
                           │                     │
                           │ - models(llm, vlm)        │
                           │ - models(embedding)  │
                           │ - tool_templates    │
                           └─────────────────────┘
```

## Enhanced Components

### 1. Enhanced Model Service (`enhanced_model_service.py`)

Extends existing database models with LangGraph capabilities:

```python
from services.enhanced_model_service import get_enhanced_model_service

# Get enhanced service
service = get_enhanced_model_service()

# List models with enhanced filtering
llm_models = await service.list_llm_models(provider="openai", status="active")

# Create model with LangGraph support
model_data = {
    "name": "gpt-4",
    "display_name": "GPT-4",
    "provider": "openai",
    "capabilities": {
        "max_tokens": 8192,
        "supports_streaming": True,
        "supports_function_calling": True
    },
    "model_config": {
        "temperature": 0.7,
        "max_tokens": 4096
    }
}
result = await service.create_llm_model(model_data)
```

### 2. Enhanced Chat Service (`enhanced_chat_service.py`)

Provides chat functionality using the enhanced models:

```python
from services.enhanced_chat_service import get_enhanced_chat_service

chat_service = get_enhanced_chat_service()

# Chat with default model
response = await chat_service.chat(
    message="Hello, how are you?",
    conversation_history=[],
    stream=False
)

# Chat with specific model
response = await chat_service.chat(
    message="Explain quantum computing",
    model_id="specific-model-id",
    stream=True
)
```

## Updated API Endpoints

All endpoints are available under `/api/tools/` and maintain backward compatibility:

### Enhanced LLM Model Management

#### List Models
```http
GET /api/tools/llm-models?provider=openai&status=active&limit=10
```

#### Get Specific Model
```http
GET /api/tools/llm-models/{model_id}
```

#### Create Model
```http
POST /api/tools/create/llm-model
Content-Type: application/json

{
  "name": "gpt-4",
  "display_name": "GPT-4",
  "provider": "openai",
  "api_key": "sk-...",
  "status": "active",
  "capabilities": {
    "max_tokens": 8192,
    "supports_streaming": true,
    "supports_function_calling": true
  },
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "pricing_info": {
    "input_cost_per_token": 0.00003,
    "output_cost_per_token": 0.00006
  }
}
```

#### Update Model
```http
PUT /api/tools/edit/llm-model/{model_id}
```

#### Test Model
```http
POST /api/tools/llm-models/{model_id}/test
```

#### Set Default
```http
POST /api/tools/llm-models/{model_id}/set-default
```

#### Delete Model
```http
DELETE /api/tools/llm-models/{model_id}
```

### Enhanced Embedding Models

Similar endpoints with `/embedding-models` instead of `/llm-models`.

### Enhanced Chat

#### Chat (Non-streaming)
```http
POST /api/tools/chat
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "conversation_history": [],
  "session_id": "chat-123",
  "model_id": "optional-specific-model"
}
```

#### Chat (Streaming)
```http
POST /api/tools/chat/stream
Content-Type: application/json

{
  "message": "Tell me about LangGraph",
  "conversation_history": [],
  "session_id": "chat-123"
}
```

#### Conversation Summary
```http
POST /api/tools/chat/summary
Content-Type: application/json

{
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ],
  "max_length": 200
}
```

### System Information

#### Supported Providers
```http
GET /api/tools/models/providers
```

#### Default Models
```http
GET /api/tools/models/defaults
```

#### Service Health
```http
GET /api/tools/models/health
GET /api/tools/chat/health
```

## Enhanced Features

### 1. Multi-Provider Support

- **OpenAI**: GPT models and embeddings
- **Azure OpenAI**: Enterprise-grade OpenAI models
- **Google Gemini**: Google's latest AI models
- **Ollama**: Local open-source models

### 2. Advanced Configuration

```javascript
// Enhanced model configuration
{
  "capabilities": {
    "max_tokens": 8192,
    "supports_streaming": true,
    "supports_function_calling": true,
    "input_modalities": ["text", "image"],
    "output_modalities": ["text"]
  },
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop_sequences": []
  },
  "pricing_info": {
    "input_cost_per_token": 0.00003,
    "output_cost_per_token": 0.00006,
    "currency": "USD"
  },
  "performance_metrics": {
    "avg_latency": 100.0,
    "availability": 99.9
  }
}
```

### 3. Default Model System

- Set default LLM for chat when no specific agent/workflow is selected
- Set default embedding model for RAG and semantic search
- Automatic fallback to default models

### 4. Model Testing

Built-in connectivity and functionality testing:

```javascript
// Test response for LLM
{
  "success": true,
  "response": "Test successful.",
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}

// Test response for embedding
{
  "success": true,
  "dimensions": 1536,
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Database Integration

The enhanced services work with existing database tables:

### LLM Models Table (`llm_models`)
- Enhanced `model_config` column stores LangGraph-specific settings
- Backward compatible with existing records
- New fields automatically available

### Embedding Models Table (`embedding_models`)
- Similar enhancement pattern
- Maintains existing functionality
- Adds LangGraph capabilities

### Usage Tracking
Existing usage patterns are enhanced with:
- Model instance tracking
- Performance metrics
- Cost monitoring

## Migration Guide

### For Existing Models

1. **No Action Required**: Existing models continue to work
2. **Enhanced Features**: Update models to add new capabilities
3. **Set Defaults**: Configure default models for chat functionality

### For Frontend Integration

1. **Existing Forms**: Continue to work with enhanced backend
2. **New Features**: Access enhanced capabilities through existing endpoints
3. **Chat Integration**: New chat endpoints available immediately

### Configuration Examples

#### Upgrading Existing OpenAI Model
```http
PUT /api/tools/edit/llm-model/{existing-model-id}
Content-Type: application/json

{
  "capabilities": {
    "supports_streaming": true,
    "supports_function_calling": true
  },
  "model_config": {
    "temperature": 0.7,
    "stop_sequences": ["Human:", "AI:"]
  }
}
```

#### Setting Default Models
```bash
# Set default LLM
curl -X POST "/api/tools/llm-models/{model-id}/set-default"

# Set default embedding
curl -X POST "/api/tools/embedding-models/{model-id}/set-default"
```

## Environment Variables

Add these to your `.env` file for enhanced functionality:

```bash
# AI Provider API Keys
OPENAI_API_KEY=sk-your-openai-key
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
GOOGLE_API_KEY=your-google-api-key

# Ollama (if using)
OLLAMA_API_BASE=http://localhost:11434
```

## Chat Integration

### When Default Model is Available

The chat automatically uses the configured default LLM:

```javascript
// User sends message without specific agent/workflow
const response = await fetch('/api/tools/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "How can AI help my business?",
    session_id: "user-session-123"
  })
});
```

### When No Default Model

The system provides helpful guidance:

```javascript
{
  "success": false,
  "error": "No default model configured",
  "message": "Please configure a default LLM model in the Tools section...",
  "action_required": "configure_default_model"
}
```

## Benefits of Merged Approach

1. **Seamless Upgrade**: Existing functionality enhanced without breaking changes
2. **Unified Management**: Single interface for all model types and providers
3. **Backward Compatibility**: Existing models and configurations preserved
4. **Enhanced Capabilities**: LangGraph features available immediately
5. **Consistent API**: Same endpoints for both old and new features

## Next Steps

1. **Update Models**: Enhance existing models with new capabilities
2. **Set Defaults**: Configure default LLM and embedding models
3. **Test Integration**: Use the test endpoints to verify connectivity
4. **Enable Chat**: Start using the enhanced chat functionality
5. **Monitor Usage**: Track model performance and costs

## Support

The enhanced system maintains full compatibility with existing tools while adding powerful new capabilities. All existing workflows continue to function while new LangGraph features become available through the same familiar interface.