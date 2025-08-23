# PowerShell script to run Next.js frontend locally
$env:NODE_ENV = "development"
$env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000/api"
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_GATEWAY_URL = "http://localhost:8000"
$env:INTERNAL_GATEWAY_URL = "http://gateway:8000"
cd ../frontend
pnpm dev
