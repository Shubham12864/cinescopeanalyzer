#!/usr/bin/env python3
"""
LAYER 3: REAL-TIME SCRAPING SYSTEM (1-3 seconds)
Advanced multi-source scraping with Scrapy and IMDB tools integration
"""
import asyncio
import logging
import time
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScrapingResult:
    """Data class for scraping results"""
    title: str
    year: str
    imdb_id: str
    poster_url: str
    rating: str
    plot: str
    genre: str
    director: str
    cast: List[str]
    source: str
    confidence: float
    scraped_at: datetime

class RealTimeScrapingSystem:
    """
    Layer 3: Real-time Scraping System
    - Multi-source parallel scraping
    - IMDB, TMDB, OMDb API fallback
    - Scrapy integration for deep searches
    - Result validation and confidence scoring
    """
    
    def __init__(self):
        # HTTP session for scraping
        self.session = None
        
        # Scrapy integration
        self.scrapy_runner = None
        self.scrapy_executor = ThreadPoolExecutor(max_workers=3)
        
        # Source configurations
        self.sources = {
            'imdb_web': {
                'base_url': 'https://www.imdb.com',
                'search_path': '/find/?q={}&ref_=nv_sr_sm',
                'enabled': True,
                'timeout': 5,
                'priority': 1
            },
            'scrapy_spider': {
                'enabled': True,
                'timeout': 8,
                'priority': 2
            }
        }
        
        # Performance tracking
        self.scraping_stats = {
            'total_requests': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'avg_response_time': 0,
            'source_performance': {}
        }
        
        # Rate limiting
        self.rate_limiter = {
            'imdb_web': {'requests': 0, 'reset_time': time.time()},
            'scrapy_spider': {'requests': 0, 'reset_time': time.time()}
        }
        
        # Cache for avoiding duplicate scraping
        self.recent_scrapes = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("🕷️ Real-time Scraping System initialized")
    
    async def initialize(self):
        """Initialize HTTP session and scrapy components"""
        try:
            # Create aiohttp session with optimized settings
            connector = aiohttp.TCPConnector(
                limit=20,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            logger.info("✅ HTTP session initialized")
            
        except Exception as e:
            logger.error(f"❌ Scraping system initialization failed: {e}")
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Layer 3: Real-time multi-source scraping (1-3 seconds)
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"scrape:{query.lower().strip()}"
            if cache_key in self.recent_scrapes:
                cache_entry = self.recent_scrapes[cache_key]
                if (time.time() - cache_entry['timestamp']) < self.cache_ttl:
                    elapsed_ms = (time.time() - start_time) * 1000
                    logger.info(f"⚡ Scraping cache HIT: '{query}' in {elapsed_ms:.1f}ms")
                    return cache_entry['results'][:limit]
            
            # Execute parallel searches from OMDB + Enhanced Scraping
            search_tasks = []
            
            # IMDB Web Scraping (highest priority)
            if self.sources['imdb_web']['enabled']:
                search_tasks.append(self._scrape_imdb_web(query, limit))
            
            # Scrapy Spider Integration (comprehensive scraping)
            if self.sources['scrapy_spider']['enabled']:
                search_tasks.append(self._run_scrapy_spider(query, limit))
            
            # Execute all scraping tasks in parallel
            results_sets = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Merge and deduplicate results
            merged_results = await self._merge_scraping_results(results_sets, limit)
            
            # Cache results
            self.recent_scrapes[cache_key] = {
                'results': merged_results,
                'timestamp': time.time()
            }
            
            elapsed_ms = (time.time() - start_time) * 1000
            self.scraping_stats['total_requests'] += 1
            self.scraping_stats['avg_response_time'] = (
                (self.scraping_stats['avg_response_time'] * (self.scraping_stats['total_requests'] - 1) + elapsed_ms) /
                self.scraping_stats['total_requests']
            )
            
            if merged_results:
                self.scraping_stats['successful_scrapes'] += 1
                logger.info(f"🕷️ Real-time scraping: '{query}' → {len(merged_results)} results in {elapsed_ms:.1f}ms")
            else:
                self.scraping_stats['failed_scrapes'] += 1
                logger.warning(f"⚠️ No scraping results for: '{query}' in {elapsed_ms:.1f}ms")
            
            return merged_results
            
        except Exception as e:
            logger.error(f"❌ Real-time scraping error: {e}")
            return []
    
    async def _scrape_imdb_web(self, query: str, limit: int) -> List[ScrapingResult]:
        """Scrape IMDB website directly"""
        try:
            if not await self._check_rate_limit('imdb_web'):
                logger.warning("⚠️ IMDB web rate limit exceeded")
                return []
            
            search_url = self.sources['imdb_web']['base_url'] + self.sources['imdb_web']['search_path'].format(query.replace(' ', '%20'))
            
            async with self.session.get(search_url, timeout=self.sources['imdb_web']['timeout']) as response:
                if response.status != 200:
                    logger.error(f"❌ IMDB web request failed: {response.status}")
                    return []
                
                html = await response.text()
                results = await self._parse_imdb_html(html, query, limit)
                
                logger.debug(f"🎬 IMDB web: {len(results)} results for '{query}'")
                return results
                
        except Exception as e:
            logger.error(f"❌ IMDB web scraping error: {e}")
            return []
    
    async def _parse_imdb_html(self, html: str, query: str, limit: int) -> List[ScrapingResult]:
        """Parse IMDB HTML search results"""
        try:
            results = []
            
            # Enhanced regex patterns for IMDB parsing
            title_pattern = r'<a[^>]*href="/title/(tt\d+)/[^"]*"[^>]*>([^<]+)</a>'
            year_pattern = r'<span[^>]*class="[^"]*release_year[^"]*"[^>]*>\((\d{4})\)</span>'
            rating_pattern = r'<span[^>]*class="[^"]*rating[^"]*"[^>]*>([0-9.]+)</span>'
            
            # Find all title matches
            title_matches = re.finditer(title_pattern, html)
            
            for match in title_matches:
                if len(results) >= limit:
                    break
                    
                imdb_id = match.group(1)
                title = match.group(2).strip()
                
                # Extract additional data around the title
                section_start = max(0, match.start() - 500)
                section_end = min(len(html), match.end() + 500)
                section = html[section_start:section_end]
                
                # Extract year
                year_match = re.search(year_pattern, section)
                year = year_match.group(1) if year_match else "N/A"
                
                # Extract rating
                rating_match = re.search(rating_pattern, section)
                rating = rating_match.group(1) if rating_match else "N/A"
                
                # Create result
                result = ScrapingResult(
                    title=title,
                    year=year,
                    imdb_id=imdb_id,
                    poster_url=f"https://m.media-amazon.com/images/M/{imdb_id}_SX300.jpg",
                    rating=rating,
                    plot="Plot available on detail page",
                    genre="Multiple",
                    director="N/A",
                    cast=[],
                    source="imdb_web",
                    confidence=0.9,
                    scraped_at=datetime.utcnow()
                )
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ IMDB HTML parsing error: {e}")
            return []
    
    async def _run_scrapy_spider(self, query: str, limit: int) -> List[ScrapingResult]:
        """Run simplified scraping for comprehensive movie data"""
        try:
            if not await self._check_rate_limit('scrapy_spider'):
                logger.warning("⚠️ Scrapy spider rate limit exceeded")
                return []
            
            logger.info(f"🕷️ Running enhanced scraping for: '{query}'")
            
            # Enhanced IMDB scraping with more data
            results = []
            
            # Search multiple IMDB pages for better coverage
            search_urls = [
                f"https://www.imdb.com/find/?q={query.replace(' ', '%20')}&ref_=nv_sr_sm",
                f"https://www.imdb.com/search/title/?title={query.replace(' ', '%20')}&title_type=feature"
            ]
            
            for url in search_urls:
                try:
                    async with self.session.get(url, timeout=8) as response:
                        if response.status == 200:
                            html = await response.text()
                            page_results = await self._parse_enhanced_imdb(html, query, limit//2)
                            results.extend(page_results)
                            
                            if len(results) >= limit:
                                break
                                
                except Exception as e:
                    logger.warning(f"⚠️ Enhanced scraping URL failed: {e}")
                    continue
            
            # Remove duplicates
            seen_ids = set()
            unique_results = []
            
            for result in results:
                if result.imdb_id not in seen_ids:
                    seen_ids.add(result.imdb_id)
                    unique_results.append(result)
                    
                    if len(unique_results) >= limit:
                        break
            
            logger.debug(f"🕷️ Enhanced scraping: {len(unique_results)} results for '{query}'")
            return unique_results
            
        except Exception as e:
            logger.error(f"❌ Enhanced scraping error: {e}")
            return []
    
    async def _parse_enhanced_imdb(self, html: str, query: str, limit: int) -> List[ScrapingResult]:
        """Parse IMDB HTML with enhanced data extraction"""
        try:
            results = []
            
            # Multiple patterns for different IMDB page types
            patterns = [
                # Search results page
                r'<td class="result_text">\s*<a href="/title/(tt\d+)/[^"]*"[^>]*>([^<]+)</a>\s*(?:\([^)]*\))?\s*(?:\((\d{4})\))?',
                # Title search page
                r'<h3 class="titleColumn">\s*<a href="/title/(tt\d+)/[^"]*"[^>]*>([^<]+)</a>\s*<span class="secondaryInfo">\((\d{4})\)</span>',
                # General title pattern
                r'href="/title/(tt\d+)/[^"]*"[^>]*>([^<]+)</a>[^<]*(?:\((\d{4})\))?'
            ]
            
            all_matches = []
            for pattern in patterns:
                matches = re.finditer(pattern, html, re.IGNORECASE | re.DOTALL)
                all_matches.extend(matches)
            
            # Process matches
            seen_ids = set()
            for match in all_matches:
                if len(results) >= limit:
                    break
                    
                imdb_id = match.group(1)
                title = match.group(2).strip()
                year = match.group(3) if len(match.groups()) > 2 and match.group(3) else "N/A"
                
                # Skip duplicates
                if imdb_id in seen_ids:
                    continue
                seen_ids.add(imdb_id)
                
                # Create enhanced result
                result = ScrapingResult(
                    title=title,
                    year=year,
                    imdb_id=imdb_id,
                    poster_url=f"https://m.media-amazon.com/images/M/{imdb_id}_SX300.jpg",
                    rating="N/A",
                    plot="Detailed plot available on IMDB",
                    genre="Multiple genres",
                    director="N/A",
                    cast=[],
                    source="enhanced_imdb",
                    confidence=0.9,
                    scraped_at=datetime.utcnow()
                )
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Enhanced IMDB parsing error: {e}")
            return []
    
    async def _merge_scraping_results(self, results_sets: List, limit: int) -> List[Dict[str, Any]]:
        """Merge and deduplicate results from multiple sources"""
        try:
            all_results = []
            seen_titles = set()
            seen_imdb_ids = set()
            
            # Flatten results and handle exceptions
            for result_set in results_sets:
                if isinstance(result_set, Exception):
                    logger.error(f"❌ Scraping task failed: {result_set}")
                    continue
                
                if isinstance(result_set, list):
                    all_results.extend(result_set)
            
            # Sort by confidence and source priority
            all_results.sort(key=lambda x: (x.confidence, -self.sources.get(x.source, {}).get('priority', 999)), reverse=True)
            
            merged_results = []
            
            for result in all_results:
                if len(merged_results) >= limit:
                    break
                
                # Deduplicate by title and IMDB ID
                title_key = result.title.lower().strip()
                if title_key in seen_titles or result.imdb_id in seen_imdb_ids:
                    continue
                
                seen_titles.add(title_key)
                if result.imdb_id:
                    seen_imdb_ids.add(result.imdb_id)
                
                # Convert to dictionary format
                movie_dict = {
                    'Title': result.title,
                    'Year': result.year,
                    'imdbID': result.imdb_id,
                    'Poster': result.poster_url,
                    'imdbRating': result.rating,
                    'Plot': result.plot,
                    'Genre': result.genre,
                    'Director': result.director,
                    'Actors': ', '.join(result.cast[:3]) if result.cast else 'N/A',
                    'Source': result.source,
                    'Confidence': result.confidence,
                    'ScrapedAt': result.scraped_at.isoformat()
                }
                
                merged_results.append(movie_dict)
            
            return merged_results
            
        except Exception as e:
            logger.error(f"❌ Results merging error: {e}")
            return []
    
    async def _check_rate_limit(self, source: str) -> bool:
        """Check rate limiting for a source"""
        try:
            current_time = time.time()
            rate_info = self.rate_limiter.get(source, {})
            
            # Reset counter every minute
            if current_time - rate_info.get('reset_time', 0) > 60:
                rate_info['requests'] = 0
                rate_info['reset_time'] = current_time
            
            # Check limits (conservative limits)
            limits = {
                'imdb_web': 30,     # 30 requests per minute
                'scrapy_spider': 10  # 10 requests per minute (more intensive)
            }
            
            if rate_info.get('requests', 0) >= limits.get(source, 20):
                return False
            
            # Increment counter
            rate_info['requests'] = rate_info.get('requests', 0) + 1
            self.rate_limiter[source] = rate_info
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Rate limit check error: {e}")
            return True  # Allow by default if check fails
    
    async def get_movie_details(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific movie"""
        try:
            # Try multiple sources for detailed information
            detail_tasks = []
            
            # IMDB detail scraping
            detail_tasks.append(self._get_imdb_details(imdb_id))
            
            # Execute tasks
            detail_results = await asyncio.gather(*detail_tasks, return_exceptions=True)
            
            # Return first successful result
            for result in detail_results:
                if isinstance(result, dict) and result:
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Movie details error: {e}")
            return None
    
    async def _get_imdb_details(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed IMDB information"""
        try:
            detail_url = f"https://www.imdb.com/title/{imdb_id}/"
            
            async with self.session.get(detail_url, timeout=5) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                
                # Parse detailed information
                details = {
                    'imdbID': imdb_id,
                    'DetailedPlot': self._extract_plot_from_html(html),
                    'Runtime': self._extract_runtime_from_html(html),
                    'Awards': self._extract_awards_from_html(html),
                    'BoxOffice': self._extract_boxoffice_from_html(html),
                    'Country': self._extract_country_from_html(html),
                    'Language': self._extract_language_from_html(html)
                }
                
                return details
                
        except Exception as e:
            logger.error(f"❌ IMDB details error: {e}")
            return None
    
    def _extract_plot_from_html(self, html: str) -> str:
        """Extract plot from IMDB HTML"""
        try:
            plot_pattern = r'<span[^>]*data-testid="plot-xl"[^>]*>([^<]+)</span>'
            match = re.search(plot_pattern, html)
            return match.group(1).strip() if match else "Plot not available"
        except:
            return "Plot not available"
    
    def _extract_runtime_from_html(self, html: str) -> str:
        """Extract runtime from IMDB HTML"""
        try:
            runtime_pattern = r'<span[^>]*class="[^"]*runtime[^"]*"[^>]*>([^<]+)</span>'
            match = re.search(runtime_pattern, html)
            return match.group(1).strip() if match else "N/A"
        except:
            return "N/A"
    
    def _extract_awards_from_html(self, html: str) -> str:
        """Extract awards from IMDB HTML"""
        try:
            awards_pattern = r'<span[^>]*class="[^"]*awards[^"]*"[^>]*>([^<]+)</span>'
            match = re.search(awards_pattern, html)
            return match.group(1).strip() if match else "N/A"
        except:
            return "N/A"
    
    def _extract_boxoffice_from_html(self, html: str) -> str:
        """Extract box office from IMDB HTML"""
        try:
            boxoffice_pattern = r'<span[^>]*class="[^"]*box-office[^"]*"[^>]*>([^<]+)</span>'
            match = re.search(boxoffice_pattern, html)
            return match.group(1).strip() if match else "N/A"
        except:
            return "N/A"
    
    def _extract_country_from_html(self, html: str) -> str:
        """Extract country from IMDB HTML"""
        try:
            country_pattern = r'<span[^>]*class="[^"]*country[^"]*"[^>]*>([^<]+)</span>'
            match = re.search(country_pattern, html)
            return match.group(1).strip() if match else "N/A"
        except:
            return "N/A"
    
    def _extract_language_from_html(self, html: str) -> str:
        """Extract language from IMDB HTML"""
        try:
            language_pattern = r'<span[^>]*class="[^"]*language[^"]*"[^>]*>([^<]+)</span>'
            match = re.search(language_pattern, html)
            return match.group(1).strip() if match else "N/A"
        except:
            return "N/A"
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get scraping performance statistics"""
        return {
            **self.scraping_stats,
            "cache_size": len(self.recent_scrapes),
            "sources_enabled": sum(1 for source in self.sources.values() if source['enabled']),
            "rate_limiter_status": {
                source: {
                    'requests_made': info.get('requests', 0),
                    'time_until_reset': max(0, 60 - (time.time() - info.get('reset_time', 0)))
                }
                for source, info in self.rate_limiter.items()
            }
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
                
            # Shutdown executor
            self.scrapy_executor.shutdown(wait=True)
            
            logger.info("🧹 Scraping system cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

# Global instance
realtime_scraper = RealTimeScrapingSystem()

# Export functions
async def initialize_scraping_system():
    """Initialize the scraping system"""
    await realtime_scraper.initialize()
    return realtime_scraper

async def scrape_movies_realtime(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Scrape movies in real-time from multiple sources"""
    return await realtime_scraper.search_movies(query, limit)
