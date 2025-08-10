#!/usr/bin/env python3
"""
Quick API Test - Tests all endpoints without complex dependencies
"""

import requests
import json
import sys

def test_endpoint(url, endpoint_name):
    """Test a single endpoint"""
    try:
        print(f"🔍 Testing {endpoint_name}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ {endpoint_name}: OK ({len(data)} items)")
                return True
            elif isinstance(data, dict):
                print(f"✅ {endpoint_name}: OK (dict response)")
                return True
            else:
                print(f"⚠️ {endpoint_name}: Empty response")
                return False
        else:
            print(f"❌ {endpoint_name}: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint_name}: Connection failed - server not running?")
        return False
    except Exception as e:
        print(f"❌ {endpoint_name}: Error - {e}")
        return False

def main():
    """Test all critical endpoints"""
    base_url = "http://localhost:8000"
    
    print("🎬 CineScopeAnalyzer API Test")
    print("=" * 40)
    
    # Test endpoints in order of importance
    endpoints = [
        ("/api/movies/suggestions?limit=3", "Movie Suggestions"),
        ("/api/movies/popular?limit=5", "Popular Movies"),
        ("/api/movies/top-rated?limit=5", "Top Rated Movies"),
        ("/api/movies/search?q=batman&limit=3", "Movie Search"),
        ("/docs", "API Documentation"),
        ("/health" if "/health" else "/", "Health Check")
    ]
    
    results = []
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        success = test_endpoint(url, name)
        results.append((name, success))
    
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    elif passed > 0:
        print("⚠️ Some tests failed, but basic functionality works.")
        return 1
    else:
        print("💥 All tests failed. Check if server is running.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
