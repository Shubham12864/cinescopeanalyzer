import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.core.api_manager import APIManager

async def test_search():
    api = APIManager()
    print("🔍 Testing search with Scrapy integration...")
    
    results = await api.search_movies("inception", limit=3)
    print(f"✅ Found {len(results)} movies")
    
    for movie in results:
        print(f"- {movie.get('title')} ({movie.get('year')}) - Source: {movie.get('source')}")

if __name__ == "__main__":
    asyncio.run(test_search())
