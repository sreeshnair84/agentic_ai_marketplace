import { useState, useCallback, useRef, useEffect } from 'react';
import { mockA2AService } from '@/services/mockA2AService';
import { a2aService, A2AAgent } from '@/services/a2aService';
import { SelectedContext, WorkflowMetadata, AgentMetadata, ToolMetadata } from '@/components/chat/MetadataSelector';

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

// Chat Message with Enhanced Context
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
  context?: SelectedContext; // Enhanced: track message context
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

// Enhanced Chat Session with Context
export interface ChatSession {
  id: string;
  name: string;
  workflowId?: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, any>;
  context?: SelectedContext; // Enhanced: session context
}

// Routing Information
export interface RoutingInfo {
  routing_url: string;
  dns_name?: string;
  base_url?: string;
  health_url?: string;
  capabilities?: any;
  input_modes?: string[];
  output_modes?: string[];
  status: string;
  available: boolean;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AGENTS_BASE = process.env.NEXT_PUBLIC_AGENTS_URL || 'http://localhost:8002';
const ORCHESTRATOR_BASE = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8003';
const USE_MOCK_SERVICE = process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_MOCK_A2A === 'true';

export function useA2AChatEnhanced() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [selectedContext, setSelectedContext] = useState<SelectedContext>({ type: null });
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    currentMessage: '',
    chunks: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentCommunications, setAgentCommunications] = useState<AgentCommunication[]>([]);
  
  // A2A specific state
  const [availableAgents, setAvailableAgents] = useState<A2AAgent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<A2AAgent | null>(null);
  const [a2aBackendAvailable, setA2aBackendAvailable] = useState(false);
  
  // WebSocket connection for real-time updates
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Initialize A2A backend connection and fetch agents
  const initializeA2A = useCallback(async () => {
    try {
      // Check if A2A backend is available
      const isAvailable = await a2aService.isAvailable();
      setA2aBackendAvailable(isAvailable);

      if (isAvailable) {
        // Fetch available agents
        const agentsResponse = await a2aService.listAgents();
        if (agentsResponse.success) {
          setAvailableAgents(agentsResponse.agents);
          
          // Set default agent if available
          if (agentsResponse.agents.length > 0 && !selectedAgent) {
            const defaultAgent = agentsResponse.agents.find(a => a.id === 'general_assistant') 
              || agentsResponse.agents[0];
            setSelectedAgent(defaultAgent);
          }
        }
      }
    } catch (error) {
      console.warn('A2A initialization failed:', error);
      setA2aBackendAvailable(false);
    }
  }, [selectedAgent]);

  // Use effect to initialize A2A on mount
  useEffect(() => {
    initializeA2A();
  }, [initializeA2A]);

  // Create new chat session with context
  const createSession = useCallback(async (name: string, context?: SelectedContext): Promise<ChatSession> => {
    const newSession: ChatSession = {
      id: `session_${Date.now()}`,
      name,
      workflowId: context?.workflow?.id,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      metadata: { context },
      context
    };
    
    setSessions(prev => [...prev, newSession]);
    setCurrentSession(newSession);
    return newSession;
  }, []);

  // Update session context
  const updateSessionContext = useCallback((context: SelectedContext) => {
    setSelectedContext(context);
    
    if (currentSession) {
      const updatedSession = {
        ...currentSession,
        context,
        metadata: { ...currentSession.metadata, context },
        updatedAt: new Date()
      };
      setCurrentSession(updatedSession);
      setSessions(prev => prev.map(s => s.id === currentSession.id ? updatedSession : s));
    }
  }, [currentSession]);

  // Get routing information based on context
  const getRoutingInfo = useCallback(async (context: SelectedContext): Promise<RoutingInfo | null> => {
    try {
      if (context.type === 'workflow' && context.workflow) {
        const response = await fetch(`${API_BASE}/api/v1/metadata/workflow/${context.workflow.name}/routing`);
        if (response.ok) {
          return await response.json();
        }
      } else if (context.type === 'agent' && context.agent) {
        const response = await fetch(`${API_BASE}/api/v1/metadata/agent/${context.agent.name}/routing`);
        if (response.ok) {
          return await response.json();
        }
      }
      return null;
    } catch (error) {
      console.error('Failed to get routing info:', error);
      return null;
    }
  }, []);

  // Get default workflow for when no context is selected
  const getDefaultWorkflow = useCallback(async (): Promise<any> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/metadata/default-workflow`);
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error('Failed to get default workflow:', error);
      return null;
    }
  }, []);

  // Determine the target URL for A2A communication
  const getTargetUrl = useCallback(async (context: SelectedContext): Promise<string> => {
    // Get routing info based on context
    const routingInfo = await getRoutingInfo(context);
    
    if (routingInfo?.available && routingInfo.routing_url) {
      return routingInfo.routing_url;
    }
    
    // Fallback routing logic
    if (context.type === 'workflow' && context.workflow) {
      // Workflow-specific routing
      if (context.workflow.dns_name) {
        return `http://${context.workflow.dns_name}/a2a/message/stream`;
      } else if (context.workflow.url) {
        return `${context.workflow.url}/a2a/message/stream`;
      }
    } else if (context.type === 'agent' && context.agent) {
      // Agent-specific routing
      if (context.agent.a2a_address) {
        return `${context.agent.a2a_address}/a2a/message/stream`;
      } else if (context.agent.dns_name) {
        return `https://${context.agent.dns_name}/a2a/message/stream`;
      } else if (context.agent.url) {
        return `${context.agent.url}/a2a/message/stream`;
      }
    } else if (context.type === 'tools' && context.tools) {
      // Tools routing - use default workflow with tools context
      const defaultWorkflow = await getDefaultWorkflow();
      if (defaultWorkflow && defaultWorkflow.dns_name) {
        return `http://${defaultWorkflow.dns_name}/a2a/message/stream`;
      }
      return `${AGENTS_BASE}/a2a/agents/general/stream`;
    }
    
    // Default to the smart workflow service
    const defaultWorkflow = await getDefaultWorkflow();
    if (defaultWorkflow && defaultWorkflow.dns_name) {
      return `http://${defaultWorkflow.dns_name}/a2a/message/stream`;
    }
    
    // Final fallback to orchestrator
    return `${ORCHESTRATOR_BASE}/a2a/message/stream`;
  }, [getRoutingInfo, getDefaultWorkflow]);

  // Enhanced send A2A message with context-aware routing
  const sendA2AMessage = useCallback(async (
    message: string,
    attachments: FileAttachment[] = [],
    voiceRecording?: VoiceRecording,
    contextOverride?: SelectedContext
  ): Promise<void> => {
    if (!currentSession) return;
    
    const activeContext = contextOverride || selectedContext;
    setError(null);
    setLoading(true);

    try {
      // Create user message with context
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        type: 'user',
        content: message,
        timestamp: new Date(),
        attachments,
        isComplete: true,
        context: activeContext
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

      // Enhanced JSON-RPC request with context
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
          },
          context: activeContext, // Include context in request
          tools: activeContext.type === 'tools' ? activeContext.tools?.map(t => t.name) : undefined
        }
      };

      // Get target URL based on context
      const targetUrl = await getTargetUrl(activeContext);
      
      // Send streaming request to appropriate endpoint
      await handleStreamingResponse(rpcRequest, targetUrl, activeContext);

    } catch (error) {
      console.error('Error sending A2A message:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }, [currentSession, selectedContext, getTargetUrl]);

  // Enhanced streaming response handler with context awareness
  const handleStreamingResponse = useCallback(async (
    rpcRequest: any, 
    targetUrl: string, 
    context: SelectedContext
  ) => {
    if (!currentSession) return;

    let currentAgentMessage: ChatMessage | null = null;

    try {
      setStreamingState({
        isStreaming: true,
        currentMessage: '',
        chunks: []
      });

      if (USE_MOCK_SERVICE || !a2aBackendAvailable) {
        // Use mock service for development with context or when A2A backend is not available
        const messageText = rpcRequest.params.message.parts[0]?.text || '';
        
        for await (const chunk of mockA2AService.generateMockA2AResponse(
          messageText, 
          currentSession.id,
          context
        )) {
          currentAgentMessage = await processStreamChunk(chunk, currentAgentMessage, context);
        }
      } else {
        // Use real A2A service
        const chatRequest = {
          message: rpcRequest.params.message.parts[0]?.text || '',
          agent_id: selectedAgent?.id,
          session_id: currentSession.id,
          conversation_history: currentSession.messages
            .filter(m => m.type !== 'system' && m.type !== 'inter_agent')
            .slice(-10) // Keep last 10 messages for context
            .map(m => ({
              role: m.type === 'user' ? 'user' : 'assistant',
              content: m.content,
              timestamp: m.timestamp.toISOString()
            }))
        };

        // Stream responses from A2A backend
        try {
          for await (const chunk of a2aService.streamChatMessage(chatRequest)) {
            // Map A2A response format to expected chunk format
            const mappedChunk = {
              result: {
                type: 'task_status_update',
                status: {
                  type: chunk.final ? 'completed' : 'in_progress',
                  message: {
                    parts: [{ text: chunk.message || chunk.chunk || '' }]
                  },
                  result: chunk.final ? {
                    content: chunk.message || currentAgentMessage?.content || '',
                    citations: chunk.citations || [],
                    tool_calls: chunk.tool_calls || [],
                    scratchpad: chunk.scratchpad || null
                  } : null
                }
              }
            };

            currentAgentMessage = await processStreamChunk(mappedChunk, currentAgentMessage, context);
            
            if (chunk.final) {
              break;
            }
          }
        } catch (streamError) {
          console.error('A2A streaming error:', streamError);
          // Fallback to mock service
          const messageText = rpcRequest.params.message.parts[0]?.text || '';
          for await (const chunk of mockA2AService.generateMockA2AResponse(
            messageText, 
            currentSession.id,
            context
          )) {
            currentAgentMessage = await processStreamChunk(chunk, currentAgentMessage, context);
          }
        }
      }

      // Final cleanup: ensure streaming is stopped
      setStreamingState({
        isStreaming: false,
        currentMessage: '',
        chunks: []
      });

      // Mark the current message as complete if it exists
      if (currentAgentMessage) {
        const completedMessage = {
          ...currentAgentMessage,
          streaming: false,
          isComplete: true
        };
        updateCurrentMessage(completedMessage);
      }

    } catch (error) {
      console.error('Streaming error:', error);
      setError(error instanceof Error ? error.message : 'Streaming failed');
      setStreamingState({
        isStreaming: false,
        currentMessage: '',
        chunks: []
      });

      // If there's an incomplete message, mark it as complete with error
      if (currentAgentMessage && currentAgentMessage.streaming) {
        const errorMessage = {
          ...currentAgentMessage,
          streaming: false,
          isComplete: true,
          content: currentAgentMessage.content + '\n\n⚠️ Message interrupted due to connection error.'
        };
        updateCurrentMessage(errorMessage);
      }
    }
  }, [currentSession, a2aBackendAvailable, selectedAgent]);

  // Enhanced stream chunk processing with context
  const processStreamChunk = useCallback(async (
    chunk: any,
    currentAgentMessage: ChatMessage | null,
    context: SelectedContext
  ): Promise<ChatMessage | null> => {
    if (!currentSession) return currentAgentMessage;

    if (chunk.result?.type === 'task_status_update') {
      const status = chunk.result.status;
      
      if (status.type === 'in_progress') {
        const messageText = status.message?.parts?.[0]?.text || '';
        
        // Update streaming state for display
        setStreamingState(prev => ({
          ...prev,
          currentMessage: prev.currentMessage + messageText,
          chunks: [...prev.chunks, messageText]
        }));

        // Create or update agent message
        if (!currentAgentMessage) {
          const newAgentMessage: ChatMessage = {
            id: `msg_${Date.now()}`,
            type: 'agent',
            content: messageText,
            agentName: getAgentNameFromContext(context, status),
            timestamp: new Date(),
            streaming: true,
            isComplete: false,
            context
          };
          addMessageToSession(newAgentMessage);
          return newAgentMessage;
        } else {
          const updatedMessage: ChatMessage = {
            ...currentAgentMessage,
            content: currentAgentMessage.content + messageText,
            context
          };
          updateCurrentMessage(updatedMessage);
          return updatedMessage;
        }
      } else if (status.type === 'completed' && status.result) {
        // Handle completion with citations, tool calls, etc.
        if (currentAgentMessage) {
          const completedMessage: ChatMessage = {
            ...currentAgentMessage,
            content: status.result.content || currentAgentMessage.content,
            citations: status.result.citations || [],
            toolCalls: status.result.tool_calls || [],
            scratchpad: status.result.scratchpad,
            streaming: false,
            isComplete: true,
            context
          };
          updateCurrentMessage(completedMessage);
          
          // Clear streaming state since message is complete
          setStreamingState({
            isStreaming: false,
            currentMessage: '',
            chunks: []
          });
          
          return completedMessage;
        }
      }
    }

    // Handle agent-to-agent communications with context
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
      
      // Add inter-agent message to chat with context
      const interAgentMessage: ChatMessage = {
        id: `inter_${Date.now()}`,
        type: 'inter_agent',
        content: `${communication.sourceAgent} → ${communication.targetAgent}: ${communication.message}`,
        timestamp: new Date(),
        a2aTrace: [communication],
        isComplete: true,
        context
      };
      
      addMessageToSession(interAgentMessage);
    }

    return currentAgentMessage;
  }, [currentSession]);

  // Helper to get agent name from context
  const getAgentNameFromContext = (context: SelectedContext, status: any): string => {
    if (context.type === 'workflow' && context.workflow) {
      return context.workflow.display_name;
    } else if (context.type === 'agent' && context.agent) {
      return context.agent.display_name;
    } else if (context.type === 'tools' && context.tools) {
      return `Generic Agent (${context.tools.length} tools)`;
    }
    return status.result?.agent_name || 'AI Assistant';
  };

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
      if (session.context) {
        content += `**Context:** ${session.context.type}\n\n`;
      }
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
    
    // Context management
    selectedContext,
    updateSessionContext,
    
    // Messaging
    sendA2AMessage,
    uploadFile,
    startVoiceRecording,
    
    // Routing
    getRoutingInfo,
    
    // A2A Agent management
    availableAgents,
    selectedAgent,
    setSelectedAgent,
    a2aBackendAvailable,
    initializeA2A,
    
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