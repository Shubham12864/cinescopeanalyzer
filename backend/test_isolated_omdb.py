#!/usr/bin/env python3
"""
Test OMDB Service in complete isolation
"""
import asyncio
import aiohttp
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IsolatedOMDBService:
    def __init__(self):
        self.api_key = "4977b044"  # Your working API key
        self.base_url = "http://www.omdbapi.com/"
        self.session = None
        logger.info(f"✅ OMDB Service initialized with key: {self.api_key[:4]}****")
    
    async def get_session(self):
        """Get or create HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session
    
    async def search_movies(self, query: str, limit: int = 10):
        """Search for movies using OMDB API"""
        try:
            session = await self.get_session()
            
            params = {
                "apikey": self.api_key,
                "s": query,
                "type": "movie",
                "page": 1
            }
            
            logger.info(f"🔍 Searching for: '{query}'")
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("Response") == "True" and "Search" in data:
                        movies = data["Search"][:limit]
                        logger.info(f"✅ Found {len(movies)} movies for '{query}'")
                        
                        return [
                            {
                                "id": movie.get("imdbID"),
                                "title": movie.get("Title"),
                                "year": movie.get("Year"),
                                "poster": movie.get("Poster", "https://via.placeholder.com/300x450?text=No+Image")
                            }
                            for movie in movies
                        ]
                    else:
                        logger.warning(f"⚠️ No results for '{query}': {data.get('Error', 'Unknown error')}")
                        return []
                else:
                    logger.error(f"❌ API request failed with status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Search failed for '{query}': {e}")
            return []
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

async def test_omdb_service():
    """Test the OMDB service with various queries"""
    print("🎬 Testing OMDB Service in Isolation")
    print("=" * 50)
    
    service = IsolatedOMDBService()
    
    test_queries = ["batman", "avengers", "star wars", "marvel", "superman"]
    
    try:
        for query in test_queries[:3]:  # Test first 3 queries
            print(f"\n🔍 Testing query: '{query}'")
            results = await service.search_movies(query, 3)
            
            if results:
                print(f"✅ Found {len(results)} movies:")
                for movie in results:
                    print(f"   - {movie['title']} ({movie['year']}) - {movie['id']}")
            else:
                print(f"❌ No results found for '{query}'")
                
    finally:
        await service.close()
        print("\n✨ OMDB service test completed!")

# Test if we can simulate the popular endpoint
async def test_popular_endpoint_logic():
    """Test the popular endpoint logic"""
    print("\n🌟 Testing Popular Endpoint Logic")
    print("=" * 50)
    
    service = IsolatedOMDBService()
    
    try:
        # Same logic as in the popular endpoint
        popular_queries = ["avengers", "batman", "star wars", "marvel", "superman"]
        all_movies = []
        
        for query in popular_queries[:3]:  # Limit to avoid rate limits
            try:
                results = await service.search_movies(query, 5)
                if results:
                    all_movies.extend(results[:3])  # Take top 3 from each query
            except Exception as e:
                logger.warning(f"Popular search failed for '{query}': {e}")
                continue
        
        # Remove duplicates by id
        seen_ids = set()
        unique_movies = []
        for movie in all_movies:
            if movie['id'] not in seen_ids:
                unique_movies.append(movie)
                seen_ids.add(movie['id'])
        
        print(f"✅ Popular endpoint would return {len(unique_movies)} unique movies:")
        for movie in unique_movies[:5]:  # Show first 5
            print(f"   - {movie['title']} ({movie['year']})")
            
        return unique_movies
        
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(test_omdb_service())
    asyncio.run(test_popular_endpoint_logic())
