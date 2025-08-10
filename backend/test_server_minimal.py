#!/usr/bin/env python3
"""
Minimal test server to verify route registration
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create app
app = FastAPI(title="Test CineScope API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create router
router = APIRouter()

# Mock OMDB service for testing  
class MockOMDBService:
    def __init__(self):
        self.api_key = "4977b044"
    
    async def search_movies(self, query: str, limit: int = 10):
        """Mock search that returns test data"""
        return [
            {
                "id": f"tt000{i}",
                "title": f"Test Movie {i} for {query}",
                "year": "2024",
                "poster": "https://via.placeholder.com/300x450?text=Test+Movie"
            }
            for i in range(1, min(limit + 1, 4))
        ]

# Create mock service instance
mock_omdb = MockOMDBService()

# Define test endpoints
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "movies", "timestamp": "2024-01-01T00:00:00"}

@router.get("/popular")
async def get_popular_movies(limit: int = 15):
    """Get popular movies"""
    try:
        popular_queries = ["avengers", "batman", "star wars"]
        all_movies = []
        
        for query in popular_queries:
            results = await mock_omdb.search_movies(query, 3)
            all_movies.extend(results)
        
        return all_movies[:limit]
    except Exception as e:
        return {"error": str(e)}

@router.get("/recent")
async def get_recent_movies(limit: int = 12):
    """Get recent movies"""
    try:
        recent_queries = ["2024", "2023"] 
        all_movies = []
        
        for query in recent_queries:
            results = await mock_omdb.search_movies(query, 4)
            all_movies.extend(results)
        
        return all_movies[:limit]
    except Exception as e:
        return {"error": str(e)}

@router.get("/top-rated")
async def get_top_rated_movies(limit: int = 10):
    """Get top rated movies"""
    try:
        top_queries = ["oscar", "winner"]
        all_movies = []
        
        for query in top_queries:
            results = await mock_omdb.search_movies(query, 3)
            all_movies.extend(results)
        
        return all_movies[:limit]
    except Exception as e:
        return {"error": str(e)}

@router.get("/suggestions")
async def get_movie_suggestions(limit: int = 8):
    """Get movie suggestions"""
    try:
        suggestion_queries = ["action", "comedy"]
        all_movies = []
        
        for query in suggestion_queries:
            results = await mock_omdb.search_movies(query, 2)
            all_movies.extend(results)
        
        return all_movies[:limit]
    except Exception as e:
        return {"error": str(e)}

# Include router
app.include_router(router, prefix="/api/movies", tags=["movies"])

@app.get("/")
async def root():
    return {"message": "Test CineScope API", "version": "1.0.0"}

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint working!"}

if __name__ == "__main__":
    print("🚀 Starting test server...")
    print("📋 Available endpoints:")
    print("   GET /api/movies/health")
    print("   GET /api/movies/popular")
    print("   GET /api/movies/recent") 
    print("   GET /api/movies/top-rated")
    print("   GET /api/movies/suggestions")
    print("   GET /test")
    print("\n🌐 Server will run at: http://localhost:8001")
    print("💡 Try: http://localhost:8001/api/movies/popular")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
