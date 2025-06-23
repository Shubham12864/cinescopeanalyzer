#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""
import sys
import os
import uvicorn

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    # Import the app
    from app.main import app
    
    print("🚀 Starting CineScope Backend API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("⚠️  Reddit analyzer running in demo mode (no real API credentials)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
