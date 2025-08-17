#!/usr/bin/env python3

import os
from pydantic_settings import BaseSettings
from typing import List

print("Environment variables:")
for key, value in os.environ.items():
    if 'CORS' in key:
        print(f"{key} = {value!r}")

class SimpleSettings(BaseSettings):
    CORS_ORIGINS: str = "http://localhost:3000"
    
    class Config:
        case_sensitive = True

try:
    settings = SimpleSettings()
    print(f"CORS_ORIGINS value: {settings.CORS_ORIGINS!r}")
    print("Settings created successfully!")
except Exception as e:
    print(f"Error: {e}")

# Try with List[str] type
class ListSettings(BaseSettings):
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        case_sensitive = True

try:
    settings2 = ListSettings()
    print(f"List CORS_ORIGINS value: {settings2.CORS_ORIGINS!r}")
    print("List Settings created successfully!")
except Exception as e:
    print(f"List Error: {e}")
