#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
"""

import requests
import json
import time

def test_api_endpoint(url, name):
    """Test a single API endpoint"""
    try:
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS: {len(data)} items returned")
            
            # Show first item details if available
            if data and len(data) > 0:
                first_item = data[0]
                print(f"   📽️  Sample: {first_item.get('title', 'N/A')} ({first_item.get('year', 'N/A')})")
                print(f"   🖼️  Poster: {first_item.get('poster', 'N/A')[:50]}...")
                print(f"   ⭐ Rating: {first_item.get('rating', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🎬 CineScope API Test Suite")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("/api/movies", "All Movies"),
        ("/api/movies/trending", "Trending Movies"),
        ("/api/movies/popular", "Popular Movies"),
        ("/api/movies/suggestions", "Movie Suggestions"),
        ("/api/movies/search?q=spider", "Search Movies"),
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        success = test_api_endpoint(url, name)
        results.append((name, success))
        time.sleep(1)  # Be nice to the server
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints need attention.")

if __name__ == "__main__":
    main()
