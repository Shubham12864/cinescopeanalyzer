from typing import List, Optional, Dict
import asyncio
import random
import logging
from datetime import datetime

from ..models.movie import Movie, Review, AnalyticsData, SentimentData, RatingDistributionData, MovieSummary
from ..core.api_manager import APIManager
from ..core.azure_database import get_movies_collection, get_cache_collection
from .comprehensive_movie_service_working import ComprehensiveMovieService
from ..scraper.enhanced_movie_scraper import EnhancedMovieDescriptionScraper

class MovieService:
    def __init__(self):
        self.api_manager = APIManager()
        self.comprehensive_service = ComprehensiveMovieService()
        self.description_scraper = EnhancedMovieDescriptionScraper()
        self.logger = logging.getLogger(__name__)
        # Database collections (will be initialized when needed)
        self.movies_collection = None
        self.cache_collection = None
        self.movies_db = []
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo movie data"""
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
            Movie(
                id="2",
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
            ),
            Movie(
                id="3",
                title="The Dark Knight",
                year=2008,
                poster="https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
                rating=9.0,
                genre=["Action", "Crime", "Drama"],
                plot="When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                director="Christopher Nolan",
                cast=["Christian Bale", "Heath Ledger"],
                reviews=[
                    Review(
                        id="r3",
                        author="ComicFan",
                        content="Heath Ledger's Joker is unforgettable. A perfect superhero film.",
                        rating=9.5,
                        sentiment="positive",
                        date="2024-01-08"
                    )
                ]
            ),
            Movie(
                id="4",
                title="Pulp Fiction",
                year=1994,
                poster="https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
                rating=8.9,
                genre=["Crime", "Drama"],
                plot="The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                director="Quentin Tarantino",
                cast=["John Travolta", "Uma Thurman", "Samuel L. Jackson"],
                reviews=[
                    Review(
                        id="r4",
                        author="CinemaLover",
                        content="Tarantino's masterpiece with incredible dialogue and storytelling.",
                        rating=9.0,
                        sentiment="positive",
                        date="2024-01-05"
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
            filtered_movies.sort(key=lambda x: x.title, reverse=reverse)
        elif sort_by == "reviews":
            filtered_movies.sort(key=lambda x: len(x.reviews), reverse=reverse)
        
        # Apply pagination
        return filtered_movies[offset:offset + limit]
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Movie]:
        """Get a specific movie by ID"""
        self.logger.info(f"🔍 Looking for movie with ID: {movie_id}")
        self.logger.info(f"📚 Local movies_db has {len(self.movies_db)} movies")
        
        # Check the local movies_db list
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
                    movie = Movie(
                        id=movie_data.get('id', movie_id),
                        title=movie_data.get('title', 'Unknown'),
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
                    
                    # Add to local database for future requests
                    self.movies_db.append(movie)
                    self.logger.info(f"✅ Fetched and cached movie: {movie.title}")
                    return movie
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch movie from OMDB: {e}")
        
        self.logger.warning(f"❌ Movie {movie_id} not found anywhere")
        return None
    
    async def search_movies(self, query: str, limit: int = 10) -> List[Movie]:
        """Search movies by title, plot, or genre"""
        self.logger.info(f"🔍 Searching for: {query}")
        
        # Search in local database first
        results = []
        query_lower = query.lower()
        
        for movie in self.movies_db:
            if (query_lower in movie.title.lower() or 
                query_lower in movie.plot.lower() or 
                any(query_lower in genre.lower() for genre in movie.genre)):
                results.append(movie)
        
        # If we have enough results from local DB, return them
        if len(results) >= limit:
            return results[:limit]
        
        # Otherwise, try to get more from APIs
        try:
            api_results = await self.api_manager.search_movies(query, limit - len(results))
            
            for movie_data in api_results:
                if len(results) >= limit:
                    break
                    
                movie = Movie(
                    id=movie_data.get('id', f'search-{len(results)}'),
                    title=movie_data.get('title', 'Unknown'),
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
                
                # Don't add duplicates
                if not any(m.id == movie.id for m in results):
                    results.append(movie)
                    
        except Exception as e:
            self.logger.warning(f"Failed to search via APIs: {e}")
        
        return results[:limit]
    
    async def get_movie_suggestions(self, limit: int = 12) -> List[Movie]:
        """Get dynamic movie suggestions"""
        self.logger.info(f"🎬 Getting {limit} dynamic suggestions...")
        
        # Create a more dynamic seed that changes every minute
        now = datetime.now()
        minute_seed = now.hour * 60 + now.minute + (now.second // 10)
        random.seed(minute_seed)
        
        # Use existing movies and shuffle them
        suggestions = self.movies_db.copy()
        random.shuffle(suggestions)
        
        return suggestions[:limit]
    
    async def get_popular_movies(self, limit: int = 12) -> List[Movie]:
        """Get popular movies"""
        # Sort by rating and return top movies
        popular = sorted(self.movies_db, key=lambda x: x.rating, reverse=True)
        return popular[:limit]
    
    async def get_recent_movies(self, limit: int = 12) -> List[Movie]:
        """Get recent movies"""
        # Sort by year and return most recent
        recent = sorted(self.movies_db, key=lambda x: x.year, reverse=True)
        return recent[:limit]
    
    async def get_top_rated_movies(self, limit: int = 12) -> List[Movie]:
        """Get top rated movies"""
        # Sort by rating
        top_rated = sorted(self.movies_db, key=lambda x: x.rating, reverse=True)
        return top_rated[:limit]
    
    async def _update_movie_in_db(self, movie: Movie):
        """Update movie in the local database"""
        try:
            # Update the local movies_db list
            for i, local_movie in enumerate(self.movies_db):
                if local_movie.id == movie.id:
                    self.movies_db[i] = movie
                    self.logger.info(f"✅ Updated movie in local database: {movie.title}")
                    return True
            
            # If not found in local list, add it
            self.movies_db.append(movie)
            self.logger.info(f"✅ Added new movie to local database: {movie.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update movie in database: {e}")
            return False
