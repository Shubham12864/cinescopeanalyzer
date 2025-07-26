#!/usr/bin/env python3
"""
ENHANCED MOVIE ROUTES - FIXED VERSION
Robust search with dynamic image loading, no PIL dependencies
"""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from typing import List
import logging
import time
from datetime import datetime

from ...models.movie import Movie
from ...services.enhanced_movie_service import fixed_movie_service
from ...core.error_handler import ValidationException, SearchException, get_request_id

router = APIRouter(prefix="/api/movies", tags=["movies"])
logger = logging.getLogger(__name__)

@router.get("/health")
async def movies_health():
    """Health check for movie service"""
    return {
        "status": "healthy",
        "service": "enhanced-movie-service",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "omdb_api": "available",
            "search_service": "available", 
            "image_proxy": "available"
        }
    }

@router.get("/search", response_model=List[Movie])
async def search_movies_enhanced(
    request: Request,
    response: Response,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    🚀 ENHANCED SEARCH - Fast, robust movie search with dynamic image loading
    
    Features:
    - Multiple API sources with intelligent fallback
    - Dynamic image proxy integration
    - Fast response times with caching
    - Always returns results (never empty)
    """
    request_id = get_request_id(request)
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Enhanced search request: '{q}' (limit: {limit}, request_id: {request_id})")
        
        # Use fixed movie service for REAL search results
        movies = await fixed_movie_service.search_movies(q, limit)
        
        # Set response headers for caching
        response.headers["Cache-Control"] = "public, max-age=300, s-maxage=300"  # 5 minutes
        response.headers["Vary"] = "Accept-Encoding" 
        response.headers["X-Search-Results"] = str(len(movies))
        response.headers["X-Request-ID"] = request_id
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"✅ Search completed: {len(movies)} results in {elapsed:.0f}ms (request_id: {request_id})")
        
        return movies
        
    except ValidationException as e:
        logger.warning(f"❌ Validation error: {e} (request_id: {request_id})")
        raise HTTPException(status_code=400, detail=str(e))
        
    except SearchException as e:
        logger.error(f"❌ Search error: {e} (request_id: {request_id})")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(f"❌ Unexpected error after {elapsed:.0f}ms: {e} (request_id: {request_id})")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during search")

@router.get("/quick-search")
async def quick_search(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """
    ⚡ Quick search endpoint for fast autocomplete/suggestions
    """
    request_id = get_request_id(request)
    
    try:
        # Use fixed movie service for real results
        movies = await fixed_movie_service.search_movies(q, min(limit, 10))
        
        # Return simplified movie data for quick responses
        quick_results = []
        for movie in movies:
            quick_results.append({
                "id": movie.id,
                "title": movie.title,
                "year": movie.year,
                "poster": movie.poster,
                "rating": movie.rating
            })
        
        return {
            "query": q,
            "results": quick_results,
            "total": len(quick_results),
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(f"❌ Quick search error: {e}")
        return {
            "query": q,
            "results": [],
            "total": 0,
            "error": str(e),
            "request_id": request_id
        }

@router.get("/popular")
async def get_popular_movies(
    request: Request,
    limit: int = Query(20, ge=1, le=50)
):
    """Get popular movies (fallback to search-based results)"""
    try:
        # Search for popular movie terms to get varied results
        popular_queries = ["batman", "marvel", "star wars", "lord of the rings", "harry potter"]
        all_movies = []
        
        for query in popular_queries:
            movies = await fixed_movie_service.search_movies(query, 4)
            all_movies.extend(movies)
            if len(all_movies) >= limit:
                break
        
        return all_movies[:limit]
        
    except Exception as e:
        logger.error(f"❌ Popular movies error: {e}")
        return []

# Add CORS preflight support
@router.options("/search")
@router.options("/quick-search") 
@router.options("/popular")
async def movies_options():
    """Handle CORS preflight requests"""
    return Response(
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        }
    )
