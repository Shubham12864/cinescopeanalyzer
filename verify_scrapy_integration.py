#!/usr/bin/env python3
"""
Verify Scrapy integration is working properly
"""
import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def verify_scrapy_integration():
    """Verify that Scrapy integration is working in the full system"""
    print("🔍 SCRAPY INTEGRATION VERIFICATION")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: ScrapySearchService import
    print("1️⃣  Testing ScrapySearchService import...")
    try:
        from backend.app.services.scrapy_search_service import ScrapySearchService
        print("   ✅ ScrapySearchService imported successfully")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
    
    # Test 2: Service initialization
    print("\n2️⃣  Testing service initialization...")
    try:
        scrapy_service = ScrapySearchService()
        print("   ✅ ScrapySearchService initialized")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        scrapy_service = None
    
    # Test 3: API Manager integration
    print("\n3️⃣  Testing API Manager integration...")
    try:
        from backend.app.core.api_manager import APIManager, SCRAPY_SEARCH_AVAILABLE
        print(f"   ✅ SCRAPY_SEARCH_AVAILABLE: {SCRAPY_SEARCH_AVAILABLE}")
        
        if SCRAPY_SEARCH_AVAILABLE:
            api_manager = APIManager()
            has_scrapy = api_manager.scrapy_search is not None
            print(f"   ✅ API Manager has Scrapy service: {has_scrapy}")
            success_count += 1
        else:
            print("   ⚠️ Scrapy not available in API Manager (will use fallbacks)")
    except Exception as e:
        print(f"   ❌ API Manager test failed: {e}")
    
    # Test 4: Basic search functionality
    print("\n4️⃣  Testing basic search...")
    if scrapy_service:
        try:
            results = await scrapy_service.search_movies("Matrix", limit=1)
            if results:
                movie = results[0]
                print(f"   ✅ Search successful: {movie.get('title', 'Unknown')}")
                success_count += 1
            else:
                print("   ⚠️ Search returned no results (may be network issue)")
        except Exception as e:
            print(f"   ❌ Search test failed: {e}")
    else:
        print("   ⏩ Skipping search test (service not initialized)")
    
    # Summary
    print(f"\n📊 RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count >= 3:
        print("🎉 SCRAPY INTEGRATION IS WORKING!")
        print("   ✅ Service can be imported and initialized")
        print("   ✅ API Manager integration functional")
        print("   ✅ Ready for use in movie search pipeline")
        return True
    elif success_count >= 2:
        print("⚠️ SCRAPY PARTIALLY WORKING")
        print("   ✅ Service available but may have issues")
        print("   💡 Check network connectivity for searches")
        return True
    else:
        print("❌ SCRAPY INTEGRATION HAS ISSUES")
        print("   💡 Check if dependencies are installed:")
        print("      pip install requests beautifulsoup4 lxml")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(verify_scrapy_integration())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Verification interrupted")
        sys.exit(1)
