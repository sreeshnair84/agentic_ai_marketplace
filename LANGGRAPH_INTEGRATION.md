# LangGraph Integration for GenAI Functionalities

This document describes the LangGraph-based framework implementation for managing LLM and embedding models in the Enterprise AI Acceleration platform.

## Overview

The platform now includes comprehensive LangGraph integration that provides:
- **Unified Model Management**: Support for Google Gemini, Azure OpenAI, OpenAI, and Ollama
- **Default Model Selection**: Configurable default LLM for chat when no agents/workflows are selected
- **Dynamic Configuration**: Runtime model configuration and testing
- **Template-Based Setup**: Pre-configured templates for different providers
- **Usage Analytics**: Model usage tracking and performance metrics

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    Frontend UI      │    │   Gateway API       │    │  Model Service      │
│                     │    │                     │    │                     │
│ - Model Forms       │◄──►│ - LLM Models API    │◄──►│ - LangGraph Models  │
│ - Configuration     │    │ - Embedding API     │    │ - Provider Factory  │
│ - Testing UI        │    │ - Default Chat API  │    │ - Instance Manager  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                       │
                                       ▼
                           ┌─────────────────────┐
                           │     Database        │
                           │                     │
                           │ - models            │
                           │ - model_usage_logs  │
                           │ - config_history    │
                           └─────────────────────┘
```

## Components

### Backend Services

#### 1. LangGraph Model Service (`langgraph_model_service.py`)
Core service for managing model configurations and instances:

```python
from services.langgraph_model_service import LangGraphModelService

# Initialize service
service = LangGraphModelService(db_session)

# Create LLM model
model_data = {
    "name": "gpt-4",
    "display_name": "GPT-4",
    "provider": "openai",
    "api_key": "your-api-key"
}
result = await service.create_llm_model(model_data)

# Set default model
await service.set_default_llm(model_id)

# Get model instance for use
llm_instance = await service.get_model_instance(model_id)
```

#### 2. Default Chat Service (`default_chat_service.py`)
Handles chat when no specific agents/workflows are selected:

```python
from services.default_chat_service import DefaultChatService

chat_service = DefaultChatService(model_service)

# Send chat message
response = await chat_service.chat(
    message="Hello, how are you?",
    conversation_history=[],
    stream=False
)
```

### API Endpoints

#### LLM Models API (`/api/v1/llm-models/`)
- `GET /` - List LLM models
- `POST /` - Create LLM model
- `GET /{id}` - Get specific model
- `PUT /{id}` - Update model
- `DELETE /{id}` - Delete model
- `POST /{id}/test` - Test model connectivity
- `POST /{id}/set-default` - Set as default LLM
- `GET /providers/supported` - List supported providers
- `GET /templates/configuration` - Get configuration templates

#### Embedding Models API (`/api/v1/embedding-models/`)
- Similar endpoints for embedding models
- Additional endpoints for embedding-specific functionality

#### Default Chat API (`/api/v1/default-chat/`)
- `POST /chat` - Send chat message
- `POST /chat/stream` - Stream chat response
- `GET /health` - Chat service health
- `POST /conversation/summary` - Generate conversation summary
- `GET /models/default` - Get default model info
- `POST /test` - Test default chat

### Frontend Components

#### 1. LangGraph Model Form
Enhanced form component supporting all model types and providers:

```tsx
import LangGraphModelForm from '@/components/models/LangGraphModelForm';

<LangGraphModelForm
  modelType="llm"
  onSave={handleSave}
  onCancel={handleCancel}
  onTest={handleTest}
  onSetDefault={handleSetDefault}
/>
```

## Supported Providers

### 1. OpenAI
```json
{
  "provider": "openai",
  "api_key": "sk-...",
  "models": {
    "llm": ["gpt-4", "gpt-3.5-turbo"],
    "embedding": ["text-embedding-ada-002"]
  }
}
```

### 2. Azure OpenAI
```json
{
  "provider": "azure_openai",
  "api_endpoint": "https://your-resource.openai.azure.com/",
  "api_key": "your-api-key",
  "api_version": "2024-02-01"
}
```

### 3. Google Gemini
```json
{
  "provider": "google_gemini",
  "api_key": "your-google-api-key",
  "models": {
    "llm": ["gemini-pro"],
    "embedding": ["models/embedding-001"]
  }
}
```

### 4. Ollama
```json
{
  "provider": "ollama",
  "api_endpoint": "http://localhost:11434",
  "models": {
    "llm": ["llama2", "codellama"],
    "embedding": ["nomic-embed-text"]
  }
}
```

## Database Schema

### Models Table
```sql
CREATE TABLE models (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_type VARCHAR(20) NOT NULL,
    api_endpoint TEXT,
    api_key_encrypted TEXT,
    status VARCHAR(20) DEFAULT 'inactive',
    capabilities JSONB DEFAULT '{}',
    pricing_info JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    model_config JSONB DEFAULT '{}',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Usage Tracking
```sql
CREATE TABLE model_usage_logs (
    id UUID PRIMARY KEY,
    model_id UUID REFERENCES models(id),
    user_id UUID REFERENCES users(id),
    usage_type VARCHAR(50),
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd DECIMAL(10, 6),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Configuration Examples

### Creating an OpenAI GPT-4 Model
```bash
curl -X POST "http://localhost:8000/api/v1/llm-models/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "gpt-4",
    "display_name": "GPT-4",
    "provider": "openai",
    "api_key": "sk-your-api-key",
    "status": "active",
    "capabilities": {
      "max_tokens": 8192,
      "supports_streaming": true,
      "supports_function_calling": true
    },
    "model_config": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }'
```

### Setting Default Model
```bash
curl -X POST "http://localhost:8000/api/v1/llm-models/{model_id}/set-default"
```

### Testing Model
```bash
curl -X POST "http://localhost:8000/api/v1/llm-models/{model_id}/test"
```

## Usage in Chat

When no specific agent or workflow is selected, the chat system automatically uses the configured default LLM model:

```bash
curl -X POST "http://localhost:8000/api/v1/default-chat/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how can you help me?",
    "session_id": "chat-session-123"
  }'
```

For streaming responses:
```bash
curl -X POST "http://localhost:8000/api/v1/default-chat/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about LangGraph",
    "stream": true
  }'
```

## Environment Variables

Add these to your `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# Ollama (if using custom endpoint)
OLLAMA_API_BASE=http://localhost:11434
```

## Setup Instructions

### 1. Backend Setup
```bash
# Install dependencies
cd backend/services/gateway
pip install -r requirements.txt

# Run database migration
psql -d your_database -f infra/migrations/0008_langgraph_models.sql

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
The existing UI components have been enhanced to support the new model management features. The forms will automatically appear in the Models section.

### 3. Configuration
1. Navigate to `/models/llm-models` in the UI
2. Click "Add Model" to create a new model configuration
3. Fill in the provider details and API keys
4. Test the model connectivity
5. Set as default if desired

## Troubleshooting

### Common Issues

1. **Model not responding**
   - Check API key validity
   - Verify endpoint URL
   - Test model connectivity

2. **Default chat not working**
   - Ensure a default LLM model is configured
   - Check model status is 'active'
   - Verify model instance initialization

3. **Provider-specific issues**
   - OpenAI: Check API key format and quotas
   - Azure: Verify endpoint and deployment name
   - Gemini: Confirm API key and model availability
   - Ollama: Ensure service is running locally

### Debugging
Enable debug logging:
```python
import logging
logging.getLogger('services.langgraph_model_service').setLevel(logging.DEBUG)
logging.getLogger('services.default_chat_service').setLevel(logging.DEBUG)
```

## Future Enhancements

- [ ] Model performance monitoring dashboard
- [ ] Automatic model selection based on query type
- [ ] Multi-model ensemble support
- [ ] Cost optimization recommendations
- [ ] Advanced caching strategies
- [ ] Model A/B testing framework

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review server logs for error details
3. Test individual components using the provided endpoints
4. Consult the troubleshooting section above