#!/usr/bin/env python3
"""
WORKING OMDB API SERVICE
Real OMDB API integration that actually searches and returns real movie data
"""
import asyncio
import logging
import os
import aiohttp
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import json

logger = logging.getLogger(__name__)

class WorkingOMDBService:
    """
    Working OMDB API service that makes real API calls
    """
    
    def __init__(self):
        # Use working OMDB API key
        self.api_key = os.getenv("OMDB_API_KEY", "4977b044")  # Updated API key
        self.base_url = "http://www.omdbapi.com/"
        self.timeout = 10.0
        
        logger.info(f"🎬 OMDB API initialized with key: {self.api_key[:4]}****")
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for movies using OMDB API
        Returns real movie data, not demo data
        """
        try:
            logger.info(f"🔍 OMDB API search: '{query}' (limit: {limit})")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                # Step 1: Search for movies
                search_url = f"{self.base_url}?apikey={self.api_key}&s={quote(query)}&type=movie"
                
                async with session.get(search_url) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ OMDB search request failed: HTTP {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    if data.get('Response') != 'True':
                        error_msg = data.get('Error', 'Unknown error')
                        logger.warning(f"⚠️ OMDB search failed: {error_msg}")
                        return []
                    
                    search_results = data.get('Search', [])
                    if not search_results:
                        logger.info(f"📭 No OMDB results found for '{query}'")
                        return []
                    
                    logger.info(f"📋 Found {len(search_results)} OMDB search results")
                    
                    # Step 2: Get detailed info for each movie (limited by limit parameter)
                    detailed_movies = []
                    
                    for movie in search_results[:limit]:
                        imdb_id = movie.get('imdbID')
                        if not imdb_id:
                            continue
                            
                        detailed_movie = await self._get_movie_details(session, imdb_id)
                        if detailed_movie:
                            detailed_movies.append(detailed_movie)
                    
                    logger.info(f"✅ OMDB API success: {len(detailed_movies)} detailed movies")
                    return detailed_movies
                    
        except asyncio.TimeoutError:
            logger.error("⏰ OMDB API timeout")
            return []
        except Exception as e:
            logger.error(f"❌ OMDB API error: {e}")
            return []
    
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
                        logger.debug(f"📄 Got details for: {data.get('Title', 'Unknown')}")
                        return data
                    else:
                        logger.warning(f"⚠️ Failed to get details for {imdb_id}: {data.get('Error', 'Unknown error')}")
                else:
                    logger.warning(f"⚠️ HTTP {response.status} for movie details {imdb_id}")
                    
        except Exception as e:
            logger.error(f"❌ Error fetching details for {imdb_id}: {e}")
            
        return None
    
    async def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific movie by exact title
        """
        try:
            url = f"{self.base_url}?apikey={self.api_key}&t={quote(title)}&plot=full"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('Response') == 'True':
                            return data
                            
        except Exception as e:
            logger.error(f"❌ Error getting movie by title '{title}': {e}")
            
        return None

# Global instance
working_omdb_service = WorkingOMDBService()

# Export main search function
async def search_real_movies(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for real movies using OMDB API
    NO DEMO DATA - only real search results
    """
    return await working_omdb_service.search_movies(query, limit)
