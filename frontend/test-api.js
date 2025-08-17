// Simple script to test backend API connection
const API_BASE_URL = 'http://localhost:8000';

async function testAPI() {
  console.log('Testing backend API connection...\n');

  try {
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    console.log(`Health Status: ${healthResponse.status}`);
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('Health Data:', healthData);
    }
    console.log('');

    // Test projects endpoint
    console.log('2. Testing projects endpoint...');
    const projectsResponse = await fetch(`${API_BASE_URL}/api/v1/projects`);
    console.log(`Projects Status: ${projectsResponse.status}`);
    if (projectsResponse.ok) {
      const projectsData = await projectsResponse.json();
      console.log('Projects Data:', JSON.stringify(projectsData, null, 2));
    } else {
      const errorText = await projectsResponse.text();
      console.log('Projects Error:', errorText);
    }
    console.log('');

    // Test default project endpoint
    console.log('3. Testing default project endpoint...');
    const defaultResponse = await fetch(`${API_BASE_URL}/api/v1/projects/default`);
    console.log(`Default Project Status: ${defaultResponse.status}`);
    if (defaultResponse.ok) {
      const defaultData = await defaultResponse.json();
      console.log('Default Project Data:', JSON.stringify(defaultData, null, 2));
    } else {
      const errorText = await defaultResponse.text();
      console.log('Default Project Error:', errorText);
    }

  } catch (error) {
    console.error('API Test Failed:', error.message);
    console.log('\nMake sure the backend is running on http://localhost:8000');
    console.log('To start the backend:');
    console.log('1. Navigate to backend/services/gateway');
    console.log('2. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000');
  }
}

testAPI();
