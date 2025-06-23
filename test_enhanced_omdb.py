#!/usr/bin/env python3
"""
Test Enhanced OMDB API directly
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.omdb_api_enhanced import OMDbAPI
from dotenv import load_dotenv

async def test_enhanced_omdb():
    load_dotenv('backend/.env')
    api_key = os.getenv('OMDB_API_KEY')
    
    print(f"🔑 API Key: {api_key}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    omdb = OMDbAPI(api_key)
    
    try:
        print("🔍 Testing enhanced OMDB API search...")
        results = await omdb.search_movies("Dune", 5)
        
        print(f"📊 Results count: {len(results)}")
        
        for i, movie in enumerate(results):
            print(f"\n🎬 Movie {i+1}:")
            print(f"   Title: {movie.get('title', 'NOT FOUND')}")
            print(f"   Year: {movie.get('year', 'NOT FOUND')}")
            print(f"   Type: {type(movie)}")
            print(f"   All Keys: {list(movie.keys()) if isinstance(movie, dict) else 'Not a dict'}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_omdb())
