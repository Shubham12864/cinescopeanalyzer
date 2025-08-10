#!/usr/bin/env python3
"""
Test script for Azure Cosmos DB connection
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.azure_database import db_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test the database connection"""
    try:
        logger.info("🔌 Testing Azure Cosmos DB connection...")
        
        # Connect to database
        await db_manager.connect()
        
        # Test basic operations
        movies_collection = await db_manager.get_collection("movies")
        
        # Test write operation
        test_movie = {
            "id": "test_movie_001",
            "title": "Connection Test Movie",
            "year": "2024",
            "plot": "A test movie to verify database connectivity",
            "rating": "8.5",
            "test_document": True
        }
        
        logger.info("📝 Testing write operation...")
        await movies_collection.insert_one(test_movie)
        logger.info("✅ Write operation successful")
        
        # Test read operation
        logger.info("📖 Testing read operation...")
        found_movie = await movies_collection.find_one({"id": "test_movie_001"})
        if found_movie is not None:
            logger.info(f"✅ Read operation successful: Found movie '{found_movie['title']}'")
        else:
            logger.error("❌ Read operation failed: Movie not found")
            return False
        
        # Test update operation
        logger.info("📝 Testing update operation...")
        result = await movies_collection.update_one(
            {"id": "test_movie_001"},
            {"$set": {"rating": "9.0", "updated": True}}
        )
        if result.modified_count > 0:
            logger.info("✅ Update operation successful")
        else:
            logger.error("❌ Update operation failed")
            return False
        
        # Test delete operation
        logger.info("🗑️ Cleaning up test data...")
        await movies_collection.delete_one({"id": "test_movie_001"})
        logger.info("✅ Test data cleaned up")
        
        # Test collections list
        logger.info("📋 Listing collections...")
        collections = await db_manager.db.list_collection_names()
        logger.info(f"📋 Available collections: {collections}")
        
        logger.info("🎉 All database operations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False
    
    finally:
        # Close connection
        await db_manager.close()

def main():
    """Main test function"""
    logger.info("🚀 Starting Azure Cosmos DB connection test...")
    
    # Check environment variables
    mongodb_uri = os.getenv("MONGODB_URI")
    database_type = os.getenv("DATABASE_TYPE")
    
    if not mongodb_uri:
        logger.error("❌ MONGODB_URI environment variable not set")
        return False
    
    logger.info(f"🔧 Database Type: {database_type}")
    logger.info(f"🔧 Connection String: {mongodb_uri[:50]}...")
    
    # Run the test
    success = asyncio.run(test_connection())
    
    if success:
        logger.info("✅ Azure Cosmos DB connection test PASSED")
        return True
    else:
        logger.error("❌ Azure Cosmos DB connection test FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
