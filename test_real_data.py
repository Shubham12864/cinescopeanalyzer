import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.core.api_manager import APIManager
from backend.app.services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer

async def test_real_data():
    """Test that we're getting real data, not demo data"""
    print("🔍 Testing Real Data Integration")
    print("=" * 50)
    
    # Test API Manager
    api = APIManager()
    print("✅ API Manager initialized")
    
    # Test search with real data
    print(f"\n🔍 Testing search for 'inception'...")
    results = await api.search_movies("inception", limit=3)
    
    if results:
        print(f"✅ Found {len(results)} movies:")
        for i, movie in enumerate(results, 1):
            print(f"  {i}. {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
            print(f"     Source: {movie.get('source', 'Unknown')}")
            print(f"     Plot: {movie.get('plot', 'No plot')[:100]}...")
            print(f"     Rating: {movie.get('rating', 'N/A')}")
            
            # Check if this is demo data
            if movie.get('source') == 'fallback' or 'demo' in str(movie.get('source', '')).lower():
                print(f"     ⚠️ WARNING: This appears to be demo/fallback data!")
            else:
                print(f"     ✅ Real data confirmed")
            print()
    else:
        print("❌ No results found")
      # Test Reddit analyzer
    print("\n🔍 Testing Reddit analyzer for 'Inception'...")
    reddit = EnhancedRedditAnalyzer()
    
    try:
        analysis = await reddit.comprehensive_movie_analysis("Inception")
        
        if analysis:
            print("✅ Reddit analysis successful:")
            print(f"   Posts analyzed: {analysis.get('total_posts', 0)}")
            print(f"   Overall sentiment: {analysis.get('overall_sentiment', 'Unknown')}")
            print(f"   Sentiment score: {analysis.get('sentiment_distribution', {}).get('average_score', 'N/A')}")
              # Check for discussions
            discussions = analysis.get('detailed_discussions', [])
            if discussions:
                print(f"   Discussions found: {len(discussions)}")
                for i, disc in enumerate(discussions[:2], 1):
                    if isinstance(disc, dict):
                        print(f"     {i}. {disc.get('title', 'No title')[:50]}...")
                        print(f"        Upvotes: {disc.get('upvotes', 0)}")
                        print(f"        Comments: {disc.get('comment_count', 0)}")
                        print(f"        Content: {disc.get('content', '')[:100]}...")
                    else:
                        print(f"     {i}. Discussion data format issue: {type(disc)}")
            else:
                print("   ⚠️ No discussions found")
                
        else:
            print("❌ Reddit analysis failed or returned empty")
            
    except Exception as e:
        print(f"❌ Reddit analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Real Data Test Summary:")
    print("   • Search functionality tested")
    print("   • Reddit analysis tested")
    print("   • Data sources verified")

if __name__ == "__main__":
    asyncio.run(test_real_data())
