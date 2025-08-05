"""
Enhanced API Routes with Azure Cosmos DB Caching
High-performance movie and image endpoints with intelligent caching
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Request
from fastapi.responses import Response, JSONResponse
import base64

from ..services.azure_cache_service import AzureCosmosCache
from ..services.enhanced_image_service import enhanced_image_service
from ..core.tmdb_api import TMDbAPI

logger = logging.getLogger(__name__)

# Initialize services
cache_service = AzureCosmosCache()
tmdb_api = TMDbAPI()

# Create router
router = APIRouter()

# Initialize services globally
cache_service = AzureCosmosCache()
tmdb_api = TMDbAPI()

# Service initialization will be handled in main app startup
async def initialize_enhanced_services():
    """Initialize all enhanced services"""
    await cache_service.initialize()
    await enhanced_image_service.initialize()
    logger.info("✅ Enhanced API routes initialized with Azure caching")

async def cleanup_enhanced_services():
    """Cleanup enhanced services"""
    await cache_service.close()
    await enhanced_image_service.close()
    logger.info("🔌 Enhanced API routes closed")

@router.get("/movies/search")
async def search_movies_enhanced(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, le=500, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Results per page"),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    background_tasks: BackgroundTasks = None
):
    """
    Enhanced movie search with Azure Cosmos DB caching
    
    Features:
    - Intelligent caching with Azure Cosmos DB
    - Fast response times with memory fallback
    - Automatic cache refresh in background
    - Comprehensive error handling
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🔍 Enhanced search request: '{q}' page {page} limit {limit}")
        
        # Generate cache key
        cache_key = f"search_{q}_{page}_{limit}"
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = await cache_service.get_cached_data(cache_key, "movies_cache")
            if cached_result:
                logger.info(f"🎯 Cache hit for search: '{q}'")
                
                # Add cache metadata
                cached_result["from_cache"] = True
                cached_result["response_time_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
                cached_result["timestamp"] = datetime.utcnow().isoformat()
                
                return cached_result
        
        # Fetch from TMDB API
        logger.info(f"🌐 API call for search: '{q}' page {page}")
        
        search_result = await _fetch_tmdb_search(q, page)
        
        if search_result and "results" in search_result:
            # Process and enhance results
            movies = search_result["results"][:limit]
            enhanced_movies = await _enhance_movie_list(movies)
            
            # Prepare response
            response_data = {
                "results": enhanced_movies,
                "page": page,
                "total_pages": min(search_result.get("total_pages", 1), 500),
                "total_results": search_result.get("total_results", len(enhanced_movies)),
                "query": q,
                "limit": limit,
                "from_cache": False,
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": datetime.utcnow().isoformat(),
                "enhanced": True
            }
            
            # Cache the result (background task)
            if background_tasks:
                background_tasks.add_task(
                    cache_service.set_cached_data,
                    cache_key,
                    response_data,
                    ttl_hours=6,
                    collection_name="movies_cache"
                )
            
            logger.info(f"✅ Search completed: {len(enhanced_movies)} results for '{q}'")
            return response_data
        else:
            return {
                "results": [],
                "page": page,
                "total_pages": 0,
                "total_results": 0,
                "query": q,
                "limit": limit,
                "from_cache": False,
                "message": "No results found",
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Enhanced search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/movies/{movie_id}")
async def get_movie_details_enhanced(
    movie_id: int,
    force_refresh: bool = Query(False, description="Force refresh cache"),
    background_tasks: BackgroundTasks = None
):
    """
    Enhanced movie details with Azure Cosmos DB caching
    
    Features:
    - Detailed movie information with cast/crew
    - High-quality image URLs
    - Azure caching for fast responses
    - Automatic background refresh
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🎬 Enhanced details request: movie {movie_id}")
        
        # Generate cache key
        cache_key = f"movie_details_{movie_id}"
        
        # Check cache first
        if not force_refresh:
            cached_result = await cache_service.get_cached_data(cache_key, "movies_cache")
            if cached_result:
                logger.info(f"🎯 Cache hit for movie details: {movie_id}")
                
                cached_result["from_cache"] = True
                cached_result["response_time_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
                cached_result["timestamp"] = datetime.utcnow().isoformat()
                
                return cached_result
        
        # Fetch from TMDB API
        logger.info(f"🌐 API call for movie details: {movie_id}")
        
        movie_details = await _fetch_tmdb_movie_details(movie_id)
        
        if movie_details:
            # Enhance movie data
            enhanced_movie = await _enhance_single_movie(movie_details)
            
            response_data = {
                "movie": enhanced_movie,
                "from_cache": False,
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": datetime.utcnow().isoformat(),
                "enhanced": True
            }
            
            # Cache the result (background task)
            if background_tasks:
                background_tasks.add_task(
                    cache_service.set_cached_data,
                    cache_key,
                    response_data,
                    ttl_hours=12,
                    collection_name="movies_cache"
                )
            
            logger.info(f"✅ Movie details completed: {movie_id}")
            return response_data
        else:
            raise HTTPException(status_code=404, detail="Movie not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enhanced movie details error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get movie details: {str(e)}")

@router.get("/movies/popular")
async def get_popular_movies_enhanced(
    page: int = Query(1, ge=1, le=500, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Results per page"),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    background_tasks: BackgroundTasks = None
):
    """
    Enhanced popular movies with Azure Cosmos DB caching
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🔥 Enhanced popular movies request: page {page} limit {limit}")
        
        cache_key = f"popular_{page}_{limit}"
        
        # Check cache first
        if not force_refresh:
            cached_result = await cache_service.get_cached_data(cache_key, "movies_cache")
            if cached_result:
                logger.info(f"🎯 Cache hit for popular movies: page {page}")
                
                cached_result["from_cache"] = True
                cached_result["response_time_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
                cached_result["timestamp"] = datetime.utcnow().isoformat()
                
                return cached_result
        
        # Fetch from TMDB API
        popular_result = await _fetch_tmdb_popular(page)
        
        if popular_result and "results" in popular_result:
            movies = popular_result["results"][:limit]
            enhanced_movies = await _enhance_movie_list(movies)
            
            response_data = {
                "results": enhanced_movies,
                "page": page,
                "total_pages": min(popular_result.get("total_pages", 1), 500),
                "total_results": popular_result.get("total_results", len(enhanced_movies)),
                "limit": limit,
                "from_cache": False,
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": datetime.utcnow().isoformat(),
                "enhanced": True
            }
            
            # Cache the result
            if background_tasks:
                background_tasks.add_task(
                    cache_service.set_cached_data,
                    cache_key,
                    response_data,
                    ttl_hours=2,  # Popular movies change more frequently
                    collection_name="movies_cache"
                )
            
            return response_data
        else:
            return {
                "results": [],
                "page": page,
                "total_pages": 0,
                "total_results": 0,
                "from_cache": False,
                "message": "No popular movies found",
                "response_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ Enhanced popular movies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get popular movies: {str(e)}")

@router.get("/images/proxy")
async def proxy_image_enhanced(
    url: str = Query(..., description="Image URL to proxy"),
    quality: str = Query("medium", regex="^(low|medium|high)$", description="Image quality"),
    format: str = Query("base64", regex="^(base64|binary)$", description="Response format")
):
    """
    Enhanced image proxy with Azure Cosmos DB caching
    
    Features:
    - Intelligent image caching
    - Quality optimization (low/medium/high)
    - Format conversion (JPEG optimization)
    - Fast response with Azure storage
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🖼️ Enhanced image proxy: {url[:50]}... quality={quality}")
        
        # Get cached/processed image
        image_result = await enhanced_image_service.get_image_cached(url, quality)
        
        if image_result["success"]:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if format == "binary":
                # Return binary image data
                image_bytes = base64.b64decode(image_result["image_data"])
                return Response(
                    content=image_bytes,
                    media_type=image_result["content_type"],
                    headers={
                        "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                        "X-From-Cache": str(image_result["from_cache"]),
                        "X-Response-Time": f"{response_time:.1f}ms",
                        "X-Image-Size": str(image_result["size"]),
                        "X-Enhanced": "true"
                    }
                )
            else:
                # Return JSON with base64 data
                return {
                    "success": True,
                    "image_data": image_result["image_data"],
                    "content_type": image_result["content_type"],
                    "size": image_result["size"],
                    "quality": quality,
                    "from_cache": image_result["from_cache"],
                    "response_time_ms": response_time,
                    "timestamp": datetime.utcnow().isoformat(),
                    "enhanced": True
                }
        else:
            raise HTTPException(status_code=404, detail=image_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enhanced image proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Image proxy failed: {str(e)}")

@router.get("/cache/stats")
async def get_cache_stats():
    """Get comprehensive cache statistics"""
    try:
        # Get cache service stats
        cache_stats = await cache_service.get_cache_stats()
        
        # Get image service stats
        image_stats = await enhanced_image_service.get_service_stats()
        
        return {
            "cache_service": cache_stats,
            "image_service": image_stats,
            "system": {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "operational",
                "azure_cosmos_enabled": cache_stats.get("cache_type") == "azure_cosmos"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Cache stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@router.post("/cache/clear")
async def clear_all_caches():
    """Clear all caches (admin endpoint)"""
    try:
        # Clear cache service
        await cache_service.clear_all_cache()
        
        # Clear image service cache
        await enhanced_image_service.clear_image_cache()
        
        return {
            "success": True,
            "message": "All caches cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Clear cache error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear caches: {str(e)}")

# Helper functions
async def _fetch_tmdb_search(query: str, page: int) -> Optional[Dict[str, Any]]:
    """Fetch search results from TMDB API"""
    try:
        if hasattr(tmdb_api, 'search_movies'):
            return await _call_tmdb_async(tmdb_api.search_movies, query, page)
        else:
            # Direct API call fallback
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"https://api.themoviedb.org/3/search/movie"
                params = {
                    "api_key": tmdb_api.api_key,
                    "query": query,
                    "page": page,
                    "include_adult": "false"
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
        return None
    except Exception as e:
        logger.error(f"❌ TMDB search error: {e}")
        return None

async def _fetch_tmdb_movie_details(movie_id: int) -> Optional[Dict[str, Any]]:
    """Fetch movie details from TMDB API"""
    try:
        if hasattr(tmdb_api, 'get_movie_details'):
            return await _call_tmdb_async(tmdb_api.get_movie_details, movie_id)
        else:
            # Direct API call fallback
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"https://api.themoviedb.org/3/movie/{movie_id}"
                params = {
                    "api_key": tmdb_api.api_key,
                    "append_to_response": "credits,videos,images,recommendations"
                }
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
        return None
    except Exception as e:
        logger.error(f"❌ TMDB movie details error: {e}")
        return None

async def _fetch_tmdb_popular(page: int) -> Optional[Dict[str, Any]]:
    """Fetch popular movies from TMDB API"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = f"https://api.themoviedb.org/3/movie/popular"
            params = {
                "api_key": tmdb_api.api_key,
                "page": page
            }
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
        return None
    except Exception as e:
        logger.error(f"❌ TMDB popular error: {e}")
        return None

async def _call_tmdb_async(method, *args):
    """Call TMDB API method asynchronously"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, method, *args)

async def _enhance_movie_list(movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enhance movie list with additional data"""
    enhanced_movies = []
    
    for movie in movies:
        enhanced_movie = await _enhance_single_movie(movie)
        enhanced_movies.append(enhanced_movie)
    
    return enhanced_movies

async def _enhance_single_movie(movie: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance single movie with additional data"""
    enhanced = movie.copy()
    
    # Add enhanced image URLs
    if "poster_path" in enhanced and enhanced["poster_path"]:
        base_url = "https://image.tmdb.org/t/p"
        enhanced["poster_url"] = f"{base_url}/w500{enhanced['poster_path']}"
        enhanced["poster_url_high"] = f"{base_url}/w780{enhanced['poster_path']}"
        enhanced["poster_url_low"] = f"{base_url}/w300{enhanced['poster_path']}"
    
    if "backdrop_path" in enhanced and enhanced["backdrop_path"]:
        base_url = "https://image.tmdb.org/t/p"
        enhanced["backdrop_url"] = f"{base_url}/w1280{enhanced['backdrop_path']}"
        enhanced["backdrop_url_high"] = f"{base_url}/original{enhanced['backdrop_path']}"
    
    # Add computed fields
    enhanced["release_year"] = None
    if "release_date" in enhanced and enhanced["release_date"]:
        try:
            enhanced["release_year"] = int(enhanced["release_date"][:4])
        except (ValueError, TypeError):
            pass
    
    # Add genre string if genres are available
    if "genres" in enhanced and enhanced["genres"]:
        enhanced["genre_string"] = ", ".join([g.get("name", "") for g in enhanced["genres"]])
    
    # Add runtime string if available
    if "runtime" in enhanced and enhanced["runtime"]:
        hours = enhanced["runtime"] // 60
        minutes = enhanced["runtime"] % 60
        if hours > 0:
            enhanced["runtime_string"] = f"{hours}h {minutes}m"
        else:
            enhanced["runtime_string"] = f"{minutes}m"
    
    # Add cache metadata
    enhanced["cached_at"] = datetime.utcnow().isoformat()
    enhanced["enhanced"] = True
    
    return enhanced
