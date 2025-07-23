import asyncio
import aiohttp
import logging
import random
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import json

class RobustScrapingService:
    """
    Robust scraping service that works without Chrome/Selenium dependencies
    Uses aiohttp and BeautifulSoup for reliable web scraping
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = None
        
        # Rotate user agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Base URLs for different sources
        self.sources = {
            'imdb': 'https://www.imdb.com',
            'tmdb': 'https://www.themoviedb.org',
            'omdb': 'http://www.omdbapi.com'
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with proper configuration"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
        return self.session
    
    async def safe_request(self, url: str, retries: int = 2) -> Optional[BeautifulSoup]:
        """Make a safe HTTP request with retries and error handling"""
        session = await self.get_session()
        
        for attempt in range(retries + 1):
            try:
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    await asyncio.sleep(random.uniform(1, 3))
                
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return BeautifulSoup(content, 'html.parser')
                    elif response.status == 429:  # Rate limited
                        self.logger.warning(f"Rate limited on {url}, waiting...")
                        await asyncio.sleep(random.uniform(5, 10))
                        continue
                    else:
                        self.logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            except Exception as e:
                self.logger.warning(f"Request failed on attempt {attempt + 1} for {url}: {e}")
        
        return None
    
    async def search_movies_imdb(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search movies on IMDb using their find endpoint"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"{self.sources['imdb']}/find/?q={encoded_query}&s=tt&ttype=ft"
            
            soup = await self.safe_request(search_url)
            if not soup:
                return []
            
            movies = []
            
            # Try multiple selectors for IMDb search results
            selectors = [
                'td.result_text a[href*="/title/tt"]',
                '.ipc-metadata-list-summary-item__t a[href*="/title/"]',
                '.titleColumn a[href*="/title/"]',
                'a[href*="/title/tt"]'
            ]
            
            for selector in selectors:
                results = soup.select(selector)
                if results:
                    break
            
            if not results:
                self.logger.warning(f"No IMDb results found for: {query}")
                return []
            
            for result in results[:limit]:
                try:
                    href = result.get('href', '')
                    if '/title/tt' not in href:
                        continue
                    
                    title = result.get_text(strip=True)
                    movie_url = urljoin(self.sources['imdb'], href.split('?')[0])
                    imdb_id = re.search(r'/title/(tt\d+)', href)
                    
                    if imdb_id:
                        movie_data = await self.get_movie_details_imdb(movie_url, imdb_id.group(1))
                        if movie_data:
                            movies.append(movie_data)
                            
                except Exception as e:
                    self.logger.warning(f"Error processing IMDb result: {e}")
                    continue
            
            self.logger.info(f"Found {len(movies)} movies on IMDb for: {query}")
            return movies
            
        except Exception as e:
            self.logger.error(f"IMDb search failed for {query}: {e}")
            return []
    
    async def get_movie_details_imdb(self, movie_url: str, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed movie information from IMDb"""
        try:
            soup = await self.safe_request(movie_url)
            if not soup:
                return None
            
            # Extract movie details using multiple selectors
            movie_data = {
                'id': imdb_id,
                'imdbId': imdb_id,
                'source': 'imdb_scraping',
                'url': movie_url
            }
            
            # Title
            title_selectors = [
                'h1[data-testid="hero-title-block__title"]',
                'h1.titleType',
                '.title_wrapper h1',
                'h1'
            ]
            title = self.extract_text_by_selectors(soup, title_selectors)
            movie_data['title'] = re.sub(r'\s*\(\d{4}\).*$', '', title) if title else 'Unknown Title'
            
            # Year
            year_selectors = [
                '[data-testid="hero-title-block__metadata"] a',
                '.subtext a[href*="year"]',
                '.titleBar .nobr a'
            ]
            year_text = self.extract_text_by_selectors(soup, year_selectors)
            year_match = re.search(r'(\d{4})', year_text) if year_text else None
            movie_data['year'] = int(year_match.group(1)) if year_match else 2000
            
            # Rating
            rating_selectors = [
                '[data-testid="hero-rating-bar__aggregate-rating__score"] span',
                '.ratingValue strong span',
                '.aggregateRatingButton .ratingValue strong'
            ]
            rating_text = self.extract_text_by_selectors(soup, rating_selectors)
            rating_match = re.search(r'(\d+\.?\d*)', rating_text) if rating_text else None
            movie_data['rating'] = float(rating_match.group(1)) if rating_match else 5.0
            
            # Plot
            plot_selectors = [
                '[data-testid="plot-xl"]',
                '[data-testid="plot"]',
                '.plot_summary .summary_text',
                '.summary_text'
            ]
            plot = self.extract_text_by_selectors(soup, plot_selectors)
            movie_data['plot'] = plot if plot else 'No plot available.'
            
            # Genre
            genre_selectors = [
                '[data-testid="genres"] .chip',
                '.see-more.inline.canwrap a',
                '.subtext a[href*="genres"]'
            ]
            genres = []
            for selector in genre_selectors:
                genre_elems = soup.select(selector)
                for elem in genre_elems:
                    genre = elem.get_text(strip=True)
                    if genre and genre not in genres:
                        genres.append(genre)
            movie_data['genre'] = genres if genres else ['Unknown']
            
            # Director
            director_selectors = [
                '[data-testid="title-pc-principal-credit"] a',
                '.credit_summary_item:contains("Director") a',
                '.plot_summary .credit_summary_item a'
            ]
            director = self.extract_text_by_selectors(soup, director_selectors)
            movie_data['director'] = director if director else 'Unknown Director'
            
            # Cast
            cast_selectors = [
                '[data-testid="title-cast"] .cast-item a',
                '.cast_list .primary_photo + td a',
                '.cast .actor a'
            ]
            cast = []
            for selector in cast_selectors:
                cast_elems = soup.select(selector)
                for elem in cast_elems[:5]:  # Limit to top 5
                    actor = elem.get_text(strip=True)
                    if actor and actor not in cast:
                        cast.append(actor)
            movie_data['cast'] = cast if cast else ['Unknown Cast']
            
            # Runtime
            runtime_selectors = [
                '[data-testid="title-techspec_runtime"] .cli-title',
                '.subtext time',
                '.runtime'
            ]
            runtime_text = self.extract_text_by_selectors(soup, runtime_selectors)
            runtime_match = re.search(r'(\d+)', runtime_text) if runtime_text else None
            movie_data['runtime'] = int(runtime_match.group(1)) if runtime_match else 120
            
            # Poster - try to find poster image
            poster_selectors = [
                '.ipc-image[data-testid="hero-media__poster"] img',
                '.poster img',
                '.primary_photo img'
            ]
            poster_elem = None
            for selector in poster_selectors:
                poster_elem = soup.select_one(selector)
                if poster_elem:
                    break
            
            if poster_elem:
                poster_url = poster_elem.get('src') or poster_elem.get('data-src')
                movie_data['poster'] = poster_url if poster_url else ''
            else:
                movie_data['poster'] = ''
            
            return movie_data
            
        except Exception as e:
            self.logger.error(f"Error getting IMDb details for {imdb_id}: {e}")
            return None
    
    def extract_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple CSS selectors as fallbacks"""
        for selector in selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue
        return None
    
    async def search_movies_multiple_sources(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search movies across multiple sources and combine results"""
        all_movies = []
        
        # Search IMDb
        try:
            imdb_movies = await self.search_movies_imdb(query, limit)
            all_movies.extend(imdb_movies)
            self.logger.info(f"IMDb contributed {len(imdb_movies)} movies")
        except Exception as e:
            self.logger.warning(f"IMDb search failed: {e}")
        
        # Remove duplicates based on title and year
        unique_movies = []
        seen = set()
        
        for movie in all_movies:
            key = (movie.get('title', '').lower(), movie.get('year', 0))
            if key not in seen:
                seen.add(key)
                unique_movies.append(movie)
        
        self.logger.info(f"Total unique movies found: {len(unique_movies)}")
        return unique_movies[:limit]
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Get movie details by IMDb ID"""
        if movie_id.startswith('tt'):
            movie_url = f"{self.sources['imdb']}/title/{movie_id}/"
            return await self.get_movie_details_imdb(movie_url, movie_id)
        return None
    
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

# Global instance
robust_scraping_service = RobustScrapingService()