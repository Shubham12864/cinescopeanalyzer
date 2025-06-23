"""
Simple Working FastAPI Server for Testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CineScope Movie Analysis API - Simple Test",
    description="Simple test version to verify functionality",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CineScope API is running!", "status": "healthy"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "CineScope Movie Analysis API is running",
        "version": "1.0.0"
    }

@app.get("/api/movies/suggestions")
async def get_movie_suggestions():
    """Get movie suggestions with real poster URLs"""
    suggestions = [
        {
            "id": "tt0468569",
            "title": "The Dark Knight",
            "year": 2008,
            "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
            "rating": 9.0,
            "genre": ["Action", "Crime", "Drama"],
            "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.",
            "director": "Christopher Nolan",
            "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
            "reviews": [],
            "imdbId": "tt0468569",
            "runtime": 152
        },
        {
            "id": "tt0111161",
            "title": "The Shawshank Redemption",
            "year": 1994,
            "poster": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
            "rating": 9.3,
            "genre": ["Drama"],
            "plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "director": "Frank Darabont",
            "cast": ["Tim Robbins", "Morgan Freeman"],
            "reviews": [],
            "imdbId": "tt0111161",
            "runtime": 142
        },
        {
            "id": "tt1375666",
            "title": "Inception",
            "year": 2010,
            "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
            "rating": 8.8,
            "genre": ["Action", "Sci-Fi", "Thriller"],
            "plot": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea.",
            "director": "Christopher Nolan",
            "cast": ["Leonardo DiCaprio", "Marion Cotillard", "Tom Hardy"],
            "reviews": [],
            "imdbId": "tt1375666",
            "runtime": 148
        },
        {
            "id": "tt0137523",
            "title": "Fight Club",
            "year": 1999,
            "poster": "https://m.media-amazon.com/images/M/MV5BNDIzNDU0YzEtYzE5Ni00ZjlkLTk5ZjgtNjM3NWE4YWE0NzUyXkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1_SX300.jpg",
            "rating": 8.8,
            "genre": ["Drama"],
            "plot": "An insomniac office worker and a devil-may-care soap maker form an underground fight club.",
            "director": "David Fincher",
            "cast": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
            "reviews": [],
            "imdbId": "tt0137523",
            "runtime": 139
        },
        {
            "id": "tt0816692",
            "title": "Interstellar",
            "year": 2014,
            "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
            "rating": 8.6,
            "genre": ["Adventure", "Drama", "Sci-Fi"],
            "plot": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "director": "Christopher Nolan",
            "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
            "reviews": [],
            "imdbId": "tt0816692",
            "runtime": 169
        },
        {
            "id": "hod2022",
            "title": "House of the Dragon",
            "year": 2022,
            "poster": "https://m.media-amazon.com/images/M/MV5BM2QzM2JiNTctYjRjYi00MmY2LThmYzItMjU5MTRhYWRlYWNlXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg",
            "rating": 8.4,
            "genre": ["Action", "Adventure", "Drama"],
            "plot": "An internal succession war within House Targaryen at the height of its power, 172 years before the birth of Daenerys Targaryen.",
            "director": "Various",
            "cast": ["Paddy Considine", "Emma D'Arcy", "Olivia Cooke"],
            "reviews": [],
            "imdbId": "tt11198330",
            "runtime": 60
        },
        {
            "id": "st2016",
            "title": "Stranger Things",
            "year": 2016,
            "poster": "https://m.media-amazon.com/images/M/MV5BN2ZmYjg1YmItNWQ4OC00YWM0LWE0ZDktYThjOTZiZjhhN2Q2XkEyXkFqcGdeQXVyNjgxNTQ3Mjk@._V1_SX300.jpg",
            "rating": 8.7,
            "genre": ["Drama", "Fantasy", "Horror"],
            "plot": "When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces.",
            "director": "The Duffer Brothers",
            "cast": ["Millie Bobby Brown", "Finn Wolfhard", "Winona Ryder"],
            "reviews": [],
            "imdbId": "tt4574334",
            "runtime": 50
        },
        {
            "id": "tt0109830",
            "title": "Forrest Gump",
            "year": 1994,
            "poster": "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg",
            "rating": 8.8,
            "genre": ["Drama", "Romance"],
            "plot": "The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold from the perspective of an Alabama man.",
            "director": "Robert Zemeckis",
            "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
            "reviews": [],
            "imdbId": "tt0109830",
            "runtime": 142
        }
    ]
    
    logger.info(f"✅ Returning {len(suggestions)} movie suggestions with real poster URLs")
    return suggestions

@app.get("/api/analytics")
async def get_analytics():
    """Get movie analytics data"""
    analytics = {
        "totalMovies": 8,
        "totalReviews": 24,
        "averageRating": 8.7,
        "sentimentDistribution": {
            "positive": 18,
            "negative": 3,
            "neutral": 3
        },
        "ratingDistribution": [
            {"rating": 9.0, "count": 3},
            {"rating": 8.0, "count": 4},
            {"rating": 7.0, "count": 1}
        ],
        "genrePopularity": [
            {"genre": "Drama", "count": 6, "percentage": 75.0},
            {"genre": "Action", "count": 4, "percentage": 50.0},
            {"genre": "Sci-Fi", "count": 3, "percentage": 37.5},
            {"genre": "Crime", "count": 2, "percentage": 25.0}
        ],
        "reviewTimeline": [
            {"date": "2024-06-18", "count": 5},
            {"date": "2024-06-19", "count": 8},
            {"date": "2024-06-20", "count": 6},
            {"date": "2024-06-21", "count": 3},
            {"date": "2024-06-22", "count": 2}
        ],
        "topRatedMovies": [
            {"id": "tt0111161", "title": "The Shawshank Redemption", "rating": 9.3, "year": 1994},
            {"id": "tt0468569", "title": "The Dark Knight", "rating": 9.0, "year": 2008},
            {"id": "tt0137523", "title": "Fight Club", "rating": 8.8, "year": 1999}
        ],
        "recentlyAnalyzed": [
            {"id": "st2016", "title": "Stranger Things", "rating": 8.7, "year": 2016},
            {"id": "hod2022", "title": "House of the Dragon", "rating": 8.4, "year": 2022}
        ]
    }
    
    logger.info("✅ Returning comprehensive analytics data")
    return analytics

@app.get("/api/movies/search")
async def search_movies(q: str):
    """Search for movies"""
    # Simple search simulation
    all_movies = [
        {
            "id": "tt0468569",
            "title": "The Dark Knight",
            "year": 2008,
            "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
            "rating": 9.0,
            "genre": ["Action", "Crime", "Drama"],
            "plot": "Batman faces the Joker in Gotham City.",
            "director": "Christopher Nolan",
            "cast": ["Christian Bale", "Heath Ledger"],
            "reviews": [],
            "imdbId": "tt0468569",
            "runtime": 152
        }
    ]
    
    # Filter based on query
    results = [movie for movie in all_movies if q.lower() in movie["title"].lower()]
    
    logger.info(f"✅ Search for '{q}' returned {len(results)} results")
    return results

if __name__ == "__main__":
    print("🚀 Starting CineScope Simple Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
