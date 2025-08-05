#!/usr/bin/env python3
"""
CineScope Comprehensive Diagnostic & Azure Cache Implementation
Diagnoses API/image issues and implements Azure Cosmos DB caching
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
import os
from typing import Optional, Dict, Any, List
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CineScopeDebugger:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.railway_url = "https://cinescopeanalyzer-production.up.railway.app"
        self.frontend_url = "http://localhost:3000"
        self.issues = []
        self.api_results = {}
        
    async def check_backend_health(self):
        """Check if backend is running and healthy"""
        print("🔍 CHECKING BACKEND HEALTH")
        print("=" * 50)
        
        # Test both local and Railway
        for name, url in [("Local", self.backend_url), ("Railway", self.railway_url)]:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(f"{url}/health") as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ {name} backend health: {data.get('status', 'OK')}")
                        else:
                            print(f"❌ {name} backend health check failed: {response.status}")
                            self.issues.append(f"{name} backend health check failing")
            except Exception as e:
                print(f"❌ {name} backend not accessible: {e}")
                self.issues.append(f"{name} backend not running: {e}")
        
        return True
    
    async def test_api_endpoints(self):
        """Test all critical API endpoints"""
        print("\n🎬 TESTING API ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            ("/api/movies/popular?limit=5", "Popular Movies"),
            ("/api/movies/search?q=batman&limit=3", "Search Results"),
            ("/api/movies/1311031", "Movie Details"),
            ("/api/movies/suggestions?limit=5", "Movie Suggestions"),
        ]
        
        for name, url in [("Local", self.backend_url), ("Railway", self.railway_url)]:
            print(f"\n📡 Testing {name} Backend ({url})")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                for endpoint, desc in endpoints:
                    try:
                        print(f"🔍 Testing {desc}...")
                        start_time = time.time()
                        
                        async with session.get(f"{url}{endpoint}") as response:
                            end_time = time.time()
                            duration = (end_time - start_time) * 1000
                            
                            if response.status == 200:
                                data = await response.json()
                                
                                if isinstance(data, list):
                                    count = len(data)
                                    print(f"✅ {desc}: {count} items in {duration:.0f}ms")
                                    
                                    if count > 0:
                                        sample = data[0]
                                        title = sample.get('title', 'Unknown')
                                        print(f"   📄 Sample: {title}")
                                    
                                elif isinstance(data, dict):
                                    title = data.get('title', 'Unknown')
                                    print(f"✅ {desc}: '{title}' in {duration:.0f}ms")
                                
                                self.api_results[f"{name}_{endpoint}"] = {
                                    "status": "success", 
                                    "count": len(data) if isinstance(data, list) else 1,
                                    "duration_ms": duration
                                }
                            else:
                                print(f"❌ {desc}: HTTP {response.status} in {duration:.0f}ms")
                                error_text = await response.text()
                                print(f"   Error: {error_text[:100]}")
                                self.issues.append(f"{name} {desc}: HTTP error {response.status}")
                                
                    except Exception as e:
                        print(f"❌ {desc}: Exception - {e}")
                        self.issues.append(f"{name} {desc}: Exception {e}")
    
    async def test_image_loading(self):
        """Test image proxy and loading"""
        print("\n🖼️ TESTING IMAGE LOADING")
        print("=" * 50)
        
        # Test image URLs
        test_images = [
            "https://image.tmdb.org/t/p/w500/aFRDH3P7TX61FVGpaLhKr6QiOC1.jpg",
            "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg"
        ]
        
        for name, url in [("Local", self.backend_url), ("Railway", self.railway_url)]:
            print(f"\n🖼️ Testing {name} Image Proxy")
            
            for test_image in test_images:
                encoded_url = quote(test_image, safe='')
                proxy_endpoints = [
                    f"/api/images/image-proxy?url={encoded_url}",
                    f"/api/movies/image-proxy?url={encoded_url}",
                ]
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                    for endpoint in proxy_endpoints:
                        try:
                            print(f"🔍 Testing {endpoint[:60]}...")
                            
                            async with session.get(f"{url}{endpoint}") as response:
                                if response.status == 200:
                                    content_type = response.headers.get('content-type', '')
                                    content_length = response.headers.get('content-length', '0')
                                    
                                    if 'image' in content_type:
                                        print(f"✅ Image proxy working: {content_length} bytes, {content_type}")
                                    else:
                                        print(f"⚠️ Response not an image: {content_type}")
                                        self.issues.append(f"{name} image proxy returning non-image content")
                                        
                                elif response.status == 404:
                                    print(f"⚠️ Image proxy endpoint not found: {endpoint}")
                                else:
                                    print(f"❌ Image proxy failed: HTTP {response.status}")
                                    self.issues.append(f"{name} image proxy HTTP error {response.status}")
                                    
                        except Exception as e:
                            print(f"❌ Image proxy exception: {e}")
                            self.issues.append(f"{name} image proxy exception: {e}")
    
    async def check_frontend_config(self):
        """Check frontend configuration"""
        print("\n🌐 CHECKING FRONTEND CONFIGURATION")
        print("=" * 50)
        
        # Check environment files
        env_files = [
            "/workspaces/cinescopeanalyzer/frontend/.env.local",
            "/workspaces/cinescopeanalyzer/frontend/.env.production"
        ]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    content = f.read()
                    print(f"✅ Found {os.path.basename(env_file)}")
                    
                    if "NEXT_PUBLIC_API_URL" in content:
                        # Extract API URL
                        for line in content.split('\n'):
                            if 'NEXT_PUBLIC_API_URL' in line and '=' in line:
                                api_url = line.split('=', 1)[1].strip()
                                print(f"   🔗 API URL: {api_url}")
                    else:
                        print("   ⚠️ NEXT_PUBLIC_API_URL not found")
                        self.issues.append(f"Missing NEXT_PUBLIC_API_URL in {env_file}")
            else:
                print(f"⚠️ {os.path.basename(env_file)} not found")
        
        # Check API configuration file
        api_file = "/workspaces/cinescopeanalyzer/frontend/lib/api.ts"
        if os.path.exists(api_file):
            print("✅ Found lib/api.ts")
            with open(api_file, 'r') as f:
                content = f.read()
                if "railway.app" in content:
                    print("   ✅ Railway URL configured in API file")
                else:
                    print("   ⚠️ Railway URL not found in API file")
        else:
            print("❌ lib/api.ts not found")
            self.issues.append("Frontend API configuration file missing")
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        print("\n📊 DIAGNOSTIC REPORT")
        print("=" * 60)
        
        print(f"🔍 Issues Found: {len(self.issues)}")
        if self.issues:
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   🎉 No critical issues found!")
        
        print(f"\n✅ Working Endpoints: {len([r for r in self.api_results.values() if r['status'] == 'success'])}")
        for endpoint, result in self.api_results.items():
            if result['status'] == 'success':
                print(f"   ✅ {endpoint}: {result['count']} items ({result['duration_ms']:.0f}ms)")
        
        return len(self.issues) == 0

# Azure Cosmos DB Cache Implementation
class AzureCosmosCache:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv('COSMOS_CONNECTION_STRING')
        self.client = None
        self.database = None
        self.collections = {}
        self.memory_cache = {}
        self.cache_expiry = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "errors": 0
        }
        
    async def initialize(self):
        """Initialize Azure Cosmos DB connection"""
        try:
            if not self.connection_string:
                logger.warning("No Cosmos DB connection string provided, using local cache")
                self._init_memory_fallback()
                return True
            
            # Try to import motor for MongoDB/Cosmos DB
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                
                self.client = AsyncIOMotorClient(self.connection_string)
                self.database = self.client["cinescopeanalyzer"]
                
                # Test connection
                await self.database.command("ping")
                
                # Initialize collections
                await self._setup_collections()
                
                logger.info("✅ Azure Cosmos DB cache initialized successfully")
                return True
                
            except ImportError:
                logger.warning("Motor library not found, using memory cache fallback")
                self._init_memory_fallback()
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Cosmos DB: {e}")
            self._init_memory_fallback()
            return True
    
    def _init_memory_fallback(self):
        """Initialize in-memory cache as fallback"""
        self.memory_cache = {}
        self.cache_expiry = {}
        logger.info("✅ Memory cache fallback initialized")
    
    async def _setup_collections(self):
        """Setup required collections with indexes"""
        collections_config = {
            "movies_cache": {
                "indexes": [
                    ("cache_key", 1),
                    ("created_at", 1),
                    ("expires_at", 1)
                ]
            },
            "images_cache": {
                "indexes": [
                    ("image_url_hash", 1),
                    ("created_at", 1),
                    ("expires_at", 1)
                ]
            },
            "api_cache": {
                "indexes": [
                    ("endpoint_hash", 1),
                    ("created_at", 1),
                    ("expires_at", 1)
                ]
            }
        }
        
        for collection_name, config in collections_config.items():
            collection = self.database[collection_name]
            self.collections[collection_name] = collection
            
            # Create indexes
            for index_spec in config["indexes"]:
                try:
                    await collection.create_index([index_spec])
                except Exception as e:
                    logger.warning(f"Index creation warning for {collection_name}: {e}")
    
    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True)
        
        hash_obj = hashlib.md5(content.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    async def get_cached_data(self, cache_key: str, collection_name: str = "api_cache") -> Optional[Dict[Any, Any]]:
        """Get cached data from Azure Cosmos DB or memory"""
        # Memory fallback
        if not self.client:
            return self._get_from_memory(cache_key)
        
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                return None
            
            # Find non-expired cache entry
            now = datetime.utcnow()
            result = await collection.find_one({
                "cache_key": cache_key,
                "expires_at": {"$gt": now}
            })
            
            if result:
                self.stats["hits"] += 1
                logger.info(f"✅ Cache hit for {cache_key}")
                return result.get("data")
            else:
                self.stats["misses"] += 1
                logger.info(f"⚠️ Cache miss for {cache_key}")
                return None
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ Cache retrieval error: {e}")
            return None
    
    async def set_cached_data(self, cache_key: str, data: Any, ttl_hours: int = 24, collection_name: str = "api_cache"):
        """Set cached data in Azure Cosmos DB or memory"""
        # Memory fallback
        if not self.client:
            self._set_in_memory(cache_key, data, ttl_hours)
            return True
        
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                return False
            
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=ttl_hours)
            
            document = {
                "cache_key": cache_key,
                "data": data,
                "created_at": now,
                "expires_at": expires_at,
                "ttl": int(ttl_hours * 3600)  # TTL in seconds for Cosmos DB
            }
            
            # Upsert the document
            await collection.replace_one(
                {"cache_key": cache_key},
                document,
                upsert=True
            )
            
            self.stats["writes"] += 1
            logger.info(f"✅ Cached data for {cache_key}")
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ Cache storage error: {e}")
            return False
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get from memory cache fallback"""
        if key in self.memory_cache:
            expiry = self.cache_expiry.get(key, datetime.min)
            if datetime.utcnow() < expiry:
                self.stats["hits"] += 1
                return self.memory_cache[key]
            else:
                del self.memory_cache[key]
                del self.cache_expiry[key]
        
        self.stats["misses"] += 1
        return None
    
    def _set_in_memory(self, key: str, data: Any, ttl_hours: int):
        """Set in memory cache fallback"""
        self.memory_cache[key] = data
        self.cache_expiry[key] = datetime.utcnow() + timedelta(hours=ttl_hours)
        self.stats["writes"] += 1
    
    async def cache_movie_data(self, endpoint: str, params: Dict[str, Any], data: List[Dict[str, Any]]):
        """Cache movie API response data"""
        cache_key = self._generate_cache_key("movies", f"{endpoint}_{params}")
        await self.set_cached_data(cache_key, data, ttl_hours=6, collection_name="movies_cache")
    
    async def get_cached_movies(self, endpoint: str, params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Get cached movie data"""
        cache_key = self._generate_cache_key("movies", f"{endpoint}_{params}")
        return await self.get_cached_data(cache_key, collection_name="movies_cache")
    
    async def cache_image_data(self, image_url: str, image_data: bytes, content_type: str):
        """Cache image data"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        cache_data = {
            "image_url": image_url,
            "content_type": content_type,
            "size": len(image_data),
            "data": image_data.hex()  # Store as hex string
        }
        
        await self.set_cached_data(url_hash, cache_data, ttl_hours=48, collection_name="images_cache")
    
    async def get_cached_image(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Get cached image data"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        return await self.get_cached_data(url_hash, collection_name="images_cache")
    
    async def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        if not self.client:
            # Memory cache cleanup
            now = datetime.utcnow()
            expired_keys = [k for k, v in self.cache_expiry.items() if v < now]
            for key in expired_keys:
                del self.memory_cache[key]
                del self.cache_expiry[key]
            return
        
        now = datetime.utcnow()
        
        for collection_name in self.collections:
            try:
                collection = self.collections[collection_name]
                result = await collection.delete_many({
                    "expires_at": {"$lt": now}
                })
                
                if result.deleted_count > 0:
                    logger.info(f"🧹 Cleaned up {result.deleted_count} expired entries from {collection_name}")
                    
            except Exception as e:
                logger.error(f"❌ Cleanup error for {collection_name}: {e}")

# Main diagnostic and setup function
async def main():
    """Run comprehensive diagnostic and implement Azure caching"""
    print("🎬 CINESCOPE COMPREHENSIVE DIAGNOSTIC & AZURE CACHE SETUP")
    print("=" * 70)
    
    # Step 1: Run diagnostics
    debugger = CineScopeDebugger()
    
    await debugger.check_backend_health()
    await debugger.test_api_endpoints()
    await debugger.test_image_loading()
    await debugger.check_frontend_config()
    
    # Generate diagnostic report
    all_good = debugger.generate_diagnostic_report()
    
    # Step 2: Setup Azure Cosmos DB Cache
    print("\n🔷 SETTING UP AZURE COSMOS DB CACHE")
    print("=" * 50)
    
    # Initialize Azure cache
    azure_cache = AzureCosmosCache()
    cache_initialized = await azure_cache.initialize()
    
    if cache_initialized:
        print("✅ Cache system initialized successfully")
        
        # Test cache operations
        test_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
        await azure_cache.set_cached_data("test_key", test_data, ttl_hours=1)
        retrieved = await azure_cache.get_cached_data("test_key")
        
        if retrieved == test_data:
            print("✅ Cache read/write test successful")
        else:
            print("⚠️ Cache test failed")
    
    # Step 3: Generate recommendations
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if not all_good:
        print("🔧 Issues found that need fixing:")
        for i, issue in enumerate(debugger.issues, 1):
            print(f"   {i}. {issue}")
    
    print("\n🚀 Next steps:")
    print("1. Fix any API endpoint issues found above")
    print("2. Ensure image proxy endpoints are working")
    print("3. Set up Azure Cosmos DB connection string (optional)")
    print("4. Restart backend to enable enhanced caching")
    print("5. Test improved performance with cached responses")
    
    return all_good

if __name__ == "__main__":
    asyncio.run(main())
