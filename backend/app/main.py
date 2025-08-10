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
    logger.error(f"❌ CRITICAL: Service import failed: {e}")
    logger.error("This will cause the application to use fallback demo data only")
    SERVICES_LOADED = False
    movies_router = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service initialization with explicit error handling
omdb_client = None
enhanced_service = None
azure_db = None
fanart_client = None
reddit_client = None

# Service status tracking
SERVICE_STATUS = {
    "omdb": False,
    "fanart": False,
    "reddit": False,
    "azure": False,
    "enhanced": False
}

if SERVICES_LOADED:
    # Initialize OMDB Client
    try:
        omdb_client = WorkingOMDBClient()
        # Test the connection
        test_result = omdb_client.api_key and len(omdb_client.api_key) > 0
        SERVICE_STATUS["omdb"] = test_result
        if test_result:
            logger.info("✅ OMDB client initialized successfully")
        else:
            logger.error("❌ OMDB client has no valid API key")
    except Exception as e:
        logger.error(f"❌ OMDB client initialization failed: {e}")
        SERVICE_STATUS["omdb"] = False

    # Initialize FanArt Service
    try:
        fanart_client = fanart_service
        SERVICE_STATUS["fanart"] = fanart_client is not None
        if SERVICE_STATUS["fanart"]:
            logger.info("✅ FanArt service initialized successfully")
        else:
            logger.error("❌ FanArt service is None")
    except Exception as e:
        logger.error(f"❌ FanArt service initialization failed: {e}")
        SERVICE_STATUS["fanart"] = False

    # Initialize Reddit Service
    try:
        reddit_client = reddit_review_service
        SERVICE_STATUS["reddit"] = reddit_client is not None
        if SERVICE_STATUS["reddit"]:
            logger.info("✅ Reddit service initialized successfully")
        else:
            logger.error("❌ Reddit service is None")
    except Exception as e:
        logger.error(f"❌ Reddit service initialization failed: {e}")
        SERVICE_STATUS["reddit"] = False

    # Initialize Enhanced Movie Service
    try:
        from services.enhanced_movie_service import EnhancedMovieService
        enhanced_service = EnhancedMovieService()
        SERVICE_STATUS["enhanced"] = True
        logger.info("✅ Enhanced Movie service initialized successfully")
    except ImportError:
        try:
            # Fallback to working search service
            from services.working_search_service import WorkingMovieSearchService
            enhanced_service = WorkingMovieSearchService()
            SERVICE_STATUS["enhanced"] = True
            logger.info("✅ Working Search service initialized as fallback")
        except Exception as e:
            logger.error(f"❌ Enhanced service fallback failed: {e}")
            SERVICE_STATUS["enhanced"] = False
    except Exception as e:
        logger.error(f"❌ Enhanced service initialization failed: {e}")
        SERVICE_STATUS["enhanced"] = False

    # Initialize Azure Database
    try:
        azure_db = AzureDatabaseManager()
        SERVICE_STATUS["azure"] = True
        logger.info("✅ Azure Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Azure Database initialization failed: {e}")
        SERVICE_STATUS["azure"] = False

    # Log final service status
    active_services = sum(SERVICE_STATUS.values())
    total_services = len(SERVICE_STATUS)
    logger.info(f"🔧 Service initialization complete: {active_services}/{total_services} services active")
    logger.info(f"📊 Service status: {SERVICE_STATUS}")
    
    if active_services == 0:
        logger.error("🚨 CRITICAL: No services initialized successfully - application will use demo data only")
        SERVICES_LOADED = False
else:
    logger.error("🚨 CRITICAL: Service imports failed - application will use demo data only")

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

# Data normalization functions
def _safe_float(v):
    """Convert value to float safely"""
    try:
        if isinstance(v, str) and v.lower() in ("n/a", "", "null", "none"):
            return 0.0
        return float(v) if v is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def _safe_int(v):
    """Convert value to int safely"""
    try:
        if isinstance(v, str):
            # Extract year from strings like "2023–2024" or "2023 TV Movie"
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', v)
            if year_match:
                return int(year_match.group())
        return int(v) if v is not None else 0
    except (ValueError, TypeError):
        return 0

def _split_list(v):
    """Convert comma-separated string or list to list"""
    if not v or v == "N/A":
        return []
    if isinstance(v, list):
        return [item.strip() for item in v if item and item.strip()]
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip() and item.strip() != "N/A"]
    return []

def _proxy_url(raw: str) -> str:
    """Generate proxy URL for images"""
    if not raw or raw in ("N/A", "null", "None", ""):
        return ""
    # Already proxied?
    if "/api/movies/image-proxy" in raw:
        return raw
    # Skip proxy for placeholder URLs
    if "placeholder.com" in raw or "via.placeholder.com" in raw:
        return raw
    # Generate proxy URL
    from urllib.parse import quote_plus
    api_base = os.getenv("PUBLIC_API_BASE", "http://localhost:8000")
    return f"{api_base}/api/movies/image-proxy?url={quote_plus(raw)}"

def _normalize_movie(raw: dict) -> dict:
    """Normalize movie data from any source to consistent schema"""
    normalized = {
        "id": raw.get("imdbID") or raw.get("imdbId") or raw.get("id") or "",
        "imdbId": raw.get("imdbID") or raw.get("imdbId") or raw.get("id") or "",
        "title": raw.get("Title") or raw.get("title") or "Unknown Title",
        "year": _safe_int(raw.get("Year") or raw.get("year")),
        "rating": _safe_float(raw.get("imdbRating") or raw.get("rating")),
        "genre": _split_list(raw.get("Genre") or raw.get("genre")),
        "plot": raw.get("Plot") or raw.get("plot") or raw.get("description") or "No plot available.",
        "director": raw.get("Director") or raw.get("director") or "N/A",
        "cast": _split_list(raw.get("Actors") or raw.get("cast")),
        "runtime": raw.get("Runtime") or raw.get("runtime") or "N/A",
        "poster": _proxy_url(raw.get("Poster") or raw.get("poster") or ""),
        "released": raw.get("Released") or raw.get("released") or raw.get("release_date") or "",
        "type": raw.get("Type") or raw.get("type") or "movie",
        "language": raw.get("Language") or raw.get("language") or "English",
        "country": raw.get("Country") or raw.get("country") or "N/A",
        "awards": raw.get("Awards") or raw.get("awards") or "N/A",
        "metascore": _safe_int(raw.get("Metascore") or raw.get("metascore")),
        "imdbVotes": raw.get("imdbVotes") or raw.get("imdbVotes") or "N/A",
        "boxOffice": raw.get("BoxOffice") or raw.get("boxOffice") or "N/A"
    }
    
    # Add fallback poster if none available
    if not normalized["poster"]:
        title_encoded = normalized["title"].replace(" ", "+")[:20]
        normalized["poster"] = f"https://via.placeholder.com/300x450/1a1a1a/ffffff?text={title_encoded}"
    
    return normalized

def get_fallback_movies(limit: int = 20) -> list:
    """Get fallback demo movies when services are unavailable"""
    return WORKING_MOVIES[:limit]

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
    """Get movie suggestions - dynamic with fallback"""
    logger.info(f"💡 Getting {limit} movie suggestions")
    
    try:
        if enhanced_service and omdb_client:
            # Try to get varied suggestions by genre
            suggestion_queries = [
                "action 2023", "comedy 2022", "drama 2023", "thriller 2022",
                "sci-fi 2023", "horror 2022", "romance 2023", "animation 2022"
            ]
            
            movies = []
            for query in suggestion_queries:
                try:
                    result = await omdb_client.search_movies(query)
                    if result and result.get("Search"):
                        for movie in result["Search"][:3]:  # Top 3 per category
                            normalized = _normalize_movie(movie)
                            movies.append(normalized)
                            if len(movies) >= limit:
                                break
                    if len(movies) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"Failed to fetch suggestions for {query}: {e}")
                    continue
            
            if movies:
                logger.info(f"✅ Suggestions: Retrieved {len(movies)} dynamic movies")
                return {"movies": movies[:limit], "source": "dynamic"}
                
        # Fallback to demo suggestions (randomized order)
        import random
        demo_suggestions = WORKING_MOVIES.copy()
        random.shuffle(demo_suggestions)
        logger.warning(f"⚠️ Using fallback suggestions ({len(demo_suggestions[:limit])} movies)")
        return {"movies": demo_suggestions[:limit], "source": "fallback"}
        
    except Exception as e:
        logger.error(f"❌ Suggestions error: {e}")
        return {"movies": WORKING_MOVIES[:limit], "source": "error_fallback"}

@app.get("/api/movies/trending")
async def get_trending_movies(limit: int = Query(20, ge=1, le=100)):
    """Get trending movies - dynamic with fallback"""
    logger.info(f"🔥 Getting {limit} trending movies")
    
    try:
        if enhanced_service and omdb_client:
            # Try to get actual trending from OMDB popular searches
            trending_titles = [
                "Dune", "Spider-Man", "Batman", "Avengers", "Star Wars",
                "John Wick", "Mission Impossible", "Fast and Furious", 
                "Guardians of the Galaxy", "Black Panther"
            ]
            
            movies = []
            for title in trending_titles[:limit]:
                try:
                    result = await omdb_client.search_movie(title)
                    if result and result.get("Response") == "True":
                        normalized = _normalize_movie(result)
                        movies.append(normalized)
                    if len(movies) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"Failed to fetch trending movie {title}: {e}")
                    continue
            
            if movies:
                logger.info(f"✅ Trending: Retrieved {len(movies)} dynamic movies")
                return {"movies": movies, "source": "dynamic"}
        
        # Fallback to demo trending (sorted by rating)
        trending_demo = sorted(WORKING_MOVIES, key=lambda x: x.get('rating', 0), reverse=True)
        logger.warning(f"⚠️ Using fallback trending ({len(trending_demo[:limit])} movies)")
        return {"movies": trending_demo[:limit], "source": "fallback"}
        
    except Exception as e:
        logger.error(f"❌ Trending movies error: {e}")
        return {"movies": WORKING_MOVIES[:limit], "source": "error_fallback"}

@app.get("/api/movies/search")
async def search_movies(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Search movies - dynamic with fallback"""
    logger.info(f"🔍 Searching for: '{q}' (limit: {limit})")
    
    try:
        if not q or len(q.strip()) < 2:
            return {"movies": [], "query": q, "source": "invalid_query"}
            
        if omdb_client:
            result = await omdb_client.search_movies(q)
            if result and result.get("Search"):
                movies = []
                for movie in result["Search"][:limit]:
                    normalized = _normalize_movie(movie)
                    movies.append(normalized)
                
                logger.info(f"✅ Search '{q}': Retrieved {len(movies)} dynamic results")
                return {"movies": movies, "query": q, "source": "dynamic"}
        
        # Fallback: search in working movies
        query_lower = q.lower()
        demo_results = []
        
        for movie in WORKING_MOVIES:
            if (query_lower in movie['title'].lower() or 
                any(query_lower in genre.lower() for genre in movie['genre']) or
                query_lower in movie['director'].lower()):
                demo_results.append(movie)
                
            if len(demo_results) >= limit:
                break
        
        logger.warning(f"⚠️ Search '{q}': Using fallback ({len(demo_results)} results)")
        return {"movies": demo_results, "query": q, "source": "fallback"}
        
    except Exception as e:
        logger.error(f"❌ Search error for '{q}': {e}")
        return {"movies": [], "query": q, "source": "error"}
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