#!/usr/bin/env python3
"""
Simple server startup script to test the fixed endpoints
"""
import os
import sys
import uvicorn
import logging

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_server():
    """Start the test server"""
    try:
        logger.info("🚀 Starting CineScope Backend Server...")
        logger.info("📋 Available endpoints:")
        logger.info("   GET /api/movies/health")
        logger.info("   GET /api/movies/popular")
        logger.info("   GET /api/movies/recent")
        logger.info("   GET /api/movies/top-rated")
        logger.info("   GET /api/movies/suggestions")
        logger.info("")
        logger.info("🌐 Server will run at: http://localhost:8000")
        logger.info("💡 Test URLs:")
        logger.info("   http://localhost:8000/api/movies/health")
        logger.info("   http://localhost:8000/api/movies/popular")
        logger.info("")
        
        # Import the app
        from app.main import app
        
        # Start the server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_server()
