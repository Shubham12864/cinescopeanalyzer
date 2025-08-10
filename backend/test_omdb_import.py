#!/usr/bin/env python3
"""
Test OMDB service import
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath('.'))

print("🔍 Testing OMDB Service Import...")
print(f"Python path: {sys.path[:3]}...")
print(f"Current directory: {os.getcwd()}")

try:
    from app.services.omdb_service import omdb_service
    print("✅ OMDB service imported successfully!")
    print(f"Service instance: {omdb_service}")
    print(f"API Key: {omdb_service.api_key[:4]}****")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.services.omdb_service import OMDBService  
    print("✅ OMDBService class imported successfully!")
except ImportError as e:
    print(f"❌ Class import failed: {e}")

# Test the routes import
try:
    from app.api.routes.movies import router
    print("✅ Movies router imported successfully!")
    print(f"Routes in router: {len(router.routes)}")
    
    # Check for specific routes
    route_paths = [route.path for route in router.routes if hasattr(route, 'path')]
    print(f"Available routes: {route_paths[:10]}...")  # Show first 10
    
    if '/popular' in route_paths:
        print("✅ /popular route found!")
    else:
        print("❌ /popular route not found!")
        
except ImportError as e:
    print(f"❌ Router import failed: {e}")
    import traceback
    traceback.print_exc()
