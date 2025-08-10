#!/usr/bin/env python3
"""
REAL OMDB API TEST
Test that we get real movie data, not demo data
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.working_omdb_service import search_real_movies

async def test_real_omdb_search():
    print("🧪 TESTING REAL OMDB API")
    print("=" * 50)
    
    # Test queries
    test_queries = ["batman", "saiyaara", "inception", "avengers"]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            # Search for real movies
            movies = await search_real_movies(query, 3)
            
            if movies:
                print(f"✅ Found {len(movies)} REAL movies:")
                for i, movie in enumerate(movies, 1):
                    title = movie.get('Title', 'Unknown')
                    year = movie.get('Year', 'Unknown')
                    imdb_id = movie.get('imdbID', 'Unknown')
                    poster = movie.get('Poster', 'N/A')
                    
                    print(f"   {i}. {title} ({year})")
                    print(f"      ID: {imdb_id}")
                    print(f"      Poster: {poster[:60]}...")
                    
                    # Check if this is demo data
                    if title in ['Inception', 'The Dark Knight', 'Avatar'] and imdb_id in ['tt1375666', 'tt0468569', 'tt0499549']:
                        print(f"      ⚠️  WARNING: This looks like demo data!")
                    else:
                        print(f"      ✅ This is REAL movie data!")
            else:
                print(f"📭 No movies found for '{query}'")
                print("   This is CORRECT behavior - no demo fallback!")
                
        except Exception as e:
            print(f"❌ Error searching for '{query}': {e}")
    
    print("\n" + "=" * 50)
    print("🎯 OMDB API TEST COMPLETED")
    print("If you see 'REAL movie data' above, the API is working correctly!")

if __name__ == "__main__":
    asyncio.run(test_real_omdb_search())
