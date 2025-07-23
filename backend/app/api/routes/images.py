"""
Enhanced image proxy endpoint to resolve CORS issues with external images
"""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, FileResponse, Response
import httpx
import asyncio
import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
import io
import hashlib
from datetime import datetime, timedelta

from ...services.image_processing_service import image_processing_service, fallback_image_generator
from ...core.error_handler import (
    error_handler,
    ErrorSeverity,
    ValidationException,
    ImageProcessingException,
    ExternalAPIException,
    get_request_id
)

router = APIRouter(prefix="/api/images", tags=["images"])
logger = logging.getLogger(__name__)

# In-memory cache for image proxy responses
_image_cache: Dict[str, Dict] = {}
_cache_ttl = 24 * 60 * 60  # 24 hours in seconds

def _generate_cache_key(url: str) -> str:
    """Generate cache key for image URL"""
    return hashlib.md5(url.encode()).hexdigest()

def _get_cached_image(url: str) -> Optional[bytes]:
    """Get cached image if it exists and is still valid"""
    cache_key = _generate_cache_key(url)
    
    if cache_key not in _image_cache:
        return None
    
    cache_entry = _image_cache[cache_key]
    cache_time = cache_entry.get('timestamp', 0)
    current_time = datetime.now().timestamp()
    
    # Check if cache has expired
    if current_time - cache_time > _cache_ttl:
        logger.debug(f"🖼️ Image cache EXPIRED for: {url}")
        del _image_cache[cache_key]
        return None
    
    age_hours = (current_time - cache_time) / 3600
    logger.debug(f"🖼️ Image cache HIT for: {url} (age: {age_hours:.1f}h)")
    return cache_entry.get('data')

def _cache_image(url: str, image_data: bytes, content_type: str) -> None:
    """Cache image data"""
    try:
        cache_key = _generate_cache_key(url)
        
        # Don't cache very large images (> 5MB)
        if len(image_data) > 5 * 1024 * 1024:
            logger.debug(f"🖼️ Image too large to cache: {url} ({len(image_data)} bytes)")
            return
        
        _image_cache[cache_key] = {
            'data': image_data,
            'content_type': content_type,
            'timestamp': datetime.now().timestamp()
        }
        
        logger.debug(f"🖼️ Image cache SET for: {url} ({len(image_data)} bytes)")
        
        # Clean up old cache entries (keep only last 100 entries)
        if len(_image_cache) > 100:
            # Remove oldest entries
            sorted_keys = sorted(
                _image_cache.keys(),
                key=lambda k: _image_cache[k]['timestamp']
            )
            for old_key in sorted_keys[:-100]:
                del _image_cache[old_key]
            logger.debug("🖼️ Image cache cleanup: removed old entries")
            
    except Exception as e:
        logger.warning(f"Failed to cache image: {e}")

def _clear_expired_image_cache() -> None:
    """Clear expired image cache entries"""
    current_time = datetime.now().timestamp()
    expired_keys = []
    
    for key, entry in _image_cache.items():
        if current_time - entry['timestamp'] > _cache_ttl:
            expired_keys.append(key)
    
    for key in expired_keys:
        del _image_cache[key]
    
    if expired_keys:
        logger.debug(f"🖼️ Image cache cleanup: removed {len(expired_keys)} expired entries")

# Add CORS preflight support for image proxy
@router.options("/image-proxy")
@router.options("/proxy")
async def proxy_image_options():
    """Handle CORS preflight requests for image proxy"""
    return Response(
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'  # Cache preflight for 24 hours
        }
    )

def validate_and_sanitize_url(url: str, request_id: Optional[str] = None) -> str:
    """Validate and sanitize image URL using the image processing service"""
    if not url:
        raise error_handler.handle_validation_error(
            "Image URL is required", "url", url
        )
    
    if len(url) > 2000:
        raise error_handler.handle_validation_error(
            "Image URL too long (max 2000 characters)", "url", url
        )
    
    try:
        # Use the image processing service for consistent URL processing
        result = image_processing_service.process_image_url(url, source='generic')
        
        if not result['valid'] or not result['processed_url']:
            error_msg = result.get('error', 'Invalid URL format or value')
            raise ImageProcessingException(url, error_msg)
        
        processed_url = result['processed_url']
        
        # Security check - only allow HTTPS
        if not processed_url.startswith('https://'):
            raise ImageProcessingException(url, "Only HTTPS URLs are allowed for security")
        
        return processed_url
        
    except ImageProcessingException:
        raise
    except Exception as e:
        error_handler.log_error(
            e,
            severity=ErrorSeverity.MEDIUM,
            context={"url": url, "function": "validate_and_sanitize_url"},
            request_id=request_id
        )
        raise ImageProcessingException(url, f"URL validation failed: {str(e)}")



async def try_proxy_with_retry(url: str, max_retries: int = 2, request_id: Optional[str] = None) -> Response:
    """Try to proxy image with retry mechanism, caching, and different headers"""
    
    # Check cache first
    cached_data = _get_cached_image(url)
    if cached_data:
        cache_key = _generate_cache_key(url)
        cached_entry = _image_cache[cache_key]
        content_type = cached_entry.get('content_type', 'image/jpeg')
        
        return Response(
            content=cached_data,
            media_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=86400, s-maxage=86400',  # 24 hours for cached images
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'X-Cache': 'HIT',
                'Vary': 'Accept-Encoding',
                'ETag': f'"{_generate_cache_key(url)}"'
            }
        )
    
    headers_variants = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.imdb.com/',
            'Cache-Control': 'no-cache'
        },
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
        }
    ]
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            headers = headers_variants[attempt % len(headers_variants)]
            
            async with httpx.AsyncClient(
                timeout=10.0, 
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            ) as client:
                
                logger.debug(f"🔄 Attempt {attempt + 1} proxying image: {url}")
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    
                    # Validate it's actually an image
                    if not content_type.startswith('image/'):
                        logger.warning(f"⚠️ Non-image content type: {content_type}")
                        content_type = 'image/jpeg'
                    
                    # Validate content size (max 10MB)
                    if len(response.content) > 10 * 1024 * 1024:
                        raise ImageProcessingException(url, "Image too large (max 10MB)")
                    
                    logger.debug(f"✅ Successfully proxied image on attempt {attempt + 1}: {url}")
                    
                    # Cache the successful response
                    _cache_image(url, response.content, content_type)
                    
                    return Response(
                        content=response.content,
                        media_type=content_type,
                        headers={
                            'Cache-Control': 'public, max-age=86400, s-maxage=86400', # 24 hours as per requirements
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET',
                            'Access-Control-Allow-Headers': 'Content-Type',
                            'X-Cache': 'MISS',
                            'Vary': 'Accept-Encoding',
                            'ETag': f'"{hashlib.md5(response.content).hexdigest()}"'
                        }
                    )
                else:
                    last_error = f"HTTP {response.status_code}"
                    logger.warning(f"⚠️ HTTP {response.status_code} on attempt {attempt + 1} for: {url}")
                    
        except httpx.TimeoutException as e:
            last_error = "Request timeout"
            logger.warning(f"⏰ Timeout on attempt {attempt + 1} for: {url}")
        except httpx.HTTPStatusError as e:
            last_error = f"HTTP error {e.response.status_code}"
            logger.warning(f"❌ HTTP error {e.response.status_code} on attempt {attempt + 1} for: {url}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"❌ Error on attempt {attempt + 1} for {url}: {e}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries:
            await asyncio.sleep(0.5 * (2 ** attempt))
    
    # All attempts failed - log and raise appropriate exception
    error_handler.log_error(
        Exception(f"Image proxy failed after {max_retries + 1} attempts: {last_error}"),
        severity=ErrorSeverity.MEDIUM,
        context={"url": url, "attempts": max_retries + 1, "last_error": last_error},
        request_id=request_id
    )
    
    raise ImageProcessingException(url, f"Could not load image after {max_retries + 1} attempts: {last_error}")

@router.get("/proxy")
@router.get("/image-proxy")  # Add compatibility route for frontend
async def proxy_image(
    request: Request,
    url: str = Query(..., description="Image URL to proxy")
):
    """Enhanced proxy for external images with retry mechanism, caching, and fallback generation"""
    request_id = get_request_id(request)
    
    try:
        # Clean up expired cache entries periodically
        _clear_expired_image_cache()
        
        # Validate and sanitize URL
        clean_url = validate_and_sanitize_url(url, request_id)
        
        # Try to proxy the image with retries and caching
        try:
            return await try_proxy_with_retry(clean_url, request_id=request_id)
            
        except ImageProcessingException:
            # Generate fallback image using the new service
            logger.info(f"🎨 Generating fallback image for failed URL: {url} (request_id: {request_id})")
            
            # Try to extract movie title from URL or use generic
            title = "Movie Poster"
            try:
                # Simple title extraction from common patterns
                if 'title=' in url:
                    title = url.split('title=')[1].split('&')[0].replace('%20', ' ')
                elif '/title/' in url:
                    title_part = url.split('/title/')[1].split('/')[0]
                    title = title_part.replace('-', ' ').title()
            except:
                pass
            
            try:
                fallback_content = fallback_image_generator.generate_fallback_image(title)
                
                return Response(
                    content=fallback_content,
                    media_type="image/png",
                    headers={
                        'Cache-Control': 'public, max-age=1800',  # Cache fallback for 30 minutes
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET',
                        'Access-Control-Allow-Headers': 'Content-Type'
                    }
                )
            except Exception as fallback_error:
                error_handler.log_error(
                    fallback_error,
                    severity=ErrorSeverity.HIGH,
                    context={"url": url, "title": title, "function": "generate_fallback"},
                    request_id=request_id
                )
                raise ImageProcessingException(url, "Failed to generate fallback image")
                
    except (ValidationException, ImageProcessingException):
        raise
    except Exception as e:
        error_handler.log_error(
            e,
            severity=ErrorSeverity.HIGH,
            context={"url": url, "endpoint": "proxy_image"},
            request_id=request_id
        )
        
        # Generate generic fallback as last resort
        try:
            fallback_content = fallback_image_generator.generate_fallback_image("Error Loading Image")
            return Response(
                content=fallback_content,
                media_type="image/png",
                headers={
                    'Cache-Control': 'public, max-age=300',  # Cache error fallback for 5 minutes
                    'Access-Control-Allow-Origin': '*'
                }
            )
        except:
            raise ImageProcessingException(url, "Unable to generate fallback image")

@router.get("/cached/{filename}")
async def get_cached_image(request: Request, filename: str):
    """Serve cached images"""
    request_id = get_request_id(request)
    
    try:
        # Validate filename
        if not filename or len(filename) > 255:
            raise error_handler.handle_validation_error(
                "Invalid filename", "filename", filename
            )
        
        # Security check - prevent path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise error_handler.handle_validation_error(
                "Invalid filename format", "filename", filename
            )
        
        # Define the cache directory
        cache_dir = Path("./cache/images")
        
        # Check different subdirectories
        possible_paths = [
            cache_dir / "posters" / filename,
            cache_dir / "backdrops" / filename,
            cache_dir / "thumbnails" / filename,
            cache_dir / filename
        ]
        
        for file_path in possible_paths:
            if file_path.exists() and file_path.is_file():
                logger.debug(f"Serving cached image: {file_path} (request_id: {request_id})")
                return FileResponse(
                    path=str(file_path),
                    headers={
                        "Cache-Control": "public, max-age=86400",  # 24 hours
                        "Access-Control-Allow-Origin": "*"
                    }
                )
        
        # Image not found
        raise error_handler.handle_not_found_error("Cached image", filename)
        
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        error_handler.log_error(
            e,
            severity=ErrorSeverity.MEDIUM,
            context={"filename": filename, "endpoint": "get_cached_image"},
            request_id=request_id
        )
        raise HTTPException(
            status_code=500, 
            detail="Error serving cached image. Please try again later."
        )
