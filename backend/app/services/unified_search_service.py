#!/usr/bin/env python3
"""
Unified Search Service - OMDB API + Robust Scraping + Scrapy
Three-tier search workflow without TMDB API dependency
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import aiohttp
from urllib.parse import quote
import time

# Import our search components
from .working_omdb_client import WorkingOMDBClient
from .robust_search_service import RobustSearchService
from .scrapy_search_service import ScrapySearchService

logger = logging.getLogger(__name__)

class UnifiedSearchService:
    """
    Unified Search Service with Three-Tier Architecture:
    1. OMDB API (Primary) - Fast, reliable movie data
    2. Robust Scraping - Enhanced IMDb scraping
    3. Scrapy Search - Comprehensive web scraping
    
    NO TMDB API - Using OMDB + Scraping for complete coverage
    """
    
    def __init__(self):
        self.omdb_client = WorkingOMDBClient()
        self.robust_scraper = RobustSearchService()
        self.scrapy_service = ScrapySearchService()
        self.session = None
        
        # Performance tracking
        self.search_stats = {
            'omdb_hits': 0,
            'scraping_hits': 0,
            'scrapy_hits': 0,
            'total_searches': 0,
            'avg_response_time': 0
        }
        
        logger.info("🎬 Unified Search Service initialized (OMDB + Robust Scraping + Scrapy)")
    
    async def initialize(self):
        """Initialize all search components"""
        try:
            # Initialize HTTP session
            self.session = aiohttp.ClientSession()
            
            # Initialize search components (they initialize themselves)
            logger.info("✅ All search components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize search service: {e}")
            raise
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("🔒 Unified search session closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Unified movie search using three-tier approach
        
        Args:
            query: Movie title to search
            limit: Maximum number of results
            
        Returns:
            List of movie dictionaries with standardized format
        """
        start_time = time.time()
        all_results = []
        self.search_stats['total_searches'] += 1
        
        logger.info(f"🔍 Starting unified search for: '{query}'")
        
        try:
            # TIER 1: OMDB API (Primary Source)
            logger.info("🎯 Tier 1: OMDB API search...")
            omdb_results = await self._search_omdb(query, limit)
            if omdb_results:
                all_results.extend(omdb_results)
                self.search_stats['omdb_hits'] += 1
                logger.info(f"✅ OMDB found {len(omdb_results)} results")
            
            # TIER 2: Robust Scraping (If OMDB insufficient)
            if len(all_results) < limit // 2:
                logger.info("🕷️ Tier 2: Robust scraping search...")
                scraping_results = await self._search_robust_scraping(query, limit - len(all_results))
                if scraping_results:
                    all_results.extend(scraping_results)
                    self.search_stats['scraping_hits'] += 1
                    logger.info(f"✅ Robust scraping found {len(scraping_results)} results")
            
            # TIER 3: Scrapy Search (For comprehensive coverage)
            if len(all_results) < limit:
                logger.info("🔧 Tier 3: Scrapy search...")
                scrapy_results = await self._search_scrapy(query, limit - len(all_results))
                if scrapy_results:
                    all_results.extend(scrapy_results)
                    self.search_stats['scrapy_hits'] += 1
                    logger.info(f"✅ Scrapy found {len(scrapy_results)} results")
            
            # Deduplicate and standardize results
            final_results = self._deduplicate_results(all_results)[:limit]
            
            # Update performance stats
            response_time = (time.time() - start_time) * 1000
            self._update_performance_stats(response_time)
            
            logger.info(f"🎬 Unified search completed: {len(final_results)} results in {response_time:.1f}ms")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Unified search failed: {e}")
            return []
    
    async def _search_omdb(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search using OMDB API"""
        try:
            results = await self.omdb_client.search_movies(query, limit)
            return self._standardize_omdb_results(results)
        except Exception as e:
            logger.error(f"❌ OMDB search failed: {e}")
            return []
    
    async def _search_robust_scraping(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search using robust scraping service"""
        try:
            results = await self.robust_scraper.search_movies_robust(query, limit)
            return self._standardize_scraping_results(results[:limit])
        except Exception as e:
            logger.error(f"❌ Robust scraping failed: {e}")
            return []
    
    async def _search_scrapy(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search using Scrapy service"""
        try:
            results = await self.scrapy_service.search_movies(query)
            return self._standardize_scrapy_results(results[:limit])
        except Exception as e:
            logger.error(f"❌ Scrapy search failed: {e}")
            return []
    
    def _standardize_omdb_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Standardize OMDB results to unified format"""
        standardized = []
        for movie in results:
            try:
                standardized.append({
                    'title': movie.get('Title', ''),
                    'year': movie.get('Year', ''),
                    'imdb_id': movie.get('imdbID', ''),  # Fixed field name
                    'type': movie.get('Type', 'movie'),
                    'poster_url': movie.get('Poster', ''),  # Fixed field name
                    'plot': movie.get('Plot', ''),
                    'director': movie.get('Director', ''),
                    'actors': movie.get('Actors', ''),
                    'imdbRating': movie.get('imdbRating', ''),
                    'source': 'omdb_api',
                    'search_tier': 1
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to standardize OMDB result: {e}")
                continue
        return standardized
    
    def _standardize_scraping_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Standardize robust scraping results to unified format"""
        standardized = []
        for movie in results:
            try:
                standardized.append({
                    'title': movie.get('title', ''),
                    'year': movie.get('year', ''),
                    'imdb_id': movie.get('imdb_id', ''),  # Already correct
                    'type': 'movie',
                    'poster_url': movie.get('poster_url', ''),  # Already correct
                    'plot': movie.get('plot', ''),
                    'director': movie.get('director', ''),
                    'actors': movie.get('cast', ''),
                    'imdbRating': movie.get('rating', ''),
                    'source': 'robust_scraping',
                    'search_tier': 2
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to standardize scraping result: {e}")
                continue
        return standardized
    
    def _standardize_scrapy_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Standardize Scrapy results to unified format"""
        standardized = []
        for movie in results:
            try:
                standardized.append({
                    'title': movie.get('title', ''),
                    'year': movie.get('year', ''),
                    'imdb_id': movie.get('imdb_id', ''),  # Fixed field name
                    'type': 'movie',
                    'poster_url': movie.get('image_url', ''),  # Fixed field name
                    'plot': movie.get('description', ''),
                    'director': movie.get('director', ''),
                    'actors': movie.get('actors', ''),
                    'imdbRating': movie.get('rating', ''),
                    'source': 'scrapy_search',
                    'search_tier': 3
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to standardize Scrapy result: {e}")
                continue
        return standardized
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate movies based on IMDb ID and title"""
        seen_ids = set()
        seen_titles = set()
        deduplicated = []
        
        for movie in results:
            imdb_id = movie.get('imdb_id', '').strip()  # Fixed field name
            title = movie.get('title', '').strip().lower()
            
            # Check for IMDb ID duplicates (most reliable)
            if imdb_id and imdb_id not in seen_ids:
                seen_ids.add(imdb_id)
                deduplicated.append(movie)
            # Check for title duplicates (fallback)
            elif not imdb_id and title and title not in seen_titles:
                seen_titles.add(title)
                deduplicated.append(movie)
        
        # Sort by search tier (prefer OMDB results)
        deduplicated.sort(key=lambda x: x.get('search_tier', 999))
        return deduplicated
    
    def _update_performance_stats(self, response_time: float):
        """Update performance statistics"""
        total = self.search_stats['total_searches']
        current_avg = self.search_stats['avg_response_time']
        self.search_stats['avg_response_time'] = ((current_avg * (total - 1)) + response_time) / total
    
    async def get_movie_details(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed movie information by IMDb ID"""
        logger.info(f"🎯 Getting movie details for: {imdb_id}")
        
        try:
            # Try OMDB first (most reliable)
            details = await self.omdb_client.get_movie_by_id(imdb_id)
            if details:
                return self._standardize_omdb_results([details])[0]
            
            logger.warning(f"⚠️ No details found for IMDb ID: {imdb_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get movie details: {e}")
            return None
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get current search statistics"""
        total = self.search_stats['total_searches']
        if total == 0:
            return self.search_stats
        
        return {
            **self.search_stats,
            'omdb_hit_rate': (self.search_stats['omdb_hits'] / total) * 100,
            'scraping_hit_rate': (self.search_stats['scraping_hits'] / total) * 100,
            'scrapy_hit_rate': (self.search_stats['scrapy_hits'] / total) * 100
        }
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
        
        logger.info("🧹 Unified search service closed")

# Global service instance
unified_search_service = UnifiedSearchService()
