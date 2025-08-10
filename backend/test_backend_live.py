#!/usr/bin/env python3
"""
START WORKING BACKEND AND TEST
Starts the backend with working search and tests it live
"""
import subprocess
import time
import requests
import sys
import os
import json

def start_backend():
    """Start the enhanced backend"""
    print("🚀 Starting Enhanced Backend...")
    
    # Change to backend directory
    backend_dir = "C:/Users/Acer/Downloads/CineScopeAnalyzer/backend"
    python_exe = "C:/Users/Acer/Downloads/CineScopeAnalyzer/venv/Scripts/python.exe"
    
    # Start backend process
    process = subprocess.Popen([
        python_exe, "-m", "uvicorn", "app.enhanced_main:app", 
        "--port", "8000", "--reload"
    ], cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("⏳ Waiting for backend to start...")
    time.sleep(8)  # Wait for startup
    
    return process

def test_search_endpoint():
    """Test the search endpoint with real queries"""
    print("\n🧪 TESTING SEARCH ENDPOINT")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health first
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        return False
    
    # Test search queries
    test_queries = ["batman", "saiyaara", "inception", "random123"]
    
    for query in test_queries:
        print(f"\n🔍 Testing search: '{query}'")
        try:
            response = requests.get(
                f"{base_url}/api/movies/search?q={query}&limit=3", 
                timeout=10
            )
            
            if response.status_code == 200:
                movies = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Results: {len(movies)} movies")
                
                if movies:
                    for i, movie in enumerate(movies, 1):
                        title = movie.get('title', 'Unknown')
                        year = movie.get('year', 'Unknown')
                        movie_id = movie.get('id', 'Unknown')
                        
                        print(f"   {i}. {title} ({year}) - {movie_id}")
                        
                        # Check for problematic demo data
                        if title in ['Inception', 'The Dark Knight', 'Avatar']:
                            if movie_id in ['tt1375666', 'tt0468569', 'tt0499549']:
                                print(f"      ❌ DEMO DATA DETECTED! This should be fixed!")
                            else:
                                print(f"      ✅ Different movie with same title (OK)")
                        else:
                            print(f"      ✅ Unique result")
                else:
                    print(f"   📭 No results (this is OK for unknown queries)")
                    
            else:
                print(f"❌ Search failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error testing '{query}': {e}")
    
    return True

def main():
    """Main test function"""
    print("🎬 CINESCOPE BACKEND TEST - REAL DATA ONLY")
    print("=" * 60)
    
    # Start backend
    backend_process = start_backend()
    
    try:
        # Test the search
        success = test_search_endpoint()
        
        if success:
            print("\n🎉 BACKEND TEST COMPLETED!")
            print("Check the results above for any 'DEMO DATA DETECTED' warnings")
        else:
            print("\n❌ BACKEND TEST FAILED!")
            
    finally:
        # Clean up
        print("\n🛑 Stopping backend...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("✅ Backend stopped")

if __name__ == "__main__":
    main()
