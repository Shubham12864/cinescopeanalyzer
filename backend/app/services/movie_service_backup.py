from typing import List, Optional
import asyncio
from datetime import datetime

from ..models.movie import Movie, Review, AnalyticsData
from ..core.api_manager import APIManager

class MovieService:
    def __init__(self):
        self.movies_db = []  # In-memory storage for demo
        self.api_manager = APIManager()  # Use comprehensive API manager
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo movie data"""
        # Initialize with fallback demo data immediately
        self._init_original_demo_data()
        # Optionally load from API manager later
    
    async def _load_initial_movies(self):
        """Load initial movies from API manager"""
        try:
            # Get some popular movies for initial display
            popular_queries = ["the dark knight", "inception", "fight club", "shawshank redemption"]
            for query in popular_queries:
                movie_dicts = await self.api_manager.search_movies(query, 1)
                if movie_dicts:
                    # Convert dict results to Movie objects
                    for movie_data in movie_dicts:
                        movie = Movie(
                            id=movie_data.get('id', 'unknown'),
                            title=movie_data.get('title', 'Unknown Title'),
                            year=movie_data.get('year', 2000),
                            poster=movie_data.get('poster', '/placeholder.svg'),
                            rating=movie_data.get('rating', 5.0),
                            genre=movie_data.get('genre', ['Unknown']),
                            plot=movie_data.get('plot', 'No plot available.'),
                            director=movie_data.get('director', 'Unknown Director'),
                            cast=movie_data.get('cast', ['Unknown Cast']),
                            reviews=[],
                            imdbId=movie_data.get('imdbId'),
                            runtime=movie_data.get('runtime', 120)
                        )
                        # Check if movie already exists
                        if not any(m.id == movie.id for m in self.movies_db):
                            self.movies_db.append(movie)
        except Exception as e:
            print(f"Error loading initial movies: {e}")
            # Fallback to original demo data
            self._init_original_demo_data()
    
    def _init_original_demo_data(self):
        """Original demo data as fallback"""
        demo_movies = [
            Movie(
                id="1",
                title="The Shawshank Redemption",
                year=1994,
                poster="https://via.placeholder.com/300x450?text=Shawshank",
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
                poster="https://via.placeholder.com/300x450?text=Godfather",
                rating=9.2,
                genre=["Crime", "Drama"],
                plot="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                director="Francis Ford Coppola",
                cast=["Marlon Brando", "Al Pacino"],                reviews=[
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
            filtered_movies = [m for m in filtered_movies if m.year == year]        # Sort movies
        reverse = sort_order == "desc"
        if sort_by == "rating":
            filtered_movies.sort(key=lambda x: x.rating, reverse=reverse)
        elif sort_by == "year":
            filtered_movies.sort(key=lambda x: x.year, reverse=reverse)
        elif sort_by == "title":
            filtered_movies.sort(key=lambda x: x.title, reverse=reverse)
          # Apply pagination
        return filtered_movies[offset:offset + limit]
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Movie]:
        """Search movies by title, plot, or genre - now with TMDB integration"""
        try:
            # First, try to get movies from API manager (OMDB -> TMDB -> Scraping)
            api_results = await self.api_manager.search_movies(query, limit)
            api_movies = []
            
            # Convert API results (already Movie objects)
            for movie in api_results:
                api_movies.append(movie)
            
            # Also search in local database
            query_lower = query.lower()
            local_results = []
            
            for movie in self.movies_db:
                if (query_lower in movie.title.lower() or
                    query_lower in movie.plot.lower() or
                    any(query_lower in genre.lower() for genre in movie.genre)):
                    local_results.append(movie)
            
            # Combine results, prioritizing TMDB results
            combined_results = []
            seen_ids = set()
              # Add API results first
            for movie in api_movies:
                if movie.id not in seen_ids:
                    combined_results.append(movie)
                    seen_ids.add(movie.id)
            
            # Add local results that aren't duplicates
            for movie in local_results:
                if movie.id not in seen_ids:
                    combined_results.append(movie)
                    seen_ids.add(movie.id)
            
            return combined_results[:limit]
            
        except Exception as e:
            print(f"Search error: {e}")
            # Fallback to local search only
            query_lower = query.lower()
            results = []
            
            for movie in self.movies_db:
                if (query_lower in movie.title.lower() or
                    query_lower in movie.plot.lower() or
                    any(query_lower in genre.lower() for genre in movie.genre)):
                    results.append(movie)
            
            return results[:limit]
    
    async def get_movie_by_id(self, movie_id: str) -> Optional[Movie]:
        """Get a specific movie by ID"""
        for movie in self.movies_db:
            if movie.id == movie_id:
                return movie
        return None
    
    async def get_movie_analysis(self, movie_id: str) -> Optional[AnalyticsData]:
        """Get analysis data for a specific movie"""
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return None
        
        # Generate analytics data
        return AnalyticsData(
            totalMovies=1,
            totalReviews=len(movie.reviews),
            averageRating=movie.rating,
            sentimentDistribution={
                "positive": len([r for r in movie.reviews if r.sentiment == "positive"]),
                "negative": len([r for r in movie.reviews if r.sentiment == "negative"]),
                "neutral": len([r for r in movie.reviews if r.sentiment == "neutral"])
            },
            ratingDistribution=[1, 0, 0, 1, 2, 3, 5, 10, 15, 20],
            genrePopularity=[{"genre": g, "count": 1} for g in movie.genre],
            reviewTimeline=[{"date": "2024-01-15", "count": len(movie.reviews)}],
            topRatedMovies=[movie],
            recentlyAnalyzed=[movie]
        )
    
    async def analyze_movie(self, movie_id: str) -> str:
        """Trigger analysis for a specific movie"""
        # Mock implementation - would trigger actual analysis in real app
        return f"analysis_task_{movie_id}_{datetime.now().timestamp()}"
    
    async def get_analytics(self) -> AnalyticsData:
        """Get overall analytics data"""
        all_reviews = []
        for movie in self.movies_db:
            all_reviews.extend(movie.reviews)
        
        return AnalyticsData(
            totalMovies=len(self.movies_db),
            totalReviews=len(all_reviews),
            averageRating=sum(m.rating for m in self.movies_db) / len(self.movies_db) if self.movies_db else 0,
            sentimentDistribution={
                "positive": len([r for r in all_reviews if r.sentiment == "positive"]),
                "negative": len([r for r in all_reviews if r.sentiment == "negative"]),
                "neutral": len([r for r in all_reviews if r.sentiment == "neutral"])
            },
            ratingDistribution=[2, 1, 0, 1, 3, 5, 8, 12, 15, 25],
            genrePopularity=[
                {"genre": "Drama", "count": 2},
                {"genre": "Crime", "count": 2},
                {"genre": "Action", "count": 1}
            ],
            reviewTimeline=[
                {"date": "2024-01-15", "count": 1},
                {"date": "2024-01-20", "count": 1},
                {"date": "2024-01-25", "count": 1}
            ],
            topRatedMovies=sorted(self.movies_db, key=lambda x: x.rating, reverse=True)[:5],
            recentlyAnalyzed=self.movies_db[-3:]
        )
