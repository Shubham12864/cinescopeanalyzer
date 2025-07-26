#!/usr/bin/env python3
"""
LAYER 2: SMART PRE-FETCHING SYSTEM (Background)
Intelligent background pre-fetching based on user patterns and trends
"""
import asyncio
import logging
import time
import json
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class SmartPreFetchingSystem:
    """
    Layer 2: Smart Pre-fetching System
    - Analyze user search patterns
    - Pre-fetch popular and trending content
    - Background queue processing
    - Predictive caching based on typing patterns
    """
    
    def __init__(self, omdb_client, scraping_layer):
        self.omdb_client = omdb_client
        self.scraping_layer = scraping_layer
        
        # Pattern analysis
        self.search_patterns = defaultdict(int)
        self.search_sequence = deque(maxlen=1000)  # Last 1000 searches
        self.typing_patterns = defaultdict(list)   # User typing sequences
        
        # Pre-fetching queues
        self.prefetch_queue = asyncio.Queue(maxsize=100)
        self.priority_queue = asyncio.Queue(maxsize=50)
        self.background_tasks = set()
        
        # Popular content tracking
        self.trending_searches = defaultdict(int)
        self.popular_genres = defaultdict(int)
        self.seasonal_trends = defaultdict(list)
        
        # Performance tracking
        self.prefetch_hits = 0
        self.prefetch_attempts = 0
        
        # Control flags
        self.is_running = False
        self.prefetch_lock = threading.Lock()
        
        logger.info("🎯 Smart Pre-fetching System initialized")
        
    async def start_background_processing(self):
        """Start background pre-fetching workers"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Start multiple background workers
        workers = [
            self._pattern_analyzer_worker(),
            self._priority_prefetch_worker(),
            self._general_prefetch_worker(),
            self._trending_content_worker(),
            self._seasonal_predictor_worker()
        ]
        
        for worker in workers:
            task = asyncio.create_task(worker)
            self.background_tasks.add(task)
            
        logger.info("🚀 Background pre-fetching workers started")
    
    async def stop_background_processing(self):
        """Stop background processing"""
        self.is_running = False
        
        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()
            
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        logger.info("⏹️ Background pre-fetching stopped")
    
    async def analyze_search_pattern(self, query: str, user_context: Dict = None):
        """
        Analyze search patterns for predictive pre-fetching
        """
        try:
            normalized_query = query.lower().strip()
            current_time = datetime.utcnow()
            
            # Record search pattern
            self.search_patterns[normalized_query] += 1
            self.search_sequence.append({
                'query': normalized_query,
                'timestamp': current_time,
                'user_context': user_context or {}
            })
            
            # Analyze typing pattern for predictive suggestions
            await self._analyze_typing_pattern(normalized_query)
            
            # Extract genre and content patterns
            await self._extract_content_patterns(normalized_query)
            
            # Trigger related pre-fetching
            await self._trigger_related_prefetch(normalized_query)
            
        except Exception as e:
            logger.error(f"❌ Pattern analysis error: {e}")
    
    async def _analyze_typing_pattern(self, query: str):
        """Analyze typing patterns for predictive pre-fetching"""
        try:
            # Look for partial matches in popular searches
            for popular_query, count in self.search_patterns.items():
                if count > 5 and popular_query.startswith(query[:3]):
                    # Pre-fetch likely completions
                    await self._queue_priority_prefetch(popular_query, "typing_prediction")
                    
        except Exception as e:
            logger.error(f"❌ Typing pattern analysis error: {e}")
    
    async def _extract_content_patterns(self, query: str):
        """Extract content patterns for genre and theme analysis"""
        try:
            # Genre keywords mapping
            genre_keywords = {
                'action': ['action', 'fight', 'war', 'battle', 'hero', 'explosion'],
                'comedy': ['comedy', 'funny', 'laugh', 'humor', 'joke'],
                'drama': ['drama', 'emotional', 'life', 'family', 'relationship'],
                'horror': ['horror', 'scary', 'ghost', 'zombie', 'fear'],
                'sci-fi': ['sci-fi', 'space', 'future', 'robot', 'alien', 'technology'],
                'romance': ['romance', 'love', 'romantic', 'couple', 'wedding'],
                'thriller': ['thriller', 'suspense', 'mystery', 'crime', 'detective']
            }
            
            # Detect genre preferences
            for genre, keywords in genre_keywords.items():
                for keyword in keywords:
                    if keyword in query:
                        self.popular_genres[genre] += 1
                        break
                        
        except Exception as e:
            logger.error(f"❌ Content pattern extraction error: {e}")
    
    async def _trigger_related_prefetch(self, query: str):
        """Trigger pre-fetching of related content"""
        try:
            # Find similar searches
            similar_searches = []
            query_words = set(query.split())
            
            for past_query, count in self.search_patterns.items():
                if count > 2:  # Only consider searches with some frequency
                    past_words = set(past_query.split())
                    
                    # Calculate word overlap
                    overlap = len(query_words & past_words)
                    if overlap > 0 and past_query != query:
                        similarity_score = overlap / len(query_words | past_words)
                        if similarity_score > 0.3:  # 30% similarity threshold
                            similar_searches.append((past_query, similarity_score))
            
            # Sort by similarity and queue for pre-fetching
            similar_searches.sort(key=lambda x: x[1], reverse=True)
            
            for similar_query, score in similar_searches[:5]:  # Top 5 similar
                await self._queue_prefetch(similar_query, "similarity_based")
                
        except Exception as e:
            logger.error(f"❌ Related pre-fetch error: {e}")
    
    async def _queue_priority_prefetch(self, query: str, reason: str):
        """Queue high-priority pre-fetch request"""
        try:
            if not self.priority_queue.full():
                await self.priority_queue.put({
                    'query': query,
                    'reason': reason,
                    'timestamp': datetime.utcnow(),
                    'priority': 'high'
                })
                
        except Exception as e:
            logger.error(f"❌ Priority queue error: {e}")
    
    async def _queue_prefetch(self, query: str, reason: str):
        """Queue general pre-fetch request"""
        try:
            if not self.prefetch_queue.full():
                await self.prefetch_queue.put({
                    'query': query,
                    'reason': reason,
                    'timestamp': datetime.utcnow(),
                    'priority': 'normal'
                })
                
        except Exception as e:
            logger.error(f"❌ General queue error: {e}")
    
    async def _priority_prefetch_worker(self):
        """High-priority pre-fetch worker"""
        while self.is_running:
            try:
                # Get priority task with timeout
                task = await asyncio.wait_for(
                    self.priority_queue.get(), 
                    timeout=5.0
                )
                
                await self._execute_prefetch(task)
                self.priority_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Priority worker error: {e}")
                await asyncio.sleep(1)
    
    async def _general_prefetch_worker(self):
        """General pre-fetch worker"""
        while self.is_running:
            try:
                # Get general task with timeout
                task = await asyncio.wait_for(
                    self.prefetch_queue.get(), 
                    timeout=10.0
                )
                
                await self._execute_prefetch(task)
                self.prefetch_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ General worker error: {e}")
                await asyncio.sleep(2)
    
    async def _execute_prefetch(self, task: Dict):
        """Execute pre-fetch task"""
        try:
            query = task['query']
            reason = task['reason']
            
            start_time = time.time()
            
            # Check if already cached
            from .instant_cache_layer import get_instant_search_results
            cached = await get_instant_search_results(query)
            
            if cached:
                logger.debug(f"⚡ Pre-fetch skipped (already cached): '{query}'")
                return
            
            # Execute search and cache results
            self.prefetch_attempts += 1
            
            # Try OMDB first (faster)
            results = await self.omdb_client.search_movies(query, limit=10)
            
            # If OMDB results are limited, enhance with scraping
            if len(results) < 5:
                scraping_results = await self.scraping_layer.search_movies(query, limit=5)
                
                # Merge results without duplicates
                existing_ids = {r.get('imdbID') for r in results if r.get('imdbID')}
                for result in scraping_results:
                    if result.get('imdbID') not in existing_ids:
                        results.append(result)
            
            # Cache the results
            if results:
                from .instant_cache_layer import cache_search_results
                await cache_search_results(query, results)
                
                elapsed_ms = (time.time() - start_time) * 1000
                logger.info(f"🎯 Pre-fetched '{query}' ({reason}): {len(results)} results in {elapsed_ms:.1f}ms")
            
        except Exception as e:
            logger.error(f"❌ Pre-fetch execution error: {e}")
    
    async def _pattern_analyzer_worker(self):
        """Analyze search patterns and predict future needs"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
                # Analyze recent search sequences
                await self._analyze_search_sequences()
                
                # Update trending content
                await self._update_trending_content()
                
                # Predict popular upcoming searches
                await self._predict_popular_searches()
                
            except Exception as e:
                logger.error(f"❌ Pattern analyzer error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_search_sequences(self):
        """Analyze sequences of searches to predict patterns"""
        try:
            if len(self.search_sequence) < 10:
                return
                
            # Look for sequential patterns
            recent_searches = list(self.search_sequence)[-50:]  # Last 50 searches
            
            # Find common search progressions
            progressions = defaultdict(int)
            
            for i in range(len(recent_searches) - 1):
                current = recent_searches[i]['query']
                next_search = recent_searches[i + 1]['query']
                
                # Only consider if searches are within 5 minutes
                time_diff = recent_searches[i + 1]['timestamp'] - recent_searches[i]['timestamp']
                if time_diff < timedelta(minutes=5):
                    progressions[f"{current} -> {next_search}"] += 1
            
            # Pre-fetch based on strong progressions
            for progression, count in progressions.items():
                if count >= 3:  # Seen at least 3 times
                    current_query, next_query = progression.split(' -> ')
                    await self._queue_prefetch(next_query, "sequence_prediction")
                    
        except Exception as e:
            logger.error(f"❌ Sequence analysis error: {e}")
    
    async def _trending_content_worker(self):
        """Pre-fetch trending and popular content"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Get trending searches from various sources
                trending_queries = await self._get_trending_queries()
                
                for query in trending_queries[:10]:  # Top 10 trending
                    await self._queue_prefetch(query, "trending_content")
                    
            except Exception as e:
                logger.error(f"❌ Trending content worker error: {e}")
                await asyncio.sleep(600)
    
    async def _get_trending_queries(self) -> List[str]:
        """Get trending search queries"""
        try:
            trending = []
            
            # Popular movie keywords by season/time
            current_month = datetime.now().month
            
            seasonal_keywords = {
                12: ['christmas', 'holiday', 'winter', 'family'],  # December
                1: ['new year', 'resolution', 'drama', 'oscar'],   # January
                2: ['valentine', 'romance', 'love', 'romantic'],   # February
                10: ['halloween', 'horror', 'scary', 'thriller'],  # October
                7: ['summer', 'action', 'blockbuster', 'adventure'] # July
            }
            
            if current_month in seasonal_keywords:
                trending.extend(seasonal_keywords[current_month])
            
            # Add most frequent recent searches
            recent_queries = [item['query'] for item in list(self.search_sequence)[-100:]]
            query_frequency = defaultdict(int)
            
            for query in recent_queries:
                query_frequency[query] += 1
            
            # Get top frequent queries
            top_queries = sorted(query_frequency.items(), key=lambda x: x[1], reverse=True)
            trending.extend([query for query, count in top_queries[:5] if count > 2])
            
            return trending
            
        except Exception as e:
            logger.error(f"❌ Trending queries error: {e}")
            return []
    
    async def _seasonal_predictor_worker(self):
        """Predict and pre-fetch seasonal content"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                current_time = datetime.now()
                
                # Predict seasonal searches
                seasonal_predictions = await self._predict_seasonal_content(current_time)
                
                for prediction in seasonal_predictions:
                    await self._queue_prefetch(prediction, "seasonal_prediction")
                    
            except Exception as e:
                logger.error(f"❌ Seasonal predictor error: {e}")
                await asyncio.sleep(7200)
    
    async def _predict_seasonal_content(self, current_time: datetime) -> List[str]:
        """Predict seasonal content based on time of year"""
        try:
            predictions = []
            
            month = current_time.month
            day = current_time.day
            
            # Holiday predictions
            if month == 12 and day > 15:  # Late December
                predictions.extend(['christmas movies', 'holiday films', 'family christmas'])
            elif month == 10 and day > 20:  # Late October
                predictions.extend(['halloween movies', 'horror films', 'scary movies'])
            elif month == 2 and day < 20:  # Early February
                predictions.extend(['romantic movies', 'valentine films', 'love stories'])
            elif month in [6, 7, 8]:  # Summer
                predictions.extend(['summer blockbusters', 'action movies', 'adventure films'])
            
            # Award season predictions
            if month in [1, 2, 3]:  # Award season
                predictions.extend(['oscar movies', 'award winners', 'best picture'])
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Seasonal prediction error: {e}")
            return []
    
    async def _update_trending_content(self):
        """Update trending content analysis"""
        try:
            # Decay trending scores over time
            current_time = datetime.utcnow()
            
            for query in list(self.trending_searches.keys()):
                # Reduce score by 10% every update
                self.trending_searches[query] *= 0.9
                
                # Remove if score is too low
                if self.trending_searches[query] < 1:
                    del self.trending_searches[query]
                    
        except Exception as e:
            logger.error(f"❌ Trending update error: {e}")
    
    async def _predict_popular_searches(self):
        """Predict and pre-fetch likely popular searches"""
        try:
            # Common movie search patterns
            popular_patterns = [
                'best {} movies',
                'top {} films',
                '{} movie recommendations',
                'latest {} movies',
                'popular {} films'
            ]
            
            # Popular genres from our analysis
            top_genres = sorted(self.popular_genres.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for genre, count in top_genres:
                for pattern in popular_patterns[:2]:  # Limit to avoid spam
                    query = pattern.format(genre)
                    await self._queue_prefetch(query, "popular_prediction")
                    
        except Exception as e:
            logger.error(f"❌ Popular prediction error: {e}")
    
    def get_prefetch_stats(self) -> Dict[str, Any]:
        """Get pre-fetching statistics"""
        return {
            "prefetch_attempts": self.prefetch_attempts,
            "prefetch_hits": self.prefetch_hits,
            "success_rate": (self.prefetch_hits / max(self.prefetch_attempts, 1)) * 100,
            "priority_queue_size": self.priority_queue.qsize(),
            "general_queue_size": self.prefetch_queue.qsize(),
            "search_patterns_count": len(self.search_patterns),
            "trending_searches": dict(list(sorted(self.trending_searches.items(), 
                                                key=lambda x: x[1], reverse=True))[:10]),
            "popular_genres": dict(list(sorted(self.popular_genres.items(), 
                                             key=lambda x: x[1], reverse=True))[:5])
        }

# Export main function
async def initialize_prefetching_system(omdb_client, scraping_layer):
    """Initialize and start the pre-fetching system"""
    system = SmartPreFetchingSystem(omdb_client, scraping_layer)
    await system.start_background_processing()
    return system
