#!/usr/bin/env python3
"""
ENHANCED BACKEND TEST
Test the new PIL-free backend with robust search
"""
import requests
import time
import json

def test_enhanced_backend():
    print("🧪 ENHANCED BACKEND TEST")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1. 🏥 Health Check:")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
            health_data = response.json()
            print(f"   📊 Version: {health_data.get('version', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend not running on localhost:8000")
        return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. 🏠 Root Endpoint:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Root endpoint working")
            root_data = response.json()
            print(f"   📝 Message: {root_data.get('message', 'N/A')}")
        else:
            print(f"   ❌ Root endpoint failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Movie search
    print("\n3. 🔍 Movie Search Test:")
    search_queries = ["batman", "inception", "marvel", "satyaars"]  # Including the query from screenshot
    
    for query in search_queries:
        print(f"\n   Testing query: '{query}'")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/api/movies/search?q={query}&limit=3", timeout=10)
            elapsed = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                movies = response.json()
                print(f"   ✅ Found {len(movies)} movies in {elapsed:.0f}ms")
                
                # Test first movie details
                if movies:
                    movie = movies[0]
                    print(f"      🎬 Title: {movie.get('title', 'N/A')}")
                    print(f"      📅 Year: {movie.get('year', 'N/A')}")
                    print(f"      ⭐ Rating: {movie.get('rating', 'N/A')}")
                    print(f"      🖼️ Poster: {movie.get('poster', 'N/A')[:60]}...")
            else:
                print(f"   ❌ Search failed: HTTP {response.status_code}")
                print(f"      Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    # Test 4: Image proxy
    print("\n4. 🖼️ Image Proxy Test:")
    test_image_url = "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
    
    try:
        response = requests.get(f"{base_url}/api/images/image-proxy?url={test_image_url}", timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', 'unknown')
            content_length = len(response.content)
            print(f"   ✅ Image proxy working: {content_type}, {content_length} bytes")
        else:
            print(f"   ❌ Image proxy failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Image proxy error: {e}")
    
    # Test 5: Quick search
    print("\n5. ⚡ Quick Search Test:")
    try:
        response = requests.get(f"{base_url}/api/movies/quick-search?q=batman&limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   ✅ Quick search: {len(results)} results")
        else:
            print(f"   ❌ Quick search failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Quick search error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 ENHANCED BACKEND TEST COMPLETED!")
    print("Ready for frontend integration")
    
    return True

if __name__ == "__main__":
    test_enhanced_backend()
