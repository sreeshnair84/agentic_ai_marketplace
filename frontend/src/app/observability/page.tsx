'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { StandardPageLayout, StandardSection } from '@/components/layout/StandardPageLayout';
import { 
  Activity, 
  Eye, 
  Search, 
  Filter, 
  Network,
  MessageSquare,
  Bot,
  Zap,
  Clock,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Download,
  Settings,
  PlayCircle,
  PauseCircle
} from 'lucide-react';

interface A2AMessage {
  id: string;
  sourceAgent: string;
  targetAgent: string;
  type: 'request' | 'response' | 'notification' | 'error';
  payload: string;
  timestamp: string;
  duration: number;
  status: 'success' | 'pending' | 'failed';
  traceId: string;
}

interface AgentMetrics {
  agentId: string;
  agentName: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  messagesProcessed: number;
  avgResponseTime: number;
  errorRate: number;
  lastActive: string;
  cpuUsage: number;
  memoryUsage: number;
}

interface TraceData {
  id: string;
  workflowName: string;
  totalDuration: number;
  spans: Array<{
    id: string;
    agentName: string;
    operation: string;
    duration: number;
    startTime: string;
    status: 'success' | 'error' | 'pending';
  }>;
  status: 'completed' | 'running' | 'failed';
  timestamp: string;
}

const mockA2AMessages: A2AMessage[] = [
  {
    id: '1',
    sourceAgent: 'Classifier Agent',
    targetAgent: 'Support Agent',
    type: 'request',
    payload: 'CLASSIFY_INQUIRY: Customer billing question',
    timestamp: '2024-08-12 14:30:15',
    duration: 245,
    status: 'success',
    traceId: 'trace-123-456'
  },
  {
    id: '2',
    sourceAgent: 'Support Agent',
    targetAgent: 'Knowledge Agent',
    type: 'request',
    payload: 'QUERY_KNOWLEDGE: billing_policies',
    timestamp: '2024-08-12 14:30:16',
    duration: 1200,
    status: 'success',
    traceId: 'trace-123-456'
  },
  {
    id: '3',
    sourceAgent: 'Knowledge Agent',
    targetAgent: 'Support Agent',
    type: 'response',
    payload: 'KNOWLEDGE_RESULT: Found 3 relevant policies',
    timestamp: '2024-08-12 14:30:17',
    duration: 89,
    status: 'success',
    traceId: 'trace-123-456'
  },
  {
    id: '4',
    sourceAgent: 'Document Agent',
    targetAgent: 'Analysis Agent',
    type: 'request',
    payload: 'ANALYZE_DOCUMENT: contract_v2.pdf',
    timestamp: '2024-08-12 14:29:45',
    duration: 3400,
    status: 'failed',
    traceId: 'trace-789-012'
  }
];

const mockAgentMetrics: AgentMetrics[] = [
  {
    agentId: '1',
    agentName: 'Classifier Agent',
    status: 'online',
    messagesProcessed: 1247,
    avgResponseTime: 245,
    errorRate: 2.1,
    lastActive: '30 seconds ago',
    cpuUsage: 15,
    memoryUsage: 280
  },
  {
    agentId: '2',
    agentName: 'Support Agent',
    status: 'busy',
    messagesProcessed: 892,
    avgResponseTime: 890,
    errorRate: 1.8,
    lastActive: '5 seconds ago',
    cpuUsage: 45,
    memoryUsage: 512
  },
  {
    agentId: '3',
    agentName: 'Knowledge Agent',
    status: 'online',
    messagesProcessed: 2156,
    avgResponseTime: 1200,
    errorRate: 0.9,
    lastActive: '10 seconds ago',
    cpuUsage: 32,
    memoryUsage: 768
  },
  {
    agentId: '4',
    agentName: 'Document Agent',
    status: 'error',
    messagesProcessed: 234,
    avgResponseTime: 3400,
    errorRate: 15.2,
    lastActive: '2 minutes ago',
    cpuUsage: 8,
    memoryUsage: 156
  }
];

const mockTraces: TraceData[] = [
  {
    id: 'trace-123-456',
    workflowName: 'Customer Support Pipeline',
    totalDuration: 1534,
    spans: [
      {
        id: 'span-1',
        agentName: 'Classifier Agent',
        operation: 'classify_inquiry',
        duration: 245,
        startTime: '14:30:15',
        status: 'success'
      },
      {
        id: 'span-2',
        agentName: 'Support Agent',
        operation: 'generate_response',
        duration: 890,
        startTime: '14:30:16',
        status: 'success'
      },
      {
        id: 'span-3',
        agentName: 'Knowledge Agent',
        operation: 'query_knowledge',
        duration: 399,
        startTime: '14:30:16',
        status: 'success'
      }
    ],
    status: 'completed',
    timestamp: '2024-08-12 14:30:15'
  }
];

export default function ObservabilityPage() {
  const [a2aMessages] = useState<A2AMessage[]>(mockA2AMessages);
  const [agentMetrics, setAgentMetrics] = useState<AgentMetrics[]>(mockAgentMetrics);
  const [traces] = useState<TraceData[]>(mockTraces);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMessageType, setSelectedMessageType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);

  // Simulate real-time updates
  useEffect(() => {
    if (!isRealTimeEnabled) return;

    const interval = setInterval(() => {
      setAgentMetrics(prev => prev.map(agent => ({
        ...agent,
        messagesProcessed: agent.messagesProcessed + Math.floor(Math.random() * 5),
        cpuUsage: Math.max(5, Math.min(95, agent.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(50, Math.min(1024, agent.memoryUsage + (Math.random() - 0.5) * 50))
      })));
    }, 3000);

    return () => clearInterval(interval);
  }, [isRealTimeEnabled]);

  const filteredMessages = a2aMessages.filter(message => {
    const matchesSearch = message.sourceAgent.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         message.targetAgent.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         message.payload.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedMessageType === 'all' || message.type === selectedMessageType;
    const matchesStatus = selectedStatus === 'all' || message.status === selectedStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'online':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
      case 'busy':
      case 'running':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'failed':
      case 'error':
      case 'offline':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'online':
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'pending':
      case 'busy':
      case 'running':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'failed':
      case 'error':
      case 'offline':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'request':
        return <MessageSquare className="h-4 w-4 text-blue-500" />;
      case 'response':
        return <MessageSquare className="h-4 w-4 text-green-500" />;
      case 'notification':
        return <MessageSquare className="h-4 w-4 text-purple-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <MessageSquare className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <StandardPageLayout
      title="Observability Dashboard"
      description="Monitor A2A communications, agent performance, and system traces"
      actions={
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setIsRealTimeEnabled(!isRealTimeEnabled)}
          >
            {isRealTimeEnabled ? (
              <PauseCircle className="mr-2 h-4 w-4" />
            ) : (
              <PlayCircle className="mr-2 h-4 w-4" />
            )}
            {isRealTimeEnabled ? 'Pause' : 'Resume'} Real-time
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button variant="outline">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </div>
      }
    >
      <StandardSection>
        {/* System Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Network className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold">{a2aMessages.length}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">A2A Messages</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5 text-green-500" />
                <div>
                  <div className="text-2xl font-bold">
                    {agentMetrics.filter(a => a.status === 'online' || a.status === 'busy').length}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Active Agents</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-purple-500" />
                <div>
                  <div className="text-2xl font-bold">
                    {Math.round(agentMetrics.reduce((acc, a) => acc + a.avgResponseTime, 0) / agentMetrics.length)}ms
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Avg Response</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-orange-500" />
                <div>
                  <div className="text-2xl font-bold">
                    {agentMetrics.filter(a => a.status === 'error').length}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Agents in Error</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agent Metrics */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bot className="h-5 w-5" />
                  <span>Agent Status</span>
                  {isRealTimeEnabled && (
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-xs text-green-600">Live</span>
                    </div>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {agentMetrics.map((agent) => (
                    <div key={agent.agentId} className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(agent.status)}
                          <span className="font-medium text-sm">{agent.agentName}</span>
                        </div>
                        <Badge className={getStatusColor(agent.status)}>
                          {agent.status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-300">
                        <div>
                          <span className="block">Messages: {agent.messagesProcessed}</span>
                          <span className="block">Avg Time: {agent.avgResponseTime}ms</span>
                        </div>
                        <div>
                          <span className="block">CPU: {agent.cpuUsage}%</span>
                          <span className="block">Memory: {agent.memoryUsage}MB</span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        Last active: {agent.lastActive}
                      </div>
                      {agent.errorRate > 10 && (
                        <div className="text-xs text-red-600 mt-1">
                          Error rate: {agent.errorRate}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* A2A Message Stream */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <Network className="h-5 w-5" />
                    <span>A2A Message Stream</span>
                  </CardTitle>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
                
                {/* Filters */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search messages..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <select
                    value={selectedMessageType}
                    onChange={(e) => setSelectedMessageType(e.target.value)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md"
                  >
                    <option value="all">All Types</option>
                    <option value="request">Request</option>
                    <option value="response">Response</option>
                    <option value="notification">Notification</option>
                    <option value="error">Error</option>
                  </select>
                  <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md"
                  >
                    <option value="all">All Status</option>
                    <option value="success">Success</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {filteredMessages.map((message) => (
                    <div key={message.id} className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-2">
                          {getTypeIcon(message.type)}
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="font-medium text-sm">{message.sourceAgent}</span>
                              <span className="text-gray-400">→</span>
                              <span className="font-medium text-sm">{message.targetAgent}</span>
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                              {message.payload}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(message.status)}>
                            {message.status}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {message.type}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                        <div className="text-xs text-gray-500 flex items-center space-x-4">
                          <span>{message.timestamp}</span>
                          <span>Duration: {message.duration}ms</span>
                          <span>Trace: {message.traceId}</span>
                        </div>
                        <Button variant="outline" size="sm" className="text-xs">
                          <Eye className="h-3 w-3 mr-1" />
                          Trace
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Distributed Traces */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Distributed Traces</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {traces.map((trace) => (
                  <div key={trace.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(trace.status)}
                        <div>
                          <h3 className="font-medium">{trace.workflowName}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            Total duration: {trace.totalDuration}ms | {trace.timestamp}
                          </p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(trace.status)}>
                        {trace.status}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      {trace.spans.map((span) => (
                        <div key={span.id} className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          {getStatusIcon(span.status)}
                          <div className="flex-grow">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-sm">{span.agentName}</span>
                              <span className="text-xs text-gray-500">{span.duration}ms</span>
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-300">
                              {span.operation} | {span.startTime}
                            </div>
                          </div>
                          <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-blue-500 h-2 rounded-full" 
                              style={{ width: `${Math.min(100, (span.duration / trace.totalDuration) * 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </StandardSection>
    </StandardPageLayout>
  );
}
