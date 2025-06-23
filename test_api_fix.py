#!/usr/bin/env python3
"""
Test the API endpoint directly to verify the Unknown Title fix
"""
import requests
import json

def test_api_endpoint():
    """Test the /api/movies/search endpoint"""
    try:
        print("🔧 Testing API endpoint for Unknown Title fix...")
        
        # Test the search endpoint
        url = "http://localhost:8000/api/movies/search"
        params = {"query": "Inception", "limit": 3}
        
        print(f"\n📡 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"\n📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response data: {json.dumps(data, indent=2)}")
            
            # Check for Unknown Title issues
            if isinstance(data, list):
                print(f"\n✅ Found {len(data)} results:")
                success = True
                for i, movie in enumerate(data, 1):
                    title = movie.get('title', 'NO TITLE')
                    year = movie.get('year', 'NO YEAR') 
                    source = movie.get('source', 'unknown')
                    print(f"   {i}. '{title}' ({year}) - Source: {source}")
                    
                    if title == "Unknown Title":
                        print(f"   ❌ FOUND 'Unknown Title' in result {i}")
                        success = False
                    else:
                        print(f"   ✅ Title looks good")
                        
                if success:
                    print("\n🎉 SUCCESS: No 'Unknown Title' issues found via API!")
                    return True
                else:
                    print("\n❌ FAILED: 'Unknown Title' issues found via API")
                    return False
            else:
                print(f"❌ Unexpected response format: {type(data)}")
                return False
        else:
            print(f"❌ API returned error status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api_endpoint()
    if success:
        print("\n🎯 API ENDPOINT TEST: Unknown Title issue is FIXED!")
    else:
        print("\n⚠️ API ENDPOINT TEST: Issue may still exist")
