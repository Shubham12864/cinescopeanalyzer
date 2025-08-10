"""
Phase 1-2: Backend and Configuration Debugging Tool
This script checks backend status, environment variables, and proxy endpoint
"""
import requests
import os
import json
from pathlib import Path

def check_backend_status():
    """Phase 1: Check if backend is running and accessible"""
    print("🔍 Phase 1: Backend Status Check")
    print("-" * 40)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running on port 8000")
            health_data = response.json()
            print(f"   Services: {health_data.get('services', {})}")
        else:
            print(f"⚠️ Backend health check returned: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running on port 8000")
        print("   Start it with: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False
    
    return True

def check_environment_config():
    """Phase 2: Check environment variables and configuration"""
    print("\n🔧 Phase 2: Environment Configuration Check")
    print("-" * 40)
    
    # Check .env file
    env_file = Path("../.env")  # Backend is one level up from root
    if env_file.exists():
        print("✅ .env file found")
        with open(env_file, 'r') as f:
            content = f.read()
            if "OMDB_API_KEY" in content:
                print("✅ OMDB_API_KEY found in .env")
            else:
                print("⚠️ OMDB_API_KEY not found in .env")
                
            if "NEXT_PUBLIC_API_URL" in content:
                print("✅ NEXT_PUBLIC_API_URL found in .env")
            else:
                print("⚠️ NEXT_PUBLIC_API_URL not found in .env")
    else:
        print("❌ .env file not found")
    
    # Check backend .env
    backend_env = Path(".env")
    if backend_env.exists():
        print("✅ Backend .env file found")
        with open(backend_env, 'r') as f:
            content = f.read()
            if "OMDB_API_KEY" in content:
                key_line = [line for line in content.split('\n') if 'OMDB_API_KEY' in line][0]
                print(f"✅ Backend OMDB_API_KEY: {key_line[:20]}...")
    else:
        print("❌ Backend .env file not found")

def test_image_proxy_endpoint():
    """Phase 3: Test image proxy endpoint directly"""
    print("\n🖼️ Phase 3: Image Proxy Endpoint Test")
    print("-" * 40)
    
    # Test with a known OMDB image URL
    test_urls = [
        "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
        "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg"
    ]
    
    for i, test_url in enumerate(test_urls, 1):
        print(f"\nTest {i}: Testing image proxy with OMDB URL")
        print(f"URL: {test_url[:80]}...")
        
        try:
            proxy_url = f"http://localhost:8000/api/movies/image-proxy?url={test_url}"
            response = requests.get(proxy_url, timeout=15)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                content_length = len(response.content)
                print(f"✅ Success! Content-Type: {content_type}, Size: {content_length} bytes")
                
                if 'image' in content_type:
                    print("✅ Response is an image")
                else:
                    print(f"⚠️ Response is not an image: {response.text[:100]}")
                    
            elif response.status_code == 404:
                print("❌ Image proxy endpoint not found (404)")
                print("   Check if /api/movies/image-proxy route exists")
                
            elif response.status_code >= 500:
                print(f"❌ Server error ({response.status_code})")
                print(f"   Error: {response.text[:200]}")
                
            else:
                print(f"❌ HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (>15s)")
            print("   This suggests the proxy is trying to fetch but failing")
            
        except Exception as e:
            print(f"❌ Request failed: {e}")

def test_search_endpoint():
    """Phase 4: Test search endpoint to check poster URLs"""
    print("\n🔍 Phase 4: Search Endpoint Test")
    print("-" * 40)
    
    test_queries = ["batman", "inception"]
    
    for query in test_queries:
        print(f"\nTesting search: '{query}'")
        
        try:
            response = requests.get(f"http://localhost:8000/api/movies/search?q={query}&limit=2", timeout=15)
            
            if response.status_code == 200:
                movies = response.json()
                print(f"✅ Found {len(movies)} movies")
                
                for i, movie in enumerate(movies, 1):
                    title = movie.get('title', 'Unknown')
                    poster = movie.get('poster', 'No poster')
                    
                    print(f"\n  Movie {i}: {title}")
                    print(f"  Poster URL: {poster[:100]}...")
                    
                    # Analyze poster URL
                    if not poster or poster == "N/A":
                        print("    ❌ No poster URL")
                    elif "image-proxy" in poster:
                        if poster.count("image-proxy") > 1:
                            print("    ❌ CIRCULAR REFERENCE DETECTED!")
                        else:
                            print("    ✅ Using image proxy")
                    elif "m.media-amazon.com" in poster:
                        print("    ✅ Direct OMDB URL")
                    else:
                        print(f"    ⚠️ Unknown URL type")
                        
            else:
                print(f"❌ Search failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Search error: {e}")

def main():
    print("🔧 CineScopeAnalyzer - Systematic Debugging Tool")
    print("=" * 60)
    print("Following your Phase 1-4 debugging process...")
    
    # Phase 1: Backend Status
    backend_ok = check_backend_status()
    
    if not backend_ok:
        print("\n❌ Cannot proceed with testing - backend is not running")
        print("\nTo start backend:")
        print("1. Open terminal in backend directory")
        print("2. Run: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Phase 2: Environment
    check_environment_config()
    
    # Phase 3: Image Proxy
    test_image_proxy_endpoint()
    
    # Phase 4: Search Endpoint
    test_search_endpoint()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUGGING SUMMARY")
    print("=" * 60)
    print("Next steps:")
    print("1. If image proxy fails → Check backend logs for errors")
    print("2. If circular references found → Check frontend URL construction")
    print("3. If no poster URLs → Check OMDB API integration") 
    print("4. If backend issues → Check environment variables and API keys")
    print("\nContinue with Phase 5-8 debugging in browser developer tools")

if __name__ == "__main__":
    main()
