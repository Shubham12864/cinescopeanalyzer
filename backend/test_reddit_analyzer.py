#!/usr/bin/env python3
"""
Simple test script for Reddit analyzer
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_reddit_analyzer():
    """Test the Reddit analyzer with demo data"""
    print("🧪 Testing Reddit Analyzer...")
    
    try:
        from app.services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer
        
        # Initialize analyzer
        analyzer = EnhancedRedditAnalyzer()
        print(f"✅ Reddit Analyzer initialized. API available: {analyzer.reddit_available}")
        
        # Test with a sample movie
        print("🎬 Testing with 'The Matrix' (1999)...")
        
        result = await analyzer.comprehensive_movie_analysis(
            movie_title="The Matrix",
            year=1999,
            limit_per_subreddit=25
        )
        
        print("📊 Analysis Results:")
        print(f"  - Total posts: {result['collection_summary']['total_posts']}")
        print(f"  - Subreddits: {result['collection_summary']['total_subreddits']}")
        print(f"  - Sentiment score: {result['sentiment_analysis']['overall_sentiment']['mean']:.3f}")
        print(f"  - Overall reception: {result.get('summary', {}).get('overall_reception', 'N/A')}")
        
        # Test top keywords
        keywords = result['content_analysis']['keyword_analysis']['top_keywords'][:5]
        print(f"  - Top keywords: {[k[0] for k in keywords]}")
        
        print("✅ Reddit Analyzer test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Reddit analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reddit_analyzer())
    sys.exit(0 if success else 1)
