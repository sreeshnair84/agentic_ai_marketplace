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
  Workflow,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Activity,
  X,
  Plus,
  Filter,
  Search,
  Archive,
  Star
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
import { cn } from '@/lib/utils';

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
  <div className="mt-3 border border-blue-200 dark:border-blue-800/50 rounded-xl bg-blue-50/30 dark:bg-blue-900/10 overflow-hidden">
    <Button
      variant="ghost"
      size="sm"
      onClick={onToggle}
      className="w-full justify-between p-3 h-auto hover:bg-blue-100/50 dark:hover:bg-blue-800/20 rounded-none"
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-sm">
          <Brain className="h-4 w-4 text-white" />
        </div>
        <div className="text-left">
          <span className="text-sm font-semibold text-gray-900 dark:text-white">Agent Reasoning</span>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant="outline" className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700">
              {(scratchpad.confidence_score * 100).toFixed(0)}% confidence
            </Badge>
          </div>
        </div>
      </div>
      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
    </Button>
    
    {isExpanded && (
      <div className="p-4 border-t border-blue-200 dark:border-blue-800/50 space-y-4 bg-white/50 dark:bg-gray-900/50">
        <div>
          <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Reasoning Process
          </h4>
          <p className="text-sm text-gray-700 dark:text-gray-300 bg-white/70 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
            {scratchpad.reasoning}
          </p>
        </div>
        
        {scratchpad.thinking.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Thought Process
            </h4>
            <div className="space-y-2">
              {scratchpad.thinking.map((thought, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-white/70 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-medium text-blue-600 dark:text-blue-400">{index + 1}</span>
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{thought}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {scratchpad.alternative_approaches && scratchpad.alternative_approaches.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-white">Alternative Approaches</h4>
            <div className="space-y-2">
              {scratchpad.alternative_approaches.map((approach, index) => (
                <div key={index} className="text-sm text-gray-600 dark:text-gray-400 p-3 bg-gray-50 dark:bg-gray-800/30 rounded-lg border border-gray-200 dark:border-gray-700">
                  {approach}
                </div>
              ))}
            </div>
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
  <div className="mt-3 space-y-3">
    <h4 className="text-sm font-semibold flex items-center gap-2 text-gray-900 dark:text-white">
      <FileText className="h-4 w-4" />
      Sources ({citations.length})
    </h4>
    <div className="grid gap-3">
      {citations.map((citation) => (
        <div 
          key={citation.id} 
          className="p-4 bg-gradient-to-r from-emerald-50 to-blue-50 dark:from-emerald-900/20 dark:to-blue-900/20 rounded-xl border-l-4 border-emerald-400 shadow-sm"
        >
          <div className="flex items-start justify-between mb-2">
            <h5 className="text-sm font-semibold text-gray-900 dark:text-white line-clamp-1">{citation.title}</h5>
            <div className="flex items-center gap-2 ml-4">
              <Badge variant="outline" className="text-xs px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/30 border-emerald-300 dark:border-emerald-700">
                {(citation.confidence * 100).toFixed(0)}%
              </Badge>
              {citation.url && (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="ghost" size="sm" className="p-1 h-auto">
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Open source</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )}
            </div>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 mb-2 line-clamp-2">{citation.excerpt}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">{citation.source}</p>
        </div>
      ))}
    </div>
  </div>
);

interface ToolCallsViewProps {
  toolCalls: ToolCall[];
}

const ToolCallsView: React.FC<ToolCallsViewProps> = ({ toolCalls }) => (
  <div className="mt-3 space-y-3">
    <h4 className="text-sm font-semibold flex items-center gap-2 text-gray-900 dark:text-white">
      <Wrench className="h-4 w-4" />
      Tool Usage ({toolCalls.length})
    </h4>
    <div className="grid gap-3">
      {toolCalls.map((toolCall) => (
        <div 
          key={toolCall.id} 
          className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl border-l-4 border-purple-400 shadow-sm"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center shadow-sm">
                <Wrench className="h-4 w-4 text-white" />
              </div>
              <div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{toolCall.toolName}</span>
                <Badge variant="outline" className="ml-2 text-xs px-2 py-0.5">{toolCall.toolType}</Badge>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {toolCall.status === 'pending' && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
              {toolCall.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-500" />}
              {toolCall.status === 'error' && <AlertCircle className="h-4 w-4 text-red-500" />}
              {toolCall.duration_ms && (
                <span className="text-xs text-gray-500 bg-white/70 dark:bg-gray-800/50 px-2 py-1 rounded">
                  {toolCall.duration_ms}ms
                </span>
              )}
            </div>
          </div>
          
          <Tabs defaultValue="input" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-3">
              <TabsTrigger value="input">Input</TabsTrigger>
              <TabsTrigger value="output">Output</TabsTrigger>
            </TabsList>
            
            <TabsContent value="input" className="mt-0">
              <pre className="text-xs text-gray-700 dark:text-gray-300 p-3 bg-white/70 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700 overflow-auto">
                {JSON.stringify(toolCall.input, null, 2)}
              </pre>
            </TabsContent>
            
            <TabsContent value="output" className="mt-0">
              {toolCall.output ? (
                <pre className="text-xs text-gray-700 dark:text-gray-300 p-3 bg-white/70 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700 overflow-auto">
                  {JSON.stringify(toolCall.output, null, 2)}
                </pre>
              ) : toolCall.error_message ? (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                  <span className="text-sm font-medium text-red-700 dark:text-red-400">Error:</span>
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">{toolCall.error_message}</p>
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400 p-3 italic">No output available</p>
              )}
            </TabsContent>
          </Tabs>
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
    <div className="mt-3 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl border-l-4 border-indigo-400">
      <h4 className="text-sm font-semibold flex items-center gap-2 mb-4 text-gray-900 dark:text-white">
        <Network className="h-4 w-4 text-indigo-500" />
        Agent Communications ({communications.length})
      </h4>
      
      <div className="space-y-3">
        {communications.map((comm) => (
          <div key={comm.id} className="p-3 bg-white/70 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{comm.sourceAgent}</span>
                  <Network className="h-3 w-3 text-indigo-500" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{comm.targetAgent}</span>
                </div>
                <Badge variant="outline" className="text-xs px-2 py-0.5">
                  {comm.message_type}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                {comm.latency_ms && (
                  <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    {comm.latency_ms}ms
                  </span>
                )}
                {comm.status === 'processed' && <CheckCircle className="h-3 w-3 text-green-500" />}
                {comm.status === 'error' && <AlertCircle className="h-3 w-3 text-red-500" />}
              </div>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">{comm.message}</p>
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
    <div className="space-y-3">
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => (
            <div key={file.id} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-sm font-medium text-gray-900 dark:text-white truncate">{file.name}</span>
                {file.uploadProgress !== undefined && file.uploadProgress < 100 && (
                  <Progress value={file.uploadProgress} className="w-full mt-1 h-1" />
                )}
              </div>
              <Badge variant="outline" className="text-xs">
                {file.processingStatus}
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFileRemove(file.id)}
                className="p-1 h-auto text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
      
      <div
        className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all duration-200"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        <Paperclip className="h-8 w-8 mx-auto mb-3 text-gray-400" />
        <p className="text-sm text-gray-600 dark:text-gray-300 font-medium mb-1">
          Drop files here or click to upload
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Supports TXT, PDF, DOC, DOCX, JPG, PNG, MP3, WAV
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
  
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';
  const isInterAgent = message.type === 'inter_agent';
  
  return (
    <div className={cn(
      "group animate-fade-in-up",
      isUser ? "ml-8" : "mr-8"
    )}>
      <div className={cn(
        "flex items-start gap-3 mb-4",
        isUser && "flex-row-reverse"
      )}>
        {/* Avatar */}
        <div className={cn(
          "w-10 h-10 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0",
          isUser 
            ? "bg-gradient-to-r from-blue-600 to-purple-600" 
            : isInterAgent 
            ? "bg-gradient-to-r from-purple-600 to-pink-600"
            : "bg-gradient-to-r from-emerald-500 to-blue-600"
        )}>
          {isUser && <User className="h-5 w-5 text-white" />}
          {!isUser && !isInterAgent && <Bot className="h-5 w-5 text-white" />}
          {isInterAgent && <Network className="h-5 w-5 text-white" />}
        </div>
        
        {/* Message Content */}
        <div className="flex-1 min-w-0">
          <div className={cn(
            "rounded-2xl p-4 shadow-sm border",
            isUser 
              ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white border-blue-300"
              : isSystem
              ? "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700"
              : isInterAgent
              ? "bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800"
              : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
          )}>
            {/* Message Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={cn(
                  "text-sm font-semibold",
                  isUser ? "text-white/90" : "text-gray-900 dark:text-white"
                )}>
                  {isUser ? 'You' : 
                   isInterAgent ? 'Agent Communication' :
                   message.agentName || 'Assistant'}
                </span>
                
                <span className={cn(
                  "text-xs",
                  isUser ? "text-white/70" : "text-gray-500 dark:text-gray-400"
                )}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
                
                {message.streaming && (
                  <Loader2 className={cn(
                    "h-3 w-3 animate-spin",
                    isUser ? "text-white/70" : "text-blue-500"
                  )} />
                )}
              </div>
              
              <div className="flex items-center gap-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onCopy(message.content)}
                        className={cn(
                          "p-1 h-auto opacity-0 group-hover:opacity-100 transition-opacity",
                          isUser 
                            ? "hover:bg-white/20 text-white/70 hover:text-white" 
                            : "hover:bg-gray-100 dark:hover:bg-gray-700"
                        )}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Copy message</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>

            {/* Message Text */}
            <div className={cn(
              "text-sm leading-relaxed",
              isUser ? "text-white" : "text-gray-900 dark:text-white"
            )}>
              <p className="whitespace-pre-wrap">
                {message.content}
                {message.streaming && <span className="animate-pulse">|</span>}
              </p>
            </div>

            {/* File Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <div className="mt-3 space-y-2">
                {message.attachments.map((attachment) => (
                  <div key={attachment.id} className="flex items-center gap-2 text-xs">
                    <Paperclip className="h-3 w-3" />
                    <span>{attachment.name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Agent Scratchpad */}
          {showScratchpad && message.scratchpad && (
            <AgentScratchpadView
              scratchpad={message.scratchpad}
              isExpanded={scratchpadExpanded}
              onToggle={() => setScratchpadExpanded(!scratchpadExpanded)}
            />
          )}

          {/* Citations */}
          {message.citations && message.citations.length > 0 && (
            <CitationsView citations={message.citations} />
          )}

          {/* Tool Calls */}
          {message.toolCalls && message.toolCalls.length > 0 && (
            <ToolCallsView toolCalls={message.toolCalls} />
          )}

          {/* A2A Trace */}
          {message.a2aTrace && (
            <A2ATraceView communications={message.a2aTrace} isExpanded={showA2ATrace} />
          )}
        </div>
      </div>
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
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
      if (mediaRecorder) {
        mediaRecorder.stop();
        setMediaRecorder(null);
      }
      setIsRecording(false);
    } else {
      const recorder = await startVoiceRecording();
      if (recorder) {
        setMediaRecorder(recorder);
        setIsRecording(true);
      }
    }
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
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

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  return (
    <div className="h-full flex bg-gray-50 dark:bg-gray-900">
      {/* Enhanced Session Sidebar */}
      <div className={cn(
        "bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col shadow-lg transition-all duration-300",
        sidebarCollapsed ? "w-16" : "w-80"
      )}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Chat Sessions
              </h2>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2"
            >
              {sidebarCollapsed ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
          </div>
          
          {!sidebarCollapsed && (
            <Button 
              onClick={handleCreateNewSession} 
              className="w-full mt-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          )}
        </div>

        {/* Metadata Selector */}
        {!sidebarCollapsed && (
          <div className="border-b border-gray-200 dark:border-gray-700">
            <MetadataSelector
              selectedContext={selectedContext}
              onSelectionChange={handleContextChange}
              isCollapsed={metadataSelectorCollapsed}
              onToggleCollapse={() => setMetadataSelectorCollapsed(!metadataSelectorCollapsed)}
            />
          </div>
        )}
        
        {/* Sessions List */}
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  "p-3 rounded-xl cursor-pointer transition-all duration-200 group",
                  currentSession?.id === session.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm'
                )}
                onClick={() => setCurrentSession(session)}
              >
                {sidebarCollapsed ? (
                  <div className="flex items-center justify-center">
                    <MessageSquare className="h-5 w-5" />
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <h3 className={cn(
                        "font-medium text-sm truncate",
                        currentSession?.id === session.id ? "text-white" : "text-gray-900 dark:text-white"
                      )}>
                        {session.name}
                      </h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.id);
                        }}
                        className={cn(
                          "p-1 opacity-0 group-hover:opacity-100 transition-opacity",
                          currentSession?.id === session.id 
                            ? "hover:bg-white/20 text-white/70" 
                            : "hover:bg-red-50 text-red-500"
                        )}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className={cn(
                      "flex items-center justify-between mt-2 text-xs",
                      currentSession?.id === session.id ? "text-white/80" : "text-gray-500 dark:text-gray-400"
                    )}>
                      <span>{session.messages.length} messages</span>
                      <span>{session.updatedAt.toLocaleDateString()}</span>
                    </div>
                  </>
                )}
              </div>
            ))}
            
            {sidebarCollapsed && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCreateNewSession}
                      className="w-full p-2"
                    >
                      <Plus className="h-5 w-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>New Chat</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Enhanced Chat Header */}
        <div className="bg-white dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white truncate">
                  {currentSession?.name || 'Select a conversation'}
                </h1>
                
                {/* A2A Agent Selector */}
                {a2aBackendAvailable && availableAgents.length > 0 && (
                  <div className="flex items-center gap-2 ml-4">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Agent:</span>
                    <Select
                      value={selectedAgent?.id || ''}
                      onValueChange={(value) => {
                        const agent = availableAgents.find(a => a.id === value);
                        setSelectedAgent(agent || null);
                      }}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Select agent..." />
                      </SelectTrigger>
                      <SelectContent>
                        {availableAgents.map((agent) => (
                          <SelectItem key={agent.id} value={agent.id}>
                            <div className="flex items-center gap-2">
                              <div className={cn(
                                "w-2 h-2 rounded-full",
                                agent.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                              )} />
                              <span>{agent.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
              
              {/* Status and Context Badges */}
              <div className="flex items-center gap-2 flex-wrap">
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
                
                {selectedAgent && a2aBackendAvailable && (
                  <Badge variant="outline" className="text-xs">
                    <Bot className="h-3 w-3 mr-1" />
                    {selectedAgent.name}
                  </Badge>
                )}
                
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
                <p className="text-sm text-blue-600 dark:text-blue-400 flex items-center mt-2">
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  AI is thinking...
                </p>
              )}
            </div>
            
            {/* Action Buttons */}
            <div className="flex items-center gap-2 ml-4">
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
                      className={showScratchpad ? "bg-blue-50 border-blue-300" : ""}
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
                      className={showA2ATrace ? "bg-purple-50 border-purple-300" : ""}
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
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleExportChat}
                      disabled={!currentSession}
                    >
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
                      <Archive className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>View memory & execution history</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
          
          {error && (
            <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center justify-between">
              <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
              <Button variant="ghost" size="sm" onClick={clearError}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Enhanced Messages Area */}
        <div className="flex-1 overflow-hidden bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
          <ScrollArea className="h-full">
            {currentSession ? (
              <div className="p-6 space-y-6">
                {currentSession.messages.map((message) => (
                  <ChatMessageComponent
                    key={message.id}
                    message={message}
                    showA2ATrace={showA2ATrace}
                    showScratchpad={showScratchpad}
                    onCopy={handleCopyMessage}
                  />
                ))}
                
                {streamingState.isStreaming && !streamingState.currentMessage && (
                  <div className="mr-8 animate-fade-in">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                      <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-sm font-semibold text-gray-900 dark:text-white">AI Assistant</span>
                          <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            ) : (
              <div className="h-full flex items-center justify-center p-8">
                <div className="text-center max-w-md">
                  <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                    <MessageSquare className="h-12 w-12 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Welcome to A2A Chat
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Experience next-generation AI conversations with agent-to-agent communication, 
                    advanced reasoning, and intelligent tool usage.
                  </p>
                  <Button 
                    onClick={handleCreateNewSession}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Start New Conversation
                  </Button>
                </div>
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Enhanced Input Area */}
        {currentSession && (
          <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4 shadow-lg">
            {/* File Upload Area */}
            {files.length > 0 && (
              <div className="mb-4">
                <FileUploadArea
                  files={files}
                  onFilesAdd={handleFileUpload}
                  onFileRemove={(fileId) => setFiles(prev => prev.filter(f => f.id !== fileId))}
                />
              </div>
            )}

            {/* Input Controls */}
            <div className="flex items-end gap-3">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => document.createElement('input').click()}
                      disabled={loading || streamingState.isStreaming}
                      className="p-3 h-auto"
                    >
                      <Paperclip className="h-4 w-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Attach file</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleVoiceToggle}
                      disabled={loading || streamingState.isStreaming}
                      className={cn(
                        "p-3 h-auto transition-colors",
                        isRecording && 'bg-red-500 text-white hover:bg-red-600 border-red-500'
                      )}
                    >
                      {isRecording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>{isRecording ? 'Stop recording' : 'Start voice input'}</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <div className="flex-1 relative">
                <Textarea
                  ref={textareaRef}
                  placeholder="Type your message... (Shift+Enter for new line)"
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyPress}
                  disabled={loading || streamingState.isStreaming}
                  className="resize-none pr-12 py-3 min-h-[48px] max-h-[120px] bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 rounded-xl"
                  rows={1}
                />
                <div className="absolute bottom-2 right-2 flex items-center gap-1">
                  {inputValue.length > 0 && (
                    <span className="text-xs text-gray-400">
                      {inputValue.length}
                    </span>
                  )}
                </div>
              </div>

              <Button
                onClick={handleSendMessage}
                disabled={(!inputValue.trim() && files.length === 0) || loading || streamingState.isStreaming}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white p-3 h-auto shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading || streamingState.isStreaming ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Quick Stats */}
            <div className="flex items-center justify-between mt-3 text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-4">
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
              {inputValue.trim() && (
                <span className="text-blue-500">Ready to send</span>
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