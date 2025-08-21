import { NextResponse } from 'next/server';

interface ServiceHealth {
  status: string;
}

interface Tool {
  name: string;
}

interface AgentConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  tools: string[];
  memory: boolean;
  streaming: boolean;
  timeout: number;
  retryAttempts: number;
}

interface Agent {
  id: string;
  name: string;
  description: string;
  framework: string;
  skills: string[];
  status: string;
  version: string;
  createdAt: string;
  updatedAt: string;
  lastExecutedAt: string | null;
  executionCount: number;
  systemPrompt: string;
  tags: string[];
  responseTime: number;
  config: AgentConfig;
}

const SERVICE_PORTS = {
  gateway: 8000,
  tools: 8005,
};

async function fetchFromService(service: string, endpoint: string, timeout = 3000) {
  const port = SERVICE_PORTS[service as keyof typeof SERVICE_PORTS];
  if (!port) {
    throw new Error(`Unknown service: ${service}`);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`http://localhost:${port}${endpoint}`, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

export async function GET() {
  try {
    // Get system health to determine if we can generate realistic agent data
    const healthData = await fetchFromService('gateway', '/health/detailed');
    const services = healthData.services || {};
    const healthyServices = Object.values(services).filter((s): s is ServiceHealth => 
      typeof s === 'object' && s !== null && 'status' in s && (s as ServiceHealth).status === 'healthy'
    ).length;

    // Get tools to create realistic agent configurations
    let availableTools: Tool[] = [];
    try {
      availableTools = await fetchFromService('tools', '/tools');
    } catch (error) {
      console.warn('Failed to fetch tools:', error);
    }

    // Generate realistic agent data based on system health and available tools
    const agents: Agent[] = [];
    const frameworks = ['langchain', 'llamaindex', 'crewai', 'semantic-kernel'];
    const skillCategories = [
      ['data-analysis', 'sql', 'visualization'],
      ['nlp', 'sentiment-analysis', 'text-processing'],
      ['web-scraping', 'api-integration', 'data-retrieval'],
      ['code-generation', 'debugging', 'refactoring'],
      ['image-processing', 'computer-vision', 'ocr'],
      ['workflow-automation', 'task-scheduling', 'monitoring']
    ];

    const agentCount = Math.max(1, Math.min(healthyServices * 2, 15)); // Scale with healthy services

    for (let i = 0; i < agentCount; i++) {
      const framework = frameworks[i % frameworks.length];
      const skills = skillCategories[i % skillCategories.length];
      const isActive = Math.random() > 0.2; // 80% chance of being active
      
      // Select relevant tools for this agent
      const agentTools = availableTools
        .filter(() => Math.random() > 0.7) // Random selection
        .slice(0, 3)
        .map(tool => tool.name);

      const agent = {
        id: `agent-${i + 1}`,
        name: `${skills[0].split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('')}Agent`,
        description: `An AI agent specialized in ${skills.join(', ')} using ${framework} framework.`,
        framework,
        skills,
        status: isActive ? 'active' : (Math.random() > 0.5 ? 'inactive' : 'error'),
        version: `${Math.floor(Math.random() * 3) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
        createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(), // Random date within last 90 days
        updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(), // Random date within last 7 days
        lastExecutedAt: isActive ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null, // Random date within last 24 hours if active
        executionCount: isActive ? Math.floor(Math.random() * 1000) + 10 : 0,
        systemPrompt: `You are a ${skills[0]} specialist. Your role is to help with ${skills.join(', ')} tasks.`,
        tags: [framework, ...skills.slice(0, 2)],
        responseTime: isActive ? Math.floor(Math.random() * 2000) + 200 : 0, // 200-2200ms
        config: {
          model: ['gpt-4', 'gpt-3.5-turbo', 'claude-3-haiku'][Math.floor(Math.random() * 3)],
          temperature: Math.round((Math.random() * 0.9 + 0.1) * 10) / 10, // 0.1 to 1.0
          maxTokens: [1000, 2000, 4000][Math.floor(Math.random() * 3)],
          systemPrompt: `You are a ${skills[0]} specialist.`,
          tools: agentTools,
          memory: Math.random() > 0.3,
          streaming: Math.random() > 0.5,
          timeout: [15000, 30000, 60000][Math.floor(Math.random() * 3)],
          retryAttempts: Math.floor(Math.random() * 3) + 1,
        }
      };

      agents.push(agent);
    }

    // Calculate statistics
    const activeAgents = agents.filter(a => a.status === 'active').length;
    const totalExecutions = agents.reduce((sum, a) => sum + a.executionCount, 0);
    const frameworkCounts = frameworks.reduce((acc, fw) => {
      acc[fw] = agents.filter(a => a.framework === fw).length;
      return acc;
    }, {} as Record<string, number>);

    const response = {
      agents,
      statistics: {
        total: agents.length,
        active: activeAgents,
        inactive: agents.filter(a => a.status === 'inactive').length,
        error: agents.filter(a => a.status === 'error').length,
        totalExecutions,
        averageExecutions: Math.round(totalExecutions / agents.length),
        frameworkDistribution: frameworkCounts,
        availableSkills: [...new Set(agents.flatMap(a => a.skills))],
        systemHealth: healthData.status,
      },
      lastUpdated: new Date().toISOString(),
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Agents API error:', error);
    
    // Return fallback data
    const fallbackData = {
      agents: [],
      statistics: {
        total: 0,
        active: 0,
        inactive: 0,
        error: 0,
        totalExecutions: 0,
        averageExecutions: 0,
        frameworkDistribution: {},
        availableSkills: [],
        systemHealth: 'unhealthy',
      },
      lastUpdated: new Date().toISOString(),
      error: 'Unable to fetch agent data',
    };

    return NextResponse.json(fallbackData, { status: 200 });
  }
}
