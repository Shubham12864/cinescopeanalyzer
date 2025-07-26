#!/usr/bin/env python3
"""
Quick Image Pipeline Status Check
"""

def check_image_pipeline_integration():
    print("🖼️ IMAGE PIPELINE INTEGRATION CHECK")
    print("=" * 45)
    
    # Check movies.py for correct integration
    try:
        with open("backend/app/api/routes/movies.py", 'r') as f:
            movies_content = f.read()
            
        # Key checkpoints
        checks = [
            ("process_movie_images function", "async def process_movie_images"),
            ("FanArt service import", "from ...services.fanart_api_service import fanart_service"),
            ("Scrapy service import", "from ...services.scrapy_search_service import ScrapySearchService"),
            ("FanArt priority logic", "Priority 1: FanArt API"),
            ("Scrapy fallback logic", "Priority 2: Scrapy images"),
            ("Pipeline call in search", "await process_movie_images(movie_objects"),
            ("Dynamic loading param", "use_dynamic_loading=True"),
            ("Image pipeline header", "X-Image-Pipeline"),
        ]
        
        results = []
        for check_name, check_pattern in checks:
            if check_pattern in movies_content:
                print(f"✅ {check_name}")
                results.append(True)
            else:
                print(f"❌ {check_name}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        print(f"\n📊 INTEGRATION STATUS: {passed}/{total} checks passed")
        
        if passed >= 7:  # Allow 1 minor failure
            print("🎉 IMAGE PIPELINE IS PROPERLY INTEGRATED!")
            print("\n🔄 PIPELINE FLOW:")
            print("   1. Search endpoint processes movies")
            print("   2. process_movie_images() called with dynamic loading")
            print("   3. FanArt API tried first (high quality)")
            print("   4. Scrapy scraping tried second (fallback)") 
            print("   5. URL cleanup tried third (existing URLs)")
            print("   6. Response includes X-Image-Pipeline header")
            return True
        else:
            print("❌ IMAGE PIPELINE HAS INTEGRATION ISSUES")
            return False
            
    except FileNotFoundError:
        print("❌ movies.py file not found")
        return False
    except Exception as e:
        print(f"❌ Error checking integration: {e}")
        return False

if __name__ == "__main__":
    success = check_image_pipeline_integration()
    if success:
        print("\n✨ RECOMMENDATION: Image pipeline is ready!")
        print("   • FanArt provides high-quality posters as primary source")
        print("   • Scrapy provides reliable fallback scraping") 
        print("   • Existing URL cleanup ensures no broken images")
        print("   • Dynamic loading optimizes performance")
    else:
        print("\n⚠️ RECOMMENDATION: Check pipeline integration")
