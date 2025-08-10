#!/usr/bin/env python3

import asyncio
import aiohttp
import json

async def test_frontend_api_calls():
    """Test the exact API calls the frontend should be making"""
    
    print("🧪 Testing Frontend API Integration")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health check (frontend's testConnection)
        print("1️⃣ Frontend testConnection() call...")
        try:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check successful: {data['status']}")
                    print(f"📡 Backend message: {data['message']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
        
        # Test 2: Movie suggestions (what populates the cards)
        print("\n2️⃣ Frontend getSuggestions() call...")
        try:
            async with session.get("http://localhost:8000/api/movies/suggestions?limit=12") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Suggestions endpoint: {len(data)} movies")
                    
                    # Examine first movie structure
                    if data:
                        movie = data[0]
                        print(f"\n📽️  Sample Movie Data:")
                        print(f"   ID: {movie.get('id', 'Missing')}")
                        print(f"   Title: {movie.get('title', 'Missing')}")
                        print(f"   Year: {movie.get('year', 'Missing')}")
                        print(f"   Rating: {movie.get('rating', 'Missing')}")
                        print(f"   Poster: {movie.get('poster', 'Missing')[:50]}...")
                        print(f"   Genre: {movie.get('genre', 'Missing')}")
                        print(f"   Plot: {movie.get('plot', 'Missing')[:50]}...")
                        
                        # Check required fields for frontend
                        required_fields = ['id', 'title', 'year', 'poster', 'rating', 'genre']
                        missing_fields = [field for field in required_fields if not movie.get(field)]
                        
                        if missing_fields:
                            print(f"⚠️  Missing required fields: {missing_fields}")
                        else:
                            print(f"✅ All required fields present")
                    
                    return True
                else:
                    print(f"❌ Suggestions failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Suggestions error: {e}")
            return False
        
        # Test 3: Check if all movies have valid posters
        print("\n3️⃣ Validating movie poster URLs...")
        poster_count = 0
        valid_posters = 0
        
        for movie in data:
            poster_count += 1
            poster_url = movie.get('poster')
            if poster_url and poster_url.startswith('http'):
                # Test if poster URL is accessible
                try:
                    async with session.head(poster_url) as poster_response:
                        if poster_response.status == 200:
                            valid_posters += 1
                except:
                    pass  # Poster URL not accessible
        
        print(f"📊 Poster validation: {valid_posters}/{poster_count} posters accessible")
        
        # Test 4: Check frontend's API base URL config
        print("\n4️⃣ Testing frontend configuration...")
        
        # Simulate frontend's API call structure
        frontend_api_calls = [
            "http://localhost:8000/health",
            "http://localhost:8000/api/movies/suggestions",
            "http://localhost:8000/api/movies/popular", 
            "http://localhost:8000/api/movies/trending"
        ]
        
        for endpoint in frontend_api_calls:
            try:
                async with session.get(endpoint) as response:
                    status = "✅" if response.status == 200 else "❌"
                    print(f"{status} {endpoint}: {response.status}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
    
    print(f"\n💡 Debugging Tips:")
    print(f"   - If API calls work but frontend shows empty: Check browser console")
    print(f"   - If posters fail: Check CORS/image loading policies")
    print(f"   - If connection fails: Verify NEXT_PUBLIC_API_URL in .env.local")
    print(f"   - Browser should show: 'Debug Connection' component with status")

if __name__ == "__main__":
    asyncio.run(test_frontend_api_calls())
