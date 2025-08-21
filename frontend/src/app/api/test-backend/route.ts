import { NextResponse } from 'next/server';

interface TestResult {
  name: string;
  url: string;
  status: string;
  statusCode?: number;
  error?: string | null;
}

interface TestResults {
  timestamp: string;
  tests: TestResult[];
  environment?: {
    nodeEnv: string | undefined;
    backendUrl: string;
    platform: string;
  };
}

export async function GET() {
  const testResults: TestResults = {
    timestamp: new Date().toISOString(),
    tests: [],
  };

  // Test 1: Basic localhost connectivity
  try {
    const response = await fetch('http://localhost:8000/health', {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    testResults.tests.push({
      name: 'Gateway Health Check',
      url: 'http://localhost:8000/health',
      status: response.ok ? 'success' : 'failed',
      statusCode: response.status,
      error: response.ok ? null : response.statusText,
    });
  } catch (error) {
    testResults.tests.push({
      name: 'Gateway Health Check',
      url: 'http://localhost:8000/health',
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Test 2: Tools service
  try {
    const response = await fetch('http://localhost:8005/health', {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    testResults.tests.push({
      name: 'Tools Health Check',
      url: 'http://localhost:8005/health',
      status: response.ok ? 'success' : 'failed',
      statusCode: response.status,
      error: response.ok ? null : response.statusText,
    });
  } catch (error) {
    testResults.tests.push({
      name: 'Tools Health Check',
      url: 'http://localhost:8005/health',
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Test 3: Network environment
  testResults.environment = {
    nodeEnv: process.env.NODE_ENV,
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
    platform: process.platform,
  };

  return NextResponse.json(testResults);
}
