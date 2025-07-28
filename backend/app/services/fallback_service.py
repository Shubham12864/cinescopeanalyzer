#!/usr/bin/env python3
"""
Fallback Movie Service
Provides sample movie data when external APIs fail due to network issues
"""
import json
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FallbackMovieService:
    """
    Fallback service that provides sample movie data when external APIs are unavailable
    """
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "fallback_movies.json"
        self.movies_data = {}
        self._load_fallback_data()
    
    def _load_fallback_data(self):
        """Load fallback movie data from JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    self.movies_data = json.load(f)
                logger.info(f"✅ Loaded fallback data for {len(self.movies_data)} search terms")
            else:
                logger.warning(f"⚠️ Fallback data file not found: {self.data_file}")
                self.movies_data = {}
        except Exception as e:
            logger.error(f"❌ Error loading fallback data: {e}")
            self.movies_data = {}
    
    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for movies in fallback data
        """
        query_lower = query.lower().strip()
        logger.info(f"🔍 Fallback search for: '{query}' (limit: {limit})")
        
        # Direct keyword match
        if query_lower in self.movies_data:
            movies = self.movies_data[query_lower][:limit]
            logger.info(f"✅ Found {len(movies)} fallback movies for '{query}'")
            return movies
        
        # Partial match search
        matching_movies = []
        for keyword, movies in self.movies_data.items():
            if query_lower in keyword or keyword in query_lower:
                matching_movies.extend(movies)
                if len(matching_movies) >= limit:
                    break
        
        # Also search in movie titles
        if not matching_movies:
            for movies in self.movies_data.values():
                for movie in movies:
                    if query_lower in movie.get('title', '').lower():
                        matching_movies.append(movie)
                        if len(matching_movies) >= limit:
                            break
                if len(matching_movies) >= limit:
                    break
        
        result = matching_movies[:limit]
        logger.info(f"✅ Found {len(result)} fallback movies for '{query}' (partial match)")
        return result
    
    async def get_movie_by_id(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a movie by IMDb ID from fallback data
        """
        for movies in self.movies_data.values():
            for movie in movies:
                if movie.get('imdb_id') == imdb_id:
                    logger.info(f"✅ Found fallback movie: {movie.get('title')} ({imdb_id})")
                    return movie
        
        logger.warning(f"⚠️ No fallback movie found for ID: {imdb_id}")
        return None
    
    def get_popular_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular movies from fallback data (highest rated)
        """
        all_movies = []
        for movies in self.movies_data.values():
            all_movies.extend(movies)
        
        # Sort by rating
        sorted_movies = sorted(all_movies, key=lambda x: x.get('rating', 0), reverse=True)
        result = sorted_movies[:limit]
        
        logger.info(f"✅ Returning {len(result)} popular fallback movies")
        return result
    
    def get_recent_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent movies from fallback data (newest first)
        """
        all_movies = []
        for movies in self.movies_data.values():
            all_movies.extend(movies)
        
        # Sort by year
        sorted_movies = sorted(all_movies, key=lambda x: x.get('year', 0), reverse=True)
        result = sorted_movies[:limit]
        
        logger.info(f"✅ Returning {len(result)} recent fallback movies")
        return result
    
    def get_available_genres(self) -> List[str]:
        """
        Get all available genres from fallback data
        """
        genres = set()
        for movies in self.movies_data.values():
            for movie in movies:
                genre_str = movie.get('genre', '')
                if genre_str:
                    for genre in genre_str.split(', '):
                        genres.add(genre.strip())
        
        return sorted(list(genres))
    
    def get_movies_by_genre(self, genre: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get movies by genre from fallback data
        """
        matching_movies = []
        for movies in self.movies_data.values():
            for movie in movies:
                movie_genres = movie.get('genre', '').lower()
                if genre.lower() in movie_genres:
                    matching_movies.append(movie)
                    if len(matching_movies) >= limit:
                        break
            if len(matching_movies) >= limit:
                break
        
        logger.info(f"✅ Found {len(matching_movies)} fallback movies for genre '{genre}'")
        return matching_movies
    
    def add_sample_reviews(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add sample reviews to a movie when Reddit API is unavailable
        """
        movie_copy = movie.copy()
        
        # Sample reviews based on movie title
        sample_reviews = [
            {
                "id": "fallback_1",
                "author": "movie_fan_2024",
                "rating": 4.5,
                "text": f"Great movie! {movie.get('title', 'This film')} exceeded my expectations.",
                "sentiment": "positive",
                "platform": "reddit",
                "created_at": "2024-01-15T10:30:00Z",
                "source": "fallback"
            },
            {
                "id": "fallback_2", 
                "author": "cinema_critic",
                "rating": 4.0,
                "text": f"Solid performance and great direction. {movie.get('director', 'The director')} did an excellent job.",
                "sentiment": "positive",
                "platform": "reddit",
                "created_at": "2024-01-20T14:45:00Z",
                "source": "fallback"
            },
            {
                "id": "fallback_3",
                "author": "film_enthusiast",
                "rating": 3.5,
                "text": "Good movie overall, though some parts could have been better. Worth watching!",
                "sentiment": "neutral",
                "platform": "reddit", 
                "created_at": "2024-01-25T18:20:00Z",
                "source": "fallback"
            }
        ]
        
        movie_copy['reviews'] = sample_reviews
        movie_copy['review_count'] = len(sample_reviews)
        movie_copy['average_rating'] = sum(r['rating'] for r in sample_reviews) / len(sample_reviews)
        
        return movie_copy

# Global instance
fallback_service = FallbackMovieService()