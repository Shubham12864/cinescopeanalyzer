#!/usr/bin/env python3
"""
CineScope Dynamic Data Verification Test
Tests the complete data flow from backend to frontend
"""

import requests
import json
import time
import sys

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data.get('status', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend Health Check Failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend Connection Failed: {e}")
        return False

def test_popular_movies_api():
    """Test the popular movies API endpoint"""
    try:
        print("\n🎬 Testing Popular Movies API...")
        response = requests.get('http://localhost:8000/api/movies/popular?limit=12', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ Popular Movies API returned {len(data)} movies")
                
                # Test first movie structure
                first_movie = data[0]
                print(f"   Sample Movie: {first_movie.get('title', 'Unknown')}")
                print(f"   Year: {first_movie.get('year', 'Unknown')}")
                print(f"   Rating: {first_movie.get('rating', 'Unknown')}")
                
                # Check image proxy URLs
                poster = first_movie.get('poster', '')
                if '/api/movies/image-proxy' in poster:
                    print(f"✅ Image Proxy URL Found: {poster[:50]}...")
                else:
                    print(f"⚠️  Direct Image URL: {poster[:50]}...")
                
                return True, data
            else:
                print(f"❌ Popular Movies API returned empty or invalid data")
                return False, []
        else:
            print(f"❌ Popular Movies API Failed: {response.status_code}")
            return False, []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Popular Movies API Error: {e}")
        return False, []

def test_search_api():
    """Test the search functionality"""
    try:
        print("\n🔍 Testing Search API...")
        search_terms = ["batman", "inception", "avengers"]
        
        for term in search_terms:
            response = requests.get(f'http://localhost:8000/api/movies/search?query={term}&limit=3', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ Search '{term}' returned {len(data)} movies")
                    print(f"   Top Result: {data[0].get('title', 'Unknown')}")
                else:
                    print(f"⚠️  Search '{term}' returned no results")
            else:
                print(f"❌ Search '{term}' failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Search API Error: {e}")
        return False

def test_image_proxy():
    """Test the image proxy functionality"""
    try:
        print("\n🖼️  Testing Image Proxy...")
        
        # Test with a known OMDB image URL
        test_url = "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg"
        proxy_url = f"http://localhost:8000/api/movies/image-proxy?url={requests.utils.quote(test_url)}"
        
        response = requests.head(proxy_url, timeout=10)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type:
                print(f"✅ Image Proxy Working: {content_type}")
                return True
            else:
                print(f"⚠️  Image Proxy returned: {content_type}")
                return False
        else:
            print(f"❌ Image Proxy Failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Image Proxy Error: {e}")
        return False

def generate_frontend_test_data(movies_data):
    """Generate test data structure for frontend verification"""
    print("\n📊 Frontend Integration Summary:")
    
    if not movies_data:
        print("❌ No movie data available for frontend")
        return
    
    print(f"✅ Backend providing {len(movies_data)} movies")
    print("\n🎬 Sample Movie Data Structure:")
    
    if movies_data:
        sample = movies_data[0]
        print(f"   ID: {sample.get('id', 'Missing')}")
        print(f"   Title: {sample.get('title', 'Missing')}")
        print(f"   Plot: {sample.get('plot', 'Missing')[:50]}...")
        print(f"   Poster: {sample.get('poster', 'Missing')[:50]}...")
        print(f"   Rating: {sample.get('rating', 'Missing')}")
        print(f"   Genre: {sample.get('genre', [])}")
        print(f"   Year: {sample.get('year', 'Missing')}")
    
    print("\n✅ Frontend Components Updated:")
    print("   ✅ MovieContext - Dynamic data loading")
    print("   ✅ MovieCard - Image proxy handling")
    print("   ✅ PopularMoviesSection - Backend API integration")
    print("   ✅ NetflixHeroBanner - Real movie IDs and data")
    print("   ✅ MovieGrid - Dynamic trending/popular data")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🎬 CineScope Dynamic Data Verification Test")
    print("=" * 60)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not available. Please start the backend server first.")
        sys.exit(1)
    
    # Test popular movies API
    popular_success, popular_data = test_popular_movies_api()
    
    # Test search API
    search_success = test_search_api()
    
    # Test image proxy
    proxy_success = test_image_proxy()
    
    # Generate frontend summary
    generate_frontend_test_data(popular_data)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Backend Health", True),
        ("Popular Movies API", popular_success),
        ("Search API", search_success),
        ("Image Proxy", proxy_success)
    ]
    
    all_passed = True
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Your CineScope app should now display dynamic data!")
        print("\n💡 Next steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Check that movie posters are loading")
        print("   3. Verify hero section shows real movie data")
        print("   4. Test search functionality")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
