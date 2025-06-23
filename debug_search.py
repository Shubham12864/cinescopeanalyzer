#!/usr/bin/env python3
"""
Debug search endpoint response
"""

import requests
import json

def debug_search():
    """Debug a single search to see what's being returned"""
    try:
        url = "http://localhost:8000/api/movies/search"
        params = {"q": "Dune"}
        
        print(f"🔍 Testing URL: {url}")
        print(f"🔍 Params: {params}")
        
        response = requests.get(url, params=params, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {response.headers}")
        print(f"📊 Raw Response Length: {len(response.text)}")
        print(f"📊 Raw Response (first 500 chars):")
        print(response.text[:500])
        print("\n" + "="*50)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Parsed JSON Type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"📊 List Length: {len(data)}")
                    if data:
                        print(f"📊 First Item Type: {type(data[0])}")
                        print(f"📊 First Item Keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                        print(f"📊 First Item: {json.dumps(data[0], indent=2)}")
                        
                        # Check for title field
                        first_item = data[0]
                        if isinstance(first_item, dict):
                            title = first_item.get('title', 'NOT FOUND')
                            print(f"📊 Title Field: '{title}'")
                            
                            # Check all keys
                            print(f"📊 All Keys: {list(first_item.keys())}")
                            
                elif isinstance(data, dict):
                    print(f"📊 Dict Keys: {list(data.keys())}")
                    print(f"📊 Full Response: {json.dumps(data, indent=2)}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    debug_search()
