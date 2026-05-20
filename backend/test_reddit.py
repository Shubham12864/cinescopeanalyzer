import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from app.services.reddit_review_service import reddit_review_service

async def test_reddit():
    print(f"Enabled: {reddit_review_service.enabled}")
    if reddit_review_service.enabled:
        print("Fetching reviews for 'The Matrix'...")
        reviews = await reddit_review_service.get_movie_reviews("The Matrix", 1999, limit=3)
        print(f"Found {len(reviews)} reviews.")
        for r in reviews:
            print(f"- [{r.get('score', 0)}] {r.get('title', 'No Title')[:50]}... ({len(r.get('content', ''))} chars)")
    else:
        print("Reddit service is disabled.")

if __name__ == "__main__":
    asyncio.run(test_reddit())
