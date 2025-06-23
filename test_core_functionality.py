#!/usr/bin/env python3
"""
🎬 CineScopeAnalyzer - Core Functionality Test
============================================================
Test core functionality: search, suggestions, and frontend
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_core_functionality():
    """Test core functionality that should be working"""
    print("🎬 CineScopeAnalyzer - Core Functionality Test")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'status': 'UNKNOWN'
    }
    
    # Test 1: Backend Health
    print("🔧 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            results['tests']['backend_health'] = True
        else:
            print(f"❌ Backend health failed: {response.status_code}")
            results['tests']['backend_health'] = False
    except Exception as e:
        print(f"❌ Backend health error: {e}")
        results['tests']['backend_health'] = False
    
    # Test 2: Movie Search
    print("🔍 Testing Movie Search...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/movies/search", params={"q": "inception"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                print(f"✅ Search returned {len(data)} results")
                print(f"   First result: {data[0]['title']} ({data[0]['year']})")
                results['tests']['movie_search'] = True
            else:
                print("❌ Search returned no results")
                results['tests']['movie_search'] = False
        else:
            print(f"❌ Search failed: {response.status_code}")
            results['tests']['movie_search'] = False
    except Exception as e:
        print(f"❌ Search error: {e}")
        results['tests']['movie_search'] = False
    
    # Test 3: Movie Suggestions
    print("💡 Testing Movie Suggestions...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/movies/suggestions", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                print(f"✅ Suggestions returned {len(data)} results")
                print(f"   Sample titles: {[m['title'] for m in data[:3]]}")
                results['tests']['suggestions'] = True
            else:
                print("❌ Suggestions returned no results")
                results['tests']['suggestions'] = False
        else:
            print(f"❌ Suggestions failed: {response.status_code}")
            results['tests']['suggestions'] = False
    except Exception as e:
        print(f"❌ Suggestions error: {e}")
        results['tests']['suggestions'] = False
    
    # Test 4: Movie Details
    print("📄 Testing Movie Details...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/movies/tt1375666", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Movie details retrieved: {data['title']}")
            results['tests']['movie_details'] = True
        else:
            print(f"❌ Movie details failed: {response.status_code}")
            results['tests']['movie_details'] = False
    except Exception as e:
        print(f"❌ Movie details error: {e}")
        results['tests']['movie_details'] = False
    
    # Test 5: Frontend Accessibility
    print("🎨 Testing Frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            results['tests']['frontend'] = True
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            results['tests']['frontend'] = False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        results['tests']['frontend'] = False
    
    # Calculate overall status
    total_tests = len(results['tests'])
    passed_tests = sum(1 for result in results['tests'].values() if result)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate == 100:
        status = "🟢 EXCELLENT"
    elif success_rate >= 80:
        status = "🟡 GOOD"
    elif success_rate >= 60:
        status = "⚠️ FAIR"
    else:
        status = "🔴 POOR"
    
    results['status'] = status
    results['success_rate'] = success_rate
    results['passed_tests'] = passed_tests
    results['total_tests'] = total_tests
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CORE FUNCTIONALITY TEST RESULTS")
    print("=" * 60)
    print(f"Overall Status: {status}")
    print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    print("")
    
    for test_name, result in results['tests'].items():
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name.replace('_', ' ').title()}")
    
    print(f"\n📅 Test completed at: {results['timestamp']}")
    print("=" * 60)
    
    # Save results
    with open("core_test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = test_core_functionality()
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:
        exit(0)  # Success
    else:
        exit(1)  # Failure
