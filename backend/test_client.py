#!/usr/bin/env python3
"""
Test client to verify the API endpoints work correctly
"""
import requests
import json
import time

def test_endpoint(url, endpoint_name):
    """Test a single endpoint"""
    try:
        print(f"\n🔍 Testing {endpoint_name}...")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Success: Returned {len(data)} items")
                if data:
                    print(f"   📝 Sample: {data[0].get('title', 'N/A')} ({data[0].get('year', 'N/A')})")
            elif isinstance(data, dict):
                print(f"   ✅ Success: {data}")
            else:
                print(f"   ✅ Success: {type(data)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error details: {error_data}")
            except:
                print(f"   📝 Error text: {response.text[:200]}...")
                
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - is the server running?")
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

def main():
    """Test all endpoints"""
    base_url = "http://localhost:8000"
    
    print("🎬 CineScope Backend API Tester")
    print("=" * 50)
    print(f"🌐 Base URL: {base_url}")
    print(f"⏰ Testing started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test endpoints
    endpoints = [
        ("/", "Root Endpoint"),
        ("/api/movies/health", "Health Check"),
        ("/api/movies/popular", "Popular Movies"),
        ("/api/movies/recent", "Recent Movies"),
        ("/api/movies/top-rated", "Top Rated Movies"),
        ("/api/movies/suggestions", "Movie Suggestions")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        test_endpoint(url, name)
        time.sleep(1)  # Brief pause between requests
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")
    print("\n💡 If you see connection errors, make sure to:")
    print("   1. Start the backend server first")
    print("   2. Wait for it to fully initialize")
    print("   3. Check if port 8000 is available")

if __name__ == "__main__":
    main()
