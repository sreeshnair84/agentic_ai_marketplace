"""
Database migration script for authentication tables
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'VIEWER' CHECK (role IN ('ADMIN', 'USER', 'VIEWER')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    provider VARCHAR(50) DEFAULT 'local',
    provider_id VARCHAR(255),
    avatar_url VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_provider ON users(provider, provider_id);
"""

CREATE_REFRESH_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    device_id VARCHAR(255),
    user_agent TEXT,
    ip_address VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
"""

CREATE_USER_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    device_id VARCHAR(255),
    user_agent TEXT,
    ip_address VARCHAR(50),
    location VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
"""

CREATE_PASSWORD_RESET_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token_hash ON password_reset_tokens(token_hash);
"""

CREATE_EMAIL_VERIFICATION_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token_hash ON email_verification_tokens(token_hash);
"""

CREATE_UPDATED_AT_TRIGGER = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""

INSERT_DEFAULT_ADMIN = """
INSERT INTO users (
    email, 
    username, 
    first_name, 
    last_name, 
    hashed_password, 
    role, 
    is_active, 
    is_verified,
    provider
) VALUES (
    'admin@agenticai.com', 
    'admin', 
    'System', 
    'Administrator', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- 'secret123'
    'ADMIN', 
    TRUE, 
    TRUE,
    'local'
) ON CONFLICT (email) DO NOTHING;
"""

# Migration to add selected_project_id column
ADD_SELECTED_PROJECT_ID_COLUMN = """
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS selected_project_id UUID;
"""

# SQL statements in order
MIGRATION_STATEMENTS = [
    CREATE_USERS_TABLE,
    CREATE_REFRESH_TOKENS_TABLE,
    CREATE_USER_SESSIONS_TABLE,
    CREATE_PASSWORD_RESET_TOKENS_TABLE,
    CREATE_EMAIL_VERIFICATION_TOKENS_TABLE,
    CREATE_UPDATED_AT_TRIGGER,
    INSERT_DEFAULT_ADMIN,
    ADD_SELECTED_PROJECT_ID_COLUMN
]


async def run_migration(db_connection):
    """Run database migration"""
    for statement in MIGRATION_STATEMENTS:
        await db_connection.execute(statement)
    
    await db_connection.commit()
    print("✅ Authentication tables created successfully")
    print("📧 Default admin user: admin@agenticai.com / secret123")


if __name__ == "__main__":
    import asyncio
    import asyncpg
    import os
    
    async def main():
        # Database connection details
        DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://agenticai_user:agenticai_password@localhost:5432/agenticai_platform"
        )
        
        # Parse connection string for asyncpg
        # Remove postgresql:// prefix and extract components
        db_url = DATABASE_URL.replace("postgresql://", "").replace("postgresql+asyncpg://", "")
        
        try:
            # Connect to database
            conn = await asyncpg.connect(DATABASE_URL.replace("+asyncpg", ""))
            
            print("🔗 Connected to database")
            print("🚀 Running authentication migration...")
            
            # Run migration
            for statement in MIGRATION_STATEMENTS:
                await conn.execute(statement)
            
            print("✅ Authentication tables created successfully")
            print("📧 Default admin user: admin@agenticai.com / secret123")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
        finally:
            if 'conn' in locals():
                await conn.close()
    
    asyncio.run(main())
