#!/usr/bin/env python3
"""
Test specific import issues
"""
import sys
import os

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

print("🔍 Testing specific imports that might be causing issues...")

# Test 1: Can we import aiohttp?
try:
    import aiohttp
    print("✅ aiohttp imported successfully")
except ImportError as e:
    print(f"❌ aiohttp import failed: {e}")

# Test 2: Can we import fastapi components?
try:
    from fastapi import APIRouter, Query
    print("✅ FastAPI components imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

# Test 3: Test OMDB service in isolation
try:
    # Create a minimal version without triggering other imports
    import aiohttp
    import asyncio
    import logging
    import os
    
    class TestOMDBService:
        def __init__(self):
            self.api_key = "4977b044"
            self.base_url = "http://www.omdbapi.com/"
            print(f"✅ Test OMDB Service created with key: {self.api_key[:4]}****")
    
    service = TestOMDBService()
    print("✅ Test OMDB service works in isolation")
    
except Exception as e:
    print(f"❌ Test OMDB service failed: {e}")

# Test 4: Check if we can create a minimal router
try:
    from fastapi import APIRouter
    test_router = APIRouter()
    
    @test_router.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    print("✅ Test router created successfully")
    print(f"   Routes: {[route.path for route in test_router.routes if hasattr(route, 'path')]}")
    
except Exception as e:
    print(f"❌ Test router failed: {e}")

print("\n✨ Basic import test completed!")
