#!/usr/bin/env python3
"""
ENHANCED MAIN APP - NO PIL DEPENDENCIES
Fast, reliable movie search API with robust image proxy
"""
import warnings
import os
import logging

# Suppress warnings to clean up startup
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

# Import our enhanced routes (no PIL dependencies)
from .api.routes.enhanced_movies import router as movies_router
from .api.routes.simple_images import router as images_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CineScope Enhanced API",
    description="Fast, Robust Movie Search API with Dynamic Image Loading",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://cinescopeanalyzer.vercel.app",
    "https://cinescopeanalyzer-production.up.railway.app",
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Global OPTIONS handler for preflight requests
@app.options("/{path:path}")
async def global_options_handler(path: str):
    """Handle all CORS preflight requests"""
    return Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600"
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": str(os.times()),
            "path": str(request.url)
        }
    )

# Include routers
app.include_router(movies_router)
app.include_router(images_router)

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "CineScope Enhanced API - v3.0.0", 
        "status": "operational",
        "features": [
            "🚀 Ultra-fast movie search",
            "🖼️ Dynamic image proxy (no PIL)",
            "⚡ Multiple API sources with fallback",
            "📱 CORS-enabled for frontend integration",
            "🛡️ Robust error handling",
            "💾 Intelligent caching system"
        ],
        "endpoints": {
            "search": "/api/movies/search?q=batman",
            "quick_search": "/api/movies/quick-search?q=avatar", 
            "popular": "/api/movies/popular",
            "image_proxy": "/api/images/image-proxy?url=<image_url>",
            "health": "/api/movies/health"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Global health check"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": str(os.times()),
        "services": {
            "movies": "operational",
            "images": "operational", 
            "search": "operational"
        }
    }

# Add startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 CineScope Enhanced API starting up...")
    logger.info("✅ No PIL dependencies - using simplified image proxy")
    logger.info("✅ Enhanced search service initialized")
    logger.info("✅ CORS configured for frontend integration")
    logger.info("🎬 Ready to serve movie data!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.enhanced_main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
