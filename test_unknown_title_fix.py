#!/usr/bin/env python3
"""
Test script to debug the "Unknown Title" issue
This will test the entire search flow and identify where the problem occurs
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.core.api_manager import APIManager
from app.core.omdb_api_enhanced import OMDbAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_omdb_api_directly():
    """Test OMDB API directly"""
    print("\n" + "="*50)
    print("🔍 TESTING OMDB API DIRECTLY")
    print("="*50)
    
    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OMDB_API_KEY")
    print(f"🔑 API Key: {api_key}")
    
    omdb = OMDbAPI(api_key)
    
    # Test search
    print("\n🔍 Testing search for 'Batman'...")
    results = await omdb.search_movies("Batman", limit=3)
    
    print(f"📊 Results count: {len(results)}")
    for i, movie in enumerate(results):
        print(f"\n🎬 Movie {i+1}:")
        print(f"   ID: {movie.get('id')}")
        print(f"   Title: {movie.get('title')}")
        print(f"   Year: {movie.get('year')}")
        print(f"   Source: {movie.get('source')}")
        print(f"   Rating: {movie.get('rating')}")
    
    return results

async def test_api_manager():
    """Test API Manager search"""
    print("\n" + "="*50)
    print("🔍 TESTING API MANAGER SEARCH")
    print("="*50)
    
    api_manager = APIManager()
    
    # Test search
    print("\n🔍 Testing search for 'Inception'...")
    results = await api_manager.search_movies("Inception", limit=3)
    
    print(f"📊 Results count: {len(results)}")
    for i, movie in enumerate(results):
        print(f"\n🎬 Movie {i+1}:")
        print(f"   ID: {movie.get('id')}")
        print(f"   Title: {movie.get('title')}")
        print(f"   Year: {movie.get('year')}")
        print(f"   Source: {movie.get('source')}")
        print(f"   Rating: {movie.get('rating')}")
        print(f"   Genre: {movie.get('genre')}")
    
    return results

async def test_specific_movie():
    """Test getting a specific movie by ID"""
    print("\n" + "="*50)
    print("🔍 TESTING SPECIFIC MOVIE BY ID")
    print("="*50)
    
    api_manager = APIManager()
      # Test getting a specific movie
    print("\n🎬 Testing get movie by ID 'tt1375666' (Inception)...")
    movie = await api_manager.get_movie_by_id("tt1375666")
    
    if movie:
        print(f"\n🎬 Movie Details:")
        print(f"   ID: {movie.get('id')}")
        print(f"   Title: {movie.get('title')}")
        print(f"   Year: {movie.get('year')}")
        print(f"   Plot: {movie.get('plot')[:100]}...")
        print(f"   Source: {movie.get('source')}")
        print(f"   Rating: {movie.get('rating')}")
        print(f"   Director: {movie.get('director')}")
        print(f"   Cast: {movie.get('cast')[:3]}")
    else:
        print("❌ No movie found")
    
    return movie

async def main():
    """Run all tests"""
    print("🚀 STARTING UNKNOWN TITLE DEBUG TEST")
    print("This will test the entire search pipeline to identify issues")
    
    try:
        # Test 1: OMDB API directly
        omdb_results = await test_omdb_api_directly()
        
        # Test 2: API Manager search
        manager_results = await test_api_manager()
        
        # Test 3: Specific movie
        specific_movie = await test_specific_movie()
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        print(f"✅ OMDB Direct Results: {len(omdb_results)}")
        unknown_titles_omdb = [m for m in omdb_results if m.get('title') == 'Unknown Title']
        print(f"❌ OMDB Unknown Titles: {len(unknown_titles_omdb)}")
        
        print(f"✅ API Manager Results: {len(manager_results)}")
        unknown_titles_manager = [m for m in manager_results if m.get('title') == 'Unknown Title']
        print(f"❌ Manager Unknown Titles: {len(unknown_titles_manager)}")
        
        print(f"✅ Specific Movie: {'Found' if specific_movie else 'Not Found'}")
        if specific_movie and specific_movie.get('title') == 'Unknown Title':
            print("❌ Specific Movie has Unknown Title")
        
        # Identify the issue
        print("\n🔍 ISSUE ANALYSIS:")
        if len(unknown_titles_omdb) > 0:
            print("❌ Issue is in OMDB API conversion")
        elif len(unknown_titles_manager) > 0:
            print("❌ Issue is in API Manager conversion")
        elif not specific_movie:
            print("❌ Issue is in movie details retrieval")
        else:
            print("✅ No Unknown Title issues found!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
