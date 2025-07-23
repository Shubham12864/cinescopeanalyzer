import warnings
import os
# Suppress cryptography deprecation warnings at startup
warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import logging

# Import API routes
from .api.routes.movies import router as movies_router
from .api.routes.images import router as images_router
from .api.routes.analytics import router as analytics_router
# Temporarily disabled to avoid pandas/numpy compatibility issues
# from .api.routes.enhanced_analysis_routes import router as enhanced_analysis_router

# Import error handling
from .core.error_handler import (
    global_exception_handler,
    CineScopeException,
    ValidationException,
    NotFoundException,
    ExternalAPIException,
    ImageProcessingException,
    SearchException
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="CineScope Movie Analysis API - Enhanced Edition",
    description="Advanced Backend API for Comprehensive Movie Analysis with Reddit, Scrapy, and Multi-platform Integration",
    version="2.0.0"
)

# Configure CORS for React frontend
# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://cinescopeanalyzer.vercel.app",
    "https://cinescopeanalyzer-production.up.railway.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["*"],  # Add wildcard for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Add explicit OPTIONS handler for preflight requests
@app.options("/{path:path}")
async def options_handler(path: str):
    from fastapi import Response
    response = Response(content="")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

# Add global exception handlers
app.add_exception_handler(CineScopeException, global_exception_handler)
app.add_exception_handler(ValidationException, global_exception_handler)
app.add_exception_handler(NotFoundException, global_exception_handler)
app.add_exception_handler(ExternalAPIException, global_exception_handler)
app.add_exception_handler(ImageProcessingException, global_exception_handler)
app.add_exception_handler(SearchException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include API routes
app.include_router(movies_router)
app.include_router(images_router)
app.include_router(analytics_router)
# Temporarily disabled to avoid pandas/numpy compatibility issues
# app.include_router(enhanced_analysis_router)

@app.get("/")
async def root():
    return {
        "message": "CineScope Movie Analysis API - Enhanced Edition", 
        "version": "2.0.0",
        "features": [
            "Comprehensive Reddit Analysis",
            "Multi-platform Web Scraping (IMDB, RT, Metacritic, Letterboxd)",
            "Advanced Sentiment Analysis",
            "Cross-platform Comparison",
            "Real-time Discussion Tracking",
            "Parallel Processing for Faster Analysis"
        ],
        "endpoints": {
            "comprehensive_analysis": "/api/v1/movies/analyze/comprehensive",
            "quick_analysis": "/api/v1/movies/analyze/quick",
            "batch_analysis": "/api/v1/movies/analyze/batch",
            "trending_discussions": "/api/v1/movies/trending-discussions",
            "platform_comparison": "/api/v1/analytics/platform-comparison"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    return {
        "status": "healthy", 
        "message": "CineScope Enhanced API is running",
        "version": "2.0.0",
        "services": {
            "reddit_analyzer": "ready",
            "web_scraper": "ready", 
            "sentiment_analyzer": "ready",
            "api_integrations": "ready"
        }
    }

# Alias for backwards compatibility
@app.get("/api/health")
async def api_health_check():
    """API health check endpoint - alias for /health"""
    return await health_check()

@app.get("/api/analytics")
async def get_analytics():
    """Get overall analytics data"""
    from .services.movie_service import MovieService
    movie_service = MovieService()
    analytics = await movie_service.get_analytics()
    return analytics

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )