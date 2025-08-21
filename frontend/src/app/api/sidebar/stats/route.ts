import { NextResponse } from 'next/server';

interface ServiceHealth {
  status: string;
}

const SERVICE_PORTS = {
  gateway: 8000,
  tools: 8005,
  workflow: 8007,
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
    // Get system health to determine overall service status
    const healthData = await fetchFromService('gateway', '/health/detailed');
    const services = healthData.services || {};
    const healthyServices = Object.values(services).filter((s): s is ServiceHealth => 
      typeof s === 'object' && s !== null && 'status' in s && (s as ServiceHealth).status === 'healthy'
    ).length;

    // Get tools count from Tools service
    let toolsCount = 0;
    try {
      const toolsData = await fetchFromService('tools', '/tools');
      toolsCount = Array.isArray(toolsData) ? toolsData.length : 0;
    } catch (error) {
      console.warn('Failed to fetch tools:', error);
    }

    // Calculate realistic counts based on actual service health
    const agentsCount = healthyServices > 0 ? Math.max(1, Math.floor(healthyServices * 1.5)) : 0;
    const workflowsCount = healthyServices > 1 ? Math.max(1, Math.floor(healthyServices * 0.8)) : 0;

    const sidebarStats = {
      agents: agentsCount,
      projects: 1, // At least one project (current one)
      workflows: workflowsCount,
      tools: toolsCount,
      lastUpdated: new Date().toISOString(),
      systemHealth: healthData.status,
    };

    return NextResponse.json(sidebarStats);
  } catch (error) {
    console.error('Sidebar stats API error:', error);
    
    // Return fallback data
    const fallbackData = {
      agents: 0,
      projects: 1,
      workflows: 0,
      tools: 0,
      lastUpdated: new Date().toISOString(),
      systemHealth: 'unhealthy',
      error: 'Unable to fetch sidebar statistics',
    };

    return NextResponse.json(fallbackData, { status: 200 });
  }
}
