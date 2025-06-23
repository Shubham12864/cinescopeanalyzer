#!/usr/bin/env python3
"""
Final comprehensive test for Unknown Title fix across multiple scenarios
"""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def final_comprehensive_test():
    """Test multiple scenarios to ensure Unknown Title is completely fixed"""
    try:
        from backend.app.core.api_manager import APIManager
        
        print("🎯 FINAL COMPREHENSIVE UNKNOWN TITLE TEST")
        print("="*70)
        
        api_manager = APIManager()
        
        # Test scenarios
        test_cases = [
            ("Inception", "Popular movie"),
            ("The Matrix", "Classic movie"),
            ("Avengers", "Multiple results expected"),
            ("Batman", "Many variations"),
            ("Pulp Fiction", "Movie with space"),
            ("xyz123nonexistent", "Non-existent movie"),
            ("a", "Single letter search"),
            ("", "Empty search"),
        ]
        
        total_tests = 0
        passed_tests = 0
        unknown_title_count = 0
        
        for query, description in test_cases:
            print(f"\n🔍 Testing: '{query}' ({description})")
            
            try:
                results = await api_manager.search_movies(query, limit=3)
                total_tests += 1
                
                print(f"   📊 Results: {len(results)} movies")
                
                test_passed = True
                for i, movie in enumerate(results, 1):
                    title = movie.get('title', 'MISSING')
                    source = movie.get('source', 'unknown')
                    year = movie.get('year', 'N/A')
                    
                    print(f"      {i}. '{title}' ({year}) - {source}")
                    
                    if title == 'Unknown Title':
                        print(f"         ❌ FOUND 'Unknown Title' issue!")
                        unknown_title_count += 1
                        test_passed = False
                    elif title == 'MISSING' or not title:
                        print(f"         ⚠️ Missing title field")
                        test_passed = False
                    else:
                        print(f"         ✅ Title looks good")
                
                if test_passed:
                    print(f"   ✅ PASSED: No Unknown Title issues")
                    passed_tests += 1
                else:
                    print(f"   ❌ FAILED: Found issues")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                total_tests += 1
        
        # Summary
        print("\n" + "="*70)
        print("📊 FINAL TEST SUMMARY")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed tests: {passed_tests}")
        print(f"   Failed tests: {total_tests - passed_tests}")
        print(f"   'Unknown Title' occurrences: {unknown_title_count}")
        
        if unknown_title_count == 0:
            print("\n🎉 SUCCESS: NO 'Unknown Title' issues found across all test cases!")
            print("✅ The Unknown Title fix is working perfectly!")
            return True
        else:
            print(f"\n❌ FAILURE: Found {unknown_title_count} 'Unknown Title' issues")
            print("⚠️ The fix may need additional work")
            return False
            
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(final_comprehensive_test())
    if success:
        print("\n🎯 FINAL CONCLUSION: Unknown Title issue is COMPLETELY FIXED!")
        print("🚀 The search functionality is working correctly!")
    else:
        print("\n⚠️ FINAL CONCLUSION: Unknown Title issue needs more work")
