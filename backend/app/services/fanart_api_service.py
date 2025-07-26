#!/usr/bin/env python3
"""
FanArt API Service for Dynamic Image Loading
Replaces OMDB Amazon URLs with high-quality FanArt.tv images
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp
import json
from urllib.parse import quote
import time
import os

logger = logging.getLogger(__name__)

class FanArtAPIService:
    """
    FanArt.tv API service for high-quality movie images
    
    API Key: fb2b79b4e05ed6d3452f751ddcf38bda
    Provides: Movie posters, backgrounds, logos, thumbnails
    
    Replaces OMDB Amazon URLs with FanArt.tv high-quality images
    """
    
    def __init__(self):
        self.api_key = os.getenv("FANART_API_KEY", "fb2b79b4e05ed6d3452f751ddcf38bda")
        self.base_url = "https://webservice.fanart.tv/v3/movies"
        self.session = None
        
        # Image type priorities (highest quality first)
        self.image_priorities = {
            'poster': ['movieposter', 'moviethumb'],
            'background': ['moviebackground', 'movieart'],
            'logo': ['movielogo', 'hdmovielogo'],
            'thumbnail': ['moviethumb', 'movieposter']
        }
        
        # Cache for FanArt results
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        logger.info(f"🎨 FanArt API initialized with key: {self.api_key[:8]}****")
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ FanArt API session initialized")

    async def get_movie_poster(self, imdb_id: str) -> Optional[str]:
        """Get high-quality poster from FanArt API - BLOCKS AMAZON URLs"""
        try:
            if not imdb_id:
                return None
                
            # Check cache first
            cache_key = f"poster_{imdb_id}"
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_ttl:
                    return cached_result['url']
            
            if not self.session:
                await self.initialize()
            
            url = f"{self.base_url}/{imdb_id}"
            params = {"api_key": self.api_key}
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Get highest quality poster
                    for image_type in self.image_priorities['poster']:
                        if image_type in data and data[image_type]:
                            images = data[image_type]
                            # Sort by likes and get highest quality
                            best_image = max(images, key=lambda x: x.get("likes", 0))
                            poster_url = best_image.get("url")
                            
                            # CRITICAL: Block Amazon URLs
                            if poster_url and not self._is_amazon_url(poster_url):
                                # Cache the result
                                self.cache[cache_key] = {
                                    'url': poster_url,
                                    'timestamp': time.time()
                                }
                                logger.info(f"✅ FanArt poster found: {imdb_id}")
                                return poster_url
                            else:
                                logger.warning(f"🚫 Blocked Amazon URL from FanArt: {imdb_id}")
                                
        except Exception as e:
            logger.warning(f"⚠️ FanArt API failed for {imdb_id}: {e}")
        
        return None
    
    def _is_amazon_url(self, url: str) -> bool:
        """Check if URL is from Amazon (to be blocked)"""
        if not url:
            return False
        amazon_patterns = [
            'm.media-amazon.com',
            'images-amazon.com',
            'amazon-images',
            'amazonaws.com'
        ]
        return any(pattern in url.lower() for pattern in amazon_patterns)
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("🔒 FanArt API session closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def get_movie_images(self, imdb_id: str) -> Dict[str, Any]:
        """
        Get high-quality movie images from FanArt.tv
        
        Args:
            imdb_id: IMDb ID (e.g., 'tt0133093')
            
        Returns:
            Dictionary with image URLs by type
        """
        if not imdb_id or not imdb_id.startswith('tt'):
            logger.warning(f"⚠️ Invalid IMDb ID: {imdb_id}")
            return {}
        
        # Check cache first
        cache_key = f"fanart_{imdb_id}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"🎯 FanArt cache hit for: {imdb_id}")
                return cached_data
        
        try:
            # Ensure session is available (reinitialize if closed)
            if not self.session or self.session.closed:
                await self.initialize()
            
            # FanArt API URL
            url = f"{self.base_url}/{imdb_id}"
            headers = {
                'api-key': self.api_key,
                'User-Agent': 'CineScopeAnalyzer/1.0'
            }
            
            logger.info(f"🎨 Fetching FanArt images for: {imdb_id}")
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    images = self._process_fanart_response(data)
                    
                    # Cache the results
                    self.cache[cache_key] = (images, time.time())
                    
                    logger.info(f"✅ FanArt images found: {len(images)} types")
                    return images
                    
                elif response.status == 404:
                    logger.info(f"ℹ️ No FanArt images found for: {imdb_id}")
                    return {}
                    
                else:
                    logger.warning(f"⚠️ FanArt API error {response.status}: {await response.text()}")
                    return {}
        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ FanArt API timeout for: {imdb_id}")
            return {}
        except Exception as e:
            logger.error(f"❌ FanArt API error: {e}")
            return {}
    
    def _process_fanart_response(self, data: Dict) -> Dict[str, Any]:
        """Process FanArt API response and extract best images"""
        images = {
            'poster': [],
            'background': [],
            'logo': [],
            'thumbnail': []
        }
        
        try:
            # Process different image types
            for image_type, fanart_keys in self.image_priorities.items():
                for fanart_key in fanart_keys:
                    if fanart_key in data:
                        fanart_images = data[fanart_key]
                        
                        # Sort by likes (most popular first)
                        if isinstance(fanart_images, list):
                            fanart_images.sort(key=lambda x: int(x.get('likes', 0)), reverse=True)
                            
                            for img in fanart_images[:3]:  # Top 3 images
                                url = img.get('url')
                                if url:
                                    images[image_type].append({
                                        'url': url,
                                        'likes': int(img.get('likes', 0)),
                                        'lang': img.get('lang', 'en'),
                                        'source': 'fanart'
                                    })
            
            # Get the best image for each type
            best_images = {}
            for img_type, img_list in images.items():
                if img_list:
                    best_images[img_type] = img_list[0]['url']  # Highest liked image
                    best_images[f"{img_type}_all"] = [img['url'] for img in img_list]
            
            return best_images
            
        except Exception as e:
            logger.error(f"❌ Error processing FanArt response: {e}")
            return {}
    
    async def get_poster_url(self, imdb_id: str, fallback_url: str = None) -> str:
        """
        Get the best poster URL for a movie
        
        Args:
            imdb_id: IMDb ID
            fallback_url: Fallback URL if FanArt not available
            
        Returns:
            Best available poster URL
        """
        try:
            images = await self.get_movie_images(imdb_id)
            poster_url = images.get('poster')
            
            if poster_url:
                logger.debug(f"🎨 FanArt poster found for: {imdb_id}")
                return poster_url
            
            # Use fallback if provided and not an Amazon URL
            if fallback_url and not self._is_amazon_url(fallback_url):
                logger.debug(f"🔄 Using fallback poster for: {imdb_id}")
                return fallback_url
            
            logger.info(f"ℹ️ No poster available for: {imdb_id}")
            return ""
            
        except Exception as e:
            logger.error(f"❌ Error getting poster URL: {e}")
            return fallback_url or ""
    
    async def get_background_url(self, imdb_id: str, fallback_url: str = None) -> str:
        """Get the best background image URL for a movie"""
        try:
            images = await self.get_movie_images(imdb_id)
            bg_url = images.get('background')
            
            if bg_url:
                logger.debug(f"🎨 FanArt background found for: {imdb_id}")
                return bg_url
            
            return fallback_url or ""
            
        except Exception as e:
            logger.error(f"❌ Error getting background URL: {e}")
            return fallback_url or ""
    
    def _is_amazon_url(self, url: str) -> bool:
        """Check if URL is from Amazon (OMDB often returns these)"""
        amazon_domains = [
            'amazon.com',
            'media-amazon.com',
            'm.media-amazon.com',
            'images-amazon.com'
        ]
        return any(domain in url.lower() for domain in amazon_domains)
    
    async def enhance_movie_with_fanart(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance movie data with FanArt images - REPLACES ALL OMDB/Amazon URLs
        
        Args:
            movie: Movie dictionary with 'imdb_id' field
            
        Returns:
            Enhanced movie dictionary with FanArt images (NO Amazon URLs)
        """
        # Check for imdb_id (fixed field name)
        imdb_id = movie.get('imdb_id') or movie.get('imdbID')
        if not imdb_id:
            logger.warning("⚠️ No IMDb ID provided for FanArt enhancement")
            return movie
        
        try:
            # Get FanArt images
            fanart_images = await self.get_movie_images(imdb_id)
            
            if fanart_images:
                # FORCE REPLACE poster_url with FanArt (remove Amazon URLs)
                original_poster = movie.get('poster_url', '')
                if fanart_images.get('poster'):
                    movie['poster_url'] = fanart_images['poster']  # Fixed field name
                    movie['poster_original'] = original_poster
                    movie['poster_source'] = 'fanart'
                    movie['amazon_url_replaced'] = self._is_amazon_url(original_poster)
                    logger.info(f"🎨 Replaced {'Amazon' if self._is_amazon_url(original_poster) else 'OMDB'} poster with FanArt")
                else:
                    # If no FanArt poster available, remove Amazon URLs entirely
                    if self._is_amazon_url(original_poster):
                        movie['poster_url'] = None  # Remove Amazon URL
                        movie['poster_source'] = 'removed_amazon'
                        movie['amazon_url_removed'] = True
                        logger.info("🚫 Removed Amazon URL - no FanArt available")
                
                # Add additional FanArt image types for webapp
                if fanart_images.get('background'):
                    movie['background_url'] = fanart_images['background']
                
                if fanart_images.get('logo'):
                    movie['logo_url'] = fanart_images['logo']
                
                if fanart_images.get('thumbnail'):
                    movie['thumbnail_url'] = fanart_images['thumbnail']
                
                # Add all available images for webapp flexibility
                for img_type in ['poster', 'background', 'logo', 'thumbnail']:
                    all_key = f"{img_type}_all"
                    if fanart_images.get(all_key):
                        movie[f"fanart_{img_type}s"] = fanart_images[all_key]
                
                # Mark as webapp ready
                movie['webapp_images_ready'] = True
                movie['fanart_enhanced'] = True
                
                logger.debug(f"✅ Movie enhanced with FanArt images: {imdb_id}")
            else:
                # No FanArt available - remove Amazon URLs anyway
                original_poster = movie.get('poster_url', '')
                if self._is_amazon_url(original_poster):
                    movie['poster_url'] = None
                    movie['poster_source'] = 'removed_amazon_no_fanart'
                    movie['amazon_url_removed'] = True
                    logger.info("🚫 Removed Amazon URL - FanArt API has no images for this movie")
            
            return movie
            
        except Exception as e:
            logger.error(f"❌ Error enhancing movie with FanArt: {e}")
            # Still remove Amazon URLs even on error
            original_poster = movie.get('poster_url', '')
            if self._is_amazon_url(original_poster):
                movie['poster_url'] = None
                movie['poster_source'] = 'removed_amazon_error'
                movie['amazon_url_removed'] = True
                logger.info("🚫 Removed Amazon URL due to FanArt error")
            return movie
            return movie
    
    async def batch_enhance_movies(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance multiple movies with FanArt images in parallel
        
        Args:
            movies: List of movie dictionaries
            
        Returns:
            List of enhanced movie dictionaries
        """
        if not movies:
            return movies
        
        logger.info(f"🎨 Enhancing {len(movies)} movies with FanArt images...")
        
        try:
            # Process movies in parallel (but with reasonable concurrency)
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
            
            async def enhance_single(movie):
                async with semaphore:
                    return await self.enhance_movie_with_fanart(movie)
            
            enhanced_movies = await asyncio.gather(
                *[enhance_single(movie) for movie in movies],
                return_exceptions=True
            )
            
            # Filter out any exceptions
            valid_movies = []
            for i, result in enumerate(enhanced_movies):
                if isinstance(result, Exception):
                    logger.warning(f"⚠️ Failed to enhance movie {i}: {result}")
                    valid_movies.append(movies[i])  # Use original
                else:
                    valid_movies.append(result)
            
            logger.info(f"✅ Enhanced {len(valid_movies)} movies with FanArt")
            return valid_movies
            
        except Exception as e:
            logger.error(f"❌ Batch enhancement failed: {e}")
            return movies
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'api_key': f"{self.api_key[:8]}****"
        }
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            logger.info("🧹 FanArt API session closed")

# Global service instance
fanart_service = FanArtAPIService()
