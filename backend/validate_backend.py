#!/usr/bin/env python3
"""
Quick test script to validate backend can start without errors
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all main imports work"""
    try:
        print("🔍 Testing FastAPI import...")
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        print("🔍 Testing app main import...")
        from app.main import app
        print("✅ App main imported successfully")
        
        print("🔍 Testing routes import...")
        from app.api.routes.movies import router
        print("✅ Movies router imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that the app can be created"""
    try:
        print("🔍 Testing app creation...")
        from app.main import app
        print(f"✅ App created: {app.title}")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def main():
    print("🧪 Backend Validation Test")
    print("=" * 30)
    
    import_success = test_imports()
    app_success = test_app_creation()
    
    if import_success and app_success:
        print("\n✅ All tests passed! Backend is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
