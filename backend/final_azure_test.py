#!/usr/bin/env python3
"""
Final Azure Cosmos DB Connection Verification
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def comprehensive_test():
    """Comprehensive test of all components"""
    logger.info("🚀 Starting comprehensive Azure Cosmos DB test...")
    
    results = {
        "environment_variables": False,
        "database_connection": False,
        "database_operations": False,
        "health_endpoint": False,
        "overall_status": "FAILED"
    }
    
    try:
        # Test 1: Environment Variables
        logger.info("1️⃣ Testing environment variables...")
        mongodb_uri = os.getenv("MONGODB_URI")
        omdb_key = os.getenv("OMDB_API_KEY")
        fanart_key = os.getenv("FANART_API_KEY")
        
        if mongodb_uri and omdb_key and fanart_key:
            results["environment_variables"] = True
            logger.info("✅ Environment variables loaded successfully")
            logger.info(f"   MongoDB URI: {mongodb_uri[:50]}...")
            logger.info(f"   OMDB API Key: {omdb_key}")
            logger.info(f"   FanArt API Key: {fanart_key[:20]}...")
        else:
            logger.error("❌ Missing environment variables")
            return results
        
        # Test 2: Database Connection
        logger.info("2️⃣ Testing database connection...")
        from app.core.azure_database import AzureDatabaseManager
        
        db_manager = AzureDatabaseManager()
        await db_manager.connect()
        
        if db_manager.client and db_manager.db:
            results["database_connection"] = True
            logger.info("✅ Database connection successful")
            logger.info(f"   Database type: {db_manager.database_type}")
            logger.info(f"   Database name: {db_manager.db_name}")
        else:
            logger.error("❌ Database connection failed")
            return results
        
        # Test 3: Database Operations
        logger.info("3️⃣ Testing database operations...")
        
        # Test collection access
        movies_collection = await db_manager.get_collection("movies")
        
        # Test write operation
        test_movie = {
            "id": "test_final",
            "title": "Final Test Movie",
            "year": 2025,
            "rating": 9.0,
            "test": True
        }
        
        insert_result = await movies_collection.insert_one(test_movie)
        logger.info(f"✅ Write operation successful: {insert_result.inserted_id}")
        
        # Test read operation
        found_movie = await movies_collection.find_one({"id": "test_final"})
        if found_movie:
            logger.info("✅ Read operation successful")
            results["database_operations"] = True
        
        # Cleanup
        await movies_collection.delete_one({"id": "test_final"})
        logger.info("✅ Cleanup completed")
        
        # Test 4: Health Endpoint
        logger.info("4️⃣ Testing health endpoint...")
        from app.main import health_check
        
        health_result = await health_check()
        if health_result and health_result.get("status") == "healthy":
            results["health_endpoint"] = True
            logger.info("✅ Health endpoint working")
            logger.info(f"   Database status: {health_result.get('database', {}).get('status', 'unknown')}")
        else:
            logger.error("❌ Health endpoint failed")
        
        # Final assessment
        all_passed = all(results[k] for k in ["environment_variables", "database_connection", "database_operations", "health_endpoint"])
        
        if all_passed:
            results["overall_status"] = "SUCCESS"
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.error("❌ Some tests failed")
        
        await db_manager.close()
        
    except Exception as e:
        logger.error(f"❌ Test error: {str(e)}")
        results["error"] = str(e)
    
    return results

async def main():
    """Main function"""
    logger.info("🔍 CineScopeAnalyzer - Azure Cosmos DB Final Verification")
    logger.info("=" * 60)
    
    results = await comprehensive_test()
    
    logger.info("=" * 60)
    logger.info("📊 FINAL RESULTS:")
    logger.info("=" * 60)
    
    for test, passed in results.items():
        if test == "overall_status":
            continue
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"   {test.replace('_', ' ').title()}: {status}")
    
    logger.info("=" * 60)
    
    if results["overall_status"] == "SUCCESS":
        print("\n🎉 SUCCESS: Azure Cosmos DB is fully operational!")
        print("✅ Your CineScopeAnalyzer backend is ready for production")
        print("🚀 You can now deploy to Railway with confidence")
        print("\n📋 Next Steps:")
        print("1. Copy environment variables to Railway dashboard")
        print("2. Push your code to trigger Railway deployment")
        print("3. Test the deployed endpoints")
    else:
        print("\n❌ ISSUES DETECTED: Some components need attention")
        print("🔧 Please review the test results above")
        if "error" in results:
            print(f"💥 Error details: {results['error']}")
    
    return results["overall_status"] == "SUCCESS"

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
