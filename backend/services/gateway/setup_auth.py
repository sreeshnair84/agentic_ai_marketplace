#!/usr/bin/env python3
"""
Setup script for LCNC Gateway Service Authentication
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🚀 LCNC Gateway Service - Authentication Setup")
    print("=" * 50)

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8, 0):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Setup environment file"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping...")
        return
    
    if env_example.exists():
        # Copy example file
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Environment file created from .env.example")
        print("📝 Please update .env with your configuration")
    else:
        print("⚠️  .env.example not found, please create .env manually")

async def setup_database():
    """Setup database tables"""
    print("\n🗄️  Setting up database...")
    
    try:
        # Import the migration script
        from migrate_auth import MIGRATION_STATEMENTS
        import asyncpg
        import os
        
        # Get database URL from environment
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform"
        )
        
        # Connect and run migration
        conn = await asyncpg.connect(DATABASE_URL.replace("+asyncpg", ""))
        
        print("🔗 Connected to database")
        
        # Run migration statements
        for statement in MIGRATION_STATEMENTS:
            await conn.execute(statement)
        
        await conn.close()
        
        print("✅ Database tables created successfully")
        print("👤 Default admin user created:")
        print("   📧 Email: admin@lcnc.com")
        print("   🔑 Password: secret123")
        
    except ImportError:
        print("❌ Migration script not found")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("💡 Make sure PostgreSQL is running and database exists")

def print_next_steps():
    """Print next steps for user"""
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your configuration")
    print("2. Ensure PostgreSQL and Redis are running")
    print("3. Start the gateway service:")
    print("   python run.py")
    print("\n🔗 Service endpoints:")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    print("\n🔐 Test authentication:")
    print("   curl -X POST http://localhost:8000/api/v1/auth/login \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"email\":\"admin@lcnc.com\",\"password\":\"secret123\"}'")

async def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Setup database
    await setup_database()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    asyncio.run(main())
