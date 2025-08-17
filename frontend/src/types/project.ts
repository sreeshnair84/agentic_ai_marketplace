export interface Project {
  id: string;
  name: string;
  description: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  isDefault?: boolean;
  color?: string;
  status: 'active' | 'inactive' | 'archived';
  memberCount?: number;
}

export interface ProjectFilters {
  status?: string;
  search?: string;
  tags?: string[];
  sortBy?: 'name' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}

export interface ProjectFormData {
  name: string;
  description: string;
  tags: string[];
  color?: string;
}

// Enhanced types for agents, tools, and workflows with project tags
export interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  version: string;
  status: 'active' | 'inactive' | 'deprecated';
  config: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  usageCount: number;
  isBuiltIn: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  tags: string[];
  status: 'active' | 'inactive' | 'draft';
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  version: string;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  executionCount: number;
  lastExecutedAt?: Date;
}

export interface WorkflowNode {
  id: string;
  type: 'agent' | 'tool' | 'condition' | 'start' | 'end';
  data: {
    label: string;
    agentId?: string;
    toolId?: string;
    config?: Record<string, any>;
  };
  position: { x: number; y: number };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  condition?: string;
}

// Project context for filtering
export interface ProjectContext {
  selectedProject: Project | null;
  projects: Project[];
  isLoading: boolean;
  error: string | null;
}

export interface ProjectFilteredData {
  agents: any[];
  tools: Tool[];
  workflows: Workflow[];
}
