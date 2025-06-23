#!/usr/bin/env python3
"""
Simple test to verify the Unknown Title fix
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.core.api_manager import APIManager

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

async def quick_test():
    """Quick test of search functionality"""
    print("🔍 Quick test of movie search functionality")
    
    api_manager = APIManager()
    
    # Test multiple search terms
    test_queries = ["Batman", "Inception", "Avengers", "Matrix"]
    
    for query in test_queries:
        print(f"\n🎬 Testing: '{query}'")
        results = await api_manager.search_movies(query, limit=2)
        
        print(f"   Results: {len(results)}")
        for i, movie in enumerate(results):
            title = movie.get('title', 'NO TITLE')
            source = movie.get('source', 'unknown')
            print(f"   {i+1}. {title} ({source})")
            
            # Check for Unknown Title issue
            if title == 'Unknown Title':
                print(f"   ❌ FOUND UNKNOWN TITLE ISSUE!")
                return False
    
    print("\n✅ All tests passed - no 'Unknown Title' issues found!")
    return True

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    if success:
        print("\n🎉 SUCCESS: Unknown Title issue appears to be FIXED!")
    else:
        print("\n❌ FAILURE: Unknown Title issue still exists.")
