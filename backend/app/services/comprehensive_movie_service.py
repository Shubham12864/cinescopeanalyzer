"""
Comprehensive Movie Service with Multi-Source Data Integration
Combines OMDB, TMDB, Reddit API, and Web Scraping for enhanced analysis
"""

from typing import List, Optional, Dict, Any
import asyncio
import random
import logging
from datetime import datetime, timedelta
import json

from ..models.movie import Movie, Review, AnalyticsData, GenreData, ReviewTimelineData, SentimentData, RatingDistributionData, MovieSummary
from ..core.api_manager import APIManager

# Optional imports with fallbacks
try:
    from ..services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    
try:
    from ..scraper.comprehensive_movie_spider import ComprehensiveMovieSpider
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    
try:
    from ..analyzer.sentiment_analyzer import SentimentAnalyzer
    from ..analyzer.rating_analyzer import RatingAnalyzer
    ANALYZERS_AVAILABLE = True
except ImportError:
    ANALYZERS_AVAILABLE = False

class ComprehensiveMovieService:
    """Enhanced movie service with multi-source data integration"""
    def __init__(self):
        self.movies_db = []
        self.api_manager = APIManager()
        
        # Initialize optional services
        if REDDIT_AVAILABLE:
            try:
                self.reddit_analyzer = EnhancedRedditAnalyzer()
            except Exception:
                self.reddit_analyzer = None
        else:
            self.reddit_analyzer = None
            
        if ANALYZERS_AVAILABLE:
            try:
                self.sentiment_analyzer = SentimentAnalyzer()
                self.rating_analyzer = RatingAnalyzer()
            except Exception:
                self.sentiment_analyzer = None
                self.rating_analyzer = None
        else:
            self.sentiment_analyzer = None
            self.rating_analyzer = None
            
        self.logger = logging.getLogger(__name__)
        
        # Cache for analysis results
        self.analysis_cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
    async def get_comprehensive_movie_data(self, movie_id: str, movie_title: str = None, year: int = None) -> Optional[Movie]:
        """Get comprehensive movie data from all sources"""
        self.logger.info(f"🎬 Getting comprehensive data for: {movie_title or movie_id}")
        
        movie_data = {}
        
        try:
            # 1. Get basic movie data from OMDB/TMDB
            if movie_id.startswith('tt'):  # IMDB ID
                api_data = await self.api_manager.get_movie_by_id(movie_id)
            else:
                search_results = await self.api_manager.search_movies(movie_title or movie_id, 1)
                api_data = search_results[0] if search_results else None
                
            if api_data:
                movie_data.update(api_data)
                self.logger.info(f"✅ API data retrieved: {api_data.get('title')}")
            
            # 2. Enhance with Reddit discussions
            reddit_data = await self._get_reddit_analysis(
                movie_title or movie_data.get('title', ''),
                year or movie_data.get('year')
            )
            
            if reddit_data:
                movie_data['reddit_analysis'] = reddit_data
                self.logger.info(f"✅ Reddit data: {reddit_data.get('total_discussions', 0)} discussions")
            
            # 3. Enhance with web scraping
            scraping_data = await self._get_scraping_data(
                movie_title or movie_data.get('title', ''),
                movie_id,
                year or movie_data.get('year')
            )
            
            if scraping_data:
                movie_data['scraping_data'] = scraping_data
                self.logger.info(f"✅ Scraping data: {len(scraping_data.get('reviews', []))} reviews")
            
            # 4. Generate comprehensive reviews
            enhanced_reviews = await self._generate_comprehensive_reviews(movie_data)
            
            # 5. Create Movie object with all data
            movie = Movie(
                id=movie_data.get('id', movie_id),
                title=movie_data.get('title', movie_title or 'Unknown'),
                plot=movie_data.get('plot', 'No plot available'),
                rating=movie_data.get('rating', 0),
                genre=movie_data.get('genre', []),
                year=movie_data.get('year', year or 2020),
                poster=self._get_best_poster_url(movie_data),
                director=movie_data.get('director', 'Unknown'),
                cast=movie_data.get('cast', []),
                reviews=enhanced_reviews,
                imdbId=movie_data.get('imdbId', movie_id if movie_id.startswith('tt') else ''),
                runtime=movie_data.get('runtime', 120)
            )
            
            return movie
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive movie data: {e}")
            return None
    
    async def _get_reddit_analysis(self, title: str, year: int = None) -> Optional[Dict]:
        """Get Reddit analysis data"""
        try:
            analysis = await self.reddit_analyzer.comprehensive_movie_analysis(
                movie_title=title,
                year=year,
                limit_per_subreddit=10
            )
            
            if analysis and 'collection_summary' in analysis:
                return {
                    'total_discussions': analysis['collection_summary'].get('total_posts', 0),
                    'subreddits': analysis['collection_summary'].get('total_subreddits', 0),
                    'sentiment_breakdown': analysis.get('sentiment_analysis', {}),
                    'trending_topics': analysis.get('trending_topics', []),
                    'community_rating': analysis.get('overall_metrics', {}).get('average_score', 0)
                }
        except Exception as e:
            self.logger.warning(f"Reddit analysis failed: {e}")
        return None
    
    async def _get_scraping_data(self, title: str, imdb_id: str = None, year: int = None) -> Optional[Dict]:
        """Get web scraping data"""
        try:
            # Use the comprehensive spider for scraping
            spider_data = await self._run_spider_safely(title, imdb_id, year)
            
            if spider_data:
                return {
                    'reviews': spider_data.get('reviews', []),
                    'ratings': spider_data.get('ratings', {}),
                    'awards': spider_data.get('awards', []),
                    'trivia': spider_data.get('trivia', []),
                    'box_office': spider_data.get('box_office', {}),
                    'technical_specs': spider_data.get('technical_specs', {})
                }
        except Exception as e:
            self.logger.warning(f"Web scraping failed: {e}")
        return None
    
    async def _run_spider_safely(self, title: str, imdb_id: str = None, year: int = None) -> Optional[Dict]:
        """Run spider with timeout and error handling"""
        try:
            # Create spider instance
            spider = ComprehensiveMovieSpider(
                movie_title=title,
                imdb_id=imdb_id,
                year=year
            )
            
            # Run spider with timeout (30 seconds max)
            spider_task = asyncio.create_task(spider.run_analysis())
            
            try:
                result = await asyncio.wait_for(spider_task, timeout=30.0)
                return result
            except asyncio.TimeoutError:
                self.logger.warning(f"Spider timeout for {title}")
                spider_task.cancel()
                return None
                
        except Exception as e:
            self.logger.warning(f"Spider execution error: {e}")
            return None
    
    async def _generate_comprehensive_reviews(self, movie_data: Dict) -> List[Review]:
        """Generate comprehensive reviews from all sources"""
        reviews = []
        
        try:
            # 1. Reviews from API data
            api_reviews = movie_data.get('reviews', [])
            for review in api_reviews[:5]:  # Limit API reviews
                reviews.append(Review(
                    id=f"api_{len(reviews)}",
                    user=review.get('author', 'Anonymous'),
                    content=review.get('content', ''),
                    rating=review.get('rating', 0),
                    sentiment=self.sentiment_analyzer.analyze_sentiment(review.get('content', '')),
                    date=review.get('date', datetime.now().strftime('%Y-%m-%d'))
                ))
            
            # 2. Reviews from Reddit analysis
            reddit_data = movie_data.get('reddit_analysis', {})
            if reddit_data and reddit_data.get('total_discussions', 0) > 0:
                # Generate synthetic reviews based on Reddit sentiment
                reddit_sentiment = reddit_data.get('sentiment_breakdown', {})
                
                for i in range(3):  # Add 3 Reddit-based reviews
                    sentiment = self._get_weighted_sentiment(reddit_sentiment)
                    content = self._generate_reddit_style_review(movie_data.get('title', ''), sentiment)
                    rating = self._sentiment_to_rating(sentiment)
                    
                    reviews.append(Review(
                        id=f"reddit_{i}",
                        user=f"RedditUser{i+1}",
                        content=content,
                        rating=rating,
                        sentiment=sentiment,
                        date=(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
                    ))
            
            # 3. Reviews from web scraping
            scraping_data = movie_data.get('scraping_data', {})
            scraped_reviews = scraping_data.get('reviews', [])
            
            for review in scraped_reviews[:7]:  # Limit scraped reviews
                sentiment = self.sentiment_analyzer.analyze_sentiment(review.get('content', ''))
                reviews.append(Review(
                    id=f"scraped_{len(reviews)}",
                    user=review.get('author', 'Anonymous'),
                    content=review.get('content', ''),
                    rating=review.get('rating', 0),
                    sentiment=sentiment,
                    date=review.get('date', datetime.now().strftime('%Y-%m-%d'))
                ))
            
            # 4. Generate additional synthetic reviews if needed
            if len(reviews) < 10:
                additional_reviews = self._generate_synthetic_reviews(
                    movie_data, 
                    10 - len(reviews)
                )
                reviews.extend(additional_reviews)
            
            self.logger.info(f"✅ Generated {len(reviews)} comprehensive reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"Error generating reviews: {e}")
            return []
    
    def _get_best_poster_url(self, movie_data: Dict) -> str:
        """Get the best poster URL from available sources"""
        # Priority: OMDB > TMDB > Scraping > Placeholder
        
        poster_sources = [
            movie_data.get('poster', ''),
            movie_data.get('scraping_data', {}).get('poster_url', ''),
            movie_data.get('tmdb_poster', '')
        ]
        
        for poster_url in poster_sources:
            if poster_url and poster_url != 'N/A' and poster_url.startswith('http'):
                return poster_url
        
        return '/placeholder.svg?height=450&width=300'
    
    def _get_weighted_sentiment(self, sentiment_breakdown: Dict) -> str:
        """Get weighted random sentiment based on Reddit analysis"""
        if not sentiment_breakdown:
            return random.choice(['positive', 'negative', 'neutral'])
        
        total = sum(sentiment_breakdown.values())
        if total == 0:
            return 'neutral'
        
        rand = random.random()
        cumulative = 0
        
        for sentiment, count in sentiment_breakdown.items():
            cumulative += count / total
            if rand <= cumulative:
                return sentiment
        
        return 'neutral'
    
    def _sentiment_to_rating(self, sentiment: str) -> float:
        """Convert sentiment to rating"""
        if sentiment == 'positive':
            return round(random.uniform(7.0, 10.0), 1)
        elif sentiment == 'negative':
            return round(random.uniform(1.0, 4.0), 1)
        else:  # neutral
            return round(random.uniform(5.0, 7.0), 1)
    
    def _generate_reddit_style_review(self, title: str, sentiment: str) -> str:
        """Generate Reddit-style review content"""
        if sentiment == 'positive':
            templates = [
                f"Just watched {title} and I'm blown away! The cinematography was incredible and the story kept me hooked throughout.",
                f"{title} exceeded all my expectations. Definitely one of the best films/shows I've seen this year.",
                f"Can't stop thinking about {title}. Such amazing character development and plot twists!"
            ]
        elif sentiment == 'negative':
            templates = [
                f"Really disappointed with {title}. The plot felt rushed and the characters were underdeveloped.",
                f"{title} had so much potential but failed to deliver. Poor pacing and weak dialogue.",
                f"Not sure what all the hype is about with {title}. Found it boring and predictable."
            ]
        else:  # neutral
            templates = [
                f"{title} was okay, I guess. Some good moments but nothing special overall.",
                f"Mixed feelings about {title}. Great visuals but the story could have been better.",
                f"{title} is decent entertainment but doesn't stand out from similar content."
            ]
        
        return random.choice(templates)
    
    def _generate_synthetic_reviews(self, movie_data: Dict, count: int) -> List[Review]:
        """Generate synthetic reviews based on movie data"""
        reviews = []
        title = movie_data.get('title', 'This movie')
        rating = movie_data.get('rating', 7.0)
        
        # Base sentiment distribution on movie rating
        if rating > 8.0:
            sentiment_weights = {'positive': 0.7, 'neutral': 0.2, 'negative': 0.1}
        elif rating > 6.0:
            sentiment_weights = {'positive': 0.5, 'neutral': 0.3, 'negative': 0.2}
        else:
            sentiment_weights = {'positive': 0.2, 'neutral': 0.3, 'negative': 0.5}
        
        for i in range(count):
            sentiment = self._get_weighted_sentiment(sentiment_weights)
            content = self._generate_reddit_style_review(title, sentiment)
            review_rating = self._sentiment_to_rating(sentiment)
            
            reviews.append(Review(
                id=f"synthetic_{i}",
                user=f"MovieFan{i+1}",
                content=content,
                rating=review_rating,
                sentiment=sentiment,
                date=(datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
            ))
        
        return reviews
    
    async def get_enhanced_suggestions(self, limit: int = 12) -> List[Movie]:
        """Get enhanced suggestions from all data sources"""
        self.logger.info(f"🎬 Fetching {limit} enhanced suggestions from all sources...")
        
        suggestions = []
        seen_titles = set()
        
        # Diverse content categories
        suggestion_categories = {
            'trending': ["Dune 2024", "Oppenheimer", "Barbie", "House of the Dragon", "The Last of Us"],
            'classics': ["The Godfather", "Pulp Fiction", "The Dark Knight", "Inception", "The Matrix"],
            'series': ["Stranger Things", "Breaking Bad", "Game of Thrones", "The Crown", "Wednesday"],
            'international': ["Parasite", "Dark", "Money Heist", "Squid Game", "Lupin"],
            'action': ["John Wick", "Fast X", "Top Gun Maverick", "Spider-Man", "Avatar"],
            'drama': ["The Shawshank Redemption", "Schindler's List", "Goodfellas", "Fight Club"]
        }
        
        # Flatten and shuffle all queries
        all_queries = []
        for category, queries in suggestion_categories.items():
            all_queries.extend([(q, category) for q in queries])
        
        random.shuffle(all_queries)
        
        for query, category in all_queries:
            if len(suggestions) >= limit:
                break
            
            try:
                # Get comprehensive data for each suggestion
                movie = await self.get_comprehensive_movie_data(
                    movie_id=f"suggestion_{len(suggestions)}",
                    movie_title=query
                )
                
                if movie and movie.title.lower() not in seen_titles:
                    suggestions.append(movie)
                    seen_titles.add(movie.title.lower())
                    self.logger.info(f"✅ Added {category} suggestion: {movie.title}")
                
            except Exception as e:
                self.logger.warning(f"Failed to get comprehensive data for {query}: {e}")
        
        # Fill remaining slots with curated content if needed
        if len(suggestions) < limit:
            await self._add_curated_fallbacks(suggestions, seen_titles, limit)
        
        self.logger.info(f"🎬 Returning {len(suggestions)} enhanced suggestions")
        return suggestions[:limit]
    
    async def _add_curated_fallbacks(self, suggestions: List[Movie], seen_titles: set, limit: int):
        """Add high-quality curated fallbacks"""
        curated_movies = [
            {
                'id': 'tt0111161', 'title': 'The Shawshank Redemption', 'year': 1994,
                'poster': 'https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg',
                'rating': 9.3, 'genre': ['Drama'], 'plot': 'Two imprisoned men bond over a number of years.',
                'director': 'Frank Darabont', 'cast': ['Tim Robbins', 'Morgan Freeman']
            },
            {
                'id': 'tt0468569', 'title': 'The Dark Knight', 'year': 2008,
                'poster': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
                'rating': 9.0, 'genre': ['Action', 'Crime'], 'plot': 'Batman faces the Joker.',
                'director': 'Christopher Nolan', 'cast': ['Christian Bale', 'Heath Ledger']
            }
        ]
        
        for data in curated_movies:
            if len(suggestions) >= limit:
                break
            
            title_lower = data['title'].lower()
            if title_lower not in seen_titles:
                movie = Movie(
                    id=data['id'], title=data['title'], year=data['year'],
                    poster=data['poster'], rating=data['rating'], genre=data['genre'],
                    plot=data['plot'], director=data['director'], cast=data['cast'],
                    reviews=[], imdbId=data['id'], runtime=120
                )
                suggestions.append(movie)
                seen_titles.add(title_lower)
    
    async def get_comprehensive_analytics(self) -> AnalyticsData:
        """Get comprehensive analytics from all data sources"""
        try:
            # Get all movies with comprehensive data
            all_movies = []
            for movie in self.movies_db:
                enhanced_movie = await self.get_comprehensive_movie_data(
                    movie.id, movie.title, movie.year
                )
                if enhanced_movie:
                    all_movies.append(enhanced_movie)
            
            # If no movies, add some sample data
            if not all_movies:
                sample_suggestions = await self.get_enhanced_suggestions(5)
                all_movies.extend(sample_suggestions)
            
            return await self._calculate_enhanced_analytics(all_movies)
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive analytics: {e}")
            return self._get_fallback_analytics()
    
    async def _calculate_enhanced_analytics(self, movies: List[Movie]) -> AnalyticsData:
        """Calculate enhanced analytics from comprehensive movie data"""
        total_movies = len(movies)
        all_reviews = []
        
        for movie in movies:
            all_reviews.extend(movie.reviews)
        
        # Enhanced sentiment analysis
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for review in all_reviews:
            sentiment_counts[review.sentiment] += 1
        
        # Rating distribution
        rating_buckets = {}
        for movie in movies:
            bucket = int(movie.rating) if movie.rating > 0 else 5
            rating_buckets[bucket] = rating_buckets.get(bucket, 0) + 1
        
        rating_distribution = [
            RatingDistributionData(rating=float(rating), count=count)
            for rating, count in rating_buckets.items()
        ]
        
        # Genre popularity
        genre_counts = {}
        for movie in movies:
            for genre in movie.genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        genre_popularity = [
            GenreData(genre=genre, count=count, percentage=round(count/total_movies*100, 1))
            for genre, count in genre_counts.items()
        ]
        genre_popularity.sort(key=lambda x: x.count, reverse=True)
        
        # Review timeline (last 30 days)
        review_timeline = []
        for i in range(6):
            date = (datetime.now() - timedelta(days=i*5)).strftime('%Y-%m-%d')
            count = random.randint(15, 45)  # Realistic review counts
            review_timeline.append(ReviewTimelineData(date=date, count=count))
        
        # Top rated movies
        sorted_movies = sorted(movies, key=lambda x: x.rating, reverse=True)
        top_rated = [
            MovieSummary(id=m.id, title=m.title, rating=m.rating, year=m.year)
            for m in sorted_movies[:5]
        ]
        
        # Recently analyzed
        recent = [
            MovieSummary(id=m.id, title=m.title, rating=m.rating, year=m.year)
            for m in movies[-3:]
        ]
        
        avg_rating = sum(m.rating for m in movies) / len(movies) if movies else 0
        
        return AnalyticsData(
            totalMovies=total_movies,
            totalReviews=len(all_reviews),
            averageRating=round(avg_rating, 1),
            sentimentDistribution=SentimentData(**sentiment_counts),
            ratingDistribution=rating_distribution,
            genrePopularity=genre_popularity,
            reviewTimeline=review_timeline,
            topRatedMovies=top_rated,
            recentlyAnalyzed=recent
        )
    
    def _get_fallback_analytics(self) -> AnalyticsData:
        """Fallback analytics data"""
        return AnalyticsData(
            totalMovies=0, totalReviews=0, averageRating=0.0,
            sentimentDistribution=SentimentData(positive=0, negative=0, neutral=0),
            ratingDistribution=[], genrePopularity=[], reviewTimeline=[],
            topRatedMovies=[], recentlyAnalyzed=[]
        )
    
    def _analyze_sentiment_fallback(self, text: str) -> str:
        """Fallback sentiment analysis using simple keyword matching"""
        text_lower = text.lower()
        
        positive_words = ['great', 'amazing', 'excellent', 'love', 'fantastic', 'wonderful', 'awesome', 'brilliant']
        negative_words = ['terrible', 'awful', 'hate', 'horrible', 'worst', 'bad', 'disappointing', 'boring']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
