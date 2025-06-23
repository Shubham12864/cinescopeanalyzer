import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
from dataclasses import dataclass
import logging

# Import all analysis modules
from .enhanced_reddit_analyzer import EnhancedRedditAnalyzer
from ..scraper.comprehensive_movie_spider import ComprehensiveMovieSpider
from ..analyzer.sentiment_analyzer import SentimentAnalyzer
from ..analyzer.rating_analyzer import RatingAnalyzer
from ..core.omdb_api import OMDBAPIManager
from ..core.tmdb_api import TMDBAPIManager

@dataclass
class AnalysisTask:
    """Represents an analysis task with metadata"""
    task_id: str
    task_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    progress: int = 0

class ComprehensiveMovieAnalysisOrchestrator:
    """
    Orchestrates simultaneous execution of multiple analysis components:
    1. Scrapy-based web scraping (IMDB, RT, Metacritic, etc.)
    2. Reddit API analysis
    3. Official API data (OMDB, TMDB)
    4. Sentiment analysis
    5. Rating analysis
    6. Cross-platform comparison
    """
    
    def __init__(self):
        """Initialize all analysis components"""
        self.reddit_analyzer = EnhancedRedditAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.rating_analyzer = RatingAnalyzer()
        self.omdb_api = OMDBAPIManager()
        self.tmdb_api = TMDBAPIManager()
        
        # Task management
        self.active_tasks: Dict[str, AnalysisTask] = {}
        self.completed_analyses: Dict[str, Dict] = {}
        
        # Concurrency settings
        self.max_workers = 8
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=4)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def analyze_movie_comprehensive(self, 
                                        movie_title: str, 
                                        imdb_id: str = None,
                                        year: int = None,
                                        include_reddit: bool = True,
                                        include_scraping: bool = True,
                                        include_api_sources: bool = True,
                                        deep_analysis: bool = True) -> Dict:
        """
        Perform comprehensive movie analysis with parallel execution
        
        Args:
            movie_title: Movie title to analyze
            imdb_id: IMDB ID for precise identification
            year: Release year for better filtering
            include_reddit: Whether to include Reddit analysis
            include_scraping: Whether to include web scraping
            include_api_sources: Whether to include official API sources
            deep_analysis: Whether to perform deep sentiment/content analysis
            
        Returns:
            Comprehensive analysis results
        """
        
        analysis_id = f"analysis_{int(time.time())}_{hash(movie_title) % 10000}"
        start_time = datetime.now()
        
        self.logger.info(f"Starting comprehensive analysis for '{movie_title}' (ID: {analysis_id})")
        
        # Initialize analysis structure
        comprehensive_results = {
            'analysis_metadata': {
                'analysis_id': analysis_id,
                'movie_title': movie_title,
                'imdb_id': imdb_id,
                'year': year,
                'started_at': start_time.isoformat(),
                'components_included': {
                    'reddit_analysis': include_reddit,
                    'web_scraping': include_scraping,
                    'api_sources': include_api_sources,
                    'deep_analysis': deep_analysis
                }
            },
            'data_sources': {},
            'analysis_results': {},
            'cross_platform_comparison': {},
            'comprehensive_insights': {}
        }
        
        # Create concurrent tasks
        tasks = []
        
        # Task 1: Reddit Analysis
        if include_reddit:
            reddit_task = self._create_analysis_task(
                'reddit_analysis',
                self._run_reddit_analysis(movie_title, imdb_id, year)
            )
            tasks.append(('reddit_analysis', reddit_task))
        
        # Task 2: Web Scraping
        if include_scraping:
            scraping_task = self._create_analysis_task(
                'web_scraping',
                self._run_web_scraping_analysis(movie_title, imdb_id, year)
            )
            tasks.append(('web_scraping', scraping_task))
        
        # Task 3: Official API Sources
        if include_api_sources:
            api_task = self._create_analysis_task(
                'api_sources',
                self._run_api_analysis(movie_title, imdb_id, year)
            )
            tasks.append(('api_sources', api_task))
        
        # Task 4: Initial Sentiment Analysis (can run while others complete)
        if deep_analysis:
            initial_sentiment_task = self._create_analysis_task(
                'initial_sentiment',
                self._run_initial_sentiment_analysis(movie_title)
            )
            tasks.append(('initial_sentiment', initial_sentiment_task))
        
        # Execute all tasks concurrently
        self.logger.info(f"Executing {len(tasks)} concurrent analysis tasks...")
        
        try:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Process results
            for i, (task_name, _) in enumerate(tasks):
                result = results[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Task {task_name} failed: {result}")
                    comprehensive_results['data_sources'][task_name] = {
                        'status': 'failed',
                        'error': str(result)
                    }
                else:
                    self.logger.info(f"Task {task_name} completed successfully")
                    comprehensive_results['data_sources'][task_name] = {
                        'status': 'completed',
                        'data': result
                    }
            
            # Phase 2: Deep Analysis with collected data
            if deep_analysis:
                await self._perform_deep_analysis(comprehensive_results)
            
            # Phase 3: Cross-platform comparison and insights
            await self._generate_comprehensive_insights(comprehensive_results)
            
            # Finalize
            comprehensive_results['analysis_metadata']['completed_at'] = datetime.now().isoformat()
            comprehensive_results['analysis_metadata']['total_duration_seconds'] = (
                datetime.now() - start_time
            ).total_seconds()
            
            # Store results
            self.completed_analyses[analysis_id] = comprehensive_results
            
            self.logger.info(f"Comprehensive analysis completed for '{movie_title}' in "
                           f"{comprehensive_results['analysis_metadata']['total_duration_seconds']:.2f} seconds")
            
            return comprehensive_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            comprehensive_results['analysis_metadata']['error'] = str(e)
            comprehensive_results['analysis_metadata']['status'] = 'failed'
            return comprehensive_results
    
    async def _create_analysis_task(self, task_type: str, coroutine) -> Any:
        """Create and track an analysis task"""
        task_id = f"{task_type}_{int(time.time())}"
        
        task = AnalysisTask(
            task_id=task_id,
            task_type=task_type,
            status='running',
            started_at=datetime.now()
        )
        
        self.active_tasks[task_id] = task
        
        try:
            result = await coroutine
            task.status = 'completed'
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 100
            return result
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.completed_at = datetime.now()
            raise e
        finally:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def _run_reddit_analysis(self, movie_title: str, imdb_id: str = None, year: int = None) -> Dict:
        """Run comprehensive Reddit analysis"""
        self.logger.info(f"Starting Reddit analysis for '{movie_title}'")
        
        try:
            reddit_results = await self.reddit_analyzer.comprehensive_movie_analysis(
                movie_title=movie_title,
                imdb_id=imdb_id,
                year=year,
                limit_per_subreddit=75  # Increased for more comprehensive data
            )
            
            self.logger.info(f"Reddit analysis completed: {reddit_results['collection_summary']['total_posts']} posts analyzed")
            return reddit_results
            
        except Exception as e:
            self.logger.error(f"Reddit analysis failed: {e}")
            return {'error': str(e), 'source': 'reddit'}
    
    async def _run_web_scraping_analysis(self, movie_title: str, imdb_id: str = None, year: int = None) -> Dict:
        """Run comprehensive web scraping analysis"""
        self.logger.info(f"Starting web scraping analysis for '{movie_title}'")
        
        try:
            # This would integrate with Scrapy
            # For now, return a placeholder structure
            scraping_results = {
                'imdb_data': await self._scrape_imdb_comprehensive(movie_title, imdb_id),
                'rotten_tomatoes_data': await self._scrape_rotten_tomatoes(movie_title),
                'metacritic_data': await self._scrape_metacritic(movie_title),
                'letterboxd_data': await self._scrape_letterboxd(movie_title),
                'box_office_data': await self._scrape_box_office(movie_title),
                'scraping_metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'sources_scraped': ['imdb', 'rotten_tomatoes', 'metacritic', 'letterboxd', 'box_office'],
                    'total_data_points': 0  # Will be calculated
                }
            }
            
            # Calculate total data points
            total_points = sum(
                len(data) if isinstance(data, (list, dict)) else 1 
                for data in scraping_results.values() 
                if data and not isinstance(data, dict) or (isinstance(data, dict) and 'error' not in data)
            )
            scraping_results['scraping_metadata']['total_data_points'] = total_points
            
            self.logger.info(f"Web scraping completed: {total_points} data points collected")
            return scraping_results
            
        except Exception as e:
            self.logger.error(f"Web scraping failed: {e}")
            return {'error': str(e), 'source': 'web_scraping'}
    
    async def _run_api_analysis(self, movie_title: str, imdb_id: str = None, year: int = None) -> Dict:
        """Run analysis using official APIs"""
        self.logger.info(f"Starting API analysis for '{movie_title}'")
        
        try:
            # Run API calls concurrently
            api_tasks = [
                self._get_omdb_data(movie_title, imdb_id, year),
                self._get_tmdb_data(movie_title, year),
                self._get_additional_api_data(movie_title, imdb_id)
            ]
            
            omdb_data, tmdb_data, additional_data = await asyncio.gather(
                *api_tasks, return_exceptions=True
            )
            
            api_results = {
                'omdb_data': omdb_data if not isinstance(omdb_data, Exception) else {'error': str(omdb_data)},
                'tmdb_data': tmdb_data if not isinstance(tmdb_data, Exception) else {'error': str(tmdb_data)},
                'additional_data': additional_data if not isinstance(additional_data, Exception) else {'error': str(additional_data)},
                'api_metadata': {
                    'queried_at': datetime.now().isoformat(),
                    'apis_used': ['omdb', 'tmdb', 'additional_sources'],
                    'success_rate': sum(1 for data in [omdb_data, tmdb_data, additional_data] 
                                      if not isinstance(data, Exception)) / 3
                }
            }
            
            self.logger.info(f"API analysis completed with {api_results['api_metadata']['success_rate']:.2%} success rate")
            return api_results
            
        except Exception as e:
            self.logger.error(f"API analysis failed: {e}")
            return {'error': str(e), 'source': 'api_analysis'}
    
    async def _run_initial_sentiment_analysis(self, movie_title: str) -> Dict:
        """Run initial sentiment analysis while other tasks are running"""
        self.logger.info(f"Starting initial sentiment analysis for '{movie_title}'")
        
        try:
            # This would run basic sentiment analysis on any immediately available data
            initial_sentiment = {
                'title_sentiment': self.sentiment_analyzer.analyze_text(movie_title),
                'baseline_metrics': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'preliminary_indicators': {}
                }
            }
            
            return initial_sentiment
            
        except Exception as e:
            self.logger.error(f"Initial sentiment analysis failed: {e}")
            return {'error': str(e), 'source': 'initial_sentiment'}
    
    async def _perform_deep_analysis(self, comprehensive_results: Dict) -> None:
        """Perform deep analysis on collected data"""
        self.logger.info("Starting deep analysis phase...")
        
        try:
            # Extract all text data for comprehensive sentiment analysis
            all_text_data = self._extract_all_text_data(comprehensive_results)
            
            # Concurrent deep analysis tasks
            deep_analysis_tasks = [
                self._deep_sentiment_analysis(all_text_data),
                self._content_theme_analysis(all_text_data),
                self._rating_correlation_analysis(comprehensive_results),
                self._temporal_trend_analysis(comprehensive_results),
                self._audience_segmentation_analysis(comprehensive_results)
            ]
            
            deep_results = await asyncio.gather(*deep_analysis_tasks, return_exceptions=True)
            
            comprehensive_results['analysis_results'] = {
                'deep_sentiment': deep_results[0] if not isinstance(deep_results[0], Exception) else {'error': str(deep_results[0])},
                'content_themes': deep_results[1] if not isinstance(deep_results[1], Exception) else {'error': str(deep_results[1])},
                'rating_correlations': deep_results[2] if not isinstance(deep_results[2], Exception) else {'error': str(deep_results[2])},
                'temporal_trends': deep_results[3] if not isinstance(deep_results[3], Exception) else {'error': str(deep_results[3])},
                'audience_segmentation': deep_results[4] if not isinstance(deep_results[4], Exception) else {'error': str(deep_results[4])}
            }
            
            self.logger.info("Deep analysis phase completed")
            
        except Exception as e:
            self.logger.error(f"Deep analysis failed: {e}")
            comprehensive_results['analysis_results'] = {'error': str(e)}
    
    async def _generate_comprehensive_insights(self, comprehensive_results: Dict) -> None:
        """Generate comprehensive insights from all collected data"""
        self.logger.info("Generating comprehensive insights...")
        
        try:
            insights = {
                'cross_platform_sentiment_comparison': self._compare_sentiment_across_platforms(comprehensive_results),
                'rating_consensus_analysis': self._analyze_rating_consensus(comprehensive_results),
                'audience_vs_critic_divide': self._analyze_audience_critic_divide(comprehensive_results),
                'discussion_volume_analysis': self._analyze_discussion_volume(comprehensive_results),
                'content_quality_indicators': self._assess_content_quality(comprehensive_results),
                'recommendation_score': self._calculate_recommendation_score(comprehensive_results),
                'detailed_breakdown': self._create_detailed_breakdown(comprehensive_results),
                'data_confidence_metrics': self._calculate_confidence_metrics(comprehensive_results)
            }
            
            comprehensive_results['comprehensive_insights'] = insights
            self.logger.info("Comprehensive insights generation completed")
            
        except Exception as e:
            self.logger.error(f"Insights generation failed: {e}")
            comprehensive_results['comprehensive_insights'] = {'error': str(e)}
    
    # Helper methods for data extraction and analysis
    def _extract_all_text_data(self, results: Dict) -> List[str]:
        """Extract all text data from comprehensive results"""
        text_data = []
        
        # Extract from Reddit data
        reddit_data = results.get('data_sources', {}).get('reddit_analysis', {}).get('data', {})
        if reddit_data and 'reddit_analysis' in reddit_data:
            for discussion in reddit_data['reddit_analysis'].get('discussions', []):
                text_data.append(discussion.get('title', ''))
                text_data.append(discussion.get('selftext', ''))
                for comment in discussion.get('comments', []):
                    text_data.append(comment.get('body', ''))
        
        # Extract from scraping data
        scraping_data = results.get('data_sources', {}).get('web_scraping', {}).get('data', {})
        if scraping_data:
            for source_key, source_data in scraping_data.items():
                if isinstance(source_data, dict):
                    # Extract reviews, descriptions, etc.
                    if 'reviews' in source_data:
                        for review in source_data['reviews']:
                            if isinstance(review, dict):
                                text_data.append(review.get('text', ''))
                                text_data.append(review.get('title', ''))
        
        return [text for text in text_data if text and len(text.strip()) > 0]
    
    # Placeholder implementations for scraping methods (would be replaced with actual Scrapy integration)
    async def _scrape_imdb_comprehensive(self, movie_title: str, imdb_id: str = None) -> Dict:
        """Comprehensive IMDB scraping"""
        # This would use the ComprehensiveMovieSpider
        return {'placeholder': 'imdb_data', 'source': 'imdb'}
    
    async def _scrape_rotten_tomatoes(self, movie_title: str) -> Dict:
        """Rotten Tomatoes scraping"""
        return {'placeholder': 'rt_data', 'source': 'rotten_tomatoes'}
    
    async def _scrape_metacritic(self, movie_title: str) -> Dict:
        """Metacritic scraping"""
        return {'placeholder': 'metacritic_data', 'source': 'metacritic'}
    
    async def _scrape_letterboxd(self, movie_title: str) -> Dict:
        """Letterboxd scraping"""
        return {'placeholder': 'letterboxd_data', 'source': 'letterboxd'}
    
    async def _scrape_box_office(self, movie_title: str) -> Dict:
        """Box Office scraping"""
        return {'placeholder': 'box_office_data', 'source': 'box_office'}
    
    # Placeholder implementations for API methods
    async def _get_omdb_data(self, movie_title: str, imdb_id: str = None, year: int = None) -> Dict:
        """Get OMDB data"""
        try:
            return await self.omdb_api.get_movie_details(title=movie_title, imdb_id=imdb_id, year=year)
        except Exception as e:
            return {'error': str(e), 'source': 'omdb'}
    
    async def _get_tmdb_data(self, movie_title: str, year: int = None) -> Dict:
        """Get TMDB data"""
        try:
            return await self.tmdb_api.search_movie(query=movie_title, year=year)
        except Exception as e:
            return {'error': str(e), 'source': 'tmdb'}
    
    async def _get_additional_api_data(self, movie_title: str, imdb_id: str = None) -> Dict:
        """Get additional API data"""
        return {'placeholder': 'additional_api_data'}
    
    # Placeholder implementations for analysis methods
    async def _deep_sentiment_analysis(self, text_data: List[str]) -> Dict:
        """Deep sentiment analysis"""
        return {'placeholder': 'deep_sentiment_analysis'}
    
    async def _content_theme_analysis(self, text_data: List[str]) -> Dict:
        """Content theme analysis"""
        return {'placeholder': 'content_theme_analysis'}
    
    async def _rating_correlation_analysis(self, results: Dict) -> Dict:
        """Rating correlation analysis"""
        return {'placeholder': 'rating_correlation_analysis'}
    
    async def _temporal_trend_analysis(self, results: Dict) -> Dict:
        """Temporal trend analysis"""
        return {'placeholder': 'temporal_trend_analysis'}
    
    async def _audience_segmentation_analysis(self, results: Dict) -> Dict:
        """Audience segmentation analysis"""
        return {'placeholder': 'audience_segmentation_analysis'}
    
    def _compare_sentiment_across_platforms(self, results: Dict) -> Dict:
        """Compare sentiment across different platforms"""
        return {'placeholder': 'cross_platform_sentiment'}
    
    def _analyze_rating_consensus(self, results: Dict) -> Dict:
        """Analyze rating consensus"""
        return {'placeholder': 'rating_consensus'}
    
    def _analyze_audience_critic_divide(self, results: Dict) -> Dict:
        """Analyze audience vs critic divide"""
        return {'placeholder': 'audience_critic_divide'}
    
    def _analyze_discussion_volume(self, results: Dict) -> Dict:
        """Analyze discussion volume"""
        return {'placeholder': 'discussion_volume'}
    
    def _assess_content_quality(self, results: Dict) -> Dict:
        """Assess content quality"""
        return {'placeholder': 'content_quality'}
    
    def _calculate_recommendation_score(self, results: Dict) -> Dict:
        """Calculate recommendation score"""
        return {'placeholder': 'recommendation_score'}
    
    def _create_detailed_breakdown(self, results: Dict) -> Dict:
        """Create detailed breakdown"""
        return {'placeholder': 'detailed_breakdown'}
    
    def _calculate_confidence_metrics(self, results: Dict) -> Dict:
        """Calculate confidence metrics"""
        return {'placeholder': 'confidence_metrics'}
    
    def get_analysis_status(self, analysis_id: str) -> Optional[Dict]:
        """Get status of a running analysis"""
        if analysis_id in self.active_tasks:
            task = self.active_tasks[analysis_id]
            return {
                'task_id': task.task_id,
                'status': task.status,
                'progress': task.progress,
                'started_at': task.started_at.isoformat(),
                'error': task.error
            }
        elif analysis_id in self.completed_analyses:
            return {
                'status': 'completed',
                'completed_at': self.completed_analyses[analysis_id]['analysis_metadata'].get('completed_at')
            }
        else:
            return None
    
    def get_completed_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get completed analysis results"""
        return self.completed_analyses.get(analysis_id)
