#!/usr/bin/env python3
"""
Final Production Test - Random Popular Movies/Series
Tests real-time search with various popular titles to ensure no "Unknown Title" issues
"""

import requests
import json
import time
import random

def test_search_endpoint(query):
    """Test the search endpoint with a specific query"""
    try:
        url = "http://localhost:8000/api/movies/search"
        params = {"q": query}
          print(f"🔍 Testing: '{query}'")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                results = data
            else:
                results = data.get('results', [])
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Results: {len(results)} found")
            
            # Check for "Unknown Title" issues
            unknown_count = 0
            valid_titles = []
            
            for i, movie in enumerate(results[:5]):  # Check first 5 results
                title = movie.get('title', 'Unknown Title')
                if title == 'Unknown Title' or not title or title.strip() == '':
                    unknown_count += 1
                    print(f"   ❌ Result {i+1}: {title} (PROBLEM!)")
                else:
                    valid_titles.append(title)
                    print(f"   ✅ Result {i+1}: {title}")
            
            if unknown_count > 0:
                print(f"   🚨 ISSUE: {unknown_count} results with 'Unknown Title'")
                return False
            else:
                print(f"   🎉 SUCCESS: All titles are valid!")
                return True
                
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   💥 Error: {str(e)}")
        return False

def main():
    print("🎬 FINAL PRODUCTION TEST - Popular Movies/Series")
    print("=" * 60)
    print("Testing with random popular titles to ensure no 'Unknown Title' issues\n")
    
    # Popular movies and series to test
    test_queries = [
        "Dune",
        "Game of Thrones", 
        "Stranger Things",
        "The Batman",
        "Breaking Bad",
        "Avengers",
        "Spider-Man",
        "The Matrix",
        "Inception",
        "Interstellar",
        "The Godfather",
        "Pulp Fiction",
        "The Office",
        "Friends",
        "Harry Potter",
        "Star Wars",
        "Lord of the Rings",
        "Black Panther",
        "Iron Man",
        "Thor"
    ]
    
    # Randomly select 10 queries to test
    selected_queries = random.sample(test_queries, 10)
    
    successful_tests = 0
    total_tests = len(selected_queries)
    
    for i, query in enumerate(selected_queries, 1):
        print(f"\n[Test {i}/{total_tests}]")
        success = test_search_endpoint(query)
        if success:
            successful_tests += 1
        
        # Brief pause between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"🎯 FINAL RESULTS:")
    print(f"   ✅ Successful: {successful_tests}/{total_tests}")
    print(f"   ❌ Failed: {total_tests - successful_tests}/{total_tests}")
    print(f"   📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 PRODUCTION READY! All tests passed - No 'Unknown Title' issues found!")
    else:
        print(f"\n🚨 ISSUES DETECTED! {total_tests - successful_tests} tests failed")
        
    return successful_tests == total_tests

if __name__ == "__main__":
    # Wait for servers to be ready
    print("⏳ Waiting for servers to be ready...")
    time.sleep(5)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
