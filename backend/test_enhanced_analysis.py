#!/usr/bin/env python3
"""
Comprehensive Movie Analysis Test Script
Tests all enhanced features including Reddit analysis, web scraping, and parallel processing
"""

import asyncio
import json
import time
from datetime import datetime
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.comprehensive_analysis_orchestrator import ComprehensiveMovieAnalysisOrchestrator
from app.services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer

async def test_comprehensive_analysis():
    """Test comprehensive movie analysis with all features"""
    
    print("🎬 CineScope Enhanced Movie Analysis Test")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = ComprehensiveMovieAnalysisOrchestrator()
    
    # Test movies with different characteristics
    test_movies = [
        {
            "title": "The Matrix",
            "imdb_id": "tt0133093",
            "year": 1999,
            "description": "Classic sci-fi with strong online presence"
        },
        {
            "title": "Dune",
            "imdb_id": "tt1160419", 
            "year": 2021,
            "description": "Recent blockbuster with active discussions"
        },
        {
            "title": "Parasite",
            "imdb_id": "tt6751668",
            "year": 2019,
            "description": "Award-winning international film"
        }
    ]
    
    for i, movie in enumerate(test_movies, 1):
        print(f"\n🎭 Test {i}/3: Analyzing '{movie['title']}' ({movie['year']})")
        print(f"📝 Description: {movie['description']}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Run comprehensive analysis
            results = await orchestrator.analyze_movie_comprehensive(
                movie_title=movie["title"],
                imdb_id=movie.get("imdb_id"),
                year=movie.get("year"),
                include_reddit=True,
                include_scraping=True,
                include_api_sources=True,
                deep_analysis=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Display results summary
            print(f"✅ Analysis completed in {duration:.2f} seconds")
            print(f"📊 Analysis ID: {results['analysis_metadata']['analysis_id']}")
            
            # Data sources summary
            data_sources = results.get('data_sources', {})
            print(f"📋 Data Sources Collected:")
            for source, data in data_sources.items():
                status = data.get('status', 'unknown')
                emoji = "✅" if status == 'completed' else "❌"
                print(f"   {emoji} {source.replace('_', ' ').title()}: {status}")
            
            # Reddit analysis summary
            reddit_data = data_sources.get('reddit_analysis', {}).get('data', {})
            if reddit_data and 'collection_summary' in reddit_data:
                reddit_summary = reddit_data['collection_summary']
                print(f"🗣️  Reddit Analysis:")
                print(f"   • Total Posts: {reddit_summary.get('total_posts', 0)}")
                print(f"   • Subreddits: {reddit_summary.get('total_subreddits', 0)}")
                print(f"   • Date Range: {reddit_summary.get('date_range', {}).get('span_days', 0)} days")
            
            # Sentiment analysis summary
            sentiment_data = reddit_data.get('sentiment_analysis', {})
            if sentiment_data and 'overall_sentiment' in sentiment_data:
                sentiment = sentiment_data['overall_sentiment']
                print(f"💭 Sentiment Analysis:")
                print(f"   • Mean Sentiment: {sentiment.get('mean', 0):.3f}")
                print(f"   • Distribution: {sentiment_data.get('distribution', {})}")
            
            # Save detailed results
            output_file = f"test_results_{movie['title'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Detailed results saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            continue
        
        print(f"⏱️  Waiting 5 seconds before next test...")
        await asyncio.sleep(5)
    
    print("\n🎉 All tests completed!")

async def test_reddit_analyzer_only():
    """Test Reddit analyzer independently"""
    
    print("\n🔍 Testing Reddit Analyzer (Standalone)")
    print("=" * 50)
    
    reddit_analyzer = EnhancedRedditAnalyzer()
    
    test_movie = "The Dark Knight"
    print(f"🎬 Analyzing Reddit discussions for: {test_movie}")
    
    try:
        start_time = time.time()
        
        results = await reddit_analyzer.comprehensive_movie_analysis(
            movie_title=test_movie,
            year=2008,
            limit_per_subreddit=20
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Reddit analysis completed in {duration:.2f} seconds")
        
        # Display summary
        collection_summary = results.get('collection_summary', {})
        print(f"📊 Collection Summary:")
        print(f"   • Total Posts: {collection_summary.get('total_posts', 0)}")
        print(f"   • Subreddits Searched: {collection_summary.get('total_subreddits', 0)}")
        print(f"   • Search Queries: {collection_summary.get('search_queries_used', [])}")
        
        # Sentiment summary
        sentiment_analysis = results.get('sentiment_analysis', {})
        if sentiment_analysis and 'overall_sentiment' in sentiment_analysis:
            sentiment = sentiment_analysis['overall_sentiment']
            print(f"💭 Sentiment Overview:")
            print(f"   • Mean: {sentiment.get('mean', 0):.3f}")
            print(f"   • Std Dev: {sentiment.get('std', 0):.3f}")
            print(f"   • Range: {sentiment.get('min', 0):.3f} to {sentiment.get('max', 0):.3f}")
        
        # Save results
        output_file = f"reddit_test_{test_movie.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Reddit analysis failed: {str(e)}")

async def test_quick_analysis():
    """Test quick analysis mode"""
    
    print("\n⚡ Testing Quick Analysis Mode")
    print("=" * 40)
    
    orchestrator = ComprehensiveMovieAnalysisOrchestrator()
    
    test_movie = "Inception"
    print(f"🎬 Quick analysis for: {test_movie}")
    
    try:
        start_time = time.time()
        
        results = await orchestrator.analyze_movie_comprehensive(
            movie_title=test_movie,
            imdb_id="tt1375666",
            year=2010,
            include_reddit=True,
            include_scraping=False,  # Skip for speed
            include_api_sources=True,
            deep_analysis=False  # Skip for speed
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Quick analysis completed in {duration:.2f} seconds")
        print(f"📊 Analysis ID: {results['analysis_metadata']['analysis_id']}")
        
        # Show what was included/excluded
        metadata = results['analysis_metadata']
        components = metadata.get('components_included', {})
        print(f"🔧 Components Used:")
        for component, enabled in components.items():
            emoji = "✅" if enabled else "⏸️"
            print(f"   {emoji} {component.replace('_', ' ').title()}")
        
    except Exception as e:
        print(f"❌ Quick analysis failed: {str(e)}")

async def test_api_endpoints():
    """Test API endpoints directly"""
    
    print("\n🌐 Testing API Integration")
    print("=" * 35)
    
    import aiohttp
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health Check: {data.get('message', 'OK')}")
                else:
                    print(f"❌ Health Check Failed: Status {response.status}")
    except Exception as e:
        print(f"❌ API Connection Failed: {str(e)}")
        print("💡 Make sure the backend server is running on localhost:8000")

def display_system_info():
    """Display system information for debugging"""
    
    print("🖥️  System Information")
    print("=" * 25)
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    # Check for required environment variables
    required_env_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET', 
        'OMDB_API_KEY',
        'TMDB_API_KEY'
    ]
    
    print("\n🔐 Environment Variables:")
    for var in required_env_vars:
        value = os.getenv(var)
        status = "✅ Set" if value else "❌ Missing"
        print(f"   {var}: {status}")
    
    if not any(os.getenv(var) for var in required_env_vars):
        print("\n⚠️  Warning: No environment variables detected.")
        print("   Make sure to copy .env.example to .env and add your API keys.")

async def main():
    """Main test function"""
    
    print("🎬 CineScope Enhanced Movie Analyzer - Comprehensive Test Suite")
    print("=" * 80)
    
    display_system_info()
    
    print("\n🚀 Starting Test Suite...")
    
    # Menu for test selection
    print("\nSelect test to run:")
    print("1. Full Comprehensive Analysis (3 movies)")
    print("2. Reddit Analyzer Only")
    print("3. Quick Analysis Mode")
    print("4. API Endpoints Test")
    print("5. All Tests (Sequential)")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            await test_comprehensive_analysis()
        elif choice == "2":
            await test_reddit_analyzer_only()
        elif choice == "3":
            await test_quick_analysis()
        elif choice == "4":
            await test_api_endpoints()
        elif choice == "5":
            await test_api_endpoints()
            await test_quick_analysis()
            await test_reddit_analyzer_only()
            await test_comprehensive_analysis()
        else:
            print("❌ Invalid choice. Running quick test...")
            await test_quick_analysis()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
    
    print("\n🏁 Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
