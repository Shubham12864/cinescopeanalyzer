#!/usr/bin/env python3
"""
Simple Azure Cosmos DB Connection Test
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_azure_connection():
    """Test Azure Cosmos DB connection"""
    logger.info("🔍 Testing Azure Cosmos DB connection...")
    
    uri = os.getenv("MONGODB_URI")
    if not uri:
        logger.error("❌ MONGODB_URI not found in environment")
        return False
    
    logger.info(f"🔗 Using connection: {uri[:50]}...")
    
    try:
        # Create client with Cosmos DB settings
        client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=10000,  # 10 seconds
            connectTimeoutMS=10000,
            retryWrites=False,  # Required for Cosmos DB
            ssl=True
        )
        
        logger.info("📡 Testing connection...")
        
        # Test ping with timeout
        await asyncio.wait_for(client.admin.command('ping'), timeout=15.0)
        logger.info("✅ Ping successful!")
        
        # Test database access
        db = client["cinescope"]
        logger.info("📚 Accessing database...")
        
        # List collections (this will work even if none exist)
        collections = await db.list_collection_names()
        logger.info(f"📄 Collections found: {collections}")
        
        # Test write operation
        logger.info("✏️ Testing write operation...")
        test_collection = db["connection_test"]
        result = await test_collection.insert_one({
            "test": "connection_check",
            "timestamp": "2025-01-27",
            "status": "success"
        })
        logger.info(f"✅ Write successful! ID: {result.inserted_id}")
        
        # Test read operation
        logger.info("📖 Testing read operation...")
        document = await test_collection.find_one({"_id": result.inserted_id})
        logger.info(f"✅ Read successful! Document: {document}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        logger.info("🧹 Test document cleaned up")
        
        client.close()
        logger.info("🎉 Azure Cosmos DB connection test PASSED!")
        return True
        
    except asyncio.TimeoutError:
        logger.error("❌ Connection timeout - check firewall settings")
        return False
    except Exception as e:
        logger.error(f"❌ Connection failed: {str(e)}")
        if "SSL" in str(e) or "certificate" in str(e):
            logger.info("💡 SSL certificate issue - this might be a warning, not an error")
        return False

async def main():
    success = await test_azure_connection()
    if success:
        print("\n🎉 SUCCESS: Azure Cosmos DB is properly connected!")
        print("✅ Your database configuration is working correctly")
    else:
        print("\n❌ FAILED: Azure Cosmos DB connection issues detected")
        print("🔧 Check the troubleshooting steps above")

if __name__ == "__main__":
    asyncio.run(main())
