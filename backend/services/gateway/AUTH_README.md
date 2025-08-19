# AgenticAI Gateway Service - Authentication Backend

Complete authentication backend for the Agentic AI Acceleration with JWT tokens, user management, and OAuth support.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Setup

1. **Install Dependencies**
```bash
cd backend/services/gateway
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Setup Database**
```bash
python setup_auth.py
```

4. **Start the Service**
```bash
python run.py
```

The service will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔐 Authentication Endpoints

### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@agenticai.com",      # or use "username" instead
  "password": "secret123"
}
```

**Response:**
```json
{
  "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "admin@agenticai.com",
    "username": "admin",
    "firstName": "System",
    "lastName": "Administrator",
    "role": "admin",
    "isActive": true,
    "isVerified": true,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z",
    "provider": "local"
  }
}
```

### Register
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "newuser",
  "password": "securepassword",
  "firstName": "John",
  "lastName": "Doe"
}
```

### Refresh Token
```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Logout
```bash
POST /api/v1/auth/logout
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🏗️ Architecture

### Authentication Flow
1. **Login**: User provides email/username + password
2. **Validation**: Backend verifies credentials against database
3. **Token Generation**: JWT access token (30min) + refresh token (7 days)
4. **Token Storage**: Refresh tokens stored in database with metadata
5. **API Access**: Access token used for authenticated requests
6. **Token Refresh**: Refresh token used to get new access token
7. **Logout**: All user refresh tokens revoked

### Security Features
- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Signed with secret key, includes user info and expiration
- **Token Rotation**: New refresh token issued on each refresh
- **Token Revocation**: Logout revokes all user refresh tokens
- **Role-Based Access**: Admin, User, Viewer roles
- **Session Management**: Track user sessions with device/IP info

## 📊 Database Schema

### Users Table
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(100) UNIQUE NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user',
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  provider VARCHAR(50) DEFAULT 'local',
  provider_id VARCHAR(255),
  avatar_url VARCHAR(500)
)
```

### Refresh Tokens Table
```sql
refresh_tokens (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  token_hash VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  is_revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  device_id VARCHAR(255),
  user_agent TEXT,
  ip_address VARCHAR(50)
)
```

## 🔧 Configuration

### Environment Variables
```env
# Security
SECRET_KEY="your-super-secret-key"
JWT_SECRET_KEY="your-jwt-secret-key"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db"

# Redis
REDIS_URL="redis://localhost:6379/0"

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
```

### Dependencies
```
fastapi[all]>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
redis>=5.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic[email]>=2.0.0
```

## 🧪 Testing

### Manual Testing
```bash
# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.com","password":"secret123"}'

# Test protected endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Test token refresh
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN_HERE"}'
```

### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/auth/health
```

## 🔄 Frontend Integration

The backend is designed to work seamlessly with the frontend authentication system:

### Field Mapping
- Backend `auth_token` → Frontend `access_token`
- Backend `first_name` → Frontend `firstName`
- Backend `last_name` → Frontend `lastName`
- Backend `is_active` → Frontend `isActive`

### Login Support
- Supports both email and username login
- Frontend can send either field, backend handles both

### Token Management
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Automatic token refresh handled by frontend auth service

## 🔮 Future Enhancements

### OAuth Integration
- GitHub OAuth (in progress)
- Google OAuth (in progress)
- Microsoft OAuth (in progress)
- Additional providers as needed

### Advanced Features
- Two-factor authentication (2FA)
- Email verification
- Password reset flows
- Account recovery
- Device management
- Session analytics

### Security Improvements
- Rate limiting on auth endpoints
- Suspicious activity detection
- Geographic login alerts
- Password strength requirements
- Account lockout policies

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in .env
   - Verify database exists and user has permissions

2. **Redis Connection Error**
   - Ensure Redis is running
   - Check REDIS_URL in .env
   - Test connection: `redis-cli ping`

3. **JWT Token Error**
   - Ensure JWT_SECRET_KEY is set and consistent
   - Check token expiration
   - Verify token format in Authorization header

4. **CORS Issues**
   - Update CORS_ORIGINS in .env
   - Ensure frontend URL is included
   - Check browser network tab for CORS errors

### Debug Mode
Set `DEBUG=true` in .env for detailed error messages and SQL query logging.

### Logs
Service logs are output to console. For production, configure structured logging to files.

## 🤝 API Compatibility

This backend authentication system is fully compatible with the frontend implementation and provides:

- ✅ JWT-based authentication
- ✅ Multi-provider support (local + OAuth)
- ✅ Role-based access control
- ✅ Token refresh mechanism
- ✅ User management endpoints
- ✅ Session tracking
- ✅ Security best practices

The system is production-ready and can be extended with additional authentication methods and security features as needed.
