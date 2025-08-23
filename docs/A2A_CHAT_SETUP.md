# A2A Chat UI Setup Guide

This guide explains how to set up and use the A2A (Agent-to-Agent) chat interface with the LangGraph backend.

## Overview

The A2A chat interface provides:
- Real-time chat with multiple A2A agents
- Agent selection and status monitoring
- Streaming responses from agents
- Fallback to mock service when backend is unavailable
- Session management and conversation history
- File upload and voice recording support

## Configuration

### 1. Environment Variables

Create a `.env.local` file in the frontend directory with the following configuration:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# A2A Configuration
# Set to 'true' to use mock A2A service instead of real backend
NEXT_PUBLIC_USE_MOCK_A2A=false

# Legacy service URLs (optional)
NEXT_PUBLIC_AGENTS_URL=http://localhost:8002
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8003
```

### 2. Backend Setup

Ensure the A2A backend service is running:

1. **Start the Gateway Service**:
   ```bash
   cd backend/services/gateway
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Verify A2A Endpoints**:
   - Health check: `GET http://localhost:8000/api/v1/a2a/health`
   - List agents: `GET http://localhost:8000/api/v1/a2a/agents`
   - Configuration: `GET http://localhost:8000/api/v1/a2a/config`

## Features

### 1. Agent Management

The chat interface automatically:
- Fetches available A2A agents on startup
- Displays agent status (active/inactive)
- Allows selection of specific agents for conversation
- Shows backend connection status

### 2. Chat Functionality

#### Real-time Streaming
- Messages are streamed in real-time from agents
- Shows typing indicators and progress
- Handles connection interruptions gracefully

#### Agent Selection
- Dropdown selector for available agents
- Default agent selection (general_assistant preferred)
- Visual status indicators for agent availability

#### Fallback Mode
- Automatically falls back to mock service if backend unavailable
- Clear indication of mock mode vs. real backend
- Retry button to reconnect to backend

### 3. Advanced Features

#### Session Management
- Multiple conversation sessions
- Session history and restoration
- Context preservation across sessions

#### File Attachments
- Drag-and-drop file upload
- Progress indicators for uploads
- Support for multiple file types

#### Voice Recording
- Voice message recording
- Speech-to-text transcription (when available)
- Audio playback controls

## Usage

### 1. Starting a Chat Session

1. Navigate to `/chat` page
2. Click "New Chat" to start a session
3. Select an agent from the dropdown (if A2A backend is connected)
4. Start typing your message

### 2. Agent Interaction

#### With A2A Backend:
- Select specific agents for specialized tasks
- Real-time streaming responses
- Agent thinking process visibility
- Tool usage tracking

#### Mock Mode:
- Simulated agent responses
- Development and testing purposes
- Same interface functionality

### 3. Backend Status Monitoring

The interface shows:
- **Green "A2A Connected"**: Backend available, real agents active
- **Gray "Mock Mode"**: Using simulated responses
- **Orange retry button**: Appears when backend unavailable

## API Integration

### Frontend Service (`a2aService.ts`)

The frontend service provides:

```typescript
// List available agents
const agents = await a2aService.listAgents();

// Send streaming chat message
for await (const chunk of a2aService.streamChatMessage({
  message: "Hello",
  agent_id: "general_assistant",
  session_id: "session_123"
})) {
  // Handle streaming response
  console.log(chunk);
}

// Check backend availability
const isAvailable = await a2aService.isAvailable();
```

### Backend Endpoints

The chat interface uses these A2A API endpoints:

- `GET /api/v1/a2a/agents` - List agents
- `POST /api/v1/a2a/chat` - Non-streaming chat
- `POST /api/v1/a2a/chat/stream` - Streaming chat
- `GET /api/v1/a2a/health` - Health status
- `GET /api/v1/a2a/config` - System configuration

## Troubleshooting

### Backend Connection Issues

1. **"Mock Mode" badge showing**:
   - Check if backend service is running on port 8000
   - Verify environment variables are correct
   - Use retry button to reconnect

2. **No agents available**:
   - Check backend logs for agent initialization errors
   - Verify LLM models are configured in Tools service
   - Ensure A2A agent service can access model instances

3. **Streaming not working**:
   - Check browser network console for connection errors
   - Verify CORS settings in backend
   - Test with non-streaming endpoint first

### Frontend Issues

1. **Component errors**:
   - Ensure all UI components are installed (`@radix-ui/react-select`)
   - Check console for missing dependencies
   - Verify import paths in components

2. **Hook errors**:
   - Check if `useA2AChat` hook is properly initialized
   - Verify context providers are wrapped around components
   - Monitor state updates in React DevTools

## Development

### Adding New Agents

1. **Backend**: Add agent to `a2a_agent_service.py`
2. **Frontend**: Agents are automatically detected and displayed

### Customizing UI

Key components to modify:
- `A2AChatInterface.tsx` - Main chat interface
- `useA2AChat.ts` - Chat logic and state management
- `a2aService.ts` - API communication

### Testing

```bash
# Start frontend in development mode
npm run dev

# Enable mock mode for testing
NEXT_PUBLIC_USE_MOCK_A2A=true npm run dev
```

## Security Considerations

- Environment variables are client-side visible (NEXT_PUBLIC_ prefix)
- Ensure backend APIs have proper authentication if needed
- File uploads should be validated on backend
- Voice recordings contain sensitive data - handle appropriately

## Performance Notes

- Streaming responses reduce perceived latency
- Agent selection is cached after initial load
- Sessions are stored in browser memory (not persistent)
- Large file uploads may impact performance

---

The A2A chat interface provides a complete solution for interacting with LangGraph-based agents through a modern, responsive web interface with real-time capabilities and robust fallback mechanisms.