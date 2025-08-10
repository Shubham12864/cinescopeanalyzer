#!/usr/bin/env python3

import asyncio
import aiohttp

async def test_manual_api_call():
    """Manually test what the frontend should be doing"""
    
    print("🧪 Manual Frontend API Test")
    print("=" * 40)
    
    # Test EXACTLY what the frontend should call
    api_calls = [
        ("Health Check", "http://localhost:8000/health"),
        ("Suggestions", "http://localhost:8000/api/movies/suggestions?limit=12"),
        ("Popular", "http://localhost:8000/api/movies/popular"),
        ("Frontend CORS Test", "http://localhost:8000/health", {
            'Origin': 'http://localhost:3001',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        })
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url, *headers in api_calls:
            try:
                request_headers = headers[0] if headers else {}
                async with session.get(url, headers=request_headers) as response:
                    print(f"🔗 {name}: {response.status}")
                    if response.status == 200:
                        if 'suggestions' in url or 'popular' in url:
                            data = await response.json()
                            print(f"   📊 Data: {len(data)} items")
                        else:
                            data = await response.json()
                            print(f"   📊 Response: {data.get('status', 'unknown')}")
                    else:
                        print(f"   ❌ Error: {response.status}")
            except Exception as e:
                print(f"❌ {name}: {e}")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Check browser DevTools Network tab")
    print(f"   2. Look for JavaScript console errors")
    print(f"   3. Verify CORS headers are working")
    print(f"   4. Check if frontend is calling wrong endpoints")

if __name__ == "__main__":
    asyncio.run(test_manual_api_call())
