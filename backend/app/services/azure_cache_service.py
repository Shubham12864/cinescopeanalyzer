"""
Azure Cosmos DB Cache Service Implementation
High-performance caching with Azure Cosmos DB backend and memory fallback
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

class AzureCosmosCache:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv('COSMOS_CONNECTION_STRING')
        self.client = None
        self.database = None
        self.collections = {}
        
        # Memory fallback
        self.memory_cache = {}
        self.cache_expiry = {}
        
        # Performance stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "errors": 0,
            "memory_fallback": 0
        }
    
    async def initialize(self):
        """Initialize Azure Cosmos DB connection with fallback"""
        try:
            if not self.connection_string:
                logger.warning("No Cosmos DB connection string - using memory cache")
                self._init_memory_fallback()
                return True
            
            # Try to import motor for MongoDB/Cosmos DB API
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                
                self.client = AsyncIOMotorClient(self.connection_string)
                self.database = self.client["cinescopeanalyzer"]
                
                # Test connection
                await self.database.command("ping")
                
                # Setup collections and indexes
                await self._setup_collections()
                
                logger.info("✅ Azure Cosmos DB cache initialized successfully")
                return True
                
            except ImportError:
                logger.warning("Motor library not installed - using memory cache")
                self._init_memory_fallback()
                return True
                
        except Exception as e:
            logger.error(f"❌ Azure Cosmos DB initialization failed: {e}")
            logger.info("🔄 Falling back to memory cache")
            self._init_memory_fallback()
            return True
    
    def _init_memory_fallback(self):
        """Initialize in-memory cache as fallback"""
        self.memory_cache = {}
        self.cache_expiry = {}
        self.stats["memory_fallback"] = 1
        logger.info("✅ Memory cache fallback initialized")
    
    async def _setup_collections(self):
        """Setup collections with proper indexing for performance"""
        collections_config = {
            "movies_cache": {
                "indexes": [
                    ("cache_key", 1),
                    ("expires_at", 1),
                    ("created_at", 1),
                    ("endpoint", 1)
                ]
            },
            "images_cache": {
                "indexes": [
                    ("url_hash", 1),
                    ("expires_at", 1),
                    ("size", 1),
                    ("content_type", 1)
                ]
            },
            "api_responses": {
                "indexes": [
                    ("endpoint_hash", 1),
                    ("expires_at", 1),
                    ("params_hash", 1),
                    ("created_at", 1)
                ]
            }
        }
        
        for collection_name, config in collections_config.items():
            collection = self.database[collection_name]
            self.collections[collection_name] = collection
            
            # Create indexes for performance
            for field, direction in config["indexes"]:
                try:
                    await collection.create_index([(field, direction)])
                except Exception as e:
                    logger.debug(f"Index creation note for {collection_name}.{field}: {e}")
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache key"""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True)
        
        hash_obj = hashlib.md5(content.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    async def get_cached_data(self, cache_key: str, collection_name: str = "api_responses") -> Optional[Any]:
        """Get data from cache with automatic fallback"""
        try:
            # Use Azure Cosmos DB if available
            if self.client and collection_name in self.collections:
                return await self._get_from_cosmos(cache_key, collection_name)
            else:
                return self._get_from_memory(cache_key)
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ Cache get error: {e}")
            # Try memory fallback
            return self._get_from_memory(cache_key)
    
    async def _get_from_cosmos(self, cache_key: str, collection_name: str) -> Optional[Any]:
        """Get from Azure Cosmos DB"""
        collection = self.collections[collection_name]
        now = datetime.utcnow()
        
        result = await collection.find_one({
            "cache_key": cache_key,
            "expires_at": {"$gt": now}
        })
        
        if result:
            self.stats["hits"] += 1
            logger.debug(f"🎯 Azure cache hit: {cache_key}")
            return result.get("data")
        else:
            self.stats["misses"] += 1
            logger.debug(f"💨 Azure cache miss: {cache_key}")
            return None
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get from memory cache"""
        if key in self.memory_cache:
            expiry = self.cache_expiry.get(key, datetime.min)
            if datetime.utcnow() < expiry:
                self.stats["hits"] += 1
                logger.debug(f"🎯 Memory cache hit: {key}")
                return self.memory_cache[key]
            else:
                # Clean up expired entry
                del self.memory_cache[key]
                del self.cache_expiry[key]
        
        self.stats["misses"] += 1
        logger.debug(f"💨 Memory cache miss: {key}")
        return None
    
    async def set_cached_data(self, cache_key: str, data: Any, ttl_hours: int = 6, collection_name: str = "api_responses"):
        """Set data in cache with automatic fallback"""
        try:
            # Use Azure Cosmos DB if available
            if self.client and collection_name in self.collections:
                return await self._set_in_cosmos(cache_key, data, ttl_hours, collection_name)
            else:
                self._set_in_memory(cache_key, data, ttl_hours)
                return True
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ Cache set error: {e}")
            # Fallback to memory
            self._set_in_memory(cache_key, data, ttl_hours)
            return True
    
    async def _set_in_cosmos(self, cache_key: str, data: Any, ttl_hours: int, collection_name: str):
        """Set in Azure Cosmos DB"""
        collection = self.collections[collection_name]
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=ttl_hours)
        
        document = {
            "cache_key": cache_key,
            "data": data,
            "created_at": now,
            "expires_at": expires_at,
            "ttl": int(ttl_hours * 3600),
            "collection_type": collection_name
        }
        
        await collection.replace_one(
            {"cache_key": cache_key},
            document,
            upsert=True
        )
        
        self.stats["writes"] += 1
        logger.debug(f"💾 Azure cached: {cache_key}")
        return True
    
    def _set_in_memory(self, key: str, data: Any, ttl_hours: int):
        """Set in memory cache"""
        self.memory_cache[key] = data
        self.cache_expiry[key] = datetime.utcnow() + timedelta(hours=ttl_hours)
        self.stats["writes"] += 1
        logger.debug(f"💾 Memory cached: {key}")
    
    async def cache_movies(self, endpoint: str, params: Dict[str, Any], movies: List[Dict[str, Any]]):
        """Cache movie API response"""
        cache_key = self._generate_key("movies", f"{endpoint}_{json.dumps(params, sort_keys=True)}")
        await self.set_cached_data(cache_key, movies, ttl_hours=6, collection_name="movies_cache")
    
    async def get_cached_movies(self, endpoint: str, params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Get cached movie data"""
        cache_key = self._generate_key("movies", f"{endpoint}_{json.dumps(params, sort_keys=True)}")
        return await self.get_cached_data(cache_key, collection_name="movies_cache")
    
    async def cache_image(self, image_url: str, image_data: bytes, content_type: str):
        """Cache image data"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        # Store image metadata and data
        cache_data = {
            "image_url": image_url,
            "content_type": content_type,
            "size": len(image_data),
            "data": image_data.hex()  # Store as hex string for JSON compatibility
        }
        
        await self.set_cached_data(url_hash, cache_data, ttl_hours=48, collection_name="images_cache")
    
    async def get_cached_image(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Get cached image data"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        return await self.get_cached_data(url_hash, collection_name="images_cache")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_operations = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_operations * 100) if total_operations > 0 else 0
        
        stats = {
            "hit_rate_percent": round(hit_rate, 1),
            "total_hits": self.stats["hits"],
            "total_misses": self.stats["misses"],
            "total_writes": self.stats["writes"],
            "total_errors": self.stats["errors"],
            "cache_type": "azure_cosmos" if self.client else "memory_fallback",
            "memory_fallback_active": bool(self.stats.get("memory_fallback", 0))
        }
        
        # Get collection statistics if using Azure
        if self.client:
            try:
                for collection_name in self.collections:
                    collection = self.collections[collection_name]
                    count = await collection.count_documents({})
                    active_count = await collection.count_documents({
                        "expires_at": {"$gt": datetime.utcnow()}
                    })
                    stats[f"{collection_name}_total"] = count
                    stats[f"{collection_name}_active"] = active_count
            except Exception as e:
                logger.debug(f"Stats collection error: {e}")
        else:
            # Memory cache stats
            stats["memory_cache_size"] = len(self.memory_cache)
            stats["memory_cache_active"] = len([
                k for k, v in self.cache_expiry.items() 
                if v > datetime.utcnow()
            ])
        
        return stats
    
    async def clear_all_cache(self):
        """Clear all cached data"""
        try:
            if self.client:
                # Clear Azure collections
                for collection_name in self.collections:
                    collection = self.collections[collection_name]
                    await collection.delete_many({})
                logger.info("✅ Azure cache cleared")
            
            # Clear memory cache
            self.memory_cache.clear()
            self.cache_expiry.clear()
            logger.info("✅ Memory cache cleared")
            
            # Reset stats
            self.stats = {
                "hits": 0,
                "misses": 0,
                "writes": 0,
                "errors": 0,
                "memory_fallback": self.stats.get("memory_fallback", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Cache clear error: {e}")
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            now = datetime.utcnow()
            total_deleted = 0
            
            if self.client:
                # Clean Azure collections
                for collection_name in self.collections:
                    collection = self.collections[collection_name]
                    result = await collection.delete_many({
                        "expires_at": {"$lt": now}
                    })
                    total_deleted += result.deleted_count
                
                if total_deleted > 0:
                    logger.info(f"🧹 Cleaned {total_deleted} expired Azure cache entries")
            
            # Clean memory cache
            expired_keys = [k for k, v in self.cache_expiry.items() if v < now]
            for key in expired_keys:
                del self.memory_cache[key]
                del self.cache_expiry[key]
            
            if expired_keys:
                logger.info(f"🧹 Cleaned {len(expired_keys)} expired memory entries")
                    
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")
    
    async def close(self):
        """Close Azure Cosmos DB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Azure Cosmos DB connection closed")
