"""
Image cache service for downloading and storing movie images locally
"""
import os
import sqlite3
import hashlib
import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from urllib.parse import urlparse
import logging
from pathlib import Path

from ..models.image_cache import CachedImage, ImageCacheStats

logger = logging.getLogger(__name__)

class ImageCacheService:
    def __init__(self, cache_dir: str = "./cache/images", db_path: str = "./cache/image_cache.db"):
        """
        Initialize image cache service
        
        Args:
            cache_dir: Directory to store cached images
            db_path: Path to SQLite database for cache metadata
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        
        # Create subdirectories for different image types
        (self.cache_dir / "posters").mkdir(exist_ok=True)
        (self.cache_dir / "backdrops").mkdir(exist_ok=True)
        (self.cache_dir / "thumbnails").mkdir(exist_ok=True)
        
        logger.info(f"🖼️  Image cache initialized: {self.cache_dir}")
    
    def _init_database(self):
        """Initialize SQLite database for image cache"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cached_images (
                    id TEXT PRIMARY KEY,
                    movie_id TEXT NOT NULL,
                    image_type TEXT NOT NULL,
                    original_url TEXT NOT NULL,
                    local_path TEXT,
                    cached_url TEXT NOT NULL,
                    width INTEGER,
                    height INTEGER,
                    file_size INTEGER,
                    format TEXT,
                    is_downloaded BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_movie_id ON cached_images(movie_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_image_type ON cached_images(image_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cached_images(last_accessed)")
            
            conn.commit()
    
    def _generate_cache_id(self, movie_id: str, image_type: str, original_url: str) -> str:
        """Generate unique cache ID for image"""
        content = f"{movie_id}_{image_type}_{original_url}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        if path.endswith('.jpg') or path.endswith('.jpeg'):
            return 'jpg'
        elif path.endswith('.png'):
            return 'png'
        elif path.endswith('.webp'):
            return 'webp'
        else:
            # Default to jpg for unknown formats
            return 'jpg'
    
    async def get_cached_image(self, movie_id: str, image_type: str) -> Optional[CachedImage]:
        """
        Get cached image for a movie
        
        Args:
            movie_id: Movie identifier
            image_type: Type of image ('poster', 'backdrop', 'thumbnail')
            
        Returns:
            CachedImage object if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM cached_images 
                WHERE movie_id = ? AND image_type = ?
                ORDER BY last_accessed DESC
                LIMIT 1
            """, (movie_id, image_type))
            
            row = cursor.fetchone()
            if row:
                # Update access count and timestamp
                conn.execute("""
                    UPDATE cached_images 
                    SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                    WHERE id = ?
                """, (row['id'],))
                conn.commit()
                
                return CachedImage(
                    id=row['id'],
                    movie_id=row['movie_id'],
                    image_type=row['image_type'],
                    original_url=row['original_url'],
                    local_path=row['local_path'],
                    cached_url=row['cached_url'],
                    width=row['width'],
                    height=row['height'],
                    file_size=row['file_size'],
                    format=row['format'],
                    is_downloaded=bool(row['is_downloaded']),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else datetime.now(),
                    access_count=row['access_count']
                )
        return None
    
    async def get_or_cache_image(self, original_url: str, movie_id: str, image_type: str = "poster") -> Optional[str]:
        """
        Get cached image URL or cache the image and return the local URL
        
        Args:
            original_url: Original image URL
            movie_id: Movie identifier
            image_type: Type of image ('poster', 'backdrop', 'thumbnail')
            
        Returns:
            Local cached image URL or original URL if caching fails
        """
        try:
            if not original_url:
                return None
            
            # Check if image is already cached
            cached_image = await self.get_cached_image(movie_id, image_type)
            if cached_image and cached_image.is_downloaded and cached_image.local_path and os.path.exists(cached_image.local_path):
                # Return the cached URL
                cached_url = f"/api/movies/images/cached/{os.path.basename(cached_image.local_path)}"
                logger.debug(f"✅ Using cached image: {cached_url}")
                return cached_url
            
            # Try to cache the image
            try:
                cached_image = await self.cache_image(movie_id, image_type, original_url, download=True)
                if cached_image and cached_image.is_downloaded and cached_image.local_path and os.path.exists(cached_image.local_path):
                    cached_url = f"/api/movies/images/cached/{os.path.basename(cached_image.local_path)}"
                    logger.info(f"🖼️  Successfully cached image: {cached_url}")
                    return cached_url
            except Exception as cache_error:
                logger.warning(f"⚠️ Image caching failed: {cache_error}")
            
            # Fallback to original URL
            logger.debug(f"📷 Using original image URL: {original_url}")
            return original_url
            
        except Exception as e:
            logger.error(f"❌ Error in get_or_cache_image: {e}")
            return original_url  # Always return something, even if it's the original URL
    
    async def cache_image(self, movie_id: str, image_type: str, original_url: str, download: bool = True) -> CachedImage:
        """
        Cache an image (with optional download)
        
        Args:
            movie_id: Movie identifier
            image_type: Type of image ('poster', 'backdrop', 'thumbnail')
            original_url: Original URL of the image
            download: Whether to download the image locally
            
        Returns:
            CachedImage object
        """
        # Check if already cached
        existing = await self.get_cached_image(movie_id, image_type)
        if existing:
            logger.info(f"🖼️  Image already cached: {movie_id}/{image_type}")
            return existing
        
        cache_id = self._generate_cache_id(movie_id, image_type, original_url)
        extension = self._get_file_extension(original_url)
        
        local_path = None
        cached_url = original_url  # Default to original URL
        is_downloaded = False
        file_size = None
        width = None
        height = None
        
        if download:
            try:
                # Download the image
                local_filename = f"{cache_id}.{extension}"
                local_path = self.cache_dir / image_type.lower() / local_filename
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(original_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            content = await response.read()
                            
                            # Save to local file
                            with open(local_path, 'wb') as f:
                                f.write(content)
                            
                            file_size = len(content)
                            is_downloaded = True
                            cached_url = f"/cache/images/{image_type.lower()}/{local_filename}"
                            
                            logger.info(f"🖼️  Downloaded image: {original_url} -> {local_path}")
                        else:
                            logger.warning(f"🖼️  Failed to download image: {response.status} {original_url}")
            
            except Exception as e:
                logger.error(f"🖼️  Error downloading image {original_url}: {e}")
        
        # Store in database
        cached_image = CachedImage(
            id=cache_id,
            movie_id=movie_id,
            image_type=image_type,
            original_url=original_url,
            local_path=str(local_path) if local_path else None,
            cached_url=cached_url,
            width=width,
            height=height,
            file_size=file_size,
            format=extension,
            is_downloaded=is_downloaded,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO cached_images (
                    id, movie_id, image_type, original_url, local_path, cached_url,
                    width, height, file_size, format, is_downloaded, created_at, last_accessed, access_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cached_image.id, cached_image.movie_id, cached_image.image_type,
                cached_image.original_url, cached_image.local_path, cached_image.cached_url,
                cached_image.width, cached_image.height, cached_image.file_size,
                cached_image.format, cached_image.is_downloaded,
                cached_image.created_at.isoformat(), cached_image.last_accessed.isoformat(),
                cached_image.access_count
            ))
            conn.commit()
        
        logger.info(f"🖼️  Cached image: {movie_id}/{image_type} -> {cached_url}")
        return cached_image
    
    async def get_optimized_image_url(self, movie_id: str, image_type: str, original_url: str) -> str:
        """
        Get optimized image URL (cached if available, original otherwise)
        
        Args:
            movie_id: Movie identifier
            image_type: Type of image ('poster', 'backdrop', 'thumbnail')
            original_url: Original URL of the image
            
        Returns:
            URL to use for the image (cached or original)
        """
        # Skip caching for placeholder images
        if not original_url or 'placeholder' in original_url.lower() or 'dummyimage' in original_url.lower():
            return original_url
        
        # Check cache first
        cached = await self.get_cached_image(movie_id, image_type)
        if cached:
            # Return local path if downloaded, otherwise original URL
            return cached.cached_url if cached.is_downloaded else cached.original_url
        
        # Cache in background without blocking
        asyncio.create_task(self.cache_image(movie_id, image_type, original_url, download=True))
        
        # Return original URL for now
        return original_url
    

    
    async def get_cache_stats(self) -> ImageCacheStats:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Total images
            total_result = conn.execute("SELECT COUNT(*) as count FROM cached_images").fetchone()
            total_images = total_result['count'] if total_result else 0
            
            # Downloaded images
            downloaded_result = conn.execute("SELECT COUNT(*) as count FROM cached_images WHERE is_downloaded = 1").fetchone()
            downloaded_images = downloaded_result['count'] if downloaded_result else 0
            
            # Cache size
            size_result = conn.execute("SELECT SUM(file_size) as total_size FROM cached_images WHERE is_downloaded = 1").fetchone()
            cache_size_bytes = size_result['total_size'] if size_result and size_result['total_size'] else 0
            
            # Most accessed images
            most_accessed = conn.execute("""
                SELECT movie_id, image_type, access_count 
                FROM cached_images 
                ORDER BY access_count DESC 
                LIMIT 10
            """).fetchall()
            
            most_accessed_list = [
                {"movie_id": row['movie_id'], "image_type": row['image_type'], "access_count": row['access_count']}
                for row in most_accessed
            ]
            
            return ImageCacheStats(
                total_images=total_images,
                downloaded_images=downloaded_images,
                cache_size_bytes=cache_size_bytes,
                most_accessed_images=most_accessed_list
            )
    
    async def cleanup_old_images(self, days_old: int = 30, max_cache_size_mb: int = 500):
        """
        Clean up old and unused cached images
        
        Args:
            days_old: Delete images older than this many days
            max_cache_size_mb: Maximum cache size in MB
        """
        with sqlite3.connect(self.db_path) as conn:
            # Delete old images
            cutoff_date = datetime.now().replace(day=datetime.now().day - days_old)
            old_images = conn.execute("""
                SELECT local_path FROM cached_images 
                WHERE last_accessed < ? AND is_downloaded = 1
            """, (cutoff_date.isoformat(),)).fetchall()
            
            # Delete files and database entries
            for row in old_images:
                if row[0] and os.path.exists(row[0]):
                    try:
                        os.remove(row[0])
                        logger.info(f"🗑️  Deleted old cached image: {row[0]}")
                    except Exception as e:
                        logger.error(f"🗑️  Error deleting file {row[0]}: {e}")
            
            # Remove from database
            conn.execute("DELETE FROM cached_images WHERE last_accessed < ?", (cutoff_date.isoformat(),))
            
            # Check cache size and remove least accessed if needed
            stats = await self.get_cache_stats()
            if stats.cache_size_bytes > max_cache_size_mb * 1024 * 1024:
                # Remove least accessed images until under limit
                least_accessed = conn.execute("""
                    SELECT id, local_path FROM cached_images 
                    WHERE is_downloaded = 1 
                    ORDER BY access_count ASC, last_accessed ASC
                """).fetchall()
                
                for row in least_accessed:
                    if row[1] and os.path.exists(row[1]):
                        try:
                            os.remove(row[1])
                            conn.execute("DELETE FROM cached_images WHERE id = ?", (row[0],))
                            logger.info(f"🗑️  Deleted cached image for size limit: {row[1]}")
                            
                            # Check if we're under the limit now
                            new_stats = await self.get_cache_stats()
                            if new_stats.cache_size_bytes <= max_cache_size_mb * 1024 * 1024:
                                break
                        except Exception as e:
                            logger.error(f"🗑️  Error deleting file {row[1]}: {e}")
            
            conn.commit()
            logger.info("🗑️  Image cache cleanup completed")

# Global instance
image_cache_service = ImageCacheService()
