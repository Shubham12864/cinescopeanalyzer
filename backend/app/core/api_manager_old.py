import asyncio
from typing import Optional, Dict, List
import logging
from .tmdb_api import TMDbAPI  # type: ignore # This import may be failing
from .omdb_api import OMDbAPI   # This import may be failing

class APIManager:
    def __init__(self):
        try:
            self.tmdb = TMDbAPI()
            self.omdb = OMDbAPI()
            self.logger = logging.getLogger(__name__)
        except ImportError as e:
            self.logger.error(f"Failed to import API modules: {e}")
            # Add fallback initialization
            self.tmdb = None
            self.omdb = None
            self.logger = logging.getLogger(__name__)
        
    async def get_comprehensive_movie_data(self, title: str) -> Dict:
        """Get movie data from both APIs and merge"""
        try:
            self.logger.info(f"🔍 Searching APIs for: {title}")
            
            # Run both API calls concurrently
            tmdb_task = self.tmdb.search_movie(title)
            omdb_task = self.omdb.search_by_title(title)
            
            tmdb_result, omdb_result = await asyncio.gather(
                tmdb_task, omdb_task, return_exceptions=True
            )
            
            # Process results
            merged_data = {
                'title': title,
                'source': 'API',
                'tmdb_available': isinstance(tmdb_result, dict),
                'omdb_available': isinstance(omdb_result, dict)
            }
            
            # Get detailed TMDb data if available
            if isinstance(tmdb_result, dict) and tmdb_result.get('id'):
                details = await self.tmdb.get_movie_details(tmdb_result['id'])
                tmdb_formatted = self.tmdb.format_movie_data(tmdb_result, details)
                merged_data.update(tmdb_formatted)
                
                # Get reviews from TMDb
                reviews = await self.tmdb.get_movie_reviews(tmdb_result['id'])
                merged_data['reviews'] = [
                    {
                        'text': review.get('content', ''),
                        'author': review.get('author', 'Anonymous'),
                        'source': 'TMDb'
                    }
                    for review in reviews[:10]  # Limit to 10 reviews
                ]
            
            # Merge OMDb data
            if isinstance(omdb_result, dict):
                omdb_formatted = self.omdb.format_movie_data(omdb_result)
                
                # Use OMDb data to fill missing fields
                for key, value in omdb_formatted.items():
                    if key not in merged_data or merged_data[key] in ['Unknown', 'N/A', None]:
                        merged_data[key] = value
            
            self.logger.info(f"✅ API data merged for: {merged_data.get('title', title)}")
            return merged_data
            
        except Exception as e:
            self.logger.error(f"❌ API manager error: {str(e)}")
            return {
                'title': title,
                'source': 'API (Error)',
                'error': str(e)
            }
        
    async def get_movie_with_reviews(self, title: str, max_reviews: int = 20) -> Dict:
        """Get movie data plus reviews"""
        movie_data = await self.get_comprehensive_movie_data(title)
        
        # If we have TMDb ID, get more reviews
        if movie_data.get('tmdb_id'):
            try:
                reviews = await self.tmdb.get_movie_reviews(movie_data['tmdb_id'])
                movie_data['reviews'] = [
                    {
                        'text': review.get('content', ''),
                        'author': review.get('author', 'Anonymous'),
                        'rating': review.get('author_details', {}).get('rating'),
                        'source': 'TMDb'
                    }
                    for review in reviews[:max_reviews]
                ]
            except Exception as e:
                self.logger.error(f"Error getting reviews: {str(e)}")
        
        return movie_data