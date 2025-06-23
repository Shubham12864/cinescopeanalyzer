import asyncio
import sys
import os
sys.path.append('./backend')
from app.core.api_manager import APIManager

async def test_movie_plot():
    api = APIManager()
    movies = await api.search_movies('Inception', 1)
    if movies:
        movie = movies[0]
        print('Movie data:')
        print(f'Title: {movie.get("title")}')
        print(f'Plot: {movie.get("plot")}')
        print(f'Plot length: {len(movie.get("plot", ""))}')
        print(f'Source: {movie.get("source")}')
    else:
        print('No movies found')

if __name__ == "__main__":
    asyncio.run(test_movie_plot())
