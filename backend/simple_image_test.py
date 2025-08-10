#!/usr/bin/env python3
"""
Simple Image Fix Test - Verify single /api/images/image-proxy endpoint
"""
import requests
import sys

def test_single_image_proxy():
    print("🧪 SIMPLE IMAGE FIX TEST")
    print("=" * 40)
    
    # Test the fixed single endpoint
    endpoint = "http://localhost:8000/api/images/image-proxy"
    test_url = "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
    
    print(f"🔍 Testing: {endpoint}")
    print(f"🖼️  Image: {test_url[:60]}...")
    
    try:
        response = requests.get(f"{endpoint}?url={test_url}", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', 'unknown')
            content_length = len(response.content)
            print(f"✅ SUCCESS! Content-Type: {content_type}, Size: {content_length} bytes")
            return True
        else:
            print(f"❌ FAILED! HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_single_image_proxy()
    sys.exit(0 if success else 1)
