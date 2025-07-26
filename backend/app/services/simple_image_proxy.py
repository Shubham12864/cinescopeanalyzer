#!/usr/bin/env python3
"""
SIMPLIFIED IMAGE PROXY SERVICE - NO PIL DEPENDENCIES
Fast image proxy without image processing dependencies
"""
import logging
import hashlib
import asyncio
from typing import Optional, Dict
import httpx
from fastapi import Response
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleImageProxyService:
    """Simple image proxy without PIL dependencies"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 24 * 60 * 60  # 24 hours
        
    def _generate_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
            
        cache_time = self.cache[cache_key].get('timestamp', 0)
        current_time = datetime.now().timestamp()
        
        return (current_time - cache_time) < self.cache_ttl
    
    async def proxy_image(self, url: str) -> Response:
        """Proxy image without PIL processing"""
        try:
            # Validate URL
            if not url or not url.startswith('https://'):
                raise ValueError("Invalid URL")
            
            # Check cache first
            cache_key = self._generate_cache_key(url)
            if self._is_cache_valid(cache_key):
                cached_data = self.cache[cache_key]
                logger.debug(f"📦 Cache HIT for {url[:50]}...")
                return Response(
                    content=cached_data['content'],
                    media_type=cached_data['content_type'],
                    headers={
                        'Cache-Control': 'public, max-age=86400',
                        'Access-Control-Allow-Origin': '*',
                        'X-Cache': 'HIT'
                    }
                )
            
            # Fetch image with multiple retry strategies
            headers_list = [
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': 'https://www.imdb.com/',
                    'sec-ch-ua': '"Chromium";v="91", " Not A;Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Accept': 'image/*,*/*;q=0.8',
                },
                {
                    'User-Agent': 'CineScope/1.0 (+https://cinescopeanalyzer.vercel.app)',
                    'Accept': '*/*',
                }
            ]
            
            for attempt, headers in enumerate(headers_list):
                try:
                    async with httpx.AsyncClient(
                        timeout=15.0,
                        follow_redirects=True,
                        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                    ) as client:
                        
                        response = await client.get(url, headers=headers)
                        
                        if response.status_code == 200:
                            content_type = response.headers.get('content-type', 'image/jpeg')
                            
                            # Basic content validation
                            if len(response.content) < 100:  # Too small to be a real image
                                continue
                                
                            if len(response.content) > 10 * 1024 * 1024:  # Too large (>10MB)
                                logger.warning(f"Image too large: {len(response.content)} bytes")
                                continue
                            
                            # Cache successful response
                            self.cache[cache_key] = {
                                'content': response.content,
                                'content_type': content_type,
                                'timestamp': datetime.now().timestamp()
                            }
                            
                            logger.info(f"✅ Image proxied successfully: {len(response.content)} bytes")
                            
                            return Response(
                                content=response.content,
                                media_type=content_type,
                                headers={
                                    'Cache-Control': 'public, max-age=86400',
                                    'Access-Control-Allow-Origin': '*',
                                    'Access-Control-Allow-Methods': 'GET',
                                    'X-Cache': 'MISS',
                                    'Content-Length': str(len(response.content))
                                }
                            )
                        
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    continue
            
            # All attempts failed - return placeholder
            logger.warning(f"All proxy attempts failed for: {url[:50]}...")
            return await self._generate_placeholder_response()
            
        except Exception as e:
            logger.error(f"Image proxy error: {e}")
            return await self._generate_placeholder_response()
    
    async def _generate_placeholder_response(self) -> Response:
        """Generate a simple placeholder response"""
        # Simple 1x1 pixel PNG in base64
        placeholder_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13'
            b'\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```'
            b'\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        return Response(
            content=placeholder_png,
            media_type='image/png',
            headers={
                'Cache-Control': 'public, max-age=300',  # Cache placeholder for 5 minutes
                'Access-Control-Allow-Origin': '*',
                'X-Placeholder': 'true'
            }
        )

# Global instance
simple_image_proxy = SimpleImageProxyService()
