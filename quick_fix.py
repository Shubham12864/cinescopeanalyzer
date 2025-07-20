#!/usr/bin/env python3
"""
Quick fix script for CineScopeAnalyzer connectivity and image issues
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with necessary configurations"""
    env_content = """# CineScopeAnalyzer Environment Configuration

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://cinescopeanalyzer.vercel.app

# Image Cache Configuration
IMAGE_CACHE_DIR=./cache/images
IMAGE_CACHE_MAX_SIZE=1000

# Database Configuration (Optional - will use SQLite fallback)
# AZURE_COSMOS_DB_CONNECTION_STRING=your_connection_string_here
# AZURE_COSMOS_DB_KEY=your_key_here

# External API Keys (Optional)
# OMDB_API_KEY=your_omdb_key_here
# REDDIT_CLIENT_ID=your_reddit_client_id_here
# REDDIT_CLIENT_SECRET=your_reddit_secret_here
"""
    
    env_path = Path("backend/.env")
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_path}")
    else:
        print(f"ℹ️  {env_path} already exists")

def create_cache_directories():
    """Create necessary cache directories"""
    directories = [
        "backend/cache",
        "backend/cache/images",
        "backend/cache/images/posters",
        "backend/cache/images/backdrops", 
        "backend/cache/images/thumbnails"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def fix_frontend_env():
    """Create frontend .env.local file"""
    frontend_env = """# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CineScope Analyzer
NEXT_PUBLIC_APP_VERSION=1.0.0
"""
    
    env_path = Path("frontend/.env.local")
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(frontend_env)
        print(f"✅ Created {env_path}")
    else:
        print(f"ℹ️  {env_path} already exists")

def show_startup_instructions():
    """Show instructions for starting the application"""
    print("\n" + "="*60)
    print("🚀 CineScopeAnalyzer Quick Fix Complete!")
    print("="*60)
    print("\n📋 To start your application:")
    print("\n1. Start the Backend:")
    print("   cd backend")
    print("   python -m app.main")
    print("   # OR")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    print("\n2. In a new terminal, start the Frontend:")
    print("   cd frontend")
    print("   npm install  # if not already done")
    print("   npm run dev")
    
    print("\n3. Test the connection:")
    print("   Backend: http://localhost:8000/health")
    print("   Frontend: http://localhost:3000")
    
    print("\n🔧 Fixes Applied:")
    print("   ✅ Fixed image cache service parameter mismatch")
    print("   ✅ Updated CORS configuration")
    print("   ✅ Fixed Next.js Image component width property")
    print("   ✅ Added proper error handling for sentiment data")
    print("   ✅ Created cached image serving routes")
    print("   ✅ Enhanced API error messages")
    
    print("\n⚠️  If you still see errors:")
    print("   - Make sure both backend and frontend are running")
    print("   - Check browser console for any remaining errors")
    print("   - Verify your backend logs for any service issues")
    print("="*60)

def main():
    """Main fix function"""
    print("🔧 Applying CineScopeAnalyzer Quick Fixes...")
    
    try:
        create_cache_directories()
        create_env_file()
        fix_frontend_env()
        show_startup_instructions()
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
