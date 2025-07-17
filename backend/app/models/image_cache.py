"""
Image cache model for storing movie poster and backdrop images
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CachedImage(BaseModel):
    """Model for cached movie images"""
    id: str  # unique identifier
    movie_id: str  # reference to movie
    image_type: str  # 'poster', 'backdrop', 'thumbnail'
    original_url: str  # original external URL
    local_path: Optional[str] = None  # local file path if downloaded
    cached_url: str  # URL to serve from (could be local or external)
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None  # in bytes
    format: Optional[str] = None  # 'jpg', 'png', 'webp'
    is_downloaded: bool = False  # whether image is stored locally
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    
class ImageCacheStats(BaseModel):
    """Statistics for image cache"""
    total_images: int
    downloaded_images: int
    cache_size_bytes: int
    most_accessed_images: list
    last_cleanup: Optional[datetime] = None
