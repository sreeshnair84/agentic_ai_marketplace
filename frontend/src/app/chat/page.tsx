'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Send, 
  Bot, 
  User, 
  Paperclip, 
  Mic, 
  Download,
  Network,
  Eye,
  EyeOff,
  Settings,
  MessageSquare,
  Workflow
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  agentName?: string;
  timestamp: string;
  attachments?: string[];
  a2aTrace?: A2ATrace;
}

interface A2ATrace {
  sourceAgent: string;
  targetAgent: string;
  message: string;
  timestamp: string;
  status: 'sent' | 'received' | 'processed';
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  agents: string[];
  status: 'active' | 'inactive';
}

const mockWorkflows: Workflow[] = [
  {
    id: '1',
    name: 'Customer Support Flow',
    description: 'Handles customer inquiries with classification and routing',
    agents: ['Classifier Agent', 'Support Agent', 'Escalation Agent'],
    status: 'active'
  },
  {
    id: '2',
    name: 'Document Analysis',
    description: 'Analyzes documents and extracts insights',
    agents: ['Document Reader', 'Text Analyzer', 'Summary Generator'],
    status: 'active'
  },
  {
    id: '3',
    name: 'Research Pipeline',
    description: 'Conducts research and generates comprehensive reports',
    agents: ['Web Researcher', 'Data Analyzer', 'Report Writer'],
    status: 'inactive'
  }
];

const mockMessages: Message[] = [
  {
    id: '1',
    type: 'system',
    content: 'Customer Support Flow activated. Ready to assist with your inquiry.',
    timestamp: '10:30 AM',
  },
  {
    id: '2',
    type: 'user',
    content: 'I need help with my account billing issue.',
    timestamp: '10:31 AM',
  },
  {
    id: '3',
    type: 'agent',
    agentName: 'Classifier Agent',
    content: 'I\'ve analyzed your request and identified this as a billing inquiry. Routing to our billing specialist.',
    timestamp: '10:31 AM',
    a2aTrace: {
      sourceAgent: 'Classifier Agent',
      targetAgent: 'Support Agent',
      message: 'BILLING_INQUIRY: User needs help with account billing',
      timestamp: '10:31 AM',
      status: 'processed'
    }
  },
  {
    id: '4',
    type: 'agent',
    agentName: 'Support Agent',
    content: 'Hello! I can help you with your billing issue. Could you please provide your account number or email address?',
    timestamp: '10:32 AM',
  }
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [inputValue, setInputValue] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>(mockWorkflows[0].id);
  const [showA2ATrace, setShowA2ATrace] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');

    // Simulate agent response
    setTimeout(() => {
      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        agentName: 'Support Agent',
        content: 'I understand your concern. Let me help you with that right away.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, agentResponse]);
    }, 1000);
  };

  const handleFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleVoiceRecord = () => {
    setIsRecording(!isRecording);
    // Implement voice recording logic here
  };

  const exportChatHistory = () => {
    const chatData = {
      workflow: mockWorkflows.find(w => w.id === selectedWorkflow)?.name,
      messages: messages,
      exportedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-history-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const selectedWorkflowData = mockWorkflows.find(w => w.id === selectedWorkflow);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Chat Interface
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Interact with your multi-agent workflow system
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Workflow Selector */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Workflow className="h-5 w-5" />
                  <span>Workflows</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockWorkflows.map((workflow) => (
                    <div
                      key={workflow.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedWorkflow === workflow.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => setSelectedWorkflow(workflow.id)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-sm">{workflow.name}</h3>
                        <Badge variant={workflow.status === 'active' ? 'default' : 'outline'}>
                          {workflow.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-300 mb-2">
                        {workflow.description}
                      </p>
                      <div className="flex items-center space-x-1">
                        <Bot className="h-3 w-3 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {workflow.agents.length} agents
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Active Workflow Info */}
            {selectedWorkflowData && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="text-sm">Active Workflow</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <h3 className="font-medium">{selectedWorkflowData.name}</h3>
                    <div className="space-y-1">
                      {selectedWorkflowData.agents.map((agent, index) => (
                        <div key={index} className="flex items-center space-x-2 text-sm">
                          <Bot className="h-3 w-3 text-blue-500" />
                          <span>{agent}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col">
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="h-5 w-5" />
                    <span>Chat</span>
                  </CardTitle>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowA2ATrace(!showA2ATrace)}
                    >
                      {showA2ATrace ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      A2A Trace
                    </Button>
                    <Button variant="outline" size="sm" onClick={exportChatHistory}>
                      <Download className="h-4 w-4" />
                      Export
                    </Button>
                    <Button variant="outline" size="sm">
                      <Settings className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              {/* Messages */}
              <CardContent className="flex-1 overflow-y-auto p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div key={message.id} className="space-y-2">
                      <div
                        className={`flex ${
                          message.type === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-3 ${
                            message.type === 'user'
                              ? 'bg-blue-500 text-white'
                              : message.type === 'system'
                              ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                              : 'bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'
                          }`}
                        >
                          {message.type === 'agent' && (
                            <div className="flex items-center space-x-2 mb-2">
                              <Bot className="h-4 w-4 text-blue-500" />
                              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                                {message.agentName}
                              </span>
                              <span className="text-xs text-gray-500">
                                {message.timestamp}
                              </span>
                            </div>
                          )}
                          {message.type === 'user' && (
                            <div className="flex items-center space-x-2 mb-2">
                              <User className="h-4 w-4" />
                              <span className="text-sm font-medium">You</span>
                              <span className="text-xs opacity-75">
                                {message.timestamp}
                              </span>
                            </div>
                          )}
                          <p className="text-sm">{message.content}</p>
                        </div>
                      </div>

                      {/* A2A Trace */}
                      {showA2ATrace && message.a2aTrace && (
                        <div className="ml-8 p-2 bg-purple-50 dark:bg-purple-900/20 rounded border-l-2 border-purple-300">
                          <div className="flex items-center space-x-2 mb-1">
                            <Network className="h-3 w-3 text-purple-500" />
                            <span className="text-xs font-medium text-purple-700 dark:text-purple-300">
                              A2A Communication
                            </span>
                          </div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">
                            {message.a2aTrace.sourceAgent} → {message.a2aTrace.targetAgent}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {message.a2aTrace.message}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </CardContent>

              {/* Input Area */}
              <div className="border-t p-4">
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleFileUpload}
                  >
                    <Paperclip className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleVoiceRecord}
                    className={isRecording ? 'bg-red-500 text-white' : ''}
                  >
                    <Mic className="h-4 w-4" />
                  </Button>
                  <Input
                    placeholder="Type your message..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1"
                  />
                  <Button onClick={handleSendMessage}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  multiple
                  onChange={(e) => {
                    // Handle file upload
                    console.log('Files:', e.target.files);
                  }}
                />
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
