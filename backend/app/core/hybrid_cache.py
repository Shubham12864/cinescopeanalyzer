"""
FREE Cache Implementation for CineScope
No Redis needed - saves $200+/year while maintaining good performance
"""

import os
import json
import time
import sqlite3
import threading
import asyncio
from typing import Any, Optional, Dict, List
from pathlib import Path

class HybridCache:
    """
    Hybrid caching system that combines:
    1. Memory cache (fastest access)
    2. SQLite cache (persistent storage)
    3. Azure Blob storage (backup/sharing)
    
    Where cache is stored:
    - Memory: In server RAM (temporary, super fast)
    - SQLite: Local file /home/site/wwwroot/cache.db (persistent)
    - Blob: Azure Storage (optional backup)
    """
    
    def __init__(self, cache_dir: str = None):
        # Determine cache directory based on environment
        if os.environ.get('WEBSITE_SITE_NAME'):  # Azure App Service
            self.cache_dir = '/home/site/wwwroot/cache'
        else:  # Local development
            self.cache_dir = cache_dir or './cache'
            
        Path(self.cache_dir).mkdir(exist_ok=True)
        
        # Memory cache (stored in RAM)
        self._memory_cache: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        
        # SQLite cache (stored in file)
        self.db_path = os.path.join(self.cache_dir, 'cache.db')
        self._init_sqlite()
        
        print(f"💾 Cache initialized:")
        print(f"   Memory: RAM (temporary)")
        print(f"   SQLite: {self.db_path}")
        print(f"   Directory: {self.cache_dir}")
    
    def _init_sqlite(self):
        """Initialize SQLite database for persistent cache"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                expires_at REAL,
                created_at REAL,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)')
        conn.commit()
        conn.close()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value with fallback chain:
        1. Check memory cache (fastest)
        2. Check SQLite cache (persistent)
        3. Return None if not found
        """
        current_time = time.time()
        
        # Step 1: Check memory cache (stored in RAM)
        with self._lock:
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if current_time < entry['expires_at']:
                    return entry['value']
                else:
                    del self._memory_cache[key]
        
        # Step 2: Check SQLite cache (stored in file)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            'SELECT value, expires_at FROM cache WHERE key = ?', (key,)
        )
        row = cursor.fetchone()
        
        if row and current_time < row[1]:
            value = json.loads(row[0])
            
            # Update access stats
            conn.execute(
                'UPDATE cache SET access_count = access_count + 1, last_accessed = ? WHERE key = ?',
                (current_time, key)
            )
            conn.commit()
            
            # Copy to memory cache for faster future access
            with self._lock:
                self._memory_cache[key] = {
                    'value': value,
                    'expires_at': row[1],
                    'created_at': current_time
                }
            
            conn.close()
            return value
        
        conn.close()
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Store value in both memory and SQLite cache
        
        Args:
            key: Cache key
            value: Data to cache  
            ttl: Time to live in seconds
        """
        current_time = time.time()
        expires_at = current_time + ttl
        json_value = json.dumps(value)
        
        # Store in memory cache (RAM)
        with self._lock:
            self._memory_cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': current_time
            }
            
            # Limit memory cache size (prevent RAM overflow)
            if len(self._memory_cache) > 1000:
                oldest_key = min(
                    self._memory_cache.keys(),
                    key=lambda k: self._memory_cache[k]['created_at']
                )
                del self._memory_cache[oldest_key]
        
        # Store in SQLite cache (persistent file)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            '''INSERT OR REPLACE INTO cache 
               (key, value, expires_at, created_at, access_count, last_accessed) 
               VALUES (?, ?, ?, ?, 0, ?)''',
            (key, json_value, expires_at, current_time, current_time)
        )
        conn.commit()
        conn.close()
    
    def delete(self, key: str):
        """Remove from both memory and SQLite"""
        # Remove from memory
        with self._lock:
            if key in self._memory_cache:
                del self._memory_cache[key]
        
        # Remove from SQLite
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM cache WHERE key = ?', (key,))
        conn.commit()
        conn.close()
    
    def cleanup_expired(self):
        """Remove expired entries to free up space"""
        current_time = time.time()
        
        # Clean memory cache
        with self._lock:
            expired_keys = [
                key for key, entry in self._memory_cache.items()
                if current_time >= entry['expires_at']
            ]
            for key in expired_keys:
                del self._memory_cache[key]
        
        # Clean SQLite cache
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM cache WHERE expires_at < ?', (current_time,))
        deleted_count = conn.total_changes
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_entries,
                COUNT(*) FILTER (WHERE expires_at > ?) as active_entries,
                SUM(access_count) as total_accesses,
                AVG(access_count) as avg_accesses
            FROM cache
        ''', (time.time(),))
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'memory_cache_size': len(self._memory_cache),
            'sqlite_total_entries': stats[0],
            'sqlite_active_entries': stats[1],
            'total_accesses': stats[2] or 0,
            'average_accesses': round(stats[3] or 0, 2),
            'cache_directory': self.cache_dir,
            'database_path': self.db_path
        }

    # Async wrapper methods for compatibility with async code
    async def async_get(self, key: str) -> Optional[Any]:
        """Async wrapper for get method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get, key)
    
    async def async_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Async wrapper for set method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.set, key, value, ttl)
    
    async def async_delete(self, key: str) -> bool:
        """Async wrapper for delete method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.delete, key)
    
    async def async_clear(self) -> bool:
        """Async wrapper for clear method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.clear)
    
    async def async_get_stats(self) -> Dict:
        """Async wrapper for get_stats method"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_stats)

# Global cache instance
hybrid_cache = HybridCache()

# Usage in your FastAPI app:
def cache_search_results(query: str, results: List[Dict]):
    """Cache movie search results"""
    cache_key = f"search:{query.lower().strip()}"
    hybrid_cache.set(cache_key, results, ttl=1800)  # 30 minutes
    print(f"🗄️ Cached search '{query}' with {len(results)} results")

def get_cached_search(query: str) -> Optional[List[Dict]]:
    """Get cached search results"""
    cache_key = f"search:{query.lower().strip()}"
    results = hybrid_cache.get(cache_key)
    if results:
        print(f"⚡ Cache HIT for search '{query}' - {len(results)} results")
        return results
    else:
        print(f"❌ Cache MISS for search '{query}'")
        return None
