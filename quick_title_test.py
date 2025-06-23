#!/usr/bin/env python3
"""
Quick verification that Unknown Title issue is fixed
"""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def quick_test():
    """Quick test to verify titles are not 'Unknown Title'"""
    try:
        from backend.app.core.api_manager import APIManager
        
        print("🔧 Quick test for Unknown Title fix...")
        
        # Initialize API manager
        api_manager = APIManager()
        
        # Test search for a well-known movie
        print("\n📽️ Testing search for 'Batman'...")
        results = await api_manager.search_movies("Batman", limit=3)
        
        print(f"\n✅ Found {len(results)} results:")
        success = True
        for i, movie in enumerate(results[:3], 1):
            title = movie.get('title', 'NO TITLE')
            year = movie.get('year', 'NO YEAR')
            source = movie.get('source', 'unknown')
            print(f"   {i}. '{title}' ({year}) - Source: {source}")
            
            # Check for "Unknown Title" issue
            if title == "Unknown Title":
                print(f"   ❌ FOUND 'Unknown Title' issue in result {i}")
                success = False
            elif title and title != 'NO TITLE':
                print(f"   ✅ Title looks good: '{title}'")
                
        if success:
            print("\n🎉 SUCCESS: No 'Unknown Title' issues found!")
            print("✅ The fix appears to be working correctly!")
        else:
            print("\n❌ FAILED: 'Unknown Title' issues still exist")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    if success:
        print("\n🎯 CONCLUSION: Unknown Title issue is FIXED!")
    else:
        print("\n⚠️ CONCLUSION: Unknown Title issue still needs work")
