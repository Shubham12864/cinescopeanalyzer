#!/usr/bin/env python3
"""
Test script to verify dynamic content rotation in CineScope API endpoints.
Tests suggestions, trending, popular, and genre endpoints multiple times to confirm dynamic behavior.
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint_multiple_times(endpoint, name, times=3, delay=2):
    """Test an endpoint multiple times to check for dynamic content"""
    print(f"\n🎬 Testing {name} ({times} times)")
    print("=" * 50)
    
    results = []
    for i in range(times):
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    first_movie = data[0]['title'] if len(data) > 0 else "No movies"
                    count = len(data)
                    results.append((first_movie, count))
                    print(f"   Test {i+1}: ✅ {count} movies | First: {first_movie}")
                else:
                    print(f"   Test {i+1}: ❌ No data returned")
            else:
                print(f"   Test {i+1}: ❌ Status {response.status_code}")
        except Exception as e:
            print(f"   Test {i+1}: ❌ Error: {str(e)[:50]}...")
        
        if i < times - 1:  # Don't wait after the last test
            time.sleep(delay)
    
    # Check if content changed
    unique_results = set(results)
    if len(unique_results) > 1:
        print(f"   🎉 DYNAMIC: Content changed {len(unique_results)} different ways!")
    elif len(unique_results) == 1:
        print(f"   ⚠️  STATIC: Same content all {times} times (may be expected for slower rotation)")
    else:
        print(f"   ❌ FAILED: No successful results")
    
    return results

def main():
    print("🎯 CineScope Dynamic Content Test Suite")
    print(f"⏰ Testing at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Test suggestions (should change every 10 seconds)
    test_endpoint_multiple_times("/api/movies/suggestions?limit=5", "Movie Suggestions", 4, 3)
    
    # Test trending (changes every 2 hours - may not change during test)
    test_endpoint_multiple_times("/api/movies/trending?limit=5", "Trending Movies", 3, 1)
    
    # Test popular (changes every 30 minutes - may not change during test)
    test_endpoint_multiple_times("/api/movies/popular?limit=5", "Popular Movies", 3, 1)
    
    # Test genre endpoint (changes every 3 hours based on genre)
    test_endpoint_multiple_times("/api/movies/genre/action?limit=4", "Action Genre", 3, 1)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("  • Suggestions: Should change frequently (every 10 seconds)")
    print("  • Trending: Changes every 2 hours")
    print("  • Popular: Changes every 30 minutes") 
    print("  • Genre: Changes every 3 hours")
    print("  • If suggestions show different content, dynamic rotation is working! 🎉")

if __name__ == "__main__":
    main()
