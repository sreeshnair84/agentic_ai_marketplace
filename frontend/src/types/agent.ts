export type Framework = 'langchain' | 'llamaindex' | 'crewai' | 'semantic-kernel';

export type AgentStatus = 'active' | 'inactive' | 'error' | 'draft';

export type ExecutionStatus = 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Agent {
  id: string;
  name: string;
  description: string;
  framework: Framework;
  skills: string[];
  config: AgentConfig;
  status: AgentStatus;
  version: string;
  createdAt: Date;
  updatedAt: Date;
  lastExecutedAt?: Date;
  executionCount: number;
  systemPrompt?: string;
  tags: string[];
}

export interface AgentConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  tools: string[];
  memory: boolean;
  streaming: boolean;
  timeout: number;
  retryAttempts: number;
  [key: string]: unknown;
}

export interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  framework: Framework;
  category: string;
  skills: string[];
  defaultConfig: AgentConfig;
  isPublic: boolean;
  icon?: string;
  tags: string[];
  usageCount: number;
  rating: number;
  createdBy: string;
  createdAt: Date;
}

export interface AgentExecution {
  id: string;
  agentId: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: ExecutionStatus;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  traceId: string;
  error?: string;
  metadata: Record<string, unknown>;
}

export interface AgentMetrics {
  agentId: string;
  totalExecutions: number;
  successfulExecutions: number;
  failedExecutions: number;
  averageResponseTime: number;
  lastExecutionTime?: Date;
  uptime: number;
  errorRate: number;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  category: string;
  parameters: SkillParameter[];
  framework: Framework[];
  complexity: 'beginner' | 'intermediate' | 'advanced';
  isBuiltIn: boolean;
}

export interface SkillParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  description: string;
  default?: unknown;
  enum?: string[];
  validation?: string;
}

export interface AgentFormData {
  name: string;
  description: string;
  framework: Framework;
  skills: string[];
  systemPrompt: string;
  config: AgentConfig;
  tags: string[];
}

export interface AgentFilters {
  framework?: Framework;
  status?: AgentStatus;
  skills?: string[];
  tags?: string[];
  search?: string;
  sortBy?: 'name' | 'createdAt' | 'updatedAt' | 'executionCount';
  sortOrder?: 'asc' | 'desc';
}
