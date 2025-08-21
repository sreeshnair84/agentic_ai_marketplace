'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { StandardSection } from '@/components/layout/StandardPageLayout';
import { 
  PlayIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  BeakerIcon,
  CodeBracketIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';

interface MCPToolTesterProps {
  servers: any[];
  endpoints: any[];
  tools: any[];
  onTestTool: (toolId: string, parameters: any) => Promise<any>;
  onExecuteEndpoint: (endpointName: string, parameters: any) => Promise<any>;
}

export default function MCPToolTester({ 
  servers, 
  endpoints, 
  tools, 
  onTestTool, 
  onExecuteEndpoint 
}: MCPToolTesterProps) {
  const [selectedType, setSelectedType] = useState<'tool' | 'endpoint'>('tool');
  const [selectedId, setSelectedId] = useState('');
  const [parameters, setParameters] = useState('{}');
  const [parametersError, setParametersError] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [testing, setTesting] = useState(false);
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());

  const selectedItem = selectedType === 'tool' 
    ? tools.find(t => t.id === selectedId)
    : endpoints.find(e => e.id === selectedId);

  const availableItems = selectedType === 'tool' ? tools : endpoints;

  useEffect(() => {
    setSelectedId('');
  }, [selectedType]);

  useEffect(() => {
    if (selectedItem?.schema) {
      // Auto-generate parameter template from schema
      try {
        const schema = selectedItem.schema;
        if (schema.properties) {
          const template: any = {};
          Object.entries(schema.properties).forEach(([key, prop]: [string, any]) => {
            if (prop.type === 'string') {
              template[key] = prop.default || '';
            } else if (prop.type === 'number' || prop.type === 'integer') {
              template[key] = prop.default || 0;
            } else if (prop.type === 'boolean') {
              template[key] = prop.default || false;
            } else if (prop.type === 'array') {
              template[key] = prop.default || [];
            } else if (prop.type === 'object') {
              template[key] = prop.default || {};
            }
          });
          setParameters(JSON.stringify(template, null, 2));
        }
      } catch (err) {
        console.error('Error generating parameter template:', err);
      }
    }
  }, [selectedItem]);

  const handleParametersChange = (value: string) => {
    setParameters(value);
    try {
      JSON.parse(value);
      setParametersError('');
    } catch (err) {
      setParametersError('Invalid JSON format');
    }
  };

  const handleTest = async () => {
    if (!selectedId || parametersError) return;

    setTesting(true);
    const startTime = Date.now();

    try {
      const parsedParameters = JSON.parse(parameters);
      let result;

      if (selectedType === 'tool') {
        result = await onTestTool(selectedId, parsedParameters);
      } else {
        const endpoint = endpoints.find(e => e.id === selectedId);
        result = await onExecuteEndpoint(endpoint.endpoint_name, parsedParameters);
      }

      const executionTime = Date.now() - startTime;

      const testResult = {
        id: Date.now(),
        type: selectedType,
        item: selectedItem,
        parameters: parsedParameters,
        result,
        executionTime,
        status: 'success',
        timestamp: new Date()
      };

      setResults(prev => [testResult, ...prev]);
    } catch (error: any) {
      const executionTime = Date.now() - startTime;

      const testResult = {
        id: Date.now(),
        type: selectedType,
        item: selectedItem,
        parameters: JSON.parse(parameters),
        error: error.message || 'Unknown error',
        executionTime,
        status: 'error',
        timestamp: new Date()
      };

      setResults(prev => [testResult, ...prev]);
    } finally {
      setTesting(false);
    }
  };

  const toggleResultExpansion = (resultId: number) => {
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(resultId)) {
        newSet.delete(resultId);
      } else {
        newSet.add(resultId);
      }
      return newSet;
    });
  };

  const clearResults = () => {
    setResults([]);
    setExpandedResults(new Set());
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 dark:text-green-400';
      case 'error':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'error':
        return <XCircleIcon className="h-4 w-4" />;
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Test Configuration */}
      <StandardSection>
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <BeakerIcon className="h-6 w-6 text-purple-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              MCP Tool Tester
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              {/* Type Selection */}
              <div>
                <Label>Test Type</Label>
                <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mt-1">
                  <button
                    onClick={() => setSelectedType('tool')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      selectedType === 'tool'
                        ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    Test Tool
                  </button>
                  <button
                    onClick={() => setSelectedType('endpoint')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      selectedType === 'endpoint'
                        ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }`}
                  >
                    Test Endpoint
                  </button>
                </div>
              </div>

              {/* Item Selection */}
              <div>
                <Label htmlFor="item-select">
                  Select {selectedType === 'tool' ? 'Tool' : 'Endpoint'}
                </Label>
                <select
                  id="item-select"
                  value={selectedId}
                  onChange={(e) => setSelectedId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white mt-1"
                >
                  <option value="">Select {selectedType}...</option>
                  {availableItems.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.display_name || item.tool_name || item.endpoint_name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Selected Item Info */}
              {selectedItem && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <CodeBracketIcon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                    <span className="font-medium text-gray-900 dark:text-white">
                      {selectedItem.display_name || selectedItem.tool_name || selectedItem.endpoint_name}
                    </span>
                  </div>
                  {selectedItem.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {selectedItem.description}
                    </p>
                  )}
                  {selectedItem.version && (
                    <Badge variant="outline" className="text-xs">
                      v{selectedItem.version}
                    </Badge>
                  )}
                </div>
              )}

              {/* Test Button */}
              <Button
                onClick={handleTest}
                disabled={!selectedId || testing || !!parametersError}
                className="w-full"
              >
                {testing ? (
                  <>
                    <ClockIcon className="h-4 w-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-4 w-4 mr-2" />
                    Run Test
                  </>
                )}
              </Button>
            </div>

            <div className="space-y-4">
              {/* Parameters */}
              <div>
                <Label htmlFor="parameters">Parameters (JSON)</Label>
                <textarea
                  id="parameters"
                  value={parameters}
                  onChange={(e) => handleParametersChange(e.target.value)}
                  placeholder='{"param1": "value1", "param2": "value2"}'
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm resize-vertical min-h-[200px] mt-1"
                />
                {parametersError && (
                  <p className="text-red-600 dark:text-red-400 text-sm mt-1">
                    {parametersError}
                  </p>
                )}
              </div>

              {/* Schema Preview */}
              {selectedItem?.schema && (
                <div>
                  <Label>Expected Schema</Label>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mt-1">
                    <pre className="text-xs text-gray-600 dark:text-gray-400 font-mono overflow-x-auto">
                      {JSON.stringify(selectedItem.schema, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </StandardSection>

      {/* Test Results */}
      <StandardSection>
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Test Results ({results.length})
            </h3>
            {results.length > 0 && (
              <Button variant="outline" size="sm" onClick={clearResults}>
                Clear Results
              </Button>
            )}
          </div>

          {results.length === 0 ? (
            <div className="text-center py-12">
              <BeakerIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No test results yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Run a test to see results here.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`flex items-center space-x-2 ${getStatusColor(result.status)}`}>
                        {getStatusIcon(result.status)}
                        <span className="font-medium">
                          {result.item.display_name || result.item.tool_name || result.item.endpoint_name}
                        </span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {result.type}
                      </Badge>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {result.executionTime}ms
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {result.timestamp.toLocaleTimeString()}
                      </span>
                      <button
                        onClick={() => toggleResultExpansion(result.id)}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        {expandedResults.has(result.id) ? (
                          <ChevronDownIcon className="h-4 w-4" />
                        ) : (
                          <ChevronRightIcon className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {result.status === 'success' && (
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      ✅ Test completed successfully
                    </div>
                  )}

                  {result.status === 'error' && (
                    <div className="text-sm text-red-600 dark:text-red-400 mb-2">
                      ❌ Error: {result.error}
                    </div>
                  )}

                  {expandedResults.has(result.id) && (
                    <div className="space-y-3 mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                      {/* Input Parameters */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                          Input Parameters:
                        </h4>
                        <div className="bg-gray-50 dark:bg-gray-700 rounded p-3">
                          <pre className="text-xs text-gray-600 dark:text-gray-400 font-mono overflow-x-auto">
                            {JSON.stringify(result.parameters, null, 2)}
                          </pre>
                        </div>
                      </div>

                      {/* Output Result */}
                      {result.result && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                            Output Result:
                          </h4>
                          <div className="bg-gray-50 dark:bg-gray-700 rounded p-3">
                            <pre className="text-xs text-gray-600 dark:text-gray-400 font-mono overflow-x-auto">
                              {JSON.stringify(result.result, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </StandardSection>
    </div>
  );
}
