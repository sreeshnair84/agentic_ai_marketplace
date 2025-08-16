# LCNC Multi-Agent Platform - Quick Start Guide

## Consolidated Setup Process

Since the application has not gone live yet, all migration scripts have been consolidated into a single initial setup script for easier deployment and development setup.

## Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL** server running
   - Default: `localhost:5432`
   - Admin user: `postgres` with password `password`
3. **Node.js 16+** for frontend (optional for backend-only setup)
4. **Git** (if cloning repository)

## Fresh Installation

### 1. Run Initial Setup

The consolidated setup script handles everything:

```bash
# Run the complete setup
python initial_setup.py
```

This single script will:
- ✅ Create and configure the database
- ✅ Run essential schema migrations (6 core files)
- ✅ Populate minimal sample data (agents, basic models, demo queries)
- ✅ Set up development environments for backend services
- ✅ Create environment configuration files
- ✅ Install dependencies for backend services
- ✅ Install frontend dependencies
- ✅ Create verification scripts and health check functions

### 2. Verify Setup

```bash
# Test the installation
python verify_setup.py
```

### 3. Start Services

**Backend (API Gateway):**
```bash
cd backend/services/gateway
# Windows
.\\venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate

uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Access Points:**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Admin Login: `admin@lcnc.local` / `admin123`

## What's Different

### Before (Multiple Scripts)
```
run_migration.py              # Database migration
run_agent_migration.py        # Agent fields migration  
run_tools_workflows_migration.py  # Tools/workflows migration
setup_dev.py                  # Dev environment
setup_llm_management.py       # LLM setup
create_admin.py               # Admin user creation
add_sample_data.py            # Sample data
+ many other setup/check scripts (15+ files)
```

### After (Single Script)
```
initial_setup.py              # Everything essential in one place
verify_setup.py               # Auto-generated verification
cleanup_migrations.py         # Archive old scripts (optional)
```

## Streamlined Approach

The new setup focuses on **essential functionality only**:

- **6 core SQL migrations** instead of 12+ files
- **Minimal sample data** (2 agents, 2 models) instead of extensive datasets
- **Essential fields only** for agents, tools, and workflows
- **Development-ready** configuration with ability to add more data later

## Configuration

### Environment Files

The setup script creates these files:

**`.env` (Backend Configuration):**
```env
DATABASE_URL=postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
# ... other settings
```

**`frontend/.env.local` (Frontend Configuration):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Database Configuration

The setup automatically:
- Creates `lcnc_platform` database
- Creates `lcnc_user` with appropriate permissions
- Runs all migrations in sequence
- Populates sample data

## Default Data Created

### Users
- **Admin User**: `admin@lcnc.local` / `admin123`

### Agents (Minimal Set)
- Customer Service Agent
- Data Analyst Agent  

### LLM Models (Essential)
- GPT-4o (OpenAI)
- Gemini 1.5 Pro (Google)

### Embedding Models
- OpenAI Text Embedding 3 Small

### Demo Queries
- Basic agent discovery
- Tool template listing
- Simple workflow creation

*Note: Additional agents, tools, and workflows can be added through the API or admin interface after setup.*

## Migration from Old Setup

If you previously used the individual migration scripts:

1. **Archive old scripts** (optional):
   ```bash
   python cleanup_migrations.py
   ```

2. **Drop and recreate database** (if needed):
   ```sql
   DROP DATABASE IF EXISTS lcnc_platform;
   ```

3. **Run fresh setup**:
   ```bash
   python initial_setup.py
   ```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check user can connect
psql -h localhost -U lcnc_user -d lcnc_platform
```

### Service Dependencies
```bash
# Install missing system dependencies
pip install asyncpg uvicorn fastapi

# Frontend dependencies
cd frontend && npm install
```

### Port Conflicts
Default ports used:
- Gateway: 8000
- Orchestrator: 8001
- Agent: 8002
- RAG: 8003
- Tools: 8005
- Workflow Engine: 8006
- Frontend: 3000

Change in `.env` file if needed.

## Next Steps

1. **Review Documentation**: Check `docs/` folder for detailed guides
2. **API Testing**: Use `WORKING_ENDPOINTS_GUIDE.md` for API examples
3. **Development**: See `docs/operations/FASTAPI_SETUP.md` for development guidelines
4. **Deployment**: Check `docs/operations/deployment.md` for production setup

## Support

- Check verification output: `python verify_setup.py`
- Review setup logs for any error messages
- Ensure all prerequisites are installed
- Check database connectivity and permissions

---

This consolidated approach eliminates the need to run multiple migration scripts and provides a consistent, reliable setup process for both development and production environments.
