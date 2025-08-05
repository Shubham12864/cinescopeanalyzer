import os
import httpx
import asyncio
import logging
from typing import List, Optional, Dict, Any

class TMDBApi:
    def __init__(self, api_key: str = None):
        # Real TMDB credentials provided by user
        self.api_key = api_key or os.getenv("TMDB_API_KEY", "9f362b6618db6e8a53976a51c2da62a4")
        self.access_token = os.getenv("TMDB_ACCESS_TOKEN", "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ZjM2MmI2NjE4ZGI2ZThhNTM5NzZhNTFjMmRhNjJhNCIsIm5iZiI6MTc1MDE2OTg2Ni4wODA5OTk5LCJzdWIiOiI2ODUxNzkwYTNhODk3M2NjMmM2YWVhOTciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.q74ulySmlmbxKBPFda37bXbuFd3ZAMMRReoc_lWLCLg")
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self.logger = logging.getLogger(__name__)
        
        # Headers for Bearer token authentication (preferred method)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json;charset=utf-8"
        }
        
        self.logger.info("✅ TMDB API initialized with real credentials")

    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search movies using real TMDB API"""
        if not query.strip():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/movie",
                    headers=self.headers,
                    params={
                        "api_key": self.api_key,
                        "query": query,
                        "page": 1,
                        "include_adult": False,
                        "language": "en-US"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    movies = []
                    
                    for item in data.get("results", [])[:limit]:
                        movie_data = self._format_tmdb_movie(item)
                        if movie_data:
                            movies.append(movie_data)
                    
                    self.logger.info(f"✅ TMDB returned {len(movies)} real movies for '{query}'")
                    return movies
                else:
                    self.logger.warning(f"⚠️ TMDB API returned status {response.status_code}")
                    return self._get_demo_movies(query, limit)
                    
        except Exception as e:
            self.logger.error(f"❌ TMDB search error: {e}")
            return self._get_demo_movies(query, limit)

    async def get_popular_movies(self) -> Dict[str, Any]:
        """Get popular movies from TMDB API using real credentials"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/movie/popular",
                    headers=self.headers,
                    params={
                        "api_key": self.api_key,
                        "language": "en-US",
                        "page": 1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"✅ TMDB popular API returned {len(data.get('results', []))} movies")
                    return data
                else:
                    self.logger.error(f"❌ TMDB popular API error: {response.status_code}")
                    return self._get_demo_popular_data()
                    
        except Exception as e:
            self.logger.error(f"❌ TMDB popular API request failed: {e}")
            return self._get_demo_popular_data()

    async def get_trending_movies(self, time_window: str = "week") -> Dict[str, Any]:
        """Get trending movies from TMDB API using real credentials"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/trending/movie/{time_window}",
                    headers=self.headers,
                    params={
                        "api_key": self.api_key,
                        "language": "en-US"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"✅ TMDB trending API returned {len(data.get('results', []))} movies")
                    return data
                else:
                    self.logger.error(f"❌ TMDB trending API error: {response.status_code}")
                    return self._get_demo_trending_data()
                    
        except Exception as e:
            self.logger.error(f"❌ TMDB trending API request failed: {e}")
            return self._get_demo_trending_data()

    async def get_movie_details(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed movie information by TMDB ID"""
        try:
            # Remove 'tmdb_' prefix if present
            tmdb_id = movie_id.replace('tmdb_', '') if movie_id.startswith('tmdb_') else movie_id
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Get movie details
                response = await client.get(
                    f"{self.base_url}/movie/{tmdb_id}",
                    headers=self.headers,
                    params={
                        "api_key": self.api_key,
                        "language": "en-US"
                    }
                )
                
                if response.status_code == 200:
                    movie_data = response.json()
                    
                    # Format the movie data
                    formatted_movie = self._format_detailed_tmdb_movie(movie_data)
                    self.logger.info(f"✅ TMDB movie details retrieved for ID: {tmdb_id}")
                    return formatted_movie
                else:
                    self.logger.warning(f"⚠️ TMDB movie details API returned status {response.status_code} for ID: {tmdb_id}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"❌ TMDB movie details error for ID {movie_id}: {e}")
            return None

    def _format_detailed_tmdb_movie(self, tmdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert detailed TMDB movie data to our standard format"""
        try:
            # Extract year from release date
            year = 2023
            if tmdb_data.get('release_date'):
                try:
                    year = int(tmdb_data['release_date'][:4])
                except (ValueError, TypeError):
                    year = 2023
            
            # Extract poster URL
            poster_url = ""
            if tmdb_data.get('poster_path'):
                poster_url = f"{self.image_base_url}{tmdb_data['poster_path']}"
            
            # Extract genres
            genres = []
            if tmdb_data.get('genres'):
                genres = [genre['name'] for genre in tmdb_data['genres']]
            if not genres:
                genres = ["Unknown"]
            
            # Extract cast from credits (simplified)
            cast = ["Cast info requires additional API call"]
            
            # Extract director from crew (simplified)
            director = "Director info requires additional API call"
            
            # Get external IDs for IMDB (simplified)
            imdb_id = f"tmdb_{tmdb_data.get('id', 'unknown')}"
            
            return {
                "id": str(tmdb_data.get('id', 'unknown')),
                "imdbId": imdb_id,
                "title": tmdb_data.get('title', 'Unknown Title'),
                "year": year,
                "poster": poster_url,
                "rating": float(tmdb_data.get('vote_average', 0)),
                "plot": tmdb_data.get('overview', ''),
                "genre": genres,
                "director": director,
                "cast": cast,
                "runtime": tmdb_data.get('runtime'),
                "awards": [],  # TMDB doesn't provide awards in this format
                "reviews": [],
                "tmdb_id": tmdb_data.get('id'),
                "source": "tmdb_details"
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting detailed TMDB movie data: {e}")
            return None

    def _format_tmdb_movie(self, tmdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert TMDB movie data to our standard format"""
        try:
            year = 2023
            if tmdb_data.get('release_date'):
                try:
                    year = int(tmdb_data['release_date'][:4])
                except (ValueError, TypeError):
                    year = 2023
            
            poster_url = ""
            if tmdb_data.get('poster_path'):
                poster_url = f"{self.image_base_url}{tmdb_data['poster_path']}"
            
            return {
                "id": f"tmdb_{tmdb_data.get('id', 'unknown')}",
                "imdbId": f"tmdb_{tmdb_data.get('id', 'unknown')}",
                "title": tmdb_data.get('title', 'Unknown Title'),
                "year": year,
                "poster": poster_url,
                "rating": float(tmdb_data.get('vote_average', 0)),
                "plot": tmdb_data.get('overview', ''),
                "genre": ["Unknown"],
                "director": "Unknown",
                "cast": ["Unknown"],
                "runtime": None,
                "awards": [],
                "reviews": [],
                "tmdb_id": tmdb_data.get('id'),
                "source": "tmdb_live"
            }
            
        except Exception as e:
            self.logger.error(f"Error formatting TMDB movie data: {e}")
            return None

    def _get_demo_movies(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Return demo movies when API fails"""
        demo_movies = [
            {
                "id": "demo_tt0111161",
                "imdbId": "demo_tt0111161", 
                "title": f"Demo: {query.title()} Movie 1",
                "year": 2023,
                "poster": "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=Demo+Movie",
                "rating": 8.5,
                "plot": f"Demo movie for search '{query}'",
                "genre": ["Drama"],
                "director": "Demo Director",
                "cast": ["Demo Actor"],
                "runtime": 120,
                "awards": [],
                "reviews": [],
                "source": "tmdb_demo"
            }
        ]
        return demo_movies[:limit]

    def _get_demo_popular_data(self) -> Dict[str, Any]:
        """Return demo popular movies data"""
        return {
            "results": [
                {
                    "id": "278",
                    "title": "The Shawshank Redemption",
                    "vote_average": 9.3,
                    "release_date": "1994-09-23",
                    "overview": "Two imprisoned men bond over years, finding solace and redemption.",
                    "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
                }
            ]
        }

    def _get_demo_trending_data(self) -> Dict[str, Any]:
        """Return demo trending movies data"""
        return {
            "results": [
                {
                    "id": "550",
                    "title": "Fight Club",
                    "vote_average": 8.8,
                    "release_date": "1999-10-15",
                    "overview": "An insomniac office worker forms an underground fight club.",
                    "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"
                }
            ]
        }
