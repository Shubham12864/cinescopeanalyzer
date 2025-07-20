#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""
import sys
import os
import uvicorn

# Add the backend directory to Python path
backend_dir = os.path.dirname(__file__)
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("🚀 Starting CineScope Backend API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("🎬 Image proxy system: ACTIVE")
    print("-" * 50)
    
    # Use import string for reload functionality
    uvicorn.run(
        "app.main:app",  # Import string instead of app object
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
