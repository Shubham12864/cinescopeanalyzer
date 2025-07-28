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
                    # CRITICAL: Fix float conversion errors
                    movie_title = movie.get('title', '')
                    movie_year = movie.get('year', '')
                    
                    # Safe rating conversion
                    rating_value = movie.get('rating') or movie.get('imdbRating') or 0
                    if isinstance(rating_value, str):
                        if rating_value.lower() in ['n/a', 'null', 'none', '']:
                            movie['rating'] = 0.0
                        else:
                            try:
                                movie['rating'] = float(rating_value)
                            except (ValueError, TypeError):
                                movie['rating'] = 0.0
                    else:
                        movie['rating'] = float(rating_value) if rating_value else 0.0
                    
                    # Safe year conversion
                    year_value = movie.get('year')
                    if isinstance(year_value, str):
                        if year_value.lower() in ['n/a', 'null', 'none', '']:
                            movie['year'] = 2023
                        else:
                            try:
                                movie['year'] = int(year_value.split('-')[0]) if '-' in year_value else int(year_value)
                            except (ValueError, TypeError):
                                movie['year'] = 2023
                    else:
                        movie['year'] = int(year_value) if year_value else 2023
                    
                    # Add Reddit reviews with timeout protection
                    if movie_title:
                        try:
                            reddit_reviews = await asyncio.wait_for(
                                self.review_service.get_movie_reviews(movie_title, str(movie_year), limit=2),
                                timeout=3.0  # Reduced from 5 to 3 seconds
                            )
                        except (asyncio.TimeoutError, Exception) as e:
                            logger.warning(f"⚠️ Reddit skipped for {movie_title}: {e}")
                            reddit_reviews = []
                        
                        movie.update({
                            'reddit_reviews': reddit_reviews,
                            'review_count': len(reddit_reviews),
                            'has_reddit_reviews': len(reddit_reviews) > 0
                        })
                    
                    final_results.append(movie)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Movie processing error: {e}")
                    # Still include movie with safe defaults
                    movie.update({
                        'rating': 0.0,
                        'year': 2023,
                        'reddit_reviews': [],
                        'review_count': 0,
                        'has_reddit_reviews': False
                    })
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
    
    def _safe_convert_movie_data(self, movie_data: dict) -> dict:
        """Safely convert movie data with proper error handling"""
        safe_movie = {}
        
        # Safe string fields
        safe_movie['title'] = str(movie_data.get('title', 'Unknown Movie'))
        safe_movie['plot'] = str(movie_data.get('plot', 'No plot available'))
        safe_movie['director'] = str(movie_data.get('director', 'Unknown Director'))
        
        # Safe numeric fields
        try:
            rating = movie_data.get('rating') or movie_data.get('imdbRating') or 0
            if isinstance(rating, str) and rating.lower() in ['n/a', 'null', 'none', '']:
                safe_movie['rating'] = 0.0
            else:
                safe_movie['rating'] = float(rating)
        except (ValueError, TypeError):
            safe_movie['rating'] = 0.0
        
        try:
            year = movie_data.get('year') or 2023
            if isinstance(year, str):
                if year.lower() in ['n/a', 'null', 'none', '']:
                    safe_movie['year'] = 2023
                else:
                    safe_movie['year'] = int(year.split('-')[0]) if '-' in year else int(year)
            else:
                safe_movie['year'] = int(year)
        except (ValueError, TypeError):
            safe_movie['year'] = 2023
        
        # Safe list fields
        genre = movie_data.get('genre', [])
        if isinstance(genre, str):
            safe_movie['genre'] = [g.strip() for g in genre.split(',') if g.strip()]
        else:
            safe_movie['genre'] = list(genre) if genre else []
        
        # Safe poster field
        poster = movie_data.get('poster', '')
        if poster and poster.lower() not in ['n/a', 'null', 'none']:
            safe_movie['poster'] = str(poster)
        else:
            safe_movie['poster'] = f"https://via.placeholder.com/300x450/333333/ffffff?text={safe_movie['title'].replace(' ', '+')}"
        
        # IDs
        safe_movie['id'] = str(movie_data.get('id', movie_data.get('imdbId', f"movie_{hash(safe_movie['title'])}")))
        safe_movie['imdbId'] = str(movie_data.get('imdbId', safe_movie['id']))
        
        return safe_movie

# Global service instance
enhanced_movie_service = EnhancedMovieService()

# Export main functions for compatibility with existing API routes
async def search_movies_enhanced(query: str, limit: int = 20, user_context: Dict = None) -> List[Dict[str, Any]]:
    """Enhanced movie search for webapp - maintains API compatibility"""
    return await enhanced_movie_service.search_movies(query, limit, user_context)

async def get_movie_details_enhanced(imdb_id: str) -> Optional[Dict[str, Any]]:
    """Get enhanced movie details for webapp - maintains API compatibility"""
    return await enhanced_movie_service.get_movie_details(imdb_id)
