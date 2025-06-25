from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Import API routes
from .api.routes.movies import router as movies_router
from .api.routes.images import router as images_router
# Temporarily disabled to avoid pandas/numpy compatibility issues
# from .api.routes.enhanced_analysis_routes import router as enhanced_analysis_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="CineScope Movie Analysis API - Enhanced Edition",
    description="Advanced Backend API for Comprehensive Movie Analysis with Reddit, Scrapy, and Multi-platform Integration",
    version="2.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(movies_router)
app.include_router(images_router)
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

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "healthy", "message": "CineScope API is running", "version": "1.0.0"}

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