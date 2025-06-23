import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.scrapy_search_service import ScrapySearchService

async def simple_test():
    print("🕷️ Simple Scrapy Test")
    service = ScrapySearchService()
    
    try:
        # Test one quick search
        results = await service.search_movies("matrix", limit=2)
        print(f"✅ Found {len(results)} movies")
        
        for movie in results:
            print(f"- {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
            print(f"  Source: {movie.get('source', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())
