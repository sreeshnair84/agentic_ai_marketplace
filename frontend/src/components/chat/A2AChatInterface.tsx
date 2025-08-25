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
  <div className="mt-3 border border-blue-200/30 dark:border-blue-700/30 rounded-xl bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-900/10 dark:to-purple-900/10 backdrop-blur-sm">
    <Button
      variant="ghost"
      size="sm"
      onClick={onToggle}
      className="w-full justify-between p-3 h-auto rounded-t-xl hover:bg-blue-50/50 dark:hover:bg-blue-900/20"
    >
      <div className="flex items-center space-x-3">
        <div className="p-1.5 rounded-lg bg-gradient-to-br from-blue-400 to-purple-500 text-white">
          <Brain className="h-4 w-4" />
        </div>
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">Agent Thinking Process</span>
        <Badge className="text-xs font-medium px-2.5 py-1 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 dark:from-blue-900/30 dark:to-purple-900/30 dark:text-blue-300 border-0">
          {(scratchpad.confidence_score * 100).toFixed(0)}% confidence
        </Badge>
      </div>
      <div className={`p-1 rounded-lg transition-colors ${isExpanded ? 'bg-blue-100 dark:bg-blue-800' : ''}`}>
        {isExpanded ? <Minimize2 className="h-4 w-4 text-blue-600" /> : <Maximize2 className="h-4 w-4 text-gray-500" />}
      </div>
    </Button>
    
    {isExpanded && (
      <div className="p-4 border-t border-blue-200/20 dark:border-blue-700/20 space-y-4">
        <div className="p-3 rounded-lg bg-white/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-600/50">
          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
            Reasoning
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{scratchpad.reasoning}</p>
        </div>
        
        {scratchpad.thinking.length > 0 && (
          <div className="p-3 rounded-lg bg-white/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-600/50">
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
              Thought Process
            </h4>
            <ul className="space-y-2">
              {scratchpad.thinking.map((thought, index) => (
                <li key={index} className="text-sm text-gray-600 dark:text-gray-300 flex items-start space-x-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 mt-2 flex-shrink-0"></div>
                  <span className="leading-relaxed">{thought}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {scratchpad.alternative_approaches && scratchpad.alternative_approaches.length > 0 && (
          <div className="p-3 rounded-lg bg-white/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-600/50">
            <h4 className="text-sm font-semibold mb-3 flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
              Alternative Approaches
            </h4>
            <ul className="space-y-2">
              {scratchpad.alternative_approaches.map((approach, index) => (
                <li key={index} className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed pl-3 border-l-2 border-amber-200/50 dark:border-amber-700/50">
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
  <div className="mt-3 space-y-3">
    <h4 className="text-sm font-semibold flex items-center space-x-3 text-gray-700 dark:text-gray-300">
      <div className="p-1.5 rounded-lg bg-gradient-to-br from-emerald-400 to-blue-500 text-white">
        <FileText className="h-4 w-4" />
      </div>
      <span>Sources ({citations.length})</span>
    </h4>
    <div className="space-y-3">
      {citations.map((citation) => (
        <div 
          key={citation.id} 
          className="group p-4 bg-gradient-to-r from-emerald-50/50 to-blue-50/50 dark:from-emerald-900/10 dark:to-blue-900/10 rounded-xl border border-emerald-200/30 dark:border-emerald-700/30 backdrop-blur-sm hover:shadow-lg hover:shadow-emerald-500/10 transition-all duration-200"
        >
          <div className="flex items-start justify-between mb-3">
            <h5 className="text-sm font-semibold text-gray-800 dark:text-gray-200 leading-tight flex-1 mr-3">
              {citation.title}
            </h5>
            <div className="flex items-center space-x-2 flex-shrink-0">
              <Badge className="text-xs font-medium px-2.5 py-1 bg-gradient-to-r from-emerald-100 to-blue-100 text-emerald-800 dark:from-emerald-900/30 dark:to-blue-900/30 dark:text-emerald-300 border-0">
                {(citation.confidence * 100).toFixed(0)}%
              </Badge>
              {citation.url && (
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="p-2 h-8 w-8 rounded-lg hover:bg-emerald-100 hover:text-emerald-600 dark:hover:bg-emerald-900/20 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2 leading-relaxed bg-white/50 dark:bg-gray-800/50 p-2 rounded-lg border border-gray-200/50 dark:border-gray-600/50">
            "{citation.excerpt}"
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
            <span>{citation.source}</span>
          </div>
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
    <h4 className="text-sm font-semibold flex items-center space-x-3 text-gray-700 dark:text-gray-300">
      <div className="p-1.5 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 text-white">
        <Wrench className="h-4 w-4" />
      </div>
      <span>Tool Usage ({toolCalls.length})</span>
    </h4>
    <div className="space-y-3">
      {toolCalls.map((toolCall) => (
        <div 
          key={toolCall.id} 
          className="group p-4 bg-gradient-to-r from-purple-50/50 to-pink-50/50 dark:from-purple-900/10 dark:to-pink-900/10 rounded-xl border border-purple-200/30 dark:border-purple-700/30 backdrop-blur-sm hover:shadow-lg hover:shadow-purple-500/10 transition-all duration-200"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white shadow-lg ${
                toolCall.status === 'completed' ? 'bg-gradient-to-br from-emerald-400 to-emerald-600' :
                toolCall.status === 'error' ? 'bg-gradient-to-br from-red-400 to-red-600' :
                'bg-gradient-to-br from-amber-400 to-amber-600'
              }`}>
                {toolCall.status === 'pending' && <Loader2 className="h-4 w-4 animate-spin" />}
                {toolCall.status === 'completed' && <CheckCircle className="h-4 w-4" />}
                {toolCall.status === 'error' && <AlertCircle className="h-4 w-4" />}
              </div>
              <div>
                <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{toolCall.toolName}</span>
                <Badge className="ml-2 text-xs font-medium px-2.5 py-1 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 dark:from-purple-900/30 dark:to-pink-900/30 dark:text-purple-300 border-0">
                  {toolCall.toolType}
                </Badge>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {toolCall.duration_ms && (
                <Badge variant="outline" className="text-xs font-medium border-gray-300 dark:border-gray-600">
                  <Clock className="h-3 w-3 mr-1" />
                  {toolCall.duration_ms}ms
                </Badge>
              )}
            </div>
          </div>
          
          <div className="text-sm space-y-3">
            <div className="p-3 rounded-lg bg-white/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-600/50">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                <span className="font-semibold text-gray-700 dark:text-gray-300">Input</span>
              </div>
              <pre className="text-xs text-gray-600 dark:text-gray-300 bg-gray-50/50 dark:bg-gray-900/50 p-2 rounded border overflow-x-auto">
                {JSON.stringify(toolCall.input, null, 2)}
              </pre>
            </div>
            
            {toolCall.output && (
              <div className="p-3 rounded-lg bg-white/50 dark:bg-gray-800/50 border border-gray-200/50 dark:border-gray-600/50">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                  <span className="font-semibold text-gray-700 dark:text-gray-300">Output</span>
                </div>
                <pre className="text-xs text-gray-600 dark:text-gray-300 bg-gray-50/50 dark:bg-gray-900/50 p-2 rounded border overflow-x-auto">
                  {JSON.stringify(toolCall.output, null, 2)}
                </pre>
              </div>
            )}
            
            {toolCall.error_message && (
              <div className="p-3 rounded-lg bg-red-50/50 dark:bg-red-900/20 border border-red-200/50 dark:border-red-700/50">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-red-500"></div>
                  <span className="font-semibold text-red-700 dark:text-red-300">Error</span>
                </div>
                <p className="text-sm text-red-600 dark:text-red-400 leading-relaxed">{toolCall.error_message}</p>
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
    <div className="mt-3 p-4 bg-gradient-to-r from-purple-50/50 to-indigo-50/50 dark:from-purple-900/10 dark:to-indigo-900/10 rounded-xl border border-purple-200/30 dark:border-purple-700/30 backdrop-blur-sm">
      <h4 className="text-sm font-semibold flex items-center space-x-3 mb-4 text-gray-700 dark:text-gray-300">
        <div className="p-1.5 rounded-lg bg-gradient-to-br from-purple-400 to-indigo-500 text-white">
          <Network className="h-4 w-4" />
        </div>
        <span>Agent Communications ({communications.length})</span>
      </h4>
      
      <div className="space-y-3">
        {communications.map((comm, index) => (
          <div key={comm.id} className="relative">
            {/* Connection Line */}
            {index < communications.length - 1 && (
              <div className="absolute left-4 top-12 w-px h-6 bg-gradient-to-b from-purple-300 to-transparent dark:from-purple-600"></div>
            )}
            
            <div className="flex items-start space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white shadow-lg flex-shrink-0 ${
                comm.status === 'processed' ? 'bg-gradient-to-br from-emerald-400 to-emerald-600' :
                comm.status === 'error' ? 'bg-gradient-to-br from-red-400 to-red-600' :
                'bg-gradient-to-br from-purple-400 to-indigo-500'
              }`}>
                {comm.status === 'processed' && <CheckCircle className="h-4 w-4" />}
                {comm.status === 'error' && <AlertCircle className="h-4 w-4" />}
                {comm.status !== 'processed' && comm.status !== 'error' && <Network className="h-4 w-4" />}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2 min-w-0">
                    <span className="text-sm font-semibold text-gray-800 dark:text-gray-200 truncate">
                      {comm.sourceAgent}
                    </span>
                    <div className="flex items-center space-x-1 text-purple-500">
                      <div className="w-1 h-1 rounded-full bg-purple-400"></div>
                      <div className="w-1 h-1 rounded-full bg-purple-400"></div>
                      <div className="w-1 h-1 rounded-full bg-purple-400"></div>
                    </div>
                    <span className="text-sm font-semibold text-gray-800 dark:text-gray-200 truncate">
                      {comm.targetAgent}
                    </span>
                    <Badge className="text-xs font-medium px-2 py-1 bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-800 dark:from-purple-900/30 dark:to-indigo-900/30 dark:text-purple-300 border-0">
                      {comm.message_type}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    {comm.latency_ms && (
                      <Badge variant="outline" className="text-xs font-medium border-gray-300 dark:border-gray-600">
                        <Clock className="h-3 w-3 mr-1" />
                        {comm.latency_ms}ms
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg border border-gray-200/50 dark:border-gray-600/50">
                  <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{comm.message}</p>
                </div>
              </div>
            </div>
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
    <div className="group space-y-3">
      <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
        <div className={`max-w-[85%] ${
          message.type === 'user'
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25'
            : message.type === 'system'
            ? 'bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 text-gray-700 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50'
            : message.type === 'inter_agent'
            ? 'bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 text-purple-700 dark:text-purple-300 border border-purple-200/30 dark:border-purple-700/30'
            : 'bg-white/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50 backdrop-blur-xl shadow-lg shadow-gray-500/10'
        } rounded-2xl p-4 transition-all duration-200 hover:shadow-xl ${
          message.type === 'user' ? 'hover:shadow-blue-500/30' : 'hover:shadow-gray-500/20'
        }`}>
          {/* Message Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
                message.type === 'user' 
                  ? 'bg-white/20 text-white' 
                  : message.type === 'system'
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                  : message.type === 'inter_agent'
                  ? 'bg-gradient-to-br from-purple-400 to-indigo-500 text-white'
                  : 'bg-gradient-to-br from-blue-400 to-blue-600 text-white'
              }`}>
                {message.type === 'user' && <User className="h-4 w-4" />}
                {message.type === 'agent' && <Bot className="h-4 w-4" />}
                {message.type === 'inter_agent' && <Network className="h-4 w-4" />}
                {message.type === 'system' && <Settings className="h-4 w-4" />}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-semibold">
                    {message.type === 'user' ? 'You' : 
                     message.type === 'inter_agent' ? 'Agent Communication' :
                     message.type === 'system' ? 'System' :
                     message.agentName || 'Assistant'}
                  </span>
                  
                  {message.streaming && (
                    <div className="flex items-center space-x-1">
                      <Loader2 className="h-3 w-3 animate-spin" />
                      <span className="text-xs opacity-75">typing...</span>
                    </div>
                  )}
                </div>
                
                <span className="text-xs opacity-60">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onCopy(message.content)}
                      className={`p-2 h-8 w-8 rounded-lg ${
                        message.type === 'user' 
                          ? 'hover:bg-white/20 text-white/80 hover:text-white' 
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
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
          <div className="text-sm leading-relaxed">
            <p className="whitespace-pre-wrap">
              {message.content}
              {message.streaming && <span className="animate-pulse ml-1 text-blue-400">●</span>}
            </p>
          </div>

          {/* File Attachments */}
          {message.attachments && message.attachments.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.attachments.map((attachment) => (
                <div key={attachment.id} className="flex items-center space-x-2 text-xs p-2 rounded-lg bg-black/10 dark:bg-white/10">
                  <div className="p-1 rounded bg-gray-200 dark:bg-gray-700">
                    <Paperclip className="h-3 w-3" />
                  </div>
                  <span className="font-medium">{attachment.name}</span>
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
                    {selectedContext.type === 'llm' && selectedContext.llm_model && (
                      <Badge variant="outline" className="text-xs">
                        <Zap className="h-3 w-3 mr-1" />
                        {selectedContext.llm_model.display_name}
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
