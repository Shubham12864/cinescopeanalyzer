#!/usr/bin/env python3

import asyncio
import aiohttp

async def test_frontend_backend_connection():
    """Test the connection between frontend and backend"""
    
    print("🧪 Testing Frontend-Backend Connection")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health endpoint (what frontend calls)
        print("1️⃣ Testing /health endpoint...")
        try:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check: {data['status']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test 2: Suggestions endpoint (what should populate the cards)
        print("\n2️⃣ Testing /api/movies/suggestions endpoint...")
        try:
            async with session.get("http://localhost:8000/api/movies/suggestions") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Suggestions: {len(data)} movies available")
                    
                    # Show first movie details
                    if data:
                        first_movie = data[0]
                        print(f"📽️  First movie: {first_movie.get('title', 'Unknown')}")
                        print(f"🎭 Year: {first_movie.get('year', 'Unknown')}")
                        print(f"⭐ Rating: {first_movie.get('rating', 'Unknown')}")
                        print(f"🖼️  Has poster: {'Yes' if first_movie.get('poster') else 'No'}")
                else:
                    print(f"❌ Suggestions failed: {response.status}")
        except Exception as e:
            print(f"❌ Suggestions error: {e}")
        
        # Test 3: Check if frontend can fetch from itself (Next.js API routes)
        print("\n3️⃣ Testing frontend server...")
        try:
            async with session.get("http://localhost:3001") as response:
                if response.status == 200:
                    print("✅ Frontend server is running")
                else:
                    print(f"❌ Frontend server error: {response.status}")
        except Exception as e:
            print(f"❌ Frontend server error: {e}")
    
    print("\n💡 If health check passes but frontend shows empty cards:")
    print("   1. Check browser console for CORS errors")
    print("   2. Verify frontend is calling correct API endpoints")
    print("   3. Check if movies are being rendered but not visible")
    print("   4. Look for image loading issues")

if __name__ == "__main__":
    asyncio.run(test_frontend_backend_connection())
