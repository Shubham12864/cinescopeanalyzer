import asyncio
import aiohttp
import logging
import os
from typing import List, Dict, Optional, Any
import json

class FixedOMDbAPI:
    """
    Fixed OMDB API implementation that handles free tier limitations properly
    and provides better fallback mechanisms
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OMDB_API_KEY", "")
        self.base_url = "http://www.omdbapi.com/"
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # Check if we have a valid API key
        self.has_valid_key = bool(self.api_key and self.api_key not in ["demo_key", "your_omdb_api_key_here"] and len(self.api_key) > 5)
        
        if not self.has_valid_key:
            self.logger.warning("⚠️ OMDB API key missing or invalid - will use fallback data")
        else:
            self.logger.info(f"✅ OMDB API initialized with key: {self.api_key[:4]}...")
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def search_movies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search movies using OMDB API with proper error handling"""
        if not self.has_valid_key:
            self.logger.warning("🔑 No valid OMDB API key - returning fallback data")
            return self._get_fallback_search_results(query, limit)
        
        try:
            session = await self.get_session()
            
            # OMDB search endpoint
            params = {
                'apikey': self.api_key,
                's': query,
                'type': 'movie',
                'page': 1
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('Response') == 'True' and 'Search' in data:
                        movies = []
                        search_results = data['Search'][:limit]
                        
                        # Get detailed info for each movie
                        for movie_basic in search_results:
                            try:
                                detailed_movie = await self.get_movie_by_id(movie_basic.get('imdbID'))
                                if detailed_movie:
                                    movies.append(detailed_movie)
                                else:
                                    # Use basic info if detailed fetch fails
                                    basic_movie = self._convert_basic_to_detailed(movie_basic)
                                    movies.append(basic_movie)
                            except Exception as e:
                                self.logger.warning(f"Failed to get details for {movie_basic.get('Title')}: {e}")
                                # Use basic info as fallback
                                basic_movie = self._convert_basic_to_detailed(movie_basic)
                                movies.append(basic_movie)
                        
                        self.logger.info(f"✅ OMDB search found {len(movies)} movies for: {query}")
                        return movies
                    
                    elif data.get('Response') == 'False':
                        error_msg = data.get('Error', 'Unknown error')
                        if 'not found' in error_msg.lower():
                            self.logger.info(f"ℹ️ OMDB: No movies found for '{query}'")
                            return []
                        else:
                            self.logger.warning(f"⚠️ OMDB API error: {error_msg}")
                            return self._get_fallback_search_results(query, limit)
                    
                elif response.status == 401:
                    self.logger.error("❌ OMDB API: Invalid API key")
                    self.has_valid_key = False  # Mark key as invalid
                    return self._get_fallback_search_results(query, limit)
                
                elif response.status == 429:
                    self.logger.warning("⚠️ OMDB API: Rate limit exceeded")
                    return self._get_fallback_search_results(query, limit)
                
                else:
                    self.logger.warning(f"⚠️ OMDB API returned status {response.status}")
                    return self._get_fallback_search_results(query, limit)
                    
        except asyncio.TimeoutError:
            self.logger.warning("⏰ OMDB API timeout")
            return self._get_fallback_search_results(query, limit)
        except Exception as e:
            self.logger.error(f"❌ OMDB API error: {e}")
            return self._get_fallback_search_results(query, limit)
        
        return []
    
    async def get_movie_by_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed movie information by IMDB ID"""
        if not self.has_valid_key or not imdb_id:
            return None
        
        try:
            session = await self.get_session()
            
            params = {
                'apikey': self.api_key,
                'i': imdb_id,
                'plot': 'full'
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('Response') == 'True':
                        return self._normalize_omdb_response(data)
                    else:
                        self.logger.warning(f"OMDB error for {imdb_id}: {data.get('Error')}")
                        return None
                else:
                    self.logger.warning(f"OMDB API returned status {response.status} for {imdb_id}")
                    return None
                    
        except Exception as e:
            self.logger.warning(f"Error getting OMDB details for {imdb_id}: {e}")
            return None
    
    def _convert_basic_to_detailed(self, basic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert basic search result to detailed format"""
        return {
            'id': basic_data.get('imdbID', ''),
            'imdbId': basic_data.get('imdbID', ''),
            'title': basic_data.get('Title', 'Unknown Title'),
            'year': int(basic_data.get('Year', '2000')),
            'plot': 'Plot information not available.',
            'rating': 7.0,  # Default rating
            'genre': ['Unknown'],
            'director': 'Unknown Director',
            'cast': ['Unknown Cast'],
            'poster': basic_data.get('Poster', ''),
            'runtime': 120,
            'source': 'omdb_basic'
        }
    
    def _normalize_omdb_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize OMDB API response to standard format"""
        try:
            # Parse genre
            genre_str = data.get('Genre', 'Unknown')
            genres = [g.strip() for g in genre_str.split(',') if g.strip()] if genre_str != 'N/A' else ['Unknown']
            
            # Parse cast
            actors_str = data.get('Actors', 'Unknown Cast')
            cast = [a.strip() for a in actors_str.split(',') if a.strip()] if actors_str != 'N/A' else ['Unknown Cast']
            
            # Parse rating
            rating_str = data.get('imdbRating', '5.0')
            try:
                rating = float(rating_str) if rating_str != 'N/A' else 5.0
            except (ValueError, TypeError):
                rating = 5.0
            
            # Parse runtime
            runtime_str = data.get('Runtime', '120 min')
            runtime_match = None
            if runtime_str != 'N/A':
                import re
                runtime_match = re.search(r'(\d+)', runtime_str)
            runtime = int(runtime_match.group(1)) if runtime_match else 120
            
            # Parse year
            year_str = data.get('Year', '2000')
            try:
                year = int(year_str) if year_str != 'N/A' else 2000
            except (ValueError, TypeError):
                year = 2000
            
            return {
                'id': data.get('imdbID', ''),
                'imdbId': data.get('imdbID', ''),
                'title': data.get('Title', 'Unknown Title'),
                'year': year,
                'plot': data.get('Plot', 'No plot available.') if data.get('Plot') != 'N/A' else 'No plot available.',
                'rating': rating,
                'genre': genres,
                'director': data.get('Director', 'Unknown Director') if data.get('Director') != 'N/A' else 'Unknown Director',
                'cast': cast,
                'poster': data.get('Poster', '') if data.get('Poster') != 'N/A' else '',
                'runtime': runtime,
                'source': 'omdb_detailed'
            }
            
        except Exception as e:
            self.logger.error(f"Error normalizing OMDB response: {e}")
            return self._convert_basic_to_detailed(data)
    
    def _get_fallback_search_results(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Generate fallback search results when OMDB is unavailable"""
        query_lower = query.lower()
        
        # Predefined movie database for fallback
        fallback_movies = [
            {
                'id': 'tt0111161',
                'imdbId': 'tt0111161',
                'title': 'The Shawshank Redemption',
                'year': 1994,
                'plot': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'rating': 9.3,
                'genre': ['Drama'],
                'director': 'Frank Darabont',
                'cast': ['Tim Robbins', 'Morgan Freeman'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg',
                'runtime': 142,
                'source': 'omdb_fallback'
            },
            {
                'id': 'tt0468569',
                'imdbId': 'tt0468569',
                'title': 'The Dark Knight',
                'year': 2008,
                'plot': 'Batman raises the stakes in his war on crime with the help of Lieutenant Jim Gordon and District Attorney Harvey Dent.',
                'rating': 9.0,
                'genre': ['Action', 'Crime', 'Drama'],
                'director': 'Christopher Nolan',
                'cast': ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                'runtime': 152,
                'source': 'omdb_fallback'
            },
            {
                'id': 'tt1375666',
                'imdbId': 'tt1375666',
                'title': 'Inception',
                'year': 2010,
                'plot': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'rating': 8.8,
                'genre': ['Action', 'Sci-Fi', 'Thriller'],
                'director': 'Christopher Nolan',
                'cast': ['Leonardo DiCaprio', 'Marion Cotillard', 'Tom Hardy'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
                'runtime': 148,
                'source': 'omdb_fallback'
            },
            {
                'id': 'tt0133093',
                'imdbId': 'tt0133093',
                'title': 'The Matrix',
                'year': 1999,
                'plot': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
                'rating': 8.7,
                'genre': ['Action', 'Sci-Fi'],
                'director': 'The Wachowskis',
                'cast': ['Keanu Reeves', 'Laurence Fishburne', 'Carrie-Anne Moss'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg',
                'runtime': 136,
                'source': 'omdb_fallback'
            },
            {
                'id': 'tt0372784',
                'imdbId': 'tt0372784',
                'title': 'Batman Begins',
                'year': 2005,
                'plot': 'After training with his mentor, Batman begins his fight to free crime-ridden Gotham City from corruption.',
                'rating': 8.2,
                'genre': ['Action', 'Crime'],
                'director': 'Christopher Nolan',
                'cast': ['Christian Bale', 'Michael Caine', 'Liam Neeson'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BOTY4YjI2N2MtYmFlMC00ZjcyLTg3YjEtMDQyM2ZjYzQ5YWFkXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg',
                'runtime': 140,
                'source': 'omdb_fallback'
            }
        ]
        
        # Filter movies based on query
        matching_movies = []
        for movie in fallback_movies:
            if (query_lower in movie['title'].lower() or 
                any(query_lower in genre.lower() for genre in movie['genre']) or
                query_lower in movie['director'].lower() or
                any(query_lower in actor.lower() for actor in movie['cast'])):
                matching_movies.append(movie)
        
        # If no matches, return some popular movies
        if not matching_movies:
            matching_movies = fallback_movies[:3]
        
        result = matching_movies[:limit]
        self.logger.info(f"📦 OMDB fallback returning {len(result)} movies for: {query}")
        return result
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            try:
                asyncio.create_task(self.session.close())
            except Exception:
                pass