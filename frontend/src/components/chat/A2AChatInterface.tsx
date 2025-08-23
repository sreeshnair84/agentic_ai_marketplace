'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  Mic, 
  Square,
  Download,
  Settings,
  MessageSquare,
  Bot,
  User,
  Network,
  Eye,
  EyeOff,
  Brain,
  Wrench,
  FileText,
  Trash2,
  MoreVertical,
  Maximize2,
  Minimize2,
  Copy,
  ExternalLink,
  Zap,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Workflow
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useA2AChatEnhanced, ChatMessage, FileAttachment, AgentScratchpad, Citation, ToolCall, AgentCommunication } from '@/hooks/useA2AChat';
import { MetadataSelector, SelectedContext } from './MetadataSelector';
import { MemoryViewer } from './MemoryViewer';

interface AgentScratchpadViewProps {
  scratchpad: AgentScratchpad;
  isExpanded: boolean;
  onToggle: () => void;
}

const AgentScratchpadView: React.FC<AgentScratchpadViewProps> = ({ 
  scratchpad, 
  isExpanded, 
  onToggle 
}) => (
  <div className="mt-2 border border-blue-200 dark:border-blue-800 rounded-lg">
    <Button
      variant="ghost"
      size="sm"
      onClick={onToggle}
      className="w-full justify-between p-2 h-auto"
    >
      <div className="flex items-center space-x-2">
        <Brain className="h-4 w-4 text-blue-500" />
        <span className="text-sm font-medium">Agent Thinking Process</span>
        <Badge variant="outline" className="text-xs">
          {(scratchpad.confidence_score * 100).toFixed(0)}% confidence
        </Badge>
      </div>
      {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
    </Button>
    
    {isExpanded && (
      <div className="p-3 border-t space-y-3">
        <div>
          <h4 className="text-sm font-medium mb-2">Reasoning</h4>
          <p className="text-sm text-gray-600 dark:text-gray-300">{scratchpad.reasoning}</p>
        </div>
        
        {scratchpad.thinking.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Thought Process</h4>
            <ul className="space-y-1">
              {scratchpad.thinking.map((thought, index) => (
                <li key={index} className="text-sm text-gray-600 dark:text-gray-300 flex items-start space-x-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>{thought}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {scratchpad.alternative_approaches && scratchpad.alternative_approaches.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Alternative Approaches</h4>
            <ul className="space-y-1">
              {scratchpad.alternative_approaches.map((approach, index) => (
                <li key={index} className="text-sm text-gray-500 dark:text-gray-400">
                  {approach}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )}
  </div>
);

interface CitationsViewProps {
  citations: Citation[];
}

const CitationsView: React.FC<CitationsViewProps> = ({ citations }) => (
  <div className="mt-2 space-y-2">
    <h4 className="text-sm font-medium flex items-center space-x-2">
      <FileText className="h-4 w-4" />
      <span>Sources ({citations.length})</span>
    </h4>
    <div className="space-y-2">
      {citations.map((citation) => (
        <div 
          key={citation.id} 
          className="p-2 bg-gray-50 dark:bg-gray-800 rounded border-l-2 border-blue-300"
        >
          <div className="flex items-center justify-between mb-1">
            <h5 className="text-sm font-medium">{citation.title}</h5>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-xs">
                {(citation.confidence * 100).toFixed(0)}%
              </Badge>
              {citation.url && (
                <Button variant="ghost" size="sm" className="p-1">
                  <ExternalLink className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-300">{citation.excerpt}</p>
          <p className="text-xs text-gray-500 mt-1">{citation.source}</p>
        </div>
      ))}
    </div>
  </div>
);

interface ToolCallsViewProps {
  toolCalls: ToolCall[];
}

const ToolCallsView: React.FC<ToolCallsViewProps> = ({ toolCalls }) => (
  <div className="mt-2 space-y-2">
    <h4 className="text-sm font-medium flex items-center space-x-2">
      <Wrench className="h-4 w-4" />
      <span>Tool Usage ({toolCalls.length})</span>
    </h4>
    <div className="space-y-2">
      {toolCalls.map((toolCall) => (
        <div 
          key={toolCall.id} 
          className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded border-l-2 border-purple-300"
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">{toolCall.toolName}</span>
              <Badge variant="outline" className="text-xs">{toolCall.toolType}</Badge>
            </div>
            <div className="flex items-center space-x-2">
              {toolCall.status === 'pending' && <Loader2 className="h-3 w-3 animate-spin" />}
              {toolCall.status === 'completed' && <CheckCircle className="h-3 w-3 text-green-500" />}
              {toolCall.status === 'error' && <AlertCircle className="h-3 w-3 text-red-500" />}
              {toolCall.duration_ms && (
                <span className="text-xs text-gray-500">{toolCall.duration_ms}ms</span>
              )}
            </div>
          </div>
          
          <div className="text-xs space-y-1">
            <div>
              <span className="font-medium">Input:</span>
              <pre className="text-gray-600 dark:text-gray-300 mt-1 p-1 bg-gray-100 dark:bg-gray-800 rounded">
                {JSON.stringify(toolCall.input, null, 2)}
              </pre>
            </div>
            
            {toolCall.output && (
              <div>
                <span className="font-medium">Output:</span>
                <pre className="text-gray-600 dark:text-gray-300 mt-1 p-1 bg-gray-100 dark:bg-gray-800 rounded">
                  {JSON.stringify(toolCall.output, null, 2)}
                </pre>
              </div>
            )}
            
            {toolCall.error_message && (
              <div>
                <span className="font-medium text-red-600">Error:</span>
                <p className="text-red-600 mt-1">{toolCall.error_message}</p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  </div>
);

interface A2ATraceViewProps {
  communications: AgentCommunication[];
  isExpanded: boolean;
}

const A2ATraceView: React.FC<A2ATraceViewProps> = ({ communications, isExpanded }) => {
  if (!isExpanded || communications.length === 0) return null;

  return (
    <div className="mt-2 p-3 bg-purple-50 dark:bg-purple-900/20 rounded border-l-2 border-purple-300">
      <h4 className="text-sm font-medium flex items-center space-x-2 mb-2">
        <Network className="h-4 w-4 text-purple-500" />
        <span>Agent Communications ({communications.length})</span>
      </h4>
      
      <div className="space-y-2">
        {communications.map((comm) => (
          <div key={comm.id} className="text-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="font-medium">{comm.sourceAgent}</span>
                <span className="text-purple-500">→</span>
                <span className="font-medium">{comm.targetAgent}</span>
                <Badge variant="outline" className="text-xs">
                  {comm.message_type}
                </Badge>
              </div>
              <div className="flex items-center space-x-2">
                {comm.latency_ms && (
                  <span className="text-gray-500">{comm.latency_ms}ms</span>
                )}
                {comm.status === 'processed' && <CheckCircle className="h-3 w-3 text-green-500" />}
                {comm.status === 'error' && <AlertCircle className="h-3 w-3 text-red-500" />}
              </div>
            </div>
            <p className="text-gray-600 dark:text-gray-300 mt-1">{comm.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

interface FileUploadAreaProps {
  files: FileAttachment[];
  onFilesAdd: (files: File[]) => void;
  onFileRemove: (fileId: string) => void;
}

const FileUploadArea: React.FC<FileUploadAreaProps> = ({ files, onFilesAdd, onFileRemove }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      onFilesAdd(Array.from(e.target.files));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      onFilesAdd(Array.from(e.dataTransfer.files));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="space-y-2">
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => (
            <div key={file.id} className="flex items-center space-x-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
              <FileText className="h-4 w-4" />
              <span className="text-sm flex-1">{file.name}</span>
              {file.uploadProgress !== undefined && file.uploadProgress < 100 && (
                <Progress value={file.uploadProgress} className="w-20" />
              )}
              <Badge variant="outline" className="text-xs">
                {file.processingStatus}
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFileRemove(file.id)}
                className="p-1"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
      
      <div
        className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 text-center cursor-pointer hover:border-blue-400 transition-colors"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        <Paperclip className="h-6 w-6 mx-auto mb-2 text-gray-400" />
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Drop files here or click to upload
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileSelect}
          accept=".txt,.pdf,.doc,.docx,.jpg,.jpeg,.png,.mp3,.wav"
        />
      </div>
    </div>
  );
};

interface ChatMessageProps {
  message: ChatMessage;
  showA2ATrace: boolean;
  showScratchpad: boolean;
  onCopy: (content: string) => void;
}

const ChatMessageComponent: React.FC<ChatMessageProps> = ({ 
  message, 
  showA2ATrace, 
  showScratchpad,
  onCopy 
}) => {
  const [scratchpadExpanded, setScratchpadExpanded] = useState(false);
  
  return (
    <div className="space-y-2">
      <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[80%] rounded-lg p-3 ${
          message.type === 'user'
            ? 'bg-blue-500 text-white'
            : message.type === 'system'
            ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
            : message.type === 'inter_agent'
            ? 'bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300'
            : 'bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'
        }`}>
          {/* Message Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              {message.type === 'user' && <User className="h-4 w-4" />}
              {message.type === 'agent' && <Bot className="h-4 w-4 text-blue-500" />}
              {message.type === 'inter_agent' && <Network className="h-4 w-4 text-purple-500" />}
              
              <span className="text-sm font-medium">
                {message.type === 'user' ? 'You' : 
                 message.type === 'inter_agent' ? 'Agent Communication' :
                 message.agentName || 'Assistant'}
              </span>
              
              <span className="text-xs opacity-75">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              
              {message.streaming && (
                <Loader2 className="h-3 w-3 animate-spin" />
              )}
            </div>
            
            <div className="flex items-center space-x-1">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onCopy(message.content)}
                      className="p-1"
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Copy message</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>

          {/* Message Content */}
          <div className="text-sm">
            <p>{message.content}{message.streaming && <span className="animate-pulse">|</span>}</p>
          </div>

          {/* File Attachments */}
          {message.attachments && message.attachments.length > 0 && (
            <div className="mt-2 space-y-1">
              {message.attachments.map((attachment) => (
                <div key={attachment.id} className="flex items-center space-x-2 text-xs">
                  <Paperclip className="h-3 w-3" />
                  <span>{attachment.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Agent Scratchpad */}
      {showScratchpad && message.scratchpad && (
        <div className="ml-8">
          <AgentScratchpadView
            scratchpad={message.scratchpad}
            isExpanded={scratchpadExpanded}
            onToggle={() => setScratchpadExpanded(!scratchpadExpanded)}
          />
        </div>
      )}

      {/* Citations */}
      {message.citations && message.citations.length > 0 && (
        <div className="ml-8">
          <CitationsView citations={message.citations} />
        </div>
      )}

      {/* Tool Calls */}
      {message.toolCalls && message.toolCalls.length > 0 && (
        <div className="ml-8">
          <ToolCallsView toolCalls={message.toolCalls} />
        </div>
      )}

      {/* A2A Trace */}
      {message.a2aTrace && (
        <div className="ml-8">
          <A2ATraceView communications={message.a2aTrace} isExpanded={showA2ATrace} />
        </div>
      )}
    </div>
  );
};

export const A2AChatInterface: React.FC = () => {
  const {
    sessions,
    currentSession,
    setCurrentSession,
    createSession,
    selectedContext,
    updateSessionContext,
    sendA2AMessage,
    uploadFile,
    startVoiceRecording,
    availableAgents,
    selectedAgent,
    setSelectedAgent,
    a2aBackendAvailable,
    initializeA2A,
    streamingState,
    loading,
    error,
    agentCommunications,
    exportSession,
    deleteSession,
    clearError
  } = useA2AChatEnhanced();

  const [inputValue, setInputValue] = useState('');
  const [files, setFiles] = useState<FileAttachment[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [showA2ATrace, setShowA2ATrace] = useState(false);
  const [showScratchpad, setShowScratchpad] = useState(true);
  const [metadataSelectorCollapsed, setMetadataSelectorCollapsed] = useState(false);
  const [showMemoryViewer, setShowMemoryViewer] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentSession?.messages]);

  useEffect(() => {
    if (!currentSession && sessions.length === 0) {
      createSession('New Chat');
    }
  }, [currentSession, sessions, createSession]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() && files.length === 0) return;
    if (!currentSession) return;

    try {
      await sendA2AMessage(inputValue, files);
      setInputValue('');
      setFiles([]);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (newFiles: File[]) => {
    try {
      const uploadPromises = newFiles.map(uploadFile);
      const uploadedFiles = await Promise.all(uploadPromises);
      setFiles(prev => [...prev, ...uploadedFiles]);
    } catch (error) {
      console.error('File upload failed:', error);
    }
  };

  const handleVoiceToggle = async () => {
    if (isRecording) {
      // Stop recording
      if (mediaRecorder) {
        mediaRecorder.stop();
        setMediaRecorder(null);
      }
      setIsRecording(false);
    } else {
      // Start recording
      const recorder = await startVoiceRecording();
      if (recorder) {
        setMediaRecorder(recorder);
        setIsRecording(true);
      }
    }
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    // You could add a toast notification here
  };

  const handleExportChat = () => {
    if (currentSession) {
      exportSession(currentSession.id, 'json');
    }
  };

  const handleCreateNewSession = () => {
    createSession(`Chat ${sessions.length + 1}`, selectedContext);
  };

  const handleContextChange = (context: SelectedContext) => {
    updateSessionContext(context);
  };

  return (
    <div className="h-full flex">
      {/* Session Sidebar */}
      <div className="w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Metadata Selector */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <MetadataSelector
            selectedContext={selectedContext}
            onSelectionChange={handleContextChange}
            isCollapsed={metadataSelectorCollapsed}
            onToggleCollapse={() => setMetadataSelectorCollapsed(!metadataSelectorCollapsed)}
          />
        </div>
        
        <div className="p-4 border-b">
          <Button onClick={handleCreateNewSession} className="w-full">
            <MessageSquare className="h-4 w-4 mr-2" />
            New Chat
          </Button>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`p-3 rounded cursor-pointer transition-colors ${
                  currentSession?.id === session.id
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => setCurrentSession(session)}
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-sm truncate">{session.name}</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="p-1"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {session.messages.length} messages
                </p>
                <p className="text-xs text-gray-400">
                  {session.updatedAt.toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-semibold">
                  {currentSession?.name || 'Select a conversation'}
                </h1>
                
                {/* A2A Agent Selector */}
                {a2aBackendAvailable && availableAgents.length > 0 && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Agent:</span>
                    <Select
                      value={selectedAgent?.id || ''}
                      onValueChange={(value) => {
                        const agent = availableAgents.find(a => a.id === value);
                        setSelectedAgent(agent || null);
                      }}
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="Select agent..." />
                      </SelectTrigger>
                      <SelectContent>
                        {availableAgents.map((agent) => (
                          <SelectItem key={agent.id} value={agent.id}>
                            <div className="flex items-center space-x-2">
                              <div className={`h-2 w-2 rounded-full ${
                                agent.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                              }`} />
                              <span>{agent.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2 mt-1">
                {/* Backend Status */}
                <Badge variant={a2aBackendAvailable ? "default" : "secondary"} className="text-xs">
                  {a2aBackendAvailable ? (
                    <>
                      <CheckCircle className="h-3 w-3 mr-1" />
                      A2A Connected
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Mock Mode
                    </>
                  )}
                </Badge>
                
                {/* Selected Agent Info */}
                {selectedAgent && a2aBackendAvailable && (
                  <Badge variant="outline" className="text-xs">
                    <Bot className="h-3 w-3 mr-1" />
                    {selectedAgent.name}
                  </Badge>
                )}
                
                {/* Context Info */}
                {selectedContext.type && (
                  <>
                    {selectedContext.type === 'workflow' && selectedContext.workflow && (
                      <Badge variant="outline" className="text-xs">
                        <Workflow className="h-3 w-3 mr-1" />
                        {selectedContext.workflow.display_name}
                      </Badge>
                    )}
                    {selectedContext.type === 'agent' && selectedContext.agent && (
                      <Badge variant="outline" className="text-xs">
                        <Bot className="h-3 w-3 mr-1" />
                        {selectedContext.agent.display_name}
                      </Badge>
                    )}
                    {selectedContext.type === 'tools' && selectedContext.tools && (
                      <Badge variant="outline" className="text-xs">
                        <Wrench className="h-3 w-3 mr-1" />
                        {selectedContext.tools.length} tools
                      </Badge>
                    )}
                  </>
                )}
              </div>
              
              {streamingState.isStreaming && (
                <p className="text-sm text-gray-500 flex items-center mt-1">
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  AI is thinking...
                </p>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Retry A2A Connection */}
              {!a2aBackendAvailable && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={initializeA2A}
                        className="text-orange-600 border-orange-300 hover:bg-orange-50"
                      >
                        <Zap className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Retry A2A connection</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
              
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowScratchpad(!showScratchpad)}
                    >
                      <Brain className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Toggle thinking process</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowA2ATrace(!showA2ATrace)}
                    >
                      {showA2ATrace ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Toggle A2A communications</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="sm" onClick={handleExportChat}>
                      <Download className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Export chat</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setShowMemoryViewer(!showMemoryViewer)}
                    >
                      <Brain className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>View memory & execution history</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {error && (
            <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded flex items-center justify-between">
              <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
              <Button variant="ghost" size="sm" onClick={clearError}>
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          {currentSession ? (
            <div className="space-y-4">
              {currentSession.messages.map((message) => (
                <ChatMessageComponent
                  key={message.id}
                  message={message}
                  showA2ATrace={showA2ATrace}
                  showScratchpad={showScratchpad}
                  onCopy={handleCopyMessage}
                />
              ))}
              
              {/* Only show streaming indicator if no message is being streamed yet */}
              {streamingState.isStreaming && !streamingState.currentMessage && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600">
                    <div className="flex items-center space-x-2 mb-2">
                      <Bot className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">AI Assistant</span>
                      <Loader2 className="h-3 w-3 animate-spin" />
                    </div>
                    <div className="text-sm">
                      <span className="animate-pulse">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  Welcome to A2A Chat
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Start a new conversation or select an existing one
                </p>
              </div>
            </div>
          )}
        </ScrollArea>

        {/* Input Area */}
        {currentSession && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
            {/* File Upload Area */}
            {files.length > 0 && (
              <FileUploadArea
                files={files}
                onFilesAdd={handleFileUpload}
                onFileRemove={(fileId) => setFiles(prev => prev.filter(f => f.id !== fileId))}
              />
            )}

            {/* Input Controls */}
            <div className="flex items-end space-x-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => handleFileUpload([])}
                disabled={loading || streamingState.isStreaming}
              >
                <Paperclip className="h-4 w-4" />
              </Button>

              <Button
                variant="outline"
                size="icon"
                onClick={handleVoiceToggle}
                disabled={loading || streamingState.isStreaming}
                className={isRecording ? 'bg-red-500 text-white hover:bg-red-600' : ''}
              >
                {isRecording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </Button>

              <div className="flex-1">
                <Textarea
                  ref={textareaRef}
                  placeholder="Type your message..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading || streamingState.isStreaming}
                  className="resize-none"
                  rows={1}
                />
              </div>

              <Button
                onClick={handleSendMessage}
                disabled={(!inputValue.trim() && files.length === 0) || loading || streamingState.isStreaming}
              >
                {loading || streamingState.isStreaming ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <span>Press Shift+Enter for new line</span>
              <Separator orientation="vertical" className="h-3" />
              <span>{currentSession.messages.length} messages</span>
              {agentCommunications.length > 0 && (
                <>
                  <Separator orientation="vertical" className="h-3" />
                  <span>{agentCommunications.length} agent communications</span>
                </>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Memory Viewer */}
      <MemoryViewer
        sessionId={currentSession?.id || ''}
        isOpen={showMemoryViewer}
        onToggle={() => setShowMemoryViewer(!showMemoryViewer)}
      />
    </div>
  );
};
