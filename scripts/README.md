# LCNC Platform - Scripts Directory

This directory contains utility scripts for testing, debugging, and maintaining the LCNC Multi-Agent Platform.

## 📁 Directory Structure

```
scripts/
├── testing/          # API and functionality testing scripts
├── debug/            # Database and system debugging scripts  
├── utilities/        # System maintenance and utilities
└── README.md         # This file
```

## 🧪 Testing Scripts (`testing/`)

### API Testing
- **`test_all_endpoints.py`** - Comprehensive endpoint testing across all 8 microservices
- **`test_backend.py`** - Backend authentication API testing
- **`test_basic_endpoints.py`** - Basic service health and functionality validation
- **`test_frontend_api.py`** - Frontend API integration testing
- **`test_llm_api.py`** - LLM Models API endpoint testing
- **`test_user_management.py`** - User management functionality testing

### Specialized Testing
- **`test_rag_pgvector.py`** - RAG service with PGVector testing
- **`test_password.py`** - Password hashing and verification testing
- **`verify_complete_apis.py`** - Complete API verification with signature support
- **`verify_signatures.py`** - Agent signature and DNS data verification

### Usage Examples

```bash
# Test all backend services
python scripts/testing/test_backend.py

# Test all API endpoints
python scripts/testing/test_all_endpoints.py

# Verify API completeness
python scripts/testing/verify_complete_apis.py

# Test RAG functionality
python scripts/testing/test_rag_pgvector.py
```

## 🔍 Debug Scripts (`debug/`)

### Database Inspection
- **`check_agents.py`** - Agents table schema and data inspection
- **`check_db.py`** - General database structure and connectivity check
- **`check_schema.py`** - Current database schema analysis
- **`check_tools_workflows.py`** - Tools and workflows table schema inspection
- **`debug_db.py`** - Advanced database debugging and query testing

### Usage Examples

```bash
# Check database connectivity and structure
python scripts/debug/check_db.py

# Inspect agents table
python scripts/debug/check_agents.py

# Debug database queries
python scripts/debug/debug_db.py

# Check current schema
python scripts/debug/check_schema.py
```

## 🛠️ Utility Scripts (`utilities/`)

### System Maintenance
- **`fix_docker.py`** - Docker configuration troubleshooting and fixes
- **`cleanup_migrations.py`** - Archive old migration scripts (historical)

### Usage Examples

```bash
# Fix Docker configuration issues
python scripts/utilities/fix_docker.py

# Archive old migration files
python scripts/utilities/cleanup_migrations.py
```

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure the platform is set up
python initial_setup.py

# Start backend services
cd backend/services/gateway
python -m uvicorn app.main:app --reload --port 8000
```

### Run Basic Health Check
```bash
# Test basic connectivity
python scripts/testing/test_basic_endpoints.py

# Check database health
python scripts/debug/check_db.py
```

### Run Comprehensive Testing
```bash
# Test all endpoints
python scripts/testing/test_all_endpoints.py

# Verify all APIs
python scripts/testing/verify_complete_apis.py
```

## 📋 Testing Checklist

When developing or debugging, run these scripts in order:

1. **Database Health**: `python scripts/debug/check_db.py`
2. **Schema Verification**: `python scripts/debug/check_schema.py`
3. **Basic Endpoints**: `python scripts/testing/test_basic_endpoints.py`
4. **Backend APIs**: `python scripts/testing/test_backend.py`
5. **Complete Testing**: `python scripts/testing/test_all_endpoints.py`

## 🔧 Common Issues

### Database Connection Errors
```bash
# Check database connectivity
python scripts/debug/check_db.py

# Verify schema
python scripts/debug/check_schema.py
```

### API Endpoint Issues
```bash
# Test specific endpoints
python scripts/testing/test_backend.py

# Check all endpoints
python scripts/testing/test_all_endpoints.py
```

### Docker Problems
```bash
# Fix Docker configuration
python scripts/utilities/fix_docker.py
```

## 📝 Notes

- All scripts assume the platform is set up using `initial_setup.py`
- Database URL: `postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform`
- Default admin credentials: `admin@lcnc.local` / `admin123`
- Backend services run on ports 8000-8008
- Frontend runs on port 3000

## 🔄 Maintenance

These scripts are maintained as part of the LCNC Platform. When adding new features:

1. Add corresponding test scripts to `testing/`
2. Add debug scripts to `debug/` if needed
3. Update this README with new script descriptions
4. Test the scripts with the consolidated setup

---

**Note**: All migration and setup functionality has been consolidated into `initial_setup.py` in the root directory. These scripts are for testing, debugging, and maintenance only.
