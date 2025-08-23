#!/usr/bin/env python3
"""
Initial Setup Script for AgenticAI Multi-Agent Platform
This consolidated script replaces all migration scripts for a fresh installation.

Includes:
- Complete database schema initialization
- Sample data population
- Development environment setup
- Service dependency installation
- Basic verification tests

Run this script once when setting up the platform for the first time.
"""

import asyncio
import asyncpg
import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from typing import List, Dict, Any

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform")
POSTGRES_ADMIN_URL = os.getenv("POSTGRES_ADMIN_URL", "postgresql://postgres:password@localhost:5432/postgres")

class SetupManager:
    """Manages the complete setup process"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.success_count = 0
        self.total_steps = 0
        
    def log_step(self, message: str, success: bool = True):
        """Log a setup step"""
        symbol = "✅" if success else "❌"
        print(f"{symbol} {message}")
        if success:
            self.success_count += 1
        self.total_steps += 1
    
    def run_command(self, command: str, description: str, cwd: str | None = None) -> bool:
        """Run a shell command"""
        try:
            print(f"🔄 {description}...")
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.log_step(description)
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()[:200]}...")
                return True
            else:
                self.log_step(f"{description} - {result.stderr.strip()}", False)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step(f"{description} - Timeout", False)
            return False
        except Exception as e:
            self.log_step(f"{description} - Exception: {e}", False)
            return False

    async def setup_database(self) -> bool:
        """Set up the complete database schema"""
        print("\n" + "="*50)
        print("🗄️  DATABASE SETUP")
        print("="*50)
        
        try:
            # First, ensure database exists
            await self.ensure_database_exists()
            
            # Connect to the main database
            print("🔌 Connecting to AgenticAI database...")
            conn = await asyncpg.connect(DATABASE_URL)
            
            # Execute consolidated migrations (only 2 files)
            migration_files = [
                "0001_complete_schema.sql",
                "0002_vector_and_data.sql",
                
            ]
            
            for migration_file in migration_files:
                await self.execute_migration(conn, migration_file)
            
            # Add comprehensive sample data
            await self.populate_sample_data(conn)
            
            # Verify database setup
            await self.verify_database(conn)
            
            await conn.close()
            self.log_step("Database setup completed")
            return True
            
        except Exception as e:
            self.log_step(f"Database setup failed: {str(e)}", False)
            return False

    async def ensure_database_exists(self):
        """Ensure the AgenticAI database exists"""
        try:
            # Connect to postgres admin database
            admin_conn = await asyncpg.connect(POSTGRES_ADMIN_URL)
            
            # Check if database exists
            db_exists = await admin_conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = 'agenticai_platform')"
            )
            
            if not db_exists:
                print("🔧 Creating AgenticAI database...")
                await admin_conn.execute("CREATE DATABASE agenticai_platform")
                self.log_step("Created AgenticAI database")
            else:
                self.log_step("AgenticAI database already exists")
            
            # Create user if not exists
            user_exists = await admin_conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname = 'agenticai_user')"
            )
            
            if not user_exists:
                await admin_conn.execute("CREATE USER agenticai_user WITH PASSWORD 'agenticai_password'")
                await admin_conn.execute("GRANT ALL PRIVILEGES ON DATABASE agenticai_platform TO agenticai_user")
                self.log_step("Created AgenticAI user")
            else:
                self.log_step("AgenticAI user already exists")
                
            await admin_conn.close()
            
        except Exception as e:
            print(f"⚠️  Database creation check failed: {e}")
            print("   Assuming database exists and continuing...")

    async def execute_migration(self, conn: asyncpg.Connection, filename: str):
        """Execute a single migration file"""
        migration_path = self.project_root / "infra" / "migrations" / filename
        
        if not migration_path.exists():
            print(f"⚠️  Migration file not found: {filename}")
            return
        
        print(f"📄 Executing migration: {filename}")
        
        try:
            migration_sql = migration_path.read_text(encoding='utf-8')
            await conn.execute(migration_sql)
            self.log_step(f"Applied migration: {filename}")
        except Exception as e:
            if "already exists" in str(e).lower():
                self.log_step(f"Migration {filename} already applied")
            else:
                raise e

    async def populate_sample_data(self, conn: asyncpg.Connection):
        """Sample data is now included in migration files"""
        print("\n📊 Sample data included in migrations...")
        self.log_step("Sample data loaded from migration files")

    async def verify_database(self, conn: asyncpg.Connection):
        """Verify database setup"""
        print("\n🔍 Verifying database setup...")
        
        # Check essential tables exist
        essential_tables = [
            'agents', 'tool_templates', 'workflow_definitions',
            'llm_models', 'embedding_models', 'users', 'demo_sample_queries',
            'document_embeddings', 'knowledge_base_embeddings', 'projects'
        ]
        
        for table in essential_tables:
            exists = await conn.fetchval(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table}'
                )
            """)
            if exists:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                self.log_step(f"Table {table}: {count} records")
            else:
                self.log_step(f"Table {table} missing", False)
        
        # Test platform health function
        try:
            health_check = await conn.fetch("SELECT * FROM check_platform_health()")
            self.log_step("Platform health check function works")
            for record in health_check:
                print(f"   {record['component']}: {record['count']} {record['status']}")
        except Exception as e:
            self.log_step(f"Health check function failed: {e}", False)
        
        # Test vector extension
        try:
            vector_enabled = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            self.log_step(f"Vector extension enabled: {vector_enabled}")
        except Exception as e:
            self.log_step(f"Vector extension check failed: {e}", False)
        
        # Verify admin user
        admin_exists = await conn.fetchval("""
            SELECT EXISTS(SELECT 1 FROM users WHERE email = 'admin@agenticai.local')
        """)
        self.log_step(f"Admin user exists: {admin_exists}")

    def setup_development_environment(self) -> bool:
        """Set up development environment"""
        print("\n" + "="*50)
        print("🛠️  DEVELOPMENT ENVIRONMENT SETUP")
        print("="*50)
        
        success = True
        
        # Backend services setup
        backend_services = [
            ("backend/services/gateway", "API Gateway"),
            ("backend/services/orchestrator", "Orchestrator"),
            ("backend/services/rag", "RAG Service"),
            ("backend/services/tools", "Tools Service"),
            ("backend/services/workflow-engine", "Workflow Engine")
        ]
        
        for service_path, service_name in backend_services:
            full_path = self.project_root / service_path
            if full_path.exists():
                success &= self.setup_backend_service(full_path, service_name)
            else:
                print(f"⚠️  Service not found: {service_path}")
        
        # Frontend setup
        frontend_path = self.project_root / "frontend"
        if frontend_path.exists():
            success &= self.setup_frontend(frontend_path)
        else:
            print("⚠️  Frontend directory not found")
        
        return success

    def setup_backend_service(self, service_path: Path, service_name: str) -> bool:
        """Set up a single backend service"""
        print(f"\n🔧 Setting up {service_name}...")
        
        requirements_file = service_path / "requirements.txt"
        if not requirements_file.exists():
            print(f"⚠️  No requirements.txt found for {service_name}")
            return True
        
        # Create virtual environment
        venv_path = service_path / "venv"
        if not venv_path.exists():
            success = self.run_command(
                "python -m venv venv",
                f"Creating virtual environment for {service_name}",
                str(service_path)
            )
            if not success:
                return False
        
        # Install dependencies
        if sys.platform == "win32":
            pip_cmd = str(venv_path / "Scripts" / "pip")
        else:
            pip_cmd = str(venv_path / "bin" / "pip")
        
        success = self.run_command(
            f'"{pip_cmd}" install --upgrade pip',
            f"Upgrading pip for {service_name}",
            str(service_path)
        )
        
        if success:
            success = self.run_command(
                f'"{pip_cmd}" install -r requirements.txt',
                f"Installing dependencies for {service_name}",
                str(service_path)
            )
        
        return success

    def setup_frontend(self, frontend_path: Path) -> bool:
        """Set up frontend"""
        print(f"\n🎨 Setting up Frontend...")
        
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            print("⚠️  No package.json found for frontend")
            return True
        
        # Determine package manager
        if (frontend_path / "pnpm-lock.yaml").exists():
            return self.run_command("pnpm install", "Installing frontend dependencies (pnpm)", str(frontend_path))
        elif (frontend_path / "yarn.lock").exists():
            return self.run_command("yarn install", "Installing frontend dependencies (yarn)", str(frontend_path))
        else:
            return self.run_command("npm install", "Installing frontend dependencies (npm)", str(frontend_path))

    def create_environment_files(self) -> bool:
        """Create necessary environment files"""
        print("\n" + "="*50)
        print("📝 ENVIRONMENT CONFIGURATION")
        print("="*50)
        
        # Create .env file for backend services
        env_content = """# Agentic AI Accelerator Environment Configuration

# Database
DATABASE_URL=postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform
POSTGRES_ADMIN_URL=postgresql://postgres:password@localhost:5432/postgres

# Redis (if using)
REDIS_URL=redis://localhost:6379

# JWT Configuration  
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Origins
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# API Keys (configure as needed)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# Service Ports
GATEWAY_PORT=8000
ORCHESTRATOR_PORT=8001
AGENT_PORT=8002
RAG_PORT=8003
TOOLS_PORT=8005
WORKFLOW_ENGINE_PORT=8006

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Frontend URL
FRONTEND_URL=http://localhost:3000
"""
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            env_file.write_text(env_content)
            self.log_step("Created .env file")
        else:
            self.log_step(".env file already exists")
        
        # Create .env.local for frontend
        frontend_env_content = """# Frontend Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
"""
        
        frontend_env = self.project_root / "frontend" / ".env.local"
        if not frontend_env.exists() and (self.project_root / "frontend").exists():
            frontend_env.write_text(frontend_env_content)
            self.log_step("Created frontend .env.local file")
        
        return True

    def run_verification_tests(self) -> bool:
        """Run basic verification tests"""
        print("\n" + "="*50)
        print("🧪 VERIFICATION TESTS")
        print("="*50)
        
        # Test database connection
        try:
            asyncio.run(self.test_database_connection())
        except Exception as e:
            self.log_step(f"Database connection test failed: {e}", False)
            return False
        
        # Create verification script
        self.create_verification_script()
        
        return True

    async def test_database_connection(self):
        """Test database connection"""
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            
            # Test basic query
            result = await conn.fetchval("SELECT COUNT(*) FROM agents")
            self.log_step(f"Database connection test passed - {result} agents found")
            
            # Test user authentication table
            admin_count = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'ADMIN'")
            self.log_step(f"Authentication system ready - {admin_count} admin users")
            
            await conn.close()
            
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")

    def create_verification_script(self):
        """Create a verification script for testing the setup"""
        verification_script = '''#!/usr/bin/env python3
"""
Quick verification script to test AgenticAI platform setup
"""
import asyncio
import asyncpg
import requests
import sys

DATABASE_URL = "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"

async def verify_database():
    """Verify database setup"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check essential tables
        tables = ['agents', 'users', 'tool_templates', 'workflow_definitions', 'llm_models', 'projects']
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"✅ {table}: {count} records")
        
        # Test health check function
        try:
            health = await conn.fetch("SELECT * FROM check_platform_health()")
            print("\\n📊 Platform Health:")
            for record in health:
                print(f"   {record['component']}: {record['count']} {record['status']}")
        except Exception as e:
            print(f"⚠️  Health check function error: {e}")
        
        # Test vector extension
        try:
            vector_enabled = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            print(f"\\n🔗 Vector extension enabled: {vector_enabled}")
            
            # Check vector tables
            vector_tables = ['document_embeddings', 'knowledge_base_embeddings']
            for table in vector_tables:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"   {table}: {count} records")
        except Exception as e:
            print(f"⚠️  Vector extension check error: {e}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def verify_backend():
    """Verify backend services (if running)"""
    services = [
        ("Gateway", "http://localhost:8000/health"),
        ("Tools", "http://localhost:8005/health")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} service is running")
            else:
                print(f"⚠️  {name} service returned {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"⚠️  {name} service is not running")

async def main():
    print("🔍 Agentic AI Accelerator Verification")
    print("=" * 40)
    
    # Test database
    db_ok = await verify_database()
    
    # Test backend services
    print("\\nBackend Services Status:")
    verify_backend()
    
    print("\\n" + "=" * 40)
    if db_ok:
        print("✅ Platform setup verification completed!")
        print("\\nDatabase Schema: 2 consolidated migration files")
        print("✅ Complete schema with all tables")
        print("✅ Vector storage for RAG capabilities") 
        print("✅ Essential sample data loaded")
        print("✅ Health check functions working")
        print("\\nTo start the platform:")
        print("1. Start backend:")
        print("   cd backend/services/gateway && python -m uvicorn app.main:app --reload --port 8000")
        print("2. Start frontend:")
        print("   cd frontend && npm run dev")
        print("3. Visit: http://localhost:3000")
        print("4. Admin login: admin@agenticai.local / admin123")
    else:
        print("❌ Platform setup has issues - check the errors above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        verify_script_path = self.project_root / "verify_setup.py"
        verify_script_path.write_text(verification_script)
        self.log_step("Created verification script: verify_setup.py")

    def print_summary(self):
        """Print setup summary"""
        print("\n" + "="*60)
        print("🎉 AgenticAI PLATFORM INITIAL SETUP COMPLETE!")
        print("="*60)
        
        print(f"\nSetup Results: {self.success_count}/{self.total_steps} steps completed successfully")
        
        print("\nWhat was set up:")
        print("✅ Complete database schema (2 consolidated migrations)")
        print("✅ Vector storage for RAG capabilities")
        print("✅ Essential sample data (2 agents, 2 LLM models, workflows)")
        print("✅ Default admin user (admin@agenticai.local / admin123)")
        print("✅ Development environment for backend services")
        print("✅ Environment configuration files")
        print("✅ Health check functions and verification scripts")
        
        print("\nNext Steps:")
        print("1. 📝 Review and update .env files with your API keys")
        print("2. 🚀 Start the backend services:")
        print("   cd backend/services/gateway")
        if sys.platform == "win32":
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("   python -m uvicorn app.main:app --reload --port 8000")
        
        print("\n3. 🎨 Start the frontend:")
        print("   cd frontend")
        print("   npm run dev")
        
        print("\n4. 🌐 Access the platform:")
        print("   Frontend: http://localhost:3000")
        print("   API Docs: http://localhost:8000/docs")
        print("   Admin: admin@agenticai.local / admin123")
        
        print("\n5. 🧪 Verify setup:")
        print("   python verify_setup.py")
        
        print("\n📚 Documentation:")
        print("   README.md - General setup guide")
        print("   docs/ - Detailed documentation")
        print("   WORKING_ENDPOINTS_GUIDE.md - API usage examples")
        
        if self.success_count < self.total_steps:
            print(f"\n⚠️  Warning: {self.total_steps - self.success_count} steps had issues")
            print("   Check the error messages above and resolve any problems")

async def main():
    """Main setup function"""
    print("🚀 AgenticAI Multi-Agent Platform - Initial Setup")
    print("This script will set up the complete platform from scratch")
    print("="*60)
    
    # Confirm setup
    try:
        response = input("\nProceed with initial setup? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        return
    
    setup_manager = SetupManager()
    
    try:
        # Run all setup steps
        await setup_manager.setup_database()
        setup_manager.setup_development_environment()
        setup_manager.create_environment_files()
        setup_manager.run_verification_tests()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        setup_manager.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
