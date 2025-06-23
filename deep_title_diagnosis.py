#!/usr/bin/env python3
"""
Deep diagnosis of the Unknown Title issue
"""
import sys
import os
import asyncio
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def deep_diagnosis():
    """Deep diagnosis of the search and title mapping"""
    try:
        from backend.app.core.omdb_api_enhanced import OMDbAPI
        from backend.app.core.api_manager import APIManager
        
        print("🔍 DEEP UNKNOWN TITLE DIAGNOSIS")
        print("="*60)
        
        # Step 1: Test OMDB API directly
        print("\n🎬 STEP 1: Testing OMDB API directly...")
        omdb_api = OMDbAPI("2f777f63")
        
        # Test direct OMDB search
        print("   📡 Making direct OMDB search for 'Inception'...")
        raw_results = await omdb_api.search_movies("Inception", limit=2)
        
        print(f"   📊 Raw OMDB results: {len(raw_results)} movies")
        for i, movie in enumerate(raw_results, 1):
            print(f"\n   === MOVIE {i} RAW DATA ===")
            print(f"   Keys available: {list(movie.keys())}")
            print(f"   Title (capital): '{movie.get('Title', 'MISSING')}'")
            print(f"   title (lower): '{movie.get('title', 'MISSING')}'")
            print(f"   Year: '{movie.get('Year', 'MISSING')}'")
            print(f"   Plot: '{movie.get('Plot', 'MISSING')}'")
            
        # Step 2: Test the _dict_to_movie method in detail
        print(f"\n🔧 STEP 2: Testing _dict_to_movie conversion...")
        api_manager = APIManager()
        
        if raw_results:
            for i, raw_movie in enumerate(raw_results, 1):
                print(f"\n   === CONVERSION TEST {i} ===")
                print(f"   Input data:")
                print(f"     Title: '{raw_movie.get('Title', 'MISSING')}'")
                print(f"     title: '{raw_movie.get('title', 'MISSING')}'")
                
                # Manual step-by-step conversion
                title_result = raw_movie.get('title', raw_movie.get('Title', 'Unknown Title'))
                print(f"   Manual title extraction: '{title_result}'")
                
                # Test the actual conversion method
                converted = api_manager._dict_to_movie(raw_movie)
                if converted:
                    print(f"   Converted title: '{converted.get('title', 'MISSING')}'")
                    if converted.get('title') == 'Unknown Title':
                        print("   ❌ PROBLEM FOUND: Conversion producing 'Unknown Title'")
                        print(f"      Original had Title='{raw_movie.get('Title')}' title='{raw_movie.get('title')}'")
                    else:
                        print("   ✅ Conversion looks good")
                else:
                    print("   ❌ PROBLEM: Conversion returned None")
        
        # Step 3: Test the entire search flow step by step
        print(f"\n🌐 STEP 3: Testing complete search flow...")
        
        # Patch the search to see intermediate steps
        original_omdb_search = api_manager.omdb_api.search_movies
        
        async def debug_search(query, limit):
            print(f"   🔍 OMDB search called with: '{query}', limit={limit}")
            results = await original_omdb_search(query, limit)
            print(f"   📊 OMDB returned {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"      {i}. OMDB result title: '{result.get('Title', result.get('title', 'NO TITLE'))}'")
            return results
        
        # Temporarily patch for debugging
        api_manager.omdb_api.search_movies = debug_search
        
        final_results = await api_manager.search_movies("Inception", limit=2)
        
        print(f"\n   📋 Final search results: {len(final_results)} movies")
        for i, movie in enumerate(final_results, 1):
            title = movie.get('title', 'MISSING')
            source = movie.get('source', 'unknown')
            print(f"   {i}. Final title: '{title}' (source: {source})")
            
            if title == 'Unknown Title':
                print(f"      ❌ CRITICAL: Final result has 'Unknown Title'!")
                print(f"      Debug info: {json.dumps(movie, indent=8)}")
            else:
                print(f"      ✅ Good: Final title is correct")
        
        print("\n" + "="*60)
        print("🎯 DEEP DIAGNOSIS COMPLETE")
        
        # Summary
        unknown_count = sum(1 for m in final_results if m.get('title') == 'Unknown Title')
        if unknown_count > 0:
            print(f"❌ FOUND {unknown_count} 'Unknown Title' issues in final results")
            return False
        else:
            print("✅ NO 'Unknown Title' issues found in final results")
            return True
        
    except Exception as e:
        print(f"❌ Deep diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(deep_diagnosis())
    if success:
        print("\n🎉 CONCLUSION: Unknown Title issue appears to be resolved")
    else:
        print("\n⚠️ CONCLUSION: Unknown Title issue still exists and needs fixing")
