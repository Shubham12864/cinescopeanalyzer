#!/usr/bin/env python3
"""
3-LAYER SEARCH ORCHESTRATOR
Coordinating instant cache, smart pre-fetching, and real-time scraping
"""
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Layer imports
from .working_omdb_client import working_omdb_client
from .instant_cache_layer import instant_cache, get_instant_search_results, cache_search_results
from .smart_prefetch_layer import initialize_prefetching_system
from .realtime_scraping_layer import initialize_scraping_system, scrape_movies_realtime

logger = logging.getLogger(__name__)

class ThreeLayerSearchOrchestrator:
    """
    3-Layer Search Architecture Orchestrator
    
    Layer 1: Instant Cache (0-50ms) - Azure Cosmos DB + Memory Cache
    Layer 2: Smart Pre-fetching (Background) - Pattern-based pre-loading
    Layer 3: Real-time Scraping (1-3s) - Multi-source live scraping
    
    Search Flow:
    1. Try Layer 1 (instant cache) - Return immediately if found
    2. If not found, trigger Layer 3 (real-time scraping) 
    3. Layer 2 runs continuously in background for future searches
    4. Cache all results in Layer 1 for future instant access
    """
    
    def __init__(self):
        # Layer components
        self.omdb_client = working_omdb_client
        self.cache_layer = instant_cache
        self.prefetch_system = None
        self.scraping_system = None
        
        # Performance tracking
        self.search_stats = {
            'total_searches': 0,
            'layer1_hits': 0,      # Instant cache hits
            'layer2_hits': 0,      # Pre-fetch cache hits  
            'layer3_executions': 0, # Real-time scraping executions
            'avg_response_time': 0,
            'search_patterns': {},
            'user_satisfaction': []
        }
        
        # System status
        self.is_initialized = False
        self.is_running = False
        
        logger.info("🎯 3-Layer Search Orchestrator initialized")
    
    async def initialize(self):
        """Initialize all three layers"""
        try:
            logger.info("🚀 Initializing 3-Layer Search System...")
            
            # Initialize Layer 1: Instant Cache
            await self.cache_layer.initialize()
            logger.info("✅ Layer 1 (Instant Cache) initialized")
            
            # Initialize working OMDB client
            await self.omdb_client.initialize()
            logger.info("✅ OMDB Client initialized")
            
            # Initialize Layer 3: Real-time Scraping
            self.scraping_system = await initialize_scraping_system()
            logger.info("✅ Layer 3 (Real-time Scraping) initialized")
            
            # Initialize Layer 2: Smart Pre-fetching (depends on other layers)
            self.prefetch_system = await initialize_prefetching_system(
                self.omdb_client, 
                self.scraping_system
            )
            logger.info("✅ Layer 2 (Smart Pre-fetching) initialized")
            
            self.is_initialized = True
            self.is_running = True
            
            logger.info("🎉 3-Layer Search System fully operational!")
            
        except Exception as e:
            logger.error(f"❌ 3-Layer system initialization failed: {e}")
            raise
    
    async def search_movies(self, query: str, limit: int = 20, user_context: Dict = None) -> Dict[str, Any]:
        """
        Execute 3-layer search with performance tracking
        
        Returns:
        {
            "results": [...],
            "metadata": {
                "layer_used": "layer1" | "layer2" | "layer3",
                "response_time_ms": float,
                "total_results": int,
                "cached": bool,
                "sources": [...],
                "search_id": str
            }
        }
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        search_id = f"search_{int(time.time() * 1000)}"
        
        try:
            self.search_stats['total_searches'] += 1
            
            # Update search patterns for Layer 2
            if self.prefetch_system:
                await self.prefetch_system.analyze_search_pattern(query, user_context)
            
            logger.info(f"🔍 Starting 3-layer search: '{query}' (ID: {search_id})")
            
            # LAYER 1: Try Instant Cache (0-50ms)
            layer1_start = time.time()
            cached_results = await get_instant_search_results(query, limit)
            layer1_time = (time.time() - layer1_start) * 1000
            
            if cached_results:
                self.search_stats['layer1_hits'] += 1
                
                response_time = (time.time() - start_time) * 1000
                self._update_response_time(response_time)
                
                logger.info(f"⚡ Layer 1 HIT: '{query}' → {len(cached_results)} results in {response_time:.1f}ms")
                
                return {
                    "results": cached_results,
                    "metadata": {
                        "layer_used": "layer1",
                        "response_time_ms": response_time,
                        "layer1_time_ms": layer1_time,
                        "total_results": len(cached_results),
                        "cached": True,
                        "sources": self._extract_sources(cached_results),
                        "search_id": search_id,
                        "performance": "excellent"
                    }
                }
            
            logger.info(f"❌ Layer 1 MISS: '{query}' in {layer1_time:.1f}ms - proceeding to Layer 3")
            
            # LAYER 3: Real-time Multi-source Scraping (1-3s)
            layer3_start = time.time()
            
            # Execute parallel searches from OMDB + Enhanced Scraping
            search_tasks = []
            
            # OMDB API search (fast and reliable)
            search_tasks.append(self._search_omdb_with_timeout(query, limit))
            
            # Enhanced multi-source scraping (comprehensive)
            search_tasks.append(scrape_movies_realtime(query, limit))
            
            # Execute both in parallel
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Merge results from both sources
            final_results = await self._merge_search_results(search_results, limit)
            
            layer3_time = (time.time() - layer3_start) * 1000
            response_time = (time.time() - start_time) * 1000
            
            if final_results:
                self.search_stats['layer3_executions'] += 1
                
                # Cache results in Layer 1 for future instant access
                await cache_search_results(query, final_results, limit)
                
                self._update_response_time(response_time)
                
                logger.info(f"🕷️ Layer 3 SUCCESS: '{query}' → {len(final_results)} results in {response_time:.1f}ms")
                
                return {
                    "results": final_results,
                    "metadata": {
                        "layer_used": "layer3",
                        "response_time_ms": response_time,
                        "layer1_time_ms": layer1_time,
                        "layer3_time_ms": layer3_time,
                        "total_results": len(final_results),
                        "cached": False,
                        "sources": self._extract_sources(final_results),
                        "search_id": search_id,
                        "performance": "good" if response_time < 2000 else "acceptable"
                    }
                }
            else:
                logger.warning(f"⚠️ No results found for: '{query}' in {response_time:.1f}ms")
                
                return {
                    "results": [],
                    "metadata": {
                        "layer_used": "none",
                        "response_time_ms": response_time,
                        "layer1_time_ms": layer1_time,
                        "layer3_time_ms": layer3_time,
                        "total_results": 0,
                        "cached": False,
                        "sources": [],
                        "search_id": search_id,
                        "performance": "failed",
                        "error": "No results found from any source"
                    }
                }
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"❌ 3-layer search error: {e}")
            
            return {
                "results": [],
                "metadata": {
                    "layer_used": "error",
                    "response_time_ms": response_time,
                    "total_results": 0,
                    "cached": False,
                    "sources": [],
                    "search_id": search_id,
                    "performance": "error",
                    "error": str(e)
                }
            }
    
    async def _search_omdb_with_timeout(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search OMDB with timeout protection"""
        try:
            return await asyncio.wait_for(
                self.omdb_client.search_movies(query, limit), 
                timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏰ OMDB search timeout for: '{query}'")
            return []
        except Exception as e:
            logger.error(f"❌ OMDB search error: {e}")
            return []
    
    async def _merge_search_results(self, search_results: List, limit: int) -> List[Dict[str, Any]]:
        """Merge results from OMDB and scraping sources"""
        try:
            all_results = []
            
            # Process each result set
            for result_set in search_results:
                if isinstance(result_set, Exception):
                    logger.error(f"❌ Search task failed: {result_set}")
                    continue
                
                if isinstance(result_set, list) and result_set:
                    all_results.extend(result_set)
            
            if not all_results:
                return []
            
            # Deduplicate by title and IMDB ID
            seen_titles = set()
            seen_imdb_ids = set()
            unique_results = []
            
            # Sort by quality score (prefer OMDB results, then by rating)
            all_results.sort(key=lambda x: (
                -1 if x.get('Source') == 'omdb' else 0,  # Prefer OMDB
                -float(x.get('imdbRating', '0').replace('N/A', '0') or '0'),  # Higher rating first
                -len(x.get('Plot', ''))  # More detailed plot
            ), reverse=True)
            
            for result in all_results:
                if len(unique_results) >= limit:
                    break
                
                title_key = result.get('Title', '').lower().strip()
                imdb_id = result.get('imdbID', '')
                
                # Skip duplicates
                if title_key in seen_titles or (imdb_id and imdb_id in seen_imdb_ids):
                    continue
                
                seen_titles.add(title_key)
                if imdb_id:
                    seen_imdb_ids.add(imdb_id)
                
                # Add merge timestamp
                result['MergedAt'] = datetime.utcnow().isoformat()
                unique_results.append(result)
            
            logger.debug(f"🔄 Merged {len(all_results)} → {len(unique_results)} unique results")
            return unique_results
            
        except Exception as e:
            logger.error(f"❌ Results merging error: {e}")
            return []
    
    def _extract_sources(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract unique sources from results"""
        try:
            sources = set()
            for result in results:
                source = result.get('Source', 'unknown')
                sources.add(source)
            return list(sources)
        except:
            return []
    
    def _update_response_time(self, response_time: float):
        """Update average response time statistics"""
        try:
            current_avg = self.search_stats['avg_response_time']
            total_searches = self.search_stats['total_searches']
            
            # Calculate new average
            new_avg = ((current_avg * (total_searches - 1)) + response_time) / total_searches
            self.search_stats['avg_response_time'] = new_avg
            
        except Exception as e:
            logger.error(f"❌ Response time update error: {e}")
    
    async def get_movie_details(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed movie information using all layers"""
        try:
            # Try cache first
            cached_movie = await self.cache_layer.get_movie_by_id(imdb_id)
            if cached_movie:
                logger.info(f"⚡ Movie details from cache: {imdb_id}")
                return cached_movie
            
            # Try OMDB
            omdb_details = await self.omdb_client.get_movie_by_id(imdb_id)
            if omdb_details:
                # Cache for future use
                await self.cache_layer._cache_individual_movies([omdb_details])
                logger.info(f"🎬 Movie details from OMDB: {imdb_id}")
                return omdb_details
            
            # Try scraping as last resort
            if self.scraping_system:
                scraping_details = await self.scraping_system.get_movie_details(imdb_id)
                if scraping_details:
                    # Cache for future use
                    await self.cache_layer._cache_individual_movies([scraping_details])
                    logger.info(f"🕷️ Movie details from scraping: {imdb_id}")
                    return scraping_details
            
            logger.warning(f"⚠️ No details found for movie: {imdb_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Movie details error: {e}")
            return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = {
                "system_status": {
                    "initialized": self.is_initialized,
                    "running": self.is_running,
                    "uptime": datetime.utcnow().isoformat()
                },
                "search_performance": self.search_stats.copy(),
                "layer_stats": {}
            }
            
            # Layer 1 stats
            if self.cache_layer:
                stats["layer_stats"]["layer1_cache"] = self.cache_layer.get_cache_stats()
            
            # Layer 2 stats
            if self.prefetch_system:
                stats["layer_stats"]["layer2_prefetch"] = self.prefetch_system.get_prefetch_stats()
            
            # Layer 3 stats
            if self.scraping_system:
                stats["layer_stats"]["layer3_scraping"] = self.scraping_system.get_scraping_stats()
                
            # OMDB stats
            if self.omdb_client:
                stats["omdb_client"] = self.omdb_client.get_client_stats()
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ System stats error: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        try:
            health = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "layers": {}
            }
            
            # Test Layer 1 (Cache)
            try:
                test_results = await get_instant_search_results("test_health")
                health["layers"]["layer1"] = {"status": "healthy", "cache_accessible": True}
            except Exception as e:
                health["layers"]["layer1"] = {"status": "degraded", "error": str(e)}
                health["status"] = "degraded"
            
            # Test OMDB Client
            try:
                test_omdb = await self.omdb_client.search_movies("test", limit=1)
                health["omdb"] = {"status": "healthy", "api_accessible": True}
            except Exception as e:
                health["omdb"] = {"status": "degraded", "error": str(e)}
                health["status"] = "degraded"
            
            # Test Layer 3 (Scraping)
            try:
                if self.scraping_system:
                    scraping_stats = self.scraping_system.get_scraping_stats()
                    health["layers"]["layer3"] = {"status": "healthy", "sources_enabled": scraping_stats.get("sources_enabled", 0)}
                else:
                    health["layers"]["layer3"] = {"status": "not_initialized"}
            except Exception as e:
                health["layers"]["layer3"] = {"status": "degraded", "error": str(e)}
                health["status"] = "degraded"
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def shutdown(self):
        """Gracefully shutdown all layers"""
        try:
            logger.info("🛑 Shutting down 3-Layer Search System...")
            
            self.is_running = False
            
            # Shutdown Layer 2 (Pre-fetching)
            if self.prefetch_system:
                await self.prefetch_system.stop_background_processing()
                logger.info("✅ Layer 2 (Pre-fetching) stopped")
            
            # Shutdown Layer 3 (Scraping)
            if self.scraping_system:
                await self.scraping_system.cleanup()
                logger.info("✅ Layer 3 (Scraping) cleaned up")
            
            # Cleanup Layer 1 (Cache)
            if self.cache_layer:
                await self.cache_layer.cleanup_expired_cache()
                logger.info("✅ Layer 1 (Cache) cleaned up")
            
            # Cleanup OMDB client
            if self.omdb_client:
                await self.omdb_client.cleanup()
                logger.info("✅ OMDB Client cleaned up")
            
            logger.info("🏁 3-Layer Search System shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")

# Global orchestrator instance
search_orchestrator = ThreeLayerSearchOrchestrator()

# Export main functions
async def search_movies_comprehensive(query: str, limit: int = 20, user_context: Dict = None) -> Dict[str, Any]:
    """
    Comprehensive 3-layer movie search
    
    Args:
        query: Search query
        limit: Maximum results to return
        user_context: Optional user context for personalization
        
    Returns:
        {
            "results": [...],
            "metadata": {
                "layer_used": str,
                "response_time_ms": float,
                "performance": str,
                ...
            }
        }
    """
    return await search_orchestrator.search_movies(query, limit, user_context)

async def get_movie_details_comprehensive(imdb_id: str) -> Optional[Dict[str, Any]]:
    """Get comprehensive movie details using all available layers"""
    return await search_orchestrator.get_movie_details(imdb_id)

async def initialize_search_system():
    """Initialize the complete 3-layer search system"""
    await search_orchestrator.initialize()
    return search_orchestrator

def get_search_system_stats() -> Dict[str, Any]:
    """Get comprehensive search system statistics"""
    return search_orchestrator.get_system_stats()

async def health_check_search_system() -> Dict[str, Any]:
    """Perform health check on search system"""
    return await search_orchestrator.health_check()
