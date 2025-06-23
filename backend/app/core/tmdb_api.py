import os
import httpx
import asyncio
import logging
from typing import List, Optional, Dict, Any

class TMDBApi:
    def __init__(self, api_key: str = None):
        # Accept API key parameter or get from environment
        self.api_key = api_key or os.getenv("TMDB_API_KEY", "demo_key_12345")
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self.logger = logging.getLogger(__name__)

    async def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search movies using real TMDB API"""
        if not query.strip():
            return []
        
        # Check if we have a real API key
        if self.api_key in ["demo_key_12345", "demo_key", "", None]:
            self.logger.warning("⚠️ Using demo TMDB key - get real key at https://www.themoviedb.org/settings/api")
            return self._get_demo_movies(query, limit)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/movie",
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
                elif response.status_code == 401:
                    self.logger.error("❌ TMDB API key is invalid")
                elif response.status_code == 429:
                    self.logger.error("❌ TMDB API rate limit exceeded")
                else:
                    self.logger.error(f"TMDB API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            self.logger.error(f"TMDB search error: {e}")
        
        # Fallback to demo data
        self.logger.warning("🔄 Falling back to TMDB demo data")
        return self._get_demo_movies(query, limit)

    async def get_trending(self, media_type: str = "movie", time_window: str = "week", limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending movies from TMDB"""
        if self.api_key in ["demo_key_12345", "demo_key", "", None]:
            self.logger.warning("⚠️ Using demo trending data - get real TMDB key")
            return self._get_demo_trending(limit)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/trending/{media_type}/{time_window}",
                    params={
                        "api_key": self.api_key,
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
                    
                    self.logger.info(f"✅ TMDB trending returned {len(movies)} movies")
                    return movies
                else:
                    self.logger.warning(f"⚠️ TMDB trending failed: {response.status_code}")
                    return self._get_demo_trending(limit)
                    
        except Exception as e:
            self.logger.error(f"❌ TMDB trending error: {e}")
            return self._get_demo_trending(limit)

    async def get_popular(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular movies from TMDB"""
        if self.api_key in ["demo_key_12345", "demo_key", "", None]:
            self.logger.warning("⚠️ Using demo popular data - get real TMDB key")
            return self._get_demo_popular(limit)
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/movie/popular",
                    params={
                        "api_key": self.api_key,
                        "language": "en-US",
                        "page": 1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    movies = []
                    
                    for item in data.get("results", [])[:limit]:
                        movie_data = self._format_tmdb_movie(item)
                        if movie_data:
                            movies.append(movie_data)
                    
                    self.logger.info(f"✅ TMDB popular returned {len(movies)} movies")
                    return movies
                else:
                    self.logger.warning(f"⚠️ TMDB popular failed: {response.status_code}")
                    return self._get_demo_popular(limit)
                    
        except Exception as e:
            self.logger.error(f"❌ TMDB popular error: {e}")
            return self._get_demo_popular(limit)

    async def get_trending_movies(self, time_window: str = "week") -> Dict[str, Any]:
        """Get trending movies from TMDB API"""
        if self.api_key in ["demo_key_12345", "demo_key", "", None]:
            self.logger.warning("⚠️ Using demo TMDB key for trending movies")
            return self._get_demo_trending_data()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/trending/movie/{time_window}",
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

    async def get_popular_movies(self) -> Dict[str, Any]:
        """Get popular movies from TMDB API"""
        if self.api_key in ["demo_key_12345", "demo_key", "", None]:
            self.logger.warning("⚠️ Using demo TMDB key for popular movies")
            return self._get_demo_popular_data()
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/movie/popular",
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

    def _format_tmdb_movie(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format TMDB data to our movie format"""
        try:
            return {
                'id': f"tmdb_{item.get('id', '')}",
                'title': item.get('title', 'Unknown'),
                'year': self._parse_year(item.get('release_date', '')),
                'plot': item.get('overview', 'No plot available'),
                'rating': round(item.get('vote_average', 0), 1),
                'genre': self._get_genre_names(item.get('genre_ids', [])),
                'director': 'Unknown',  # Would need separate API call
                'cast': [],  # Would need separate API call
                'poster': self._get_poster_url(item.get('poster_path')),
                'runtime': 0,  # Would need separate API call
                'imdbId': '',  # Would need separate API call
                'reviews': [],
                'source': 'tmdb_live'  # Mark as real data
            }
        except Exception as e:
            self.logger.error(f"Error formatting TMDB movie: {e}")
            return None

    def _parse_year(self, date_str: str) -> int:
        """Parse year from release date"""
        try:
            return int(date_str[:4]) if date_str else 0
        except:
            return 0

    def _get_poster_url(self, poster_path: Optional[str]) -> str:
        """Get full poster URL"""
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return '/placeholder.svg?height=450&width=300'

    def _get_genre_names(self, genre_ids: List[int]) -> List[str]:
        """Convert TMDB genre IDs to genre names"""
        genre_map = {
            28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
            80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
            14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
            9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
            10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
        }
        return [genre_map.get(gid, "Unknown") for gid in genre_ids if gid in genre_map]

    def _get_demo_movies(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback demo data"""
        demo_movies = [
            {
                'id': 'tmdb_demo_1',
                'title': 'The Matrix',
                'year': 1999,
                'plot': 'A computer programmer discovers reality is a simulation.',
                'rating': 8.7,
                'genre': ['Action', 'Science Fiction'],
                'director': 'The Wachowskis',
                'cast': ['Keanu Reeves', 'Laurence Fishburne'],
                'poster': '/placeholder.svg?height=450&width=300',
                'runtime': 136,
                'imdbId': 'tt0133093',
                'reviews': [],
                'source': 'tmdb_demo'
            }
        ]
        return [movie for movie in demo_movies if query.lower() in movie['title'].lower()][:limit]

    def _get_demo_trending(self, limit: int) -> List[Dict[str, Any]]:
        """Demo trending movies with real poster URLs"""
        demo_trending = [
            {
                'id': 'trending_1',
                'title': 'Dune: Part Two',
                'year': 2024,
                'plot': 'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.',
                'rating': 8.8,
                'genre': ['Science Fiction', 'Adventure', 'Drama'],
                'director': 'Denis Villeneuve',
                'cast': ['Timothée Chalamet', 'Zendaya', 'Rebecca Ferguson'],
                'poster': 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg',
                'runtime': 166,
                'imdbId': 'tt15239678',
                'source': 'tmdb_trending_demo'
            },
            {
                'id': 'trending_2',
                'title': 'Spider-Man: No Way Home',
                'year': 2021,
                'plot': 'Spider-Man seeks the help of Doctor Strange to forget his exposed secret identity as Peter Parker.',
                'rating': 8.2,
                'genre': ['Action', 'Adventure', 'Science Fiction'],
                'director': 'Jon Watts',
                'cast': ['Tom Holland', 'Zendaya', 'Benedict Cumberbatch'],
                'poster': 'https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg',
                'runtime': 148,
                'imdbId': 'tt10872600',
                'source': 'tmdb_trending_demo'
            },
            {
                'id': 'trending_3',
                'title': 'Avengers: Endgame',
                'year': 2019,
                'plot': 'After the devastating events of Infinity War, the universe is in ruins.',
                'rating': 8.4,
                'genre': ['Action', 'Adventure', 'Drama'],
                'director': 'Anthony Russo',
                'cast': ['Robert Downey Jr.', 'Chris Evans', 'Mark Ruffalo'],
                'poster': 'https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg',
                'runtime': 181,
                'imdbId': 'tt4154796',
                'source': 'tmdb_trending_demo'
            },
            {
                'id': 'trending_4',
                'title': 'Oppenheimer',
                'year': 2023,
                'plot': 'The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.',
                'rating': 8.4,
                'genre': ['Biography', 'Drama', 'History'],
                'director': 'Christopher Nolan',
                'cast': ['Cillian Murphy', 'Emily Blunt', 'Matt Damon'],
                'poster': 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
                'runtime': 180,
                'imdbId': 'tt15398776',
                'source': 'tmdb_trending_demo'
            }
        ]
        return demo_trending[:limit]

    def _get_demo_popular(self, limit: int) -> List[Dict[str, Any]]:
        """Demo popular movies with real poster URLs"""
        demo_popular = [
            {
                'id': 'popular_1',
                'title': 'Top Gun: Maverick',
                'year': 2022,
                'plot': 'After thirty years, Maverick is still pushing the envelope as a top naval aviator.',
                'rating': 8.3,
                'genre': ['Action', 'Drama'],
                'director': 'Joseph Kosinski',
                'cast': ['Tom Cruise', 'Miles Teller', 'Jennifer Connelly'],
                'poster': 'https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg',
                'runtime': 130,
                'imdbId': 'tt1745960',
                'source': 'tmdb_popular_demo'
            },
            {
                'id': 'popular_2',
                'title': 'Black Panther: Wakanda Forever',
                'year': 2022,
                'plot': 'Queen Ramonda, Shuri, M\'Baku, Okoye and the Dora Milaje fight to protect their nation.',
                'rating': 6.7,
                'genre': ['Action', 'Adventure', 'Drama'],
                'director': 'Ryan Coogler',
                'cast': ['Letitia Wright', 'Lupita Nyong\'o', 'Danai Gurira'],
                'poster': 'https://image.tmdb.org/t/p/w500/sv1xJUazXeYqALzczSZ3O6nkH75.jpg',
                'runtime': 161,
                'imdbId': 'tt9114286',
                'source': 'tmdb_popular_demo'
            },
            {
                'id': 'popular_3',
                'title': 'The Batman',
                'year': 2022,
                'plot': 'Batman ventures into Gotham City\'s underworld when a sadistic killer leaves behind a trail of cryptic clues.',
                'rating': 7.8,
                'genre': ['Action', 'Crime', 'Drama'],
                'director': 'Matt Reeves',
                'cast': ['Robert Pattinson', 'Zoë Kravitz', 'Jeffrey Wright'],
                'poster': 'https://image.tmdb.org/t/p/w500/b0PlSFdDwbyK0cf5RxwDpaOJQvQ.jpg',
                'runtime': 176,
                'imdbId': 'tt1877830',
                'source': 'tmdb_popular_demo'
            },
            {
                'id': 'popular_4',
                'title': 'Doctor Strange in the Multiverse of Madness',
                'year': 2022,
                'plot': 'Doctor Strange teams up with a mysterious teenage girl who can travel across multiverses.',
                'rating': 6.9,
                'genre': ['Action', 'Adventure', 'Fantasy'],
                'director': 'Sam Raimi',
                'cast': ['Benedict Cumberbatch', 'Elizabeth Olsen', 'Chiwetel Ejiofor'],
                'poster': 'https://image.tmdb.org/t/p/w500/9Gtg2DzBhmYamXBS1hKAhiwbBKS.jpg',
                'runtime': 126,
                'imdbId': 'tt9419884',
                'source': 'tmdb_popular_demo'
            }
        ]
        return demo_popular[:limit]

    def _get_demo_trending_data(self) -> Dict[str, Any]:
        """Demo trending data"""
        return {
            "results": [
                {
                    "id": 634649,
                    "title": "Spider-Man: No Way Home",
                    "original_title": "Spider-Man: No Way Home",
                    "overview": "Peter Parker is unmasked and no longer able to separate his normal life from the high-stakes of being a super-hero.",
                    "poster_path": "/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
                    "backdrop_path": "/iQFcwSGbZXMkeyKrxbPnwnRo5fl.jpg",
                    "release_date": "2021-12-15",
                    "vote_average": 8.1,
                    "genre_ids": [28, 12, 878]
                },
                {
                    "id": 19995,
                    "title": "Avatar",
                    "original_title": "Avatar",
                    "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission.",
                    "poster_path": "/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg",
                    "backdrop_path": "/o0s4XsEDfDlvit5pDRKjzXR4pp2.jpg",
                    "release_date": "2009-12-15",
                    "vote_average": 7.6,
                    "genre_ids": [28, 12, 14, 878]
                },
                {
                    "id": 155,
                    "title": "The Dark Knight",
                    "original_title": "The Dark Knight",
                    "overview": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and DA Harvey Dent.",
                    "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
                    "backdrop_path": "/hqkIcbrOHL86UncnHIsHVcVmzue.jpg",
                    "release_date": "2008-07-16",
                    "vote_average": 9.0,
                    "genre_ids": [28, 80, 18, 53]
                }
            ]
        }

    def _get_demo_popular_data(self) -> Dict[str, Any]:
        """Demo popular data"""
        return {
            "results": [
                {
                    "id": 278,
                    "title": "The Shawshank Redemption",
                    "original_title": "The Shawshank Redemption",
                    "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
                    "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
                    "backdrop_path": "/j9XKiZrVeViAixVRzCta7h1VU9W.jpg",
                    "release_date": "1994-09-23",
                    "vote_average": 8.7,
                    "genre_ids": [18, 80]
                },
                {
                    "id": 238,
                    "title": "The Godfather",
                    "original_title": "The Godfather",
                    "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
                    "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
                    "backdrop_path": "/rSPw7tgCH9c6NqICZef4kZjFOQ5.jpg",
                    "release_date": "1972-03-14",
                    "vote_average": 8.7,
                    "genre_ids": [18, 80]
                },
                {
                    "id": 680,
                    "title": "Pulp Fiction",
                    "original_title": "Pulp Fiction",
                    "overview": "A burger-loving hit man, his philosophical partner, and a drug-addled gangster's moll become involved in a web of violence.",
                    "poster_path": "/dM2w364MScsjFf8pfMbaWUcWrR.jpg",
                    "backdrop_path": "/4cDFJr4HnXN5AdPw4AKrmLlMWdO.jpg",
                    "release_date": "1994-09-10",
                    "vote_average": 8.5,
                    "genre_ids": [80, 18]
                }
            ]
        }
# Legacy class for compatibility
class TMDbAPI(TMDBApi):
    pass
