#!/usr/bin/env python3
"""
Test script for Scrapy search service integration
Tests the new search fallback system with Scrapy
"""
import asyncio
import sys
import os
import logging

# Add backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.scrapy_search_service import ScrapySearchService
from backend.app.core.api_manager import APIManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_scrapy_search():
    """Test Scrapy search service directly"""
    print("🕷️ Testing Scrapy Search Service")
    print("=" * 50)
    
    scrapy_service = ScrapySearchService()
    
    test_queries = [
        "inception",
        "batman",
        "avengers"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            results = await scrapy_service.search_movies(query, limit=3)
            print(f"✅ Found {len(results)} movies")
            
            for i, movie in enumerate(results[:2], 1):
                print(f"  {i}. {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
                print(f"     Rating: {movie.get('rating', 'N/A')}/10")
                print(f"     Plot: {movie.get('plot', 'No plot')[:100]}...")
                print(f"     Source: {movie.get('source', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🕷️ Testing individual movie lookup")
    try:
        movie = await scrapy_service.get_movie_by_id("tt1375666")  # Inception
        if movie:
            print(f"✅ Found movie: {movie.get('title', 'Unknown')}")
            print(f"   Plot: {movie.get('plot', 'No plot')[:150]}...")
        else:
            print("❌ No movie found")
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_api_manager_integration():
    """Test API manager with Scrapy integration"""
    print("\n🎯 Testing API Manager with Scrapy Integration")
    print("=" * 50)
    
    api_manager = APIManager()
    
    test_queries = [
        "interstellar",
        "matrix",
        "pulp fiction"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing integrated search: '{query}'")
        try:
            results = await api_manager.search_movies(query, limit=3)
            print(f"✅ Found {len(results)} movies")
            
            for i, movie in enumerate(results[:2], 1):
                print(f"  {i}. {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
                print(f"     Source: {movie.get('source', 'Unknown')}")
                print(f"     Rating: {movie.get('rating', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_search_priority():
    """Test search priority system"""
    print("\n🏆 Testing Search Priority System")
    print("=" * 50)
    
    api_manager = APIManager()
    
    # Test with a specific query to see priority order
    query = "the godfather"
    print(f"🔍 Testing priority for: '{query}'")
    
    try:
        results = await api_manager.search_movies(query, limit=5)
        print(f"✅ Final results: {len(results)} movies")
        
        for i, movie in enumerate(results, 1):
            source = movie.get('source', 'Unknown')
            title = movie.get('title', 'Unknown')
            year = movie.get('year', 'N/A')
            print(f"  {i}. {title} ({year}) - Source: {source}")
        
        # Test caching
        print(f"\n🔄 Testing cache (second search for '{query}')")
        cached_results = await api_manager.search_movies(query, limit=5)
        print(f"✅ Cached results: {len(cached_results)} movies")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run all tests"""
    print("🎬 CineScopeAnalyzer - Scrapy Search Integration Test")
    print("=" * 60)
    
    try:
        # Test Scrapy service directly
        await test_scrapy_search()
        
        # Test API manager integration
        await test_api_manager_integration()
        
        # Test search priority
        await test_search_priority()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
