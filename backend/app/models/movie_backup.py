from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import asyncio
import logging

# Import the required classes
from ..core.api_manager import APIManager
from ..scraper.imdb_scraper import ImdbScraper
from ..scraper.rotten_tomatoes_scraper import RottenTomatoesScraper
from ..scraper.metacritic_scraper import MetacriticScraper

class Review(BaseModel):
    id: str
    author: str
    content: str
    rating: float
    sentiment: str
    date: str

class Movie(BaseModel):
    id: str
    title: str
    year: int
    poster: Optional[str] = None
    rating: float
    genre: List[str]
    plot: str
    director: Optional[str] = None
    cast: List[str] = []
    reviews: List[Review] = []
    imdbId: Optional[str] = None
    runtime: Optional[int] = None

class AnalyticsData(BaseModel):
    totalMovies: int
    totalReviews: int
    averageRating: float
    topGenres: List[Dict[str, int]]
    ratingDistribution: Dict[str, int]
    sentimentAnalysis: Dict[str, int]
    reviewTrends: List[Dict[str, Any]]

class MovieDataCollector:
    """Simplified collector for demo purposes"""
    
    def __init__(self):
        pass
        
    async def collect_comprehensive_data(self, title: str, sources: List[str]) -> Dict:
        """Collect basic data - simplified for demo"""
        return {
            'title': title,
            'year': 2024,
            'plot': f'Demo plot for {title}',
            'rating': 7.5,
            'genre': ['Drama'],
            'director': 'Demo Director',
            'cast': ['Demo Actor 1', 'Demo Actor 2'],
            'poster': '/placeholder.svg',
            'reviews': [],
            'source': 'demo'
        }

class Review(BaseModel):
    id: str
    author: str
    content: str
    rating: float
    sentiment: str = "neutral"
    date: str
    source: Optional[str] = None
    helpfulVotes: Optional[int] = 0

class Movie(BaseModel):
    id: str
    title: str
    year: int
    poster: str = ""
    rating: float = 0.0
    genre: List[str] = []
    plot: str = ""
    reviews: List[Review] = []
    imdbId: Optional[str] = None
    tmdbId: Optional[str] = None
    runtime: Optional[int] = None
    director: Optional[str] = None
    cast: List[str] = []
    country: Optional[str] = None
    language: Optional[str] = None

class AnalyticsData(BaseModel):
    totalMovies: int = 0
    totalReviews: int = 0
    averageRating: float = 0.0
    sentimentDistribution: Dict[str, int] = {"positive": 0, "negative": 0, "neutral": 0}
    ratingDistribution: List[int] = [0] * 10
    genrePopularity: List[Dict[str, int]] = []
    reviewTimeline: List[Dict[str, str]] = []
    topRatedMovies: List[Movie] = []
    recentlyAnalyzed: List[Movie] = []

# Legacy Movie class for backward compatibility
class LegacyMovie:
    def __init__(self, title: str):
        self.title = title
        self.year = None
        self.genre = []
        self.director = None
        self.cast = []
        self.plot = None
        self.duration = None
        
        # Ratings from different sources
        self.imdb_rating = None
        self.rotten_tomatoes_rating = None
        self.metacritic_rating = None
        
        # Reviews
        self.reviews = []
        self.review_count = 0
        
        # Analysis results
        self.sentiment_analysis = None
        self.rating_analysis = None
        
        # Metadata
        self.scraped_at = datetime.now()
        self.sources_used = []
        
        # API data fields
        self.tmdb_id = None
        self.imdb_id = None
        self.tmdb_rating = None
        self.tmdb_vote_count = None
        self.omdb_imdb_rating = None
        self.omdb_rotten_tomatoes = None
        self.omdb_metacritic = None
        
        # Enhanced data
        self.poster_url = None
        self.backdrop_url = None
        self.production_companies = []
        self.keywords = []
        self.similar_movies = []
    
    def add_review(self, review: Dict[str, str]):
        """Add a review to the movie"""
        self.reviews.append(review)
        self.review_count = len(self.reviews)
    
    def set_rating(self, source: str, rating: float, max_rating: float = 10.0):
        """Set rating from a specific source"""
        normalized_rating = (rating / max_rating) * 10.0 if max_rating != 10.0 else rating
        
        if source.lower() == 'imdb':
            self.imdb_rating = normalized_rating
        elif source.lower() == 'rotten_tomatoes':
            self.rotten_tomatoes_rating = normalized_rating
        elif source.lower() == 'metacritic':
            self.metacritic_rating = normalized_rating
    
    def get_all_ratings(self) -> Dict[str, float]:
        """Get all available ratings"""
        ratings = {}
        if self.imdb_rating:
            ratings['IMDb'] = self.imdb_rating
        if self.rotten_tomatoes_rating:
            ratings['Rotten Tomatoes'] = self.rotten_tomatoes_rating
        if self.metacritic_rating:
            ratings['Metacritic'] = self.metacritic_rating
        return ratings
    
    def to_dict(self) -> Dict:
        """Convert movie object to dictionary"""
        return {
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            'director': self.director,
            'cast': self.cast,
            'plot': self.plot,
            'duration': self.duration,
            'ratings': self.get_all_ratings(),
            'reviews': self.reviews,
            'review_count': self.review_count,
            'sentiment_analysis': self.sentiment_analysis,
            'rating_analysis': self.rating_analysis,
            'scraped_at': self.scraped_at.isoformat(),
            'sources_used': self.sources_used
        }

class HybridDataCollector:
    """Combines API data with scraped reviews for comprehensive analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_manager = APIManager()
        self.scrapers = {
            'imdb': ImdbScraper(),
            'rt': RottenTomatoesScraper(),
            'metacritic': MetacriticScraper()
        }
        
    async def collect_comprehensive_data(self, title: str, sources: List[str]) -> Dict:
        """Collect data from APIs (fast) and scrapers (reviews)"""
        # 1. Get primary data from APIs (fast, reliable)
        api_data = await self.api_manager.get_comprehensive_movie_data(title)
        
        # 2. Get reviews from scrapers (targeted scraping)
        review_tasks = []
        for source in sources:
            if source.lower() in self.scrapers:
                task = self._scrape_reviews_only(source, title)
                review_tasks.append(task)
        
        scraped_reviews = await asyncio.gather(*review_tasks, return_exceptions=True)
        
        # 3. Combine and return
        return self._merge_api_and_scraped_data(api_data, scraped_reviews)
    
    async def _scrape_reviews_only(self, source: str, title: str) -> Dict:
        """Scrape reviews only from specified source"""
        try:
            scraper = self.scrapers.get(source.lower())
            if not scraper:
                return {'reviews': [], 'source': source}
            
            # Only get reviews, not full data
            data = scraper.scrape_movie_data(title)
            return {
                'reviews': data.get('reviews', [])[:10],  # Limit reviews
                'source': source
            }
        except Exception as e:
            self.logger.error(f"Error scraping {source}: {str(e)}")
            return {'reviews': [], 'source': source}

    async def _merge_api_and_scraped_data(self, api_data: Dict, scraped_reviews: List) -> Dict:
        """Merge API data with scraped reviews"""
        merged = api_data.copy()
        
        # Combine all reviews
        all_reviews = api_data.get('reviews', [])
        
        for scraped_data in scraped_reviews:
            if isinstance(scraped_data, dict) and 'reviews' in scraped_data:
                all_reviews.extend(scraped_data['reviews'])
        
        merged['reviews'] = all_reviews
        merged['total_sources'] = len([d for d in scraped_reviews if isinstance(d, dict)])
        
        return merged