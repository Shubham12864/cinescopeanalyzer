#!/usr/bin/env python3
"""
Quick test of the OMDB service and movie routes
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_omdb_service():
    """Test the OMDB service directly"""
    try:
        from app.services.omdb_service import omdb_service
        
        print("Testing OMDB Service...")
        print(f"API Key: {omdb_service.api_key[:4]}****")
        
        # Test search
        print("\n🔍 Testing search for 'batman'...")
        results = await omdb_service.search_movies("batman", 3)
        
        if results:
            print(f"✅ Found {len(results)} movies:")
            for movie in results:
                print(f"  - {movie.get('Title', 'N/A')} ({movie.get('Year', 'N/A')})")
        else:
            print("❌ No results found")
            
        # Test movie by ID
        if results:
            first_movie = results[0]
            movie_id = first_movie.get('imdbID')
            if movie_id:
                print(f"\n🎬 Testing movie details for ID: {movie_id}")
                details = await omdb_service.get_movie_by_id(movie_id)
                if details:
                    print(f"✅ Movie details: {details.get('Title')} - {details.get('Plot', 'No plot')[:100]}...")
                else:
                    print("❌ Failed to get movie details")
        
        await omdb_service.close()
        print("\n✅ OMDB Service test completed successfully!")
        
    except Exception as e:
        print(f"❌ OMDB Service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_omdb_service())
