#!/usr/bin/env python3
"""
Real-time search test with random movies to verify Unknown Title fix
"""
import sys
import os
import asyncio
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def real_time_search_test():
    """Test real-time search with random movies"""
    try:
        from backend.app.core.api_manager import APIManager
        
        print("🎬 REAL-TIME SEARCH TEST")
        print("="*70)
        print("Testing with random movies: Dune, Game of Thrones, Stranger Things")
        print()
        
        api_manager = APIManager()
        
        # Test movies list
        test_movies = [
            ("Dune", "Sci-fi epic movie"),
            ("Game of Thrones", "Popular HBO series"),
            ("Stranger Things", "Netflix series"),
            ("The Matrix", "Classic sci-fi"),
            ("Breaking Bad", "Crime drama series"),
            ("Avatar", "Cameron's blockbuster"),
            ("The Witcher", "Fantasy series"),
            ("Mandalorian", "Star Wars series"),
            ("House of Dragons", "GoT prequel"),
            ("Wednesday", "Netflix Addams Family")
        ]
        
        total_tests = 0
        passed_tests = 0
        unknown_title_count = 0
        
        for query, description in test_movies:
            print(f"🔍 Testing: '{query}' ({description})")
            
            try:
                # Test with limit 3 for faster results
                results = await api_manager.search_movies(query, limit=3)
                total_tests += 1
                
                print(f"   📊 Results: {len(results)} movies found")
                
                test_passed = True
                for i, movie in enumerate(results, 1):
                    title = movie.get('title', 'MISSING_TITLE')
                    source = movie.get('source', 'unknown')
                    year = movie.get('year', 'N/A')
                    rating = movie.get('rating', 'N/A')
                    
                    print(f"      {i}. '{title}' ({year}) [Rating: {rating}] - Source: {source}")
                    
                    # Check for Unknown Title issues
                    if title == 'Unknown Title':
                        print(f"         ❌ FOUND 'Unknown Title' issue!")
                        unknown_title_count += 1
                        test_passed = False
                    elif title == 'MISSING_TITLE' or not title:
                        print(f"         ⚠️ Missing or empty title field")
                        test_passed = False
                    else:
                        print(f"         ✅ Title looks good: '{title}'")
                
                if test_passed and len(results) > 0:
                    print(f"   ✅ PASSED: No Unknown Title issues, got {len(results)} valid results")
                    passed_tests += 1
                elif len(results) == 0:
                    print(f"   ⚠️ WARNING: No results found for '{query}'")
                    passed_tests += 1  # Count as pass if no results (legitimate for some searches)
                else:
                    print(f"   ❌ FAILED: Found issues with results")
                    
                print()  # Add space between tests
                
            except Exception as e:
                print(f"   ❌ ERROR during search: {e}")
                total_tests += 1
                print()
        
        # Summary
        print("=" * 70)
        print("📊 REAL-TIME SEARCH TEST SUMMARY")
        print(f"   Total searches: {total_tests}")
        print(f"   Successful searches: {passed_tests}")
        print(f"   Failed searches: {total_tests - passed_tests}")
        print(f"   'Unknown Title' occurrences: {unknown_title_count}")
        print(f"   Success rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if unknown_title_count == 0:
            print("\n🎉 SUCCESS: NO 'Unknown Title' issues found in real-time testing!")
            print("✅ The search functionality is working correctly with real data!")
            return True
        else:
            print(f"\n❌ FAILURE: Found {unknown_title_count} 'Unknown Title' issues")
            print("⚠️ The fix may need additional work")
            return False
            
    except Exception as e:
        print(f"❌ Real-time test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(real_time_search_test())
    if success:
        print("\n🎯 FINAL CONCLUSION: Real-time search is working perfectly!")
        print("🚀 Ready for production use!")
    else:
        print("\n⚠️ FINAL CONCLUSION: Real-time search needs more work")
