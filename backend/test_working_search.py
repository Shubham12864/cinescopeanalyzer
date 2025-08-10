#!/usr/bin/env python3
"""
TEST WORKING SEARCH SERVICE
Verify that search returns real data, not demo data
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.working_search_service import search_real_movies_only

async def test_working_search():
    print("🧪 TESTING WORKING SEARCH SERVICE")
    print("=" * 50)
    
    # Test queries including the problematic one from screenshot
    test_queries = ["batman", "saiyaara", "inception", "unknown movie xyz"]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 30)
        
        try:
            movies = await search_real_movies_only(query, 3)
            
            if movies:
                print(f"✅ Found {len(movies)} results:")
                for i, movie in enumerate(movies, 1):
                    title = movie.get('Title', 'Unknown')
                    year = movie.get('Year', 'Unknown')
                    imdb_id = movie.get('imdbID', 'Unknown')
                    
                    print(f"   {i}. {title} ({year}) - {imdb_id}")
                    
                    # Check if this is the problematic demo data
                    demo_titles = ['Inception', 'The Dark Knight', 'Avatar']
                    demo_ids = ['tt1375666', 'tt0468569', 'tt0499549']
                    
                    if title in demo_titles and imdb_id in demo_ids:
                        print(f"      ❌ WARNING: This is DEMO DATA! Should not appear!")
                    else:
                        print(f"      ✅ Real movie data")
            else:
                print(f"📭 No results found")
                print(f"   ✅ Correctly returns empty for '{query}' (no demo fallback)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 SEARCH TEST COMPLETED")
    print("✅ If no 'DEMO DATA' warnings above, the fix is working!")

if __name__ == "__main__":
    asyncio.run(test_working_search())
