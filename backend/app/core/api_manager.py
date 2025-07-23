import asyncio
import logging
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from .omdb_api_enhanced import OMDbAPI  # Use enhanced OMDB API
from .tmdb_api import TMDBApi
from .hybrid_cache import HybridCache

# Import scrapers for data enrichment
try:
    from ..scraper.imdb_scraper import ImdbScraper
    from ..scraper.rotten_tomatoes_scraper import RottenTomatoesScraper
    from ..scraper.metacritic_scraper import MetacriticScraper
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    # Handle missing scraper dependencies gracefully
    SCRAPERS_AVAILABLE = False
    logging.warning(f"Web scrapers not available: {e}")

# Import Scrapy search service
try:
    from ..services.scrapy_search_service import ScrapySearchService
    SCRAPY_SEARCH_AVAILABLE = True
except ImportError as e:
    # Handle missing scrapy dependencies gracefully
    SCRAPY_SEARCH_AVAILABLE = False
    logging.warning(f"Scrapy search service not available: {e}")

load_dotenv()

class APIManager:
    """
    Comprehensive API Manager with prioritized data sources:
    1. OMDB API (PRIMARY - highest quality, most comprehensive data)
    2. Scrapy Search (SECONDARY - comprehensive web scraping)
    3. Legacy Web scraping (TERTIARY - rich detailed data from IMDb, RT, etc.)
    4. TMDB API (QUATERNARY - last resort for live data)
    5. Fallback data (EMERGENCY - demo/mock data only)
    
    Features:
    - Redis-like caching for performance
    - Automatic data enrichment via web scraping
    - Intelligent fallback hierarchy
    - Cost optimization (prioritizes free/cheap sources)
    """    
    def __init__(self):
        # Initialize logger first
        self.logger = logging.getLogger(__name__)
        
        # Load API keys from environment with better validation
        omdb_key = os.getenv("OMDB_API_KEY")
        tmdb_key = os.getenv("TMDB_API_KEY")
        
        # Validate API keys with better error handling
        self.has_omdb = bool(omdb_key and omdb_key != "demo_key" and len(omdb_key) > 5)
        self.has_tmdb = bool(tmdb_key and tmdb_key != "demo_key_12345" and len(tmdb_key) > 5)
        
        if not self.has_omdb:
            self.logger.warning("⚠️ OMDB API key missing/invalid - using fallback data sources")
        else:
            self.logger.info(f"✅ OMDB API key loaded: {omdb_key[:8]}...")
            
        if not self.has_tmdb:
            self.logger.warning("⚠️ TMDB API key missing/invalid - using fallback data sources")
        else:
            self.logger.info(f"✅ TMDB API key loaded: {tmdb_key[:8]}...")
        
        # Initialize APIs with error handling
        try:
            self.omdb_api = OMDbAPI(omdb_key or "demo_key")
        except Exception as e:
            self.logger.error(f"❌ OMDB API initialization failed: {e}")
            self.omdb_api = None
            self.has_omdb = False
            
        try:
            self.tmdb_api = TMDBApi(tmdb_key or "demo_key_12345")
        except Exception as e:
            self.logger.error(f"❌ TMDB API initialization failed: {e}")
            self.tmdb_api = None
            self.has_tmdb = False
        
        # Initialize cache with error handling
        try:
            self.cache = HybridCache()
            self.logger.info("💾 Hybrid cache system initialized")
        except Exception as e:
            self.logger.error(f"❌ Cache initialization failed: {e}")
            self.cache = None
        
        # Initialize Scrapy search service
        self.scrapy_search = None
        if SCRAPY_SEARCH_AVAILABLE:
            try:
                self.scrapy_search = ScrapySearchService()
                self.logger.info("🕷️ Scrapy search service initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Scrapy search: {e}")
                self.scrapy_search = None
          # Initialize scrapers if available  
        self.scrapers = {}
        if SCRAPERS_AVAILABLE:
            try:
                # Temporarily disable ImdbScraper due to Chrome driver issues
                self.scrapers = {
                    # 'imdb': ImdbScraper(),  # Disabled - Chrome driver issues
                    'rotten_tomatoes': RottenTomatoesScraper(),
                    'metacritic': MetacriticScraper()
                }
                self.logger.info(f"🕷️ Initialized {len(self.scrapers)} web scrapers")
            except Exception as e:
                self.logger.warning(f"Failed to initialize scrapers: {e}")
                self.scrapers = {}
        
        # Log initialization status with new priority order
        self.logger.info("🎯 API Priority Order:")
        self.logger.info(f"   1️⃣ OMDB API: {'ENABLED' if omdb_key != 'demo_key' else 'DEMO MODE'}")
        self.logger.info(f"   2️⃣ Scrapy Search: {'ENABLED' if self.scrapy_search else 'DISABLED'}")
        self.logger.info(f"   3️⃣ Web Scraping: {'ENABLED' if self.scrapers else 'DISABLED'}")
        self.logger.info(f"   4️⃣ TMDB API: {'ENABLED' if tmdb_key != 'demo_key_12345' else 'DEMO MODE'}")
        self.logger.info("💾 Free Redis-like cache system: ENABLED")
        
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict]:
        """Search movies with OMDB API priority, proper error logging, and exponential backoff"""
        if not query.strip():
            return []
        
        # Create cache key
        cache_key = f"search:{query.lower()}:{limit}"
        
        # Try to get from cache first (using sync method for simplicity)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.logger.info(f"💾 Cache HIT for '{query}' - returning {len(cached_result)} movies")
            return cached_result
        
        self.logger.info(f"💾🔍 Cache MISS - Searching APIs for: '{query}' (limit: {limit})")
        
        # Priority 1: OMDB API with retry and exponential backoff (highest priority)
        omdb_results = await self._search_omdb_with_exponential_backoff(query, limit)
        if omdb_results:
            normalized = [self._normalize_movie_dict(m) for m in omdb_results]
            self.logger.info(f"✅ OMDB SUCCESS: Got {len(normalized)} movies")
            # Cache OMDB results for 2 hours (premium data)
            self.cache.set(cache_key, normalized[:limit], ttl=7200)
            return normalized[:limit]
            
        # Priority 2: Scrapy Search (comprehensive web scraping)
        if self.scrapy_search:
            self.logger.info("🕷️ Priority 2: Trying Scrapy search...")
            try:
                scrapy_results = await self.scrapy_search.search_movies(query, limit)
                if scrapy_results:
                    self.logger.info(f"✅ SCRAPY SUCCESS: Got {len(scrapy_results)} movies from Scrapy")
                    # Cache Scrapy results for 3 hours (high quality, stable data)
                    self.cache.set(cache_key, scrapy_results[:limit], ttl=10800)
                    return scrapy_results[:limit]
            except Exception as e:
                self.logger.error(f"❌ Scrapy search failed: {e}")
            
        # Priority 3: Legacy web scraping (better than TMDB for detailed data)
        if self.scrapers:
            self.logger.info("🕷️ Priority 3: Trying legacy web scraping...")
            try:
                scraping_results = await self._search_with_scraping(query, limit)
                if scraping_results:
                    self.logger.info(f"✅ LEGACY SCRAPING SUCCESS: Got {len(scraping_results)} movies")
                    # Cache scraping results for 2 hours 
                    self.cache.set(cache_key, scraping_results[:limit], ttl=7200)
                    return scraping_results[:limit]
            except Exception as e:
                self.logger.error(f"❌ Legacy scraping failed: {e}")
                  
        # Priority 4: TMDB API (last resort for live data)
        self.logger.info("🎭 Priority 4: Trying TMDB API (OMDB + Scrapy failed)...")
        try:
            tmdb_results = await self.tmdb_api.search_movies(query, limit)
            self.logger.info(f"🎭 TMDB returned {len(tmdb_results)} results")
            
            # Use ALL TMDB results, not just filtered ones
            if tmdb_results:
                self.logger.info(f"✅ TMDB SUCCESS: Got {len(tmdb_results)} movies")
                # Try to enrich TMDB with scraping as well
                enriched_tmdb = await self._enrich_with_scraping(tmdb_results)
                # Cache TMDB results for shorter time (lower priority)
                self.cache.set(cache_key, enriched_tmdb[:limit], ttl=3600)
                return enriched_tmdb[:limit]
        except Exception as e:
            self.logger.error(f"❌ TMDB search failed: {e}")
            
        # Priority 5: Return empty results instead of demo data
        self.logger.warning(f"❌ All API sources failed for query '{query}' - returning empty results")
        return []
    
    async def _search_omdb_with_exponential_backoff(self, query: str, limit: int) -> List[Dict]:
        """Search OMDB API with exponential backoff retry mechanism"""
        if not self.omdb_api or not self.has_omdb:
            self.logger.warning("🔑 OMDB API not available - skipping")
            return []
        
        max_retries = 3
        base_delay = 1.0  # Start with 1 second
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🎬 OMDB attempt {attempt + 1}/{max_retries} for '{query}'")
                
                # Try OMDB search with timeout
                omdb_results = await asyncio.wait_for(
                    self.omdb_api.search_movies(query, limit),
                    timeout=8.0  # 8-second timeout as specified in requirements
                )
                
                if omdb_results:
                    # Filter out demo/fallback results - only return real API data
                    real_results = [
                        result for result in omdb_results 
                        if result.get('source') not in ['demo', 'demo_omdb', 'fallback']
                    ]
                    
                    if real_results:
                        self.logger.info(f"✅ OMDB SUCCESS on attempt {attempt + 1}: {len(real_results)} real results")
                        return real_results
                    else:
                        self.logger.warning(f"⚠️ OMDB returned only demo data on attempt {attempt + 1}")
                
            except asyncio.TimeoutError:
                self.logger.error(f"⏰ OMDB timeout on attempt {attempt + 1} (8s limit exceeded)")
                
            except Exception as e:
                self.logger.error(f"❌ OMDB error on attempt {attempt + 1}: {e}")
            
            # Apply exponential backoff if not the last attempt
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                self.logger.info(f"⏳ Retrying OMDB in {delay}s...")
                await asyncio.sleep(delay)
        
        self.logger.error(f"❌ OMDB failed after {max_retries} attempts with exponential backoff")
        return []
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Dict]:
        """
        Get movie details by ID with caching
        Tries OMDB first, then Scrapy, then TMDB
        """
        # Create cache key
        cache_key = f"movie_by_id:{movie_id}"
        
        # Try to get from cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.logger.info(f"💾 Cache HIT for movie ID '{movie_id}'")
            return cached_result
        
        self.logger.info(f"💾 Cache MISS - Fetching movie ID '{movie_id}' from APIs")
        
        try:
            # Priority 1: OMDB by IMDB ID (highest quality)
            if movie_id.startswith('tt'):
                self.logger.info("🎬 Trying OMDB for movie details...")
                omdb_result = await self.omdb_api.search_by_imdb_id(movie_id)
                if omdb_result:
                    movie = self._dict_to_movie(omdb_result)
                    if movie:
                        # Enrich with scraping data for comprehensive details
                        enriched_movies = await self._enrich_with_scraping([movie])
                        enriched_movie = enriched_movies[0] if enriched_movies else movie
                        # Cache movie details for 6 hours (stable, high-quality data)
                        self.cache.set(cache_key, enriched_movie, ttl=21600)
                        return enriched_movie
                        
            # Priority 2: Scrapy search for movie details (if OMDB fails)
            if self.scrapy_search and movie_id.startswith('tt'):
                self.logger.info("🕷️ Trying Scrapy for movie details...")
                scrapy_result = await self.scrapy_search.get_movie_by_id(movie_id)
                if scrapy_result:
                    # Cache Scrapy movie details for 4 hours
                    self.cache.set(cache_key, scrapy_result, ttl=14400)
                    return scrapy_result
            
            # Priority 3: Web scraping for movie details
            if self.scrapers and movie_id.startswith('tt'):
                try:
                    # Extract movie title from IMDB for scraping
                    self.logger.info("🕷️ Trying web scraping for movie details...")
                    # For now, skip this complex step and move to TMDB
                except Exception as e:
                    self.logger.warning(f"Web scraping failed for {movie_id}: {e}")
            
            # Priority 4: TMDB fallback (limited data but reliable)
            if movie_id.startswith('tmdb_'):
                tmdb_id = movie_id.replace('tmdb_', '')
                self.logger.info(f"🎭 Trying TMDB for movie details (ID: {tmdb_id})...")
                tmdb_result = await self.tmdb_api.get_movie_details(tmdb_id)
                if tmdb_result:
                    movie = self._dict_to_movie(tmdb_result)
                    if movie:
                        # Cache TMDB movie details for 3 hours
                        self.cache.set(cache_key, movie, ttl=10800)
                        return movie
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching movie {movie_id}: {e}")
        
        return None
    
    async def search_by_title(self, title: str) -> Optional[Dict]:
        """Search for a specific movie by title"""
        try:
            # 1. Try OMDB first
            omdb_result = await self.omdb_api.search_by_title(title)
            if omdb_result:
                movie = self._dict_to_movie(omdb_result)
                if movie:
                    return movie
            
            # 2. Try Scrapy
            if self.scrapy_search:
                scrapy_results = await self.scrapy_search.search_movies(title, 1)
                if scrapy_results:
                    return scrapy_results[0]
                    
            # 3. Try TMDB as fallback
            tmdb_results = await self.tmdb_api.search_movies(title, 1)
            if tmdb_results:
                return tmdb_results[0]
                
        except Exception as e:
            self.logger.error(f"❌ Search by title error: {e}")
            
        return None
    
    async def _search_with_scraping(self, query: str, limit: int) -> List[Dict]:
        """Search using legacy web scraping as a fallback"""
        if not self.scrapers:
            return []
            
        try:
            results = []
            
            # Try IMDB scraping for the query
            if 'imdb' in self.scrapers:
                try:
                    imdb_results = await self._scrape_search('imdb', query, limit)
                    if imdb_results:
                        results.extend(imdb_results)
                        self.logger.info(f"🕷️ IMDB scraping found {len(imdb_results)} results")
                except Exception as e:
                    self.logger.warning(f"IMDB scraping failed: {e}")
            
            return results[:limit]
        except Exception as e:
            self.logger.error(f"Web scraping search failed: {e}")
            return []
    
    async def _scrape_search(self, source: str, query: str, limit: int) -> List[Dict]:
        """Scrape search results from a source"""
        try:
            scraper = self.scrapers.get(source)
            if not scraper:
                return []
                
            # Run scraping in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, scraper.search_movies, query, limit)
            return results or []
            
        except Exception as e:
            self.logger.warning(f"Failed to scrape search from {source}: {e}")
            return []
    
    async def _enrich_with_scraping(self, movies: List[Dict]) -> List[Dict]:
        """Enrich movie data with scraping information"""
        enriched_movies = []
        
        for movie in movies[:3]:  # Limit to avoid timeout
            try:
                enriched_movie = movie.copy()
                title = movie.get('title', '')
                
                # Try to enrich with IMDB scraping
                if 'imdb' in self.scrapers and title:
                    scraped_data = await self._scrape_movie_data('imdb', title)
                    if scraped_data:
                        # Merge scraped data (keep original OMDB/TMDB data priority)
                        enriched_movie.update({
                            k: v for k, v in scraped_data.items() 
                            if k not in enriched_movie or not enriched_movie.get(k)
                        })
                
                enriched_movies.append(enriched_movie)
                
            except Exception as e:
                self.logger.warning(f"Failed to enrich movie '{movie.get('title', 'Unknown')}': {e}")
                enriched_movies.append(movie)  # Use original if enrichment fails
        
        return enriched_movies
    
    async def _scrape_movie_data(self, source: str, title: str) -> Optional[Dict]:
        """Scrape data for a specific movie from a source with timeout and error handling"""
        try:
            scraper = self.scrapers.get(source)
            if not scraper:
                return None
            
            # Set aggressive timeout for scraping
            import asyncio
              # Run scraping with strict timeout (max 2 seconds)
            loop = asyncio.get_event_loop()
            try:
                data = await asyncio.wait_for(
                    loop.run_in_executor(None, scraper.scrape_movie_data, title),
                    timeout=2.0  # Very fast timeout
                )
                return data
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Scraping timeout for {source}:{title}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Scraping failed for {source}:{title} - {e}")
            return None
    
    def _dict_to_movie(self, data: Dict) -> Optional[Dict]:
        """Convert dictionary data to standardized movie dict"""
        try:
            return {
                'id': data.get('id', data.get('imdbID', 'unknown')),
                'title': data.get('title', data.get('Title', 'Unknown Title')),
                'year': data.get('year', data.get('Year', 2000)),
                'plot': data.get('plot', data.get('Plot', 'No plot available.')),
                'rating': data.get('rating', data.get('imdbRating', 5.0)),
                'genre': data.get('genre', data.get('Genre', ['Unknown'])),
                'director': data.get('director', data.get('Director', 'Unknown Director')),
                'cast': data.get('cast', data.get('Actors', ['Unknown Cast'])),
                'poster': data.get('poster', data.get('Poster', '/placeholder.svg')),
                'runtime': data.get('runtime', 120),
                'imdbId': data.get('imdbId', data.get('imdbID')),
                'reviews': [],
                'source': data.get('source', 'unknown')
            }
        except Exception as e:
            self.logger.error(f"❌ Error converting dict to Movie: {e}")
            return None
    
    def _normalize_movie_dict(self, movie: Dict) -> Dict:
        """Ensure all movie dicts use lowercase 'title' and consistent keys"""
        if 'Title' in movie and 'title' not in movie:
            movie['title'] = movie['Title']
        if 'Plot' in movie and 'plot' not in movie:
            movie['plot'] = movie['Plot']
        if 'Director' in movie and 'director' not in movie:
            movie['director'] = movie['Director']
        if 'Poster' in movie and 'poster' not in movie:
            movie['poster'] = movie['Poster']
        if 'imdbID' in movie and 'imdbId' not in movie:
            movie['imdbId'] = movie['imdbID']
        return movie

    async def _get_demo_movies(self, query: str, limit: int) -> List[Dict]:
        """Return demo movies as last resort"""
        demo_data = self._get_fallback_movie_data()
        # Filter by query if provided
        if query:
            filtered = [m for m in demo_data if query.lower() in m['title'].lower()]
            return filtered[:limit] if filtered else demo_data[:limit]
        return demo_data[:limit]
    
    def _get_fallback_movie_data(self) -> List[Dict]:
        """Comprehensive fallback movie data with proper images"""
        return [
            {
                'id': 'tt0111161',
                'title': 'The Shawshank Redemption',
                'year': 1994,
                'plot': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'rating': 9.3,
                'genre': ['Drama'],
                'director': 'Frank Darabont',
                'cast': ['Tim Robbins', 'Morgan Freeman'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg',
                'runtime': 142,
                'imdbId': 'tt0111161',
                'source': 'fallback'
            },
            {
                'id': 'tt1375666',
                'title': 'Inception',
                'year': 2010,
                'plot': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'rating': 8.8,
                'genre': ['Action', 'Sci-Fi', 'Thriller'],
                'director': 'Christopher Nolan',
                'cast': ['Leonardo DiCaprio', 'Marion Cotillard', 'Tom Hardy'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
                'runtime': 148,
                'imdbId': 'tt1375666',
                'source': 'fallback'
            },
            {
                'id': 'tt0468569',
                'title': 'The Dark Knight',
                'year': 2008,
                'plot': 'Batman raises the stakes in his war on crime with the help of Lieutenant Jim Gordon and District Attorney Harvey Dent.',
                'rating': 9.0,
                'genre': ['Action', 'Crime', 'Drama'],
                'director': 'Christopher Nolan',
                'cast': ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart'],
                'poster': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                'runtime': 152,
                'imdbId': 'tt0468569',
                'source': 'fallback'
            }
        ]
