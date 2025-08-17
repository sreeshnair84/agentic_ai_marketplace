from pydantic_settings import BaseSettings

class MinimalSettings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost:3000"
    
    class Config:
        case_sensitive = True

# Test it
settings = MinimalSettings()
print(f"SUCCESS: CORS_ORIGINS = {settings.CORS_ORIGINS}")
