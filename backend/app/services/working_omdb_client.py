#!/usr/bin/env python3
"""
WORKING OMDB API CLIENT - LAYER 1 & 3
Real OMDB API integration with your working API key
"""
import asyncio
import logging
import aiohttp
import time
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import json

logger = logging.getLogger(__name__)

class WorkingOMDBClient:
    """
    Working OMDB API client with your valid API key
    Supports both search and direct movie lookup
    """
    
    def __init__(self):
        # Your working API key
        self.api_key = "4977b044"
        self.base_url = "http://www.omdbapi.com/"
        self.timeout = 10.0
        
        # Request tracking for rate limiting
        self.requests_made = 0
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        logger.info(f"🎬 OMDB API initialized with key: {self.api_key[:4]}****")
    
    async def _rate_limit(self):
        """Implement rate limiting to avoid API abuse"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
        self.requests_made += 1
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for movies using OMDB API
        Returns detailed movie information
        """
        try:
            await self._rate_limit()
            
            logger.info(f"🔍 OMDB Search: '{query}' (limit: {limit})")
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                
                # Step 1: Search for movies
                search_url = f"{self.base_url}?apikey={self.api_key}&s={quote(query)}&type=movie"
                
                async with session.get(search_url) as response:
                    if response.status != 200:
                        logger.error(f"❌ OMDB search failed: HTTP {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    if data.get('Response') != 'True':
                        error_msg = data.get('Error', 'Unknown error')
                        logger.info(f"📭 OMDB: {error_msg}")
                        return []
                    
                    search_results = data.get('Search', [])
                    if not search_results:
                        logger.info(f"📭 No OMDB results for '{query}'")
                        return []
                    
                    logger.info(f"📋 Found {len(search_results)} OMDB search results")
                    
                    # Step 2: Get detailed info for each movie
                    detailed_movies = []
                    
                    for movie in search_results[:limit]:
                        imdb_id = movie.get('imdbID')
                        if imdb_id:
                            await self._rate_limit()  # Rate limit each detail request
                            details = await self._get_movie_details(session, imdb_id)
                            if details:
                                detailed_movies.append(details)
                                
                                # Stop if we have enough results
                                if len(detailed_movies) >= limit:
                                    break
                    
                    logger.info(f"✅ OMDB success: {len(detailed_movies)} detailed movies")
                    return detailed_movies
                    
        except asyncio.TimeoutError:
            logger.error("⏰ OMDB API timeout")
            return []
        except Exception as e:
            logger.error(f"❌ OMDB API error: {e}")
            return []
    
    async def get_movie_by_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get movie by IMDB ID
        Used for cache validation and direct lookups
        """
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                return await self._get_movie_details(session, imdb_id)
                
        except Exception as e:
            logger.error(f"❌ Error getting movie {imdb_id}: {e}")
            return None
    
    async def get_movie_by_title(self, title: str, year: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get movie by exact title
        Useful for cache pre-population
        """
        try:
            await self._rate_limit()
            
            url = f"{self.base_url}?apikey={self.api_key}&t={quote(title)}&plot=full"
            if year:
                url += f"&y={year}"
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('Response') == 'True':
                            logger.info(f"✅ Found movie by title: {title}")
                            return data
                        else:
                            logger.info(f"📭 No movie found for title: {title}")
                    else:
                        logger.error(f"❌ HTTP {response.status} for title: {title}")
                        
        except Exception as e:
            logger.error(f"❌ Error getting movie by title '{title}': {e}")
            
        return None
    
    async def _get_movie_details(self, session: aiohttp.ClientSession, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed movie information from OMDB
        Internal method used by search functions
        """
        try:
            detail_url = f"{self.base_url}?apikey={self.api_key}&i={imdb_id}&plot=full"
            
            async with session.get(detail_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'True':
                        logger.debug(f"📄 Got details: {data.get('Title', 'Unknown')} ({data.get('Year', 'Unknown')})")
                        return data
                    else:
                        logger.warning(f"⚠️ OMDB error for {imdb_id}: {data.get('Error', 'Unknown error')}")
                else:
                    logger.warning(f"⚠️ HTTP {response.status} for {imdb_id}")
                    
        except Exception as e:
            logger.error(f"❌ Error fetching details for {imdb_id}: {e}")
            
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "requests_made": self.requests_made,
            "api_key": f"{self.api_key[:4]}****",
            "last_request": self.last_request_time
        }

# Global instance
working_omdb_client = WorkingOMDBClient()

# Export functions
async def search_omdb_movies(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search movies using working OMDB API"""
    return await working_omdb_client.search_movies(query, limit)

async def get_omdb_movie_by_id(imdb_id: str) -> Optional[Dict[str, Any]]:
    """Get movie by IMDB ID using OMDB API"""
    return await working_omdb_client.get_movie_by_id(imdb_id)

async def get_omdb_movie_by_title(title: str, year: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get movie by title using OMDB API"""
    return await working_omdb_client.get_movie_by_title(title, year)
