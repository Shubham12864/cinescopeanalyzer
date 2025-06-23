import praw
import prawcore
import asyncio
import aiohttp
import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
from textblob import TextBlob
import nltk
from collections import Counter, defaultdict
import pandas as pd
import numpy as np

class EnhancedRedditAnalyzer:
    """
    Enhanced Reddit analyzer for comprehensive movie discussion analysis.
    Provides deep sentiment analysis, trend tracking, and community insights.
    """
    
    def __init__(self):
        """Initialize Reddit API connection and NLP tools"""
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'CineScopeAnalyzer/2.0 (Enhanced Movie Analysis)')
        
        # Check if Reddit credentials are available
        self.reddit_available = bool(self.reddit_client_id and self.reddit_client_secret and 
                                   self.reddit_client_id != 'your_reddit_client_id_here')
        
        if self.reddit_available:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_client_secret,
                    user_agent=self.reddit_user_agent
                )
                # Test the connection
                self.reddit.user.me()
                print("✅ Reddit API connection established successfully")
            except Exception as e:
                print(f"⚠️ Reddit API connection failed: {e}")
                self.reddit_available = False
                self.reddit = None
        else:
            print("⚠️ Reddit API credentials not configured. Using demo mode.")
            self.reddit = None
        
        # Enhanced subreddit list with categories
        self.subreddits = {
            'general_movies': ['movies', 'film', 'flicks', 'MovieSuggestions', 'MovieDetails', 'movies_public'],
            'genre_specific': ['horror', 'scifi', 'ActionMovies', 'MoviesCriterion', 'animation', 'Documentary'],
            'franchise_specific': ['MarvelStudios', 'DC_Cinematic', 'StarWars', 'HarryPotter', 'lotr'],
            'discussion_focused': ['TrueFilm', 'moviecritic', 'FilmIndustry', 'movies_serious'],
            'rating_focused': ['IMDbFilmGeneral', 'letterboxd', 'MovieRatings'],
            'casual_discussion': ['MovieNights', 'tipofmytongue', 'FandomeMovies', 'movie_discussion']
        }
        
        # Initialize NLP tools
        self._initialize_nltk()
        
    def _initialize_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
        except:
            pass
      async def comprehensive_movie_analysis(self, movie_title: str, imdb_id: str = None, 
                                         year: int = None, limit_per_subreddit: int = 50) -> Dict:
        """
        Perform comprehensive Reddit analysis for a movie
        
        Args:
            movie_title: Movie title to search for
            imdb_id: IMDB ID for more precise searching
            year: Release year for better filtering
            limit_per_subreddit: Max posts per subreddit
            
        Returns:
            Comprehensive analysis dictionary
        """
        
        # If Reddit API is not available, return demo data
        if not self.reddit_available:
            return self._generate_demo_analysis(movie_title, imdb_id, year)
        
        # Generate search queries
        search_queries = self._generate_search_queries(movie_title, year)
        
        # Collect all posts and comments
        all_posts = []
        subreddit_stats = {}
        
        tasks = []
        for category, subreddit_list in self.subreddits.items():
            for subreddit_name in subreddit_list:
                for query in search_queries:
                    task = self._search_subreddit_async(
                        subreddit_name, query, limit_per_subreddit // len(search_queries)
                    )
                    tasks.append((category, subreddit_name, query, task))
        
        # Execute searches concurrently
        print(f"Starting comprehensive Reddit analysis for '{movie_title}'...")
        results = await asyncio.gather(*[task for _, _, _, task in tasks], return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
                
            category, subreddit_name, query, _ = tasks[i]
            posts = result
            
            all_posts.extend(posts)
            
            if subreddit_name not in subreddit_stats:
                subreddit_stats[subreddit_name] = {
                    'category': category,
                    'total_posts': 0,
                    'total_score': 0,
                    'total_comments': 0,
                    'avg_sentiment': 0,
                    'posts': []
                }
            
            subreddit_stats[subreddit_name]['posts'].extend(posts)
            subreddit_stats[subreddit_name]['total_posts'] += len(posts)
            subreddit_stats[subreddit_name]['total_score'] += sum(p.get('score', 0) for p in posts)
            subreddit_stats[subreddit_name]['total_comments'] += sum(p.get('num_comments', 0) for p in posts)
        
        # Perform comprehensive analysis
        analysis_results = {
            'movie_info': {
                'title': movie_title,
                'imdb_id': imdb_id,
                'year': year,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'collection_summary': {
                'total_posts': len(all_posts),
                'total_subreddits': len([s for s in subreddit_stats if subreddit_stats[s]['total_posts'] > 0]),
                'date_range': self._get_date_range(all_posts),
                'search_queries_used': search_queries
            },
            'sentiment_analysis': await self._deep_sentiment_analysis(all_posts),
            'community_insights': self._analyze_community_engagement(subreddit_stats),
            'temporal_analysis': self._analyze_temporal_trends(all_posts),
            'content_analysis': await self._deep_content_analysis(all_posts),
            'comparative_metrics': self._calculate_comparative_metrics(all_posts),
            'discussion_themes': self._extract_discussion_themes(all_posts),
            'user_behavior_analysis': self._analyze_user_behavior(all_posts),
            'subreddit_breakdown': subreddit_stats,
            'raw_data_summary': {
                'posts_by_subreddit': {k: len(v['posts']) for k, v in subreddit_stats.items()},
                'total_unique_users': len(set(p.get('author', '') for p in all_posts if p.get('author'))),
                'total_text_length': sum(len(p.get('selftext', '') + p.get('title', '')) for p in all_posts)
            }
        }
        
        return analysis_results
    
    def _generate_demo_analysis(self, movie_title: str, imdb_id: str = None, year: int = None) -> Dict:
        """Generate demo analysis when Reddit API is not available"""
        print(f"⚠️ Generating demo Reddit analysis for '{movie_title}' (Reddit API not configured)")
        
        import random
        
        # Generate realistic but fake data
        base_sentiment = random.uniform(-0.3, 0.7)  # Slightly positive bias
        total_posts = random.randint(25, 150)
        
        # Generate sentiment distribution
        very_positive = max(0, int(total_posts * random.uniform(0.1, 0.4)))
        positive = max(0, int(total_posts * random.uniform(0.15, 0.35)))
        neutral = max(0, int(total_posts * random.uniform(0.1, 0.3)))
        negative = max(0, int(total_posts * random.uniform(0.05, 0.25)))
        very_negative = max(0, total_posts - very_positive - positive - neutral - negative)
        
        # Ensure total adds up
        total_sentiment = very_positive + positive + neutral + negative + very_negative
        if total_sentiment != total_posts:
            neutral += (total_posts - total_sentiment)
        
        demo_analysis = {
            'movie_info': {
                'title': movie_title,
                'imdb_id': imdb_id,
                'year': year,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'collection_summary': {
                'total_posts': total_posts,
                'total_subreddits': random.randint(8, 15),
                'date_range': {
                    'earliest': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                    'latest': datetime.now().isoformat(),
                    'span_days': random.randint(30, 365)
                },
                'search_queries_used': [movie_title, f'"{movie_title}"']
            },
            'sentiment_analysis': {
                'overall_sentiment': {
                    'mean': base_sentiment,
                    'median': base_sentiment + random.uniform(-0.1, 0.1),
                    'std': random.uniform(0.3, 0.8),
                    'min': -1.0,
                    'max': 1.0
                },
                'distribution': {
                    'very_positive': very_positive,
                    'positive': positive,
                    'neutral': neutral,
                    'negative': negative,
                    'very_negative': very_negative
                },
                'percentiles': {
                    '10th': base_sentiment - 0.4,
                    '25th': base_sentiment - 0.2,
                    '75th': base_sentiment + 0.2,
                    '90th': base_sentiment + 0.4
                },
                'posts_vs_comments': {
                    'posts_mean_sentiment': base_sentiment,
                    'comments_mean_sentiment': base_sentiment + random.uniform(-0.1, 0.1),
                    'posts_count': total_posts,
                    'comments_count': random.randint(total_posts * 2, total_posts * 8)
                }
            },
            'community_insights': {
                'total_subreddits_analyzed': random.randint(8, 15),
                'active_subreddits': random.randint(6, 12),
                'engagement_metrics': {
                    'avg_posts_per_subreddit': random.uniform(3, 15),
                    'avg_score_per_post': random.uniform(5, 50),
                    'avg_comments_per_post': random.uniform(2, 12)
                }
            },
            'temporal_analysis': {
                'date_range': {
                    'earliest': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                    'latest': datetime.now().isoformat(),
                    'total_days': random.randint(30, 365)
                },
                'peak_discussion_periods': [
                    {
                        'date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                        'rank': 1,
                        'post_count': random.randint(8, 25),
                        'avg_sentiment': base_sentiment + random.uniform(-0.2, 0.2)
                    }
                ]
            },
            'content_analysis': {
                'text_statistics': {
                    'total_words': random.randint(5000, 20000),
                    'unique_words': random.randint(1000, 5000),
                    'avg_post_length': random.uniform(50, 200)
                },
                'keyword_analysis': {
                    'top_keywords': [
                        ('acting', random.randint(5, 25)),
                        ('plot', random.randint(4, 20)),
                        ('cinematography', random.randint(3, 15)),
                        ('directing', random.randint(3, 12)),
                        ('soundtrack', random.randint(2, 10)),
                        ('effects', random.randint(2, 8)),
                        ('characters', random.randint(4, 18)),
                        ('story', random.randint(6, 22)),
                        ('performance', random.randint(3, 14)),
                        ('ending', random.randint(2, 12))
                    ],
                    'total_unique_keywords': random.randint(200, 800),
                    'keyword_diversity': random.uniform(0.3, 0.7)
                }
            },
            'discussion_themes': {
                'popular_themes': [
                    {'theme': 'review', 'count': random.randint(5, 20), 'percentage': random.uniform(15, 40)},
                    {'theme': 'discussion', 'count': random.randint(3, 15), 'percentage': random.uniform(10, 30)},
                    {'theme': 'question', 'count': random.randint(2, 10), 'percentage': random.uniform(5, 20)}
                ],
                'theme_diversity': random.randint(8, 15)
            },
            'user_behavior_analysis': {
                'total_unique_users': random.randint(total_posts // 2, total_posts),
                'engagement_distribution': {
                    'avg_posts_per_user': random.uniform(1.2, 2.5)
                }
            },
            'raw_data_summary': {
                'total_unique_users': random.randint(total_posts // 2, total_posts),
                'total_text_length': random.randint(10000, 50000)
            }
        }
        
        return demo_analysis
    
    def _generate_search_queries(self, movie_title: str, year: int = None) -> List[str]:
        """Generate multiple search queries for comprehensive coverage"""
        queries = [movie_title]
        
        # Add variations
        if year:
            queries.extend([
                f'"{movie_title}" {year}',
                f'{movie_title} {year}',
                f'{movie_title} movie {year}'
            ])
        
        # Add quoted version for exact matches
        queries.append(f'"{movie_title}"')
        
        # Add common variations
        title_words = movie_title.split()
        if len(title_words) > 1:
            # Add without articles
            title_no_articles = ' '.join([word for word in title_words if word.lower() not in ['the', 'a', 'an']])
            if title_no_articles != movie_title:
                queries.append(title_no_articles)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in queries:
            if query not in seen:
                seen.add(query)
                unique_queries.append(query)
        
        return unique_queries[:5]  # Limit to 5 queries to avoid rate limiting
    
    async def _search_subreddit_async(self, subreddit_name: str, query: str, limit: int) -> List[Dict]:
        """Asynchronously search a subreddit for posts"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            # Search with different sort methods
            search_methods = [
                ('relevance', subreddit.search(query, limit=limit//2, sort='relevance')),
                ('top', subreddit.search(query, limit=limit//2, sort='top', time_filter='all'))
            ]
            
            for sort_method, search_results in search_methods:
                for post in search_results:
                    if self._is_relevant_post(post, query):
                        post_data = await self._extract_comprehensive_post_data(post, subreddit_name)
                        post_data['search_method'] = sort_method
                        posts.append(post_data)
            
            return posts
            
        except Exception as e:
            print(f"Error searching subreddit {subreddit_name} for '{query}': {e}")
            return []
    
    def _is_relevant_post(self, post, query: str) -> bool:
        """Check if post is relevant to the movie query"""
        title = post.title.lower()
        selftext = post.selftext.lower()
        query_words = query.lower().replace('"', '').split()
        
        # Check if majority of query words are present
        matches = sum(1 for word in query_words if word in title or word in selftext)
        return matches >= len(query_words) * 0.6  # 60% of words must match
    
    async def _extract_comprehensive_post_data(self, post, subreddit_name: str) -> Dict:
        """Extract comprehensive data from a Reddit post"""
        # Get top comments with detailed analysis
        comments_data = await self._extract_detailed_comments(post, limit=20)
        
        # Calculate text statistics
        full_text = f"{post.title} {post.selftext}".strip()
        
        post_data = {
            'id': post.id,
            'subreddit': subreddit_name,
            'title': post.title,
            'selftext': post.selftext,
            'author': str(post.author) if post.author else '[deleted]',
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'num_comments': post.num_comments,
            'created_utc': datetime.fromtimestamp(post.created_utc),
            'url': post.url,
            'permalink': f"https://reddit.com{post.permalink}",
            'is_video': post.is_video,
            'is_original_content': post.is_original_content,
            'spoiler': post.spoiler,
            'over_18': post.over_18,
            'locked': post.locked,
            'stickied': post.stickied,
            'distinguished': post.distinguished,
            'awards_received': getattr(post, 'total_awards_received', 0),
            'gilded': post.gilded,
            'text_statistics': {
                'title_length': len(post.title),
                'body_length': len(post.selftext),
                'total_length': len(full_text),
                'word_count': len(full_text.split()),
                'contains_spoiler_tag': '[spoiler]' in full_text.lower() or 'spoiler' in full_text.lower(),
                'contains_rating': any(rating in full_text.lower() for rating in ['10/10', '9/10', '8/10', '7/10', '6/10', '5/10', '4/10', '3/10', '2/10', '1/10', '/10', 'stars']),
                'sentiment_score': TextBlob(full_text).sentiment.polarity if full_text else 0,
                'subjectivity_score': TextBlob(full_text).sentiment.subjectivity if full_text else 0
            },
            'comments': comments_data,
            'extracted_metadata': self._extract_post_metadata(post, full_text)
        }
        
        return post_data
    
    async def _extract_detailed_comments(self, post, limit: int = 20) -> List[Dict]:
        """Extract detailed comment data from a post"""
        comments = []
        
        try:
            post.comments.replace_more(limit=0)
            comment_list = post.comments.list()[:limit]
            
            for comment in comment_list:
                if hasattr(comment, 'body') and comment.body not in ['[deleted]', '[removed]']:
                    comment_data = {
                        'id': comment.id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'is_submitter': comment.is_submitter,
                        'depth': comment.depth,
                        'gilded': comment.gilded,
                        'awards_received': getattr(comment, 'total_awards_received', 0),
                        'controversial': getattr(comment, 'controversiality', 0) > 0,
                        'text_analysis': {
                            'length': len(comment.body),
                            'word_count': len(comment.body.split()),
                            'sentiment': TextBlob(comment.body).sentiment.polarity,
                            'subjectivity': TextBlob(comment.body).sentiment.subjectivity,
                            'contains_spoiler': 'spoiler' in comment.body.lower(),
                            'contains_rating': any(rating in comment.body.lower() for rating in ['/10', 'stars', 'rating']),
                        }
                    }
                    comments.append(comment_data)
                    
        except Exception as e:
            print(f"Error extracting comments: {e}")
        
        return comments
    
    def _extract_post_metadata(self, post, full_text: str) -> Dict:
        """Extract metadata and classifications from post content"""
        metadata = {
            'post_type': self._classify_post_type(post, full_text),
            'discussion_type': self._classify_discussion_type(full_text),
            'emotional_tone': self._analyze_emotional_tone(full_text),
            'contains_spoilers': self._detect_spoilers(full_text),
            'movie_aspects_discussed': self._extract_movie_aspects(full_text),
            'rating_mentions': self._extract_rating_mentions(full_text),
            'comparison_movies': self._extract_movie_comparisons(full_text)
        }
        
        return metadata
    
    def _classify_post_type(self, post, full_text: str) -> str:
        """Classify the type of post"""
        title_lower = post.title.lower()
        text_lower = full_text.lower()
        
        if any(word in title_lower for word in ['review', 'watched', 'opinion']):
            return 'review'
        elif any(word in title_lower for word in ['discussion', 'thoughts', 'anyone else']):
            return 'discussion'
        elif any(word in title_lower for word in ['question', '?', 'help', 'explain']):
            return 'question'
        elif any(word in title_lower for word in ['recommendation', 'suggest', 'similar']):
            return 'recommendation'
        elif any(word in title_lower for word in ['news', 'trailer', 'release', 'casting']):
            return 'news'
        elif post.is_video or 'youtube' in post.url or 'vimeo' in post.url:
            return 'video_content'
        else:
            return 'general'
    
    def _classify_discussion_type(self, text: str) -> str:
        """Classify the type of discussion"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['plot', 'story', 'ending', 'twist']):
            return 'plot_discussion'
        elif any(word in text_lower for word in ['acting', 'performance', 'actor', 'actress']):
            return 'performance_discussion'
        elif any(word in text_lower for word in ['cinematography', 'visual', 'effects', 'cgi']):
            return 'technical_discussion'
        elif any(word in text_lower for word in ['music', 'score', 'soundtrack']):
            return 'music_discussion'
        elif any(word in text_lower for word in ['director', 'directing', 'filmmaking']):
            return 'direction_discussion'
        else:
            return 'general_discussion'
    
    def _analyze_emotional_tone(self, text: str) -> Dict:
        """Analyze emotional tone of the text"""
        text_lower = text.lower()
        
        emotions = {
            'excitement': len(re.findall(r'amazing|incredible|fantastic|awesome|brilliant|masterpiece|perfect', text_lower)),
            'disappointment': len(re.findall(r'disappointed|boring|terrible|awful|waste|bad|worst', text_lower)),
            'confusion': len(re.findall(r'confused|understand|explain|unclear|weird|strange', text_lower)),
            'nostalgia': len(re.findall(r'childhood|remember|classic|old|vintage|nostalgic', text_lower)),
            'anticipation': len(re.findall(r'excited|looking forward|can\'t wait|anticipate|hype', text_lower)),
        }
        
        dominant_emotion = max(emotions.keys(), key=lambda k: emotions[k]) if any(emotions.values()) else 'neutral'
        
        return {
            'dominant_emotion': dominant_emotion,
            'emotion_scores': emotions,
            'emotional_intensity': sum(emotions.values())
        }
    
    async def _deep_sentiment_analysis(self, posts: List[Dict]) -> Dict:
        """Perform deep sentiment analysis on all posts and comments"""
        all_sentiments = []
        post_sentiments = []
        comment_sentiments = []
        
        for post in posts:
            # Post sentiment
            post_sentiment = post.get('text_statistics', {}).get('sentiment_score', 0)
            post_sentiments.append(post_sentiment)
            all_sentiments.append(post_sentiment)
            
            # Comment sentiments
            for comment in post.get('comments', []):
                comment_sentiment = comment.get('text_analysis', {}).get('sentiment', 0)
                comment_sentiments.append(comment_sentiment)
                all_sentiments.append(comment_sentiment)
        
        if not all_sentiments:
            return {'error': 'No sentiment data available'}
        
        # Calculate comprehensive sentiment statistics
        sentiment_array = np.array(all_sentiments)
        
        sentiment_analysis = {
            'overall_sentiment': {
                'mean': float(np.mean(sentiment_array)),
                'median': float(np.median(sentiment_array)),
                'std': float(np.std(sentiment_array)),
                'min': float(np.min(sentiment_array)),
                'max': float(np.max(sentiment_array))
            },
            'distribution': {
                'very_positive': int(np.sum(sentiment_array > 0.5)),
                'positive': int(np.sum((sentiment_array > 0.1) & (sentiment_array <= 0.5))),
                'neutral': int(np.sum((sentiment_array >= -0.1) & (sentiment_array <= 0.1))),
                'negative': int(np.sum((sentiment_array >= -0.5) & (sentiment_array < -0.1))),
                'very_negative': int(np.sum(sentiment_array < -0.5))
            },
            'percentiles': {
                '10th': float(np.percentile(sentiment_array, 10)),
                '25th': float(np.percentile(sentiment_array, 25)),
                '75th': float(np.percentile(sentiment_array, 75)),
                '90th': float(np.percentile(sentiment_array, 90))
            },
            'posts_vs_comments': {
                'posts_mean_sentiment': float(np.mean(post_sentiments)) if post_sentiments else 0,
                'comments_mean_sentiment': float(np.mean(comment_sentiments)) if comment_sentiments else 0,
                'posts_count': len(post_sentiments),
                'comments_count': len(comment_sentiments)
            }
        }
        
        return sentiment_analysis
    
    def _analyze_temporal_trends(self, posts: List[Dict]) -> Dict:
        """Analyze temporal trends in discussions"""
        if not posts:
            return {}
        
        # Convert timestamps and sort
        post_times = [(post['created_utc'], post) for post in posts if 'created_utc' in post]
        post_times.sort(key=lambda x: x[0])
        
        # Group by time periods
        daily_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'sentiments': []})
        weekly_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'sentiments': []})
        monthly_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'sentiments': []})
        
        for timestamp, post in post_times:
            day_key = timestamp.strftime('%Y-%m-%d')
            week_key = timestamp.strftime('%Y-W%U')
            month_key = timestamp.strftime('%Y-%m')
            
            sentiment = post.get('text_statistics', {}).get('sentiment_score', 0)
            score = post.get('score', 0)
            
            for stats, key in [(daily_stats, day_key), (weekly_stats, week_key), (monthly_stats, month_key)]:
                stats[key]['count'] += 1
                stats[key]['total_score'] += score
                stats[key]['sentiments'].append(sentiment)
        
        # Calculate trends
        def calculate_trend_stats(stats_dict):
            return {
                period: {
                    'post_count': data['count'],
                    'total_score': data['total_score'],
                    'avg_score': data['total_score'] / data['count'] if data['count'] > 0 else 0,
                    'avg_sentiment': np.mean(data['sentiments']) if data['sentiments'] else 0,
                    'sentiment_std': np.std(data['sentiments']) if len(data['sentiments']) > 1 else 0
                }
                for period, data in stats_dict.items()
            }
        
        temporal_analysis = {
            'date_range': {
                'earliest': min(timestamp for timestamp, _ in post_times).isoformat(),
                'latest': max(timestamp for timestamp, _ in post_times).isoformat(),
                'total_days': (max(timestamp for timestamp, _ in post_times) - 
                              min(timestamp for timestamp, _ in post_times)).days
            },
            'daily_trends': calculate_trend_stats(daily_stats),
            'weekly_trends': calculate_trend_stats(weekly_stats),
            'monthly_trends': calculate_trend_stats(monthly_stats),
            'peak_discussion_periods': self._identify_peak_periods(daily_stats)
        }
        
        return temporal_analysis
    
    def _identify_peak_periods(self, daily_stats: Dict) -> List[Dict]:
        """Identify peak discussion periods"""
        if not daily_stats:
            return []
        
        # Sort by post count
        sorted_days = sorted(daily_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        peak_periods = []
        for i, (date, stats) in enumerate(sorted_days[:5]):  # Top 5 days
            peak_periods.append({
                'date': date,
                'rank': i + 1,
                'post_count': stats['count'],
                'total_score': stats['total_score'],
                'avg_sentiment': np.mean(stats['sentiments']) if stats['sentiments'] else 0
            })
        
        return peak_periods
    
    async def _deep_content_analysis(self, posts: List[Dict]) -> Dict:
        """Perform deep content analysis"""
        # Extract all text content
        all_text = []
        titles = []
        bodies = []
        comments_text = []
        
        for post in posts:
            titles.append(post.get('title', ''))
            bodies.append(post.get('selftext', ''))
            all_text.append(f"{post.get('title', '')} {post.get('selftext', '')}")
            
            for comment in post.get('comments', []):
                comment_body = comment.get('body', '')
                comments_text.append(comment_body)
                all_text.append(comment_body)
        
        # Combine all text
        full_text = ' '.join(all_text).lower()
        
        content_analysis = {
            'text_statistics': {
                'total_words': len(full_text.split()),
                'unique_words': len(set(full_text.split())),
                'avg_post_length': np.mean([len(text.split()) for text in all_text if text]),
                'total_characters': len(full_text)
            },
            'keyword_analysis': self._extract_keywords(full_text),
            'movie_aspects_mentioned': self._analyze_movie_aspects(all_text),
            'rating_analysis': self._analyze_ratings_mentioned(all_text),
            'comparison_analysis': self._analyze_movie_comparisons(all_text),
            'spoiler_analysis': self._analyze_spoiler_content(all_text),
            'discussion_quality_metrics': self._analyze_discussion_quality(posts)
        }
        
        return content_analysis
    
    def _extract_keywords(self, text: str, top_n: int = 50) -> Dict:
        """Extract and analyze keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'movie', 'film', 'movies', 'films', 'watch', 'watched', 'watching', 'see', 'seen'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        word_counts = Counter(filtered_words)
        
        return {
            'top_keywords': word_counts.most_common(top_n),
            'total_unique_keywords': len(word_counts),
            'keyword_diversity': len(word_counts) / len(filtered_words) if filtered_words else 0
        }
    
    def _get_date_range(self, posts: List[Dict]) -> Dict:
        """Get date range of posts"""
        if not posts:
            return {}
        
        dates = [post['created_utc'] for post in posts if 'created_utc' in post]
        if not dates:
            return {}
        
        return {
            'earliest': min(dates).isoformat(),
            'latest': max(dates).isoformat(),
            'span_days': (max(dates) - min(dates)).days
        }
      def _analyze_community_engagement(self, subreddit_stats: Dict) -> Dict:
        """Analyze community engagement patterns"""
        try:
            if not subreddit_stats:
                return {}
            
            # Calculate engagement metrics for each subreddit
            subreddit_engagement = {}
            total_posts = sum(stats['total_posts'] for stats in subreddit_stats.values())
            total_score = sum(stats['total_score'] for stats in subreddit_stats.values())
            total_comments = sum(stats['total_comments'] for stats in subreddit_stats.values())
            
            for subreddit_name, stats in subreddit_stats.items():
                if stats['total_posts'] > 0:
                    subreddit_engagement[subreddit_name] = {
                        'category': stats['category'],
                        'post_count': stats['total_posts'],
                        'avg_score': stats['total_score'] / stats['total_posts'],
                        'avg_comments': stats['total_comments'] / stats['total_posts'],
                        'engagement_ratio': (stats['total_score'] + stats['total_comments']) / stats['total_posts'],
                        'share_of_posts': (stats['total_posts'] / total_posts * 100) if total_posts > 0 else 0
                    }
            
            # Find most engaged communities
            top_by_engagement = sorted(
                subreddit_engagement.items(),
                key=lambda x: x[1]['engagement_ratio'],
                reverse=True
            )[:5]
            
            top_by_posts = sorted(
                subreddit_engagement.items(),
                key=lambda x: x[1]['post_count'],
                reverse=True
            )[:5]
            
            # Category analysis
            category_stats = defaultdict(lambda: {'posts': 0, 'score': 0, 'comments': 0})
            for stats in subreddit_stats.values():
                category = stats['category']
                category_stats[category]['posts'] += stats['total_posts']
                category_stats[category]['score'] += stats['total_score']
                category_stats[category]['comments'] += stats['total_comments']
            
            return {
                'total_subreddits_analyzed': len(subreddit_stats),
                'active_subreddits': len([s for s in subreddit_stats if subreddit_stats[s]['total_posts'] > 0]),
                'top_subreddits_by_engagement': [{'name': name, **data} for name, data in top_by_engagement],
                'top_subreddits_by_posts': [{'name': name, **data} for name, data in top_by_posts],
                'category_breakdown': dict(category_stats),
                'engagement_metrics': {
                    'avg_posts_per_subreddit': total_posts / len(subreddit_stats) if subreddit_stats else 0,
                    'avg_score_per_post': total_score / total_posts if total_posts > 0 else 0,
                    'avg_comments_per_post': total_comments / total_posts if total_posts > 0 else 0
                }
            }
        except Exception as e:
            print(f"Error analyzing community engagement: {e}")
            return {'error': str(e)}
    
    def _calculate_comparative_metrics(self, posts: List[Dict]) -> Dict:
        """Calculate comparative metrics across different aspects"""
        try:
            if not posts:
                return {}
            
            # Score and engagement metrics
            scores = [p.get('score', 0) for p in posts]
            comments_counts = [p.get('num_comments', 0) for p in posts]
            sentiments = [p.get('text_statistics', {}).get('sentiment_score', 0) for p in posts]
            
            # Post type analysis
            post_types = [p.get('extracted_metadata', {}).get('post_type', 'general') for p in posts]
            post_type_counts = Counter(post_types)
            
            # Discussion type analysis
            discussion_types = [p.get('extracted_metadata', {}).get('discussion_type', 'general_discussion') for p in posts]
            discussion_type_counts = Counter(discussion_types)
            
            # Subreddit comparison
            subreddit_metrics = defaultdict(lambda: {'posts': 0, 'total_score': 0, 'total_sentiment': 0})
            for post in posts:
                subreddit = post.get('subreddit', 'unknown')
                subreddit_metrics[subreddit]['posts'] += 1
                subreddit_metrics[subreddit]['total_score'] += post.get('score', 0)
                subreddit_metrics[subreddit]['total_sentiment'] += post.get('text_statistics', {}).get('sentiment_score', 0)
            
            # Calculate averages
            for subreddit in subreddit_metrics:
                metrics = subreddit_metrics[subreddit]
                metrics['avg_score'] = metrics['total_score'] / metrics['posts'] if metrics['posts'] > 0 else 0
                metrics['avg_sentiment'] = metrics['total_sentiment'] / metrics['posts'] if metrics['posts'] > 0 else 0
            
            return {
                'score_metrics': {
                    'mean': float(np.mean(scores)) if scores else 0,
                    'median': float(np.median(scores)) if scores else 0,
                    'std': float(np.std(scores)) if scores else 0,
                    'max': max(scores) if scores else 0,
                    'min': min(scores) if scores else 0
                },
                'engagement_metrics': {
                    'mean_comments': float(np.mean(comments_counts)) if comments_counts else 0,
                    'median_comments': float(np.median(comments_counts)) if comments_counts else 0,
                    'max_comments': max(comments_counts) if comments_counts else 0
                },
                'content_type_distribution': dict(post_type_counts),
                'discussion_type_distribution': dict(discussion_type_counts),
                'subreddit_comparison': dict(subreddit_metrics),
                'correlation_analysis': {
                    'score_vs_sentiment': float(np.corrcoef(scores, sentiments)[0,1]) if len(scores) > 1 and len(sentiments) > 1 else 0,
                    'score_vs_comments': float(np.corrcoef(scores, comments_counts)[0,1]) if len(scores) > 1 and len(comments_counts) > 1 else 0
                }
            }
        except Exception as e:
            print(f"Error calculating comparative metrics: {e}")
            return {'error': str(e)}
    
    def _extract_discussion_themes(self, posts: List[Dict]) -> Dict:
        """Extract main discussion themes"""
        try:
            if not posts:
                return {}
            
            # Collect all text for theme analysis
            all_themes = []
            emotional_themes = []
            movie_aspects = []
            
            for post in posts:
                metadata = post.get('extracted_metadata', {})
                
                # Post types as themes
                post_type = metadata.get('post_type', 'general')
                all_themes.append(post_type)
                
                # Discussion types
                discussion_type = metadata.get('discussion_type', 'general_discussion')
                all_themes.append(discussion_type)
                
                # Emotional tones
                emotional_tone = metadata.get('emotional_tone', {})
                if emotional_tone.get('dominant_emotion'):
                    emotional_themes.append(emotional_tone['dominant_emotion'])
                
                # Movie aspects
                aspects = metadata.get('movie_aspects_discussed', [])
                movie_aspects.extend(aspects)
            
            # Count themes
            theme_counts = Counter(all_themes)
            emotional_counts = Counter(emotional_themes)
            aspect_counts = Counter(movie_aspects)
            
            # Extract popular themes
            popular_themes = [
                {'theme': theme, 'count': count, 'percentage': (count / len(posts) * 100)}
                for theme, count in theme_counts.most_common(10)
            ]
            
            return {
                'popular_themes': popular_themes,
                'emotional_themes': dict(emotional_counts),
                'movie_aspects_discussed': dict(aspect_counts),
                'theme_diversity': len(theme_counts),
                'dominant_theme': theme_counts.most_common(1)[0] if theme_counts else None,
                'discussion_patterns': {
                    'review_heavy': theme_counts.get('review', 0) / len(posts) > 0.3,
                    'discussion_heavy': theme_counts.get('discussion', 0) / len(posts) > 0.3,
                    'question_heavy': theme_counts.get('question', 0) / len(posts) > 0.3
                }
            }
        except Exception as e:
            print(f"Error extracting discussion themes: {e}")
            return {'error': str(e)}
    
    def _analyze_user_behavior(self, posts: List[Dict]) -> Dict:
        """Analyze user behavior patterns"""
        try:
            if not posts:
                return {}
            
            # Collect user data
            user_activity = defaultdict(lambda: {'posts': 0, 'total_score': 0, 'total_comments': 0, 'sentiments': []})
            deleted_users = 0
            
            for post in posts:
                author = post.get('author', '[deleted]')
                if author == '[deleted]':
                    deleted_users += 1
                    continue
                
                user_activity[author]['posts'] += 1
                user_activity[author]['total_score'] += post.get('score', 0)
                user_activity[author]['total_comments'] += post.get('num_comments', 0)
                
                sentiment = post.get('text_statistics', {}).get('sentiment_score', 0)
                user_activity[author]['sentiments'].append(sentiment)
            
            # Calculate user metrics
            user_metrics = {}
            for user, activity in user_activity.items():
                user_metrics[user] = {
                    'post_count': activity['posts'],
                    'avg_score': activity['total_score'] / activity['posts'] if activity['posts'] > 0 else 0,
                    'avg_sentiment': np.mean(activity['sentiments']) if activity['sentiments'] else 0,
                    'total_engagement': activity['total_score'] + activity['total_comments']
                }
            
            # Find top contributors
            top_contributors = sorted(
                user_metrics.items(),
                key=lambda x: x[1]['post_count'],
                reverse=True
            )[:10]
            
            # Find most engaged users
            most_engaged = sorted(
                user_metrics.items(),
                key=lambda x: x[1]['total_engagement'],
                reverse=True
            )[:10]
            
            # User behavior patterns
            power_users = len([u for u in user_metrics if user_metrics[u]['post_count'] > 3])
            positive_users = len([u for u in user_metrics if user_metrics[u]['avg_sentiment'] > 0.2])
            negative_users = len([u for u in user_metrics if user_metrics[u]['avg_sentiment'] < -0.2])
            
            return {
                'total_unique_users': len(user_activity),
                'deleted_user_posts': deleted_users,
                'top_contributors': [{'username': user, **metrics} for user, metrics in top_contributors],
                'most_engaged_users': [{'username': user, **metrics} for user, metrics in most_engaged],
                'user_behavior_patterns': {
                    'power_users': power_users,
                    'casual_users': len(user_activity) - power_users,
                    'positive_users': positive_users,
                    'negative_users': negative_users,
                    'neutral_users': len(user_activity) - positive_users - negative_users
                },
                'engagement_distribution': {
                    'avg_posts_per_user': sum(m['post_count'] for m in user_metrics.values()) / len(user_metrics) if user_metrics else 0,
                    'user_sentiment_avg': np.mean([m['avg_sentiment'] for m in user_metrics.values()]) if user_metrics else 0
                }
            }
        except Exception as e:
            print(f"Error analyzing user behavior: {e}")
            return {'error': str(e)}

    def _detect_spoilers(self, text: str) -> bool:
        """Detect if text contains spoilers"""
        spoiler_indicators = [
            'spoiler', 'spoilers', '[spoiler]', 'spoiler alert',
            'dont read if you havent seen', 'ending revealed',
            'plot twist', 'major spoiler'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in spoiler_indicators)
    
    def _extract_movie_aspects(self, text: str) -> List[str]:
        """Extract movie aspects being discussed"""
        aspects = []
        text_lower = text.lower()
        
        aspect_keywords = {
            'acting': ['acting', 'performance', 'actor', 'actress', 'cast'],
            'plot': ['plot', 'story', 'storyline', 'narrative', 'script'],
            'direction': ['director', 'directing', 'direction', 'filmmaking'],
            'cinematography': ['cinematography', 'camera', 'visual', 'shot', 'lighting'],
            'music': ['soundtrack', 'music', 'score', 'composer'],
            'effects': ['effects', 'cgi', 'vfx', 'special effects', 'visual effects'],
            'editing': ['editing', 'pacing', 'cuts', 'montage'],
            'writing': ['writing', 'dialogue', 'script', 'screenplay']
        }
        
        for aspect, keywords in aspect_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                aspects.append(aspect)
        
        return aspects
    
    def _extract_rating_mentions(self, text: str) -> List[str]:
        """Extract rating mentions from text"""
        ratings = []
        text_lower = text.lower()
        
        # Common rating patterns
        rating_patterns = [
            r'\d+/10', r'\d+\.\d+/10', r'\d+ out of 10',
            r'\d+ stars?', r'\d+\.\d+ stars?',
            r'[a-f][+-]?', r'[0-9]+%'
        ]
        
        for pattern in rating_patterns:
            matches = re.findall(pattern, text_lower)
            ratings.extend(matches)
        
        return ratings
    
    def _extract_movie_comparisons(self, text: str) -> List[str]:
        """Extract movie comparisons from text"""
        comparisons = []
        text_lower = text.lower()
        
        # Look for comparison patterns
        comparison_phrases = [
            'better than', 'worse than', 'similar to', 'like', 'reminds me of',
            'compared to', 'unlike', 'as good as', 'not as good as'
        ]
        
        for phrase in comparison_phrases:
            if phrase in text_lower:
                # Try to extract the movie being compared to
                # This is a simple approach - could be enhanced
                comparisons.append(phrase)
        
        return comparisons
    
    def _analyze_movie_aspects(self, all_text: List[str]) -> Dict:
        """Analyze which movie aspects are most discussed"""
        aspect_mentions = defaultdict(int)
        
        for text in all_text:
            aspects = self._extract_movie_aspects(text)
            for aspect in aspects:
                aspect_mentions[aspect] += 1
        
        return dict(aspect_mentions)
    
    def _analyze_ratings_mentioned(self, all_text: List[str]) -> Dict:
        """Analyze ratings mentioned in discussions"""
        all_ratings = []
        
        for text in all_text:
            ratings = self._extract_rating_mentions(text)
            all_ratings.extend(ratings)
        
        return {
            'total_rating_mentions': len(all_ratings),
            'unique_ratings': list(set(all_ratings)),
            'rating_frequency': dict(Counter(all_ratings))
        }
    
    def _analyze_movie_comparisons(self, all_text: List[str]) -> Dict:
        """Analyze movie comparisons made in discussions"""
        comparison_phrases = []
        
        for text in all_text:
            comparisons = self._extract_movie_comparisons(text)
            comparison_phrases.extend(comparisons)
        
        return {
            'total_comparisons': len(comparison_phrases),
            'comparison_types': dict(Counter(comparison_phrases))
        }
    
    def _analyze_spoiler_content(self, all_text: List[str]) -> Dict:
        """Analyze spoiler content in discussions"""
        spoiler_posts = 0
        total_posts = len(all_text)
        
        for text in all_text:
            if self._detect_spoilers(text):
                spoiler_posts += 1
        
        return {
            'total_spoiler_posts': spoiler_posts,
            'spoiler_percentage': (spoiler_posts / total_posts * 100) if total_posts > 0 else 0,
            'spoiler_aware_community': spoiler_posts > 0
        }
    
    def _analyze_discussion_quality(self, posts: List[Dict]) -> Dict:
        """Analyze the quality of discussions"""
        try:
            if not posts:
                return {}
            
            # Calculate quality metrics
            total_posts = len(posts)
            long_posts = sum(1 for p in posts if p.get('text_statistics', {}).get('word_count', 0) > 50)
            posts_with_comments = sum(1 for p in posts if p.get('num_comments', 0) > 0)
            high_score_posts = sum(1 for p in posts if p.get('score', 0) > 10)
            
            # Calculate average metrics
            avg_word_count = np.mean([p.get('text_statistics', {}).get('word_count', 0) for p in posts])
            avg_comments = np.mean([p.get('num_comments', 0) for p in posts])
            avg_score = np.mean([p.get('score', 0) for p in posts])
            
            return {
                'discussion_depth': {
                    'long_form_posts': long_posts,
                    'long_form_percentage': (long_posts / total_posts * 100) if total_posts > 0 else 0
                },
                'community_engagement': {
                    'posts_with_comments': posts_with_comments,
                    'engagement_percentage': (posts_with_comments / total_posts * 100) if total_posts > 0 else 0
                },
                'content_quality': {
                    'high_score_posts': high_score_posts,
                    'quality_percentage': (high_score_posts / total_posts * 100) if total_posts > 0 else 0
                },
                'average_metrics': {
                    'avg_word_count': float(avg_word_count),
                    'avg_comments_per_post': float(avg_comments),
                    'avg_score': float(avg_score)
                }
            }
        except Exception as e:
            print(f"Error analyzing discussion quality: {e}")
            return {'error': str(e)}
