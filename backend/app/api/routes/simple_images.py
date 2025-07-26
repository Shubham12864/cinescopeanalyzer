#!/usr/bin/env python3
"""
FIXED IMAGE ROUTES - NO PIL DEPENDENCIES
Simple, fast image proxy without image processing dependencies
"""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
import logging
import asyncio
import httpx
from urllib.parse import unquote
from datetime import datetime
import hashlib

router = APIRouter(prefix="/api/images", tags=["images"])
logger = logging.getLogger(__name__)

# Simple image proxy without external service dependencies
class SimpleImageProxy:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 24 * 60 * 60  # 24 hours
        
    async def proxy_image(self, url: str) -> Response:
        """Proxy image without PIL processing"""
        try:
            if not url or not url.startswith('https://'):
                raise ValueError("Invalid URL")
            
            # Simple cache key
            cache_key = hashlib.md5(url.encode()).hexdigest()
            
            # Check cache
            if cache_key in self.cache:
                cache_data = self.cache[cache_key]
                if (datetime.now().timestamp() - cache_data['timestamp']) < self.cache_ttl:
                    return Response(
                        content=cache_data['content'],
                        media_type=cache_data['content_type'],
                        headers={'Cache-Control': 'public, max-age=86400', 'Access-Control-Allow-Origin': '*'}
                    )
            
            # Fetch image
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200 and len(response.content) > 100:
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    
                    # Cache successful response
                    self.cache[cache_key] = {
                        'content': response.content,
                        'content_type': content_type,
                        'timestamp': datetime.now().timestamp()
                    }
                    
                    return Response(
                        content=response.content,
                        media_type=content_type,
                        headers={
                            'Cache-Control': 'public, max-age=86400',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET'
                        }
                    )
            
            # Return simple placeholder if failed
            return Response(
                content=b'',
                media_type='image/png',
                headers={'Access-Control-Allow-Origin': '*'}
            )
            
        except Exception as e:
            logger.error(f"Image proxy error: {e}")
            return Response(
                content=b'',
                media_type='image/png', 
                headers={'Access-Control-Allow-Origin': '*'}
            )

# Create global instance
simple_proxy = SimpleImageProxy()

@router.options("/image-proxy")
async def image_proxy_options():
    """Handle CORS preflight for image proxy"""
    return Response(
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        }
    )

@router.get("/image-proxy")
async def proxy_image(request: Request, url: str = Query(...)):
    """
    Simple image proxy without PIL dependencies
    Fast, reliable image proxying with caching
    """
    try:
        # Basic URL validation
        if not url:
            raise HTTPException(status_code=400, detail="URL parameter is required")
        
        # Decode URL if it's encoded
        try:
            decoded_url = unquote(url)
        except Exception:
            decoded_url = url
        
        logger.info(f"🖼️ Proxying image: {decoded_url[:60]}...")
        
        # Use simple image proxy service
        response = await simple_proxy.proxy_image(decoded_url)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Image proxy failed: {str(e)}")

@router.get("/health")
async def images_health():
    """Health check for image service"""
    return {
        "status": "healthy",
        "service": "simple-image-proxy",
        "dependencies": "none"
    }
