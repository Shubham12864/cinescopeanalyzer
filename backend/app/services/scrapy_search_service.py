import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import subprocess
import tempfile
import os
import multiprocessing
import requests
from bs4 import BeautifulSoup
import re

# Optional Scrapy imports
try:
    from scrapy.crawler import CrawlerProcess, CrawlerRunner
    from scrapy.utils.project import get_project_settings
    from twisted.internet import reactor, defer
    from twisted.internet.defer import inlineCallbacks
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False

try:
    from crochet import setup, wait_for
    CROCHET_AVAILABLE = True
except ImportError:
    CROCHET_AVAILABLE = False

# Setup crochet to run Scrapy in async environment
if SCRAPY_AVAILABLE and CROCHET_AVAILABLE:
    try:
        setup()
        SCRAPY_ASYNC_READY = True
    except Exception:
        SCRAPY_ASYNC_READY = False
else:
    SCRAPY_ASYNC_READY = False

class ScrapySearchService:
    """
    Enhanced Scrapy-based search service for movie data.
    Integrates with API manager as a fallback/supplement to OMDB and TMDB.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=2)
          # Fallback to simple scraping if Scrapy can't be used in async
        self.use_simple_scraping = not SCRAPY_ASYNC_READY
        
        if self.use_simple_scraping:
            self.logger.warning("🕷️ Using simple web scraping (Scrapy/crochet unavailable)")
        else:
            self.logger.info("🕷️ Scrapy service initialized with async support")
    
    async def search_movies(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for movies using Scrapy/web scraping as fallback
        
        Args:
            query: Movie search query
            limit: Maximum number of results
            
        Returns:
            List of movie dictionaries
        """
        if not query.strip():
            return []
        
        self.logger.info(f"🕷️ Scrapy search for: '{query}' (limit: {limit})")
        
        try:
            # Use simple scraping approach for reliability
            results = await self._simple_search_movies(query, limit)
            
            if results:
                self.logger.info(f"✅ Scrapy found {len(results)} movies for '{query}'")
                return results[:limit]
            else:
                self.logger.warning(f"⚠️ Scrapy search returned no results for '{query}'")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Scrapy search failed for '{query}': {e}")
            return []
    
    async def _simple_search_movies(self, query: str, limit: int) -> List[Dict]:
        """
        Simple movie search using requests + BeautifulSoup
        More reliable than full Scrapy for async integration
        """
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self.executor, 
                self._scrape_imdb_search, 
                query, 
                limit
            )
            return results
            
        except Exception as e:
            self.logger.error(f"Simple scraping failed: {e}")
            return []
    
    def _scrape_imdb_search(self, query: str, limit: int) -> List[Dict]:
        """
        Scrape IMDB search results
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of movie data
        """
        movies = []
        
        try:
            # Search IMDB
            search_url = f"https://www.imdb.com/find/?q={query.replace(' ', '+')}&s=tt&ttype=ft"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(search_url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse search results
            results = soup.find_all('td', class_='result_text', limit=limit)
            
            for i, result in enumerate(results):
                if len(movies) >= limit:
                    break
                
                try:
                    movie_data = self._extract_movie_from_result(result, i)
                    if movie_data:
                        movies.append(movie_data)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to extract movie {i}: {e}")
                    continue
            
            self.logger.info(f"🕷️ IMDB scraping extracted {len(movies)} movies")
            
        except requests.RequestException as e:
            self.logger.error(f"IMDB request failed: {e}")
        except Exception as e:
            self.logger.error(f"IMDB scraping failed: {e}")
        
        return movies
    
    def _extract_movie_from_result(self, result_elem, index: int) -> Optional[Dict]:
        """
        Extract movie data from IMDB search result element
        
        Args:
            result_elem: BeautifulSoup element
            index: Result index
            
        Returns:
            Movie data dictionary or None
        """
        try:
            # Get movie link and title
            link = result_elem.find('a')
            if not link:
                return None
            
            title = link.text.strip()
            imdb_url = "https://www.imdb.com" + link.get('href', '')
            
            # Extract IMDB ID from URL
            imdb_id_match = re.search(r'/title/(tt\d+)/', imdb_url)
            imdb_id = imdb_id_match.group(1) if imdb_id_match else f"scrapy_{index}"
            
            # Extract year
            year_text = result_elem.get_text()
            year_match = re.search(r'\((\d{4})\)', year_text)
            year = int(year_match.group(1)) if year_match else 2023
            
            # Get additional details by scraping the movie page
            movie_details = self._get_movie_details(imdb_url, timeout=3)
            
            # Build movie data
            movie_data = {
                'id': imdb_id,
                'title': title,
                'year': year,
                'plot': movie_details.get('plot', f'Movie about {title}'),
                'rating': movie_details.get('rating', 7.0),
                'genre': movie_details.get('genres', ['Drama']),
                'director': movie_details.get('director', 'Unknown Director'),
                'cast': movie_details.get('cast', []),
                'poster': movie_details.get('poster', '/placeholder.svg?height=450&width=300'),
                'runtime': movie_details.get('runtime', 120),
                'imdbId': imdb_id,
                'source': 'scrapy_imdb',
                'url': imdb_url
            }
            
            return movie_data
            
        except Exception as e:
            self.logger.warning(f"Failed to extract movie data: {e}")
            return None
    
    def _get_movie_details(self, imdb_url: str, timeout: int = 3) -> Dict:
        """
        Get detailed movie information from IMDB movie page
        
        Args:
            imdb_url: IMDB movie URL
            timeout: Request timeout
            
        Returns:
            Dictionary with movie details
        """
        details = {
            'plot': '',
            'rating': 7.0,
            'genres': ['Drama'],
            'director': 'Unknown',
            'cast': [],
            'poster': '/placeholder.svg?height=450&width=300',
            'runtime': 120
        }
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(imdb_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract plot
            plot_elem = soup.find('span', {'data-testid': 'plot-xl'}) or soup.find('span', {'data-testid': 'plot-l'})
            if plot_elem:
                details['plot'] = plot_elem.get_text(strip=True)
            
            # Extract rating
            rating_elem = soup.find('span', class_='sc-7ab21ed2-1')
            if rating_elem:
                try:
                    details['rating'] = float(rating_elem.get_text(strip=True))
                except (ValueError, AttributeError) as e:
                    self.logger.warning(f"Failed to parse rating: {e}")
                    pass
            
            # Extract genres
            genre_elements = soup.find_all('span', class_='ipc-chip__text')
            if genre_elements:
                genres = [elem.get_text(strip=True) for elem in genre_elements[:3]]
                if genres:
                    details['genres'] = genres
            
            # Extract director
            director_elem = soup.find('a', {'class': 'ipc-metadata-list-item__list-content-item'})
            if director_elem:
                details['director'] = director_elem.get_text(strip=True)
            
            # Extract cast
            cast_elements = soup.find_all('a', {'data-testid': 'title-cast-item__actor'})
            if cast_elements:
                details['cast'] = [elem.get_text(strip=True) for elem in cast_elements[:5]]
            
            # Extract poster
            poster_elem = soup.find('img', class_='ipc-image')
            if poster_elem and poster_elem.get('src'):
                details['poster'] = poster_elem.get('src')
            
            # Extract runtime
            runtime_elem = soup.find('time')
            if runtime_elem:
                runtime_text = runtime_elem.get_text()
                runtime_match = re.search(r'(\d+)', runtime_text)
                if runtime_match:
                    details['runtime'] = int(runtime_match.group(1))
                    
        except Exception as e:
            self.logger.warning(f"Failed to get movie details from {imdb_url}: {e}")
        
        return details
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Dict]:
        """
        Get detailed movie information by IMDB ID
        
        Args:
            movie_id: IMDB ID (tt1234567)
            
        Returns:
            Movie data dictionary or None
        """
        try:
            if not movie_id.startswith('tt'):
                return None
            
            imdb_url = f"https://www.imdb.com/title/{movie_id}/"
            
            # Run in executor
            loop = asyncio.get_event_loop()
            movie_details = await loop.run_in_executor(
                self.executor,
                self._get_movie_details,
                imdb_url,
                5  # longer timeout for individual movie
            )
            
            if movie_details.get('plot'):
                # Build full movie data
                movie_data = {
                    'id': movie_id,
                    'title': 'Unknown Title',  # Would need to extract from page
                    'year': 2023,
                    'plot': movie_details['plot'],
                    'rating': movie_details['rating'],
                    'genre': movie_details['genres'],
                    'director': movie_details['director'],
                    'cast': movie_details['cast'],
                    'poster': movie_details['poster'],
                    'runtime': movie_details['runtime'],
                    'imdbId': movie_id,
                    'source': 'scrapy_imdb_detail'
                }
                
                return movie_data
            
        except Exception as e:
            self.logger.error(f"Failed to get movie by ID {movie_id}: {e}")
        
        return None
    
    def __del__(self):
        """Cleanup executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
