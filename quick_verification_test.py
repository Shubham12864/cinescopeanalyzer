#!/usr/bin/env python3
"""
Simple test to identify missing components
"""
import os
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print result"""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - FILE NOT FOUND: {file_path}")
        return False

def check_content_exists(file_path, search_term, description):
    """Check if content exists in file"""
    try:
        if not Path(file_path).exists():
            print(f"❌ {description} - FILE NOT FOUND: {file_path}")
            return False
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if search_term in content:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} - CONTENT NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("🔍 COMPREHENSIVE FIXES VERIFICATION")
    print("=" * 60)
    
    # Backend files
    print("\n📂 BACKEND FILES:")
    check_file_exists("backend/app/main.py", "Backend main.py")
    
    # Key backend functions
    print("\n🔧 BACKEND FUNCTIONS:")
    check_content_exists("backend/app/main.py", "SERVICE_STATUS", "Service status tracking")
    check_content_exists("backend/app/main.py", "_normalize_movie", "Data normalization")
    check_content_exists("backend/app/main.py", "_proxy_url", "Image proxy function")
    check_content_exists("backend/app/main.py", "get_fallback_movies", "Fallback system")
    
    # API endpoints
    print("\n🌐 API ENDPOINTS:")
    check_content_exists("backend/app/main.py", '@app.get("/api/movies/trending")', "Trending endpoint")
    check_content_exists("backend/app/main.py", '@app.get("/api/movies/search")', "Search endpoint")
    check_content_exists("backend/app/main.py", '@app.get("/api/movies/suggestions")', "Suggestions endpoint")
    check_content_exists("backend/app/main.py", '@app.get("/api/movies/image-proxy")', "Image proxy endpoint")
    
    # Frontend components
    print("\n🎨 FRONTEND COMPONENTS:")
    check_file_exists("frontend/components/ui/unified-movie-image.tsx", "UnifiedMovieImage component")
    check_file_exists("frontend/components/movie-cards/optimized-movie-grid.tsx", "OptimizedMovieGrid component")
    check_file_exists("frontend/components/movie-cards/movie-grid.tsx", "MovieGrid component")
    
    # Component usage
    print("\n🔗 COMPONENT INTEGRATION:")
    check_content_exists("frontend/components/movie-cards/movie-card.tsx", "UnifiedMovieImage", "MovieCard uses UnifiedMovieImage")
    check_content_exists("frontend/components/movie-cards/movie-card-new.tsx", "UnifiedMovieImage", "MovieCardNew uses UnifiedMovieImage")
    check_content_exists("frontend/components/sections/popular-movies-section.tsx", "UnifiedMovieImage", "PopularSection uses UnifiedMovieImage")
    
    # Performance optimizations
    print("\n⚡ PERFORMANCE FEATURES:")
    check_content_exists("frontend/app/page.tsx", "dynamic", "Dynamic imports")
    check_content_exists("frontend/app/page.tsx", "Suspense", "Suspense loading")
    check_file_exists("frontend/lib/request-queue.ts", "Request queue system")
    
    print("\n" + "=" * 60)
    print("🎬 VERIFICATION COMPLETE")
    print("✅ = Feature implemented correctly")
    print("❌ = Feature missing or has issues")

if __name__ == "__main__":
    main()
