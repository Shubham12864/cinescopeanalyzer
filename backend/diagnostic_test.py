#!/usr/bin/env python3
"""
Diagnostic script to check route imports and definitions
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_imports():
    """Test all imports needed for movie routes"""
    print("🔍 Testing imports...")
    
    try:
        print("1. Testing FastAPI imports...")
        from fastapi import APIRouter, HTTPException, Query
        print("   ✅ FastAPI imports successful")
        
        print("2. Testing OMDB service import...")
        try:
            from app.services.omdb_service import omdb_service
            print(f"   ✅ OMDB service imported: {type(omdb_service)}")
            print(f"   🔑 API Key: {omdb_service.api_key[:4]}****")
        except Exception as e:
            print(f"   ❌ OMDB service import failed: {e}")
        
        print("3. Testing movie routes import...")
        from app.api.routes.movies import router
        print(f"   ✅ Movie router imported: {type(router)}")
        
        # Check registered routes
        print(f"   📋 Registered routes:")
        for route in router.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"      {methods} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_route_functions():
    """Test that route functions are defined"""
    print("\n🎯 Testing route functions...")
    
    try:
        from app.api.routes.movies import (
            health_check,
            get_popular_movies_endpoint,
            get_recent_movies_endpoint,
            get_top_rated_movies_endpoint,
            get_movie_suggestions_endpoint
        )
        
        print("   ✅ All route functions imported successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Route function import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CineScope Backend Diagnostic")
    print("=" * 50)
    
    imports_ok = test_imports()
    functions_ok = test_route_functions()
    
    if imports_ok and functions_ok:
        print("\n✅ All diagnostics passed!")
    else:
        print("\n❌ Some diagnostics failed!")
        sys.exit(1)
