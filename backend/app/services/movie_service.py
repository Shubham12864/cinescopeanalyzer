from typing import List, Optional, Dict
import asyncio
import random
import logging
from datetime import datetime, timedelta
import json
import aiohttp
from bs4 import BeautifulSoup
import re

from ..models.movie import Movie, Review, AnalyticsData, SentimentData, RatingDistributionData, MovieSummary
from ..core.api_manager import APIManager
from ..core.azure_database import get_movies_collection, get_cache_collection
from .comprehensive_movie_service_working import ComprehensiveMovieService
from ..scraper.enhanced_movie_scraper import EnhancedMovieDescriptionScraper
from .image_processing_service import image_processing_service
from ..core.error_handler import (
    error_handler,
    ErrorSeverity,
    SearchException,
    ExternalAPIException,
    NotFoundException
)

class MovieService:
    def __init__(self):
        self.api_manager = APIManager()  # Use comprehensive API manager
        self.comprehensive_service = ComprehensiveMovieService()  # Enhanced service
        self.description_scraper = EnhancedMovieDescriptionScraper()  # Enhanced descriptions
        self.logger = logging.getLogger(__name__)  # Add logger
        # Database collections (will be initialized when needed)
        self.movies_collection = None
        self.cache_collection = None
        self.movies_db = []  # Initialize movies_db
        
        # In-memory cache for search results (2 hours TTL)
        self._search_cache: Dict[str, Dict] = {}
        self._cache_ttl = 2 * 60 * 60  # 2 hours in seconds
        
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo movie data"""
        # Don't initialize demo data immediately - wait for real API calls
        # Only use demo data as absolute fallback
        self.movies_db = []
        self.logger.info("🚀 MovieService initialized - will load real data on first request")
    
    def _generate_cache_key(self, query: str, limit: int = 20) -> str:
        """Generate cache key for search queries"""
        return f"search:{query.lower().strip()}:{limit}"
    
    async def _check_cache(self, cache_key: str) -> Optional[List[Movie]]:
        """Check if cached results exist and are still valid"""
        if cache_key not in self._search_cache:
            return None
        
        cache_entry = self._search_cache[cache_key]
        cache_time = cache_entry.get('timestamp', 0)
        current_time = datetime.now().timestamp()
        
        # Check if cache has expired
        if current_time - cache_time > self._cache_ttl:
            self.logger.info(f"💾 Cache EXPIRED for key: {cache_key}")
            del self._search_cache[cache_key]
            return None
        
        # Return cached movies
        cached_data = cache_entry.get('data', [])
        movies = []
        
        for movie_data in cached_data:
            try:
                movie = Movie(
                    id=movie_data.get('id', ''),
                    title=movie_data.get('title', ''),
                    plot=movie_data.get('plot', ''),
                    rating=movie_data.get('rating', 0),
                    genre=movie_data.get('genre', []),
                    year=movie_data.get('year', 0),
                    poster=movie_data.get('poster', ''),
                    director=movie_data.get('director', ''),
                    cast=movie_data.get('cast', []),
                    reviews=[],
                    imdbId=movie_data.get('imdbId'),
                    runtime=movie_data.get('runtime', 120)
                )
                movies.append(movie)
            except Exception as e:
                self.logger.warning(f"Failed to reconstruct cached movie: {e}")
                continue
        
        if movies:
            age_minutes = (current_time - cache_time) / 60
            self.logger.info(f"💾 Cache HIT for key: {cache_key} ({len(movies)} movies, age: {age_minutes:.1f}min)")
            return movies
        
        return None
    
    async def _cache_search_results(self, cache_key: str, movies: List[Movie]) -> None:
        """Cache search results for future use"""
        try:
            # Convert movies to serializable format
            cached_data = []
            for movie in movies:
                movie_dict = {
                    'id': movie.id,
                    'title': movie.title,
                    'plot': movie.plot,
                    'rating': movie.rating,
                    'genre': movie.genre,
                    'year': movie.year,
                    'poster': movie.poster,
                    'director': movie.director,
                    'cast': movie.cast,
                    'imdbId': movie.imdbId,
                    'runtime': movie.runtime
                }
                cached_data.append(movie_dict)
            
            # Store in cache with timestamp
            self._search_cache[cache_key] = {
                'data': cached_data,
                'timestamp': datetime.now().timestamp()
            }
            
            self.logger.info(f"💾 Cache SET for key: {cache_key} ({len(movies)} movies)")
            
            # Clean up old cache entries (keep only last 50 entries)
            if len(self._search_cache) > 50:
                # Remove oldest entries
                sorted_keys = sorted(
                    self._search_cache.keys(),
                    key=lambda k: self._search_cache[k]['timestamp']
                )
                for old_key in sorted_keys[:-50]:
                    del self._search_cache[old_key]
                self.logger.info("💾 Cache cleanup: removed old entries")
                
        except Exception as e:
            self.logger.warning(f"Failed to cache search results: {e}")
    
    def _clear_expired_cache(self) -> None:
        """Clear expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = []
        
        for key, entry in self._search_cache.items():
            if current_time - entry['timestamp'] > self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._search_cache[key]
        
        if expired_keys:
            self.logger.info(f"💾 Cache cleanup: removed {len(expired_keys)} expired entries")
    
    def _process_movie_image(self, poster_url: str, source: str = 'generic') -> str:
        """Process movie poster URL using the image processing service"""
        if not poster_url:
            return ''
        
        try:
            result = image_processing_service.process_image_url(poster_url, source)
            
            if result['valid'] and result['processed_url']:
                processed_url = result['processed_url']
                
                # Log processing details for debugging
                if result.get('modifications'):
                    self.logger.debug(f"Image URL processed with modifications: {result['modifications']}")
                
                if result.get('cached'):
                    self.logger.debug(f"Used cached processed URL for: {poster_url}")
                
                return processed_url
            else:
                self.logger.warning(f"Failed to process image URL: {poster_url} - {result.get('error', 'Unknown error')}")
                return ''
                
        except Exception as e:
            self.logger.error(f"Error processing movie image URL {poster_url}: {e}")
            return poster_url  # Return original URL as fallback
    
    async def _load_initial_movies(self):
        """Load initial movies from real APIs"""
        try:
            self.logger.info("🚀 Loading initial movies from APIs...")
            
            # Try to get popular/trending movies
            popular_queries = ["batman", "marvel", "star wars", "inception", "godfather"]
            
            for query in popular_queries:
                try:
                    movies_data = await self.api_manager.search_movies(query, 2)  # 2 per query
                    
                    for movie_data in movies_data:
                        if movie_data.get('source') in ['omdb_live', 'tmdb_live']:  # Only real data
                            movie = Movie(
                                id=movie_data.get('id', ''),
                                title=movie_data.get('title', ''),
                                plot=movie_data.get('plot', ''),
                                rating=movie_data.get('rating', 0),
                                genre=movie_data.get('genre', []),
                                year=movie_data.get('year', 0),
                                poster=movie_data.get('poster', ''),
                                director=movie_data.get('director', ''),
                                cast=movie_data.get('cast', []),
                                reviews=[],
                                imdbId=movie_data.get('imdbId'),
                                runtime=movie_data.get('runtime', 120)
                            )
                            
                            # Check if movie already exists
                            if not any(m.id == movie.id for m in self.movies_db):
                                self.movies_db.append(movie)
                                self.logger.info(f"✅ Added real movie: {movie.title}")
                                
                except Exception as e:
                    self.logger.warning(f"Failed to load movies for '{query}': {e}")
                    continue
            
            self.logger.info(f"🎬 Loaded {len(self.movies_db)} real movies from APIs")
            
            # Only add demo data if we couldn't get any real movies
            if len(self.movies_db) == 0:
                self.logger.warning("⚠️ No real movies loaded, using demo data")
                self._init_original_demo_data()
                
        except Exception as e:
            self.logger.error(f"Error loading initial movies: {e}")
            self._init_original_demo_data()
    
    def _init_original_demo_data(self):
        """Original demo data as fallback"""
        demo_movies = [
            Movie(
                id="1",
                title="The Shawshank Redemption",
                year=1994,
                poster="https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
                rating=9.3,
                genre=["Drama"],
                plot="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                director="Frank Darabont",
                cast=["Tim Robbins", "Morgan Freeman"],
                reviews=[
                    Review(
                        id="r1",
                        author="MovieCritic",
                        content="An absolutely masterful film that explores themes of hope and redemption.",
                        rating=9.5,
                        sentiment="positive",
                        date="2024-01-15"
                    )
                ]
            ),
            Movie(                id="2",
                title="The Godfather",
                year=1972,
                poster="https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzAwMjU2MjU@._V1_SX300.jpg",
                rating=9.2,
                genre=["Crime", "Drama"],
                plot="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                director="Francis Ford Coppola",
                cast=["Marlon Brando", "Al Pacino"],
                reviews=[
                    Review(
                        id="r2",
                        author="FilmBuff",
                        content="A cinematic masterpiece that defines the crime genre.",
                        rating=9.0,
                        sentiment="positive",
                        date="2024-01-10"
                    )
                ]
            )
        ]
        self.movies_db.extend(demo_movies)
    
    async def get_movies(
        self, 
        limit: int = 20, 
        offset: int = 0,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        sort_by: str = "rating",
        sort_order: str = "desc"
    ) -> List[Movie]:
        """Get movies with filtering and sorting"""
        filtered_movies = self.movies_db.copy()
        
        # Apply filters
        if genre:
            filtered_movies = [m for m in filtered_movies if genre.lower() in [g.lower() for g in m.genre]]
        if year:
            filtered_movies = [m for m in filtered_movies if m.year == year]
          # Sort movies
        reverse = sort_order == "desc"
        if sort_by == "rating":
            filtered_movies.sort(key=lambda x: x.rating, reverse=reverse)
        elif sort_by == "year":
            filtered_movies.sort(key=lambda x: x.year, reverse=reverse)
        elif sort_by == "title":
            filtered_movies.sort(key=lambda x: x.title, reverse=reverse)        # Apply pagination
        return filtered_movies[offset:offset + limit]
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Movie]:
        """🚀 ENHANCED REAL-TIME SEARCH - Prioritizes OMDB API with proper timeout and retry"""
        import time
        start_time = time.time()
        
        try:
            # Validate input parameters
            if not query or not query.strip():
                raise error_handler.handle_validation_error(
                    "Search query cannot be empty", "query", query
                )
            
            if len(query.strip()) > 100:
                raise error_handler.handle_validation_error(
                    "Search query too long (max 100 characters)", "query", query
                )
            
            if limit <= 0 or limit > 100:
                raise error_handler.handle_validation_error(
                    "Limit must be between 1 and 100", "limit", limit
                )
            
            sanitized_query = query.strip()
            self.logger.info(f"🔍 ENHANCED Search: '{sanitized_query}' (limit: {limit})")
            
            # STEP 1: OMDB API with retry mechanism and 8-second timeout (highest priority)
            try:
                omdb_results = await self._search_omdb_with_retry(sanitized_query, limit)
                if omdb_results:
                    self.logger.info(f"✅ OMDB SUCCESS: {len(omdb_results)} fresh results")
                    # Cache successful OMDB results
                    await self._cache_search_results(f"search:{query.lower()}:{limit}", omdb_results)
                    return omdb_results[:limit]
            except Exception as omdb_error:
                self.logger.warning(f"⚠️ OMDB API failed: {omdb_error}")
            
            # STEP 2: Web scraping as secondary option (before cache)
            scraping_results = await self._search_with_web_scraping(query, limit)
            if scraping_results:
                self.logger.info(f"✅ Web Scraping SUCCESS: {len(scraping_results)} movies")
                await self._cache_search_results(f"search:{query.lower()}:{limit}", scraping_results)
                return scraping_results[:limit]
            
            # STEP 3: Cache check as tertiary fallback
            cache_key = f"search:{query.lower()}:{limit}"
            cached_result = await self._check_cache(cache_key)
            if cached_result:
                self.logger.info(f"⚡ Cache FALLBACK - returning {len(cached_result)} results")
                return cached_result[:limit]
            
            # STEP 4: Database search as quaternary fallback
            db_results = await self._search_movies_in_db(query, limit)
            if db_results:
                movies = [self._convert_dict_to_movie(data) for data in db_results if data]
                movies = [m for m in movies if m is not None]  # Filter out None results
                if movies:
                    self.logger.info(f"💾 Database FALLBACK - returning {len(movies)} results")
                    return movies[:limit]
            
            # STEP 5: Use enhanced web scraping as final fallback
            elapsed = (time.time() - start_time) * 1000
            self.logger.warning(f"❌ No API results found for '{query}' - trying enhanced web scraping after {elapsed:.0f}ms")
            
            # Use enhanced web scraping that doesn't require Scrapy
            enhanced_scraping_results = await self._enhanced_web_search(query, limit)
            if enhanced_scraping_results:
                self.logger.info(f"🌐 Enhanced scraping SUCCESS: {len(enhanced_scraping_results)} movies")
                return enhanced_scraping_results
            
            self.logger.warning(f"❌ All search methods exhausted for '{query}' - returning empty list")
            return []
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self.logger.error(f"❌ Search failed after {elapsed:.0f}ms: {e}")
            # Try enhanced scraping as last resort
            try:
                fallback_results = await self._enhanced_web_search(query, limit)
                if fallback_results:
                    return fallback_results
            except Exception:
                pass
            return []

    async def _enhanced_web_search(self, query: str, limit: int) -> List[Movie]:
        """Enhanced web search without requiring Scrapy"""
        import aiohttp
        import asyncio
        from urllib.parse import quote
        
        try:
            search_results = []
            
            # Search multiple sources
            sources = [
                f"https://www.imdb.com/find?q={quote(query)}&s=tt&ttype=ft",
                f"https://www.themoviedb.org/search/movie?query={quote(query)}"
            ]
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                tasks = [self._scrape_movie_source(session, source, query) for source in sources]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        search_results.extend(result)
            
            # Convert to Movie objects and limit results
            movies = []
            for movie_data in search_results[:limit]:
                try:
                    movie = Movie(
                        id=movie_data.get('id', f"web_{len(movies)}"),
                        title=movie_data.get('title', 'Unknown Title'),
                        plot=movie_data.get('plot', 'Plot information not available.'),
                        rating=movie_data.get('rating', 7.0),
                        genre=movie_data.get('genre', ['Drama']),
                        year=movie_data.get('year', 2020),
                        poster=f"/api/images/image-proxy?url={movie_data.get('poster', '')}" if movie_data.get('poster') else "",
                        director=movie_data.get('director', 'Unknown Director'),
                        cast=movie_data.get('cast', []),
                        reviews=[],
                        runtime=movie_data.get('runtime', 120)
                    )
                    movies.append(movie)
                except Exception as e:
                    self.logger.warning(f"Error converting scraped data to movie: {e}")
                    continue
            
            return movies
            
        except Exception as e:
            self.logger.error(f"Enhanced web search failed: {e}")
            return []

    async def _scrape_movie_source(self, session: aiohttp.ClientSession, url: str, query: str) -> List[Dict]:
        """Scrape a single movie source"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_movie_content(content, query)
                
        except Exception as e:
            self.logger.warning(f"Failed to scrape {url}: {e}")
        
        return []

    def _parse_movie_content(self, content: str, query: str) -> List[Dict]:
        """Parse movie content from scraped HTML"""
        from bs4 import BeautifulSoup
        import re
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            movies = []
            
            # Look for movie titles and basic info
            # This is a simplified parser - could be enhanced for specific sites
            title_elements = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(query, re.I))
            
            for i, element in enumerate(title_elements[:3]):  # Limit to 3 results per source
                try:
                    # Extract basic movie information
                    title = element.get_text(strip=True)
                    
                    # Try to find year in nearby elements
                    year_match = re.search(r'\b(19|20)\d{2}\b', str(element.parent))
                    year = int(year_match.group()) if year_match else 2020
                    
                    # Generate a basic movie entry
                    movie = {
                        'id': f"scraped_{hash(title)}",
                        'title': title,
                        'year': year,
                        'rating': 7.0 + (i * 0.1),  # Slight variation in ratings
                        'plot': f"A movie about {query.lower()}. Plot details to be updated.",
                        'genre': ['Drama', 'Action'],
                        'director': 'Unknown Director',
                        'cast': ['Cast Member 1', 'Cast Member 2'],
                        'poster': '',  # Would need more sophisticated scraping for images
                        'runtime': 120
                    }
                    movies.append(movie)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing movie element: {e}")
                    continue
            
            return movies
            
        except Exception as e:
            self.logger.error(f"Error parsing movie content: {e}")
            return []

    async def _generate_demo_movies_for_query(self, query: str, limit: int) -> List[Movie]:
        """Generate relevant demo movies based on search query"""
        query_lower = query.lower()
        
        # Define movie database with realistic data
        demo_movies_db = [
            {
                "id": "batman_2022", "title": "The Batman", "year": 2022, "rating": 7.8,
                "plot": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption and question his family's involvement.",
                "genre": ["Action", "Crime", "Drama"], "director": "Matt Reeves",
                "cast": ["Robert Pattinson", "Zoë Kravitz", "Paul Dano"],
                "poster": "https://m.media-amazon.com/images/M/MV5BM2MyNTAwZGEtNTAxNC00ODVjLTgzZjUtYmU0YjAzNmQyZDEwXkEyXkFqcGdeQXVyNDc2NTg3NzA@._V1_SX300.jpg"
            },
            {
                "id": "batman_begins", "title": "Batman Begins", "year": 2005, "rating": 8.2,
                "plot": "After training with his mentor, Batman begins his fight to free crime-ridden Gotham City from corruption.",
                "genre": ["Action", "Crime"], "director": "Christopher Nolan",
                "cast": ["Christian Bale", "Michael Caine", "Liam Neeson"],
                "poster": "https://m.media-amazon.com/images/M/MV5BOTY4YjI2N2MtYmFlMC00ZjcyLTg3YjEtMDQyM2ZjYzQ5YWFkXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg"
            },
            {
                "id": "dark_knight", "title": "The Dark Knight", "year": 2008, "rating": 9.0,
                "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                "genre": ["Action", "Crime", "Drama"], "director": "Christopher Nolan",
                "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
                "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg"
            },
            {
                "id": "spider_man", "title": "Spider-Man: No Way Home", "year": 2021, "rating": 8.4,
                "plot": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear.",
                "genre": ["Action", "Adventure", "Fantasy"], "director": "Jon Watts",
                "cast": ["Tom Holland", "Zendaya", "Benedict Cumberbatch"],
                "poster": "https://m.media-amazon.com/images/M/MV5BZWMyYzFjYTYtNTRjYi00OGExLWE2YzgtOGRmYjAxZTU3NzBiXkEyXkFqcGdeQXVyMzQ0MzA0NTM@._V1_SX300.jpg"
            },
            {
                "id": "inception", "title": "Inception", "year": 2010, "rating": 8.8,
                "plot": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
                "genre": ["Action", "Sci-Fi", "Thriller"], "director": "Christopher Nolan",
                "cast": ["Leonardo DiCaprio", "Marion Cotillard", "Tom Hardy"],
                "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg"
            },
            {
                "id": "avengers", "title": "Avengers: Endgame", "year": 2019, "rating": 8.4,
                "plot": "After the devastating events of Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more to reverse Thanos' actions.",
                "genre": ["Action", "Adventure", "Drama"], "director": "Anthony Russo",
                "cast": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo"],
                "poster": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg"
            }
        ]
        
        # Filter movies based on query
        matching_movies = []
        for movie_data in demo_movies_db:
            if (query_lower in movie_data["title"].lower() or 
                any(query_lower in genre.lower() for genre in movie_data["genre"]) or
                query_lower in movie_data["plot"].lower()):
                matching_movies.append(movie_data)
        
        # If no matches, return popular movies
        if not matching_movies:
            matching_movies = demo_movies_db[:limit]
        
        # Convert to Movie objects
        movies = []
        for movie_data in matching_movies[:limit]:
            movie = Movie(
                id=movie_data["id"],
                title=movie_data["title"],
                plot=movie_data["plot"],
                rating=movie_data["rating"],
                genre=movie_data["genre"],
                year=movie_data["year"],
                poster=f"/api/images/image-proxy?url={movie_data['poster']}",
                director=movie_data["director"],
                cast=movie_data["cast"],
                reviews=[],
                runtime=120
            )
            movies.append(movie)
        
        self.logger.info(f"🎭 Generated {len(movies)} demo movies for query '{query}'")
        return movies
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Movie]:
        """Get a specific movie by ID with enhanced descriptions"""
        self.logger.info(f"🔍 Looking for movie with ID: {movie_id}")
        self.logger.info(f"📚 Local movies_db has {len(self.movies_db)} movies")
        
        # First check database
        db_movie = await self._get_movie_from_db(movie_id)
        if db_movie:
            movie = self._convert_dict_to_movie(db_movie)
            if movie:  # Check if conversion was successful
                self.logger.info(f"✅ Found movie in database: {movie.title}")
                
                # Check if we need to enhance the description
                if not hasattr(movie, 'enhanced_data') or not movie.enhanced_data:
                    self.logger.info(f"🚀 Enhancing description for: {movie.title}")
                    try:
                        enhanced_data = await self.description_scraper.get_comprehensive_description(
                            movie.title, movie.year, movie.imdbId or ""
                        )
                        movie.enhanced_data = enhanced_data
                        # Update plot with enhanced description
                        if enhanced_data.get('full_description'):
                            movie.plot = enhanced_data['full_description']
                        self.logger.info(f"✅ Enhanced description added for: {movie.title}")
                    except Exception as e:
                        self.logger.warning(f"Failed to enhance description for {movie.title}: {e}")
                        if not hasattr(movie, 'enhanced_data'):
                            movie.enhanced_data = {}
                
                return movie
            else:
                self.logger.warning(f"Failed to convert database movie data for {movie_id}")
        
        # If not found in database, check the local movies_db list
        self.logger.info(f"🔍 Movie {movie_id} not in database, checking local movies list...")
        for i, movie in enumerate(self.movies_db):
            self.logger.info(f"Checking movie {i}: ID={movie.id}, Title={movie.title}")
            if str(movie.id) == str(movie_id):
                self.logger.info(f"✅ Found movie in local list: {movie.title}")
                return movie
        
        self.logger.warning(f"❌ Movie {movie_id} not found in local movies_db")
        
        # If not found locally, try to fetch from APIs
        self.logger.info(f"🔍 Movie {movie_id} not in local DB, trying APIs...")
        
        # Try OMDB first if it looks like an IMDB ID
        if movie_id.startswith('tt'):
            try:
                movie_data = await self.api_manager.omdb_api.get_movie_by_id(movie_id)
                if movie_data:
                    # Process poster image URL
                    poster_url = movie_data.get('poster', '')
                    processed_poster = self._process_movie_image(poster_url, 'omdb')
                    
                    movie = Movie(
                        id=movie_data.get('id', movie_id),
                        title=movie_data.get('title', 'Unknown'),
                        plot=movie_data.get('plot', ''),
                        rating=movie_data.get('rating', 0),
                        genre=movie_data.get('genre', []),
                        year=movie_data.get('year', 0),
                        poster=processed_poster,
                        director=movie_data.get('director', ''),
                        cast=movie_data.get('cast', []),
                        reviews=[],
                        imdbId=movie_data.get('imdbId'),
                        runtime=movie_data.get('runtime', 120),
                        enhanced_data={}
                    )
                    
                    # Get enhanced description for new movie
                    self.logger.info(f"🚀 Getting enhanced description for new movie: {movie.title}")
                    try:
                        enhanced_data = await self.description_scraper.get_comprehensive_description(
                            movie.title, movie.year, movie.imdbId or ""
                        )
                        movie.enhanced_data = enhanced_data
                        # Update plot with enhanced description
                        if enhanced_data.get('full_description'):
                            movie.plot = enhanced_data['full_description']
                        self.logger.info(f"✅ Enhanced description added for new movie: {movie.title}")
                    except Exception as e:
                        self.logger.warning(f"Failed to enhance description for new movie {movie.title}: {e}")
                        movie.enhanced_data = {}
                    
                    # Add to local database for future requests
                    self.movies_db.append(movie)
                    self.logger.info(f"✅ Fetched and cached movie: {movie.title}")
                    return movie
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch movie from OMDB: {e}")
        
        self.logger.warning(f"❌ Movie {movie_id} not found anywhere")
        return None
    
    async def get_movie_analysis(self, movie_id: str) -> Optional[AnalyticsData]:
        """Get comprehensive analysis data for a specific movie with enhanced insights"""
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            self.logger.warning(f"Movie {movie_id} not found for analysis")
            return None
        
        self.logger.info(f"🔍 Analyzing movie: {movie.title}")
          # Try to enrich movie data with scraping if possible
        try:
            if self.api_manager.scrapers:
                self.logger.info(f"🕷️ Enriching {movie.title} with web scraping data...")
                scraping_results = await self.api_manager._scrape_movie_data('imdb', movie.title)
                if scraping_results and 'reviews' in scraping_results:
                    # Convert scraped reviews to Review objects
                    scraped_reviews = scraping_results['reviews']
                    for review_data in scraped_reviews:
                        try:
                            # Ensure review_data is a dict, if it's already a Review object, convert to dict
                            if hasattr(review_data, '__dict__'):
                                review_dict = review_data.__dict__
                            else:
                                review_dict = review_data
                            
                            review_obj = Review(
                                id=review_dict.get('id', f'scraped-{len(movie.reviews)}'),
                                author=review_dict.get('author', 'Anonymous'),
                                content=review_dict.get('content', ''),
                                rating=review_dict.get('rating', 5.0),
                                sentiment=review_dict.get('sentiment', 'neutral'),
                                date=review_dict.get('date', '2024-01-01')
                            )
                            movie.reviews.append(review_obj)
                        except Exception as e:
                            self.logger.warning(f"Failed to convert review: {e}")
                            continue
                    
                    self.logger.info(f"✅ Added {len(scraped_reviews)} scraped reviews")
        except Exception as e:
            self.logger.warning(f"Failed to enrich with scraping: {e}")
        
        # Generate sentiment analysis for reviews (with safe access)
        positive_reviews = 0
        negative_reviews = 0
        neutral_reviews = 0
        
        for review in movie.reviews:
            try:
                if hasattr(review, 'sentiment'):
                    if review.sentiment == "positive":
                        positive_reviews += 1
                    elif review.sentiment == "negative":
                        negative_reviews += 1
                    else:
                        neutral_reviews += 1
                else:
                    neutral_reviews += 1  # Default for reviews without sentiment
            except Exception:
                neutral_reviews += 1  # Default for any error
          # Import the models we need
        from ..models.movie import GenreData, ReviewTimelineData, SentimentData, RatingDistributionData, MovieSummary
        
        # Generate rating distribution based on movie rating
        rating_score = int(movie.rating)
        rating_counts = [0] * 10
        
        # Create realistic distribution around the movie's rating
        if rating_score >= 8:  # High rated movie
            rating_counts = [1, 0, 1, 2, 3, 5, 8, 15, 25, 40]
        elif rating_score >= 6:  # Medium rated movie  
            rating_counts = [2, 3, 5, 8, 12, 18, 22, 15, 10, 5]
        else:  # Lower rated movie
            rating_counts = [10, 15, 20, 18, 12, 8, 5, 3, 2, 1]
        
        # Create proper RatingDistributionData objects
        rating_distribution = [
            RatingDistributionData(rating=i + 1, count=rating_counts[i])
            for i in range(10)
        ]
        
        # Generate genre analysis with proper GenreData objects
        genre_popularity = [
            GenreData(genre=genre, count=len([m for m in self.movies_db if genre in m.genre]))
            for genre in movie.genre
        ]
        
        # Generate review timeline with proper ReviewTimelineData objects
        review_timeline = [
            ReviewTimelineData(date="2024-01-15", count=max(len(movie.reviews) // 4, 1)),
            ReviewTimelineData(date="2024-02-15", count=max(len(movie.reviews) // 3, 2)),
            ReviewTimelineData(date="2024-03-15", count=max(len(movie.reviews) // 2, 3)),
            ReviewTimelineData(date="2024-04-15", count=len(movie.reviews))
        ]
        
        # Find similar movies by genre and convert to MovieSummary objects
        similar_movies = [
            m for m in self.movies_db 
            if m.id != movie.id and any(g in movie.genre for g in m.genre)
        ][:4]  # Take 4 to make room for the current movie
        
        # Convert movies to MovieSummary objects
        top_rated_movies = [MovieSummary(
            id=movie.id,
            title=movie.title,
            rating=movie.rating,
            year=movie.year        )] + [MovieSummary(
            id=m.id,
            title=m.title,
            rating=m.rating,
            year=m.year
        ) for m in similar_movies]
        
        recently_analyzed = [MovieSummary(
            id=movie.id,
            title=movie.title,
            rating=movie.rating,
            year=movie.year
        )]
        
        analysis_data = AnalyticsData(
            totalMovies=len(self.movies_db),
            totalReviews=len(movie.reviews),
            averageRating=movie.rating,
            sentimentDistribution=SentimentData(
                positive=positive_reviews,
                negative=negative_reviews,
                neutral=neutral_reviews
            ),
            ratingDistribution=rating_distribution,
            genrePopularity=genre_popularity,
            reviewTimeline=review_timeline,
            topRatedMovies=top_rated_movies,
            recentlyAnalyzed=recently_analyzed
        )
        
        self.logger.info(f"✅ Analysis complete for {movie.title}: {len(movie.reviews)} reviews, {movie.rating} rating")
        return analysis_data
    
    async def _search_omdb_with_retry(self, query: str, limit: int) -> List[Movie]:
        """Search OMDB API with retry mechanism and proper timeout"""
        import asyncio
        
        max_retries = 2
        retry_delay = 1.0  # Start with 1 second delay
        timeout = 8.0  # 8 second timeout
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"🔍 OMDB attempt {attempt + 1}/{max_retries + 1} for '{query}' (timeout: {timeout}s)")
                
                # Use asyncio.wait_for to enforce timeout
                omdb_task = self.api_manager.omdb_api.search_movies(query, limit)
                omdb_results = await asyncio.wait_for(omdb_task, timeout=timeout)
                
                if omdb_results:
                    # Convert dict results to Movie objects
                    movies = []
                    for movie_data in omdb_results:
                        if movie_data.get('source') in ['omdb', 'omdb_live']:  # Only real OMDB data
                            # Process poster image URL
                            poster_url = movie_data.get('poster', '')
                            processed_poster = self._process_movie_image(poster_url, 'omdb')
                            
                            movie = Movie(
                                id=movie_data.get('id', ''),
                                title=movie_data.get('title', ''),
                                plot=movie_data.get('plot', ''),
                                rating=movie_data.get('rating', 0),
                                genre=movie_data.get('genre', []),
                                year=movie_data.get('year', 0),
                                poster=processed_poster,
                                director=movie_data.get('director', ''),
                                cast=movie_data.get('cast', []),
                                reviews=[],
                                imdbId=movie_data.get('imdbId'),
                                runtime=movie_data.get('runtime', 120)
                            )
                            movies.append(movie)
                    
                    if movies:
                        self.logger.info(f"✅ OMDB retry success: {len(movies)} movies on attempt {attempt + 1}")
                        return movies
                
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ OMDB timeout on attempt {attempt + 1} after {timeout}s")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    
            except Exception as e:
                self.logger.warning(f"❌ OMDB error on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        self.logger.warning(f"❌ OMDB failed after {max_retries + 1} attempts")
        return []
    
    async def _search_with_web_scraping(self, query: str, limit: int) -> List[Movie]:
        """Search using web scraping as secondary option"""
        try:
            self.logger.info(f"🕷️ Trying web scraping for '{query}'")
            
            # Try Scrapy search service first if available
            if hasattr(self.api_manager, 'scrapy_search') and self.api_manager.scrapy_search:
                scrapy_results = await self.api_manager.scrapy_search.search_movies(query, limit)
                if scrapy_results:
                    # Convert dict results to Movie objects
                    movies = []
                    for movie_data in scrapy_results:
                        # Process poster image URL
                        poster_url = movie_data.get('poster', '')
                        processed_poster = self._process_movie_image(poster_url, 'scraped')
                        
                        movie = Movie(
                            id=movie_data.get('id', ''),
                            title=movie_data.get('title', ''),
                            plot=movie_data.get('plot', ''),
                            rating=movie_data.get('rating', 0),
                            genre=movie_data.get('genre', []),
                            year=movie_data.get('year', 0),
                            poster=processed_poster,
                            director=movie_data.get('director', ''),
                            cast=movie_data.get('cast', []),
                            reviews=[],
                            imdbId=movie_data.get('imdbId'),
                            runtime=movie_data.get('runtime', 120)
                        )
                        movies.append(movie)
                    
                    self.logger.info(f"✅ Scrapy search success: {len(movies)} movies")
                    return movies
            
            # Try legacy web scraping if Scrapy not available
            if self.api_manager.scrapers:
                scraping_results = await self.api_manager._search_with_scraping(query, limit)
                if scraping_results:
                    # Convert dict results to Movie objects
                    movies = []
                    for movie_data in scraping_results:
                        # Process poster image URL
                        poster_url = movie_data.get('poster', '')
                        processed_poster = self._process_movie_image(poster_url, 'scraped')
                        
                        movie = Movie(
                            id=movie_data.get('id', ''),
                            title=movie_data.get('title', ''),
                            plot=movie_data.get('plot', ''),
                            rating=movie_data.get('rating', 0),
                            genre=movie_data.get('genre', []),
                            year=movie_data.get('year', 0),
                            poster=processed_poster,
                            director=movie_data.get('director', ''),
                            cast=movie_data.get('cast', []),
                            reviews=[],
                            imdbId=movie_data.get('imdbId'),
                            runtime=movie_data.get('runtime', 120)
                        )
                        movies.append(movie)
                    
                    self.logger.info(f"✅ Legacy scraping success: {len(movies)} movies")
                    return movies
                    
        except Exception as e:
            self.logger.warning(f"❌ Web scraping failed: {e}")
        
        return []
    
    async def _cache_search_results(self, cache_key: str, results: List[Movie]) -> None:
        """Cache search results for future use"""
        try:
            # Convert Movie objects to dicts for caching
            cached_data = []
            for movie in results:
                cached_data.append({
                    'id': movie.id,
                    'title': movie.title,
                    'plot': movie.plot,
                    'rating': movie.rating,
                    'genre': movie.genre,
                    'year': movie.year,
                    'poster': movie.poster,
                    'director': movie.director,
                    'cast': movie.cast,
                    'imdbId': movie.imdbId,
                    'runtime': movie.runtime
                })
            
            # Use API manager's cache if available
            if hasattr(self.api_manager, 'cache') and self.api_manager.cache:
                self.api_manager.cache.set(cache_key, cached_data, ttl=7200)  # 2 hours
                self.logger.info(f"💾 Cached {len(cached_data)} results for key: {cache_key}")
                
        except Exception as e:
            self.logger.warning(f"❌ Failed to cache results: {e}")
    
    async def _check_cache(self, cache_key: str) -> List[Movie]:
        """Check cache for existing search results"""
        try:
            if hasattr(self.api_manager, 'cache') and self.api_manager.cache:
                cached_data = self.api_manager.cache.get(cache_key)
                if cached_data:
                    # Convert cached dicts back to Movie objects
                    movies = []
                    for movie_data in cached_data:
                        # Process poster image URL
                        poster_url = movie_data.get('poster', '')
                        processed_poster = self._process_movie_image(poster_url, 'generic')
                        
                        movie = Movie(
                            id=movie_data.get('id', ''),
                            title=movie_data.get('title', ''),
                            plot=movie_data.get('plot', ''),
                            rating=movie_data.get('rating', 0),
                            genre=movie_data.get('genre', []),
                            year=movie_data.get('year', 0),
                            poster=processed_poster,
                            director=movie_data.get('director', ''),
                            cast=movie_data.get('cast', []),
                            reviews=[],
                            imdbId=movie_data.get('imdbId'),
                            runtime=movie_data.get('runtime', 120)
                        )
                        movies.append(movie)
                    
                    self.logger.info(f"💾 Cache hit: {len(movies)} movies for key: {cache_key}")
                    return movies
                    
        except Exception as e:
            self.logger.warning(f"❌ Cache check failed: {e}")
        
        return []
    
    async def _search_movies_in_db(self, query: str, limit: int) -> List[Dict]:
        """Search movies in database as fallback"""
        try:
            # Search in local movies_db first
            local_results = []
            query_lower = query.lower()
            
            for movie in self.movies_db:
                if (query_lower in movie.title.lower() or 
                    any(query_lower in genre.lower() for genre in movie.genre) or
                    query_lower in movie.director.lower() or
                    any(query_lower in actor.lower() for actor in movie.cast)):
                    
                    local_results.append({
                        'id': movie.id,
                        'title': movie.title,
                        'plot': movie.plot,
                        'rating': movie.rating,
                        'genre': movie.genre,
                        'year': movie.year,
                        'poster': movie.poster,
                        'director': movie.director,
                        'cast': movie.cast,
                        'imdbId': movie.imdbId,
                        'runtime': movie.runtime
                    })
            
            if local_results:
                self.logger.info(f"💾 Local DB search found {len(local_results)} results")
                return local_results[:limit]
            
            # Try database collections if available
            if self.movies_collection:
                # This would be implemented based on your database structure
                pass
                
        except Exception as e:
            self.logger.warning(f"❌ Database search failed: {e}")
        
        return []
    
    async def _convert_dict_to_movie(self, movie_data: Dict) -> Optional[Movie]:
        """Convert dictionary data to Movie object"""
        try:
            if not movie_data:
                return None
            
            # Process poster image URL
            poster_url = movie_data.get('poster', '')
            source = movie_data.get('source', 'generic')
            processed_poster = self._process_movie_image(poster_url, source)
                
            return Movie(
                id=movie_data.get('id', ''),
                title=movie_data.get('title', ''),
                plot=movie_data.get('plot', ''),
                rating=movie_data.get('rating', 0),
                genre=movie_data.get('genre', []),
                year=movie_data.get('year', 0),
                poster=processed_poster,
                director=movie_data.get('director', ''),
                cast=movie_data.get('cast', []),
                reviews=[],
                imdbId=movie_data.get('imdbId'),
                runtime=movie_data.get('runtime', 120)
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to convert dict to Movie: {e}")
            return None
    
    async def _get_movie_from_db(self, movie_id: str) -> Optional[Dict]:
        """Get movie from database by ID"""
        try:
            # Search in local movies_db first
            for movie in self.movies_db:
                if str(movie.id) == str(movie_id):
                    return {
                        'id': movie.id,
                        'title': movie.title,
                        'plot': movie.plot,
                        'rating': movie.rating,
                        'genre': movie.genre,
                        'year': movie.year,
                        'poster': movie.poster,
                        'director': movie.director,
                        'cast': movie.cast,
                        'imdbId': movie.imdbId,
                        'runtime': movie.runtime
                    }
            
            # Try database collections if available
            if self.movies_collection:
                # This would be implemented based on your database structure
                pass
                
        except Exception as e:
            self.logger.warning(f"❌ Database get movie failed: {e}")
        
        return None

    async def analyze_movie(self, movie_id: str) -> str:
        """Trigger comprehensive analysis for a specific movie"""
        self.logger.info(f"🔍 Starting analysis for movie: {movie_id}")
        
        # Get the movie details
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            raise ValueError(f"Movie {movie_id} not found")
        
        # Perform the analysis (this calls get_movie_analysis internally)
        analysis_result = await self.get_movie_analysis(movie_id)
        if not analysis_result:
            raise ValueError(f"Analysis failed for movie {movie_id}")
        
        # Store analysis timestamp for tracking
        task_id = f"analysis_task_{movie_id}_{int(datetime.now().timestamp())}"
        
        self.logger.info(f"✅ Analysis completed for {movie.title}: {analysis_result.totalReviews} reviews analyzed")
        
        return task_id

    async def get_analytics(self) -> AnalyticsData:
        """Get overall analytics data"""
        from ..models.movie import GenreData, ReviewTimelineData
        
        all_reviews = []
        for movie in self.movies_db:
            all_reviews.extend(movie.reviews)
        
        # Calculate genre distribution
        genre_counts = {}
        for movie in self.movies_db:
            for genre in movie.genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Create GenreData objects instead of dicts
        genre_popularity = [GenreData(genre=genre, count=count) for genre, count in genre_counts.items()]
        
        # Create ReviewTimelineData objects instead of dicts
        review_timeline = [
            ReviewTimelineData(date="2024-01-15", count=1),
            ReviewTimelineData(date="2024-01-20", count=1),
            ReviewTimelineData(date="2024-01-25", count=1)
        ]
        
        return AnalyticsData(
            totalMovies=len(self.movies_db),
            totalReviews=len(all_reviews),
            averageRating=sum(m.rating for m in self.movies_db) / len(self.movies_db) if self.movies_db else 0,
            sentimentDistribution=SentimentData(
                positive=len([r for r in all_reviews if r.sentiment == "positive"]),
                negative=len([r for r in all_reviews if r.sentiment == "negative"]),
                neutral=len([r for r in all_reviews if r.sentiment == "neutral"])
            ),
            ratingDistribution=[
                RatingDistributionData(rating=i+1, count=cnt)
                for i, cnt in enumerate([2, 1, 0, 1, 3, 5, 8, 12, 15, 25])
            ],
            genrePopularity=genre_popularity,
            reviewTimeline=review_timeline,
            topRatedMovies=[
                MovieSummary(
                    id=m.id,
                    title=m.title,
                    rating=m.rating,
                    year=m.year
                ) for m in sorted(self.movies_db, key=lambda x: x.rating, reverse=True)[:5]
            ],
            recentlyAnalyzed=[
                MovieSummary(
                    id=m.id,
                    title=m.title,
                    rating=m.rating,
                    year=m.year
                ) for m in self.movies_db[-3:]
            ]
        )
    
    async def get_suggestions(self, limit: int = 12) -> List[Movie]:
        """Get enhanced movie suggestions from comprehensive service"""
        self.logger.info(f"🎬 Getting enhanced suggestions using comprehensive service...")
        
        try:
            # Use comprehensive service for enhanced suggestions
            suggestions = await self.comprehensive_service.get_enhanced_suggestions(limit)
            
            if suggestions:
                self.logger.info(f"✅ Comprehensive service returned {len(suggestions)} suggestions")
                return suggestions
            
        except Exception as e:
            self.logger.warning(f"Comprehensive service failed, using fallback: {e}")
        
        # Fallback to original implementation
        return await self._get_fallback_suggestions(limit)
    
    async def _get_fallback_suggestions(self, limit: int = 8) -> List[Movie]:
        """Get movie and series suggestions with accurate popular content"""
        # Target the exact popular shows the user mentioned
        popular_titles = [
            "House of the Dragon",  # HBO - User specifically mentioned
            "Stranger Things",      # Netflix - User specifically mentioned  
            "Game of Thrones",      # HBO
            "Breaking Bad",         # Netflix
            "The Witcher",          # Netflix
            "Wednesday",            # Netflix
            "The Boys",             # Amazon Prime
            "Euphoria",             # HBO
            "Ozark",                # Netflix
            "The Crown",            # Netflix
            "Better Call Saul",     # Netflix
            "Succession"            # HBO
        ]
        
        suggestions = []
        
        self.logger.info(f"🎬 Fetching suggestions for popular shows...")
        
        try:
            # Prioritize the exact titles user mentioned
            priority_titles = ["House of the Dragon", "Stranger Things"]
            remaining_titles = [t for t in popular_titles if t not in priority_titles]
            search_order = priority_titles + remaining_titles
            
            for title in search_order:
                if len(suggestions) >= limit:
                    break
                    
                try:
                    self.logger.info(f"🔍 Searching for: {title}")
                    
                    # Search with enhanced matching
                    api_results = await self.api_manager.search_movies(title, 5)
                    
                    # Find the best match (prefer exact matches)
                    best_match = None
                    exact_match = None
                    
                    for result in api_results:
                        result_title = result.get('title', '').lower().strip()
                        search_title = title.lower().strip()
                        
                        # Check for exact match first
                        if result_title == search_title:
                            exact_match = result
                            break
                        # Check for close match
                        elif (search_title in result_title or 
                              result_title in search_title or
                              result_title.replace(':', '').replace('the ', '') == search_title.replace(':', '').replace('the ', '')):
                            if not best_match or result.get('rating', 0) > best_match.get('rating', 0):
                                best_match = result
                    
                    selected_result = exact_match or best_match
                    
                    if selected_result and selected_result.get('rating', 0) > 5.0:
                        movie = Movie(
                            id=selected_result.get('id', f'popular-{len(suggestions)}'),
                            title=selected_result.get('title', title),
                            year=selected_result.get('year', 2020),
                            poster=selected_result.get('poster', '/placeholder.svg'),
                            rating=selected_result.get('rating', 8.0),
                            genre=selected_result.get('genre', ['Drama']),
                            plot=selected_result.get('plot', f'Popular series: {title}'),
                            director=selected_result.get('director', 'Various'),
                            cast=selected_result.get('cast', ['Various']),
                            reviews=selected_result.get('reviews', []),
                            imdbId=selected_result.get('imdbId'),
                            runtime=selected_result.get('runtime', 60)
                        )
                        suggestions.append(movie)
                        self.logger.info(f"✅ Added: {movie.title} (Rating: {movie.rating})")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to fetch {title}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
        
        # Add high-quality fallbacks for missing popular shows
        if len(suggestions) < limit:
            self.logger.info("🔄 Adding fallback popular shows...")
            fallback_suggestions = [
                Movie(
                    id="hotd-fallback",
                    title="House of the Dragon",
                    year=2022,
                    poster="/placeholder.svg?height=600&width=400",
                    rating=8.5,
                    genre=["Drama", "Fantasy", "Action"],
                    plot="An internal succession war within House Targaryen at the height of its power, 172 years before the birth of Daenerys.",
                    director="Ryan J. Condal",
                    cast=["Paddy Considine", "Emma D'Arcy", "Matt Smith", "Olivia Cooke"],
                    reviews=[],
                    runtime=60
                ),
                Movie(
                    id="st-fallback",
                    title="Stranger Things",
                    year=2016,
                    poster="/placeholder.svg?height=600&width=400",
                    rating=8.7,
                    genre=["Drama", "Fantasy", "Horror", "Thriller"],
                    plot="When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces in order to get him back.",
                    director="The Duffer Brothers",
                    cast=["Millie Bobby Brown", "Finn Wolfhard", "David Harbour", "Winona Ryder"],
                    reviews=[],
                    runtime=50
                ),
                Movie(
                    id="bb-fallback",
                    title="Breaking Bad",
                    year=2008,
                    poster="/placeholder.svg?height=600&width=400",
                    rating=9.5,
                    genre=["Crime", "Drama", "Thriller"],
                    plot="A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.",
                    director="Vince Gilligan",
                    cast=["Bryan Cranston", "Aaron Paul", "Anna Gunn"],
                    reviews=[],
                    runtime=47
                ),
                Movie(
                    id="witcher-fallback",
                    title="The Witcher",
                    year=2019,
                    poster="/placeholder.svg?height=600&width=400",
                    rating=8.2,
                    genre=["Action", "Adventure", "Drama", "Fantasy"],
                    plot="Geralt of Rivia, a solitary monster hunter, struggles to find his place in a world where people often prove more wicked than beasts.",
                    director="Lauren Schmidt Hissrich",
                    cast=["Henry Cavill", "Anya Chalotra", "Freya Allan"],
                    reviews=[],
                    runtime=60
                )
            ]
            
            # Add fallbacks for missing slots, avoiding duplicates
            for fallback in fallback_suggestions:
                if len(suggestions) < limit and not any(s.title.lower() == fallback.title.lower() for s in suggestions):
                    suggestions.append(fallback)
        
        self.logger.info(f"🎬 Returning {len(suggestions)} suggestions")
        return suggestions[:limit]

    async def get_movie_analysis_fast(self, movie_id: str) -> Optional[AnalyticsData]:
        """FAST movie analysis - prioritizes OMDB API, minimal scraping with timeout"""
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return None
        
        self.logger.info(f"⚡ FAST Analysis for: {movie.title}")
        
        # STEP 1: Quick OMDB enhancement (fast API call)
        try:
            if movie.imdbId or movie_id.startswith('tt'):
                imdb_id = movie.imdbId or movie_id
                omdb_data = await self.api_manager.omdb_api.get_movie_by_id(imdb_id)
                if omdb_data and omdb_data.get('rating', 0) > movie.rating:
                    movie.rating = omdb_data.get('rating', movie.rating)
                    self.logger.info(f"📡 Enhanced with OMDB: {movie.rating}")
        except Exception as e:
            self.logger.warning(f"OMDB skip: {e}")
        
        # STEP 2: Generate realistic data immediately (no waiting)
        positive_reviews = max(int(movie.rating) - 3, 0) * 2
        negative_reviews = max(7 - int(movie.rating), 0) 
        neutral_reviews = 3
        total_reviews = positive_reviews + negative_reviews + neutral_reviews
        
        movie.reviews = []
        
        # Create synthetic reviews based on rating
        for _ in range(positive_reviews):
            movie.reviews.append(Review(
                id=f"pos-{_}",
                author="Reviewer",
                content="Great movie!",
                rating=random.uniform(7.5, 10.0),
                sentiment="positive",
                date="2024-01-15"
            ))
        
        for _ in range(negative_reviews):
            movie.reviews.append(Review(
                id=f"neg-{_}",
                author="Reviewer",
                content="Terrible movie!",
                rating=random.uniform(0.0, 2.5),
                sentiment="negative",
                date="2024-01-15"
            ))
        
        for _ in range(neutral_reviews):
            movie.reviews.append(Review(
                id=f"neu-{_}",
                author="Reviewer",
                content="It was okay, not great but not bad.",
                rating=random.uniform(3.0, 7.0),
                sentiment="neutral",
                date="2024-01-15"
            ))
        
        # Shuffle reviews to mix positive, negative, and neutral
        random.shuffle(movie.reviews)
        
        # Limit to realistic number of reviews
        movie.reviews = movie.reviews[:total_reviews]
        
        # Update movie rating based on generated reviews
        if movie.reviews:
            movie.rating = sum(review.rating for review in movie.reviews) / len(movie.reviews)
        
        self.logger.info(f"✅ FAST Analysis complete for {movie.title}: {len(movie.reviews)} reviews, {movie.rating} rating")
        return await self.get_movie_analysis(movie_id)  # Return full analysis object
    
    async def _fast_local_search(self, query: str, limit: int) -> List[Movie]:
        """FAST local search - optimized for speed and accuracy"""
        self.logger.info(f"⚡ FAST Local Search: '{query}' (limit: {limit})")
        
        results = []
        
        # Normalize query for consistent matching
        query = query.lower().strip()
        
        try:
            # 1. Exact title match first
            exact_matches = [m for m in self.movies_db if m.title.lower() == query]
            results.extend(exact_matches)
            
            if len(results) >= limit:
                self.logger.info(f"✅ Found {len(results)} exact matches")
                return results[:limit]
              # 2. Smart fuzzy title matches (simple approach)
            if len(results) < limit:
                query_words = query.lower().split()
                for movie in self.movies_db:
                    if len(results) >= limit:
                        break
                    if movie in results:
                        continue
                    
                    # Check if most query words appear in title
                    title_words = movie.title.lower().split()
                    matches = sum(1 for qword in query_words if any(qword in tword for tword in title_words))
                    
                    if matches >= len(query_words) * 0.7:  # 70% word match threshold
                        results.append(movie)
            
            if len(results) >= limit:
                self.logger.info(f"✅ Found {len(results)} fuzzy matches")
                return results[:limit]
            
            # 3. Keyword matches in title or plot
            keyword_matches = [m for m in self.movies_db 
                               if query in m.title.lower() or query in m.plot.lower()]
            results.extend(keyword_matches)
            
            if len(results) >= limit:
                self.logger.info(f"✅ Found {len(results)} keyword matches")
                return results[:limit]
            
            # 4. Random sampling from the database as a last resort
            self.logger.info("🎲 No matches found, sampling from database")
            all_movies = self.movies_db.copy()
            random.shuffle(all_movies)
            results = all_movies[:limit]
            
        except Exception as e:
            self.logger.error(f"Error during fast local search: {e}")
        
        self.logger.info(f"🎬 FAST Local Search complete: {len(results)} results")
        return results[:limit]
    
    async def _fast_local_search_async(self, query: str, limit: int) -> List[Movie]:
        """Async version of fast local search"""
        return await self._fast_local_search(query, limit)
    
    def _create_movie_from_data(self, movie_data: dict, fallback_id: str) -> Optional[Movie]:
        """Create Movie object from data with enhanced error handling"""
        try:
            return Movie(
                id=movie_data.get('id', movie_data.get('imdbID', fallback_id)),
                title=movie_data.get('title', movie_data.get('Title', 'Unknown Title')),
                year=int(movie_data.get('year', movie_data.get('Year', 2000))),
                poster=self._get_enhanced_poster(movie_data),
                rating=float(movie_data.get('rating', movie_data.get('imdbRating', 5.0))),
                genre=movie_data.get('genre', movie_data.get('Genre', ['Unknown'])),
                plot=movie_data.get('plot', movie_data.get('Plot', 'No plot available.')),
                director=movie_data.get('director', movie_data.get('Director', 'Unknown Director')),
                cast=movie_data.get('cast', movie_data.get('Actors', ['Unknown Cast'])),
                reviews=[],
                imdbId=movie_data.get('imdbId', movie_data.get('imdbID')),
                runtime=int(movie_data.get('runtime', movie_data.get('Runtime', '120').replace(' min', '')))
            )
        except Exception as e:
            self.logger.warning(f"Error creating movie from data: {e}")
            return None

    async def _check_cache(self, cache_key: str) -> Optional[List[Movie]]:
        """Check cache for existing search results"""
        try:
            if hasattr(self.api_manager, 'cache') and self.api_manager.cache:
                cached_data = self.api_manager.cache.get(cache_key)
                if cached_data:
                    return [self._convert_dict_to_movie(movie_data) for movie_data in cached_data if movie_data]
        except Exception as e:
            self.logger.warning(f"Cache check failed: {e}")
        return None

    async def _search_api_manager_with_timeout(self, query: str, limit: int) -> List[Movie]:
        """API Manager search with enhanced timeout handling"""
        try:
            # Use longer timeout for API manager as it tries multiple sources
            movie_data_list = await asyncio.wait_for(
                self.api_manager.search_movies(query, limit),
                timeout=10.0  # 10 second timeout for comprehensive search
            )
            
            if movie_data_list:
                movies = []
                for data in movie_data_list:
                    try:
                        movie = self._convert_dict_to_movie(data)
                        if movie:
                            movies.append(movie)
                    except Exception as e:
                        self.logger.warning(f"API Manager movie conversion error: {e}")
                        continue
                
                return movies
            
        except asyncio.TimeoutError:
            self.logger.warning("⏰ API Manager timeout after 10s")
        except Exception as e:
            self.logger.warning(f"API Manager error: {e}")
        
        return []
    
    async def _search_with_web_scraping(self, query: str, limit: int) -> List[Movie]:
        """Web scraping search as secondary option"""
        try:
            if not self.api_manager.scrapers and not self.api_manager.scrapy_search:
                return []
            
            movies = []
            
            # Try Scrapy search service first (more comprehensive)
            if self.api_manager.scrapy_search:
                try:
                    scrapy_results = await asyncio.wait_for(
                        self.api_manager.scrapy_search.search_movies(query, limit),
                        timeout=6.0  # 6 second timeout for scraping
                    )
                    
                    if scrapy_results:
                        for movie_data in scrapy_results[:limit]:
                            try:
                                movie = self._convert_dict_to_movie(movie_data)
                                if movie:
                                    movies.append(movie)
                            except Exception as e:
                                self.logger.warning(f"Scrapy movie conversion error: {e}")
                                continue
                        
                        if movies:
                            self.logger.info(f"🕷️ Scrapy found {len(movies)} movies")
                            return movies
                            
                except asyncio.TimeoutError:
                    self.logger.warning("⏰ Scrapy search timeout")
                except Exception as e:
                    self.logger.warning(f"Scrapy search error: {e}")
            
            # Try legacy web scrapers as fallback
            if self.api_manager.scrapers:
                try:
                    scraping_results = await asyncio.wait_for(
                        self.api_manager._search_with_scraping(query, limit),
                        timeout=4.0  # 4 second timeout for legacy scraping
                    )
                    
                    if scraping_results:
                        for movie_data in scraping_results[:limit]:
                            try:
                                movie = self._convert_dict_to_movie(movie_data)
                                if movie:
                                    movies.append(movie)
                            except Exception as e:
                                self.logger.warning(f"Legacy scraping movie conversion error: {e}")
                                continue
                        
                        if movies:
                            self.logger.info(f"🕷️ Legacy scraping found {len(movies)} movies")
                            return movies
                            
                except asyncio.TimeoutError:
                    self.logger.warning("⏰ Legacy scraping timeout")
                except Exception as e:
                    self.logger.warning(f"Legacy scraping error: {e}")
            
        except Exception as e:
            self.logger.error(f"Web scraping search failed: {e}")
        
        return []
    
    async def _cache_search_results(self, cache_key: str, movies: List[Movie]):
        """Cache search results for future use"""
        try:
            if hasattr(self.api_manager, 'cache') and self.api_manager.cache and movies:
                movie_dicts = [self._movie_to_dict(movie) for movie in movies]
                self.api_manager.cache.set(cache_key, movie_dicts, ttl=7200)  # 2 hour cache
                self.logger.info(f"💾 Cached {len(movies)} search results")
        except Exception as e:
            self.logger.warning(f"Cache save error: {e}")
    
    async def _search_local_enhanced(self, query: str, limit: int) -> List[Movie]:
        """Enhanced local search with fuzzy matching"""
        try:
            results = []
            query_words = query.lower().split()
            
            for movie in self.movies_db:
                if len(results) >= limit:
                    break
                    
                # Multi-field matching
                movie_text = f"{movie.title} {' '.join(movie.genre)} {movie.plot}".lower()
                
                # Check for exact matches first
                if query in movie.title.lower():
                    results.insert(0, movie)  # Priority for exact title matches
                    continue
                
                # Check for word matches
                if any(word in movie_text for word in query_words):
                    results.append(movie)
                    continue
            
            self.logger.info(f"🏠 Local: {len(results)} movies found")
            return results[:limit]
            
        except Exception as e:
            self.logger.warning(f"Local search error: {e}")
            return []
    
    async def _search_smart_suggestions(self, query: str, limit: int) -> List[Movie]:
        """Smart suggestions based on query patterns"""
        try:
            # Use the existing instant suggestions system
            suggestions = self._generate_instant_suggestions(query, limit)
            self.logger.info(f"💡 Smart suggestions: {len(suggestions)} movies")
            return suggestions
        except Exception as e:
            self.logger.warning(f"Smart suggestions error: {e}")
            return []
    
    async def _execute_parallel_search(self, search_tasks: List, query: str, limit: int) -> Dict[str, List[Movie]]:
        """Execute search tasks in parallel with proper timeout handling"""
        results = {}
        
        try:            # Wait for all tasks with overall timeout
            done, pending = await asyncio.wait(
                [task for _, task in search_tasks],
                timeout=3.0,  # Reduced to 3s for better UX
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            # Collect results from completed tasks
            for search_type, task in search_tasks:
                if task in done:
                    try:
                        result = await task
                        results[search_type] = result if result else []
                    except Exception as e:
                        self.logger.warning(f"{search_type} task failed: {e}")
                        results[search_type] = []
                else:
                    results[search_type] = []
                    
        except Exception as e:
            self.logger.error(f"Parallel search execution error: {e}")
            # Ensure all search types have empty lists
            for search_type, _ in search_tasks:
                results[search_type] = []
        
        return results
    
    async def _process_search_results(self, results: Dict[str, List[Movie]], query: str, limit: int) -> List[Movie]:
        """Process and merge search results with intelligent ranking"""
        final_movies = []
        seen_titles = set()
        
        try:
            # Priority order: OMDB (highest quality) -> Local -> Suggestions
            search_order = ['omdb', 'local', 'suggestions']
            
            for search_type in search_order:
                movies = results.get(search_type, [])
                
                for movie in movies:
                    if len(final_movies) >= limit:
                        break
                        
                    # Avoid duplicates by title
                    title_key = movie.title.lower().strip()
                    if title_key not in seen_titles:
                        seen_titles.add(title_key)
                        final_movies.append(movie)
                        
                if len(final_movies) >= limit:
                    break
            
            # If still not enough results, try API Manager as backup
            if len(final_movies) < min(limit, 3):
                self.logger.info("🔄 Low results, trying API Manager backup...")
                try:
                    backup_results = await asyncio.wait_for(
                        self.api_manager.search_movies(query, limit - len(final_movies)),
                        timeout=3.0
                    )
                    
                    for movie_data in backup_results:
                        if len(final_movies) >= limit:
                            break
                        try:
                            movie = self._convert_dict_to_movie(movie_data)
                            if movie and movie.title.lower() not in seen_titles:
                                final_movies.append(movie)
                                seen_titles.add(movie.title.lower())
                        except Exception as e:
                            self.logger.warning(f"Failed to process movie data: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"API Manager backup failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Result processing error: {e}")
        
        return final_movies
    
    async def _cache_results(self, cache_key: str, movies: List[Movie]):
        """Cache search results for future use"""
        try:
            if hasattr(self.api_manager, 'cache') and self.api_manager.cache and movies:
                movie_dicts = [self._movie_to_dict(movie) for movie in movies]
                self.api_manager.cache.set(cache_key, movie_dicts, ttl=1800)  # 30 min cache
        except Exception as e:
            self.logger.warning(f"Cache save error: {e}")
    
    async def _get_trending_suggestions(self, limit: int) -> List[Movie]:
        """Get trending movie suggestions for empty queries"""
        try:
            trending_movies = self._generate_instant_suggestions("trending", limit)
            self.logger.info(f"📈 Trending: {len(trending_movies)} movies")
            return trending_movies
        except Exception as e:
            self.logger.error(f"Trending suggestions error: {e}")
            return []
    
    async def _emergency_fallback(self, query: str, limit: int) -> List[Movie]:
        """Emergency fallback when all search methods fail"""
        try:
            self.logger.info("🚨 Emergency fallback - using local demo data")
            # Use the existing fast local search as last resort
            return self._fast_local_search(query, limit)
        except Exception as e:
            self.logger.error(f"Emergency fallback error: {e}")
            # Return empty list rather than crash
            return []
    
    def _convert_dict_to_movie(self, movie_data: dict) -> Optional[Movie]:
        """Convert movie dictionary to Movie object efficiently"""
        try:
            if not movie_data:
                return None
            
            # Process poster image URL
            poster_url = self._get_enhanced_poster(movie_data)
            source = movie_data.get('source', 'generic')
            processed_poster = self._process_movie_image(poster_url, source)
                
            return Movie(
                id=movie_data.get('id', f"movie_{len(self.movies_db)}"),
                title=movie_data.get('title', 'Unknown Title'),
                year=int(movie_data.get('year', 2000)),
                poster=processed_poster,
                rating=float(movie_data.get('rating', 5.0)),
                genre=movie_data.get('genre', ['Unknown']),
                plot=movie_data.get('plot', 'No plot available.'),
                director=movie_data.get('director', 'Unknown Director'),
                cast=movie_data.get('cast', ['Unknown Cast']),
                reviews=[],
                imdbId=movie_data.get('imdbId'),
                runtime=int(movie_data.get('runtime', 120))
            )
        except Exception as e:
            self.logger.warning(f"Error converting movie dict: {e}")
            return None
    
    def _movie_to_dict(self, movie: Movie) -> dict:
        """Convert Movie object to dictionary for caching"""
        return {
            'id': movie.id,
            'title': movie.title,
            'year': movie.year,
            'poster': movie.poster,
            'rating': movie.rating,
            'genre': movie.genre,
            'plot': movie.plot,
            'director': movie.director,
            'cast': movie.cast,
            'imdbId': movie.imdbId,
            'runtime': movie.runtime
        }
    
    def _get_enhanced_poster(self, movie_data: dict) -> str:
        """Get enhanced poster URL from multiple sources with real image fallbacks"""
        try:
            # First try to get poster from movie_data
            poster_url = movie_data.get('poster', movie_data.get('Poster', ''))
            
            # If we have a valid URL, clean and return it
            if poster_url and poster_url != 'N/A' and poster_url.startswith('http'):
                # Clean the URL by removing any whitespace or line breaks
                cleaned_url = poster_url.replace('\n', '').replace('\r', '').replace(' ', '').strip()
                return cleaned_url
            
            # Use real poster path method
            return self._get_real_poster_path(movie_data)
            
        except Exception as e:
            self.logger.warning(f"Error getting enhanced poster: {e}")
            return self._get_real_poster_path(movie_data)
    
    def _get_real_poster_path(self, movie_data: dict) -> str:
        """Get real poster path with multiple fallback strategies"""
        try:
            title = movie_data.get('title', movie_data.get('Title', 'Unknown'))
            year = movie_data.get('year', movie_data.get('Year', '2000'))
            imdb_id = movie_data.get('imdbId', movie_data.get('imdbID', ''))
            
            # Real poster mappings for popular movies
            popular_poster_map = {
                'the shawshank redemption': 'https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg',
                'the godfather': 'https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg',
                'batman': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                'the dark knight': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                'avengers': 'https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg',
                'inception': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
                'interstellar': 'https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg',
                'spider-man': 'https://m.media-amazon.com/images/M/MV5BZDEyN2NhMjgtMjdhNi00MmNlLWE5YTgtZGE4MzNjMTRlMGEwXkEyXkFqcGdeQXVyNDUyOTg3Njg@._V1_SX300.jpg',
                'iron man': 'https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5BanBnXkFtZTcwMTU0NTIzMw@@._V1_SX300.jpg'
            }
            
            # Check for exact title match
            title_lower = title.lower().strip()
            if title_lower in popular_poster_map:
                return popular_poster_map[title_lower]
            
            # Check for partial matches
            for movie_title, poster_url in popular_poster_map.items():
                if movie_title in title_lower or title_lower in movie_title:
                    return poster_url
            
            # Default high-quality placeholder with movie theme
            return f"https://dummyimage.com/300x450/1a1a1a/ffffff.png&text={title.replace(' ', '%20')}%0A({year})"
            
        except Exception as e:
            self.logger.warning(f"Error generating real poster path: {e}")
            return "https://dummyimage.com/300x450/1a1a1a/ffffff.png&text=Movie%0APoster"
    
    async def _ensure_database_connection(self):
        """Ensure database collections are initialized"""
        if self.movies_collection is None:
            self.movies_collection = await get_movies_collection()
            self.logger.info("🔗 Connected to movies collection")
        
        if self.cache_collection is None:
            self.cache_collection = await get_cache_collection()
            self.logger.info("🔗 Connected to cache collection")
    
    async def _save_movie_to_db(self, movie_data: dict):
        """Save movie data to database"""
        try:
            await self._ensure_database_connection()
            
            # Check if movie already exists
            existing = await self.movies_collection.find_one({"id": movie_data.get("id")})
            if existing:
                # Update existing movie
                await self.movies_collection.update_one(
                    {"id": movie_data.get("id")},
                    {"$set": {
                        **movie_data,
                        "last_updated": datetime.utcnow(),
                        "source": movie_data.get("source", "api")
                    }}
                )
                self.logger.info(f"📝 Updated movie: {movie_data.get('title')}")
            else:
                # Insert new movie
                await self.movies_collection.insert_one({
                    **movie_data,
                    "created_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow(),
                    "source": movie_data.get("source", "api")
                })
                self.logger.info(f"💾 Saved new movie: {movie_data.get('title')}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save movie to database: {e}")
    
    async def _get_movie_from_db(self, movie_id: str) -> Optional[dict]:
        """Get movie from database by ID"""
        try:
            await self._ensure_database_connection()
            movie = await self.movies_collection.find_one({"id": movie_id})
            if movie:
                self.logger.info(f"📖 Retrieved movie from DB: {movie.get('title')}")
                return movie
        except Exception as e:
            self.logger.error(f"❌ Failed to get movie from database: {e}")
        return None
    
    async def _search_movies_in_db(self, query: str, limit: int = 10) -> List[dict]:
        """Search movies in database"""
        try:
            await self._ensure_database_connection()
            
            # Search by title (case-insensitive)
            movies = await self.movies_collection.find({
                "title": {"$regex": query, "$options": "i"}
            }).limit(limit).to_list(length=limit)
            
            if movies:
                self.logger.info(f"🔍 Found {len(movies)} movies in DB for query: {query}")
                return movies
        except Exception as e:
            self.logger.error(f"❌ Failed to search movies in database: {e}")
        return []
    
    async def _save_search_results_to_db(self, movies: List[Movie], query: str):
        """Save search results to database for future queries"""
        try:
            for movie in movies:
                # Convert Movie object to dict for storage
                movie_data = {
                    "id": movie.id,
                    "title": movie.title,
                    "year": movie.year,
                    "rating": movie.rating,
                    "genre": movie.genre,
                    "plot": movie.plot,
                    "poster": movie.poster,
                    "director": movie.director,
                    "cast": movie.cast,
                    "search_query": query.lower(),  # Track what query found this movie
                }
                await self._save_movie_to_db(movie_data)
        except Exception as e:
            self.logger.error(f"❌ Failed to save search results to DB: {e}")
    
    async def _update_movie_in_db(self, movie: Movie):
        """Update movie in database"""
        try:
            await self._ensure_database_connection()
            
            # Convert movie to dict for database storage
            movie_dict = movie.dict()
            
            # Update the movie in the database
            result = await self.movies_collection.update_one(
                {"id": movie.id},
                {"$set": movie_dict},
                upsert=True  # Create if doesn't exist
            )
            
            if result.modified_count > 0 or result.upserted_id:
                self.logger.info(f"✅ Updated movie in database: {movie.title}")
                
                # Also update the local movies_db list
                for i, local_movie in enumerate(self.movies_db):
                    if local_movie.id == movie.id:
                        self.movies_db[i] = movie
                        break
                else:
                    # If not found in local list, add it
                    self.movies_db.append(movie)
                    
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to update movie in database: {e}")
            return False


# Create global instance
movie_service = MovieService()
