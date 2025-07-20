#!/usr/bin/env python3
"""
Simple FastAPI server launcher that ensures proper Python path setup
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variable for consistency
os.environ['PYTHONPATH'] = str(backend_dir) + ':' + os.environ.get('PYTHONPATH', '')

# Now import and run the app
try:
    import uvicorn
    from app.main import app
    
    print("🚀 Starting CineScope Movie Analysis Server...")
    print(f"📂 Backend directory: {backend_dir}")
    print(f"🐍 Python path: {sys.path[0]}")
    print("🌐 Server will be available at: http://0.0.0.0:8000")
    print("📖 API Documentation: http://0.0.0.0:8000/docs")
    print("-" * 50)
    
    if __name__ == "__main__":
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            reload_dirs=[str(backend_dir)]
        )
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("🔧 Make sure you're running from the backend directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Server Error: {e}")
    sys.exit(1)
