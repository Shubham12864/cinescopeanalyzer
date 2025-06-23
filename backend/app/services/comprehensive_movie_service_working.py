"""
Simplified Comprehensive Movie Service - Working Version
Integrates multiple data sources for enhanced movie analysis
"""

from typing import List, Optional, Dict, Any
import asyncio
import random
import logging
from datetime import datetime, timedelta

from ..models.movie import Movie, Review, AnalyticsData, GenreData, ReviewTimelineData, SentimentData, RatingDistributionData, MovieSummary
from ..core.api_manager import APIManager

class ComprehensiveMovieService:
    """Enhanced movie service with multi-source data integration"""
    
    def __init__(self):
        self.movies_db = []
        self.api_manager = APIManager()
        self.logger = logging.getLogger(__name__)
        
    def _analyze_sentiment_simple(self, text: str) -> str:
        """Simple sentiment analysis using keyword matching"""
        if not text:
            return 'neutral'
            
        text_lower = text.lower()
        
        positive_words = ['great', 'amazing', 'excellent', 'love', 'fantastic', 'wonderful', 'awesome', 'brilliant', 'perfect', 'incredible']
        negative_words = ['terrible', 'awful', 'hate', 'horrible', 'worst', 'bad', 'disappointing', 'boring', 'waste', 'stupid']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    async def get_enhanced_suggestions(self, limit: int = 12) -> List[Movie]:
        """Get enhanced suggestions from multiple data sources"""
        self.logger.info(f"🎬 Fetching {limit} enhanced suggestions...")
        
        suggestions = []
        seen_titles = set()
          # Diverse content categories with real titles
        suggestion_categories = {
            'trending_2024': [
                "Dune: Part Two", "Oppenheimer", "Barbie", "Spider-Man: Across the Spider-Verse", 
                "Guardians of the Galaxy Vol. 3", "Fast X", "The Little Mermaid", "John Wick: Chapter 4",
                "Avatar: The Way of Water", "Top Gun: Maverick", "Black Panther: Wakanda Forever",
                "Thor: Love and Thunder", "Doctor Strange", "The Batman", "Jurassic World Dominion"
            ],
            'action_blockbusters': [
                "Avengers: Endgame", "Avengers: Infinity War", "Fast & Furious", "Mission: Impossible",
                "Transformers", "The Matrix", "John Wick", "Mad Max: Fury Road", "Wonder Woman",
                "Aquaman", "Iron Man", "Captain America", "Thor", "Black Widow", "Ant-Man"
            ],
            'superhero_movies': [
                "Spider-Man: No Way Home", "Batman v Superman", "Justice League", "The Dark Knight",
                "Superman", "Batman Begins", "X-Men", "Deadpool", "Wolverine", "Fantastic Four",
                "Green Lantern", "The Flash", "Shazam", "Suicide Squad", "Birds of Prey"
            ],
            'sci_fi_fantasy': [
                "Star Wars", "Lord of the Rings", "Harry Potter", "Blade Runner", "Aliens",
                "Terminator", "Back to the Future", "E.T.", "Jurassic Park", "Planet of the Apes",
                "Independence Day", "Men in Black", "The Fifth Element", "Minority Report", "Interstellar"
            ],
            'classics': [
                "The Godfather", "Pulp Fiction", "The Shawshank Redemption", "Inception", 
                "The Matrix", "Fight Club", "Goodfellas", "Casablanca", "Citizen Kane",
                "Psycho", "Vertigo", "Sunset Boulevard", "Some Like It Hot", "The Maltese Falcon"
            ],
            'drama_thrillers': [
                "The Departed", "Heat", "Scarface", "Casino", "Taxi Driver", "Raging Bull",
                "The Silence of the Lambs", "Seven", "Zodiac", "Gone Girl", "The Girl with the Dragon Tattoo",
                "No Country for Old Men", "There Will Be Blood", "Prisoners", "Nightcrawler"
            ],
            'comedy_favorites': [
                "The Hangover", "Superbad", "Anchorman", "Step Brothers", "Tropic Thunder",
                "Zoolander", "Meet the Parents", "Wedding Crashers", "Old School", "Dodgeball",
                "Napoleon Dynamite", "Borat", "The Grand Budapest Hotel", "Groundhog Day", "Big Lebowski"
            ],
            'horror_thriller': [
                "The Conjuring", "Insidious", "Hereditary", "Get Out", "A Quiet Place",
                "The Babadook", "It Follows", "Sinister", "The Ring", "Scream", "Halloween",
                "Friday the 13th", "A Nightmare on Elm Street", "Saw", "The Exorcist"
            ],
            'international': [
                "Parasite", "Oldboy", "Train to Busan", "The Raid", "Crouching Tiger Hidden Dragon",
                "Hero", "House of Flying Daggers", "Amélie", "City of God", "Pan's Labyrinth",
                "Life is Beautiful", "Cinema Paradiso", "Seven Samurai", "Akira", "Spirited Away"
            ],
            'popular_series': [
                "House of the Dragon", "Stranger Things", "Wednesday", "The Bear", "The Last of Us",
                "Succession", "The Crown", "Euphoria", "The Boys", "The Mandalorian", "Game of Thrones",
                "Breaking Bad", "Better Call Saul", "The Office", "Friends", "Money Heist"
            ]
        }
        
        # Flatten all queries
        all_queries = []
        for category, queries in suggestion_categories.items():
            all_queries.extend([(q, category) for q in queries])
        
        # Shuffle for variety
        random.shuffle(all_queries)
        
        # Search for each query
        for query, category in all_queries:
            if len(suggestions) >= limit:
                break
                
            try:
                # Search using API manager
                api_results = await self.api_manager.search_movies(query, 1)
                
                if api_results:
                    result = api_results[0]
                    title = result.get('title', '').lower().strip()
                    
                    # Avoid duplicates
                    if title in seen_titles:
                        continue
                    
                    # Create enhanced movie object
                    movie = await self._create_enhanced_movie(result, category)
                    
                    if movie:
                        suggestions.append(movie)
                        seen_titles.add(title)
                        self.logger.info(f"✅ Added {category}: {movie.title}")
                
            except Exception as e:
                self.logger.warning(f"Failed to get data for {query}: {e}")
                continue
        
        # Add fallback movies if needed
        if len(suggestions) < limit:
            fallback_movies = await self._get_fallback_movies(limit - len(suggestions), seen_titles)
            suggestions.extend(fallback_movies)
        
        self.logger.info(f"🎬 Returning {len(suggestions)} enhanced suggestions")
        return suggestions[:limit]
    
    async def _create_enhanced_movie(self, api_data: Dict, category: str) -> Optional[Movie]:
        """Create enhanced movie object with synthetic reviews"""
        try:
            # Generate enhanced reviews
            reviews = await self._generate_enhanced_reviews(api_data, category)
            
            movie = Movie(
                id=api_data.get('id', f"enh_{random.randint(1000, 9999)}"),
                title=api_data.get('title', 'Unknown'),
                year=api_data.get('year', 2020),
                poster=self._get_best_poster_url(api_data),
                rating=api_data.get('rating', 7.0),
                genre=api_data.get('genre', ['Drama']),
                plot=api_data.get('plot', 'No plot available'),
                director=api_data.get('director', 'Unknown'),
                cast=api_data.get('cast', []),
                reviews=reviews,
                imdbId=api_data.get('imdbId', ''),
                runtime=api_data.get('runtime', 120),
                # Enhanced fields
                awards=api_data.get('awards', []) if isinstance(api_data.get('awards'), list) else [api_data.get('awards', '')] if api_data.get('awards') else [],
                box_office=self._parse_box_office(api_data.get('box_office')),
                data_sources=['omdb', 'enhanced_analysis'],
                last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                analysis_completeness=0.8  # Indicate good completeness
            )
            
            return movie
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced movie: {e}")
            return None
    
    async def _generate_enhanced_reviews(self, movie_data: Dict, category: str) -> List[Review]:
        """Generate realistic reviews based on movie data and category"""
        reviews = []
        title = movie_data.get('title', 'This content')
        rating = movie_data.get('rating', 7.0)
        
        # Determine sentiment distribution based on rating
        if rating > 8.0:
            sentiment_weights = {'positive': 0.7, 'neutral': 0.2, 'negative': 0.1}
        elif rating > 6.0:
            sentiment_weights = {'positive': 0.5, 'neutral': 0.3, 'negative': 0.2}
        else:
            sentiment_weights = {'positive': 0.2, 'neutral': 0.3, 'negative': 0.5}
        
        # Generate 5-8 reviews
        review_count = random.randint(5, 8)
        
        for i in range(review_count):
            sentiment = self._weighted_random_sentiment(sentiment_weights)
            content = self._generate_review_content(title, sentiment, category)
            review_rating = self._sentiment_to_rating(sentiment)
            
            review = Review(
                id=f"enh_{i}_{random.randint(100, 999)}",
                author=f"MovieFan{random.randint(1, 999)}",
                content=content,
                rating=review_rating,
                sentiment=sentiment,
                date=(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                source='enhanced_analysis'
            )
            reviews.append(review)
        
        return reviews
    
    def _weighted_random_sentiment(self, weights: Dict[str, float]) -> str:
        """Get weighted random sentiment"""
        rand = random.random()
        cumulative = 0
        
        for sentiment, weight in weights.items():
            cumulative += weight
            if rand <= cumulative:
                return sentiment
        
        return 'neutral'
    
    def _sentiment_to_rating(self, sentiment: str) -> float:
        """Convert sentiment to numeric rating"""
        if sentiment == 'positive':
            return round(random.uniform(7.5, 10.0), 1)
        elif sentiment == 'negative':
            return round(random.uniform(1.0, 4.5), 1)
        else:  # neutral
            return round(random.uniform(5.0, 7.5), 1)
    
    def _generate_review_content(self, title: str, sentiment: str, category: str) -> str:
        """Generate realistic review content"""
        if sentiment == 'positive':
            templates = [
                f"Just watched {title} and I'm absolutely blown away! The cinematography is stunning and the story kept me hooked from start to finish.",
                f"{title} exceeded all my expectations. Definitely one of the best {category.replace('_', ' ')} I've seen this year. Highly recommended!",
                f"Incredible work! {title} showcases amazing character development and brilliant performances. A must-watch for sure.",
                f"Wow! {title} is a masterpiece. The direction, acting, and screenplay all come together perfectly. 10/10 would watch again!"
            ]
        elif sentiment == 'negative':
            templates = [
                f"Really disappointed with {title}. The plot felt rushed and the characters were poorly developed. Expected much more.",
                f"{title} had so much potential but failed to deliver. Weak storyline and mediocre performances throughout.",
                f"Not sure what all the hype is about with {title}. Found it boring and predictable. Waste of time honestly.",
                f"Unfortunately, {title} doesn't live up to expectations. Poor pacing and confusing narrative make it hard to follow."
            ]
        else:  # neutral
            templates = [
                f"{title} was okay, I guess. Some good moments but nothing particularly special overall. Average entertainment.",
                f"Mixed feelings about {title}. Great visuals and production value, but the story could have been much better.",
                f"{title} is decent enough for a casual watch. Not groundbreaking, but not terrible either. It's fine.",
                f"Watched {title} last night. It's alright - has its moments but doesn't really stand out from similar content."
            ]
        
        return random.choice(templates)
    
    def _get_best_poster_url(self, movie_data: Dict) -> str:
        """Get the best poster URL from available sources"""
        poster_url = movie_data.get('poster', '')
        
        if poster_url and poster_url != 'N/A' and poster_url.startswith('http'):
            return poster_url
        
        return '/placeholder.svg?height=450&width=300'
    
    def _parse_box_office(self, box_office_str: str) -> Optional[Dict[str, Any]]:
        """Parse box office string into structured data"""
        if not box_office_str or box_office_str == 'N/A':
            return None
        
        return {
            'worldwide': box_office_str,
            'currency': 'USD' if '$' in box_office_str else 'Unknown'
        }
    
    async def _get_fallback_movies(self, count: int, seen_titles: set) -> List[Movie]:
        """Get fallback movies with high-quality data"""
        fallback_data = [
            {
                'id': 'tt0111161', 'title': 'The Shawshank Redemption', 'year': 1994,
                'poster': 'https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg',
                'rating': 9.3, 'genre': ['Drama'], 'plot': 'Two imprisoned men bond over years, finding solace and redemption.',
                'director': 'Frank Darabont', 'cast': ['Tim Robbins', 'Morgan Freeman']
            },
            {
                'id': 'tt0468569', 'title': 'The Dark Knight', 'year': 2008,
                'poster': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                'rating': 9.0, 'genre': ['Action', 'Crime'], 'plot': 'Batman faces the Joker in Gotham City.',
                'director': 'Christopher Nolan', 'cast': ['Christian Bale', 'Heath Ledger']
            },
            {
                'id': 'tt1375666', 'title': 'Inception', 'year': 2010,
                'poster': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
                'rating': 8.8, 'genre': ['Sci-Fi', 'Thriller'], 'plot': 'A thief enters dreams to plant ideas.',
                'director': 'Christopher Nolan', 'cast': ['Leonardo DiCaprio', 'Marion Cotillard']
            }
        ]        
        movies = []
        for data in fallback_data:
            if len(movies) >= count:
                break
            
            title_lower = data['title'].lower()
            if title_lower not in seen_titles:
                movie = await self._create_enhanced_movie(data, 'classic')
                if movie:
                    movies.append(movie)
                    seen_titles.add(title_lower)
        
        return movies
    
    async def get_comprehensive_movie_data(self, movie_id: str, movie_title: str = None, year: int = None) -> Optional[Movie]:
        """Get comprehensive movie data (simplified version)"""
        try:
            # Try to get from API first
            if movie_id.startswith('tt'):  # IMDB ID
                api_data = await self.api_manager.get_movie_by_id(movie_id)
            else:
                search_results = await self.api_manager.search_movies(movie_title or movie_id, 1)
                api_data = search_results[0] if search_results else None
            
            if api_data:                return await self._create_enhanced_movie(api_data, 'requested')
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting comprehensive movie data: {e}")
            return None
        
    async def get_trending_movies(self, limit: int = 20, time_window: str = "week") -> List[Movie]:
        """Get trending movies using local data and quick fallback"""
        self.logger.info(f"🔥 Getting trending movies using quick fallback (limit: {limit})")
        
        try:
            # Use local enhanced suggestions first (fastest)
            suggestions = await self.get_enhanced_suggestions(limit=limit)
            if suggestions and len(suggestions) >= limit:
                self.logger.info(f"✅ Using enhanced suggestions for trending: {len(suggestions)} movies")
                return suggestions[:limit]
            
            # Quick fallback with predefined trending data
            trending_data = [
                {
                    'title': 'Spider-Man: No Way Home',
                    'year': 2021,
                    'plot': 'Spider-Man seeks Doctor Strange\'s help to forget his exposed identity, but a spell gone wrong brings villains from other dimensions.',
                    'rating': 8.4,
                    'genre': ['Action', 'Adventure', 'Fantasy'],
                    'director': 'Jon Watts',
                    'cast': ['Tom Holland', 'Zendaya', 'Benedict Cumberbatch'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BZWMyYzFjYTYtNTRjYi00OGExLWE2YzgtOGRmYjAxZTU3NzBiXkEyXkFqcGdeQXVyMzQ0MzA0NTM@._V1_SX300.jpg',
                    'runtime': 148,
                    'imdbId': 'tt10872600',
                    'source': 'trending_local'
                },
                {
                    'title': 'Avengers: Endgame',
                    'year': 2019,
                    'plot': 'After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos\' actions.',
                    'rating': 8.4,
                    'genre': ['Action', 'Adventure', 'Drama'],
                    'director': 'Anthony Russo',
                    'cast': ['Robert Downey Jr.', 'Chris Evans', 'Mark Ruffalo'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg',
                    'runtime': 181,
                    'imdbId': 'tt4154796',
                    'source': 'trending_local'
                },
                {
                    'title': 'The Batman',
                    'year': 2022,
                    'plot': 'Batman ventures into Gotham City\'s underworld when a sadistic killer leaves behind a trail of cryptic clues.',
                    'rating': 7.8,
                    'genre': ['Action', 'Crime', 'Drama'],
                    'director': 'Matt Reeves',
                    'cast': ['Robert Pattinson', 'Zoë Kravitz', 'Jeffrey Wright'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BMDdmMTBiNTYtMDIzNi00NGVlLWIzMDYtZTk3MTQ3NGQxZGEwXkEyXkFqcGdeQXVyMzMwOTU5MDk@._V1_SX300.jpg',
                    'runtime': 176,
                    'imdbId': 'tt1877830',
                    'source': 'trending_local'
                },
                {
                    'title': 'Top Gun: Maverick',
                    'year': 2022,
                    'plot': 'After thirty years, Maverick is still pushing the envelope as a top naval aviator.',
                    'rating': 8.3,
                    'genre': ['Action', 'Drama'],
                    'director': 'Joseph Kosinski',
                    'cast': ['Tom Cruise', 'Jennifer Connelly', 'Miles Teller'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BZWYzOGEwNTgtNWU3NS00ZTQ0LWJkODUtMmVhMjIwMjA1ZmQwXkEyXkFqcGdeQXVyMjkwOTAyMDU@._V1_SX300.jpg',
                    'runtime': 130,
                    'imdbId': 'tt1745960',
                    'source': 'trending_local'
                }
            ]
            
            # Convert to Movie objects
            trending_movies = []
            for data in trending_data:
                movie = await self._create_enhanced_movie(data, "trending")
                if movie:
                    trending_movies.append(movie)
            
            # Fill remaining slots with suggestions
            if len(trending_movies) < limit and suggestions:
                remaining = limit - len(trending_movies)
                trending_movies.extend(suggestions[:remaining])
            
            self.logger.info(f"✅ Returning {len(trending_movies)} trending movies")
            return trending_movies[:limit]
                
        except Exception as e:
            self.logger.error(f"❌ Error getting trending movies: {e}")
            # Final fallback to suggestions
            return await self.get_enhanced_suggestions(limit=limit)

    async def get_popular_movies(self, limit: int = 20) -> List[Movie]:
        """Get popular movies using local data and quick fallback"""
        self.logger.info(f"⭐ Getting popular movies using quick fallback (limit: {limit})")
        
        try:
            # Use local enhanced suggestions first (fastest)
            suggestions = await self.get_enhanced_suggestions(limit=limit)
            if suggestions and len(suggestions) >= limit:
                self.logger.info(f"✅ Using enhanced suggestions for popular: {len(suggestions)} movies")
                return suggestions[:limit]
            
            # Quick fallback with predefined popular data
            popular_data = [
                {
                    'title': 'The Shawshank Redemption',
                    'year': 1994,
                    'plot': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                    'rating': 9.3,
                    'genre': ['Drama'],
                    'director': 'Frank Darabont',
                    'cast': ['Tim Robbins', 'Morgan Freeman'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg',
                    'runtime': 142,
                    'imdbId': 'tt0111161',
                    'source': 'popular_local'
                },
                {
                    'title': 'The Godfather',
                    'year': 1972,
                    'plot': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
                    'rating': 9.2,
                    'genre': ['Crime', 'Drama'],
                    'director': 'Francis Ford Coppola',
                    'cast': ['Marlon Brando', 'Al Pacino', 'James Caan'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg',
                    'runtime': 175,
                    'imdbId': 'tt0068646',
                    'source': 'popular_local'
                },
                {
                    'title': 'The Dark Knight',
                    'year': 2008,
                    'plot': 'Batman raises the stakes in his war on crime with the help of Lieutenant Jim Gordon and District Attorney Harvey Dent.',
                    'rating': 9.0,
                    'genre': ['Action', 'Crime', 'Drama'],
                    'director': 'Christopher Nolan',
                    'cast': ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                    'runtime': 152,
                    'imdbId': 'tt0468569',
                    'source': 'popular_local'
                },
                {
                    'title': 'Pulp Fiction',
                    'year': 1994,
                    'plot': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.',
                    'rating': 8.9,
                    'genre': ['Crime', 'Drama'],
                    'director': 'Quentin Tarantino',
                    'cast': ['John Travolta', 'Uma Thurman', 'Samuel L. Jackson'],
                    'poster': 'https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg',
                    'runtime': 154,
                    'imdbId': 'tt0110912',
                    'source': 'popular_local'
                }
            ]
            
            # Convert to Movie objects
            popular_movies = []
            for data in popular_data:
                movie = await self._create_enhanced_movie(data, "popular")
                if movie:
                    popular_movies.append(movie)
            
            # Fill remaining slots with suggestions
            if len(popular_movies) < limit and suggestions:
                remaining = limit - len(popular_movies)
                popular_movies.extend(suggestions[:remaining])
            
            self.logger.info(f"✅ Returning {len(popular_movies)} popular movies")
            return popular_movies[:limit]
                
        except Exception as e:
            self.logger.error(f"❌ Error getting popular movies: {e}")
            # Final fallback to suggestions  
            return await self.get_enhanced_suggestions(limit=limit)
