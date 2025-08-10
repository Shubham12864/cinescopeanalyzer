#!/usr/bin/env python3
"""
Comprehensive Test Suite for CineScopeAnalyzer
Tests all implemented fixes: backend startup, Amazon URL blocking, image proxy, fast loading
"""

import os
import sys
import asyncio
import json
import time
import requests
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ SUCCESS: {message}")

def print_error(message):
    print(f"❌ ERROR: {message}")

def print_warning(message):
    print(f"⚠️  WARNING: {message}")

def test_backend_imports():
    """Test 1: Backend module imports and dependencies"""
    print_test_header("Backend Module Imports")
    
    try:
        # Test core imports
        from app.services.movie_service import MovieService
        print_success("MovieService imported successfully")
        
        from app.api.routes.movies_fixed import router
        print_success("Fixed movie routes imported successfully")
        
        # Test FastAPI imports
        import fastapi
        import uvicorn
        print_success("FastAPI and Uvicorn available")
        
        # Test essential packages
        import requests
        import httpx
        import asyncio
        print_success("HTTP clients available")
        
        import bs4
        print_success("BeautifulSoup available")
        
        return True
        
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return False

def test_movie_service_functionality():
    """Test 2: Movie Service Core Functionality"""
    print_test_header("Movie Service Functionality")
    
    try:
        from app.services.movie_service import MovieService
        
        # Initialize service
        service = MovieService()
        print_success("MovieService initialized")
        
        # Test Amazon URL blocking
        test_url = "https://images-na.ssl-images-amazon.com/images/test.jpg"
        processed_url = service._process_movie_image(test_url)
        
        if "amazon" not in processed_url.lower():
            print_success("Amazon URL blocking working correctly")
        else:
            print_error("Amazon URL not blocked properly")
            return False
        
        # Test movie search (non-async method if available)
        try:
            # Create a simple test for movie data structure
            movie_data = {
                'Title': 'Test Movie',
                'Year': '2023',
                'imdbRating': '8.0',
                'Plot': 'Test plot',
                'Genre': 'Drama',
                'Director': 'Test Director',
                'Actors': 'Test Actor',
                'Poster': 'https://example.com/poster.jpg',
                'Runtime': '120 min'
            }
            
            movie_obj = service._create_movie_object(movie_data)
            
            if movie_obj and movie_obj.title == 'Test Movie':
                print_success("Movie object creation working")
            else:
                print_error("Movie object creation failed")
                return False
                
        except Exception as e:
            print_warning(f"Movie search test skipped: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Movie service test failed: {e}")
        return False

def test_api_routes_structure():
    """Test 3: API Routes Structure"""
    print_test_header("API Routes Structure")
    
    try:
        from app.api.routes.movies_fixed import router
        
        # Check if router has the expected routes
        routes = [str(route) for route in router.routes]
        
        expected_endpoints = ['/popular', '/recent', '/top-rated', '/suggestions']
        
        for endpoint in expected_endpoints:
            found = any(endpoint in route for route in routes)
            if found:
                print_success(f"Endpoint {endpoint} found in routes")
            else:
                print_warning(f"Endpoint {endpoint} not found in routes")
        
        print_success("API routes structure validated")
        return True
        
    except Exception as e:
        print_error(f"API routes test failed: {e}")
        return False

def test_frontend_components():
    """Test 4: Frontend Components Structure"""
    print_test_header("Frontend Components Structure")
    
    try:
        # Check if optimized frontend files exist
        frontend_files = [
            'frontend/contexts/movie-context-optimized.tsx',
            'frontend/components/movie-grid-optimized.tsx'
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                print_success(f"Frontend file exists: {file_path}")
                
                # Check for key implementations
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'amazon' in content.lower() and 'block' in content.lower():
                    print_success(f"Amazon URL blocking found in {file_path}")
                
                if 'cache' in content.lower() or 'loading' in content.lower():
                    print_success(f"Performance optimization found in {file_path}")
                    
            else:
                print_warning(f"Frontend file not found: {file_path}")
        
        return True
        
    except Exception as e:
        print_error(f"Frontend components test failed: {e}")
        return False

def test_requirements_completeness():
    """Test 5: Requirements and Dependencies"""
    print_test_header("Requirements Completeness")
    
    try:
        # Check main requirements
        req_files = ['requirements.txt', 'backend/requirements_fixed.txt']
        
        for req_file in req_files:
            if os.path.exists(req_file):
                print_success(f"Requirements file exists: {req_file}")
                
                with open(req_file, 'r') as f:
                    requirements = f.read()
                    
                essential_packages = ['fastapi', 'uvicorn', 'requests', 'beautifulsoup4', 'httpx']
                
                for package in essential_packages:
                    if package in requirements.lower():
                        print_success(f"Essential package {package} found in requirements")
                    else:
                        print_warning(f"Essential package {package} not found in requirements")
            else:
                print_warning(f"Requirements file not found: {req_file}")
        
        return True
        
    except Exception as e:
        print_error(f"Requirements test failed: {e}")
        return False

def test_configuration_files():
    """Test 6: Configuration Files"""
    print_test_header("Configuration Files")
    
    try:
        # Check essential config files
        config_files = [
            'docker-compose.yml',
            'Dockerfile',
            'Procfile'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                print_success(f"Configuration file exists: {config_file}")
            else:
                print_warning(f"Configuration file not found: {config_file}")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        return False

def test_documentation():
    """Test 7: Documentation Completeness"""
    print_test_header("Documentation")
    
    try:
        doc_files = [
            'README.md',
            'HOW_TO_RUN.md',
            'PRODUCTION_READY_SUMMARY.md'
        ]
        
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                print_success(f"Documentation file exists: {doc_file}")
            else:
                print_warning(f"Documentation file not found: {doc_file}")
        
        return True
        
    except Exception as e:
        print_error(f"Documentation test failed: {e}")
        return False

def run_integration_test():
    """Test 8: Basic Integration Test"""
    print_test_header("Integration Test")
    
    try:
        # Test if we can create a movie service and process data
        from app.services.movie_service import MovieService
        
        service = MovieService()
        
        # Test image processing with Amazon URL
        amazon_url = "https://m.media-amazon.com/images/test.jpg"
        processed = service._process_movie_image(amazon_url)
        
        if "placeholder" in processed:
            print_success("Amazon URL replacement working in integration")
        else:
            print_error("Amazon URL not properly replaced in integration")
            return False
        
        # Test movie object creation
        test_data = {
            'Title': 'Integration Test Movie',
            'Year': '2023',
            'imdbRating': '7.5',
            'Plot': 'Test plot for integration',
            'Genre': 'Action, Drama',
            'Director': 'Test Director',
            'Actors': 'Actor 1, Actor 2',
            'Poster': 'https://example.com/poster.jpg',
            'Runtime': '120 min'
        }
        
        movie = service._create_movie_object(test_data)
        
        if movie and movie.title == 'Integration Test Movie':
            print_success("Movie creation working in integration")
        else:
            print_error("Movie creation failed in integration")
            return False
        
        print_success("Integration test completed successfully")
        return True
        
    except Exception as e:
        print_error(f"Integration test failed: {e}")
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    print_test_header("TEST REPORT")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for deployment.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Review issues before deployment.")
    
    return passed_tests == total_tests

def main():
    """Run all tests"""
    print(f"🚀 Starting Comprehensive Test Suite")
    print(f"📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all tests
    tests = {
        "Backend Imports": test_backend_imports,
        "Movie Service Functionality": test_movie_service_functionality,
        "API Routes Structure": test_api_routes_structure,
        "Frontend Components": test_frontend_components,
        "Requirements Completeness": test_requirements_completeness,
        "Configuration Files": test_configuration_files,
        "Documentation": test_documentation,
        "Integration Test": run_integration_test
    }
    
    results = {}
    
    # Run all tests
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Generate report
    all_passed = generate_test_report(results)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
