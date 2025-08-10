#!/usr/bin/env python3
"""
Quick Image Proxy Test - Fix HTTP 405 Issues
Test both /api/images/image-proxy and /api/movies/image-proxy endpoints
"""
import requests
import time

def test_image_proxy_endpoints():
    print("🧪 QUICK IMAGE PROXY TEST")
    print("=" * 50)
    
    # Test URLs
    test_image_url = "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
    
    endpoints = [
        "http://localhost:8000/api/images/image-proxy",
        "http://localhost:8000/api/movies/image-proxy"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        # Test GET method (correct)
        print("   GET Request:")
        try:
            response = requests.get(f"{endpoint}?url={test_image_url}", timeout=10)
            print(f"     Status: {response.status_code}")
            if response.status_code == 200:
                print(f"     Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"     Content-Length: {len(response.content)} bytes")
                print("     ✅ GET works correctly")
            else:
                print(f"     ❌ GET failed: {response.status_code}")
                print(f"     Response: {response.text[:100]}")
        except Exception as e:
            print(f"     ❌ GET error: {e}")
            
        # Test POST method (should fail with 405)
        print("   POST Request (should fail):")
        try:
            response = requests.post(f"{endpoint}?url={test_image_url}", timeout=10)
            print(f"     Status: {response.status_code}")
            if response.status_code == 405:
                print("     ✅ POST correctly returns 405 (Method Not Allowed)")
            else:
                print(f"     ⚠️  Unexpected POST response: {response.status_code}")
        except Exception as e:
            print(f"     ❌ POST error: {e}")
            
        time.sleep(1)  # Brief pause between tests

if __name__ == "__main__":
    test_image_proxy_endpoints()
