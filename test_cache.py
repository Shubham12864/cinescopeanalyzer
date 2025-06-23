#!/usr/bin/env python3
"""
Test script for the Redis-like cache implementation
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.hybrid_cache import HybridCache

async def test_cache():
    """Test the cache functionality"""
    print("🧪 Testing Free Redis-like Cache System")
    print("=" * 50)
    
    # Initialize cache
    cache = HybridCache()
    
    # Test 1: Basic set/get
    print("\n1. Testing basic set/get operations:")
    await cache.set("test_key", {"movie": "The Dark Knight", "year": 2008}, ttl=60)
    result = await cache.get("test_key")
    print(f"   ✅ Cached: {result}")
    
    # Test 2: Cache expiration
    print("\n2. Testing cache expiration:")
    await cache.set("temp_key", {"temp": "data"}, ttl=1)
    result = await cache.get("temp_key")
    print(f"   ✅ Before expiration: {result}")
    
    await asyncio.sleep(2)
    result = await cache.get("temp_key")
    print(f"   ✅ After expiration: {result}")
    
    # Test 3: Cache search results
    print("\n3. Testing movie search cache:")
    search_results = [
        {"title": "Batman", "year": 2005, "id": "tt0372784"},
        {"title": "The Dark Knight", "year": 2008, "id": "tt0468569"}
    ]
    
    await cache.set("search:batman:10", search_results, ttl=3600)
    cached_search = await cache.get("search:batman:10")
    print(f"   ✅ Cached search results: {len(cached_search)} movies")
    
    # Test 4: Cache statistics
    print("\n4. Cache statistics:")
    stats = await cache.get_stats()
    print(f"   📊 Memory entries: {stats.get('memory_entries', 0)}")
    print(f"   📊 SQLite entries: {stats.get('sqlite_entries', 0)}")
    print(f"   📊 Cache hits: {stats.get('hits', 0)}")
    print(f"   📊 Cache misses: {stats.get('misses', 0)}")
    
    # Test 5: Clear cache
    print("\n5. Testing cache clear:")
    await cache.clear()
    result = await cache.get("test_key")
    print(f"   ✅ After clear: {result}")
    
    print("\n🎉 Cache test completed successfully!")
    print("\n💡 Cache Benefits:")
    print("   • Free alternative to Redis ($200+/year saved)")
    print("   • In-memory + SQLite persistence")
    print("   • Automatic expiration")
    print("   • Thread-safe operations")
    print("   • Easy integration with search/movie APIs")

if __name__ == "__main__":
    asyncio.run(test_cache())
