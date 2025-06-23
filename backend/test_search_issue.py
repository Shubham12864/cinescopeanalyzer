import asyncio
import sys
import os
sys.path.append('.')
from app.core.api_manager import APIManager
import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

async def test_search():
    manager = APIManager()
    print('\n=== Testing search for "Batman" ===')
    results = await manager.search_movies('Batman')
    print(f'\nGot {len(results)} results:')
    
    for i, movie in enumerate(results[:3]):
        print(f'\n{i+1}. Title: {movie.get("title", "N/A")}')
        print(f'   ID: {movie.get("id", "N/A")}')
        print(f'   Year: {movie.get("year", "N/A")}')
        print(f'   Source: {movie.get("source", "N/A")}')
        print(f'   Plot: {movie.get("plot", "N/A")[:50]}...')
        
    print('\n=== Testing search for "Inception" ===')
    results2 = await manager.search_movies('Inception')
    print(f'\nGot {len(results2)} results:')
    
    for i, movie in enumerate(results2[:2]):
        print(f'\n{i+1}. Title: {movie.get("title", "N/A")}')
        print(f'   ID: {movie.get("id", "N/A")}')
        print(f'   Year: {movie.get("year", "N/A")}')
        print(f'   Source: {movie.get("source", "N/A")}')

if __name__ == "__main__":
    asyncio.run(test_search())
