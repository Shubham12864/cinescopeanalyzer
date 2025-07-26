import os
import httpx
from typing import Optional, Dict, List
import logging
from dotenv import load_dotenv

load_dotenv()

class OMDbAPI:
    def __init__(self, api_key: str = "4977b044"):  # Updated API key
        self.api_key = api_key or "4977b044"
        self.base_url = "http://www.omdbapi.com"
        self.logger = logging.getLogger(__name__)

    async def search_movies(self, query: str, limit: int = 20) -> List[Dict]:
        """Search movies using real OMDB API"""
        if not query.strip():
            return []        # Check if we have a real API key
        if self.api_key in ["demo_key", "", None] or len(self.api_key) < 6:
            self.logger.error("❌ Invalid OMDB API key - returning empty results")
            return []
        
        try:
            self.logger.info(f"🔍 OMDB API: Searching for '{query}' with API key length: {len(self.api_key)}")
            async with httpx.AsyncClient(timeout=15.0) as client:
                # First, search for movies
                search_response = await client.get(
                    f"{self.base_url}/",
                    params={
                        "apikey": self.api_key,
                        "s": query,
                        "type": "movie",
                        "page": 1
                    }
                )
                
                self.logger.info(f"🌐 OMDB API response status: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    self.logger.info(f"📊 OMDB API response: {search_data}")
                    
                    if search_data.get("Response") == "True":
                        movies = []
                        search_results = search_data.get("Search", [])[:limit]
                        self.logger.info(f"🎬 Found {len(search_results)} movies, fetching details...")
                        
                        # Get detailed info for each movie
                        for movie in search_results:
                            imdb_id = movie.get("imdbID")
                            if imdb_id:
                                detailed_movie = await self._get_movie_details(client, imdb_id)
                                if detailed_movie:
                                    movies.append(detailed_movie)
                        
                        self.logger.info(f"✅ OMDB returned {len(movies)} real movies for '{query}'")
                        return movies
                    elif search_data.get("Error") == "Invalid API key!":
                        self.logger.error("❌ OMDB API key is invalid")
                    elif search_data.get("Error") == "Request limit reached!":
                        self.logger.error("❌ OMDB API request limit reached")
                    else:
                        self.logger.warning(f"OMDB search failed: {search_data.get('Error', 'Unknown error')}")
                else:
                    self.logger.error(f"❌ OMDB API HTTP error: {search_response.status_code}")
                        
        except Exception as e:
            self.logger.error(f"OMDB API error: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Fallback to demo data
        self.logger.warning("🔄 Falling back to OMDB demo data")
        return self._get_demo_search_results(query)[:limit]

    async def _get_movie_details(self, client: httpx.AsyncClient, imdb_id: str) -> Optional[Dict]:
        """Get detailed movie information"""
        try:
            detail_response = await client.get(
                f"{self.base_url}/",
                params={
                    "apikey": self.api_key,
                    "i": imdb_id,
                    "plot": "full"
                }            )
            
            if detail_response.status_code == 200:
                data = detail_response.json()
                if data.get("Response") == "True":
                    return self._format_omdb_movie(data)
                    
        except Exception as e:
            self.logger.error(f"Error getting details for {imdb_id}: {e}")
        
        return None

    async def get_movie_by_id(self, imdb_id: str) -> Optional[Dict]:
        """Get detailed movie info by IMDB ID"""
        if not imdb_id or self.api_key in ["demo_key", "", None]:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    params={
                        "apikey": self.api_key,
                        "i": imdb_id,  # IMDB ID parameter
                        "plot": "full"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("Response") == "True":
                        return self._format_omdb_movie(data)
                    else:
                        self.logger.warning(f"OMDB returned error for {imdb_id}: {data.get('Error')}")
                        
        except Exception as e:
            self.logger.error(f"OMDB detail fetch error for {imdb_id}: {e}")
        
        return None

    def _format_omdb_movie(self, data: Dict) -> Dict:
        """Format OMDB response to our movie format with enhanced data"""
        # Handle poster URL properly
        poster_url = data.get('Poster', '')
        if poster_url and poster_url != 'N/A':
            # OMDB returns direct Amazon S3 URLs - use them as-is
            formatted_poster = poster_url
        else:
            formatted_poster = '/placeholder.svg?height=450&width=300'
        
        # Parse additional OMDB data for richer analysis
        awards = data.get('Awards', 'N/A')
        box_office = data.get('BoxOffice', 'N/A')
        ratings = data.get('Ratings', [])
        
        return {
            'id': data.get('imdbID', ''),
            'title': data.get('Title', 'Unknown'),
            'year': self._parse_year(data.get('Year', '0')),
            'plot': data.get('Plot', 'No plot available'),
            'rating': self._parse_rating(data.get('imdbRating', '0')),
            'genre': data.get('Genre', '').split(', ') if data.get('Genre') else [],
            'director': data.get('Director', 'Unknown'),
            'cast': data.get('Actors', '').split(', ') if data.get('Actors') else [],
            'poster': formatted_poster,
            'runtime': self._parse_runtime(data.get('Runtime', '0 min')),
            'imdbId': data.get('imdbID', ''),
            'reviews': [],
            'source': 'omdb_live',  # Mark as real data
            # Enhanced OMDB data
            'country': data.get('Country', ''),
            'language': data.get('Language', ''),
            'awards': awards if awards != 'N/A' else '',
            'box_office': box_office if box_office != 'N/A' else '',
            'metascore': self._parse_rating(data.get('Metascore', '0')),
            'imdb_votes': data.get('imdbVotes', ''),
            'production': data.get('Production', ''),
            'website': data.get('Website', ''),
            'dvd_release': data.get('DVD', ''),
            'all_ratings': ratings,  # Array of rating sources
            'rated': data.get('Rated', ''),  # MPAA rating
            'released': data.get('Released', ''),
            'writer': data.get('Writer', ''),
            'type': data.get('Type', 'movie')  # movie/series/episode
        }

    def _parse_year(self, year_str: str) -> int:
        """Parse year from string like '2010' or '2010-2012'"""
        try:
            return int(year_str.split('–')[0].split('-')[0])
        except:
            return 0

    def _parse_rating(self, rating_str: str) -> float:
        """Parse rating from string"""
        try:
            return float(rating_str) if rating_str != 'N/A' else 0.0
        except:
            return 0.0

    def _parse_runtime(self, runtime_str: str) -> int:
        """Parse runtime from string like '148 min'"""
        try:
            return int(runtime_str.split()[0])
        except:
            return 0

    # Keep existing demo data methods...
    def _get_demo_search_results(self, query: str) -> List[Dict]:
        """Fallback demo data"""
        demo_movies = [
            {
                'id': 'tt0137523',
                'title': 'Fight Club',
                'year': 1999,
                'plot': 'An insomniac office worker and a devil-may-care soap maker form an underground fight club.',
                'rating': 8.8,
                'genre': ['Drama', 'Thriller'],
                'director': 'David Fincher',
                'cast': ['Brad Pitt', 'Edward Norton', 'Helena Bonham Carter'],
                'poster': '/placeholder.svg?height=450&width=300',
                'runtime': 139,
                'imdbId': 'tt0137523',
                'reviews': [],
                'source': 'omdb_demo'
            },
            {
                'id': 'tt0468569',
                'title': 'The Dark Knight',
                'year': 2008,
                'plot': 'Batman faces the Joker in a battle for Gotham City.',
                'rating': 9.0,
                'genre': ['Action', 'Crime', 'Drama'],
                'director': 'Christopher Nolan',
                'cast': ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart'],
                'poster': '/placeholder.svg?height=450&width=300',
                'runtime': 152,
                'imdbId': 'tt0468569',
                'reviews': [],
                'source': 'omdb_demo'
            },
            {
                'id': 'tt1375666',
                'title': 'Inception',
                'year': 2010,
                'plot': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.',
                'rating': 8.8,
                'genre': ['Action', 'Sci-Fi', 'Thriller'],
                'director': 'Christopher Nolan',
                'cast': ['Leonardo DiCaprio', 'Marion Cotillard', 'Tom Hardy'],
                'poster': '/placeholder.svg?height=450&width=300',
                'runtime': 148,
                'imdbId': 'tt1375666',
                'reviews': [],
                'source': 'omdb_demo'
            },
            {
                'id': 'tt0111161',
                'title': 'The Shawshank Redemption',
                'year': 1994,
                'plot': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'rating': 9.3,
                'genre': ['Drama'],
                'director': 'Frank Darabont',
                'cast': ['Tim Robbins', 'Morgan Freeman'],
                'poster': '/placeholder.svg?height=450&width=300',
                'runtime': 142,
                'imdbId': 'tt0111161',
                'reviews': [],
                'source': 'omdb_demo'
            }
        ]
        return [movie for movie in demo_movies if query.lower() in movie['title'].lower()]
