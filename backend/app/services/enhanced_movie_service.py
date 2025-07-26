#!/usr/bin/env python3
"""
Enhanced Movie Service with Complete Pipeline Integration

        logger.info(f"🚀 COMPLETE PIPELINE SEARCH: '{query}' (limit: {limit})")
        
        try:
            # CACHE CHECK: Try to get cached results first
            logger.info("🗄️ CACHE CHECK: Looking for cached results")
            cached_results = await self.cache_service.get_search_results(query, limit)
            if cached_results:
                logger.info(f"⚡ CACHE HIT: Returning {len(cached_results)} cached results")
                return cached_results
            
            # STEP 1: SEARCH with OMDB + Scrapy (content only)PP ARCHITECTURE:
1. SEARCH & DETAILS: OMDB API + Scrapy (NO TMDB, NO OMDB IMAGES)
2. IMAGES: FanArt API ONLY (for cards and everywhere)
3. REVIEWS: Reddit API (user discussions and reviews)
4. CACHING: Enhanced database caching for performance
5. USAGE: Complete webapp integration

Perfect for movie cards, detailed views, and all webapp components
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import existing working services + Reddit + Enhanced Caching
from .unified_search_service import unified_search_service
from .fanart_api_service import fanart_service
from .reddit_review_service import reddit_review_service
from .enhanced_cache_service import enhanced_cache_service

logger = logging.getLogger(__name__)

class EnhancedMovieService:
    """
    Enhanced Movie Service with COMPLETE PIPELINE:
    
    YOUR EXACT PIPELINE IMPLEMENTED:
    1. SEARCH & DETAILS: OMDB API + Scrapy (content only, NO OMDB images) 
    2. IMAGES: FanArt API ONLY (replacing ALL Amazon URLs)
    3. REVIEWS: Reddit API (real user discussions)
    4. CACHING: Multi-layer database caching for performance
    
    PERFECT FOR WEBAPP: Cards, listings, detailed views
    """
    
    def __init__(self):
        self.is_initialized = False
        self.search_service = unified_search_service
        self.image_service = fanart_service  
        self.review_service = reddit_review_service  # Reddit reviews
        self.cache_service = enhanced_cache_service  # Enhanced caching
        
        logger.info("🎬 Enhanced Movie Service with COMPLETE PIPELINE")
        logger.info("🔍 SEARCH: OMDB + Scrapy (content only)")
        logger.info("🖼️ IMAGES: FanArt API (NO Amazon URLs)")
        logger.info("💬 REVIEWS: Reddit API (user discussions)")
        logger.info("🗄️ CACHING: Enhanced database caching")
    
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
                
                # Initialize Reddit review service
                await self.review_service.initialize()
                logger.info("✅ Reddit review service ready")
                
                self.is_initialized = True
                logger.info("✅ COMPLETE PIPELINE READY - All services initialized!")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize complete pipeline: {e}")
                raise
    
    async def close(self):
        """Close all service components"""
        if self.is_initialized:
            try:
                # Close all services
                await self.search_service.close()
                await self.image_service.close()
                await self.review_service.close()
                
                self.is_initialized = False
                logger.info("🔒 Enhanced Movie Service closed - All sessions closed")
                
            except Exception as e:
                logger.error(f"❌ Error closing services: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def search_movies(self, query: str, limit: int = 20, user_context: Dict = None) -> List[Dict[str, Any]]:
        """
        COMPLETE PIPELINE SEARCH for webapp
        
        YOUR EXACT IMPLEMENTATION:
        1. SEARCH: OMDB API + Scrapy (content only, NO OMDB images)
        2. IMAGES: FanArt API ONLY (replace ALL Amazon URLs) 
        3. REVIEWS: Reddit API (real user discussions)
        
        Perfect for webapp cards and listings!
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"� COMPLETE PIPELINE SEARCH: '{query}' (limit: {limit})")
        
        try:
            # STEP 1: SEARCH with OMDB + Scrapy (content only)
            logger.info("🔍 STEP 1: OMDB + Scrapy search (content only)")
            search_results = await self.search_service.search_movies(query, limit)
            
            if not search_results:
                logger.warning(f"⚠️ No search results found for: '{query}'")
                return []
            
            logger.info(f"✅ STEP 1 COMPLETE: {len(search_results)} movies found")
            
            # STEP 2: IMAGES with FanArt API (replace ALL Amazon URLs)
            logger.info("🖼️ STEP 2: FanArt API images (replacing Amazon URLs)")
            enhanced_results = await self.image_service.batch_enhance_movies(search_results)
            
            logger.info(f"✅ STEP 2 COMPLETE: {len(enhanced_results)} movies enhanced with FanArt")
            
            # STEP 3: REVIEWS with Reddit API (non-blocking)
            logger.info("💬 STEP 3: Reddit API reviews (user discussions)")
            final_results = []
            
            for movie in enhanced_results:
                try:
                    # Get Reddit reviews for each movie (with timeout)
                    movie_title = movie.get('title', '')
                    movie_year = movie.get('year', '')
                    
                    if movie_title:
                        # Use asyncio.wait_for to timeout Reddit calls quickly
                        try:
                            reddit_reviews = await asyncio.wait_for(
                                self.review_service.get_movie_reviews(movie_title, movie_year, limit=3),
                                timeout=5.0  # Only wait 5 seconds for Reddit
                            )
                        except asyncio.TimeoutError:
                            logger.warning(f"⚠️ Reddit timeout for: {movie_title}")
                            reddit_reviews = []
                        except Exception as reddit_error:
                            logger.warning(f"⚠️ Reddit error for {movie_title}: {reddit_error}")
                            reddit_reviews = []
                        
                        # Add Reddit data to movie
                        movie.update({
                            'reddit_reviews': reddit_reviews,
                            'review_count': len(reddit_reviews),
                            'has_reddit_reviews': len(reddit_reviews) > 0,
                            'top_reddit_score': max([r.get('score', 0) for r in reddit_reviews]) if reddit_reviews else 0,
                            'review_subreddits': list(set([r.get('subreddit') for r in reddit_reviews])) if reddit_reviews else []
                        })
                        
                        logger.debug(f"📝 Added {len(reddit_reviews)} Reddit reviews for: {movie_title}")
                    
                    # Add complete pipeline metadata
                    movie.update({
                        'search_timestamp': datetime.now().isoformat(),
                        'search_query': query,
                        'webapp_ready': True,
                        'complete_pipeline': True,
                        'pipeline_steps': ['omdb_scrapy_search', 'fanart_images', 'reddit_reviews'],
                        'enhanced_with_fanart': movie.get('poster_source') == 'fanart',
                        'amazon_urls_removed': movie.get('amazon_url_replaced', False),
                        'user_context': user_context or {}
                    })
                    
                    # FRONTEND COMPATIBILITY: Add frontend-expected field names
                    # Handle poster field mapping (check multiple possible field names)
                    poster_field = None
                    for field_name in ['poster_url', 'poster', 'Poster', 'fanart_poster']:
                        if movie.get(field_name):
                            poster_field = movie[field_name]
                            break
                    
                    if poster_field:
                        movie['poster'] = poster_field  # Frontend expects 'poster'
                    elif movie.get('imdb_id'):
                        # Fallback: Use a placeholder or default image
                        movie['poster'] = f"https://via.placeholder.com/300x450?text={movie.get('title', 'Movie').replace(' ', '+')}"
                    
                    if movie.get('imdb_id'):
                        movie['imdbId'] = movie['imdb_id']     # Frontend expects 'imdbId'
                        movie['id'] = movie['imdb_id']         # Frontend expects 'id'
                    if movie.get('imdbRating'):
                        movie['rating'] = float(movie.get('imdbRating', 0))  # Frontend expects 'rating'
                    elif movie.get('rating'):
                        movie['rating'] = float(movie.get('rating', 0))  # Frontend expects 'rating'
                    if movie.get('genre'):
                        movie['genre'] = movie['genre'].split(', ') if isinstance(movie['genre'], str) else movie.get('genre', [])
                    
                    final_results.append(movie)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to add Reddit reviews for movie: {e}")
                    # Still include movie without Reddit reviews
                    movie.update({
                        'reddit_reviews': [],
                        'review_count': 0,
                        'has_reddit_reviews': False,
                        'complete_pipeline': True,
                        'pipeline_steps': ['omdb_scrapy_search', 'fanart_images'],
                        'reddit_error': str(e)
                    })
                    
                    # FRONTEND COMPATIBILITY: Add frontend-expected field names
                    # Handle poster field mapping (check multiple possible field names)
                    poster_field = None
                    for field_name in ['poster_url', 'poster', 'Poster', 'fanart_poster']:
                        if movie.get(field_name):
                            poster_field = movie[field_name]
                            break
                    
                    if poster_field:
                        movie['poster'] = poster_field  # Frontend expects 'poster'
                    elif movie.get('imdb_id'):
                        # Fallback: Use a placeholder or default image
                        movie['poster'] = f"https://via.placeholder.com/300x450?text={movie.get('title', 'Movie').replace(' ', '+')}"
                    
                    if movie.get('imdb_id'):
                        movie['imdbId'] = movie['imdb_id']     # Frontend expects 'imdbId'
                        movie['id'] = movie['imdb_id']         # Frontend expects 'id'
                    if movie.get('imdbRating'):
                        movie['rating'] = float(movie.get('imdbRating', 0))  # Frontend expects 'rating'
                    elif movie.get('rating'):
                        movie['rating'] = float(movie.get('rating', 0))  # Frontend expects 'rating'
                    if movie.get('genre'):
                        movie['genre'] = movie['genre'].split(', ') if isinstance(movie['genre'], str) else movie.get('genre', [])
                    
                    final_results.append(movie)
            
            logger.info(f"✅ STEP 3 COMPLETE: {len(final_results)} movies with Reddit reviews")
            
            # STEP 4: CACHE STORAGE - Store results for future requests
            logger.info("🗄️ STEP 4: Storing results in enhanced cache")
            try:
                # Store search results (1-hour TTL for searches)
                await self.cache_service.store_search_results(query, final_results, limit, ttl_hours=1)
                
                # Store individual movie data (24-hour TTL for movies)
                for movie in final_results:
                    movie_id = movie.get('imdb_id') or movie.get('title', '')
                    if movie_id:
                        await self.cache_service.store_movie_data(movie_id, movie, ttl_hours=24)
                
                logger.info(f"💾 Cached {len(final_results)} movies with enhanced database caching")
            except Exception as cache_error:
                logger.warning(f"⚠️ Cache storage error: {cache_error}")
            
            # PIPELINE SUMMARY
            logger.info("🏆 COMPLETE PIPELINE SUCCESS!")
            logger.info(f"🔍 SEARCH: {len(search_results)} from OMDB + Scrapy")
            logger.info(f"🖼️ IMAGES: {len([m for m in final_results if m.get('fanart_enhanced')])} with FanArt")
            logger.info(f"💬 REVIEWS: {len([m for m in final_results if m.get('has_reddit_reviews')])} with Reddit")
            logger.info(f"🗄️ CACHE: Enhanced database caching active")
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ COMPLETE PIPELINE FAILED: {e}")
            return []
    
    async def get_movie_details(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed movie information with COMPLETE PIPELINE
        
        YOUR EXACT IMPLEMENTATION:
        1. SEARCH: OMDB details (content only, NO OMDB images)
        2. IMAGES: FanArt API enhancement (replace Amazon URLs)
        3. REVIEWS: Reddit API reviews (detailed discussions)
        
        Perfect for webapp detailed movie views!
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"🎯 COMPLETE PIPELINE DETAILS: {imdb_id}")
        
        try:
            # STEP 1: Get movie details from search service (content only)
            logger.info("🔍 STEP 1: Getting OMDB details (content only)")
            movie_details = await self.search_service.get_movie_details(imdb_id)
            
            if not movie_details:
                logger.warning(f"⚠️ No details found for: {imdb_id}")
                return None
            
            logger.info("✅ STEP 1 COMPLETE: OMDB details retrieved")
            
            # STEP 2: Enhance with FanArt images (replace Amazon URLs)
            logger.info("🖼️ STEP 2: FanArt API enhancement")
            enhanced_details = await self.image_service.enhance_movie_with_fanart(movie_details)
            
            logger.info("✅ STEP 2 COMPLETE: FanArt images added")
            
            # STEP 3: Get comprehensive Reddit reviews
            logger.info("💬 STEP 3: Reddit API reviews (comprehensive)")
            movie_title = enhanced_details.get('title', '')
            movie_year = enhanced_details.get('year', '')
            
            if movie_title:
                # Get more comprehensive reviews for detailed view
                reddit_reviews = await self.review_service.get_movie_reviews(
                    movie_title, movie_year, limit=15  # More reviews for details
                )
                
                # Add comprehensive Reddit data
                enhanced_details.update({
                    'reddit_reviews': reddit_reviews,
                    'review_count': len(reddit_reviews),
                    'has_reddit_reviews': len(reddit_reviews) > 0,
                    'reddit_stats': {
                        'total_reviews': len(reddit_reviews),
                        'avg_score': sum([r.get('score', 0) for r in reddit_reviews]) / len(reddit_reviews) if reddit_reviews else 0,
                        'total_comments': sum([r.get('num_comments', 0) for r in reddit_reviews]),
                        'subreddits': list(set([r.get('subreddit') for r in reddit_reviews])),
                        'review_types': {
                            'discussions': len([r for r in reddit_reviews if r.get('is_discussion')]),
                            'reviews': len([r for r in reddit_reviews if r.get('is_review')]),
                            'general': len([r for r in reddit_reviews if not r.get('is_discussion') and not r.get('is_review')])
                        }
                    }
                })
                
                logger.info(f"✅ STEP 3 COMPLETE: {len(reddit_reviews)} Reddit reviews added")
            
            # Add complete pipeline metadata
            enhanced_details.update({
                'details_timestamp': datetime.now().isoformat(),
                'detail_view_optimized': True,
                'webapp_ready': True,
                'complete_pipeline': True,
                'pipeline_steps': ['omdb_details', 'fanart_images', 'reddit_reviews'],
                'enhanced_with_fanart': enhanced_details.get('poster_source') == 'fanart',
                'amazon_urls_removed': enhanced_details.get('amazon_url_replaced', False)
            })
            
            logger.info(f"🏆 COMPLETE PIPELINE DETAILS SUCCESS: {enhanced_details.get('title')}")
            return enhanced_details
            
        except Exception as e:
            logger.error(f"❌ COMPLETE PIPELINE DETAILS FAILED: {e}")
            return None

# Global service instance
enhanced_movie_service = EnhancedMovieService()

# Export main functions for compatibility with existing API routes
async def search_movies_enhanced(query: str, limit: int = 20, user_context: Dict = None) -> List[Dict[str, Any]]:
    """Enhanced movie search for webapp - maintains API compatibility"""
    return await enhanced_movie_service.search_movies(query, limit, user_context)

async def get_movie_details_enhanced(imdb_id: str) -> Optional[Dict[str, Any]]:
    """Get enhanced movie details for webapp - maintains API compatibility"""
    return await enhanced_movie_service.get_movie_details(imdb_id)
