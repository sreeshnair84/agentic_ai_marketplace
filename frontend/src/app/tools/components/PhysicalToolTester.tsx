'use client';

import { useState, useEffect } from 'react';
import { 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Settings,
  Eye,
  Code,
  Zap,
  Clock,
  Download,
  Copy,
  Monitor
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';

interface PhysicalTool {
  name: string;
  category: string;
  description: string;
  version: string;
  methods: string[];
}

interface ToolSchema {
  config_schema: any;
  input_schema: any;
  output_schema: any;
}

interface TestResult {
  status: 'success' | 'error';
  tool_name?: string;
  operation?: string;
  result?: any;
  error?: string;
  execution_time?: number;
  timestamp?: string;
}

interface ToolExecution {
  id: string;
  tool_name: string;
  operation: string;
  parameters: any;
  status: 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  start_time: string;
  end_time?: string;
  execution_time?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export default function PhysicalToolTester() {
  const [availableTools, setAvailableTools] = useState<PhysicalTool[]>([]);
  const [selectedTool, setSelectedTool] = useState<PhysicalTool | null>(null);
  const [toolSchemas, setToolSchemas] = useState<ToolSchema | null>(null);
  const [toolConfig, setToolConfig] = useState<Record<string, any>>({});
  const [executionParameters, setExecutionParameters] = useState<Record<string, any>>({});
  const [selectedOperation, setSelectedOperation] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [executions, setExecutions] = useState<ToolExecution[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [configText, setConfigText] = useState('{}');
  const [parametersText, setParametersText] = useState('{}');

  // Load available tools on component mount
  useEffect(() => {
    loadAvailableTools();
    checkSystemHealth();
  }, []);

  // Load schemas when tool is selected
  useEffect(() => {
    if (selectedTool) {
      loadToolSchemas(selectedTool.name);
      generateExampleConfig(selectedTool.name);
    }
  }, [selectedTool]);

  const loadAvailableTools = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/physical-tools/discover`);
      if (response.ok) {
        const tools = await response.json();
        setAvailableTools(tools);
      } else {
        throw new Error('Failed to load tools');
      }
    } catch (err) {
      setError('Failed to load available tools');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/physical-tools/health`);
      if (response.ok) {
        const health = await response.json();
        setSystemHealth(health);
      }
    } catch (err) {
      console.error('Failed to check system health:', err);
    }
  };

  const loadToolSchemas = async (toolName: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/physical-tools/${toolName}/schemas`);
      if (response.ok) {
        const schemas = await response.json();
        setToolSchemas(schemas);
      }
    } catch (err) {
      console.error('Failed to load tool schemas:', err);
    }
  };

  const generateExampleConfig = async (toolName: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/physical-tools/${toolName}/example-config`);
      if (response.ok) {
        const data = await response.json();
        if (data.example_config) {
          setToolConfig(data.example_config);
          setConfigText(JSON.stringify(data.example_config, null, 2));
        }
      }
    } catch (err) {
      console.error('Failed to generate example config:', err);
    }
  };

  const initializeTool = async () => {
    if (!selectedTool) return;

    try {
      setInitializing(true);
      setError(null);

      // Parse config from text
      let config;
      try {
        config = JSON.parse(configText);
      } catch (err) {
        throw new Error('Invalid JSON in configuration');
      }

      const response = await fetch(`${API_BASE_URL}/api/physical-tools/${selectedTool.name}/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        setInitialized(true);
        setToolConfig(config);
        addTestResult({
          status: 'success',
          tool_name: selectedTool.name,
          operation: 'initialize',
          result: result,
          timestamp: new Date().toISOString()
        });
      } else {
        throw new Error(result.error || 'Initialization failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Initialization failed');
      addTestResult({
        status: 'error',
        tool_name: selectedTool?.name,
        operation: 'initialize',
        error: err instanceof Error ? err.message : 'Unknown error',
        timestamp: new Date().toISOString()
      });
    } finally {
      setInitializing(false);
    }
  };

  const executeOperation = async () => {
    if (!selectedTool || !selectedOperation) return;

    try {
      setExecuting(true);
      setError(null);

      // Parse parameters from text
      let parameters;
      try {
        parameters = JSON.parse(parametersText);
      } catch (err) {
        throw new Error('Invalid JSON in parameters');
      }

      const startTime = Date.now();
      const executionId = `exec_${Date.now()}`;

      // Add to executions list
      const newExecution: ToolExecution = {
        id: executionId,
        tool_name: selectedTool.name,
        operation: selectedOperation,
        parameters,
        status: 'running',
        start_time: new Date().toISOString()
      };
      setExecutions(prev => [newExecution, ...prev]);

      const response = await fetch(
        `${API_BASE_URL}/api/physical-tools/${selectedTool.name}/execute/${selectedOperation}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(parameters)
        }
      );

      const result = await response.json();
      const executionTime = Date.now() - startTime;
      const endTime = new Date().toISOString();

      // Update execution
      setExecutions(prev => prev.map(exec => 
        exec.id === executionId 
          ? {
              ...exec,
              status: response.ok && result.status === 'success' ? 'completed' : 'failed',
              result: result.result,
              error: result.error,
              end_time: endTime,
              execution_time: executionTime
            }
          : exec
      ));

      // Add to test results
      if (response.ok && result.status === 'success') {
        addTestResult({
          status: 'success',
          tool_name: selectedTool.name,
          operation: selectedOperation,
          result: result.result,
          execution_time: executionTime,
          timestamp: endTime
        });
      } else {
        throw new Error(result.error || 'Execution failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      
      // Update failed execution
      setExecutions(prev => prev.map(exec => 
        exec.id === `exec_${Date.now()}` 
          ? {
              ...exec,
              status: 'failed',
              error: errorMessage,
              end_time: new Date().toISOString()
            }
          : exec
      ));

      addTestResult({
        status: 'error',
        tool_name: selectedTool?.name,
        operation: selectedOperation,
        error: errorMessage,
        timestamp: new Date().toISOString()
      });
    } finally {
      setExecuting(false);
    }
  };

  const runQuickTest = async () => {
    if (!selectedTool) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/physical-tools/${selectedTool.name}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(toolConfig)
      });

      const result = await response.json();

      if (response.ok) {
        addTestResult({
          status: 'success',
          tool_name: selectedTool.name,
          operation: 'quick_test',
          result: result,
          timestamp: new Date().toISOString()
        });
      } else {
        throw new Error(result.error || 'Quick test failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Quick test failed');
      addTestResult({
        status: 'error',
        tool_name: selectedTool?.name,
        operation: 'quick_test',
        error: err instanceof Error ? err.message : 'Unknown error',
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const cleanupTool = async () => {
    if (!selectedTool) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/physical-tools/${selectedTool.name}/cleanup`, {
        method: 'DELETE'
      });

      const result = await response.json();

      if (response.ok) {
        setInitialized(false);
        addTestResult({
          status: 'success',
          tool_name: selectedTool.name,
          operation: 'cleanup',
          result: result,
          timestamp: new Date().toISOString()
        });
      }
    } catch (err) {
      console.error('Failed to cleanup tool:', err);
    }
  };

  const addTestResult = (result: TestResult) => {
    setTestResults(prev => [result, ...prev.slice(0, 49)]); // Keep last 50 results
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const exportResults = () => {
    const data = {
      tool: selectedTool?.name,
      timestamp: new Date().toISOString(),
      results: testResults,
      executions: executions
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tool-test-results-${selectedTool?.name}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'rag':
        return <Eye className="h-4 w-4" />;
      case 'sql_agent':
        return <Code className="h-4 w-4" />;
      case 'web_scraper':
        return <Monitor className="h-4 w-4" />;
      case 'api_integration':
        return <Zap className="h-4 w-4" />;
      default:
        return <Settings className="h-4 w-4" />;
    }
  };

  if (loading && availableTools.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading physical tools...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Physical Tool Tester
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Test and validate physical tool implementations
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={checkSystemHealth}>
            <Monitor className="h-4 w-4 mr-2" />
            Health Check
          </Button>
          <Button variant="outline" onClick={loadAvailableTools}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Tools
          </Button>
          {testResults.length > 0 && (
            <Button variant="outline" onClick={exportResults}>
              <Download className="h-4 w-4 mr-2" />
              Export Results
            </Button>
          )}
        </div>
      </div>

      {/* System Health Status */}
      {systemHealth && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Monitor className="h-5 w-5" />
              <span>System Health</span>
              <Badge variant={systemHealth.status === 'healthy' ? 'default' : 'destructive'}>
                {systemHealth.status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Discovered Tools:</span>
                <div className="font-semibold">{systemHealth.discovered_tools_count}</div>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Active Tools:</span>
                <div className="font-semibold">{systemHealth.active_tools_count}</div>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Categories:</span>
                <div className="font-semibold">{systemHealth.available_categories?.length || 0}</div>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Status:</span>
                <div className="font-semibold text-green-600">{systemHealth.status}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50 dark:bg-red-900/20">
          <CardContent className="pt-4">
            <div className="flex items-center space-x-2">
              <XCircle className="h-5 w-5 text-red-600" />
              <span className="text-red-800 dark:text-red-200">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tool Selection */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Available Tools</h2>
          <div className="space-y-2">
            {availableTools.map((tool) => (
              <Card
                key={tool.name}
                className={`cursor-pointer transition-colors ${
                  selectedTool?.name === tool.name 
                    ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => {
                  setSelectedTool(tool);
                  setInitialized(false);
                  setSelectedOperation('');
                }}
              >
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    {getCategoryIcon(tool.category)}
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {tool.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {tool.category} • {tool.methods.length} operations
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {tool.description}
                      </div>
                    </div>
                    <Badge variant="outline">v{tool.version}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Tool Configuration and Testing */}
        <div className="lg:col-span-2">
          {selectedTool ? (
            <Tabs defaultValue="configure" className="space-y-4">
              <TabsList>
                <TabsTrigger value="configure">Configure</TabsTrigger>
                <TabsTrigger value="execute">Execute</TabsTrigger>
                <TabsTrigger value="results">Results</TabsTrigger>
                <TabsTrigger value="schemas">Schemas</TabsTrigger>
              </TabsList>

              <TabsContent value="configure" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Tool Configuration</CardTitle>
                    <CardDescription>
                      Configure {selectedTool.name} before testing
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="config">Configuration JSON</Label>
                      <Textarea
                        id="config"
                        value={configText}
                        onChange={(e) => setConfigText(e.target.value)}
                        rows={8}
                        className="font-mono text-sm"
                        placeholder="Enter tool configuration as JSON..."
                      />
                    </div>
                    <div className="flex space-x-2">
                      <Button 
                        onClick={initializeTool}
                        disabled={initializing || !configText.trim()}
                        className="flex-1"
                      >
                        {initializing ? (
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <Play className="h-4 w-4 mr-2" />
                        )}
                        Initialize Tool
                      </Button>
                      <Button
                        variant="outline"
                        onClick={runQuickTest}
                        disabled={loading}
                      >
                        <Zap className="h-4 w-4 mr-2" />
                        Quick Test
                      </Button>
                      {initialized && (
                        <Button
                          variant="destructive"
                          onClick={cleanupTool}
                        >
                          <Square className="h-4 w-4 mr-2" />
                          Cleanup
                        </Button>
                      )}
                    </div>
                    {initialized && (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-sm">Tool initialized successfully</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="execute" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Execute Operations</CardTitle>
                    <CardDescription>
                      Run specific operations on the initialized tool
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="operation">Operation</Label>
                      <select
                        id="operation"
                        value={selectedOperation}
                        onChange={(e) => setSelectedOperation(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        disabled={!initialized}
                      >
                        <option value="">Select an operation...</option>
                        {selectedTool.methods.map((method) => (
                          <option key={method} value={method}>
                            {method}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label htmlFor="parameters">Parameters JSON</Label>
                      <Textarea
                        id="parameters"
                        value={parametersText}
                        onChange={(e) => setParametersText(e.target.value)}
                        rows={6}
                        className="font-mono text-sm"
                        placeholder="Enter operation parameters as JSON..."
                        disabled={!initialized}
                      />
                    </div>
                    <Button
                      onClick={executeOperation}
                      disabled={!initialized || !selectedOperation || executing}
                      className="w-full"
                    >
                      {executing ? (
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4 mr-2" />
                      )}
                      Execute Operation
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="results" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Execution Results</CardTitle>
                    <CardDescription>
                      Recent test results and executions
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {testResults.length === 0 ? (
                        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                          No test results yet. Run some operations to see results here.
                        </p>
                      ) : (
                        testResults.map((result, index) => (
                          <div
                            key={index}
                            className="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                {getStatusIcon(result.status)}
                                <span className="font-medium">
                                  {result.operation}
                                </span>
                                {result.execution_time && (
                                  <Badge variant="outline">
                                    <Clock className="h-3 w-3 mr-1" />
                                    {result.execution_time}ms
                                  </Badge>
                                )}
                              </div>
                              <span className="text-xs text-gray-500">
                                {new Date(result.timestamp!).toLocaleTimeString()}
                              </span>
                            </div>
                            {result.error ? (
                              <div className="text-red-600 dark:text-red-400 text-sm">
                                {result.error}
                              </div>
                            ) : result.result ? (
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm text-gray-600 dark:text-gray-400">Result:</span>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => copyToClipboard(JSON.stringify(result.result, null, 2))}
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                </div>
                                <pre className="bg-gray-50 dark:bg-gray-800 p-2 rounded text-xs overflow-x-auto">
                                  {JSON.stringify(result.result, null, 2)}
                                </pre>
                              </div>
                            ) : null}
                          </div>
                        ))
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="schemas" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Tool Schemas</CardTitle>
                    <CardDescription>
                      Configuration, input, and output schemas for {selectedTool.name}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {toolSchemas ? (
                      <Tabs defaultValue="config" className="space-y-4">
                        <TabsList>
                          <TabsTrigger value="config">Config Schema</TabsTrigger>
                          <TabsTrigger value="input">Input Schema</TabsTrigger>
                          <TabsTrigger value="output">Output Schema</TabsTrigger>
                        </TabsList>
                        <TabsContent value="config">
                          <pre className="bg-gray-50 dark:bg-gray-800 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(toolSchemas.config_schema, null, 2)}
                          </pre>
                        </TabsContent>
                        <TabsContent value="input">
                          <pre className="bg-gray-50 dark:bg-gray-800 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(toolSchemas.input_schema, null, 2)}
                          </pre>
                        </TabsContent>
                        <TabsContent value="output">
                          <pre className="bg-gray-50 dark:bg-gray-800 p-4 rounded text-xs overflow-x-auto">
                            {JSON.stringify(toolSchemas.output_schema, null, 2)}
                          </pre>
                        </TabsContent>
                      </Tabs>
                    ) : (
                      <p className="text-gray-500 dark:text-gray-400">
                        Loading schemas...
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Settings className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    Select a Tool to Test
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Choose a physical tool from the list to start testing
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
