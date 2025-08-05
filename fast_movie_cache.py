#!/usr/bin/env python3
"""
Quick fix to optimize movie endpoint performance
"""
import asyncio
import logging
from typing import Dict, Any, Optional

# Simple in-memory cache for movie details
_movie_cache: Dict[str, Dict[str, Any]] = {}
_cache_timeout = 300  # 5 minutes

logger = logging.getLogger(__name__)

class FastMovieCache:
    """Fast in-memory cache for movie details"""
    
    @classmethod
    def get(cls, movie_id: str) -> Optional[Dict[str, Any]]:
        """Get cached movie data"""
        cache_key = f"movie_{movie_id}"
        if cache_key in _movie_cache:
            cached_data = _movie_cache[cache_key]
            # Simple time-based cache expiry
            import time
            if time.time() - cached_data.get('cached_at', 0) < _cache_timeout:
                logger.info(f"⚡ Cache hit for movie: {movie_id}")
                return cached_data.get('data')
        return None
    
    @classmethod
    def set(cls, movie_id: str, data: Dict[str, Any]) -> None:
        """Cache movie data"""
        import time
        cache_key = f"movie_{movie_id}"
        _movie_cache[cache_key] = {
            'data': data,
            'cached_at': time.time()
        }
        logger.info(f"💾 Cached movie: {movie_id}")

if __name__ == "__main__":
    print("Fast movie cache utility loaded")
