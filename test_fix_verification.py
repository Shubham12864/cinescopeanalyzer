#!/usr/bin/env python3
"""
Simple test to verify the Unknown Title fix
"""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_search_fix():
    """Test that search returns proper titles"""
    try:
        from backend.app.core.api_manager import APIManager
        
        print("🔧 Testing Unknown Title fix...")
        
        # Initialize API manager
        api_manager = APIManager()
        
        # Test search for a well-known movie
        print("\n📽️ Testing search for 'The Matrix'...")
        results = await api_manager.search_movies("The Matrix", limit=3)
        
        print(f"\n✅ Found {len(results)} results:")
        for i, movie in enumerate(results[:3], 1):
            title = movie.get('title', 'NO TITLE')
            year = movie.get('year', 'NO YEAR')
            source = movie.get('source', 'unknown')
            print(f"   {i}. {title} ({year}) - Source: {source}")
            
            # Check for "Unknown Title" issue
            if title == "Unknown Title":
                print(f"   ❌ Found 'Unknown Title' issue in result {i}")
                return False
                
        print("\n✅ No 'Unknown Title' issues found!")
        
        # Test movie details
        if results:
            movie_id = results[0].get('id') or results[0].get('imdbId')
            if movie_id:                print(f"\n📖 Testing movie details for ID: {movie_id}")
                details = await api_manager.get_movie_by_id(movie_id)
                if details:
                    detail_title = details.get('title', 'NO TITLE')
                    print(f"   Title: {detail_title}")
                    if detail_title == "Unknown Title":
                        print("   ❌ Found 'Unknown Title' in movie details")
                        return False
                else:
                    print("   ⚠️ No details returned")
        
        print("\n🎉 All tests passed! Unknown Title issue appears to be fixed.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_search_fix())
    if success:
        print("\n✅ VERIFICATION COMPLETE: Fix appears successful!")
    else:
        print("\n❌ VERIFICATION FAILED: Issue still exists")
