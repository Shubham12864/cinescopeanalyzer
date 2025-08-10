#!/usr/bin/env python3
"""
Simple test to check routes without starting server
"""
import sys
import os

print("🔍 Testing FastAPI route registration...")

# First, let's check if we can import the router directly
try:
    # Add the backend directory to the path
    backend_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_path)
    
    # Import the router specifically
    from app.api.routes.movies import router
    print("✅ Movies router imported successfully!")
    
    # Get all routes
    routes = []
    for route in router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(f"{list(route.methods)[0]} {route.path}")
    
    print(f"📊 Found {len(routes)} routes:")
    for route in sorted(routes):
        print(f"   {route}")
    
    # Check for specific new routes
    target_routes = ['/popular', '/recent', '/top-rated', '/suggestions', '/health']
    for target in target_routes:
        found = any(target in route for route in routes)
        status = "✅" if found else "❌"
        print(f"{status} Route {target}: {'Found' if found else 'Not found'}")
        
except Exception as e:
    print(f"❌ Error importing router: {e}")
    import traceback
    traceback.print_exc()

# Now let's specifically check OMDB service import
print("\n🔍 Testing OMDB service import...")
try:
    from app.services.omdb_service import OMDBService, omdb_service
    print("✅ OMDB service imported successfully!")
    print(f"   Service instance: {omdb_service}")
    print(f"   API key configured: {omdb_service.api_key[:4]}****")
except Exception as e:
    print(f"❌ OMDB service import failed: {e}")
    import traceback
    traceback.print_exc()
