"""
Enhanced Image Service with Azure Cosmos DB Caching
High-performance image proxy and caching system
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
import aiohttp
import hashlib
from datetime import datetime
import base64
import io
from PIL import Image

from ..services.azure_cache_service import AzureCosmosCache

logger = logging.getLogger(__name__)

class EnhancedImageService:
    def __init__(self, cache_service: AzureCosmosCache = None):
        self.cache = cache_service or AzureCosmosCache()
        self.session = None
        
        # Image configuration
        self.supported_formats = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.quality_settings = {
            'low': 60,
            'medium': 80,
            'high': 95
        }
        
        # Performance stats
        self.stats = {
            "cache_hits": 0,
            "downloads": 0,
            "errors": 0,
            "processed": 0,
            "total_requests": 0
        }
    
    async def initialize(self):
        """Initialize cache and HTTP session"""
        await self.cache.initialize()
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30),
            headers={
                'User-Agent': 'CineScopeAnalyzer/1.0 Image Service'
            }
        )
        logger.info("✅ Enhanced Image Service initialized")
    
    async def get_image_cached(self, image_url: str, quality: str = 'medium', force_refresh: bool = False) -> Dict[str, Any]:
        """Get image with caching and optimization"""
        self.stats["total_requests"] += 1
        
        try:
            if not image_url:
                return self._error_response("No image URL provided")
            
            # Generate cache key based on URL and quality
            cache_key = self._generate_image_cache_key(image_url, quality)
            
            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_image = await self.cache.get_cached_image(image_url)
                if cached_image:
                    self.stats["cache_hits"] += 1
                    logger.debug(f"🎯 Image cache hit: {image_url[:50]}...")
                    return self._format_cached_image_response(cached_image)
            
            # Download and process image
            logger.debug(f"🌐 Downloading image: {image_url[:50]}...")
            self.stats["downloads"] += 1
            
            image_data = await self._download_image(image_url)
            if not image_data:
                return self._error_response("Failed to download image")
            
            # Process and optimize image
            processed_image = await self._process_image(image_data, quality)
            if not processed_image:
                return self._error_response("Failed to process image")
            
            # Cache the processed image
            await self.cache.cache_image(
                image_url,
                processed_image['data'],
                processed_image['content_type']
            )
            
            self.stats["processed"] += 1
            logger.debug(f"✅ Image processed and cached: {image_url[:50]}...")
            
            return {
                "success": True,
                "image_data": base64.b64encode(processed_image['data']).decode('utf-8'),
                "content_type": processed_image['content_type'],
                "size": len(processed_image['data']),
                "quality": quality,
                "from_cache": False,
                "timestamp": datetime.utcnow().isoformat(),
                "processed": True
            }
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ Image service error for {image_url}: {e}")
            return self._error_response(str(e))
    
    async def proxy_image(self, image_url: str, quality: str = 'medium') -> Dict[str, Any]:
        """Proxy image through our service with caching"""
        return await self.get_image_cached(image_url, quality)
    
    async def batch_process_images(self, image_urls: List[str], quality: str = 'medium') -> Dict[str, Any]:
        """Process multiple images in parallel"""
        if not image_urls:
            return {"results": [], "total": 0, "errors": 0}
        
        logger.info(f"🔄 Batch processing {len(image_urls)} images")
        
        # Process images in parallel with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent downloads
        
        async def process_single_image(url):
            async with semaphore:
                return await self.get_image_cached(url, quality)
        
        # Execute all downloads in parallel
        tasks = [process_single_image(url) for url in image_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful results from errors
        successful = []
        error_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_count += 1
                logger.error(f"❌ Batch processing error for {image_urls[i]}: {result}")
            elif result.get("success"):
                successful.append({
                    "url": image_urls[i],
                    "image_data": result["image_data"],
                    "content_type": result["content_type"],
                    "size": result["size"],
                    "from_cache": result["from_cache"]
                })
            else:
                error_count += 1
        
        logger.info(f"✅ Batch processing complete: {len(successful)} successful, {error_count} errors")
        
        return {
            "results": successful,
            "total": len(image_urls),
            "successful": len(successful),
            "errors": error_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL with error handling"""
        try:
            async with self.session.get(image_url) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # Check if it's a supported image format
                    if not any(fmt in content_type for fmt in self.supported_formats):
                        logger.warning(f"⚠️ Unsupported image format: {content_type}")
                        return None
                    
                    # Check content length
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > self.max_image_size:
                        logger.warning(f"⚠️ Image too large: {content_length} bytes")
                        return None
                    
                    # Download image data
                    image_data = await response.read()
                    
                    # Double-check size after download
                    if len(image_data) > self.max_image_size:
                        logger.warning(f"⚠️ Downloaded image too large: {len(image_data)} bytes")
                        return None
                    
                    return image_data
                else:
                    logger.warning(f"⚠️ Image download failed: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Image download error: {e}")
            return None
    
    async def _process_image(self, image_data: bytes, quality: str) -> Optional[Dict[str, Any]]:
        """Process and optimize image"""
        try:
            # Process image in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._process_image_sync, image_data, quality)
        except Exception as e:
            logger.error(f"❌ Image processing error: {e}")
            return None
    
    def _process_image_sync(self, image_data: bytes, quality: str) -> Optional[Dict[str, Any]]:
        """Synchronous image processing with PIL"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (removes alpha channel)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 1920x1080)
            max_width, max_height = 1920, 1080
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Optimize and save to bytes
            output = io.BytesIO()
            jpeg_quality = self.quality_settings.get(quality, 80)
            
            image.save(
                output,
                format='JPEG',
                quality=jpeg_quality,
                optimize=True,
                progressive=True
            )
            
            processed_data = output.getvalue()
            output.close()
            
            return {
                "data": processed_data,
                "content_type": "image/jpeg",
                "original_size": len(image_data),
                "processed_size": len(processed_data),
                "compression_ratio": round(len(processed_data) / len(image_data) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"❌ Sync image processing error: {e}")
            return None
    
    def _generate_image_cache_key(self, image_url: str, quality: str) -> str:
        """Generate cache key for image"""
        content = f"{image_url}_{quality}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _format_cached_image_response(self, cached_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format cached image response"""
        try:
            # Convert hex data back to bytes
            image_bytes = bytes.fromhex(cached_data["data"])
            
            return {
                "success": True,
                "image_data": base64.b64encode(image_bytes).decode('utf-8'),
                "content_type": cached_data["content_type"],
                "size": cached_data["size"],
                "from_cache": True,
                "timestamp": datetime.utcnow().isoformat(),
                "processed": True
            }
        except Exception as e:
            logger.error(f"❌ Error formatting cached image: {e}")
            return self._error_response("Cache data corrupted")
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "error": error_message,
            "image_data": None,
            "content_type": None,
            "size": 0,
            "from_cache": False,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        cache_stats = await self.cache.get_cache_stats()
        
        total_requests = self.stats["total_requests"]
        cache_hit_rate = (self.stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "image_service_stats": {
                "total_requests": total_requests,
                "cache_hits": self.stats["cache_hits"],
                "downloads": self.stats["downloads"],
                "processed": self.stats["processed"],
                "errors": self.stats["errors"],
                "cache_hit_rate_percent": round(cache_hit_rate, 1)
            },
            "cache_stats": cache_stats,
            "performance": {
                "avg_cache_hit_rate": round(cache_hit_rate, 1),
                "download_reduction_percent": round((self.stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0, 1)
            }
        }
    
    async def clear_image_cache(self):
        """Clear all cached images"""
        await self.cache.clear_all_cache()
        self.stats = {
            "cache_hits": 0,
            "downloads": 0,
            "errors": 0,
            "processed": 0,
            "total_requests": 0
        }
        logger.info("✅ Image cache cleared and stats reset")
    
    async def close(self):
        """Close connections and cleanup"""
        if self.session:
            await self.session.close()
        
        await self.cache.close()
        logger.info("🔌 Enhanced Image Service closed")

# Global instance
enhanced_image_service = EnhancedImageService()
