#!/usr/bin/env python3
"""
CineScope Complete Movie Analysis API
Main FastAPI Application Entrypoint
"""

import os
import logging
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Query, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cinescope")

# Import routes
from app.api.routes.movies import router as movies_router

# Create FastAPI app
app = FastAPI(
    title="CineScope Complete Movie Analysis API",
    description="Comprehensive Movie Search with TMDB, Google Firestore, Gemini AI, and Reddit integration",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Fallback movie list for robust offline behavior
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
        "poster": "https://image.tmdb.org/t/p/w500/9cjIGRQL0PQa1ORqSZC9IF2hy5e.jpg",
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
        "poster": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
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
        "poster": "https://image.tmdb.org/t/p/w500/hek3koDUyRQk7FIhPXsa6mT2Zc3.jpg",
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
        "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911BIGO5OHDQ5V.jpg",
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
        "poster": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
        "runtime": 195
    }
]

def get_fallback_movies(limit: int = 5) -> list:
    """Helper to return fallback movie records on TMDB API failure"""
    return WORKING_MOVIES[:limit]

# Direct API routes (root, health checks, proxy, analytics)

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to CineScope Movie Analysis API",
        "version": "4.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/api/health")
@app.get("/health")
async def health_check():
    """Retrieve detailed service health status"""
    from app.services.firestore_service import firestore_service
    from app.services.gemini_service import gemini_service
    
    return {
        "status": "healthy",
        "services": {
            "api": "available",
            "firestore": "available" if firestore_service.enabled else "disabled",
            "gemini": "available" if gemini_service.enabled else "disabled"
        }
    }

@app.get("/api/movies/image-proxy")
async def image_proxy(url: str = Query(...)):
    """Simple image proxy to prevent CORS issues on client images"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type=response.headers.get('content-type', 'image/jpeg'),
                    headers={
                        "Cache-Control": "public, max-age=86400",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
    except Exception as e:
        logger.warning(f"⚠️ Proxy failed for {url}: {e}")
        
    # Return a fallback placeholder
    placeholder_url = "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=Image+Not+Available"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(placeholder_url)
            return Response(
                content=response.content,
                media_type="image/png",
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except:
        return Response(content=b"Image not available", media_type="text/plain", status_code=404)

@app.get("/api/analytics")
async def get_analytics():
    """Get general dashboard analytics data"""
    return {
        "total_movies": len(WORKING_MOVIES),
        "genres": {
            "Drama": 4,
            "Crime": 2,
            "Sci-Fi": 1,
            "Action": 1
        },
        "average_rating": 9.1,
        "most_popular": "The Shawshank Redemption",
        "api_status": "running"
    }

# Include movie routes after direct routes to avoid path conflicts
app.include_router(movies_router)
logger.info("✅ Movie routes included successfully")

# Exception handlers

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred.", "error": str(exc)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Startup event to initialize Firestore
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 CineScope API starting up...")
    try:
        from app.services.firestore_service import firestore_service
        firestore_service.initialize()
    except Exception as e:
        logger.error(f"⚠️ Could not initialize Firestore: {e}")
    logger.info("🎬 Ready to serve movie data!")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)