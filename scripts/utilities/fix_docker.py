"""
Docker Configuration Fix Script

This script identifies and fixes common Docker configuration issues
in the Agentic AI Acceleration platform.
"""

import os
import sys
import subprocess
import yaml
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerFixer:
    """Fix Docker configuration issues"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        
    def check_docker_status(self):
        """Check if Docker is running"""
        logger.info("🐳 Checking Docker status...")
        
        try:
            result = subprocess.run(
                ["docker", "version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker is running")
                return True
            else:
                logger.error("❌ Docker is not responding")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Docker command timed out")
            return False
        except FileNotFoundError:
            logger.error("❌ Docker is not installed or not in PATH")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking Docker: {str(e)}")
            return False
    
    def fix_docker_compose_version(self):
        """Fix Docker Compose version warning"""
        logger.info("🔧 Fixing Docker Compose version warning...")
        
        try:
            with open(self.docker_compose_file, 'r') as f:
                content = f.read()
            
            # Remove version line that's causing the warning
            lines = content.split('\\n')
            new_lines = []
            
            for line in lines:
                if not line.strip().startswith('version:'):
                    new_lines.append(line)
                else:
                    logger.info("   Removing obsolete version specification")
            
            # Write back the file
            with open(self.docker_compose_file, 'w') as f:
                f.write('\\n'.join(new_lines))
            
            logger.info("✅ Fixed Docker Compose version warning")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fix Docker Compose version: {str(e)}")
            return False
    
    def check_service_dockerfiles(self):
        """Check if all service Dockerfiles exist"""
        logger.info("📄 Checking service Dockerfiles...")
        
        services = [
            "frontend",
            "backend/services/gateway",
            "backend/services/agents", 
            "backend/services/orchestrator",
            "backend/services/rag",
            "backend/services/tools",
            "backend/services/sqltool",
            "backend/services/workflow-engine",
            "backend/services/observability"
        ]
        
        missing_dockerfiles = []
        
        for service in services:
            dockerfile_path = self.project_root / service / "Dockerfile"
            if not dockerfile_path.exists():
                missing_dockerfiles.append(service)
                logger.warning(f"⚠️ Missing Dockerfile: {dockerfile_path}")
            else:
                logger.info(f"✅ Found Dockerfile: {service}")
        
        return missing_dockerfiles
    
    def create_missing_dockerfiles(self, missing_services):
        """Create missing Dockerfiles for services"""
        logger.info("🏗️ Creating missing Dockerfiles...")
        
        # Frontend Dockerfile
        frontend_dockerfile = '''# Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm build

# Expose port
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
'''
        
        # Backend service Dockerfile template
        backend_dockerfile_template = '''# Backend Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
'''
        
        service_ports = {
            "backend/services/gateway": 8000,
            "backend/services/agents": 8002,
            "backend/services/orchestrator": 8003,
            "backend/services/rag": 8004,
            "backend/services/tools": 8005,
            "backend/services/sqltool": 8006,
            "backend/services/workflow-engine": 8007,
            "backend/services/observability": 8008
        }
        
        for service in missing_services:
            service_path = self.project_root / service
            dockerfile_path = service_path / "Dockerfile"
            
            # Create directory if it doesn't exist
            service_path.mkdir(parents=True, exist_ok=True)
            
            if service == "frontend":
                content = frontend_dockerfile
            else:
                port = service_ports.get(service, 8000)
                content = backend_dockerfile_template.format(port=port)
            
            try:
                with open(dockerfile_path, 'w') as f:
                    f.write(content)
                logger.info(f"✅ Created Dockerfile for {service}")
                
                # Also create a basic requirements.txt if it doesn't exist for backend services
                if service.startswith("backend/"):
                    requirements_path = service_path / "requirements.txt"
                    if not requirements_path.exists():
                        basic_requirements = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
aiofiles==23.2.0
psutil==5.9.6
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
redis==5.0.1
'''
                        with open(requirements_path, 'w') as f:
                            f.write(basic_requirements)
                        logger.info(f"✅ Created requirements.txt for {service}")
                        
            except Exception as e:
                logger.error(f"❌ Failed to create Dockerfile for {service}: {str(e)}")
    
    def check_environment_files(self):
        """Check for required environment files"""
        logger.info("🔧 Checking environment files...")
        
        env_files = [
            ".env",
            "backend/services/gateway/.env",
        ]
        
        missing_env_files = []
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if not env_path.exists():
                missing_env_files.append(env_file)
                logger.warning(f"⚠️ Missing environment file: {env_path}")
            else:
                logger.info(f"✅ Found environment file: {env_file}")
        
        return missing_env_files
    
    def create_environment_files(self, missing_env_files):
        """Create missing environment files"""
        logger.info("📝 Creating environment files...")
        
        # Main .env file
        main_env_content = '''# Main Environment Configuration
NODE_ENV=development
ENVIRONMENT=development

# API Keys (Add your actual keys here)
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform
POSTGRES_USER=agenticai_user
POSTGRES_PASSWORD=agenticai_password
POSTGRES_DB=agenticai_platform

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://web:3000", "http://localhost:8000"]

# Service URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GATEWAY_URL=http://gateway:8000
'''
        
        # Gateway service .env file
        gateway_env_content = '''# Gateway Service Environment
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
CORS_ORIGINS=["http://localhost:3000", "http://web:3000"]

# Downstream service URLs
ORCHESTRATOR_URL=http://orchestrator:8003
AGENTS_URL=http://agents:8002
TOOLS_URL=http://tools:8005
RAG_URL=http://rag:8004
SQLTOOL_URL=http://sqltool:8006
WORKFLOW_URL=http://workflow:8007
OBSERVABILITY_URL=http://observability:8008
'''
        
        env_contents = {
            ".env": main_env_content,
            "backend/services/gateway/.env": gateway_env_content
        }
        
        for env_file in missing_env_files:
            if env_file in env_contents:
                env_path = self.project_root / env_file
                env_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    with open(env_path, 'w') as f:
                        f.write(env_contents[env_file])
                    logger.info(f"✅ Created environment file: {env_file}")
                except Exception as e:
                    logger.error(f"❌ Failed to create {env_file}: {str(e)}")
    
    def fix_all_issues(self):
        """Fix all detected Docker issues"""
        logger.info("🔧 Starting Docker configuration fixes...")
        
        # Check Docker status first
        if not self.check_docker_status():
            logger.error("❌ Docker is not running. Please start Docker Desktop and try again.")
            return False
        
        # Fix Docker Compose version warning
        self.fix_docker_compose_version()
        
        # Check and create missing Dockerfiles
        missing_dockerfiles = self.check_service_dockerfiles()
        if missing_dockerfiles:
            self.create_missing_dockerfiles(missing_dockerfiles)
        
        # Check and create missing environment files
        missing_env_files = self.check_environment_files()
        if missing_env_files:
            self.create_environment_files(missing_env_files)
        
        logger.info("✅ Docker configuration fixes completed!")
        
        # Provide next steps
        logger.info("\\n📋 Next Steps:")
        logger.info("1. Update the .env file with your actual API keys")
        logger.info("2. Run: docker-compose build")
        logger.info("3. Run: docker-compose up -d")
        logger.info("4. Test services with: python tests/api/test_services.py")
        
        return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    logger.info(f"🚀 Starting Docker configuration fixes for: {project_root}")
    
    fixer = DockerFixer(project_root)
    success = fixer.fix_all_issues()
    
    if success:
        logger.info("🎉 All fixes completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some fixes failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
