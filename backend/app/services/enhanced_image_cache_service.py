"""
Enhanced Image Cache Service with Redis/SQLite support and cache warming
"""
import os
import hashlib
import sqlite3
import aiofiles
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancedImageCacheService:
    """Enhanced image caching with multiple storage backends and cache warming"""
    
    def __init__(self):
        self.cache_dir = Path("./cache/images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage backends
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.redis_client = None
        self.sqlite_db_path = self.cache_dir / "image_cache.db"
        self._initialized = False
        
        # Cache configuration
        self.default_ttl = 24 * 60 * 60  # 24 hours
        self.memory_cache_limit = 100  # Maximum items in memory cache
        self.popular_movies_cache_ttl = 7 * 24 * 60 * 60  # 7 days for popular movies
    
    async def _ensure_initialized(self):
        """Ensure the cache service is initialized"""
        if not self._initialized:
            await self._initialize_backends()
            self._initialized = True
    
    async def _initialize_backends(self):
        """Initialize Redis and SQLite backends"""
        try:
            # Try to connect to Redis if available
            if REDIS_AVAILABLE:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.ping
                )
                logger.info("✅ Redis cache backend initialized")
        except Exception as e:
            logger.warning(f"Redis not available, using SQLite only: {e}")
            self.redis_client = None
        
        # Initialize SQLite
        await self._init_sqlite()
    
    async def _init_sqlite(self):
        """Initialize SQLite cache database"""
        try:
            def create_tables():
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS image_cache (
                        cache_key TEXT PRIMARY KEY,
                        content_type TEXT,
                        file_path TEXT,
                        url TEXT,
                        size TEXT,
                        created_at TIMESTAMP,
                        expires_at TIMESTAMP,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expires_at ON image_cache(expires_at)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_size ON image_cache(url, size)
                """)
                conn.commit()
                conn.close()
            
            await asyncio.get_event_loop().run_in_executor(None, create_tables)
            logger.info("✅ SQLite cache backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite cache: {e}")
    
    def _generate_cache_key(self, url: str, size: Optional[str] = None) -> str:
        """Generate cache key for URL and size"""
        key_data = f"{url}_{size or 'default'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_cached_image(self, url: str, size: Optional[str] = None) -> Optional[bytes]:
        """Get cached image data from any available backend"""
        await self._ensure_initialized()
        
        cache_key = self._generate_cache_key(url, size)
        
        # Try memory cache first (fastest)
        if cache_key in self.memory_cache:
            cache_entry = self.memory_cache[cache_key]
            if datetime.now().timestamp() < cache_entry.get('expires_at', 0):
                logger.debug(f"🚀 Memory cache HIT: {url}")
                return cache_entry.get('data')
            else:
                # Remove expired entry
                del self.memory_cache[cache_key]
        
        # Try Redis cache
        if self.redis_client:
            try:
                redis_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.get, f"img:{cache_key}"
                )
                if redis_data:
                    logger.debug(f"⚡ Redis cache HIT: {url}")
                    # Also cache in memory for even faster access
                    self._cache_in_memory(cache_key, redis_data, "image/jpeg")
                    return redis_data
            except Exception as e:
                logger.debug(f"Redis cache error: {e}")
        
        # Try SQLite/disk cache
        return await self._get_from_sqlite_cache(cache_key, url)
    
    async def _get_from_sqlite_cache(self, cache_key: str, url: str) -> Optional[bytes]:
        """Get image from SQLite/disk cache"""
        try:
            def get_cache_entry():
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT file_path, expires_at, content_type 
                    FROM image_cache 
                    WHERE cache_key = ? AND expires_at > ?
                """, (cache_key, datetime.now().timestamp()))
                result = cursor.fetchone()
                
                if result:
                    # Update access statistics
                    cursor.execute("""
                        UPDATE image_cache 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE cache_key = ?
                    """, (datetime.now().timestamp(), cache_key))
                    conn.commit()
                
                conn.close()
                return result
            
            cache_entry = await asyncio.get_event_loop().run_in_executor(
                None, get_cache_entry
            )
            
            if cache_entry:
                file_path, expires_at, content_type = cache_entry
                file_path = Path(file_path)
                
                if file_path.exists():
                    async with aiofiles.open(file_path, 'rb') as f:
                        image_data = await f.read()
                    
                    logger.debug(f"💾 SQLite cache HIT: {url}")
                    
                    # Cache in memory and Redis for faster future access
                    self._cache_in_memory(cache_key, image_data, content_type)
                    await self._cache_in_redis(cache_key, image_data)
                    
                    return image_data
                else:
                    # File missing, remove from database
                    await self._remove_from_sqlite_cache(cache_key)
        
        except Exception as e:
            logger.debug(f"SQLite cache error: {e}")
        
        return None
    
    async def cache_image(self, url: str, image_data: bytes, content_type: str, 
                         size: Optional[str] = None, ttl: Optional[int] = None) -> bool:
        """Cache image data in all available backends"""
        if not image_data:
            return False
        
        await self._ensure_initialized()
        
        cache_key = self._generate_cache_key(url, size)
        ttl = ttl or self.default_ttl
        expires_at = datetime.now().timestamp() + ttl
        
        # Cache in memory
        self._cache_in_memory(cache_key, image_data, content_type, expires_at)
        
        # Cache in Redis
        await self._cache_in_redis(cache_key, image_data, ttl)
        
        # Cache in SQLite/disk
        await self._cache_in_sqlite(cache_key, url, image_data, content_type, size, expires_at)
        
        logger.debug(f"💾 Cached image: {url} (size: {len(image_data)} bytes)")
        return True
    
    def _cache_in_memory(self, cache_key: str, image_data: bytes, content_type: str, 
                        expires_at: Optional[float] = None):
        """Cache image in memory"""
        if len(image_data) > 2 * 1024 * 1024:  # Don't cache large images (>2MB) in memory
            return
        
        expires_at = expires_at or (datetime.now().timestamp() + self.default_ttl)
        
        self.memory_cache[cache_key] = {
            'data': image_data,
            'content_type': content_type,
            'expires_at': expires_at
        }
        
        # Cleanup old entries if memory cache is full
        if len(self.memory_cache) > self.memory_cache_limit:
            # Remove oldest entries
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get('expires_at', 0)
            )
            for old_key, _ in sorted_items[:10]:  # Remove 10 oldest
                del self.memory_cache[old_key]
    
    async def _cache_in_redis(self, cache_key: str, image_data: bytes, ttl: Optional[int] = None):
        """Cache image in Redis"""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.default_ttl
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.setex, f"img:{cache_key}", ttl, image_data
            )
        except Exception as e:
            logger.debug(f"Redis cache error: {e}")
    
    async def _cache_in_sqlite(self, cache_key: str, url: str, image_data: bytes, 
                              content_type: str, size: Optional[str], expires_at: float):
        """Cache image in SQLite/disk"""
        try:
            # Save image file to disk
            size_dir = self.cache_dir / (size or "default")
            size_dir.mkdir(exist_ok=True)
            
            file_path = size_dir / f"{cache_key}.cache"
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_data)
            
            # Save metadata to SQLite
            def save_metadata():
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO image_cache 
                    (cache_key, content_type, file_path, url, size, created_at, expires_at, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                """, (cache_key, content_type, str(file_path), url, size or "default", 
                     datetime.now().timestamp(), expires_at, datetime.now().timestamp()))
                conn.commit()
                conn.close()
            
            await asyncio.get_event_loop().run_in_executor(None, save_metadata)
            
        except Exception as e:
            logger.error(f"SQLite cache error: {e}")
    
    async def _remove_from_sqlite_cache(self, cache_key: str):
        """Remove entry from SQLite cache"""
        try:
            def remove_entry():
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM image_cache WHERE cache_key = ?", (cache_key,))
                conn.commit()
                conn.close()
            
            await asyncio.get_event_loop().run_in_executor(None, remove_entry)
        except Exception as e:
            logger.debug(f"Error removing cache entry: {e}")
    
    async def warm_cache_for_popular_movies(self, movie_urls: List[Dict[str, str]]):
        """Warm cache for popular movies"""
        logger.info(f"🔥 Starting cache warming for {len(movie_urls)} popular movies")
        
        tasks = []
        for movie_data in movie_urls:
            url = movie_data.get('poster_url')
            if url:
                # Create warming task for different sizes
                for size in ['w200', 'w500', 'w780']:
                    task = self._warm_single_image(url, size)
                    tasks.append(task)
        
        # Process in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            await asyncio.sleep(0.1)  # Small delay between batches
        
        logger.info("✅ Cache warming completed")
    
    async def _warm_single_image(self, url: str, size: str):
        """Warm cache for a single image"""
        try:
            # Check if already cached
            cached_data = await self.get_cached_image(url, size)
            if cached_data:
                return  # Already cached
            
            # Download and cache the image
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    await self.cache_image(
                        url, response.content, content_type, size, 
                        ttl=self.popular_movies_cache_ttl
                    )
        except Exception as e:
            logger.debug(f"Cache warming failed for {url}: {e}")
    
    async def cleanup_expired_cache(self):
        """Cleanup expired cache entries"""
        logger.info("🧹 Starting cache cleanup")
        
        # Cleanup memory cache
        expired_keys = []
        current_time = datetime.now().timestamp()
        for key, entry in self.memory_cache.items():
            if current_time > entry.get('expires_at', 0):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Cleanup SQLite/disk cache
        await self._cleanup_sqlite_cache()
        
        logger.info(f"✅ Cache cleanup completed: removed {len(expired_keys)} memory entries")
    
    async def _cleanup_sqlite_cache(self):
        """Cleanup expired SQLite cache entries"""
        try:
            def cleanup_db():
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                
                # Get expired entries
                cursor.execute("""
                    SELECT file_path FROM image_cache 
                    WHERE expires_at < ?
                """, (datetime.now().timestamp(),))
                expired_files = cursor.fetchall()
                
                # Delete files
                for (file_path,) in expired_files:
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                
                # Remove from database
                cursor.execute("""
                    DELETE FROM image_cache WHERE expires_at < ?
                """, (datetime.now().timestamp(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                return deleted_count
            
            deleted_count = await asyncio.get_event_loop().run_in_executor(None, cleanup_db)
            logger.debug(f"Cleaned up {deleted_count} expired SQLite cache entries")
            
        except Exception as e:
            logger.error(f"SQLite cleanup error: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            def get_db_stats():
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM image_cache")
                total_entries = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM image_cache 
                    WHERE expires_at > ?
                """, (datetime.now().timestamp(),))
                valid_entries = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT SUM(LENGTH(content_type)) as total_size 
                    FROM image_cache 
                    WHERE expires_at > ?
                """, (datetime.now().timestamp(),))
                
                conn.close()
                return total_entries, valid_entries
            
            total_entries, valid_entries = await asyncio.get_event_loop().run_in_executor(
                None, get_db_stats
            )
            
            stats = {
                "memory_cache": {
                    "entries": len(self.memory_cache),
                    "limit": self.memory_cache_limit
                },
                "disk_cache": {
                    "total_entries": total_entries,
                    "valid_entries": valid_entries,
                    "expired_entries": total_entries - valid_entries
                },
                "redis_available": self.redis_client is not None,
                "cache_directory": str(self.cache_dir)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global instance
enhanced_image_cache = EnhancedImageCacheService()