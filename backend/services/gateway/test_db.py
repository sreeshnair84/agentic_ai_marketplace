"""
Test database connectivity
"""

import asyncio
from app.core.database import init_db, get_database
from app.models.database.user import UserDB
from sqlalchemy import select

async def test_db():
    """Test database connection"""
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized")
        
        # Get a session
        async for db in get_database():
            print("✅ Got database session")
            
            # Try a simple query
            query = select(UserDB).where(UserDB.email == "admin@lcnc.com")
            result = await db.execute(query)
            user_db = result.scalar_one_or_none()
            
            if user_db:
                print(f"✅ Found user: {user_db.email}, role: {user_db.role}")
            else:
                print("❌ No admin user found")
            
            break  # Exit the async generator
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
