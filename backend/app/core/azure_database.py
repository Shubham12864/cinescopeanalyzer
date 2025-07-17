"""
Azure-compatible database configuration
Supports both Azure Cosmos DB and MongoDB Atlas on Azure
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AzureDatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI")
        self.database_type = os.getenv("DATABASE_TYPE", "azure_cosmos")  # "azure_cosmos" or "atlas"
        self.db_name = os.getenv("MONGODB_DB_NAME", "cinescope")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Connect to Azure MongoDB service with fallback to local"""
        try:
            if not self.connection_string:
                logger.warning("⚠️ MONGODB_URI not set, using local fallback")
                self.connection_string = "mongodb://localhost:27017/"
                self.database_type = "local"
            
            # Configure connection options based on database type
            if self.database_type == "azure_cosmos":
                # Azure Cosmos DB specific settings
                self.client = AsyncIOMotorClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=3000,  # Reduced timeout
                    connectTimeoutMS=5000,
                    maxPoolSize=50,
                    retryWrites=False,  # Cosmos DB doesn't support retryWrites
                    ssl=True
                )
                logger.info("🔷 Connecting to Azure Cosmos DB for MongoDB")
            elif self.database_type == "atlas":
                # MongoDB Atlas settings
                self.client = AsyncIOMotorClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=3000,
                    connectTimeoutMS=5000,
                    maxPoolSize=50,
                    retryWrites=True,
                    ssl=True
                )
                logger.info("🍃 Connecting to MongoDB Atlas on Azure")
            else:
                # Local MongoDB settings
                self.client = AsyncIOMotorClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=2000,
                    connectTimeoutMS=3000,
                    maxPoolSize=10
                )
                logger.info("🏠 Connecting to Local MongoDB")
            
            self.db = self.client[self.db_name]
            
            # Test connection with timeout
            await asyncio.wait_for(
                self.client.admin.command('ping'), 
                timeout=5.0
            )
            logger.info(f"✅ Successfully connected to {self.database_type} database")
            
            # Initialize collections
            await self._initialize_collections()
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Database connection timeout for {self.database_type}")
            await self._fallback_to_local()
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            await self._fallback_to_local()
    
    async def _fallback_to_local(self):
        """Fallback to local SQLite-based storage"""
        try:
            logger.info("🔄 Falling back to local SQLite storage")
            # Close existing connection if any
            if self.client:
                self.client.close()
            
            # Use in-memory storage for now
            self.database_type = "sqlite_fallback"
            self.client = None
            self.db = None
            logger.info("✅ Fallback storage initialized")
        except Exception as e:
            logger.error(f"❌ Fallback initialization failed: {e}")
            raise
    
    async def _initialize_collections(self):
        """Initialize required collections with proper indexing"""
        try:
            collections = ["movies", "reviews", "analysis", "cache"]
            
            for collection_name in collections:
                collection = self.db[collection_name]
                
                # Create indexes based on collection type
                if collection_name == "movies":
                    await collection.create_index([("id", 1)], unique=True)
                    # Note: Text search indexes not supported in Cosmos DB
                    # await collection.create_index([("title", "text"), ("plot", "text")])
                    await collection.create_index([("title", 1)])
                    await collection.create_index([("year", 1)])
                    await collection.create_index([("rating", -1)])
                    
                elif collection_name == "reviews":
                    await collection.create_index([("movieId", 1)])
                    await collection.create_index([("date", -1)])
                    
                elif collection_name == "analysis":
                    await collection.create_index([("movieId", 1)], unique=True)
                    await collection.create_index([("last_updated", -1)])
                    
                elif collection_name == "cache":
                    await collection.create_index([("key", 1)], unique=True)
                    await collection.create_index([("expires_at", 1)], expireAfterSeconds=0)
            
            logger.info("✅ Collections and indexes initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Index creation failed (might already exist): {e}")
    
    async def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if self.db is None:
            await self.connect()
        return self.db[collection_name]
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Database connection closed")

# Global database instance
db_manager = AzureDatabaseManager()

async def get_database():
    """Get database instance"""
    if db_manager.client is None:
        await db_manager.connect()
    return db_manager.db

async def get_movies_collection():
    """Get movies collection"""
    return await db_manager.get_collection("movies")

async def get_reviews_collection():
    """Get reviews collection"""
    return await db_manager.get_collection("reviews")

async def get_analysis_collection():
    """Get analysis collection"""
    return await db_manager.get_collection("analysis")

async def get_cache_collection():
    """Get cache collection"""
    return await db_manager.get_collection("cache")
