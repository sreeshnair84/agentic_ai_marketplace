/**
 * A2A API Service
 * Handles communication with the A2A backend API endpoints
 */

export interface A2AAgent {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
}

export interface A2AAgentResponse {
  success: boolean;
  agents: A2AAgent[];
  count: number;
  timestamp: string;
}

export interface A2AChatRequest {
  message: string;
  agent_id?: string;
  session_id?: string;
  conversation_history?: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
}

export interface A2AChatResponse {
  success: boolean;
  message: string;
  task_id?: string;
  agent_id?: string;
  session_id?: string;
  timestamp: string;
  data?: {
    conversation_history?: any[];
    state?: string;
    requires_input?: boolean;
  };
}

export interface A2AStreamChatRequest {
  message: string;
  agent_id?: string;
  session_id?: string;
  conversation_history?: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
}

export interface A2ATaskStatus {
  task_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface A2AHealthStatus {
  success: boolean;
  health: {
    status: string;
    a2a_available: boolean;
    active_tasks: number;
    agent_service_status: any;
    timestamp: string;
  };
}

export interface A2AConfig {
  success: boolean;
  config: {
    system_info: {
      version: string;
      protocol: string;
      framework: string;
      capabilities: string[];
    };
    agents: A2AAgent[];
    health: any;
  };
  timestamp: string;
}

export class A2AService {
  private baseUrl: string;
  private apiVersion: string;

  constructor(baseUrl?: string, apiVersion?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.apiVersion = apiVersion || '/api/v1';
  }

  private getApiUrl(path: string): string {
    return `${this.baseUrl}${this.apiVersion}/a2a${path}`;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    return response.json();
  }

  /**
   * List all available A2A agents
   */
  async listAgents(): Promise<A2AAgentResponse> {
    const response = await fetch(this.getApiUrl('/agents'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse<A2AAgentResponse>(response);
  }

  /**
   * Get details of a specific A2A agent
   */
  async getAgent(agentId: string): Promise<{ success: boolean; agent: A2AAgent; timestamp: string }> {
    const response = await fetch(this.getApiUrl(`/agents/${agentId}`), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse(response);
  }

  /**
   * Send a non-streaming chat message to A2A agents
   */
  async sendChatMessage(request: A2AChatRequest): Promise<A2AChatResponse> {
    const response = await fetch(this.getApiUrl('/chat'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return this.handleResponse<A2AChatResponse>(response);
  }

  /**
   * Send a streaming chat message to A2A agents
   * Returns an async generator for streaming responses
   */
  async* streamChatMessage(request: A2AStreamChatRequest): AsyncGenerator<any, void, unknown> {
    const response = await fetch(this.getApiUrl('/chat/stream'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body available for streaming');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') {
              return;
            }
            if (data) {
              try {
                const parsedData = JSON.parse(data);
                
                // Handle different response formats from backend
                if (parsedData.success === false) {
                  yield { error: parsedData.error || parsedData.detail, final: true };
                  return;
                }
                
                // Handle streaming chunk with message content
                if (parsedData.chunk) {
                  yield { 
                    message: parsedData.chunk, 
                    final: parsedData.final || false,
                    streaming: parsedData.streaming || true
                  };
                } else if (parsedData.message) {
                  yield { 
                    message: parsedData.message, 
                    final: parsedData.final || false,
                    task_id: parsedData.task_id,
                    agent_id: parsedData.agent_id,
                    timestamp: parsedData.timestamp
                  };
                } else {
                  // Generic handling for any other response format
                  yield parsedData;
                }
                
                // Exit on final chunk
                if (parsedData.final === true) {
                  return;
                }
              } catch (parseError) {
                console.warn('Failed to parse streaming data:', data, parseError);
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * List all active A2A tasks
   */
  async listTasks(): Promise<{ success: boolean; tasks: A2ATaskStatus[]; count: number; timestamp: string }> {
    const response = await fetch(this.getApiUrl('/tasks'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse(response);
  }

  /**
   * Get status of a specific task
   */
  async getTaskStatus(taskId: string): Promise<{ success: boolean; task: A2ATaskStatus; timestamp: string }> {
    const response = await fetch(this.getApiUrl(`/tasks/${taskId}`), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse(response);
  }

  /**
   * Cancel a running task
   */
  async cancelTask(taskId: string): Promise<{ success: boolean; message: string; task_id: string; timestamp: string }> {
    const response = await fetch(this.getApiUrl(`/tasks/${taskId}/cancel`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse(response);
  }

  /**
   * Get health status of A2A system
   */
  async getHealthStatus(): Promise<A2AHealthStatus> {
    const response = await fetch(this.getApiUrl('/health'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse<A2AHealthStatus>(response);
  }

  /**
   * Get A2A system configuration
   */
  async getConfig(): Promise<A2AConfig> {
    const response = await fetch(this.getApiUrl('/config'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return this.handleResponse<A2AConfig>(response);
  }

  /**
   * Check if A2A backend is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      const healthStatus = await this.getHealthStatus();
      return healthStatus.success && healthStatus.health.status === 'healthy';
    } catch (error) {
      console.warn('A2A backend not available:', error);
      return false;
    }
  }
}

// Export singleton instance
export const a2aService = new A2AService();

// Export default instance for convenience
export default a2aService;