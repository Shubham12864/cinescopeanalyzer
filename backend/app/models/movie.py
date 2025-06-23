from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel

class Review(BaseModel):
    id: str
    author: str
    content: str
    rating: float
    sentiment: str  # 'positive', 'negative', 'neutral'
    date: str
    source: str = "unknown"  # Track review source (reddit, scraping, api, etc.)
    helpful_votes: int = 0
    total_votes: int = 0

class Movie(BaseModel):
    id: str
    title: str
    year: int
    poster: str
    rating: float
    genre: List[str]
    plot: str
    director: str
    cast: List[str]
    reviews: List[Review] = []
    imdbId: Optional[str] = None
    runtime: Optional[int] = None
    
    # Enhanced fields for multi-source data
    reddit_analysis: Optional[Dict[str, Any]] = None
    scraping_data: Optional[Dict[str, Any]] = None
    awards: List[str] = []
    box_office: Optional[Dict[str, Any]] = None
    trivia: List[str] = []
    technical_specs: Optional[Dict[str, Any]] = None
    alternative_titles: List[str] = []
    production_companies: List[str] = []
    filming_locations: List[str] = []
    
    # Enhanced description data
    enhanced_data: Optional[Dict[str, Any]] = None
    
    # Analysis metadata
    last_updated: str = ""
    data_sources: List[str] = []  # Track which sources provided data
    analysis_completeness: float = 0.0  # 0-1 score of how complete the analysis is

# Enhanced models for comprehensive analysis
class AnalysisRequest(BaseModel):
    movie_title: str
    imdb_id: Optional[str] = None
    year: Optional[int] = None
    include_reddit: bool = True
    include_scraping: bool = True
    include_api_sources: bool = True
    deep_analysis: bool = True

class SentimentAnalysis(BaseModel):
    overall_sentiment: Dict[str, float]
    distribution: Dict[str, int]
    percentiles: Dict[str, float]
    confidence_score: float

class RedditDiscussion(BaseModel):
    subreddit: str
    title: str
    author: str
    score: int
    num_comments: int
    sentiment_score: float
    created_at: datetime
    url: str

class ScrapedReview(BaseModel):
    source: str  # 'imdb', 'rotten_tomatoes', 'metacritic', etc.
    reviewer: str
    rating: Optional[float] = None
    review_text: str
    review_date: Optional[str] = None
    helpful_count: Optional[int] = None

class PlatformRating(BaseModel):
    platform: str
    score: Optional[float] = None
    scale: str  # '10', '100', '5 stars', etc.
    total_ratings: Optional[int] = None
    description: Optional[str] = None

class ComprehensiveMovieData(BaseModel):
    basic_info: Movie
    platform_ratings: List[PlatformRating] = []
    reddit_discussions: List[RedditDiscussion] = []
    scraped_reviews: List[ScrapedReview] = []
    sentiment_analysis: Optional[SentimentAnalysis] = None
    technical_specs: Dict[str, Any] = {}
    box_office: Dict[str, Any] = {}
    awards: List[Dict[str, Any]] = []
    trivia: List[str] = []

class EnhancedMovieAnalysis(BaseModel):
    analysis_id: str
    movie_data: ComprehensiveMovieData
    analysis_metadata: Dict[str, Any]
    data_sources: Dict[str, Any]
    analysis_results: Dict[str, Any]
    comprehensive_insights: Dict[str, Any]
    confidence_metrics: Dict[str, float]
    created_at: datetime
    updated_at: Optional[datetime] = None

class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: int  # 0-100
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None

class CrossPlatformComparison(BaseModel):
    movie_title: str
    platforms_compared: List[str]
    rating_comparison: Dict[str, float]
    sentiment_comparison: Dict[str, float]
    discussion_volume: Dict[str, int]
    consensus_score: float
    outlier_platforms: List[str]

class TrendingDiscussion(BaseModel):
    title: str
    platform: str
    engagement_score: float
    sentiment_trend: str
    discussion_volume: int
    trending_keywords: List[str]

# Analytics models for comprehensive data
class GenreData(BaseModel):
    genre: str
    count: int
    percentage: Optional[float] = 0.0

class ReviewTimelineData(BaseModel):
    date: str
    count: int

class SentimentData(BaseModel):
    positive: int
    negative: int
    neutral: int

class RatingDistributionData(BaseModel):
    rating: float
    count: int

class MovieSummary(BaseModel):
    id: str
    title: str
    rating: float
    year: int

class AnalyticsData(BaseModel):
    totalMovies: int
    totalReviews: int
    averageRating: float
    sentimentDistribution: SentimentData
    ratingDistribution: List[RatingDistributionData]
    genrePopularity: List[GenreData]
    reviewTimeline: List[ReviewTimelineData]
    topRatedMovies: List[MovieSummary]
    recentlyAnalyzed: List[MovieSummary] = []
