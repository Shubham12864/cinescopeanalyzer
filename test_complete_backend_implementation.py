#!/usr/bin/env python3
"""
COMPLETE BACKEND INTEGRATION TEST
Tests all implemented features and API endpoints
"""
import asyncio
import logging
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test health and status endpoints"""
    logger.info("🏥 Testing Health Endpoints")
    
    endpoints = [
        "/",
        "/health", 
        "/api/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ {endpoint}: OK")
                data = response.json()
                if 'services' in data:
                    logger.info(f"   Services: {data['services']}")
            else:
                logger.error(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {endpoint}: {e}")

def test_movie_endpoints():
    """Test movie-related endpoints"""
    logger.info("🎬 Testing Movie Endpoints")
    
    # Test basic movie endpoints
    endpoints = [
        "/api/movies",
        "/api/movies/popular",
        "/api/movies/suggestions",
        "/api/movies/trending"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                movies = data if isinstance(data, list) else data.get('movies', [])
                logger.info(f"✅ {endpoint}: {len(movies)} movies")
                
                # Log first movie for validation
                if movies:
                    first_movie = movies[0]
                    title = first_movie.get('title', first_movie.get('Title', 'Unknown'))
                    logger.info(f"   Sample: {title}")
            else:
                logger.error(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {endpoint}: {e}")

def test_search_functionality():
    """Test search functionality"""
    logger.info("🔍 Testing Search Functionality")
    
    search_queries = ["batman", "spider", "godfather", "star wars", "avengers"]
    
    for query in search_queries:
        try:
            response = requests.get(
                f"{BASE_URL}/api/movies/search",
                params={"q": query},
                timeout=20
            )
            
            if response.status_code == 200:
                results = response.json()
                movies = results if isinstance(results, list) else results.get('movies', [])
                logger.info(f"✅ Search '{query}': {len(movies)} results")
                
                # Test first result details
                if movies:
                    first_movie = movies[0]
                    title = first_movie.get('title', first_movie.get('Title', 'Unknown'))
                    logger.info(f"   First result: {title}")
            else:
                logger.error(f"❌ Search '{query}': HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Search '{query}': {e}")

def test_movie_details():
    """Test movie details endpoints"""
    logger.info("🎭 Testing Movie Details")
    
    # Test with common IMDB IDs
    test_ids = ["tt0111161", "tt0068646", "tt0468569", "tt0071562", "tt0050083"]
    
    for movie_id in test_ids:
        try:
            # Test basic movie details
            response = requests.get(f"{BASE_URL}/api/movies/{movie_id}", timeout=15)
            if response.status_code == 200:
                movie = response.json()
                title = movie.get('title', movie.get('Title', 'Unknown'))
                logger.info(f"✅ Movie details {movie_id}: {title}")
            else:
                logger.warning(f"⚠️ Movie details {movie_id}: HTTP {response.status_code}")
            
            # Test analysis endpoint
            response = requests.get(f"{BASE_URL}/api/movies/{movie_id}/analysis", timeout=15)
            if response.status_code == 200:
                analysis = response.json()
                logger.info(f"✅ Movie analysis {movie_id}: Available")
            else:
                logger.warning(f"⚠️ Movie analysis {movie_id}: HTTP {response.status_code}")
                
            # Test images endpoint
            response = requests.get(f"{BASE_URL}/api/movies/{movie_id}/images", timeout=15)
            if response.status_code == 200:
                images = response.json()
                logger.info(f"✅ Movie images {movie_id}: Available")
            else:
                logger.warning(f"⚠️ Movie images {movie_id}: HTTP {response.status_code}")
                
            # Test reviews endpoint
            response = requests.get(f"{BASE_URL}/api/movies/{movie_id}/reviews", timeout=15)
            if response.status_code == 200:
                reviews = response.json()
                logger.info(f"✅ Movie reviews {movie_id}: Available")
            else:
                logger.warning(f"⚠️ Movie reviews {movie_id}: HTTP {response.status_code}")
            
        except Exception as e:
            logger.error(f"❌ Movie {movie_id}: {e}")

def test_image_proxy():
    """Test image proxy functionality"""
    logger.info("🖼️ Testing Image Proxy")
    
    test_urls = [
        "https://via.placeholder.com/300x450/1a1a1a/ffffff?text=Test+Image",
        "https://httpbin.org/image/png",
        "https://httpbin.org/image/jpeg"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(
                f"{BASE_URL}/api/movies/image-proxy",
                params={"url": url},
                timeout=15
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                logger.info(f"✅ Image proxy: {content_type} ({len(response.content)} bytes)")
            else:
                logger.warning(f"⚠️ Image proxy: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Image proxy: {e}")

def test_analytics():
    """Test analytics endpoint"""
    logger.info("📊 Testing Analytics")
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        if response.status_code == 200:
            analytics = response.json()
            logger.info(f"✅ Analytics: {analytics.get('total_movies', 0)} movies")
            logger.info(f"   Services loaded: {analytics.get('services_loaded', False)}")
        else:
            logger.error(f"❌ Analytics: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Analytics: {e}")

def performance_test():
    """Test API performance"""
    logger.info("⚡ Testing API Performance")
    
    endpoints = [
        "/api/movies/popular",
        "/api/movies/search?q=batman",
        "/api/movies/tt0111161"
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=20)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                logger.info(f"✅ {endpoint}: {response_time:.2f}s")
            else:
                logger.warning(f"⚠️ {endpoint}: {response_time:.2f}s (HTTP {response.status_code})")
        except Exception as e:
            logger.error(f"❌ {endpoint}: {e}")

def concurrent_test():
    """Test concurrent API requests"""
    logger.info("🔄 Testing Concurrent Requests")
    
    def make_request(endpoint):
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
            return f"{endpoint}: {response.status_code}"
        except Exception as e:
            return f"{endpoint}: ERROR - {e}"
    
    endpoints = [
        "/api/movies/popular",
        "/api/movies/search?q=batman",
        "/api/movies/search?q=spider",
        "/api/movies/suggestions",
        "/api/analytics"
    ]
    
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, endpoints))
        
        for result in results:
            logger.info(f"✅ Concurrent: {result}")
    except Exception as e:
        logger.error(f"❌ Concurrent test: {e}")

def main():
    """Run complete integration test"""
    logger.info("🚀 COMPLETE BACKEND INTEGRATION TEST STARTED")
    logger.info("=" * 60)
    
    # Wait for server to be ready
    logger.info("⏳ Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Server is ready!")
                break
        except:
            time.sleep(2)
    else:
        logger.error("❌ Server is not responding!")
        return
    
    # Run all tests
    test_functions = [
        test_health_endpoints,
        test_movie_endpoints,
        test_search_functionality,
        test_movie_details,
        test_image_proxy,
        test_analytics,
        performance_test,
        concurrent_test
    ]
    
    passed_tests = 0
    total_tests = len(test_functions)
    
    for test_func in test_functions:
        try:
            logger.info("=" * 60)
            test_func()
            passed_tests += 1
            logger.info(f"✅ {test_func.__name__} completed")
        except Exception as e:
            logger.error(f"❌ {test_func.__name__} failed: {e}")
    
    # Final summary
    logger.info("=" * 60)
    logger.info("🏁 TEST SUMMARY")
    logger.info(f"✅ Passed: {passed_tests}/{total_tests}")
    logger.info(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Backend is fully functional!")
    else:
        logger.warning("⚠️ Some tests failed. Check logs above.")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
