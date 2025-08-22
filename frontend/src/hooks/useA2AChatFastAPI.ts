import { useState, useEffect, useRef, useCallback } from 'react';

// AsyncGenerator type for streaming responses
type AsyncGenerator<T = unknown, TReturn = any, TNext = unknown> = {
  next(...args: [] | [TNext]): Promise<IteratorResult<T, TReturn>>;
  return(value: TReturn | PromiseLike<TReturn>): Promise<IteratorResult<T, TReturn>>;
  throw(e: any): Promise<IteratorResult<T, TReturn>>;
  [Symbol.asyncIterator](): AsyncGenerator<T, TReturn, TNext>;
};

// Types for A2A chat functionality
export interface ChatMessage {
  id: string;
  type: 'user' | 'agent' | 'system' | 'inter_agent';
  content: string;
  agentName?: string;
  timestamp: Date;
  isStreaming?: boolean;
  isComplete?: boolean;
  citations?: Citation[];
  toolCalls?: ToolCall[];
  scratchpad?: string;
  attachments?: FileAttachment[];
  a2aTrace?: AgentCommunication[];
  metadata?: Record<string, any>;
}

export interface Citation {
  id: string;
  source: string;
  title: string;
  url?: string;
  excerpt: string;
  relevanceScore?: number;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, any>;
  result?: any;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  error?: string;
}

export interface AgentCommunication {
  id: string;
  sourceAgent: string;
  targetAgent: string;
  message: string;
  timestamp: Date;
  status: 'sent' | 'received' | 'processed' | 'failed';
  latency_ms?: number;
  message_type: string;
  correlation_id?: string;
}

export interface FileAttachment {
  id: string;
  filename: string;
  originalFilename: string;
  mimeType: string;
  fileSize: number;
  uploadStatus: 'uploading' | 'completed' | 'failed';
  url?: string;
}

export interface ChatSession {
  id: string;
  workflowId: string;
  userId?: string;
  title?: string;
  status: 'active' | 'paused' | 'completed' | 'error';
  agents: Agent[];
  capabilities: {
    streaming: boolean;
    fileUpload: boolean;
    voiceInput: boolean;
    a2aCommunication: boolean;
    pushNotifications: boolean;
  };
  createdAt: Date;
  lastActivityAt: Date;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  provider: string;
  model: string;
  status?: 'online' | 'offline' | 'busy';
}

export interface StreamingState {
  isStreaming: boolean;
  currentMessage: string;
  chunks: string[];
  currentAgent?: string;
  streamId?: string;
}

export interface VoiceRecording {
  isRecording: boolean;
  audioBlob?: Blob;
  duration: number;
  transcription?: string;
  status: 'idle' | 'recording' | 'processing' | 'completed' | 'error';
}

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export function useA2AChatFastAPI() {
  // Core state
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    currentMessage: '',
    chunks: []
  });
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  
  // WebSocket and real-time
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  
  // Voice recording
  const [voiceRecording, setVoiceRecording] = useState<VoiceRecording>({
    isRecording: false,
    duration: 0,
    status: 'idle'
  });
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  
  // File upload
  const [uploadingFiles, setUploadingFiles] = useState<FileAttachment[]>([]);
  
  // A2A Communications
  const [agentCommunications, setAgentCommunications] = useState<AgentCommunication[]>([]);
  
  // Agent status tracking
  const [connectedAgents, setConnectedAgents] = useState<Agent[]>([]);
  
  // Create a new chat session with FastAPI backend
  const createSession = useCallback(async (workflowId: string, userId?: string): Promise<ChatSession> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/a2a/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          user_id: userId
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }
      
      const sessionData = await response.json();
      
      const session: ChatSession = {
        id: sessionData.session_id,
        workflowId: sessionData.workflow_id,
        userId: userId,
        status: 'active',
        agents: sessionData.agents || [],
        capabilities: sessionData.capabilities || {
          streaming: true,
          fileUpload: true,
          voiceInput: true,
          a2aCommunication: true,
          pushNotifications: true
        },
        createdAt: new Date(),
        lastActivityAt: new Date()
      };
      
      setCurrentSession(session);
      setConnectedAgents(session.agents);
      
      // Initialize WebSocket connection for real-time updates
      await initializeWebSocket(session.id);
      
      return session;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create session';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  // Initialize WebSocket connection
  const initializeWebSocket = useCallback(async (sessionId: string) => {
    try {
      setConnectionStatus('connecting');
      
      const wsUrl = `${WS_BASE_URL}/api/chat/a2a/sessions/${sessionId}/ws`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        console.log('WebSocket connected for session:', sessionId);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
      
      ws.onclose = () => {
        setConnectionStatus('disconnected');
        console.log('WebSocket disconnected');
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (currentSession) {
            initializeWebSocket(currentSession.id);
          }
        }, 3000);
      };
      
      ws.onerror = (error) => {
        setConnectionStatus('error');
        console.error('WebSocket error:', error);
      };
      
      wsRef.current = ws;
      
    } catch (err) {
      setConnectionStatus('error');
      console.error('Failed to initialize WebSocket:', err);
    }
  }, [currentSession]);
  
  // Handle WebSocket messages for real-time updates
  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'connection_established':
        console.log('WebSocket connection established:', data.connection_id);
        break;
        
      case 'stream_chunk':
        handleStreamChunk(data);
        break;
        
      case 'message_complete':
        handleMessageComplete(data);
        break;
        
      case 'a2a_communication':
        handleA2ACommunication(data);
        break;
        
      case 'stream_complete':
        handleStreamComplete(data);
        break;
        
      case 'error':
        setError(data.error);
        break;
        
      case 'pong':
        // Handle ping/pong for connection health
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }, []);
  
  // Handle streaming message chunks
  const handleStreamChunk = useCallback((data: any) => {
    const chunkContent = data.content || '';
    
    setStreamingState(prev => ({
      ...prev,
      isStreaming: true,
      currentMessage: prev.currentMessage + chunkContent,
      chunks: [...prev.chunks, chunkContent],
      currentAgent: data.agent_name,
      streamId: data.chunk_id
    }));
    
    // Update or create the streaming message
    setMessages(prev => {
      const lastMessage = prev[prev.length - 1];
      
      if (lastMessage && lastMessage.isStreaming && lastMessage.agentName === data.agent_name) {
        // Update existing streaming message
        return prev.map((msg, index) => 
          index === prev.length - 1 
            ? {
                ...msg,
                content: data.session_content || (msg.content + chunkContent),
                timestamp: new Date(data.timestamp)
              }
            : msg
        );
      } else {
        // Create new streaming message
        const newMessage: ChatMessage = {
          id: data.chunk_id || `stream_${Date.now()}`,
          type: 'agent',
          content: chunkContent,
          agentName: data.agent_name,
          timestamp: new Date(data.timestamp),
          isStreaming: true,
          isComplete: false
        };
        
        return [...prev, newMessage];
      }
    });
  }, []);
  
  // Handle completed messages
  const handleMessageComplete = useCallback((data: any) => {
    const completedMessage: ChatMessage = {
      id: data.message_id || `msg_${Date.now()}`,
      type: 'agent',
      content: data.content,
      agentName: data.agent_name,
      timestamp: new Date(data.timestamp),
      isStreaming: false,
      isComplete: true,
      citations: data.citations || [],
      toolCalls: data.tool_calls || [],
      scratchpad: data.scratchpad,
      metadata: data.metadata
    };
    
    setMessages(prev => {
      // Replace streaming message or add new complete message
      const lastMessage = prev[prev.length - 1];
      
      if (lastMessage && lastMessage.isStreaming && lastMessage.agentName === data.agent_name) {
        return prev.map((msg, index) => 
          index === prev.length - 1 ? completedMessage : msg
        );
      } else {
        return [...prev, completedMessage];
      }
    });
    
    // Clear streaming state
    setStreamingState({
      isStreaming: false,
      currentMessage: '',
      chunks: []
    });
  }, []);
  
  // Handle A2A communications
  const handleA2ACommunication = useCallback((data: any) => {
    const communication: AgentCommunication = {
      id: data.communication_id || `comm_${Date.now()}`,
      sourceAgent: data.source_agent,
      targetAgent: data.target_agent,
      message: data.message,
      timestamp: new Date(data.timestamp),
      status: data.status || 'received',
      latency_ms: data.latency_ms,
      message_type: data.communication_type || 'internal',
      correlation_id: data.correlation_id
    };
    
    setAgentCommunications(prev => [...prev, communication]);
    
    // Optionally add to chat messages for visibility
    const interAgentMessage: ChatMessage = {
      id: `inter_${communication.id}`,
      type: 'inter_agent',
      content: `${communication.sourceAgent} → ${communication.targetAgent}: ${communication.message}`,
      timestamp: communication.timestamp,
      a2aTrace: [communication],
      isComplete: true
    };
    
    setMessages(prev => [...prev, interAgentMessage]);
  }, []);
  
  // Handle stream completion
  const handleStreamComplete = useCallback((data: any) => {
    setStreamingState({
      isStreaming: false,
      currentMessage: '',
      chunks: []
    });
  }, []);
  
  // Send message through A2A FastAPI backend
  const sendMessage = useCallback(async (
    message: string,
    options: {
      messageType?: string;
      agentTarget?: string;
      includeContext?: boolean;
      stream?: boolean;
    } = {}
  ) => {
    if (!currentSession) {
      throw new Error('No active session');
    }
    
    if (!message.trim()) {
      throw new Error('Message cannot be empty');
    }
    
    const {
      messageType = 'user',
      agentTarget,
      includeContext = true,
      stream = true
    } = options;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        type: 'user',
        content: message,
        timestamp: new Date(),
        isComplete: true
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Prepare request
      const endpoint = stream 
        ? `${API_BASE_URL}/api/chat/a2a/sessions/${currentSession.id}/message/stream`
        : `${API_BASE_URL}/api/chat/a2a/sessions/${currentSession.id}/message`;
      
      const requestBody = {
        message: message,
        type: messageType,
        agent_target: agentTarget,
        include_context: includeContext
      };
      
      if (stream) {
        // Handle streaming response
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
          throw new Error(`Request failed: ${response.statusText}`);
        }
        
        // Note: Streaming response is handled via WebSocket
        // The SSE stream provides backup/fallback handling
        
      } else {
        // Handle non-streaming response
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
          throw new Error(`Request failed: ${response.statusText}`);
        }
        
        const responseData = await response.json();
        
        // Process responses
        responseData.responses?.forEach((response: any) => {
          if (response.type === 'message_complete') {
            handleMessageComplete(response);
          } else if (response.type === 'a2a_communication') {
            handleA2ACommunication(response);
          }
        });
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      // Add error message to chat
      const errorChatMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'system',
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
        isComplete: true
      };
      
      setMessages(prev => [...prev, errorChatMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [currentSession, handleMessageComplete, handleA2ACommunication]);
  
  // File upload functionality
  const uploadFiles = useCallback(async (files: FileList) => {
    if (!currentSession) {
      throw new Error('No active session');
    }
    
    const uploadPromises = Array.from(files).map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', currentSession.id);
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat/upload`, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        return await response.json();
      } catch (err) {
        console.error('File upload failed:', err);
        throw err;
      }
    });
    
    try {
      const uploadResults = await Promise.all(uploadPromises);
      return uploadResults;
    } catch (err) {
      setError('File upload failed');
      throw err;
    }
  }, [currentSession]);
  
  // Voice recording functionality
  const startVoiceRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setVoiceRecording(prev => ({
          ...prev,
          audioBlob,
          isRecording: false,
          status: 'completed'
        }));
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      
      setVoiceRecording(prev => ({
        ...prev,
        isRecording: true,
        status: 'recording'
      }));
      
    } catch (err) {
      setError('Failed to start voice recording');
      setVoiceRecording(prev => ({
        ...prev,
        status: 'error'
      }));
    }
  }, []);
  
  const stopVoiceRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }, []);
  
  // Send voice message
  const sendVoiceMessage = useCallback(async () => {
    if (!voiceRecording.audioBlob || !currentSession) {
      return;
    }
    
    try {
      setVoiceRecording(prev => ({ ...prev, status: 'processing' }));
      
      const formData = new FormData();
      formData.append('audio', voiceRecording.audioBlob);
      formData.append('session_id', currentSession.id);
      
      const response = await fetch(`${API_BASE_URL}/api/chat/voice`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Voice message failed');
      }
      
      const result = await response.json();
      
      // Send transcribed text as regular message
      if (result.transcription) {
        await sendMessage(result.transcription);
      }
      
      setVoiceRecording({
        isRecording: false,
        duration: 0,
        status: 'idle'
      });
      
    } catch (err) {
      setError('Failed to send voice message');
      setVoiceRecording(prev => ({ ...prev, status: 'error' }));
    }
  }, [voiceRecording.audioBlob, currentSession, sendMessage]);
  
  // Get session status
  const getSessionStatus = useCallback(async () => {
    if (!currentSession) return null;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/a2a/sessions/${currentSession.id}/status`);
      if (response.ok) {
        return await response.json();
      }
    } catch (err) {
      console.error('Failed to get session status:', err);
    }
    
    return null;
  }, [currentSession]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);
  
  // Keep WebSocket alive with ping/pong
  useEffect(() => {
    if (connectionStatus === 'connected' && wsRef.current) {
      const pingInterval = setInterval(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000); // Ping every 30 seconds
      
      return () => clearInterval(pingInterval);
    }
  }, [connectionStatus]);
  
  return {
    // Core state
    currentSession,
    messages,
    streamingState,
    
    // UI state
    isLoading,
    error,
    connectionStatus,
    
    // Voice recording
    voiceRecording,
    
    // A2A communications
    agentCommunications,
    connectedAgents,
    
    // Actions
    createSession,
    sendMessage,
    uploadFiles,
    startVoiceRecording,
    stopVoiceRecording,
    sendVoiceMessage,
    getSessionStatus,
    
    // Utilities
    clearError: () => setError(null),
    clearMessages: () => setMessages([]),
    clearCommunications: () => setAgentCommunications([])
  };
}
