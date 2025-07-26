#!/usr/bin/env python3
"""
LAYER 1: INSTANT CACHE SYSTEM (0-50ms)
Azure Cosmos DB with pre-indexed searches and full-text search capability
"""
import asyncio
import logging
import time
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger(__name__)

class InstantCacheSystem:
    """
    Layer 1: Instant Cache System
    - Azure Cosmos DB for persistent storage
    - In-memory cache for ultra-fast access
    - Full-text search on movie titles
    - Pre-indexed common searches
    """
    
    def __init__(self):
        # Database configuration
        self.mongodb_uri = os.getenv("MONGODB_URI", "")
        self.db_name = "cinescope_cache"
        self.movies_collection = "instant_movies"
        self.searches_collection = "instant_searches"
        
        # In-memory cache for ultra-fast access (0-10ms)
        self.memory_cache = {}
        self.search_cache = {}
        self.cache_ttl = 3600  # 1 hour for memory cache
        
        # Connection pool
        self.client = None
        self.db = None
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.db_hits = 0
        self.db_misses = 0
        
        logger.info("🚀 Instant Cache System initialized")
    
    async def initialize(self):
        """Initialize database connections and indexes"""
        try:
            if self.mongodb_uri:
                # Connect to Azure Cosmos DB
                self.client = AsyncIOMotorClient(self.mongodb_uri)
                self.db = self.client[self.db_name]
                
                # Create collections if they don't exist
                collections = await self.db.list_collection_names()
                
                if self.movies_collection not in collections:
                    await self.db.create_collection(self.movies_collection)
                
                if self.searches_collection not in collections:
                    await self.db.create_collection(self.searches_collection)
                
                # Create indexes for fast searching
                await self._create_indexes()
                
                logger.info("✅ Connected to Azure Cosmos DB")
            else:
                logger.warning("⚠️ No MongoDB URI found, using memory-only cache")
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            # Continue with memory-only cache
    
    async def _create_indexes(self):
        """Create database indexes for fast searching"""
        try:
            movies_coll = self.db[self.movies_collection]
            searches_coll = self.db[self.searches_collection]
            
            # Movie collection indexes
            await movies_coll.create_index("imdbID", unique=True)
            await movies_coll.create_index("Title")
            await movies_coll.create_index([("Title", "text"), ("Plot", "text"), ("Genre", "text")])
            await movies_coll.create_index("cached_at")
            await movies_coll.create_index("search_popularity")
            
            # Search collection indexes
            await searches_coll.create_index("query_hash", unique=True)
            await searches_coll.create_index("query")
            await searches_coll.create_index("cached_at")
            await searches_coll.create_index("hit_count")
            
            logger.info("✅ Database indexes created")
            
        except Exception as e:
            logger.error(f"❌ Index creation failed: {e}")
    
    def _generate_cache_key(self, query: str, limit: int = 20) -> str:
        """Generate cache key for search queries"""
        normalized_query = query.lower().strip()
        return hashlib.md5(f"{normalized_query}:{limit}".encode()).hexdigest()
    
    async def get_instant_results(self, query: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Layer 1: Get instant results (0-50ms)
        1. Check memory cache (0-10ms)
        2. Check database cache (10-50ms)
        """
        start_time = time.time()
        cache_key = self._generate_cache_key(query, limit)
        
        try:
            # Step 1: Check in-memory cache (ultra-fast)
            if cache_key in self.memory_cache:
                cache_entry = self.memory_cache[cache_key]
                if (time.time() - cache_entry['timestamp']) < self.cache_ttl:
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.cache_hits += 1
                    logger.info(f"⚡ Memory cache HIT: '{query}' in {elapsed_ms:.1f}ms")
                    return cache_entry['results']
                else:
                    # Expired memory cache
                    del self.memory_cache[cache_key]
            
            # Step 2: Check database cache
            if self.db:
                db_results = await self._get_from_database(query, limit)
                if db_results:
                    # Store in memory for next time
                    self.memory_cache[cache_key] = {
                        'results': db_results,
                        'timestamp': time.time()
                    }
                    
                    elapsed_ms = (time.time() - start_time) * 1000
                    self.db_hits += 1
                    logger.info(f"💾 Database cache HIT: '{query}' in {elapsed_ms:.1f}ms")
                    return db_results
            
            # No cache hit
            elapsed_ms = (time.time() - start_time) * 1000
            self.cache_misses += 1
            logger.info(f"❌ Cache MISS: '{query}' in {elapsed_ms:.1f}ms")
            return None
            
        except Exception as e:
            logger.error(f"❌ Instant cache error: {e}")
            return None
    
    async def _get_from_database(self, query: str, limit: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results from database"""
        try:
            searches_coll = self.db[self.searches_collection]
            query_hash = self._generate_cache_key(query, limit)
            
            # Find cached search
            cached_search = await searches_coll.find_one({"query_hash": query_hash})
            
            if cached_search:
                # Check if cache is still valid (24 hours)
                cache_age = datetime.utcnow() - cached_search.get('cached_at', datetime.utcnow())
                if cache_age < timedelta(hours=24):
                    # Update hit count
                    await searches_coll.update_one(
                        {"query_hash": query_hash},
                        {"$inc": {"hit_count": 1}, "$set": {"last_accessed": datetime.utcnow()}}
                    )
                    
                    return cached_search.get('results', [])
                else:
                    # Remove expired cache
                    await searches_coll.delete_one({"query_hash": query_hash})
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Database cache error: {e}")
            return None
    
    async def cache_results(self, query: str, results: List[Dict[str, Any]], limit: int = 20):
        """
        Cache search results in both memory and database
        """
        try:
            cache_key = self._generate_cache_key(query, limit)
            
            # Cache in memory
            self.memory_cache[cache_key] = {
                'results': results,
                'timestamp': time.time()
            }
            
            # Cache in database
            if self.db and results:
                await self._cache_to_database(query, results, limit)
                
                # Also cache individual movies
                await self._cache_individual_movies(results)
                
            logger.info(f"💾 Cached {len(results)} results for '{query}'")
            
        except Exception as e:
            logger.error(f"❌ Cache storage error: {e}")
    
    async def _cache_to_database(self, query: str, results: List[Dict[str, Any]], limit: int):
        """Cache search results to database"""
        try:
            searches_coll = self.db[self.searches_collection]
            query_hash = self._generate_cache_key(query, limit)
            
            cache_doc = {
                "query_hash": query_hash,
                "query": query.lower().strip(),
                "limit": limit,
                "results": results,
                "cached_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow(),
                "hit_count": 1
            }
            
            # Upsert the cached search
            await searches_coll.replace_one(
                {"query_hash": query_hash},
                cache_doc,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Database cache storage error: {e}")
    
    async def _cache_individual_movies(self, movies: List[Dict[str, Any]]):
        """Cache individual movies for direct lookups"""
        try:
            movies_coll = self.db[self.movies_collection]
            
            for movie in movies:
                imdb_id = movie.get('imdbID')
                if imdb_id:
                    movie_doc = {
                        **movie,
                        "cached_at": datetime.utcnow(),
                        "search_popularity": 1
                    }
                    
                    # Upsert movie
                    await movies_coll.replace_one(
                        {"imdbID": imdb_id},
                        movie_doc,
                        upsert=True
                    )
                    
        except Exception as e:
            logger.error(f"❌ Individual movie caching error: {e}")
    
    async def get_movie_by_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get cached movie by IMDB ID"""
        try:
            # Check memory first
            memory_key = f"movie:{imdb_id}"
            if memory_key in self.memory_cache:
                cache_entry = self.memory_cache[memory_key]
                if (time.time() - cache_entry['timestamp']) < self.cache_ttl:
                    return cache_entry['movie']
            
            # Check database
            if self.db:
                movies_coll = self.db[self.movies_collection]
                movie = await movies_coll.find_one({"imdbID": imdb_id})
                
                if movie:
                    # Update popularity and cache in memory
                    await movies_coll.update_one(
                        {"imdbID": imdb_id},
                        {"$inc": {"search_popularity": 1}}
                    )
                    
                    self.memory_cache[memory_key] = {
                        'movie': movie,
                        'timestamp': time.time()
                    }
                    
                    return movie
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Movie lookup error: {e}")
            return None
    
    async def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular cached searches"""
        try:
            if not self.db:
                return []
                
            searches_coll = self.db[self.searches_collection]
            
            popular = await searches_coll.find(
                {},
                {"query": 1, "hit_count": 1, "cached_at": 1}
            ).sort("hit_count", -1).limit(limit).to_list(length=limit)
            
            return popular
            
        except Exception as e:
            logger.error(f"❌ Popular searches error: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses + self.db_hits + self.db_misses
        
        return {
            "memory_cache_size": len(self.memory_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "db_hits": self.db_hits,
            "db_misses": self.db_misses,
            "hit_rate": (self.cache_hits + self.db_hits) / max(total_requests, 1) * 100,
            "memory_hit_rate": self.cache_hits / max(total_requests, 1) * 100
        }
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            current_time = time.time()
            
            # Clean memory cache
            expired_keys = []
            for key, entry in self.memory_cache.items():
                if (current_time - entry['timestamp']) > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            if expired_keys:
                logger.info(f"🧹 Cleaned {len(expired_keys)} expired memory cache entries")
            
            # Clean database cache (older than 7 days)
            if self.db:
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                searches_coll = self.db[self.searches_collection]
                result = await searches_coll.delete_many({"cached_at": {"$lt": cutoff_date}})
                
                if result.deleted_count > 0:
                    logger.info(f"🧹 Cleaned {result.deleted_count} expired database cache entries")
                    
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")

# Global instance
instant_cache = InstantCacheSystem()

# Export functions
async def get_instant_search_results(query: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
    """Get instant search results from cache"""
    return await instant_cache.get_instant_results(query, limit)

async def cache_search_results(query: str, results: List[Dict[str, Any]], limit: int = 20):
    """Cache search results for instant future access"""
    await instant_cache.cache_results(query, results, limit)

async def get_cached_movie_by_id(imdb_id: str) -> Optional[Dict[str, Any]]:
    """Get cached movie by ID"""
    return await instant_cache.get_movie_by_id(imdb_id)
