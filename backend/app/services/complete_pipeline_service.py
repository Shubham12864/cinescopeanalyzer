#!/usr/bin/env python3
"""
Complete Pipeline Service for CineScope WebApp

ARCHITECTURE:
1. SEARCH & DETAILS: OMDB API + Scrapy (NO TMDB, NO OMDB IMAGES)
2. IMAGES: FanArt API ONLY (for cards and everywhere)
3. REVIEWS: Reddit API
4. USAGE: Complete webapp integration

Pipeline Flow:
Search → OMDB/Scrapy → Details → FanArt Images → Reddit Reviews
"""
import asyncio
import logging
import aiohttp
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class CompletePipelineService:
    """
    Complete webapp pipeline service with specialized APIs:
    
    SEARCH LAYER: OMDB API + Scrapy (content only)
    IMAGE LAYER: FanArt API (all images for cards/webapp)
    REVIEW LAYER: Reddit API (user reviews and discussions)
    """
    
    def __init__(self):
        # API Configuration
        self.omdb_api_key = os.getenv("OMDB_API_KEY", "4977b044")
        self.fanart_api_key = os.getenv("FANART_API_KEY", "fb2b79b4e05ed6d3452f751ddcf38bda")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        
        # API Endpoints
        self.omdb_base_url = "http://www.omdbapi.com/"
        self.fanart_base_url = "https://webservice.fanart.tv/v3/movies"
        self.reddit_base_url = "https://www.reddit.com"
        
        # HTTP Session
        self.session = None
        self.is_initialized = False
        
        # Cache for performance
        self.cache = {
            'movies': {},      # Movie details cache
            'images': {},      # FanArt images cache
            'reviews': {},     # Reddit reviews cache
        }
        
        logger.info("🎬 Complete Pipeline Service initialized")
        logger.info("🔍 SEARCH: OMDB API + Scrapy")
        logger.info("🖼️ IMAGES: FanArt API Only")
        logger.info("💬 REVIEWS: Reddit API")
    
    async def initialize(self):
        """Initialize the complete pipeline service"""
        if not self.is_initialized:
            self.session = aiohttp.ClientSession()
            self.is_initialized = True
            logger.info("✅ Complete Pipeline Service ready")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    # ========================================
    # SEARCH & DETAILS LAYER (OMDB + Scrapy)
    # ========================================
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search movies using OMDB API + Scrapy (NO TMDB, NO OMDB IMAGES)
        Returns movie data with metadata for image enhancement
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"🔍 SEARCH LAYER: Searching '{query}' (OMDB + Scrapy)")
        
        try:
            # Step 1: OMDB API Search (content only, ignore images)
            omdb_results = await self._search_omdb_content_only(query, limit)
            
            # Step 2: Enhance with Scrapy if needed (content only)
            if len(omdb_results) < limit:
                scrapy_results = await self._search_scrapy_content_only(query, limit - len(omdb_results))
                omdb_results.extend(scrapy_results)
            
            # Step 3: Prepare for image enhancement (mark for FanArt)
            for movie in omdb_results:
                movie['needs_fanart_images'] = True  # Mark for FanArt processing
                movie['omdb_poster_ignored'] = True  # Ignore OMDB poster URLs
            
            logger.info(f"✅ SEARCH LAYER: Found {len(omdb_results)} movies (ready for FanArt)")
            return omdb_results[:limit]
            
        except Exception as e:
            logger.error(f"❌ SEARCH LAYER failed: {e}")
            return []
    
    async def _search_omdb_content_only(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search OMDB for content only (ignore image URLs)"""
        try:
            # Search for movies
            search_url = f"{self.omdb_base_url}?apikey={self.omdb_api_key}&s={query}&type=movie"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'True' and 'Search' in data:
                        results = []
                        
                        # Get detailed info for each movie (but ignore poster URLs)
                        for item in data['Search'][:limit]:
                            imdb_id = item.get('imdbID')
                            if imdb_id:
                                details = await self._get_omdb_details_content_only(imdb_id)
                                if details:
                                    results.append(details)
                        
                        return results
            
            return []
            
        except Exception as e:
            logger.error(f"❌ OMDB content search failed: {e}")
            return []
    
    async def _get_omdb_details_content_only(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get OMDB details but ignore poster URLs (FanArt will handle images)"""
        try:
            detail_url = f"{self.omdb_base_url}?apikey={self.omdb_api_key}&i={imdb_id}&plot=full"
            
            async with self.session.get(detail_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'True':
                        return {
                            # Content only (NO IMAGE URLS)
                            'title': data.get('Title', ''),
                            'year': data.get('Year', ''),
                            'imdb_id': data.get('imdbID', ''),
                            'plot': data.get('Plot', ''),
                            'director': data.get('Director', ''),
                            'actors': data.get('Actors', ''),
                            'genre': data.get('Genre', ''),
                            'runtime': data.get('Runtime', ''),
                            'imdb_rating': data.get('imdbRating', ''),
                            'metascore': data.get('Metascore', ''),
                            'awards': data.get('Awards', ''),
                            'language': data.get('Language', ''),
                            'country': data.get('Country', ''),
                            'released': data.get('Released', ''),
                            'rated': data.get('Rated', ''),
                            'writer': data.get('Writer', ''),
                            'production': data.get('Production', ''),
                            'box_office': data.get('BoxOffice', ''),
                            # Metadata
                            'source': 'omdb_content_only',
                            'search_timestamp': datetime.now().isoformat(),
                            # NO POSTER URL - FanArt will handle this
                            'poster_url': None,  # Explicitly null
                            'fanart_required': True
                        }
            return None
            
        except Exception as e:
            logger.error(f"❌ OMDB details failed for {imdb_id}: {e}")
            return None
    
    async def _search_scrapy_content_only(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Scrapy search for additional content (no images)"""
        try:
            # This would integrate with your existing Scrapy service
            # For now, returning empty (implement based on your Scrapy setup)
            logger.info(f"🕷️ Scrapy content search for '{query}' (placeholder)")
            return []
            
        except Exception as e:
            logger.error(f"❌ Scrapy content search failed: {e}")
            return []
    
    # ========================================
    # IMAGE LAYER (FanArt API ONLY)
    # ========================================
    
    async def enhance_movies_with_fanart_images(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance movies with FanArt images ONLY
        This replaces ALL image URLs with FanArt images for webapp cards
        """
        if not movies:
            return movies
        
        logger.info(f"🖼️ IMAGE LAYER: Enhancing {len(movies)} movies with FanArt images")
        
        enhanced_movies = []
        for movie in movies:
            imdb_id = movie.get('imdb_id')
            if imdb_id:
                # Get FanArt images for this movie
                fanart_images = await self._get_fanart_images(imdb_id)
                
                # Add FanArt images to movie
                movie.update({
                    'poster_url': fanart_images.get('poster_url'),
                    'background_url': fanart_images.get('background_url'),
                    'logo_url': fanart_images.get('logo_url'),
                    'thumbnail_url': fanart_images.get('thumbnail_url'),
                    'banner_url': fanart_images.get('banner_url'),
                    'image_source': 'fanart_api',
                    'images_enhanced': True,
                    'omdb_images_ignored': True  # Confirm OMDB images ignored
                })
                
                logger.info(f"✅ FanArt images added for: {movie.get('title')}")
            else:
                logger.warning(f"⚠️ No IMDB ID for FanArt: {movie.get('title')}")
                movie.update({
                    'poster_url': None,
                    'background_url': None,
                    'logo_url': None,
                    'thumbnail_url': None,
                    'banner_url': None,
                    'image_source': 'none',
                    'images_enhanced': False
                })
            
            enhanced_movies.append(movie)
        
        logger.info(f"🎨 IMAGE LAYER: Enhanced {len(enhanced_movies)} movies with FanArt")
        return enhanced_movies
    
    async def _get_fanart_images(self, imdb_id: str) -> Dict[str, str]:
        """Get FanArt images for a movie by IMDB ID"""
        try:
            # Check cache first
            if imdb_id in self.cache['images']:
                return self.cache['images'][imdb_id]
            
            # FanArt API call
            fanart_url = f"{self.fanart_base_url}/{imdb_id}?api_key={self.fanart_api_key}"
            
            async with self.session.get(fanart_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    images = {
                        'poster_url': self._extract_best_fanart_image(data, 'movieposter'),
                        'background_url': self._extract_best_fanart_image(data, 'moviebackground'),
                        'logo_url': self._extract_best_fanart_image(data, 'hdmovielogo'),
                        'thumbnail_url': self._extract_best_fanart_image(data, 'moviethumb'),
                        'banner_url': self._extract_best_fanart_image(data, 'moviebanner')
                    }
                    
                    # Cache for 1 hour
                    self.cache['images'][imdb_id] = images
                    return images
            
            # Return empty if FanArt fails
            return {
                'poster_url': None,
                'background_url': None,
                'logo_url': None,
                'thumbnail_url': None,
                'banner_url': None
            }
            
        except Exception as e:
            logger.error(f"❌ FanArt images failed for {imdb_id}: {e}")
            return {
                'poster_url': None,
                'background_url': None,
                'logo_url': None,
                'thumbnail_url': None,
                'banner_url': None
            }
    
    def _extract_best_fanart_image(self, fanart_data: Dict, image_type: str) -> Optional[str]:
        """Extract the best quality image from FanArt response"""
        try:
            if image_type in fanart_data:
                images = fanart_data[image_type]
                if images and len(images) > 0:
                    # Sort by likes (highest first) and return URL
                    sorted_images = sorted(images, key=lambda x: int(x.get('likes', 0)), reverse=True)
                    return sorted_images[0].get('url')
            return None
        except Exception as e:
            logger.warning(f"⚠️ FanArt image extraction failed for {image_type}: {e}")
            return None
    
    # ========================================
    # REVIEW LAYER (Reddit API)
    # ========================================
    
    async def get_movie_reviews_from_reddit(self, movie_title: str, year: str = None) -> List[Dict[str, Any]]:
        """
        Get movie reviews and discussions from Reddit
        Searches multiple movie subreddits for reviews
        """
        logger.info(f"💬 REVIEW LAYER: Getting Reddit reviews for '{movie_title}'")
        
        try:
            # Construct search query
            search_query = movie_title
            if year:
                search_query += f" {year}"
            
            # Search multiple subreddits
            subreddits = ['movies', 'flicks', 'TrueFilm', 'MovieReviews', 'criterion']
            all_reviews = []
            
            for subreddit in subreddits:
                reviews = await self._search_reddit_subreddit(subreddit, search_query)
                all_reviews.extend(reviews)
            
            # Sort by score and limit results
            all_reviews.sort(key=lambda x: x.get('score', 0), reverse=True)
            top_reviews = all_reviews[:10]  # Top 10 reviews
            
            logger.info(f"✅ REVIEW LAYER: Found {len(top_reviews)} Reddit reviews")
            return top_reviews
            
        except Exception as e:
            logger.error(f"❌ REVIEW LAYER failed: {e}")
            return []
    
    async def _search_reddit_subreddit(self, subreddit: str, query: str) -> List[Dict[str, Any]]:
        """Search a specific subreddit for movie discussions"""
        try:
            # Reddit search URL (no auth needed for public posts)
            search_url = f"{self.reddit_base_url}/r/{subreddit}/search.json"
            params = {
                'q': query,
                'restrict_sr': 'true',
                'sort': 'relevance',
                'limit': 5
            }
            
            headers = {
                'User-Agent': 'CineScopeAnalyzer/1.0'
            }
            
            async with self.session.get(search_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    reviews = []
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            post_data = post.get('data', {})
                            
                            reviews.append({
                                'title': post_data.get('title', ''),
                                'author': post_data.get('author', ''),
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0),
                                'created_utc': post_data.get('created_utc', 0),
                                'selftext': post_data.get('selftext', ''),
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'subreddit': subreddit,
                                'source': 'reddit_api'
                            })
                    
                    return reviews
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Reddit search failed for r/{subreddit}: {e}")
            return []
    
    # ========================================
    # COMPLETE PIPELINE INTEGRATION
    # ========================================
    
    async def get_complete_movie_data(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Complete pipeline: Search → Images → Reviews
        Perfect for webapp cards and detailed views
        """
        logger.info(f"🎬 COMPLETE PIPELINE: Processing '{query}'")
        
        try:
            # Step 1: Search with OMDB + Scrapy (content only)
            movies = await self.search_movies(query, limit)
            
            if not movies:
                logger.warning(f"⚠️ No movies found for '{query}'")
                return []
            
            # Step 2: Enhance with FanArt images (for webapp cards)
            movies_with_images = await self.enhance_movies_with_fanart_images(movies)
            
            # Step 3: Add Reddit reviews for each movie
            for movie in movies_with_images:
                movie_title = movie.get('title', '')
                movie_year = movie.get('year', '')
                
                # Get Reddit reviews
                reviews = await self.get_movie_reviews_from_reddit(movie_title, movie_year)
                movie['reddit_reviews'] = reviews
                movie['review_count'] = len(reviews)
                movie['reviews_enhanced'] = True
            
            logger.info(f"🏆 COMPLETE PIPELINE: Processed {len(movies_with_images)} movies")
            logger.info("✅ SEARCH: OMDB + Scrapy")
            logger.info("✅ IMAGES: FanArt API")
            logger.info("✅ REVIEWS: Reddit API")
            
            return movies_with_images
            
        except Exception as e:
            logger.error(f"❌ COMPLETE PIPELINE failed: {e}")
            return []
    
    async def get_movie_for_card_display(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get optimized movie data for webapp card display
        Includes: Basic info + FanArt images + Review summary
        """
        try:
            # Get basic movie details (OMDB content only)
            movie_details = await self._get_omdb_details_content_only(imdb_id)
            
            if not movie_details:
                return None
            
            # Enhance with FanArt images
            enhanced_movie = await self.enhance_movies_with_fanart_images([movie_details])
            
            if enhanced_movie:
                movie = enhanced_movie[0]
                
                # Add review summary (limited for card display)
                reviews = await self.get_movie_reviews_from_reddit(movie.get('title', ''), movie.get('year', ''))
                movie.update({
                    'review_summary': {
                        'total_reviews': len(reviews),
                        'top_review': reviews[0] if reviews else None,
                        'average_score': sum(r.get('score', 0) for r in reviews) / len(reviews) if reviews else 0
                    },
                    'optimized_for_card': True
                })
                
                return movie
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Card display data failed for {imdb_id}: {e}")
            return None

# Global service instance
complete_pipeline_service = CompletePipelineService()
