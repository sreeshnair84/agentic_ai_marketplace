import { useState, useCallback, useRef, useEffect } from 'react';
import { mockA2AService } from '@/services/mockA2AService';

// A2A Message Types
export interface A2AMessage {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant' | 'system';
  parts: A2AMessagePart[];
  timestamp: Date;
  accepted_output_modes: string[];
  metadata?: Record<string, any>;
}

export interface A2AMessagePart {
  type: 'text' | 'file' | 'audio' | 'image';
  text?: string;
  file_url?: string;
  file_name?: string;
  file_type?: string;
  data?: string; // base64 encoded data
}

// Agent Communication Types
export interface AgentCommunication {
  id: string;
  sourceAgent: string;
  targetAgent: string;
  message: string;
  timestamp: Date;
  status: 'sent' | 'received' | 'processed' | 'error';
  latency_ms?: number;
  message_type: 'request' | 'response' | 'broadcast' | 'error';
}

// Chat Message with Agent Context
export interface ChatMessage {
  id: string;
  type: 'user' | 'agent' | 'system' | 'inter_agent';
  content: string;
  agentName?: string;
  agentId?: string;
  timestamp: Date;
  attachments?: FileAttachment[];
  a2aTrace?: AgentCommunication[];
  scratchpad?: AgentScratchpad;
  citations?: Citation[];
  toolCalls?: ToolCall[];
  streaming?: boolean;
  isComplete?: boolean;
}

// Agent Scratchpad for showing thinking process
export interface AgentScratchpad {
  id: string;
  agentId: string;
  thinking: string[];
  reasoning: string;
  confidence_score: number;
  alternative_approaches?: string[];
  decision_factors?: string[];
}

// Citations for AI responses
export interface Citation {
  id: string;
  source: string;
  title: string;
  url?: string;
  excerpt: string;
  confidence: number;
  relevance_score: number;
}

// Tool Usage Information
export interface ToolCall {
  id: string;
  toolName: string;
  toolType: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  status: 'pending' | 'completed' | 'error';
  timestamp: Date;
  duration_ms?: number;
  error_message?: string;
}

// File Upload
export interface FileAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  uploadProgress?: number;
  processingStatus?: 'pending' | 'processing' | 'completed' | 'error';
}

// Voice Recording
export interface VoiceRecording {
  id: string;
  audioBlob: Blob;
  duration: number;
  transcript?: string;
  isTranscribing?: boolean;
}

// Streaming State
export interface StreamingState {
  isStreaming: boolean;
  currentMessage: string;
  agentName?: string;
  chunks: string[];
}

// Chat Session
export interface ChatSession {
  id: string;
  name: string;
  workflowId?: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, any>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AGENTS_BASE = process.env.NEXT_PUBLIC_AGENTS_URL || 'http://localhost:8002';
const ORCHESTRATOR_BASE = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8003';
const USE_MOCK_SERVICE = process.env.NODE_ENV === 'development' || true; // Enable mock service for now

export function useA2AChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    currentMessage: '',
    chunks: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentCommunications, setAgentCommunications] = useState<AgentCommunication[]>([]);
  
  // WebSocket connection for real-time updates
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Create new chat session
  const createSession = useCallback(async (name: string, workflowId?: string): Promise<ChatSession> => {
    const newSession: ChatSession = {
      id: `session_${Date.now()}`,
      name,
      workflowId,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      metadata: { workflowId }
    };
    
    setSessions(prev => [...prev, newSession]);
    setCurrentSession(newSession);
    return newSession;
  }, []);

  // Send A2A message using the JSON-RPC protocol
  const sendA2AMessage = useCallback(async (
    message: string,
    attachments: FileAttachment[] = [],
    voiceRecording?: VoiceRecording
  ): Promise<void> => {
    if (!currentSession) return;
    
    setError(null);
    setLoading(true);

    try {
      // Create user message
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        type: 'user',
        content: message,
        timestamp: new Date(),
        attachments,
        isComplete: true
      };

      // Add to current session
      const updatedSession = {
        ...currentSession,
        messages: [...currentSession.messages, userMessage],
        updatedAt: new Date()
      };
      setCurrentSession(updatedSession);
      setSessions(prev => prev.map(s => s.id === currentSession.id ? updatedSession : s));

      // Prepare A2A message parts
      const parts: A2AMessagePart[] = [
        { type: 'text', text: message }
      ];

      // Add file attachments
      attachments.forEach(attachment => {
        parts.push({
          type: 'file',
          file_url: attachment.url,
          file_name: attachment.name,
          file_type: attachment.type
        });
      });

      // Add voice recording
      if (voiceRecording) {
        parts.push({
          type: 'audio',
          data: await blobToBase64(voiceRecording.audioBlob),
          text: voiceRecording.transcript
        });
      }

      // Prepare JSON-RPC request
      const rpcRequest = {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        method: 'message/stream',
        params: {
          id: `task_${Date.now()}`,
          sessionId: currentSession.id,
          acceptedOutputModes: ['text', 'json'],
          message: {
            role: 'user',
            parts
          }
        }
      };

      // Send streaming request to orchestrator
      await handleStreamingResponse(rpcRequest);

    } catch (error) {
      console.error('Error sending A2A message:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }, [currentSession]);

  // Handle streaming response from A2A endpoint
  const handleStreamingResponse = useCallback(async (rpcRequest: any) => {
    if (!currentSession) return;

    try {
      setStreamingState({
        isStreaming: true,
        currentMessage: '',
        chunks: []
      });

      if (USE_MOCK_SERVICE) {
        // Use mock service for development
        const messageText = rpcRequest.params.message.parts[0]?.text || '';
        
        for await (const chunk of mockA2AService.generateMockA2AResponse(messageText, currentSession.id)) {
          await processStreamChunk(chunk, null, '');
        }
      } else {
        // Use real A2A service
        const url = `${ORCHESTRATOR_BASE}/a2a/message/stream`;
        
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(rpcRequest)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let currentAgentMessage: ChatMessage | null = null;
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                // Mark message as complete
                if (currentAgentMessage) {
                  const completedMessage: ChatMessage = {
                    ...(currentAgentMessage as ChatMessage),
                    isComplete: true
                  };
                  updateCurrentMessage(completedMessage);
                }
                setStreamingState({
                  isStreaming: false,
                  currentMessage: '',
                  chunks: []
                });
                return;
              }

              try {
                const chunk = JSON.parse(data);
                await processStreamChunk(chunk, currentAgentMessage, fullContent);
              } catch (parseError) {
                console.warn('Failed to parse chunk:', data, parseError);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setError(error instanceof Error ? error.message : 'Streaming failed');
      setStreamingState({
        isStreaming: false,
        currentMessage: '',
        chunks: []
      });
    }
  }, [currentSession]);

  // Process individual stream chunks
  const processStreamChunk = useCallback(async (
    chunk: any,
    currentAgentMessage: ChatMessage | null,
    fullContent: string
  ) => {
    if (!currentSession) return;

    if (chunk.result?.type === 'task_status_update') {
      const status = chunk.result.status;
      
      if (status.type === 'in_progress') {
        const messageText = status.message?.parts?.[0]?.text || '';
        const newFullContent = fullContent + messageText;
        
        setStreamingState(prev => ({
          ...prev,
          currentMessage: newFullContent,
          chunks: [...prev.chunks, messageText]
        }));

        // Create or update agent message
        if (!currentAgentMessage) {
          const newAgentMessage: ChatMessage = {
            id: `msg_${Date.now()}`,
            type: 'agent',
            content: newFullContent,
            agentName: status.result?.agent_name || 'AI Assistant',
            timestamp: new Date(),
            streaming: true,
            isComplete: false
          };
          addMessageToSession(newAgentMessage);
        } else {
          const updatedMessage: ChatMessage = {
            ...(currentAgentMessage as ChatMessage),
            content: newFullContent
          };
          updateCurrentMessage(updatedMessage);
        }
      } else if (status.type === 'completed' && status.result) {
        // Handle completion with citations, tool calls, etc.
        if (currentAgentMessage) {
          const completedMessage: ChatMessage = {
            ...(currentAgentMessage as ChatMessage),
            content: status.result.content || fullContent,
            citations: status.result.citations || [],
            toolCalls: status.result.tool_calls || [],
            scratchpad: status.result.scratchpad,
            streaming: false,
            isComplete: true
          };
          updateCurrentMessage(completedMessage);
        }
      }
    }

    // Handle agent-to-agent communications
    if (chunk.result?.type === 'agent_communication') {
      const communication: AgentCommunication = {
        id: `comm_${Date.now()}`,
        sourceAgent: chunk.result.source_agent,
        targetAgent: chunk.result.target_agent,
        message: chunk.result.message,
        timestamp: new Date(),
        status: chunk.result.status,
        latency_ms: chunk.result.latency_ms,
        message_type: chunk.result.message_type
      };
      
      setAgentCommunications(prev => [...prev, communication]);
      
      // Add inter-agent message to chat
      const interAgentMessage: ChatMessage = {
        id: `inter_${Date.now()}`,
        type: 'inter_agent',
        content: `${communication.sourceAgent} → ${communication.targetAgent}: ${communication.message}`,
        timestamp: new Date(),
        a2aTrace: [communication],
        isComplete: true
      };
      
      addMessageToSession(interAgentMessage);
    }
  }, [currentSession]);

  // Add message to current session
  const addMessageToSession = useCallback((message: ChatMessage) => {
    if (!currentSession) return;
    
    const updatedSession = {
      ...currentSession,
      messages: [...currentSession.messages, message],
      updatedAt: new Date()
    };
    setCurrentSession(updatedSession);
    setSessions(prev => prev.map(s => s.id === currentSession.id ? updatedSession : s));
  }, [currentSession]);

  // Update existing message in session
  const updateCurrentMessage = useCallback((message: ChatMessage) => {
    if (!currentSession) return;
    
    const updatedSession = {
      ...currentSession,
      messages: currentSession.messages.map(m => m.id === message.id ? message : m),
      updatedAt: new Date()
    };
    setCurrentSession(updatedSession);
    setSessions(prev => prev.map(s => s.id === currentSession.id ? updatedSession : s));
  }, [currentSession]);

  // Upload file to backend
  const uploadFile = useCallback(async (file: File): Promise<FileAttachment> => {
    const formData = new FormData();
    formData.append('file', file);

    const fileAttachment: FileAttachment = {
      id: `file_${Date.now()}`,
      name: file.name,
      type: file.type,
      size: file.size,
      url: '',
      uploadProgress: 0,
      processingStatus: 'pending'
    };

    try {
      // Mock upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        fileAttachment.uploadProgress = progress;
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // In real implementation, upload to backend
      const response = await fetch(`${API_BASE}/api/files/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      fileAttachment.url = result.url;
      fileAttachment.processingStatus = 'completed';

    } catch (error) {
      fileAttachment.processingStatus = 'error';
      throw error;
    }

    return fileAttachment;
  }, []);

  // Voice recording functionality
  const startVoiceRecording = useCallback(async (): Promise<MediaRecorder | null> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        const recording: VoiceRecording = {
          id: `voice_${Date.now()}`,
          audioBlob,
          duration: Date.now(), // Calculate actual duration
          isTranscribing: true
        };

        // Transcribe audio (implement with speech-to-text service)
        // recording.transcript = await transcribeAudio(audioBlob);
        recording.transcript = "Voice transcription placeholder";
        recording.isTranscribing = false;
      };

      mediaRecorder.start();
      return mediaRecorder;
    } catch (error) {
      console.error('Voice recording error:', error);
      return null;
    }
  }, []);

  // Export chat session
  const exportSession = useCallback((sessionId: string, format: 'json' | 'md' | 'txt' = 'json') => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session) return;

    let content = '';
    
    if (format === 'json') {
      content = JSON.stringify(session, null, 2);
    } else if (format === 'md') {
      content = `# ${session.name}\n\n`;
      session.messages.forEach(msg => {
        content += `## ${msg.type === 'user' ? 'User' : msg.agentName || 'Assistant'}\n`;
        content += `${msg.content}\n\n`;
        if (msg.citations?.length) {
          content += `### Citations\n`;
          msg.citations.forEach(cite => {
            content += `- [${cite.title}](${cite.url}): ${cite.excerpt}\n`;
          });
          content += '\n';
        }
      });
    } else {
      session.messages.forEach(msg => {
        content += `[${msg.timestamp.toISOString()}] ${msg.type === 'user' ? 'User' : msg.agentName || 'Assistant'}: ${msg.content}\n`;
      });
    }

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${session.name}-${Date.now()}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [sessions]);

  // Helper function to convert blob to base64
  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        resolve(base64.split(',')[1]); // Remove data URL prefix
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  return {
    // Session management
    sessions,
    currentSession,
    setCurrentSession,
    createSession,
    
    // Messaging
    sendA2AMessage,
    uploadFile,
    startVoiceRecording,
    
    // State
    streamingState,
    loading,
    error,
    agentCommunications,
    
    // Utilities
    exportSession,
    
    // Session operations
    deleteSession: (sessionId: string) => {
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
    },
    
    clearError: () => setError(null)
  };
}
