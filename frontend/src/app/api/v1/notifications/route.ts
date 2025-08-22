import { NextRequest, NextResponse } from 'next/server';

// Use internal Docker network URL for server-side API calls
const BACKEND_URL = process.env.INTERNAL_GATEWAY_URL || process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id');
    
    if (!userId) {
      return NextResponse.json({ error: 'user_id parameter is required' }, { status: 400 });
    }

    // Proxy request to backend gateway service
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/notifications?user_id=${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend responded with ${backendResponse.status}: ${backendResponse.statusText}`);
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Notifications API error:', error);
    
    // Return empty notifications array as fallback
    return NextResponse.json({
      notifications: [],
      total: 0,
      unread_count: 0,
      error: `Failed to fetch notifications: ${error instanceof Error ? error.message : 'Unknown error'}`
    }, { status: 200 }); // Return 200 to prevent frontend errors
  }
}