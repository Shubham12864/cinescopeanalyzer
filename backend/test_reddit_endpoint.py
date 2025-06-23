#!/usr/bin/env python3
"""
Test Reddit endpoint directly without starting the full server
"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_reddit_endpoint():
    """Test the Reddit reviews endpoint logic directly"""
    print("🧪 Testing Reddit Reviews Endpoint Logic...")
    
    try:
        # Import required modules
        from app.services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer
        from app.services.movie_service import MovieService
        
        # Create a mock movie object
        class MockMovie:
            def __init__(self):
                self.title = "The Matrix"
                self.year = 1999
                self.imdbId = "tt0133093"
        
        # Initialize services
        movie_service = MovieService()
        reddit_analyzer = EnhancedRedditAnalyzer()
        
        print(f"✅ Services initialized. Reddit API available: {reddit_analyzer.reddit_available}")
        
        # Mock movie data
        mock_movie = MockMovie()
        
        # Perform Reddit analysis (simulating the endpoint logic)
        print(f"🧠 Starting Reddit analysis for '{mock_movie.title}' ({mock_movie.year})")
        
        reddit_analysis = await reddit_analyzer.comprehensive_movie_analysis(
            movie_title=mock_movie.title,
            imdb_id=mock_movie.imdbId,
            year=mock_movie.year,
            limit_per_subreddit=50
        )
        
        # Generate summary (simulating the _generate_reddit_summary function)
        def generate_summary(reddit_analysis):
            collection_summary = reddit_analysis.get('collection_summary', {})
            sentiment_analysis = reddit_analysis.get('sentiment_analysis', {})
            overall_sentiment = sentiment_analysis.get('overall_sentiment', {})
            distribution = sentiment_analysis.get('distribution', {})
            content_analysis = reddit_analysis.get('content_analysis', {})
            
            # Calculate sentiment percentage
            total_sentiments = sum(distribution.values()) if distribution else 1
            positive_percentage = ((distribution.get('very_positive', 0) + distribution.get('positive', 0)) / total_sentiments * 100) if total_sentiments > 0 else 0
            negative_percentage = ((distribution.get('very_negative', 0) + distribution.get('negative', 0)) / total_sentiments * 100) if total_sentiments > 0 else 0
            neutral_percentage = (distribution.get('neutral', 0) / total_sentiments * 100) if total_sentiments > 0 else 0
            
            # Determine overall reception
            if positive_percentage > 60:
                reception = "Very Positive"
            elif positive_percentage > 40:
                reception = "Mostly Positive" 
            elif negative_percentage > 60:
                reception = "Very Negative"
            elif negative_percentage > 40:
                reception = "Mostly Negative"
            else:
                reception = "Mixed"
            
            summary = {
                "overall_reception": reception,
                "sentiment_score": round(overall_sentiment.get('mean', 0), 2),
                "total_discussions": collection_summary.get('total_posts', 0),
                "subreddits_analyzed": collection_summary.get('total_subreddits', 0),
                "sentiment_breakdown": {
                    "positive": round(positive_percentage, 1),
                    "negative": round(negative_percentage, 1),
                    "neutral": round(neutral_percentage, 1)
                },
                "key_insights": [
                    "Demo analysis completed successfully",
                    f"Found {collection_summary.get('total_posts', 0)} discussions",
                    f"Community sentiment: {reception}",
                    "Analysis generated using demo data"
                ],
                "discussion_volume": "Moderate",
                "top_keywords": content_analysis.get('keyword_analysis', {}).get('top_keywords', [])[:10]
            }
            
            return summary
        
        summary = generate_summary(reddit_analysis)
        
        # Format response for frontend (simulating the endpoint response)
        response_data = {
            "movie_info": {
                "id": "mock_movie_id",
                "title": mock_movie.title,
                "year": mock_movie.year,
                "imdb_id": mock_movie.imdbId
            },
            "reddit_analysis": reddit_analysis,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
        
        print("📊 Reddit Analysis Endpoint Response:")
        print(f"  - Movie: {response_data['movie_info']['title']} ({response_data['movie_info']['year']})")
        print(f"  - Overall Reception: {summary['overall_reception']}")
        print(f"  - Sentiment Score: {summary['sentiment_score']}")
        print(f"  - Total Discussions: {summary['total_discussions']}")
        print(f"  - Subreddits Analyzed: {summary['subreddits_analyzed']}")
        print(f"  - Positive: {summary['sentiment_breakdown']['positive']}%")
        print(f"  - Negative: {summary['sentiment_breakdown']['negative']}%")
        print(f"  - Neutral: {summary['sentiment_breakdown']['neutral']}%")
        print(f"  - Key Insights: {len(summary['key_insights'])} insights generated")
        print(f"  - Top Keywords: {[k[0] for k in summary['top_keywords'][:5]]}")
        
        # Save to file for inspection
        with open('reddit_analysis_test_result.json', 'w') as f:
            json.dump(response_data, f, indent=2, default=str)
        
        print("📄 Full response saved to: reddit_analysis_test_result.json")
        print("✅ Reddit Reviews Endpoint Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Reddit endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_reddit_endpoint())
    print(f"\n{'🎉 SUCCESS' if success else '💥 FAILED'}: Reddit analyzer is {'ready' if success else 'not working'} for integration!")
    sys.exit(0 if success else 1)
