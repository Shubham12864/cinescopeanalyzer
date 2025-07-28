#!/usr/bin/env python3
"""
Reddit API Service for Movie Reviews and Discussions

USAGE: Get real user reviews and discussions from Reddit for webapp
SUBREDDITS: /r/movies, /r/flicks, /r/TrueFilm, /r/MovieReviews, /r/criterion
"""
import asyncio
import aiohttp
import logging
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class RedditReviewService:
    """
    Reddit API Service for Movie Reviews
    
    Gets real user reviews and discussions from multiple movie subreddits
    Perfect for webapp integration showing real user opinions
    """
    
    def __init__(self):
        # Reddit API Configuration
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "tUbcUeO71VxtvH39HpnZeg")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "Qtxb5TxT8K4Uqonvp3E-qD9BJK32TA")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "CineScopeAnalyzer/2.0 (Enhanced Movie Analysis)")
        
        # Reddit endpoints
        self.reddit_base_url = "https://www.reddit.com"
        self.oauth_url = "https://www.reddit.com/api/v1/access_token"
        
        # Movie subreddits to search (reduced for speed)
        self.movie_subreddits = [
            'movies',           # Main movie discussions
            'flicks',          # Movie enthusiasts  
            'TrueFilm',        # Serious film discussion
        ]
        
        # HTTP session
        self.session = None
        self.access_token = None
        self.is_initialized = False
        
        # Cache for performance
        self.review_cache = {}
        self.cache_duration = timedelta(hours=1)
        
        # Rate limiting
        self.rate_limit_delay = 2.0  # Increased from 0.5 to 2 seconds
        
        # Retry settings
        self.max_retries = 1  # Reduced from 3 to 1
        
        logger.info("💬 Reddit Review Service initialized")
        logger.info(f"🎯 Target subreddits: {len(self.movie_subreddits)} movie communities")
    
    async def initialize(self):
        """Initialize Reddit API service"""
        if not self.is_initialized:
            try:
                self.session = aiohttp.ClientSession()
                
                # Get OAuth token for Reddit API
                await self._get_access_token()
                
                self.is_initialized = True
                logger.info("✅ Reddit Review Service ready")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Reddit service: {e}")
                # Continue without OAuth for public posts
                if not self.session:
                    self.session = aiohttp.ClientSession()
                self.is_initialized = True
                logger.warning("⚠️ Using Reddit without OAuth (public posts only)")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.is_initialized = False
            logger.info("🔒 Reddit API session closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _get_access_token(self):
        """Get OAuth access token for Reddit API"""
        try:
            if not self.client_id or not self.client_secret:
                logger.warning("⚠️ Reddit OAuth credentials not configured")
                return
            
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            headers = {'User-Agent': self.user_agent}
            data = {
                'grant_type': 'client_credentials'
            }
            
            async with self.session.post(self.oauth_url, auth=auth, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get('access_token')
                    logger.info("✅ Reddit OAuth token obtained")
                else:
                    logger.warning(f"⚠️ Reddit OAuth failed: {response.status}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Reddit OAuth error: {e}")
    
    async def get_movie_reviews(self, movie_title: str, year: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get movie reviews with proper session cleanup"""
        session = None
        try:
            logger.info(f"💬 Getting Reddit reviews for: '{movie_title}' ({year})")
            
            # Create session with proper cleanup
            timeout = aiohttp.ClientTimeout(total=8)
            session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'User-Agent': 'CineScopeAnalyzer/2.0'}
            )
            
            all_reviews = []
            
            # Reduced subreddit list to avoid rate limits
            active_subreddits = ['movies', 'TrueFilm']  # Only 2 subreddits
            
            for subreddit in active_subreddits:
                try:
                    subreddit_reviews = await self._search_subreddit_safe(
                        session, subreddit, movie_title, year, limit_per_sub=2
                    )
                    all_reviews.extend(subreddit_reviews)
                    
                    # Longer delay to avoid rate limits
                    await asyncio.sleep(3.0)  # Increased from 0.5 to 3 seconds
                    
                except Exception as e:
                    logger.warning(f"⚠️ Subreddit {subreddit} failed: {e}")
                    continue
            
            # Sort and return best reviews
            all_reviews.sort(key=lambda x: x.get('score', 0), reverse=True)
            final_reviews = all_reviews[:limit]
            
            logger.info(f"✅ Found {len(final_reviews)} Reddit reviews")
            return final_reviews
            
        except Exception as e:
            logger.error(f"❌ Reddit reviews failed: {e}")
            return []
        
        finally:
            # CRITICAL: Always close session
            if session and not session.closed:
                await session.close()

    async def _search_subreddit_safe(self, session, subreddit: str, movie_title: str, year: str, limit_per_sub: int) -> List[Dict]:
        """Safe subreddit search with error handling"""
        try:
            search_url = f"{self.reddit_base_url}/r/{subreddit}/search.json"
            params = {
                'q': f'{movie_title} {year}' if year else movie_title,
                'restrict_sr': 'on',
                'sort': 'relevance',
                'limit': limit_per_sub
            }
            
            async with session.get(search_url, params=params) as response:
                if response.status == 429:  # Rate limited
                    logger.warning(f"⚠️ Rate limited on r/{subreddit}")
                    return []
                
                if response.status == 200:
                    data = await response.json()
                    return self._process_reddit_data(data, movie_title)
                else:
                    logger.warning(f"⚠️ Reddit API error {response.status} for r/{subreddit}")
                    return []
                    
        except Exception as e:
            logger.warning(f"⚠️ Subreddit search failed for r/{subreddit}: {e}")
            return []
    
    async def get_trending_movie_discussions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending movie discussions from Reddit"""
        try:
            logger.info("🔥 Getting trending movie discussions from Reddit")
            
            trending_posts = []
            
            # Get hot posts from main movie subreddits
            for subreddit in ['movies', 'flicks', 'TrueFilm']:
                try:
                    hot_url = f"{self.reddit_base_url}/r/{subreddit}/hot.json"
                    params = {'limit': 10}
                    
                    headers = {'User-Agent': self.user_agent}
                    if self.access_token:
                        headers['Authorization'] = f'Bearer {self.access_token}'
                    
                    async with self.session.get(hot_url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if 'data' in data and 'children' in data['data']:
                                for post in data['data']['children']:
                                    post_data = post.get('data', {})
                                    
                                    trending_posts.append({
                                        'title': post_data.get('title', ''),
                                        'author': post_data.get('author', 'Unknown'),
                                        'score': post_data.get('score', 0),
                                        'num_comments': post_data.get('num_comments', 0),
                                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                        'subreddit': subreddit,
                                        'source': 'reddit_trending'
                                    })
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get trending from r/{subreddit}: {e}")
            
            # Sort by engagement
            trending_posts.sort(key=lambda x: x.get('score', 0) + x.get('num_comments', 0), reverse=True)
            
            logger.info(f"🔥 Found {len(trending_posts[:limit])} trending discussions")
            return trending_posts[:limit]
            
        except Exception as e:
            logger.error(f"❌ Trending discussions failed: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# Global service instance
reddit_review_service = RedditReviewService()
