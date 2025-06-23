#!/usr/bin/env python3
"""
Quick test to verify errors are fixed
"""
import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_error_fixes():
    """Test that the major errors are fixed"""
    try:
        from backend.app.core.api_manager import APIManager
        
        print("🔧 Testing error fixes...")
        
        # Initialize API manager (this should not cause errors now)
        print("   📡 Initializing API Manager...")
        api_manager = APIManager()
        print("   ✅ API Manager initialized successfully")
        
        # Test a simple search (should work without scraper errors)
        print("   🔍 Testing simple search...")
        results = await api_manager.search_movies("Inception", limit=2)
        
        print(f"   📊 Search completed: {len(results)} results")
        for i, movie in enumerate(results, 1):
            title = movie.get('title', 'NO TITLE')
            print(f"      {i}. {title}")
        
        print("   ✅ Search completed without major errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_error_fixes())
    if success:
        print("\n🎉 ERROR FIXES: Working correctly!")
        print("✅ Major errors have been resolved")
    else:
        print("\n⚠️ ERROR FIXES: Still have issues")
