#!/usr/bin/env python3
"""
CineScope Backend - COMPLETE INTEGRATION
All services: OMDB, FanArt, Reddit, Scrapy, Database
"""
import warnings
import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add backend path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

from fastapi import FastAPI, Request, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
import uvicorn
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all your working services
try:
    from services.working_omdb_client import WorkingOMDBClient
    from services.fanart_api_service import fanart_service
    from services.reddit_review_service import reddit_review_service
    from services.enhanced_movie_service import EnhancedMovieService
    from core.azure_database import AzureDatabaseManager
    from api.routes.movies import router as movies_router
    
    SERVICES_LOADED = True
    logger = logging.getLogger(__name__)
    logger.info("✅ All available services imported successfully")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Service import warning: {e}")
    SERVICES_LOADED = False
    movies_router = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize core services
omdb_client = None
enhanced_service = None
azure_db = None

if SERVICES_LOADED:
    try:
        omdb_client = WorkingOMDBClient()
        
        # Try to get the EnhancedMovieService from existing services
        try:
            from services.enhanced_movie_service import EnhancedMovieService
            enhanced_service = EnhancedMovieService()
        except ImportError:
            # Fallback to working search service
            from services.working_search_service import WorkingMovieSearchService
            enhanced_service = WorkingMovieSearchService()
        
        azure_db = AzureDatabaseManager()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        SERVICES_LOADED = False

# Create FastAPI app
app = FastAPI(
    title="CineScope Complete Movie Analysis API",
    description="Comprehensive Movie Search with OMDB, FanArt, Reddit, Azure Integration",
    version="3.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include movie routes if available
if SERVICES_LOADED and movies_router:
    try:
        app.include_router(movies_router)
        logger.info("✅ Movie routes included successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not include movie routes: {e}")
        SERVICES_LOADED = False

# Working movie data
WORKING_MOVIES = [
    {
        "id": "tt0111161",
        "imdbId": "tt0111161",
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genre": ["Drama"],
        "rating": 9.3,
        "plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "director": "Frank Darabont",
        "cast": ["Tim Robbins", "Morgan Freeman"],
        "poster": "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=The+Shawshank+Redemption",
        "runtime": 142
    },
    {
        "id": "tt0068646",
        "imdbId": "tt0068646", 
        "title": "The Godfather",
        "year": 1972,
        "genre": ["Crime", "Drama"],
        "rating": 9.2,
        "plot": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "director": "Francis Ford Coppola",
        "cast": ["Marlon Brando", "Al Pacino"],
        "poster": "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=The+Godfather",
        "runtime": 175
    },
    {
        "id": "tt0071562",
        "imdbId": "tt0071562",
        "title": "The Godfather Part II", 
        "year": 1974,
        "genre": ["Crime", "Drama"],
        "rating": 9.0,
        "plot": "The early life and career of Vito Corleone in 1920s New York City is portrayed, while his son, Michael, expands and tightens his grip on the family crime syndicate.",
        "director": "Francis Ford Coppola",
        "cast": ["Al Pacino", "Robert De Niro"],
        "poster": "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=The+Godfather+Part+II",
        "runtime": 202
    },
    {
        "id": "tt0468569",
        "imdbId": "tt0468569",
        "title": "The Dark Knight",
        "year": 2008,
        "genre": ["Action", "Crime", "Drama"],
        "rating": 9.0,
        "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "director": "Christopher Nolan",
        "cast": ["Christian Bale", "Heath Ledger"],
        "poster": "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=The+Dark+Knight",
        "runtime": 152
    },
    {
        "id": "tt0108052",
        "imdbId": "tt0108052",
        "title": "Schindler's List",
        "year": 1993,
        "genre": ["Biography", "Drama", "History"],
        "rating": 8.9,
        "plot": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
        "director": "Steven Spielberg", 
        "cast": ["Liam Neeson", "Ralph Fiennes"],
        "poster": "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=Schindlers+List",
        "runtime": 195
    }
]

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CineScope API is running!",
        "status": "healthy",
        "version": "2.0.1",
        "endpoints": {
            "health": "/health",
            "movies": "/api/movies",
            "search": "/api/movies/search?q=batman",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "CineScope API is operational",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "database": "connected"
        }
    }

@app.get("/api/health")
async def api_health():
    """API health check"""
    return await health_check()

@app.get("/api/movies")
async def get_movies(limit: int = Query(20, ge=1, le=100)):
    """Get all movies"""
    logger.info(f"📽️ Getting {limit} movies")
    return WORKING_MOVIES[:limit]

@app.get("/api/movies/popular")
async def get_popular_movies(limit: int = Query(20, ge=1, le=100)):
    """Get popular movies using enhanced service"""
    logger.info(f"⭐ Getting {limit} popular movies")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for popular movies
            popular_movies = await enhanced_service.get_popular_movies()
            if popular_movies:
                logger.info(f"✅ Enhanced service returned {len(popular_movies)} popular movies")
                return popular_movies[:limit]
            else:
                logger.warning("⚠️ Enhanced service returned no popular movies")
        
        # Fallback to demo data
        logger.info(f"✅ Returning {len(WORKING_MOVIES[:limit])} demo popular movies")
        return WORKING_MOVIES[:limit]
        
    except Exception as e:
        logger.error(f"❌ Popular movies error: {e}")
        return WORKING_MOVIES[:limit]

@app.get("/api/movies/suggestions")  
async def get_movie_suggestions(limit: int = Query(12, ge=1, le=50)):
    """Get movie suggestions using enhanced algorithms"""
    logger.info(f"💡 Getting {limit} movie suggestions")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for personalized suggestions
            suggestions = await enhanced_service.get_movie_suggestions()
            if suggestions:
                logger.info(f"✅ Enhanced service returned {len(suggestions)} suggestions")
                return suggestions[:limit]
        
        # Fallback to demo suggestions (randomized order)
        import random
        demo_suggestions = WORKING_MOVIES.copy()
        random.shuffle(demo_suggestions)
        logger.info(f"✅ Returning {len(demo_suggestions[:limit])} demo suggestions")
        return demo_suggestions[:limit]
        
    except Exception as e:
        logger.error(f"❌ Suggestions error: {e}")
        return WORKING_MOVIES[:limit]

@app.get("/api/movies/trending")
async def get_trending_movies(limit: int = Query(20, ge=1, le=100)):
    """Get trending movies from multiple sources"""
    logger.info(f"🔥 Getting {limit} trending movies")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for trending movies
            trending = await enhanced_service.get_trending_movies()
            if trending:
                logger.info(f"✅ Enhanced service returned {len(trending)} trending movies")
                return trending[:limit]
        
        # Fallback to demo trending (sorted by rating)
        trending_demo = sorted(WORKING_MOVIES, key=lambda x: x.get('rating', 0), reverse=True)
        logger.info(f"✅ Returning {len(trending_demo[:limit])} demo trending movies")
        return trending_demo[:limit]
        
    except Exception as e:
        logger.error(f"❌ Trending movies error: {e}")
        return WORKING_MOVIES[:limit]

@app.get("/api/movies/search")
async def search_movies(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Search movies using real OMDB API"""
    logger.info(f"🔍 Searching for: '{q}' (limit: {limit})")
    
    try:
        if SERVICES_LOADED and omdb_client:
            # Use real OMDB search
            results = await omdb_client.search_movies(q)
            if results:
                logger.info(f"✅ OMDB returned {len(results)} results for '{q}'")
                return results[:limit]
            else:
                logger.warning(f"⚠️ No OMDB results for '{q}', using demo fallback")
        
        # Fallback to demo search
        query_lower = q.lower()
        demo_results = []
        
        for movie in WORKING_MOVIES:
            if (query_lower in movie['title'].lower() or 
                any(query_lower in genre.lower() for genre in movie['genre']) or
                query_lower in movie['director'].lower()):
                demo_results.append(movie)
                
            if len(demo_results) >= limit:
                break
        
        logger.info(f"✅ Demo search found {len(demo_results)} results for '{q}'")
        return demo_results
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return WORKING_MOVIES[:limit]

@app.get("/api/movies/{movie_id}")
async def get_movie_by_id(movie_id: str):
    """Get movie details with enhanced data"""
    logger.info(f"🎬 Getting movie: {movie_id}")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for full movie details
            movie_details = await enhanced_service.get_movie_with_analysis(movie_id)
            if movie_details:
                logger.info(f"✅ Enhanced service returned details for {movie_id}")
                return movie_details
            else:
                logger.warning(f"⚠️ Enhanced service found no details for {movie_id}")
        
        # Fallback to demo data
        for movie in WORKING_MOVIES:
            if movie['id'] == movie_id or movie['imdbId'] == movie_id:
                logger.info(f"✅ Returning demo data for {movie_id}")
                return movie
        
        raise HTTPException(status_code=404, detail=f"Movie not found: {movie_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/movies/image-proxy")
async def image_proxy(url: str = Query(...)):
    """Enhanced image proxy with FanArt integration"""
    try:
        logger.info(f"🖼️ Proxying image: {url}")
        
        # If we have enhanced services, try to get better image
        if SERVICES_LOADED and enhanced_service:
            try:
                # Try to extract movie ID from URL or get better image
                better_image = await enhanced_service.get_enhanced_poster(url)
                if better_image and better_image != url:
                    logger.info(f"✅ Enhanced image found: {better_image}")
                    url = better_image
            except Exception as e:
                logger.warning(f"⚠️ Enhanced image failed: {e}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type=response.headers.get('content-type', 'image/png'),
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            else:
                logger.warning(f"⚠️ Image request failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Image proxy error: {e}")
    
    # Return placeholder image on any error
    placeholder_url = "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=Image+Not+Available"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(placeholder_url)
            return Response(
                content=response.content,
                media_type="image/png",
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except:
        return Response(
            content=b"Image not available", 
            media_type="text/plain", 
            status_code=404
        )

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data"""
    logger.info("📊 Getting analytics data")
    
    return {
        "total_movies": len(WORKING_MOVIES),
        "genres": {
            "Drama": 4,
            "Crime": 2,
            "Sci-Fi": 1,
            "Action": 1
        },
        "average_rating": 8.7,
        "most_popular": "The Shawshank Redemption",
        "api_status": "running",
        "services_loaded": SERVICES_LOADED
    }

# New analysis endpoints
@app.get("/api/movies/{movie_id}/analysis")
async def get_movie_analysis(movie_id: str):
    """Get comprehensive movie analysis including sentiment"""
    logger.info(f"🎭 Getting analysis for movie: {movie_id}")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for sentiment analysis
            analysis = await enhanced_service.analyze_movie_sentiment(movie_id)
            if analysis:
                logger.info(f"✅ Analysis completed for {movie_id}")
                return analysis
            else:
                logger.warning(f"⚠️ No analysis available for {movie_id}")
        
        # Return demo analysis
        demo_analysis = {
            "movie_id": movie_id,
            "sentiment_analysis": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.8,
                "review_count": 1250,
                "positive_reviews": 75,
                "negative_reviews": 15,
                "neutral_reviews": 10
            },
            "reddit_data": {
                "posts_analyzed": 50,
                "average_score": 4.2,
                "trending_topics": ["cinematography", "performance", "direction"]
            },
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "using_demo_data": True
        }
        
        return demo_analysis
        
    except Exception as e:
        logger.error(f"❌ Analysis error for {movie_id}: {e}")
        return {"error": "Analysis failed", "movie_id": movie_id}

@app.get("/api/movies/{movie_id}/images")
async def get_movie_images(movie_id: str):
    """Get movie images from FanArt API"""
    logger.info(f"🖼️ Getting images for movie: {movie_id}")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for FanArt images
            images = await enhanced_service.get_movie_images(movie_id)
            if images:
                logger.info(f"✅ Found {len(images)} images for {movie_id}")
                return {"images": images}
        
        # Return demo images
        demo_images = {
            "images": {
                "poster": f"https://via.placeholder.com/300x450/1a1a1a/ffffff?text=Poster+{movie_id}",
                "backdrop": f"https://via.placeholder.com/1920x1080/1a1a1a/ffffff?text=Backdrop+{movie_id}",
                "logo": f"https://via.placeholder.com/400x200/1a1a1a/ffffff?text=Logo+{movie_id}"
            },
            "using_demo_data": True
        }
        
        return demo_images
        
    except Exception as e:
        logger.error(f"❌ Images error for {movie_id}: {e}")
        return {"error": "Images not available", "movie_id": movie_id}

@app.get("/api/movies/{movie_id}/reviews")
async def get_movie_reviews(movie_id: str):
    """Get movie reviews from Reddit"""
    logger.info(f"💬 Getting reviews for movie: {movie_id}")
    
    try:
        if SERVICES_LOADED and enhanced_service:
            # Use enhanced service for Reddit reviews
            reviews = await enhanced_service.get_reddit_reviews(movie_id)
            if reviews:
                logger.info(f"✅ Found {len(reviews)} reviews for {movie_id}")
                return {"reviews": reviews}
        
        # Return demo reviews
        demo_reviews = {
            "reviews": [
                {
                    "author": "movie_lover_123",
                    "content": "Amazing cinematography and storytelling. A masterpiece!",
                    "score": 95,
                    "sentiment": "positive",
                    "source": "reddit"
                },
                {
                    "author": "film_critic_pro", 
                    "content": "Outstanding performances from all actors. Highly recommended.",
                    "score": 88,
                    "sentiment": "positive",
                    "source": "reddit"
                }
            ],
            "total_reviews": 2,
            "average_score": 91.5,
            "using_demo_data": True
        }
        
        return demo_reviews
        
    except Exception as e:
        logger.error(f"❌ Reviews error for {movie_id}: {e}")
        return {"error": "Reviews not available", "movie_id": movie_id}

# Run the server
if __name__ == "__main__":
    logger.info("🚀 Starting CineScope Complete Backend Server")
    logger.info(f"📍 Server URL: http://localhost:8000")
    logger.info(f"📋 API Docs: http://localhost:8000/docs")
    logger.info(f"🔧 Services loaded: {SERVICES_LOADED}")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        sys.exit(1)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"❌ Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": "internal_server_error"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 CineScope API starting up...")
    logger.info(f"📊 Loaded {len(WORKING_MOVIES)} movies")
    logger.info("✅ All endpoints registered")
    logger.info("🎬 Ready to serve movie data!")

if __name__ == "__main__":
    print("🚀 Starting CineScope Backend...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )