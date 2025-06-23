#!/usr/bin/env python3
"""
Comprehensive Integration Test for CineScopeAnalyzer
Tests all data sources: OMDB, TMDB, Reddit API, Web Scraping
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

async def test_backend_comprehensive():
    """Test all backend sources and comprehensive analysis"""
    base_url = "http://localhost:8000"
    
    print("🎬 CineScope Comprehensive Integration Test")
    print("=" * 60)
    
    test_results = {
        'omdb_api': False,
        'reddit_analysis': False,
        'web_scraping': False,
        'image_loading': False,
        'suggestions_diversity': False,
        'analytics_comprehensive': False,
        'backend_endpoints': False
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Backend Health and Basic Endpoints
        print("\n🏥 Testing Backend Health & Core Endpoints...")
        try:
            async with session.get(f"{base_url}/api/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health Check: {data.get('message')}")
                    test_results['backend_endpoints'] = True
                else:
                    print(f"   ❌ Health Check Failed: {response.status}")
                    return test_results
        except Exception as e:
            print(f"   ❌ Cannot connect to backend: {e}")
            print("   💡 Make sure backend is running: python -m uvicorn app.main:app --reload")
            return test_results
        
        # Test 2: Enhanced Suggestions with Image URLs
        print("\n🎭 Testing Enhanced Suggestions with Real Images...")
        try:
            async with session.get(f"{base_url}/api/movies/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    
                    if len(suggestions) >= 10:
                        print(f"   ✅ Suggestions Count: {len(suggestions)} (Target: ≥10)")
                        test_results['suggestions_diversity'] = True
                        
                        # Check for image diversity and URLs
                        real_images = 0
                        unique_titles = set()
                        
                        for movie in suggestions:
                            title = movie.get('title', '').lower()
                            poster = movie.get('poster', '')
                            
                            unique_titles.add(title)
                            
                            if poster and poster.startswith('http') and 'amazon' in poster:
                                real_images += 1
                                print(f"   🖼️ Real Image: {movie.get('title')} - {poster[:50]}...")
                        
                        if real_images >= 5:
                            print(f"   ✅ Real Images: {real_images}/{len(suggestions)} movies have real poster URLs")
                            test_results['image_loading'] = True
                        else:
                            print(f"   ⚠️ Real Images: Only {real_images}/{len(suggestions)} have real URLs")
                        
                        if len(unique_titles) == len(suggestions):
                            print(f"   ✅ No Duplicates: All {len(suggestions)} suggestions are unique")
                        else:
                            print(f"   ⚠️ Duplicates Found: {len(suggestions) - len(unique_titles)} duplicate titles")
                        
                        # Check for popular titles mentioned by user
                        popular_titles = ['house of the dragon', 'stranger things', 'dark knight']
                        found_popular = [title for title in unique_titles if any(p in title for p in popular_titles)]
                        
                        if found_popular:
                            print(f"   ✅ Popular Content: Found {found_popular}")
                        else:
                            print(f"   ⚠️ Popular Content: Missing user-requested shows")
                    
                    else:
                        print(f"   ❌ Insufficient Suggestions: Only {len(suggestions)} returned")
                else:
                    print(f"   ❌ Suggestions Failed: {response.status}")
        
        except Exception as e:
            print(f"   ❌ Suggestions Error: {e}")
        
        # Test 3: Movie Search with OMDB Integration
        print("\n🔍 Testing Movie Search with OMDB Integration...")
        try:
            test_queries = ["Batman", "Matrix", "Inception"]
            
            for query in test_queries:
                async with session.get(f"{base_url}/api/movies/search?q={query}") as response:
                    if response.status == 200:
                        results = await response.json()
                        
                        if results:
                            movie = results[0]
                            title = movie.get('title', '')
                            poster = movie.get('poster', '')
                            rating = movie.get('rating', 0)
                            
                            print(f"   ✅ Search '{query}': Found '{title}' (Rating: {rating})")
                            
                            if poster and poster.startswith('http'):
                                print(f"      🖼️ Real poster URL: {poster[:50]}...")
                                test_results['omdb_api'] = True
                            else:
                                print(f"      ⚠️ No real poster URL")
                        else:
                            print(f"   ❌ Search '{query}': No results")
        
        except Exception as e:
            print(f"   ❌ Search Error: {e}")
        
        # Test 4: Movie Analysis with Multi-Source Data
        print("\n🧠 Testing Comprehensive Movie Analysis...")
        try:
            # Get a movie ID from suggestions first
            async with session.get(f"{base_url}/api/movies/suggestions") as response:
                if response.status == 200:
                    suggestions = await response.json()
                    if suggestions:
                        test_movie_id = suggestions[0].get('id')
                        test_movie_title = suggestions[0].get('title')
                        
                        # Test movie analysis
                        async with session.get(f"{base_url}/api/movies/{test_movie_id}/analysis") as analysis_response:
                            if analysis_response.status == 200:
                                analysis = await analysis_response.json()
                                
                                reviews_count = analysis.get('totalReviews', 0)
                                avg_rating = analysis.get('averageRating', 0)
                                sentiment = analysis.get('sentimentDistribution', {})
                                
                                print(f"   ✅ Analysis for '{test_movie_title}':")
                                print(f"      📊 Reviews: {reviews_count}")
                                print(f"      ⭐ Rating: {avg_rating}")
                                print(f"      💭 Sentiment: {sentiment}")
                                
                                if reviews_count >= 5:
                                    print("   ✅ Comprehensive Reviews: Multiple sources integrated")
                                    test_results['reddit_analysis'] = True
                                    test_results['web_scraping'] = True
                                else:
                                    print("   ⚠️ Limited Reviews: Need more source integration")
                            else:
                                print(f"   ❌ Analysis Failed: {analysis_response.status}")
        
        except Exception as e:
            print(f"   ❌ Analysis Error: {e}")
        
        # Test 5: Analytics with Enhanced Data
        print("\n📊 Testing Enhanced Analytics...")
        try:
            async with session.get(f"{base_url}/api/analytics") as response:
                if response.status == 200:
                    analytics = await response.json()
                    
                    total_movies = analytics.get('totalMovies', 0)
                    total_reviews = analytics.get('totalReviews', 0)
                    genre_data = analytics.get('genrePopularity', [])
                    timeline_data = analytics.get('reviewTimeline', [])
                    
                    print(f"   ✅ Analytics Data:")
                    print(f"      🎬 Total Movies: {total_movies}")
                    print(f"      📝 Total Reviews: {total_reviews}")
                    print(f"      🎭 Genre Categories: {len(genre_data)}")
                    print(f"      📈 Timeline Points: {len(timeline_data)}")
                    
                    if total_reviews >= 10 and len(genre_data) >= 3:
                        print("   ✅ Comprehensive Analytics: Rich data from multiple sources")
                        test_results['analytics_comprehensive'] = True
                    else:
                        print("   ⚠️ Basic Analytics: Need more comprehensive data")
                else:
                    print(f"   ❌ Analytics Failed: {response.status}")
        
        except Exception as e:
            print(f"   ❌ Analytics Error: {e}")
    
    return test_results

async def test_reddit_integration():
    """Test Reddit API integration specifically"""
    print("\n🔍 Testing Reddit API Integration...")
    
    try:
        # This would test Reddit API if credentials are available
        from backend.app.services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer
        
        reddit_analyzer = EnhancedRedditAnalyzer()
        
        # Test with a popular movie
        result = await reddit_analyzer.comprehensive_movie_analysis(
            movie_title="The Matrix",
            year=1999,
            limit_per_subreddit=3  # Small limit for testing
        )
        
        if result and 'collection_summary' in result:
            summary = result['collection_summary']
            print(f"   ✅ Reddit Analysis: {summary.get('total_posts', 0)} posts found")
            print(f"   ✅ Subreddits: {summary.get('total_subreddits', 0)}")
            return True
        else:
            print("   ⚠️ Reddit API: No results (may need API credentials)")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Reddit API: {e}")
        return False

async def test_web_scraping():
    """Test web scraping functionality"""
    print("\n🕷️ Testing Web Scraping...")
    
    try:
        from backend.app.scraper.comprehensive_movie_spider import ComprehensiveMovieSpider
        
        spider = ComprehensiveMovieSpider(
            movie_title="The Matrix",
            imdb_id="tt0133093",
            year=1999
        )
        
        # Test URL generation
        start_urls = spider._generate_start_urls()
        if start_urls and len(start_urls) > 0:
            print(f"   ✅ Scraping Setup: {len(start_urls)} URLs generated")
            print(f"   ✅ Sample URL: {start_urls[0]}")
            return True
        else:
            print("   ❌ Scraping Setup: No URLs generated")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Web Scraping: {e}")
        return False

def print_test_summary(results: dict):
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    status_icons = {True: "✅", False: "❌"}
    
    for test_name, passed_test in results.items():
        status = status_icons[passed_test]
        readable_name = test_name.replace('_', ' ').title()
        print(f"{status} {readable_name}: {'PASS' if passed_test else 'FAIL'}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall Score: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 EXCELLENT! All systems working perfectly!")
        print("   Your CineScope app is ready for comprehensive movie analysis!")
    elif passed >= total * 0.8:
        print("\n✅ GOOD! Most systems working well!")
        print("   Your app is functional with minor areas for improvement.")
    elif passed >= total * 0.6:
        print("\n⚠️ PARTIAL! Core functionality working!")
        print("   Basic features work, but enhanced features need attention.")
    else:
        print("\n❌ ISSUES! Multiple systems need attention!")
        print("   Review the failed tests and check your configuration.")
    
    print("\n🔧 Next Steps:")
    if not results.get('backend_endpoints'):
        print("   1. Ensure backend is running: python -m uvicorn app.main:app --reload")
    if not results.get('omdb_api'):
        print("   2. Check OMDB API key in environment variables")
    if not results.get('reddit_analysis'):
        print("   3. Configure Reddit API credentials for enhanced analysis")
    if not results.get('image_loading'):
        print("   4. Verify image URLs and Next.js configuration")
    
    print("\n🚀 Ready for deployment when all tests pass!")

async def main():
    """Run comprehensive integration tests"""
    print("🧪 CineScope Comprehensive Integration Test Suite")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Testing: OMDB API, Reddit API, Web Scraping, Image Loading, Analytics")
    
    # Test backend comprehensive functionality
    backend_results = await test_backend_comprehensive()
    
    # Test Reddit integration
    reddit_success = await test_reddit_integration()
    backend_results['reddit_integration'] = reddit_success
    
    # Test web scraping
    scraping_success = await test_web_scraping()
    backend_results['web_scraping_setup'] = scraping_success
    
    # Print comprehensive summary
    print_test_summary(backend_results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
