from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Union
import asyncio
import uuid
from datetime import datetime
import logging

from ...models.movie import AnalysisRequest

# Initialize router and logger
router = APIRouter(prefix="/api/v1", tags=["Enhanced Movie Analysis"])
logger = logging.getLogger(__name__)

# Try to import enhanced services (optional dependencies)
try:
    from ...services.comprehensive_analysis_orchestrator import ComprehensiveAnalysisOrchestrator
    from ...services.enhanced_reddit_analyzer import EnhancedRedditAnalyzer
    ENHANCED_SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced services not available: {e}")
    ENHANCED_SERVICES_AVAILABLE = False
    # Create dummy classes for demo mode
    class ComprehensiveAnalysisOrchestrator:
        def __init__(self):
            pass
    class EnhancedRedditAnalyzer:
        def __init__(self):
            pass

# In-memory storage for analysis status (in production, use Redis or database)
analysis_status_store = {}

@router.post("/movies/analyze/comprehensive")
async def start_comprehensive_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """
    Start comprehensive movie analysis with parallel execution of:
    - Reddit discussion analysis
    - Multi-platform web scraping (IMDB, RT, Metacritic, etc.)
    - Official API data collection (OMDB, TMDB)
    - Advanced sentiment analysis
    - Cross-platform comparison
    """
    
    analysis_id = str(uuid.uuid4())
    
    # Validate request
    if not request.movie_title:
        raise HTTPException(status_code=400, detail="Movie title is required")
    
    # Initialize analysis status
    analysis_status_store[analysis_id] = {
        'id': analysis_id,
        'status': 'starting',
        'movie_title': request.movie_title,
        'started_at': datetime.now().isoformat(),
        'progress': 0,
        'message': 'Initializing comprehensive analysis...',
        'components': {
            'reddit_analysis': 'pending',
            'web_scraping': 'pending',
            'api_sources': 'pending',
            'sentiment_analysis': 'pending',
            'cross_platform_comparison': 'pending'
        }
    }
    
    # Start comprehensive analysis in background
    try:
        orchestrator = ComprehensiveAnalysisOrchestrator()
        background_tasks.add_task(
            _run_comprehensive_analysis,
            analysis_id,
            request.movie_title,
            orchestrator,
            {
                'include_reddit': request.include_reddit,
                'include_scraping': request.include_scraping,
                'reddit_limit': request.reddit_limit,
                'scraping_platforms': request.scraping_platforms or ['imdb', 'rotten_tomatoes', 'metacritic']
            }
        )
        
        logger.info(f"🚀 Started comprehensive analysis for '{request.movie_title}' with ID: {analysis_id}")
        
    except Exception as e:
        logger.error(f"Failed to start comprehensive analysis: {e}")
        analysis_status_store[analysis_id]['status'] = 'error'
        analysis_status_store[analysis_id]['message'] = f"Failed to initialize: {str(e)}"
    
    logger.info(f"Demo analysis {analysis_id} for '{request.movie_title}'")
    
    return {
        'analysis_id': analysis_id,
        'status': 'demo_mode',
        'message': 'Enhanced analysis endpoint ready. Install dependencies to enable full functionality.',
        'movie_title': request.movie_title,
        'setup_required': [
            'Install Reddit API dependencies: pip install praw',
            'Install Scrapy: pip install scrapy',
            'Install NLP libraries: pip install nltk textblob',
            'Configure API keys in .env file',
            'Run setup_enhanced.bat to complete installation'
        ],
        'check_status_endpoint': f'/api/v1/movies/analyze/{analysis_id}/status',
        'documentation': 'See ENHANCED_FEATURES.md for full setup instructions'
    }

@router.get("/movies/analyze/{analysis_id}/status")
async def get_analysis_status(analysis_id: str) -> Dict:
    """Get the current status of a comprehensive analysis"""
    
    if analysis_id not in analysis_status_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    status = analysis_status_store[analysis_id]
    return status

@router.post("/movies/analyze/quick")
async def quick_movie_analysis(
    movie_title: str = Query(..., description="Movie title to analyze"),
    imdb_id: Optional[str] = Query(None, description="IMDB ID for precise identification"),
    year: Optional[int] = Query(None, description="Release year")
) -> Dict:
    """
    Quick movie analysis with essential data only
    - Basic API data (OMDB, TMDB)
    - Quick sentiment analysis
    - Basic Reddit metrics
    
    NOTE: Demo mode - install enhanced dependencies for full functionality
    """
    
    return {
        'status': 'demo_mode',
        'analysis_type': 'quick',
        'movie_title': movie_title,
        'message': 'Quick analysis endpoint ready. Install enhanced dependencies to enable full functionality.',
        'demo_results': {
            'movie_info': {
                'title': movie_title,
                'imdb_id': imdb_id,
                'year': year,
                'status': 'demo_data'
            },
            'enhancement_features': {
                'reddit_analysis': 'Install praw for Reddit API integration',
                'web_scraping': 'Install scrapy for multi-platform scraping',
                'sentiment_analysis': 'Install nltk and textblob for NLP',
                'api_integration': 'Configure OMDB and TMDB API keys'
            }
        },
        'setup_instructions': 'Run setup_enhanced.bat to install all dependencies'
    }

@router.get("/movies/trending-discussions")
async def get_trending_movie_discussions(
    platform: str = Query("reddit", description="Platform to check: 'reddit', 'all'"),
    time_period: str = Query("week", description="Time period: 'day', 'week', 'month'"),
    limit: int = Query(20, description="Number of results to return")
) -> Dict:
    """
    Get trending movie discussions across platforms
    
    NOTE: Demo mode - requires Reddit API setup for full functionality
    """
    
    return {
        'platform': platform,
        'time_period': time_period,
        'status': 'demo_mode',
        'message': 'Trending discussions endpoint ready. Configure Reddit API for live data.',
        'demo_trending': [
            {
                'title': 'Sample trending discussion about popular movies',
                'platform': 'reddit',
                'engagement_score': 85.5,
                'discussion_volume': 1250,
                'sentiment': 'positive'
            }
        ],
        'setup_required': [
            'Get Reddit API credentials at reddit.com/prefs/apps',
            'Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env',
            'Install praw: pip install praw',
            'Run full setup: setup_enhanced.bat'
        ]
    }

@router.get("/analytics/platform-comparison")
async def get_platform_comparison_analytics(
    movie_title: str = Query(..., description="Movie title to compare across platforms"),
    platforms: List[str] = Query(["reddit", "imdb", "rotten_tomatoes", "metacritic"], 
                                description="Platforms to compare")
) -> Dict:
    """
    Get cross-platform comparison analytics for a movie
    
    NOTE: Demo mode - requires full enhanced setup for real comparison data
    """
    
    return {
        'movie_title': movie_title,
        'platforms_compared': platforms,
        'status': 'demo_mode',
        'message': 'Platform comparison endpoint ready. Install scraping infrastructure for live data.',
        'demo_comparison': {
            'reddit': {'sentiment': 0.65, 'discussion_volume': 1200},
            'imdb': {'rating': 8.2, 'review_count': 45000},
            'rotten_tomatoes': {'critics_score': 87, 'audience_score': 91},
            'metacritic': {'metascore': 82, 'user_score': 8.9}
        },
        'enhanced_features': {
            'real_time_scraping': 'Install scrapy for live data collection',
            'reddit_integration': 'Configure Reddit API for discussion analysis',
            'sentiment_analysis': 'Install NLP libraries for advanced analysis',
            'cross_platform_insights': 'Full setup enables comprehensive comparison'
        },
        'setup_guide': 'See ENHANCED_FEATURES.md for complete installation guide'
    }

@router.get("/enhanced/info")
async def get_enhanced_info() -> Dict:
    """Get information about enhanced features and setup status"""
    
    return {
        'enhanced_edition': 'CineScope Movie Analyzer - Enhanced Edition',
        'version': '2.0.0',
        'status': 'demo_mode',
        'message': 'Enhanced features available - complete setup to enable full functionality',
        'new_features': [
            'Reddit Discussion Analysis across 20+ subreddits',
            'Multi-platform Web Scraping (IMDB, RT, Metacritic, Letterboxd)',
            'Advanced Sentiment Analysis with NLP',
            'Cross-platform Rating Comparison',
            'Parallel Processing for 3-5x faster analysis',
            'Real-time Discussion Trending',
            'Comprehensive Movie Insights'
        ],
        'setup_steps': [
            '1. Run setup_enhanced.bat (Windows) or setup_enhanced.sh (Linux/Mac)',
            '2. Get Reddit API credentials at reddit.com/prefs/apps',
            '3. Get TMDB API key at themoviedb.org/settings/api',
            '4. Update .env file with your API keys',
            '5. Test with: python test_enhanced_analysis.py'
        ],
        'dependencies_required': [
            'scrapy==2.11.0 (for web scraping)',
            'praw==7.7.1 (for Reddit API)',
            'nltk==3.8.1 (for NLP analysis)',
            'textblob==0.17.1 (for sentiment analysis)',
            'spacy==3.7.2 (for advanced NLP)',
            'transformers==4.36.0 (for ML models)'
        ],
        'documentation': {
            'setup_guide': 'ENHANCED_FEATURES.md',
            'api_docs': 'http://localhost:8000/docs',
            'test_script': 'test_enhanced_analysis.py'
        }
    }

# Background task functions

async def _run_comprehensive_analysis(
    analysis_id: str,
    movie_title: str,
    orchestrator: ComprehensiveAnalysisOrchestrator,
    options: Dict
):
    """Run comprehensive analysis in background"""
    try:
        # Update status to running
        analysis_status_store[analysis_id]['status'] = 'running'
        analysis_status_store[analysis_id]['message'] = 'Analysis in progress...'
        analysis_status_store[analysis_id]['progress'] = 10
        
        # Run comprehensive analysis
        result = await orchestrator.analyze_movie_comprehensive(
            movie_title=movie_title,
            include_reddit=options.get('include_reddit', True),
            include_scraping=options.get('include_scraping', True),
            reddit_limit=options.get('reddit_limit', 100),
            scraping_platforms=options.get('scraping_platforms', ['imdb', 'rotten_tomatoes', 'metacritic'])
        )
        
        # Update status with results
        analysis_status_store[analysis_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Analysis completed successfully',
            'completed_at': datetime.now().isoformat(),
            'results': result,
            'components': {
                'reddit_analysis': 'completed',
                'web_scraping': 'completed',
                'api_sources': 'completed',
                'sentiment_analysis': 'completed',
                'cross_platform_comparison': 'completed'
            }
        })
        
        logger.info(f"✅ Comprehensive analysis completed for '{movie_title}' (ID: {analysis_id})")
        
    except Exception as e:
        logger.error(f"❌ Comprehensive analysis failed for '{movie_title}' (ID: {analysis_id}): {e}")
        analysis_status_store[analysis_id].update({
            'status': 'error',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}',
            'error_at': datetime.now().isoformat(),
            'components': {
                'reddit_analysis': 'error',
                'web_scraping': 'error',
                'api_sources': 'error',
                'sentiment_analysis': 'error',
                'cross_platform_comparison': 'error'
            }
        })

async def _run_quick_analysis(
    analysis_id: str,
    movie_title: str,
    orchestrator: ComprehensiveAnalysisOrchestrator
):
    """Run quick analysis in background"""
    try:
        # Update status to running
        analysis_status_store[analysis_id]['status'] = 'running'
        analysis_status_store[analysis_id]['message'] = 'Quick analysis in progress...'
        analysis_status_store[analysis_id]['progress'] = 20
        
        # Run quick analysis (API only, no scraping)
        result = await orchestrator.analyze_movie_quick(movie_title)
        
        # Update status with results
        analysis_status_store[analysis_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Quick analysis completed successfully',
            'completed_at': datetime.now().isoformat(),
            'results': result
        })
        
        logger.info(f"⚡ Quick analysis completed for '{movie_title}' (ID: {analysis_id})")
        
    except Exception as e:
        logger.error(f"❌ Quick analysis failed for '{movie_title}' (ID: {analysis_id}): {e}")
        analysis_status_store[analysis_id].update({
            'status': 'error',
            'progress': 0,
            'message': f'Quick analysis failed: {str(e)}',
            'error_at': datetime.now().isoformat()
        })
