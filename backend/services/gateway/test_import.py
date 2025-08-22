#!/usr/bin/env python3
"""
Test script to check if chat_a2a module loads correctly
"""

try:
    import sys
    import os
    
    # Add current directory to path
    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)
    
    print("Testing chat_a2a import...")
    from app.api.chat_a2a import router
    print("✓ SUCCESS: Chat A2A module loaded successfully")
    print(f"Router type: {type(router)}")
    print(f"Router routes: {len(router.routes) if hasattr(router, 'routes') else 'unknown'}")
    
except Exception as e:
    print(f"✗ ERROR: Failed to load chat_a2a module: {e}")
    import traceback
    traceback.print_exc()
