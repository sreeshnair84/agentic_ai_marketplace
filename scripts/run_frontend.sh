#!/bin/bash
# Bash script to run Next.js frontend locally
export NODE_ENV=development
export NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api"
export NEXT_PUBLIC_API_URL="http://localhost:8000"
export NEXT_PUBLIC_GATEWAY_URL="http://localhost:8000"
export INTERNAL_GATEWAY_URL="http://gateway:8000"
cd ../frontend
pnpm dev
