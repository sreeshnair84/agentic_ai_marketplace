#!/usr/bin/env python3
"""
Test password hashing and verification
"""

from passlib.context import CryptContext

# Test password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "secret123"
print(f"🔐 Testing password: {password}")

# Hash the password
hashed = pwd_context.hash(password)
print(f"🔐 Hashed password: {hashed}")

# Verify the password
is_valid = pwd_context.verify(password, hashed)
print(f"✅ Password verification: {is_valid}")

# Test with the existing hash from database
existing_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
is_valid_existing = pwd_context.verify(password, existing_hash)
print(f"✅ Existing hash verification: {is_valid_existing}")

print("🎯 Password testing completed!")
