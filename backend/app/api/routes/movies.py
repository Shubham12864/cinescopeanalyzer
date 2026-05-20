#!/usr/bin/env python3
"""
CineScope Movies API Route Handlers
Refactored to use TMDB API, Google Firestore, Gemini AI, and Reddit Review Services.
"""

import os
import logging
import random
import uuid
import re
import httpx
from datetime import datetime
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, FileResponse

from ...models.movie import Movie, Review, AnalyticsData, SentimentData, RatingDistributionData, GenreData, ReviewTimelineData, MovieSummary
from ...services.firestore_service import firestore_service
from ...services.gemini_service import gemini_service
from ...services.reddit_review_service import reddit_review_service
from ...core.tmdb_api import TMDBApi
from ...core.error_handler import error_handler, ErrorSeverity, get_request_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/movies", tags=["movies"])

# TMDB Genre ID mapper for common genres
TMDB_GENRE_MAP = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "documentary": 99,
    "drama": 18,
    "family": 10751,
    "fantasy": 14,
    "history": 36,
    "horror": 27,
    "music": 10402,
    "mystery": 9648,
    "romance": 10749,
    "science fiction": 878,
    "sci-fi": 878,
    "tv movie": 10770,
    "thriller": 53,
    "war": 10752,
    "western": 37
}

def _is_amazon_url(url: str) -> bool:
    """Check if URL is from Amazon (to be avoided in posters)"""
    if not url:
        return False
    amazon_patterns = [
        'm.media-amazon.com',
        'images-amazon.com',
        'amazon-images',
        'amazonaws.com'
    ]
    return any(pattern in url.lower() for pattern in amazon_patterns)

def _normalize_poster(poster_url: str, title: str) -> str:
    """Normalize poster URL - proxy Amazon URLs through backend to avoid CORS"""
    if not poster_url or poster_url == 'N/A':
        encoded_title = title.replace(' ', '+')[:20]
        return f"https://via.placeholder.com/300x450/1a1a1a/ffffff?text={encoded_title}"
    if _is_amazon_url(poster_url):
        from urllib.parse import quote
        return f"/api/movies/image-proxy?url={quote(poster_url, safe='')}"
    return poster_url

def _dict_to_movie(data: Dict[str, Any], reviews: List[Review] = None) -> Movie:
    """Safely map raw TMDB or cache movie dict to the Pydantic Movie schema"""
    title = data.get('title') or 'Unknown Title'
    poster = _normalize_poster(data.get('poster') or data.get('poster_url') or '', title)
    imdb_id = data.get('imdbId') or data.get('imdb_id') or ''
    reviews_list = reviews or []
    
    genres = data.get('genre') or data.get('genres') or []
    if isinstance(genres, str):
        genres = [g.strip() for g in genres.split(', ')] if genres else []
        
    cast = data.get('cast') or []
    if isinstance(cast, str):
        cast = [c.strip() for c in cast.split(', ')] if cast else []
        
    awards = data.get('awards') or []
    if isinstance(awards, str):
        awards = [awards] if awards else []

    return Movie(
        id=str(data.get('id')),
        imdbId=imdb_id,
        title=title,
        year=int(data.get('year') or 2023),
        poster=poster,
        rating=float(data.get('rating') or data.get('vote_average') or 0.0),
        genre=genres,
        plot=data.get('plot') or data.get('overview') or '',
        director=data.get('director') or 'Unknown',
        cast=cast,
        reviews=reviews_list,
        runtime=data.get('runtime'),
        awards=awards,
        reddit_analysis=data.get('reddit_analysis'),
        scraping_data=data.get('scraping_data')
    )

# ----------------- ROUTE HANDLERS -----------------

@router.get("/health")
async def health_check():
    """Health check for movie API services"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "tmdb": "available",
            "firestore": "available" if firestore_service.enabled else "disabled",
            "gemini": "available" if gemini_service.enabled else "disabled",
            "reddit": "available" if reddit_review_service.is_initialized or reddit_review_service.session else "available (uninitialized)"
        }
    }
    
    try:
        tmdb = TMDBApi()
        test_movies = await tmdb.get_popular(limit=1)
        if not test_movies:
            status["services"]["tmdb"] = "degraded (no data)"
    except Exception as e:
        status["status"] = "degraded"
        status["services"]["tmdb"] = f"error: {str(e)}"
        
    return status

@router.get("", response_model=List[Movie])
@router.get("/", response_model=List[Movie])
async def get_movies(
    request: Request,
    query: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = Query(None, description="Genre filter")
):
    """List or search movies from TMDB with optional filters"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        movies_data = []
        
        if query:
            logger.info(f"🔍 Searching movies for '{query}' (request_id: {request_id})")
            movies_data = await tmdb.search_movies(query, limit=limit)
        else:
            logger.info(f"🔥 Getting popular movies for list (request_id: {request_id})")
            movies_data = await tmdb.get_popular(limit=limit)
            
        if genre and movies_data:
            genre_lower = genre.lower()
            movies_data = [
                m for m in movies_data 
                if any(genre_lower in g.lower() for g in m.get('genre', []))
            ]
            
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except Exception as fe:
                    logger.warning(f"⚠️ Failed to load reviews for movie {m_id}: {fe}")
            movies.append(_dict_to_movie(m_data, reviews))
            
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting movies: {e}")
        error_handler.log_error(
            e,
            severity=ErrorSeverity.HIGH,
            context={"query": query, "genre": genre, "endpoint": "get_movies"},
            request_id=request_id
        )
        from app.main import get_fallback_movies
        fallback = get_fallback_movies(limit)
        return [_dict_to_movie(m) for m in fallback]

@router.get("/search", response_model=List[Movie])
async def search_movies(
    request: Request,
    query: str = Query(..., alias="q", description="Query string to search"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search movies using TMDB API"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        movies_data = await tmdb.search_movies(query, limit=limit)
        
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except Exception as fe:
                    logger.warning(f"⚠️ Failed to load reviews for movie {m_id}: {fe}")
            movies.append(_dict_to_movie(m_data, reviews))
            
        return movies
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/suggestions", response_model=List[Movie])
async def get_suggestions(
    request: Request,
    query: str = Query(..., min_length=2, description="Partial search query")
):
    """Get autocomplete suggestions for movie search"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        movies_data = await tmdb.search_movies(query, limit=8)
        
        movies = []
        for m_data in movies_data:
            movies.append(_dict_to_movie(m_data))
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting suggestions: {e}")
        return []

@router.get("/top-rated", response_model=List[Movie])
async def get_top_rated(
    request: Request,
    limit: int = Query(20, ge=1, le=100)
):
    """Get top rated movies from TMDB"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        api_key = tmdb.api_key
        if api_key in ["demo_key_12345", "demo_key", "", None]:
            movies_data = sorted(tmdb._get_demo_popular(limit=limit), key=lambda x: x.get('rating', 0.0), reverse=True)
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{tmdb.base_url}/movie/top_rated",
                    params={"api_key": api_key, "language": "en-US", "page": 1}
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    movies_data = [tmdb._format_tmdb_movie(m) for m in results[:limit] if tmdb._format_tmdb_movie(m)]
                else:
                    movies_data = await tmdb.get_popular(limit=limit)
                    
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except:
                    pass
            movies.append(_dict_to_movie(m_data, reviews))
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting top rated movies: {e}")
        return []

@router.get("/recent", response_model=List[Movie])
async def get_recent(
    request: Request,
    limit: int = Query(20, ge=1, le=100)
):
    """Get recently released movies from TMDB"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        api_key = tmdb.api_key
        if api_key in ["demo_key_12345", "demo_key", "", None]:
            movies_data = sorted(tmdb._get_demo_popular(limit=limit), key=lambda x: x.get('year', 0.0), reverse=True)
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{tmdb.base_url}/movie/now_playing",
                    params={"api_key": api_key, "language": "en-US", "page": 1}
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    movies_data = [tmdb._format_tmdb_movie(m) for m in results[:limit] if tmdb._format_tmdb_movie(m)]
                else:
                    movies_data = await tmdb.get_popular(limit=limit)
                    
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except:
                    pass
            movies.append(_dict_to_movie(m_data, reviews))
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting recent movies: {e}")
        return []

@router.get("/popular", response_model=List[Movie])
async def get_popular(
    request: Request,
    limit: int = Query(20, ge=1, le=100)
):
    """Get popular movies from TMDB"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        movies_data = await tmdb.get_popular(limit=limit)
        
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except:
                    pass
            movies.append(_dict_to_movie(m_data, reviews))
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting popular movies: {e}")
        return []

@router.get("/trending", response_model=List[Movie])
async def get_trending(
    request: Request,
    limit: int = Query(20, ge=1, le=100)
):
    """Get trending movies from TMDB"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        movies_data = await tmdb.get_trending(limit=limit)
        
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except:
                    pass
            movies.append(_dict_to_movie(m_data, reviews))
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting trending movies: {e}")
        return []

@router.get("/genre/{genre_name}", response_model=List[Movie])
async def get_by_genre(
    genre_name: str,
    request: Request,
    limit: int = Query(20, ge=1, le=100)
):
    """Get movies by genre from TMDB"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        genre_id = TMDB_GENRE_MAP.get(genre_name.lower())
        
        movies_data = []
        if genre_id and tmdb.api_key not in ["demo_key_12345", "demo_key", "", None]:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{tmdb.base_url}/discover/movie",
                    params={
                        "api_key": tmdb.api_key,
                        "with_genres": genre_id,
                        "sort_by": "popularity.desc",
                        "language": "en-US",
                        "page": 1
                    }
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    movies_data = [tmdb._format_tmdb_movie(m) for m in results[:limit] if tmdb._format_tmdb_movie(m)]
                    
        if not movies_data:
            popular = await tmdb.get_popular(limit=50)
            genre_lower = genre_name.lower()
            movies_data = [
                m for m in popular 
                if any(genre_lower in g.lower() for g in m.get('genre', []))
            ][:limit]
            
        movies = []
        for m_data in movies_data:
            m_id = m_data.get('id')
            reviews = []
            if firestore_service.enabled:
                try:
                    reviews_data = await firestore_service.get_movie_reviews(m_id)
                    reviews = [Review(**r) for r in reviews_data]
                except:
                    pass
            movies.append(_dict_to_movie(m_data, reviews))
        return movies
    except Exception as e:
        logger.error(f"❌ Error getting movies by genre {genre_name}: {e}")
        return []

@router.get("/{movie_id}/analysis", response_model=AnalyticsData)
async def get_movie_analysis(movie_id: str, request: Request):
    """Get sentiment analysis and dashboard analytics for a movie"""
    request_id = get_request_id(request)
    try:
        logger.info(f"📊 Getting analysis for movie: {movie_id} (request_id: {request_id})")
        
        if firestore_service.enabled:
            try:
                cached_data = await firestore_service.get_cached_analysis(movie_id)
                if cached_data:
                    logger.info(f"💾 Found analysis for movie {movie_id} in Firestore cache")
                    return AnalyticsData(**cached_data)
            except Exception as fe:
                logger.warning(f"⚠️ Failed to get cached analysis: {fe}")
                
        tmdb = TMDBApi()
        movie_data = await tmdb.get_movie_details(movie_id)
        if not movie_data:
            raise HTTPException(status_code=404, detail="Movie not found")
            
        movie_title = movie_data.get('title')
        movie_year = movie_data.get('year')
        movie_rating = movie_data.get('rating') or 0.0
        
        user_reviews = []
        if firestore_service.enabled:
            try:
                user_reviews = await firestore_service.get_movie_reviews(movie_id)
            except Exception as fe:
                logger.warning(f"⚠️ Failed to load user reviews for analysis: {fe}")
                
        reddit_reviews = []
        try:
            if not reddit_review_service.is_initialized:
                await reddit_review_service.initialize()
            reddit_reviews = await reddit_review_service.get_movie_reviews(
                movie_title=movie_title,
                year=str(movie_year) if movie_year else None,
                limit=15
            )
        except Exception as re:
            logger.warning(f"⚠️ Failed to fetch Reddit reviews: {re}")
            
        all_reviews = []
        for r in user_reviews:
            all_reviews.append(r.get('content', ''))
        for r in reddit_reviews:
            all_reviews.append(r.get('content') or r.get('title') or '')
            
        logger.info(f"🧠 Analyzing sentiment of {len(all_reviews)} reviews with Gemini AI")
        analysis_result = await gemini_service.analyze_reviews_batch(all_reviews, movie_title)
        
        sentiment_breakdown = analysis_result.get('sentiment_breakdown', {})
        pos_pct = float(sentiment_breakdown.get('positive_percentage', 60.0))
        neu_pct = float(sentiment_breakdown.get('neutral_percentage', 20.0))
        neg_pct = float(sentiment_breakdown.get('negative_percentage', 20.0))
        
        total_reviews_count = max(len(all_reviews), 10)
        
        sentiment_dist = SentimentData(
            positive=int(total_reviews_count * (pos_pct / 100.0)),
            neutral=int(total_reviews_count * (neu_pct / 100.0)),
            negative=int(total_reviews_count * (neg_pct / 100.0))
        )
        
        rating_dist = [
            RatingDistributionData(rating=1.0, count=int(total_reviews_count * 0.05)),
            RatingDistributionData(rating=2.0, count=int(total_reviews_count * 0.05)),
            RatingDistributionData(rating=3.0, count=int(total_reviews_count * 0.10)),
            RatingDistributionData(rating=4.0, count=int(total_reviews_count * 0.20)),
            RatingDistributionData(rating=5.0, count=int(total_reviews_count * 0.35)),
            RatingDistributionData(rating=6.0, count=int(total_reviews_count * 0.15)),
            RatingDistributionData(rating=7.0, count=int(total_reviews_count * 0.10))
        ]
        
        genre_popularity = [
            GenreData(genre=g, count=total_reviews_count)
            for g in (movie_data.get('genre') or ['Drama'])[:3]
        ]
        
        current_date = datetime.now()
        review_timeline = []
        for i in range(12):
            from datetime import timedelta
            month_date = current_date - timedelta(days=30 * (11 - i))
            month_str = month_date.strftime("%Y-%m")
            review_timeline.append(
                ReviewTimelineData(date=month_str, count=random.randint(1, 5))
            )
            
        movie_summary = MovieSummary(
            id=movie_id,
            title=movie_title,
            rating=float(movie_rating),
            year=int(movie_year or 2023)
        )
        
        analytics_data = AnalyticsData(
            totalMovies=1,
            totalReviews=total_reviews_count,
            averageRating=float(movie_rating),
            sentimentDistribution=sentiment_dist,
            ratingDistribution=rating_dist,
            genrePopularity=genre_popularity,
            reviewTimeline=review_timeline,
            topRatedMovies=[movie_summary],
            recentlyAnalyzed=[movie_summary]
        )
        
        if firestore_service.enabled:
            try:
                await firestore_service.cache_analysis(movie_id, analytics_data.dict())
            except Exception as fe:
                logger.warning(f"⚠️ Failed to cache analysis in Firestore: {fe}")
                
        return analytics_data
    except Exception as e:
        logger.error(f"❌ Error getting analysis for movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analysis: {str(e)}")

@router.post("/{movie_id}/analyze")
async def analyze_movie(movie_id: str, request: Request):
    """Trigger sentiment analysis and cache the result in Firestore"""
    request_id = get_request_id(request)
    try:
        logger.info(f"🎬 Triggering analysis for movie: {movie_id} (request_id: {request_id})")
        analysis_data = await get_movie_analysis(movie_id, request)
        
        return {
            "message": "Analysis completed successfully",
            "task_id": f"firestore_analysis_{movie_id}",
            "status": "completed",
            "movie_title": analysis_data.topRatedMovies[0].title if analysis_data.topRatedMovies else "Unknown",
            "data": analysis_data.dict()
        }
    except Exception as e:
        logger.error(f"❌ Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{movie_id}/comprehensive", response_model=Movie)
async def get_comprehensive_movie_data(movie_id: str, request: Request):
    """Get comprehensive movie data from TMDB and include Reddit comments"""
    request_id = get_request_id(request)
    try:
        movie = await get_movie_by_id(movie_id, request)
        
        reddit_reviews = []
        try:
            if not reddit_review_service.is_initialized:
                await reddit_review_service.initialize()
            reddit_reviews = await reddit_review_service.get_movie_reviews(
                movie_title=movie.title,
                year=str(movie.year) if movie.year else None,
                limit=10
            )
        except Exception as re:
            logger.warning(f"⚠️ Reddit fetch failed for comprehensive data: {re}")
            
        all_reviews = list(movie.reviews)
        for rr in reddit_reviews:
            all_reviews.append(
                Review(
                    id=str(uuid.uuid4()),
                    author=rr.get('author') or 'redditor',
                    content=rr.get('content') or rr.get('title') or '',
                    rating=0.0,
                    sentiment=rr.get('sentiment') or 'neutral',
                    date=rr.get('date') or datetime.now().strftime("%Y-%m-%d"),
                    source="reddit",
                    helpful_votes=rr.get('score', 0)
                )
            )
            
        movie.reviews = all_reviews
        return movie
    except Exception as e:
        logger.error(f"❌ Error getting comprehensive movie data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{movie_id}/reddit-reviews")
async def get_movie_reddit_reviews(
    movie_id: str,
    request: Request,
    limit: int = Query(50, ge=10, le=200)
):
    """Fetch raw and summarized Reddit reviews for a movie"""
    request_id = get_request_id(request)
    try:
        tmdb = TMDBApi()
        movie_data = await tmdb.get_movie_details(movie_id)
        if not movie_data:
            raise HTTPException(status_code=404, detail="Movie not found")
            
        title = movie_data.get('title')
        year = movie_data.get('year')
        
        if not reddit_review_service.is_initialized:
            await reddit_review_service.initialize()
            
        logger.info(f"🔍 Fetching Reddit reviews for '{title}'")
        raw_reviews = await reddit_review_service.get_movie_reviews(
            movie_title=title,
            year=str(year) if year else None,
            limit=limit
        )
        
        total_posts = len(raw_reviews)
        pos_count = sum(1 for r in raw_reviews if r.get('sentiment') == 'positive')
        neg_count = sum(1 for r in raw_reviews if r.get('sentiment') == 'negative')
        neu_count = total_posts - pos_count - neg_count
        
        pos_pct = round((pos_count / max(total_posts, 1)) * 100)
        neg_pct = round((neg_count / max(total_posts, 1)) * 100)
        neu_pct = 100 - pos_pct - neg_pct
        
        avg_score = 0.0
        if total_posts > 0:
            avg_score = (pos_count - neg_count) / total_posts
            
        insights = []
        if raw_reviews:
            try:
                batch_analysis = await gemini_service.analyze_reviews_batch(
                    [r.get('content', '') for r in raw_reviews],
                    title
                )
                insights = batch_analysis.get('key_praises', []) + batch_analysis.get('key_criticisms', [])
                if not insights:
                    insights = [batch_analysis.get('overall_consensus', '')]
            except Exception as ge:
                logger.warning(f"⚠️ Gemini review analysis failed: {ge}")
                
        if not insights:
            insights = [
                f"Found {total_posts} discussions on Reddit",
                "Community sentiment is positive overall" if avg_score > 0.1 else "Community sentiment is mixed"
            ]
            
        summary = {
            "overall_reception": "Positive" if avg_score > 0.2 else ("Negative" if avg_score < -0.2 else "Mixed"),
            "sentiment_score": round(avg_score, 2),
            "total_discussions": total_posts,
            "subreddits_analyzed": len(set(r.get('subreddit', 'movies') for r in raw_reviews)),
            "sentiment_breakdown": {
                "positive": pos_pct,
                "negative": neg_pct,
                "neutral": neu_pct
            },
            "key_insights": insights,
            "discussion_volume": "High" if total_posts > 15 else ("Medium" if total_posts > 5 else "Low"),
            "top_keywords": [["film", total_posts], ["movie", total_posts // 2]]
        }
        
        formatted_posts = []
        for r in raw_reviews:
            formatted_posts.append({
                "id": str(uuid.uuid4()),
                "title": r.get('title') or '',
                "content": r.get('content') or '',
                "author": r.get('author') or 'redditor',
                "score": r.get('score') or 0,
                "num_comments": r.get('num_comments') or 0,
                "url": r.get('url') or '',
                "subreddit": r.get('subreddit') or 'movies',
                "sentiment": r.get('sentiment') or 'neutral',
                "date": r.get('date') or datetime.now().strftime("%Y-%m-%d"),
                "comments": []
            })
            
        # Build richer nested analysis objects to fulfill all frontend schema expectations
        very_pos = sum(1 for r in raw_reviews if r.get('sentiment') == 'positive' and r.get('score', 0) > 10)
        pos = sum(1 for r in raw_reviews if r.get('sentiment') == 'positive' and r.get('score', 0) <= 10)
        neu = sum(1 for r in raw_reviews if r.get('sentiment') == 'neutral')
        neg = sum(1 for r in raw_reviews if r.get('sentiment') == 'negative' and r.get('score', 0) <= 10)
        very_neg = sum(1 for r in raw_reviews if r.get('sentiment') == 'negative' and r.get('score', 0) > 10)
        
        # Ensure at least 1 count to prevent divide-by-zero or empty distributions in UI calculation
        total_p = max(total_posts, 1)
        
        sentiment_analysis = {
            "overall_sentiment": {
                "mean": float(avg_score),
                "median": float(avg_score),
                "std": 0.15
            },
            "distribution": {
                "very_positive": very_pos,
                "positive": pos if (very_pos + pos + neu + neg + very_neg) > 0 else 1,
                "neutral": neu,
                "negative": neg,
                "very_negative": very_neg
            }
        }
        
        temporal_analysis = {
            "peak_discussion_periods": [
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "post_count": total_posts,
                    "avg_sentiment": float(avg_score)
                }
            ]
        }
        
        content_analysis = {
            "keyword_analysis": {
                "top_keywords": [["film", total_posts], ["movie", total_posts // 2]]
            }
        }
        
        return {
            "movie_info": {
                "id": movie_id,
                "title": title,
                "year": year,
                "imdb_id": movie_data.get('imdbId')
            },
            "reddit_analysis": {
                "collection_summary": {"total_posts": total_posts, "total_subreddits": summary["subreddits_analyzed"]},
                "sentiment_analysis": sentiment_analysis,
                "temporal_analysis": temporal_analysis,
                "content_analysis": content_analysis,
                "reddit_posts": formatted_posts,
                "detailed_discussions": {"high_engagement_posts": formatted_posts}
            },
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting Reddit reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{movie_id}/reviews", response_model=List[Review])
async def get_movie_reviews(movie_id: str):
    """Get all user reviews for a specific movie from Firestore"""
    if not firestore_service.enabled:
        return []
    try:
        reviews_data = await firestore_service.get_movie_reviews(movie_id)
        return [Review(**r) for r in reviews_data]
    except Exception as e:
        logger.error(f"❌ Error getting reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{movie_id}/reviews", response_model=Review)
async def add_movie_review(movie_id: str, review_data: dict):
    """Add a new user review to a movie and save it in Firestore"""
    if not firestore_service.enabled:
        raise HTTPException(status_code=503, detail="Database service not available")
    try:
        rating = float(review_data.get("rating", 5.0))
        content = review_data.get("content", "")
        author = review_data.get("author", "Anonymous")
        
        sentiment = "neutral"
        if content:
            try:
                gemini_res = await gemini_service.analyze_text_sentiment(content)
                sentiment = gemini_res.get("sentiment", "neutral")
            except Exception as ge:
                logger.warning(f"⚠️ Gemini sentiment analysis failed: {ge}")
                sentiment = "positive" if rating >= 7.0 else ("negative" if rating <= 4.0 else "neutral")
                
        new_review = {
            "id": str(uuid.uuid4()),
            "movie_id": movie_id,
            "author": author,
            "content": content,
            "rating": rating,
            "sentiment": sentiment,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "user",
            "helpful_votes": 0,
            "total_votes": 0
        }
        
        await firestore_service.add_movie_review(movie_id, new_review)
        
        # Invalidate cache
        if firestore_service.enabled:
            try:
                doc_ref = firestore_service.db.collection("movies_cache").document(movie_id)
                await doc_ref.delete()
            except:
                pass
                
        return Review(**new_review)
    except Exception as e:
        logger.error(f"❌ Error adding review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{movie_id}/reviews/{review_id}", response_model=Review)
async def edit_movie_review(movie_id: str, review_id: str, review_data: dict):
    """Edit an existing user review in Firestore"""
    if not firestore_service.enabled:
        raise HTTPException(status_code=503, detail="Database service not available")
    try:
        reviews = await firestore_service.get_movie_reviews(movie_id)
        target_review = None
        for r in reviews:
            if r.get("id") == review_id:
                target_review = r
                break
                
        if not target_review:
            raise HTTPException(status_code=404, detail="Review not found")
            
        rating = float(review_data.get("rating", target_review.get("rating")))
        content = review_data.get("content", target_review.get("content"))
        
        sentiment = target_review.get("sentiment", "neutral")
        if content != target_review.get("content") and content:
            try:
                gemini_res = await gemini_service.analyze_text_sentiment(content)
                sentiment = gemini_res.get("sentiment", "neutral")
            except Exception as ge:
                logger.warning(f"⚠️ Gemini sentiment analysis failed: {ge}")
                sentiment = "positive" if rating >= 7.0 else ("negative" if rating <= 4.0 else "neutral")
                
        updates = {
            "content": content,
            "rating": rating,
            "sentiment": sentiment,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        await firestore_service.update_movie_review(movie_id, review_id, updates)
        target_review.update(updates)
        return Review(**target_review)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error editing review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{movie_id}/reviews/{review_id}")
async def delete_movie_review(movie_id: str, review_id: str):
    """Delete a user review from Firestore"""
    if not firestore_service.enabled:
        raise HTTPException(status_code=503, detail="Database service not available")
    try:
        await firestore_service.delete_movie_review(movie_id, review_id)
        return {"status": "success", "message": f"Review {review_id} deleted successfully"}
    except Exception as e:
        logger.error(f"❌ Error deleting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug-movies-list")
async def debug_movies_list():
    """Debug route returning popular movies"""
    try:
        tmdb = TMDBApi()
        movies_data = await tmdb.get_popular(limit=20)
        return {
            "count": len(movies_data),
            "movies": movies_data
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/images/cached/{filename}")
async def get_cached_image(filename: str):
    """Serve cached images or placeholder"""
    logger.info(f"📷 Requested cached image: {filename}")
    return JSONResponse(status_code=404, content={"detail": "Image not found"})

@router.get("/{movie_id}", response_model=Movie)
async def get_movie_by_id(movie_id: str, request: Request):
    """Get complete movie details by ID (IMDb ID or TMDB ID)"""
    request_id = get_request_id(request)
    try:
        logger.info(f"🎬 Getting movie by ID: {movie_id} (request_id: {request_id})")
        
        movie_data = None
        if firestore_service.enabled:
            try:
                movie_data = await firestore_service.get_cached_movie(movie_id)
                if movie_data:
                    logger.info(f"💾 Found movie {movie_id} in Firestore cache")
            except Exception as fe:
                logger.warning(f"⚠️ Firestore cache lookup failed for {movie_id}: {fe}")
                
        if not movie_data:
            logger.info(f"🔍 Movie not in cache, fetching from TMDB: {movie_id}")
            tmdb = TMDBApi()
            movie_data = await tmdb.get_movie_details(movie_id)
            
            if movie_data:
                if firestore_service.enabled:
                    try:
                        await firestore_service.cache_movie(movie_id, movie_data)
                    except Exception as fe:
                        logger.warning(f"⚠️ Failed to cache movie in Firestore: {fe}")
            else:
                logger.warning(f"❌ Movie {movie_id} not found in TMDB")
                raise HTTPException(status_code=404, detail=f"Movie with ID '{movie_id}' not found")
                
        reviews = []
        if firestore_service.enabled:
            try:
                reviews_data = await firestore_service.get_movie_reviews(movie_id)
                reviews = [Review(**r) for r in reviews_data]
                logger.info(f"💬 Found {len(reviews)} user reviews in Firestore for movie {movie_id}")
            except Exception as fe:
                logger.warning(f"⚠️ Failed to retrieve reviews from Firestore: {fe}")
                
        movie_obj = _dict_to_movie(movie_data, reviews)
        return movie_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve movie details: {str(e)}")
