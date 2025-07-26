#!/usr/bin/env python3
"""
Enhanced Movie Service with Unified Search and FanArt Images
- OMDB API + Robust Scraping + Scrapy (NO TMDB)
- FanArt.tv for high-quality dynamic image loading
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import unified search and FanArt services
from .unified_search_service import unified_search_service
from .fanart_api_service import fanart_service

logger = logging.getLogger(__name__)

class EnhancedMovieService:
    """
    Enhanced Movie Service with:
    
    SEARCH WORKFLOW:
    1. OMDB API (Primary) - API key: 4977b044
    2. Robust Scraping - Enhanced IMDb scraping
    3. Scrapy Search - Comprehensive web scraping
    
    IMAGE LOADING:
    - FanArt.tv API (API key: fb2b79b4e05ed6d3452f751ddcf38bda)
    - Replaces OMDB Amazon URLs with high-quality images
    
    NO TMDB API - Complete OMDB + Scraping + FanArt solution
    """
    
    def __init__(self):
        self.is_initialized = False
        self.search_service = unified_search_service
        self.image_service = fanart_service
        
        logger.info("🎬 Enhanced Movie Service initialized (OMDB + Scraping + FanArt)")
    
    async def initialize(self):
        """Initialize all service components"""
        if not self.is_initialized:
            try:
                # Initialize search service
                await self.search_service.initialize()
                logger.info("✅ Unified search service ready")
                
                # Initialize image service
                await self.image_service.initialize()
                logger.info("✅ FanArt image service ready")
                
                self.is_initialized = True
                logger.info("🚀 Enhanced Movie Service fully initialized")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize enhanced movie service: {e}")
                raise

    async def search_movies(self, query: str, limit: int = 20, user_context: Dict = None) -> List[Dict[str, Any]]:
        """
        Enhanced movie search with unified search + FanArt images
        
        Args:
            query: Movie title to search for
            limit: Maximum number of results
            user_context: User preferences (optional)
            
        Returns:
            List of movies with high-quality FanArt images
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"🔍 Enhanced search started: '{query}' (limit: {limit})")
        
        try:
            # Step 1: Search using unified service (OMDB + Scraping + Scrapy)
            search_results = await self.search_service.search_movies(query, limit)
            
            if not search_results:
                logger.warning(f"⚠️ No search results found for: '{query}'")
                return []
            
            logger.info(f"✅ Found {len(search_results)} search results")
            
            # Step 2: Enhance with FanArt images
            enhanced_results = await self.image_service.batch_enhance_movies(search_results)
            
            logger.info(f"🎨 Enhanced {len(enhanced_results)} movies with FanArt images")
            
            # Step 3: Add metadata
            final_results = []
            for movie in enhanced_results:
                movie.update({
                    'search_timestamp': datetime.now().isoformat(),
                    'search_query': query,
                    'enhanced_with_fanart': 'poster_source' in movie and movie['poster_source'] == 'fanart'
                })
                final_results.append(movie)
            
            logger.info(f"🎬 Enhanced search completed: {len(final_results)} results")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Enhanced search failed: {e}")
            return []

    async def get_movie_details(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed movie information with FanArt images
        
        Args:
            imdb_id: IMDb ID for the movie
            
        Returns:
            Detailed movie dictionary with FanArt images
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"🎯 Getting movie details: {imdb_id}")
        
        try:
            # Get movie details from search service
            movie_details = await self.search_service.get_movie_details(imdb_id)
            
            if not movie_details:
                logger.warning(f"⚠️ No movie details found for: {imdb_id}")
                return None
            
            # Enhance with FanArt images
            enhanced_details = await self.image_service.enhance_movie_with_fanart(movie_details)
            
            # Add metadata
            enhanced_details.update({
                'details_timestamp': datetime.now().isoformat(),
                'enhanced_with_fanart': 'poster_source' in enhanced_details and enhanced_details['poster_source'] == 'fanart'
            })
            
            logger.info(f"✅ Movie details retrieved and enhanced: {imdb_id}")
            return enhanced_details
            
        except Exception as e:
            logger.error(f"❌ Failed to get movie details: {e}")
            return None

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            search_stats = self.search_service.get_search_stats()
            fanart_stats = self.image_service.get_cache_stats()
            
            return {
                'search_service': search_stats,
                'image_service': fanart_stats,
                'initialized': self.is_initialized,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get service stats: {e}")
            return {}

    async def close(self):
        """Clean up all service resources"""
        try:
            await self.search_service.close()
            await self.image_service.close()
            logger.info("🧹 Enhanced Movie Service closed")
        except Exception as e:
            logger.error(f"❌ Error closing service: {e}")

# Global service instance
enhanced_movie_service = EnhancedMovieService()

# Export main functions for compatibility
async def search_movies_enhanced(query: str, limit: int = 20, user_context: Dict = None) -> List[Dict[str, Any]]:
    """Enhanced movie search with unified search + FanArt images"""
    return await enhanced_movie_service.search_movies(query, limit, user_context)

async def get_movie_details_enhanced(imdb_id: str) -> Optional[Dict[str, Any]]:
    """Get enhanced movie details with FanArt images"""
    return await enhanced_movie_service.get_movie_details(imdb_id)
