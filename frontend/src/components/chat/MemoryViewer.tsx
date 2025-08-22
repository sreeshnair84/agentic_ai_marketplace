'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Clock, 
  Database,
  Search,
  Filter,
  Trash2,
  RefreshCw,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  Activity,
  Zap,
  TrendingUp,
  Calendar,
  Hash,
  FileText,
  AlertCircle,
  CheckCircle,
  Timer
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Progress } from '@/components/ui/progress';

// Types for memory data
interface MemoryItem {
  id: string;
  session_id: string;
  execution_id?: string;
  memory_type: string;
  content: string;
  metadata: Record<string, any>;
  timestamp: string;
  expires_at?: string;
  memory_category?: 'short' | 'long';
  access_count?: number;
  last_accessed?: string;
}

interface MemoryStats {
  session_id: string;
  short_term_count: number;
  long_term_count: number;
  total_executions: number;
  memory_types: string[];
  oldest_memory?: string;
  newest_memory?: string;
}

interface ExecutionHistory {
  execution_id: string;
  started_at: string;
  completed_at: string;
  duration_seconds: number;
  memory_count: number;
  memory_types: string[];
  has_plan: boolean;
  has_results: boolean;
}

interface MemoryViewerProps {
  sessionId: string;
  isOpen: boolean;
  onToggle: () => void;
}

export const MemoryViewer: React.FC<MemoryViewerProps> = ({
  sessionId,
  isOpen,
  onToggle
}) => {
  const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null);
  const [shortTermMemory, setShortTermMemory] = useState<MemoryItem[]>([]);
  const [longTermMemory, setLongTermMemory] = useState<MemoryItem[]>([]);
  const [executionHistory, setExecutionHistory] = useState<ExecutionHistory[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null);
  const [executionDetails, setExecutionDetails] = useState<any>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMemoryType, setSelectedMemoryType] = useState<string>('all');
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Load memory data
  useEffect(() => {
    if (isOpen && sessionId) {
      loadMemoryData();
    }
  }, [isOpen, sessionId]);

  const loadMemoryData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        loadMemoryStats(),
        loadShortTermMemory(),
        loadLongTermMemory(),
        loadExecutionHistory()
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load memory data');
    } finally {
      setLoading(false);
    }
  };

  const loadMemoryStats = async () => {
    const response = await fetch(`${API_BASE}/api/v1/memory/sessions/${sessionId}/stats`);
    if (!response.ok) throw new Error('Failed to load memory stats');
    const data = await response.json();
    setMemoryStats(data);
  };

  const loadShortTermMemory = async () => {
    const response = await fetch(
      `${API_BASE}/api/v1/memory/sessions/${sessionId}/short-term?limit=100`
    );
    if (!response.ok) throw new Error('Failed to load short-term memory');
    const data = await response.json();
    setShortTermMemory(data.items || []);
  };

  const loadLongTermMemory = async () => {
    const response = await fetch(
      `${API_BASE}/api/v1/memory/sessions/${sessionId}/long-term?limit=50`
    );
    if (!response.ok) throw new Error('Failed to load long-term memory');
    const data = await response.json();
    setLongTermMemory(data.items || []);
  };

  const loadExecutionHistory = async () => {
    const response = await fetch(
      `${API_BASE}/api/v1/memory/sessions/${sessionId}/executions`
    );
    if (!response.ok) throw new Error('Failed to load execution history');
    const data = await response.json();
    setExecutionHistory(data.executions || []);
  };

  const loadExecutionDetails = async (executionId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/memory/sessions/${sessionId}/executions/${executionId}`
      );
      if (!response.ok) throw new Error('Failed to load execution details');
      const data = await response.json();
      setExecutionDetails(data);
      setSelectedExecution(executionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load execution details');
    }
  };

  const searchMemory = async () => {
    if (!searchTerm.trim()) return;
    
    try {
      setLoading(true);
      const memoryTypes = selectedMemoryType !== 'all' ? [selectedMemoryType] : undefined;
      
      const response = await fetch(
        `${API_BASE}/api/v1/memory/sessions/${sessionId}/memory/search`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: searchTerm,
            memory_types: memoryTypes,
            limit: 50
          })
        }
      );
      
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      
      // Update memory lists with search results
      const shortResults = data.results.filter((r: any) => r.memory_category === 'short');
      const longResults = data.results.filter((r: any) => r.memory_category === 'long');
      
      setShortTermMemory(shortResults);
      setLongTermMemory(longResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const clearMemory = async (memoryType?: string) => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (memoryType) params.append('memory_type', memoryType);
      
      const response = await fetch(
        `${API_BASE}/api/v1/memory/sessions/${sessionId}/memory?${params}`,
        { method: 'DELETE' }
      );
      
      if (!response.ok) throw new Error('Failed to clear memory');
      
      // Reload data
      await loadMemoryData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear memory');
    } finally {
      setLoading(false);
    }
  };

  const toggleItemExpansion = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  const getMemoryTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'metadata_loaded': 'bg-blue-100 text-blue-800',
      'query_analysis': 'bg-green-100 text-green-800',
      'execution_plan': 'bg-purple-100 text-purple-800',
      'step_result': 'bg-orange-100 text-orange-800',
      'workflow_completion': 'bg-indigo-100 text-indigo-800',
      'error': 'bg-red-100 text-red-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (!isOpen) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={onToggle}
        className="fixed bottom-4 right-4 z-50"
      >
        <Brain className="h-4 w-4 mr-2" />
        Memory
      </Button>
    );
  }

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 shadow-lg z-40">
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>Memory Viewer</span>
            </h2>
            <Button variant="ghost" size="sm" onClick={onToggle}>
              <EyeOff className="h-4 w-4" />
            </Button>
          </div>
          
          {memoryStats && (
            <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
              <div className="text-center">
                <div className="font-medium text-blue-600">{memoryStats.short_term_count}</div>
                <div className="text-gray-500">Short-term</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-green-600">{memoryStats.long_term_count}</div>
                <div className="text-gray-500">Long-term</div>
              </div>
              <div className="text-center">
                <div className="font-medium text-purple-600">{memoryStats.total_executions}</div>
                <div className="text-gray-500">Executions</div>
              </div>
            </div>
          )}
        </div>

        {/* Search and Controls */}
        <div className="p-3 border-b border-gray-200 dark:border-gray-700 space-y-2">
          <div className="flex space-x-2">
            <div className="flex-1">
              <Input
                placeholder="Search memory..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="text-sm"
              />
            </div>
            <Button size="sm" onClick={searchMemory} disabled={loading}>
              <Search className="h-3 w-3" />
            </Button>
          </div>
          
          <div className="flex space-x-2">
            <Select value={selectedMemoryType} onValueChange={setSelectedMemoryType}>
              <SelectTrigger className="flex-1 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {memoryStats?.memory_types.map(type => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button size="sm" variant="outline" onClick={loadMemoryData} disabled={loading}>
              <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border-b border-red-200">
            <div className="flex items-center space-x-2 text-red-600 text-sm">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Content */}
        <ScrollArea className="flex-1">
          <Tabs defaultValue="executions" className="h-full">
            <TabsList className="grid w-full grid-cols-3 m-2">
              <TabsTrigger value="executions" className="text-xs">Executions</TabsTrigger>
              <TabsTrigger value="short-term" className="text-xs">Short-term</TabsTrigger>
              <TabsTrigger value="long-term" className="text-xs">Long-term</TabsTrigger>
            </TabsList>

            {/* Execution History */}
            <TabsContent value="executions" className="p-3 space-y-2">
              {executionHistory.map((execution) => (
                <Card key={execution.execution_id} className="cursor-pointer hover:shadow-sm">
                  <CardContent className="p-3">
                    <div 
                      className="flex items-center justify-between"
                      onClick={() => loadExecutionDetails(execution.execution_id)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Hash className="h-3 w-3 text-gray-400" />
                          <span className="text-xs font-mono">{execution.execution_id.slice(-8)}</span>
                          {execution.has_results && <CheckCircle className="h-3 w-3 text-green-500" />}
                        </div>
                        <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                          <Timer className="h-3 w-3" />
                          <span>{formatDuration(execution.duration_seconds)}</span>
                          <Separator orientation="vertical" className="h-3" />
                          <span>{execution.memory_count} items</span>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4" />
                    </div>
                    
                    {selectedExecution === execution.execution_id && executionDetails && (
                      <div className="mt-3 pt-3 border-t space-y-2">
                        <div className="text-xs">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">Execution Timeline</span>
                            <Badge variant="outline" className="text-xs">
                              {executionDetails.memory_items?.length} steps
                            </Badge>
                          </div>
                          
                          <div className="space-y-2">
                            {executionDetails.memory_items?.map((item: any, index: number) => (
                              <div key={index} className="flex items-start space-x-2">
                                <div className="w-2 h-2 rounded-full bg-blue-400 mt-1 flex-shrink-0" />
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2">
                                    <Badge className={`text-xs ${getMemoryTypeColor(item.memory_type)}`}>
                                      {item.memory_type}
                                    </Badge>
                                    <span className="text-xs text-gray-500">
                                      {formatTimestamp(item.timestamp)}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                                    {item.content}
                                  </p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
              
              {executionHistory.length === 0 && !loading && (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No executions found</p>
                </div>
              )}
            </TabsContent>

            {/* Short-term Memory */}
            <TabsContent value="short-term" className="p-3 space-y-2">
              {shortTermMemory.map((item) => (
                <Card key={item.id} className="hover:shadow-sm">
                  <CardContent className="p-3">
                    <Collapsible>
                      <CollapsibleTrigger 
                        className="flex items-center justify-between w-full text-left"
                        onClick={() => toggleItemExpansion(item.id)}
                      >
                        <div className="flex items-center space-x-2">
                          <Badge className={`text-xs ${getMemoryTypeColor(item.memory_type)}`}>
                            {item.memory_type}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(item.timestamp)}
                          </span>
                        </div>
                        {expandedItems.has(item.id) ? 
                          <ChevronDown className="h-3 w-3" /> : 
                          <ChevronRight className="h-3 w-3" />
                        }
                      </CollapsibleTrigger>
                      
                      <div className="mt-2 text-xs text-gray-600">
                        {item.content.length > 100 && !expandedItems.has(item.id)
                          ? `${item.content.substring(0, 100)}...`
                          : item.content.substring(0, 200)}
                      </div>
                      
                      <CollapsibleContent>
                        {item.content.length > 200 && (
                          <div className="mt-2 text-xs text-gray-600">
                            {item.content.substring(200)}
                          </div>
                        )}
                        
                        {Object.keys(item.metadata).length > 0 && (
                          <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                            <div className="font-medium mb-1">Metadata:</div>
                            <pre className="text-xs overflow-x-auto">
                              {JSON.stringify(item.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                        
                        {item.expires_at && (
                          <div className="mt-2 flex items-center space-x-1 text-xs text-orange-500">
                            <Clock className="h-3 w-3" />
                            <span>Expires: {formatTimestamp(item.expires_at)}</span>
                          </div>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  </CardContent>
                </Card>
              ))}
              
              {shortTermMemory.length === 0 && !loading && (
                <div className="text-center py-8 text-gray-500">
                  <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No short-term memory</p>
                </div>
              )}
            </TabsContent>

            {/* Long-term Memory */}
            <TabsContent value="long-term" className="p-3 space-y-2">
              {longTermMemory.map((item) => (
                <Card key={item.id} className="hover:shadow-sm">
                  <CardContent className="p-3">
                    <Collapsible>
                      <CollapsibleTrigger 
                        className="flex items-center justify-between w-full text-left"
                        onClick={() => toggleItemExpansion(item.id)}
                      >
                        <div className="flex items-center space-x-2">
                          <Badge className={`text-xs ${getMemoryTypeColor(item.memory_type)}`}>
                            {item.memory_type}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(item.timestamp)}
                          </span>
                          {item.access_count && item.access_count > 1 && (
                            <Badge variant="outline" className="text-xs">
                              {item.access_count}x accessed
                            </Badge>
                          )}
                        </div>
                        {expandedItems.has(item.id) ? 
                          <ChevronDown className="h-3 w-3" /> : 
                          <ChevronRight className="h-3 w-3" />
                        }
                      </CollapsibleTrigger>
                      
                      <div className="mt-2 text-xs text-gray-600">
                        {item.content.length > 100 && !expandedItems.has(item.id)
                          ? `${item.content.substring(0, 100)}...`
                          : item.content.substring(0, 200)}
                      </div>
                      
                      <CollapsibleContent>
                        {item.content.length > 200 && (
                          <div className="mt-2 text-xs text-gray-600">
                            {item.content.substring(200)}
                          </div>
                        )}
                        
                        {Object.keys(item.metadata).length > 0 && (
                          <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
                            <div className="font-medium mb-1">Metadata:</div>
                            <pre className="text-xs overflow-x-auto">
                              {JSON.stringify(item.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                        
                        {item.last_accessed && (
                          <div className="mt-2 flex items-center space-x-1 text-xs text-blue-500">
                            <TrendingUp className="h-3 w-3" />
                            <span>Last accessed: {formatTimestamp(item.last_accessed)}</span>
                          </div>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  </CardContent>
                </Card>
              ))}
              
              {longTermMemory.length === 0 && !loading && (
                <div className="text-center py-8 text-gray-500">
                  <Database className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No long-term memory</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </ScrollArea>

        {/* Footer */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-2">
            <Button 
              size="sm" 
              variant="outline" 
              className="flex-1 text-xs"
              onClick={() => clearMemory()}
              disabled={loading}
            >
              <Trash2 className="h-3 w-3 mr-1" />
              Clear All
            </Button>
            <Button 
              size="sm" 
              variant="outline" 
              className="flex-1 text-xs"
              onClick={() => clearMemory(selectedMemoryType !== 'all' ? selectedMemoryType : undefined)}
              disabled={loading || selectedMemoryType === 'all'}
            >
              <Filter className="h-3 w-3 mr-1" />
              Clear Type
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};