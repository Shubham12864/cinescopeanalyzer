#!/usr/bin/env python3
"""
Simple server startup script to test the movie API routes
"""
import uvicorn
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("🚀 Starting CineScope Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📋 API Documentation at: http://localhost:8000/docs")
    print("🎬 Movie API at: http://localhost:8000/api/movies/")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
