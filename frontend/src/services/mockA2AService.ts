// Mock A2A Response Service for testing and development
export interface MockA2AAgent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  responseDelay: number; // ms
  thinkingSteps: string[];
  preferredTools: string[];
}

export const mockAgents: MockA2AAgent[] = [
  {
    id: 'classifier-agent',
    name: 'Classifier Agent',
    description: 'Classifies user intents and routes to appropriate specialists',
    capabilities: ['intent_classification', 'routing', 'context_analysis'],
    responseDelay: 500,
    thinkingSteps: [
      'Analyzing user message for intent patterns',
      'Checking context clues and keywords',
      'Evaluating confidence scores for each category',
      'Selecting most appropriate routing destination'
    ],
    preferredTools: ['intent_classifier', 'context_analyzer']
  },
  {
    id: 'research-agent',
    name: 'Research Agent',
    description: 'Conducts comprehensive research and data analysis',
    capabilities: ['web_search', 'data_analysis', 'report_generation'],
    responseDelay: 1200,
    thinkingSteps: [
      'Breaking down research question into components',
      'Identifying reliable sources and databases',
      'Gathering and cross-referencing information',
      'Synthesizing findings into coherent response'
    ],
    preferredTools: ['web_search', 'data_analyzer', 'citation_formatter']
  },
  {
    id: 'technical-agent',
    name: 'Technical Agent',
    description: 'Handles technical queries and provides coding assistance',
    capabilities: ['code_analysis', 'debugging', 'architecture_review'],
    responseDelay: 800,
    thinkingSteps: [
      'Analyzing technical requirements',
      'Reviewing code patterns and best practices',
      'Identifying potential issues or improvements',
      'Formulating technical recommendations'
    ],
    preferredTools: ['code_analyzer', 'debugger', 'documentation_search']
  },
  {
    id: 'creative-agent',
    name: 'Creative Agent',
    description: 'Generates creative content and assists with ideation',
    capabilities: ['content_generation', 'brainstorming', 'creative_writing'],
    responseDelay: 600,
    thinkingSteps: [
      'Understanding creative requirements and constraints',
      'Exploring different creative approaches',
      'Generating multiple concept variations',
      'Refining and selecting best creative direction'
    ],
    preferredTools: ['content_generator', 'image_creator', 'style_analyzer']
  }
];

export const mockCitations = [
  {
    id: 'cite1',
    source: 'Technical Documentation',
    title: 'A2A Protocol Specification v2.1',
    url: 'https://docs.a2a-protocol.org/spec/v2.1',
    excerpt: 'The A2A protocol enables seamless communication between autonomous agents...',
    confidence: 0.95,
    relevance_score: 0.92
  },
  {
    id: 'cite2',
    source: 'Research Paper',
    title: 'Multi-Agent Systems in Enterprise Applications',
    url: 'https://research.example.com/mas-enterprise',
    excerpt: 'Enterprise multi-agent systems demonstrate significant improvements in workflow automation...',
    confidence: 0.88,
    relevance_score: 0.85
  }
];

export const mockToolCalls = [
  {
    id: 'tool1',
    toolName: 'WebSearchTool',
    toolType: 'information_retrieval',
    input: { query: 'A2A protocol implementation patterns', max_results: 5 },
    output: { results: ['...search results...'], total_found: 127 },
    status: 'completed' as const,
    timestamp: new Date(),
    duration_ms: 1250
  },
  {
    id: 'tool2',
    toolName: 'CodeAnalyzer',
    toolType: 'analysis',
    input: { code: 'async function handleA2AMessage(...)', language: 'typescript' },
    output: { issues: [], suggestions: ['Consider adding error boundaries'], complexity_score: 3.2 },
    status: 'completed' as const,
    timestamp: new Date(),
    duration_ms: 800
  }
];

export class MockA2AService {
  private agents = mockAgents;
  private communicationLog: Array<{
    id: string;
    sourceAgent: string;
    targetAgent: string;
    message: string;
    timestamp: Date;
    latency_ms: number;
  }> = [];

  // Simulate A2A streaming response
  async *generateMockA2AResponse(
    userMessage: string, 
    sessionId: string,
    context?: any
  ): AsyncGenerator<any, void, unknown> {
    // Enhanced context-aware response generation with comprehensive events
    // Step 1: Determine context-aware routing
    let contextMessage = 'Analyzing your request...';
    let targetAgent = this.determineTargetAgent(userMessage);
    
    // Enhanced context-aware routing and messaging
    if (context?.type === 'workflow') {
      contextMessage = `🔄 Routing to workflow: ${context.workflow?.display_name || 'selected workflow'}...`;
      targetAgent = this.agents.find(a => a.id === 'research-agent') || targetAgent; // Use research agent for workflows
    } else if (context?.type === 'agent') {
      contextMessage = `🤖 Connecting to agent: ${context.agent?.display_name || 'selected agent'}...`;
      targetAgent = this.agents.find(a => a.id === 'technical-agent') || targetAgent; // Use technical agent for agents
    } else if (context?.type === 'tools') {
      const toolCount = context.tools?.length || 0;
      contextMessage = `🔧 Initializing ${toolCount} specialized tools for your request...`;
      targetAgent = this.agents.find(a => a.id === 'technical-agent') || targetAgent; // Use technical agent for tools
    } else if (context?.type === 'llm') {
      const modelName = context.llm_model?.display_name || 'selected LLM';
      contextMessage = `⚡ Connecting directly to ${modelName} model...`;
      targetAgent = this.agents.find(a => a.id === 'research-agent') || targetAgent; // Use research agent for direct LLM
    }
    
    const routingAgent = this.agents.find(a => a.id === 'classifier-agent')!;
    
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'task_status_update',
        task_id: `task_${Date.now()}`,
        status: {
          type: 'in_progress',
          message: {
            role: 'assistant',
            parts: [{ type: 'text', text: contextMessage }]
          }
        }
      }
    };

    // Simulate routing delay
    await this.delay(routingAgent.responseDelay);

    // Log agent communication
    this.logCommunication('system', targetAgent.id, `Routing to ${targetAgent.name} based on context: ${context?.type || 'auto'}`);

    // Step 2: Session initialization event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'session_start',
        session_id: sessionId,
        context_type: context?.type || 'default',
        target_agent: targetAgent.name,
        timestamp: new Date().toISOString(),
        routing_info: {
          type: context?.type || 'auto',
          target: targetAgent.name,
          dns_name: context?.workflow?.dns_name || context?.agent?.a2a_address,
          selected_tools: context?.tools?.map((t: any) => t.name) || [],
          llm_model: context?.llm_model?.name
        }
      }
    };

    // Step 3: Agent communication event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'agent_communication',
        source_agent: routingAgent.name,
        target_agent: targetAgent.name,
        message: `Routing ${this.classifyIntent(userMessage)} query to ${targetAgent.name}`,
        status: 'processed',
        latency_ms: 150,
        message_type: 'request'
      }
    };

    // Step 4: Model loading event (for LLM context)
    if (context?.type === 'llm') {
      yield {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        result: {
          type: 'model_loading',
          model_id: context.llm_model?.id,
          model_name: context.llm_model?.name,
          provider: context.llm_model?.provider,
          status: 'loading',
          estimated_load_time_ms: 2000
        }
      };

      await this.delay(1000);

      yield {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        result: {
          type: 'model_loading',
          model_id: context.llm_model?.id,
          model_name: context.llm_model?.name,
          provider: context.llm_model?.provider,
          status: 'ready',
          load_time_ms: 1000
        }
      };
    }

    // Step 5: Security validation event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'security_check',
        session_id: sessionId,
        checks: {
          message_safety: 'passed',
          user_authorization: 'passed',
          content_filtering: 'passed',
          rate_limiting: 'within_limits'
        },
        risk_score: 0.1,
        timestamp: new Date().toISOString()
      }
    };

    // Step 6: Target agent processes the request
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'task_status_update',
        task_id: `task_${Date.now()}`,
        status: {
          type: 'in_progress',
          message: {
            role: 'assistant',
            parts: [{ type: 'text', text: `${targetAgent.name} is processing your request...` }]
          }
        }
      }
    };

    // Simulate thinking process
    for (const step of targetAgent.thinkingSteps) {
      await this.delay(200);
      yield {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        result: {
          type: 'thinking_update',
          agent_id: targetAgent.id,
          thinking_step: step,
          confidence_building: Math.random() * 0.3 + 0.5
        }
      };
    }

    // Step 7: Resource monitoring event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'resource_monitoring',
        metrics: {
          cpu_usage: Math.random() * 30 + 20, // 20-50%
          memory_usage: Math.random() * 40 + 30, // 30-70%
          network_latency_ms: Math.random() * 50 + 10, // 10-60ms
          active_connections: Math.floor(Math.random() * 10) + 1,
          queue_size: Math.floor(Math.random() * 5)
        },
        timestamp: new Date().toISOString(),
        agent_id: targetAgent.id
      }
    };

    // Step 8: Performance metrics event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'performance_metrics',
        metrics: {
          request_processing_time_ms: Math.random() * 1000 + 500,
          token_generation_rate: Math.random() * 50 + 25, // tokens/sec
          throughput_requests_per_minute: Math.random() * 100 + 50,
          error_rate_percent: Math.random() * 2, // 0-2%
          cache_hit_rate: Math.random() * 30 + 70 // 70-100%
        },
        context_type: context?.type || 'default',
        timestamp: new Date().toISOString()
      }
    };

    // Step 9: Tool usage simulation
    if (targetAgent.preferredTools.length > 0) {
      const tool = targetAgent.preferredTools[0];
      
      yield {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        result: {
          type: 'tool_call',
          tool_name: tool,
          status: 'pending',
          input: this.generateMockToolInput(tool, userMessage)
        }
      };

      await this.delay(800);

      yield {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        result: {
          type: 'tool_call',
          tool_name: tool,
          status: 'completed',
          output: this.generateMockToolOutput(tool),
          duration_ms: 800
        }
      };
    }

    // Step 5: Generate response chunks
    const response = this.generateResponse(userMessage, targetAgent);
    const chunks = this.chunkResponse(response);

    for (const chunk of chunks) {
      await this.delay(100);
      yield {
        jsonrpc: '2.0',
        id: `task_${Date.now()}`,
        result: {
          type: 'task_status_update',
          task_id: `task_${Date.now()}`,
          status: {
            type: 'in_progress',
            message: {
              role: 'assistant',
              parts: [{ type: 'text', text: chunk }]
            }
          }
        }
      };
    }

    // Step 10: Quality assurance event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'quality_assurance',
        checks: {
          response_completeness: 'passed',
          factual_accuracy: 'verified',
          context_relevance: 'high',
          tone_appropriateness: 'passed',
          safety_compliance: 'passed'
        },
        quality_score: 0.92,
        confidence_level: 'high',
        timestamp: new Date().toISOString()
      }
    };

    // Step 11: Final completion with metadata
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'task_status_update',
        task_id: `task_${Date.now()}`,
        status: {
          type: 'completed',
          message: {
            role: 'assistant',
            parts: [{ type: 'text', text: 'Task completed successfully' }]
          },
          result: {
            response_type: 'text',
            content: response,
            agent_name: targetAgent.name,
            ai_provider: 'mock',
            citations: mockCitations,
            tool_calls: mockToolCalls,
            scratchpad: {
              id: `scratch_${Date.now()}`,
              agentId: targetAgent.id,
              thinking: targetAgent.thinkingSteps,
              reasoning: `Applied ${targetAgent.capabilities.join(', ')} to analyze and respond to the user's ${this.classifyIntent(userMessage)} query using ${context?.type || 'default'} context.`,
              confidence_score: 0.87,
              alternative_approaches: [
                'Could have consulted additional data sources',
                'Alternative routing through specialist sub-agents',
                'Parallel processing across multiple agent teams'
              ],
              decision_factors: [
                'Query complexity and scope',
                'Available agent capabilities',
                'Response time requirements',
                'User context and preferences',
                'Selected context type: ' + (context?.type || 'auto-detected')
              ]
            }
          }
        }
      }
    };

    // Step 12: Session completion event
    yield {
      jsonrpc: '2.0',
      id: `task_${Date.now()}`,
      result: {
        type: 'session_end',
        session_id: sessionId,
        context_type: context?.type || 'default',
        total_duration_ms: Date.now() % 5000 + 2000, // 2-7 seconds
        events_generated: 12,
        success: true,
        final_agent: targetAgent.name,
        timestamp: new Date().toISOString()
      }
    };
  }

  private determineTargetAgent(message: string): MockA2AAgent {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('code') || lowerMessage.includes('technical') || lowerMessage.includes('debug')) {
      return this.agents.find(a => a.id === 'technical-agent')!;
    } else if (lowerMessage.includes('research') || lowerMessage.includes('analyze') || lowerMessage.includes('data')) {
      return this.agents.find(a => a.id === 'research-agent')!;
    } else if (lowerMessage.includes('create') || lowerMessage.includes('write') || lowerMessage.includes('content')) {
      return this.agents.find(a => a.id === 'creative-agent')!;
    } else {
      return this.agents.find(a => a.id === 'research-agent')!; // Default
    }
  }

  private classifyIntent(message: string): string {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('how') || lowerMessage.includes('what') || lowerMessage.includes('explain')) {
      return 'informational';
    } else if (lowerMessage.includes('help') || lowerMessage.includes('solve') || lowerMessage.includes('fix')) {
      return 'support';
    } else if (lowerMessage.includes('create') || lowerMessage.includes('make') || lowerMessage.includes('build')) {
      return 'creative';
    } else {
      return 'general';
    }
  }

  private generateResponse(message: string, agent: MockA2AAgent): string {
    const responses: Record<string, string> = {
      'classifier-agent': `I've analyzed your request and routed it to the appropriate specialist agent.`,
      'research-agent': `Based on my research and analysis, I can provide you with comprehensive information about your query. I've gathered data from multiple reliable sources and cross-referenced the findings to ensure accuracy.`,
      'technical-agent': `I've reviewed the technical aspects of your request. Here's my analysis and recommendations based on current best practices and industry standards.`,
      'creative-agent': `I've explored several creative approaches to address your request. Here's an innovative solution that balances creativity with practical implementation.`
    };

    const baseResponse = responses[agent.id] || responses['research-agent'];
    
    return `${baseResponse}

Regarding your query: "${message}"

I've applied my specialized capabilities in ${agent.capabilities.join(', ')} to provide you with the most relevant and helpful response. The analysis involved multiple processing steps and tool usage to ensure comprehensive coverage of your request.

This response incorporates real-time data analysis, contextual understanding, and domain-specific expertise to deliver actionable insights tailored to your specific needs.`;
  }

  private chunkResponse(response: string): string[] {
    const sentences = response.split('. ');
    const chunks: string[] = [];
    let currentChunk = '';

    for (const sentence of sentences) {
      if (currentChunk.length + sentence.length > 50) {
        if (currentChunk) {
          chunks.push(currentChunk.trim() + '.');
          currentChunk = sentence;
        } else {
          chunks.push(sentence + '.');
        }
      } else {
        currentChunk += (currentChunk ? '. ' : '') + sentence;
      }
    }

    if (currentChunk) {
      chunks.push(currentChunk + (currentChunk.endsWith('.') ? '' : '.'));
    }

    return chunks;
  }

  private generateMockToolInput(toolName: string, userMessage: string): any {
    const inputs: Record<string, any> = {
      'web_search': { query: `research query based on: ${userMessage}`, max_results: 10 },
      'code_analyzer': { code: 'function example() { return "analyzing"; }', language: 'javascript' },
      'data_analyzer': { dataset: 'user_query_patterns', analysis_type: 'sentiment' },
      'intent_classifier': { text: userMessage, confidence_threshold: 0.8 },
      'content_generator': { prompt: userMessage, style: 'professional', length: 'medium' }
    };

    return inputs[toolName] || inputs['web_search'];
  }

  private generateMockToolOutput(toolName: string): any {
    const outputs: Record<string, any> = {
      'web_search': { 
        results: [
          { title: 'Relevant Article 1', url: 'https://example.com/1', snippet: 'Detailed information...' },
          { title: 'Research Paper', url: 'https://example.com/2', snippet: 'Academic insights...' }
        ],
        total_found: 15,
        search_time_ms: 450
      },
      'code_analyzer': {
        complexity_score: 2.3,
        issues: [],
        suggestions: ['Consider adding error handling', 'Optimize performance'],
        metrics: { lines: 25, functions: 3, complexity: 'low' }
      },
      'data_analyzer': {
        insights: ['Pattern detected in user queries', 'Sentiment mostly positive'],
        confidence: 0.91,
        data_points: 1547
      }
    };

    return outputs[toolName] || outputs['web_search'];
  }

  private logCommunication(source: string, target: string, message: string) {
    this.communicationLog.push({
      id: `comm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      sourceAgent: source,
      targetAgent: target,
      message,
      timestamp: new Date(),
      latency_ms: Math.random() * 200 + 50
    });
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Get communication history for debugging
  getCommunicationLog() {
    return [...this.communicationLog];
  }

  // Clear communication log
  clearCommunicationLog() {
    this.communicationLog = [];
  }
}

// Singleton instance for use across the application
export const mockA2AService = new MockA2AService();
