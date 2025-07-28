#!/usr/bin/env python3
"""
Enhanced OMDB Service with Fallback Support
Uses external OMDB API when available, fallback data when network fails
"""
import asyncio
import logging
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import os
from .fallback_service import fallback_service

logger = logging.getLogger(__name__)

class EnhancedOMDBService:
    """
    OMDB service with robust error handling and fallback support
    """
    
    def __init__(self):
        self.api_key = os.getenv("OMDB_API_KEY", "4977b044")
        self.base_url = "http://www.omdbapi.com/"
        self.timeout = 10.0
        self.fallback_enabled = True
        
        logger.info(f"🎬 Enhanced OMDB API initialized with key: {self.api_key[:4]}****")
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for movies using OMDB API with fallback support
        """
        logger.info(f"🔍 Enhanced OMDB search: '{query}' (limit: {limit})")
        
        try:
            # Try external OMDB API first
            external_results = await self._search_external_api(query, limit)
            if external_results:
                logger.info(f"✅ External OMDB API success: {len(external_results)} movies")
                return external_results
                
        except Exception as e:
            logger.warning(f"⚠️ External OMDB API failed: {e}")
        
        # Fallback to local data
        if self.fallback_enabled:
            logger.info("🔄 Using fallback movie data")
            fallback_results = await fallback_service.search_movies(query, limit)
            
            # Add source indicator
            for movie in fallback_results:
                movie['data_source'] = 'fallback'
                movie['api_status'] = 'offline'
            
            if fallback_results:
                logger.info(f"✅ Fallback data provided: {len(fallback_results)} movies")
                return fallback_results
        
        logger.warning(f"❌ No results available for query: '{query}'")
        return []
    
    async def _search_external_api(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search using external OMDB API
        """
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            # Step 1: Search for movies
            search_url = f"{self.base_url}?apikey={self.api_key}&s={quote(query)}&type=movie"
            
            async with session.get(search_url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                data = await response.json()
                
                if data.get('Response') != 'True':
                    error_msg = data.get('Error', 'Unknown error')
                    raise Exception(f"OMDB Error: {error_msg}")
                
                search_results = data.get('Search', [])
                if not search_results:
                    return []
                
                # Step 2: Get detailed info for each movie
                detailed_movies = []
                
                for movie in search_results[:limit]:
                    imdb_id = movie.get('imdbID')
                    if not imdb_id:
                        continue
                        
                    detailed_movie = await self._get_movie_details(session, imdb_id)
                    if detailed_movie:
                        # Normalize field names
                        normalized_movie = self._normalize_omdb_response(detailed_movie)
                        normalized_movie['data_source'] = 'omdb_api'
                        normalized_movie['api_status'] = 'online'
                        detailed_movies.append(normalized_movie)
                
                return detailed_movies
    
    async def _get_movie_details(self, session: aiohttp.ClientSession, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed movie information from OMDB API
        """
        try:
            detail_url = f"{self.base_url}?apikey={self.api_key}&i={imdb_id}&plot=full"
            
            async with session.get(detail_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'True':
                        return data
                        
        except Exception as e:
            logger.debug(f"Error fetching details for {imdb_id}: {e}")
            
        return None
    
    def _normalize_omdb_response(self, omdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize OMDB API response to match our internal format
        """
        try:
            # Extract runtime as integer
            runtime_str = omdb_data.get('Runtime', '')
            runtime_minutes = None
            if runtime_str and 'min' in runtime_str:
                try:
                    runtime_minutes = int(runtime_str.split(' min')[0])
                except (ValueError, IndexError):
                    pass
            
            # Extract rating as float
            rating = 0.0
            try:
                rating_str = omdb_data.get('imdbRating', 'N/A')
                if rating_str != 'N/A':
                    rating = float(rating_str)
            except (ValueError, TypeError):
                pass
            
            # Extract year as integer
            year = None
            try:
                year_str = omdb_data.get('Year', '')
                if year_str and year_str != 'N/A':
                    year = int(year_str.split('–')[0])  # Handle year ranges
            except (ValueError, TypeError):
                pass
            
            # Normalize the response
            normalized = {
                'imdb_id': omdb_data.get('imdbID'),
                'title': omdb_data.get('Title', 'Unknown Title'),
                'year': year,
                'genre': omdb_data.get('Genre', ''),
                'director': omdb_data.get('Director', 'Unknown'),
                'actors': omdb_data.get('Actors', ''),
                'plot': omdb_data.get('Plot', ''),
                'runtime': f"{runtime_minutes} min" if runtime_minutes else omdb_data.get('Runtime', ''),
                'rating': rating,
                'poster_url': omdb_data.get('Poster', ''),
                'awards': omdb_data.get('Awards', ''),
                'country': omdb_data.get('Country', ''),
                'language': omdb_data.get('Language', ''),
                'released': omdb_data.get('Released', ''),
                'metascore': omdb_data.get('Metascore', 'N/A'),
                'imdb_rating': rating,
                'imdb_votes': omdb_data.get('imdbVotes', ''),
                'box_office': omdb_data.get('BoxOffice', 'N/A'),
                'production': omdb_data.get('Production', 'N/A'),
                'website': omdb_data.get('Website', 'N/A')
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing OMDB response: {e}")
            return omdb_data
    
    async def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific movie by exact title
        """
        try:
            # Try external API first
            url = f"{self.base_url}?apikey={self.api_key}&t={quote(title)}&plot=full"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('Response') == 'True':
                            normalized = self._normalize_omdb_response(data)
                            normalized['data_source'] = 'omdb_api'
                            normalized['api_status'] = 'online'
                            return normalized
                            
        except Exception as e:
            logger.warning(f"⚠️ External OMDB API failed for title '{title}': {e}")
        
        # Fallback search
        if self.fallback_enabled:
            logger.info("🔄 Using fallback data for title search")
            # Search fallback data for movie with matching title
            search_results = await fallback_service.search_movies(title, 1)
            if search_results:
                movie = search_results[0].copy()
                movie['data_source'] = 'fallback'
                movie['api_status'] = 'offline'
                return movie
            
        return None
    
    async def get_movie_by_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a movie by IMDb ID
        """
        try:
            # Try external API first
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                movie = await self._get_movie_details(session, imdb_id)
                if movie:
                    normalized = self._normalize_omdb_response(movie)
                    normalized['data_source'] = 'omdb_api'
                    normalized['api_status'] = 'online'
                    return normalized
                    
        except Exception as e:
            logger.warning(f"⚠️ External OMDB API failed for ID '{imdb_id}': {e}")
        
        # Fallback search
        if self.fallback_enabled:
            logger.info("🔄 Using fallback data for ID search")
            movie = await fallback_service.get_movie_by_id(imdb_id)
            if movie:
                movie_copy = movie.copy()
                movie_copy['data_source'] = 'fallback'
                movie_copy['api_status'] = 'offline'
                return movie_copy
            
        return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status information
        """
        return {
            'service': 'enhanced_omdb',
            'api_key_configured': bool(self.api_key),
            'fallback_enabled': self.fallback_enabled,
            'timeout': self.timeout
        }

# Global instance
enhanced_omdb_service = EnhancedOMDBService()