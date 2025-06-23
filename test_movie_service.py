#!/usr/bin/env python3
"""
MovieService Direct Test
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.movie_service import MovieService

async def test_movie_service():
    print("🔧 Testing MovieService directly...")
    service = MovieService()
    
    print("🔍 Searching for 'Dune'...")
    results = await service.search_movies("Dune", 3)
    
    print(f"📊 Found {len(results)} results:")
    for i, movie in enumerate(results, 1):
        print(f"   {i}. Title: '{movie.title}'")
        print(f"      Year: {movie.year}")
        print(f"      ID: {movie.id}")
        print()
    
    # Check for Unknown Title
    unknown_count = sum(1 for movie in results if movie.title == "Unknown Title")
    
    if unknown_count == 0:
        print("✅ SUCCESS: No 'Unknown Title' found!")
        return True
    else:
        print(f"❌ FAILURE: Found {unknown_count} 'Unknown Title' results!")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_movie_service())
    print(f"\nTest result: {'✅ PASSED' if success else '❌ FAILED'}")
