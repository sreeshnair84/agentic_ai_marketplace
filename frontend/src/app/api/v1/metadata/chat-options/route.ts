import { NextResponse } from 'next/server';

// Use internal Docker network URL for server-side API calls
const BACKEND_URL = process.env.INTERNAL_GATEWAY_URL || process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    console.log('Chat Options API: Attempting to connect to backend at:', BACKEND_URL);
    
    // Proxy request to backend gateway service
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/metadata/chat-options`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(15000), // 15 second timeout
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend responded with ${backendResponse.status}: ${backendResponse.statusText}`);
    }

    const data = await backendResponse.json();
    console.log('Chat Options API: Successfully fetched metadata');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Chat Options API error:', error);
    
    // Return minimal fallback data to prevent frontend crashes
    const fallbackData = {
      workflows: [
        {
          id: "default-plan-execute",
          name: "default-plan-execute", 
          display_name: "Smart Plan & Execute",
          description: "Intelligent workflow that analyzes your query and selects the best approach",
          category: "intelligent-routing",
          version: "1.0.0",
          status: "active",
          type: "workflow",
          is_default: true
        }
      ],
      agents: [],
      tools: [],
      summary: {
        total_workflows: 1,
        total_agents: 0,
        total_tools: 0,
        categories: {
          workflows: ["intelligent-routing"],
          agents: [],
          tools: []
        }
      },
      error: `Failed to fetch metadata: ${error instanceof Error ? error.message : 'Unknown error'}`
    };

    return NextResponse.json(fallbackData, { status: 200 }); // Return 200 to prevent frontend errors
  }
}