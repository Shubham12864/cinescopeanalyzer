#!/usr/bin/env python3
"""
Enhanced Database Caching Service
Implements comprehensive caching for search results and movie data
"""
import os
import sqlite3
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class EnhancedCacheService:
    """
    Enhanced caching service with multiple layers:
    1. Memory cache (fastest, 5-minute TTL)
    2. SQLite database cache (persistent, 1-hour TTL)
    3. Long-term storage (24-hour TTL)
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Database paths
        self.search_db_path = self.cache_dir / "search_cache.db"
        self.movie_db_path = self.cache_dir / "movie_cache.db"
        
        # Memory caches with different TTLs
        self._memory_cache: Dict[str, Dict] = {}
        self._memory_ttl = 300  # 5 minutes
        
        # Initialize databases
        self._init_search_database()
        self._init_movie_database()
        
        logger.info(f"🗄️ Enhanced cache service initialized: {self.cache_dir}")
    
    def _init_search_database(self):
        """Initialize search results cache database"""
        with sqlite3.connect(self.search_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    cache_key TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    results TEXT NOT NULL,
                    result_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    ttl_hours INTEGER DEFAULT 1
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query ON search_cache(query)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON search_cache(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON search_cache(last_accessed)")
            
            conn.commit()
    
    def _init_movie_database(self):
        """Initialize individual movie data cache database"""
        with sqlite3.connect(self.movie_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS movie_cache (
                    movie_id TEXT PRIMARY KEY,
                    imdb_id TEXT,
                    title TEXT NOT NULL,
                    movie_data TEXT NOT NULL,
                    poster_url TEXT,
                    fanart_data TEXT,
                    reddit_reviews TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    ttl_hours INTEGER DEFAULT 24
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_imdb_id ON movie_cache(imdb_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON movie_cache(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON movie_cache(created_at)")
            
            conn.commit()
    
    def _generate_cache_key(self, query: str, limit: int = 20) -> str:
        """Generate cache key for search query"""
        content = f"{query.lower().strip()}:{limit}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_expired(self, timestamp: str, ttl_hours: int) -> bool:
        """Check if cache entry is expired"""
        try:
            created = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            expiry = created + timedelta(hours=ttl_hours)
            return datetime.now() > expiry
        except:
            return True
    
    async def get_search_results(self, query: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached search results with multi-layer caching
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Cached search results or None if not found/expired
        """
        cache_key = self._generate_cache_key(query, limit)
        
        # Layer 1: Memory cache (fastest)
        if cache_key in self._memory_cache:
            cache_data = self._memory_cache[cache_key]
            if (time.time() - cache_data['timestamp']) < self._memory_ttl:
                logger.debug(f"📦 Memory cache hit for '{query}'")
                return cache_data['results']
            else:
                # Remove expired memory cache
                del self._memory_cache[cache_key]
        
        # Layer 2: Database cache
        try:
            with sqlite3.connect(self.search_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT results, created_at, ttl_hours, access_count
                    FROM search_cache 
                    WHERE cache_key = ?
                """, (cache_key,))
                
                row = cursor.fetchone()
                if row:
                    # Check if expired
                    if self._is_expired(row['created_at'], row['ttl_hours']):
                        logger.debug(f"🗑️ Expired cache entry for '{query}'")
                        return None
                    
                    # Update access statistics
                    conn.execute("""
                        UPDATE search_cache 
                        SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                        WHERE cache_key = ?
                    """, (cache_key,))
                    conn.commit()
                    
                    # Parse and return results
                    results = json.loads(row['results'])
                    
                    # Store in memory cache for faster future access
                    self._memory_cache[cache_key] = {
                        'results': results,
                        'timestamp': time.time()
                    }
                    
                    logger.info(f"💾 Database cache hit for '{query}' ({len(results)} results)")
                    return results
                    
        except Exception as e:
            logger.error(f"❌ Cache retrieval error: {e}")
        
        return None
    
    async def store_search_results(self, query: str, results: List[Dict[str, Any]], limit: int = 20, ttl_hours: int = 1):
        """
        Store search results in cache with specified TTL
        
        Args:
            query: Search query
            results: Search results to cache
            limit: Maximum number of results
            ttl_hours: Time to live in hours
        """
        cache_key = self._generate_cache_key(query, limit)
        
        # Layer 1: Store in memory cache
        self._memory_cache[cache_key] = {
            'results': results,
            'timestamp': time.time()
        }
        
        # Layer 2: Store in database cache
        try:
            with sqlite3.connect(self.search_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO search_cache 
                    (cache_key, query, results, result_count, ttl_hours, created_at, last_accessed, access_count)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                """, (
                    cache_key,
                    query,
                    json.dumps(results),
                    len(results),
                    ttl_hours
                ))
                conn.commit()
                
                logger.info(f"💾 Cached search results for '{query}' ({len(results)} results, {ttl_hours}h TTL)")
                
        except Exception as e:
            logger.error(f"❌ Cache storage error: {e}")
    
    async def get_movie_data(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached movie data
        
        Args:
            movie_id: Movie identifier
            
        Returns:
            Cached movie data or None if not found/expired
        """
        try:
            with sqlite3.connect(self.movie_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT movie_data, created_at, ttl_hours, access_count
                    FROM movie_cache 
                    WHERE movie_id = ?
                """, (movie_id,))
                
                row = cursor.fetchone()
                if row:
                    # Check if expired
                    if self._is_expired(row['created_at'], row['ttl_hours']):
                        logger.debug(f"🗑️ Expired movie cache for '{movie_id}'")
                        return None
                    
                    # Update access statistics
                    conn.execute("""
                        UPDATE movie_cache 
                        SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                        WHERE movie_id = ?
                    """, (movie_id,))
                    conn.commit()
                    
                    # Parse and return data
                    movie_data = json.loads(row['movie_data'])
                    logger.debug(f"💾 Movie cache hit for '{movie_id}'")
                    return movie_data
                    
        except Exception as e:
            logger.error(f"❌ Movie cache retrieval error: {e}")
        
        return None
    
    async def store_movie_data(self, movie_id: str, movie_data: Dict[str, Any], ttl_hours: int = 24):
        """
        Store movie data in cache
        
        Args:
            movie_id: Movie identifier
            movie_data: Movie data to cache
            ttl_hours: Time to live in hours
        """
        try:
            with sqlite3.connect(self.movie_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO movie_cache 
                    (movie_id, imdb_id, title, movie_data, poster_url, ttl_hours, created_at, last_accessed, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                """, (
                    movie_id,
                    movie_data.get('imdb_id', ''),
                    movie_data.get('title', ''),
                    json.dumps(movie_data),
                    movie_data.get('poster', ''),
                    ttl_hours
                ))
                conn.commit()
                
                logger.info(f"💾 Cached movie data for '{movie_id}' ({ttl_hours}h TTL)")
                
        except Exception as e:
            logger.error(f"❌ Movie cache storage error: {e}")
    
    def cleanup_expired_entries(self):
        """Remove expired cache entries to free up space"""
        cleaned_search = 0
        cleaned_movies = 0
        
        try:
            # Clean search cache
            with sqlite3.connect(self.search_db_path) as conn:
                cursor = conn.execute("""
                    SELECT cache_key, created_at, ttl_hours FROM search_cache
                """)
                
                expired_keys = []
                for row in cursor.fetchall():
                    if self._is_expired(row[1], row[2]):
                        expired_keys.append(row[0])
                
                if expired_keys:
                    placeholders = ','.join(['?' for _ in expired_keys])
                    conn.execute(f"DELETE FROM search_cache WHERE cache_key IN ({placeholders})", expired_keys)
                    cleaned_search = len(expired_keys)
                    conn.commit()
            
            # Clean movie cache
            with sqlite3.connect(self.movie_db_path) as conn:
                cursor = conn.execute("""
                    SELECT movie_id, created_at, ttl_hours FROM movie_cache
                """)
                
                expired_ids = []
                for row in cursor.fetchall():
                    if self._is_expired(row[1], row[2]):
                        expired_ids.append(row[0])
                
                if expired_ids:
                    placeholders = ','.join(['?' for _ in expired_ids])
                    conn.execute(f"DELETE FROM movie_cache WHERE movie_id IN ({placeholders})", expired_ids)
                    cleaned_movies = len(expired_ids)
                    conn.commit()
            
            if cleaned_search or cleaned_movies:
                logger.info(f"🧹 Cleaned {cleaned_search} search entries, {cleaned_movies} movie entries")
                
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'memory_cache_size': len(self._memory_cache),
            'search_db_entries': 0,
            'movie_db_entries': 0,
            'total_access_count': 0
        }
        
        try:
            # Search cache stats
            with sqlite3.connect(self.search_db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*), SUM(access_count) FROM search_cache")
                row = cursor.fetchone()
                stats['search_db_entries'] = row[0] or 0
                stats['total_access_count'] += row[1] or 0
            
            # Movie cache stats
            with sqlite3.connect(self.movie_db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*), SUM(access_count) FROM movie_cache")
                row = cursor.fetchone()
                stats['movie_db_entries'] = row[0] or 0
                stats['total_access_count'] += row[1] or 0
                
        except Exception as e:
            logger.error(f"❌ Cache stats error: {e}")
        
        return stats

# Global instance
enhanced_cache_service = EnhancedCacheService()
