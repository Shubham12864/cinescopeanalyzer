import scrapy
import json
import re
from scrapy.http import Request
from urllib.parse import urljoin, quote
from datetime import datetime
import asyncio
from typing import Dict, List, Optional

class ComprehensiveMovieSpider(scrapy.Spider):
    """
    Comprehensive movie spider that scrapes detailed information from multiple sources:
    - IMDB (main page, reviews, trivia, technical specs, box office)
    - Rotten Tomatoes (critics/audience scores, reviews)
    - Metacritic (critic/user scores, reviews)
    - Letterboxd (user reviews and ratings)
    - TheMovieDB (additional metadata)
    """
    
    name = 'comprehensive_movie_scraper'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 8,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'CineScopeAnalyzer/1.0 (+http://www.yourwebsite.com/bot)',
    }
    
    def __init__(self, movie_title=None, imdb_id=None, year=None, *args, **kwargs):
        super(ComprehensiveMovieSpider, self).__init__(*args, **kwargs)
        self.movie_title = movie_title or ''
        self.imdb_id = imdb_id
        self.year = year
        self.movie_data = {
            'basic_info': {},
            'ratings_reviews': {},
            'technical_details': {},
            'box_office': {},
            'cast_crew': {},
            'trivia_goofs': {},
            'user_reviews': [],
            'critical_reviews': [],
            'social_media_sentiment': {}
        }
        
        self.start_urls = self._generate_start_urls()
    
    def _generate_start_urls(self) -> List[str]:
        """Generate comprehensive list of URLs to scrape"""
        urls = []
        
        if self.imdb_id:
            # IMDB URLs - comprehensive coverage
            base_imdb = f'https://www.imdb.com/title/{self.imdb_id}'
            urls.extend([
                f'{base_imdb}/',  # Main page
                f'{base_imdb}/reviews/',  # User reviews
                f'{base_imdb}/criticreviews/',  # Critic reviews
                f'{base_imdb}/trivia/',  # Trivia
                f'{base_imdb}/goofs/',  # Goofs
                f'{base_imdb}/technical/',  # Technical specs
                f'{base_imdb}/business/',  # Box office
                f'{base_imdb}/awards/',  # Awards
                f'{base_imdb}/releaseinfo/',  # Release info
                f'{base_imdb}/parentalguide/',  # Parental guide
                f'{base_imdb}/soundtrack/',  # Soundtrack
                f'{base_imdb}/quotes/',  # Memorable quotes
            ])
        
        if self.movie_title:
            # Encode movie title for URLs
            encoded_title = quote(self.movie_title)
            year_str = f" {self.year}" if self.year else ""
            search_query = quote(f"{self.movie_title}{year_str}")
            
            # Rotten Tomatoes
            urls.extend([
                f'https://www.rottentomatoes.com/search?search={search_query}',
                f'https://www.rottentomatoes.com/m/{encoded_title.lower().replace("%20", "_")}',
            ])
            
            # Metacritic
            urls.extend([
                f'https://www.metacritic.com/search/movie/{search_query}/results',
                f'https://www.metacritic.com/movie/{encoded_title.lower().replace("%20", "-")}',
            ])
            
            # Letterboxd
            urls.extend([
                f'https://letterboxd.com/search/{search_query}/',
                f'https://letterboxd.com/film/{encoded_title.lower().replace("%20", "-")}/',
            ])
            
            # Box Office Mojo
            urls.append(f'https://www.boxofficemojo.com/search/?q={search_query}')
        
        return urls
    
    def parse(self, response):
        """Route responses to appropriate parsing methods"""
        url = response.url.lower()
        
        if 'imdb.com' in url:
            yield from self._parse_imdb_content(response)
        elif 'rottentomatoes.com' in url:
            yield from self._parse_rotten_tomatoes(response)
        elif 'metacritic.com' in url:
            yield from self._parse_metacritic(response)
        elif 'letterboxd.com' in url:
            yield from self._parse_letterboxd(response)
        elif 'boxofficemojo.com' in url:
            yield from self._parse_box_office_mojo(response)
    
    def _parse_imdb_content(self, response):
        """Parse comprehensive IMDB content"""
        url = response.url
        
        if '/title/' in url and url.endswith('/'):
            # Main movie page
            yield from self._parse_imdb_main(response)
        elif '/reviews/' in url:
            yield from self._parse_imdb_reviews(response)
        elif '/criticreviews/' in url:
            yield from self._parse_imdb_critic_reviews(response)
        elif '/trivia/' in url:
            yield from self._parse_imdb_trivia(response)
        elif '/technical/' in url:
            yield from self._parse_imdb_technical(response)
        elif '/business/' in url:
            yield from self._parse_imdb_business(response)
        elif '/awards/' in url:
            yield from self._parse_imdb_awards(response)
    
    def _parse_imdb_main(self, response):
        """Extract comprehensive main movie information from IMDB"""
        # Basic Information
        basic_info = {
            'source': 'imdb_main',
            'scraped_at': datetime.now().isoformat(),
            'title': self._extract_text(response, 'h1[data-testid="hero__pageTitle"] span::text'),
            'original_title': self._extract_text(response, 'div[data-testid="hero__pageTitle"] div::text'),
            'year': self._extract_text(response, 'a[href*="releaseinfo"]::text'),
            'rating': self._extract_text(response, 'span[data-testid="heroRating-star-rating__aggregate-rating__score"] span::text'),
            'rating_count': self._extract_text(response, 'div[data-testid="heroRating-star-rating__aggregate-rating__count"]::text'),
            'content_rating': self._extract_text(response, 'a[href*="parentalguide/certificates"]::text'),
            'runtime': self._extract_text(response, 'time::text'),
            'genres': response.css('a[href*="search/title"][class*="genre"]::text').getall(),
            'plot_summary': self._extract_text(response, 'span[data-testid="plot-xs_to_m"]::text'),
            'plot_keywords': response.css('a[href*="search/keyword"]::text').getall()[:10],
            'tagline': self._extract_text(response, 'p[data-testid="plot"] span[data-testid="plot-l"]::text'),
            'languages': response.css('a[href*="primary_language"]::text').getall(),
            'countries': response.css('a[href*="country_of_origin"]::text').getall(),
            'release_date': self._extract_text(response, 'a[href*="releaseinfo"]::text'),
        }
        
        # Cast and Crew (detailed)
        cast_crew = {
            'source': 'imdb_cast_crew',
            'directors': [
                {
                    'name': name.strip(),
                    'profile_url': response.urljoin(url) if url else None
                }
                for name, url in zip(
                    response.css('a[href*="/name/nm"][href*="/?ref_=tt_ov_dr"]::text').getall(),
                    response.css('a[href*="/name/nm"][href*="/?ref_=tt_ov_dr"]::attr(href)').getall()
                )
            ],
            'writers': [
                {
                    'name': name.strip(),
                    'profile_url': response.urljoin(url) if url else None
                }
                for name, url in zip(
                    response.css('a[href*="/name/nm"][href*="/?ref_=tt_ov_wr"]::text').getall(),
                    response.css('a[href*="/name/nm"][href*="/?ref_=tt_ov_wr"]::attr(href)').getall()
                )
            ],
            'stars': [
                {
                    'name': name.strip(),
                    'character': char.strip() if char else None,
                    'profile_url': response.urljoin(url) if url else None
                }
                for name, char, url in zip(
                    response.css('a[data-testid="title-cast-item__actor"]::text').getall()[:15],
                    response.css('a[data-testid="title-cast-item__character"] span::text').getall()[:15] + [None] * 15,
                    response.css('a[data-testid="title-cast-item__actor"]::attr(href)').getall()[:15]
                )
            ]
        }
        
        # Production Details
        production_info = {
            'source': 'imdb_production',
            'production_companies': [
                {
                    'name': name.strip(),
                    'url': response.urljoin(url) if url else None
                }
                for name, url in zip(
                    response.css('a[href*="/company/co"]::text').getall(),
                    response.css('a[href*="/company/co"]::attr(href)').getall()
                )
            ],
            'distributors': response.css('a[href*="/company/co"]:contains("(distributor)")::text').getall(),
            'budget': self._extract_text(response, 'li[data-testid="title-boxoffice-budget"] span::text'),
            'gross_worldwide': self._extract_text(response, 'li[data-testid="title-boxoffice-cumulativeworldwidegross"] span::text'),
            'gross_usa': self._extract_text(response, 'li[data-testid="title-boxoffice-grossdomestic"] span::text'),
            'opening_weekend': self._extract_text(response, 'li[data-testid="title-boxoffice-openingweekenddomestic"] span::text'),
        }
        
        yield {**basic_info, 'data_type': 'basic_info'}
        yield {**cast_crew, 'data_type': 'cast_crew'}
        yield {**production_info, 'data_type': 'production_info'}
    
    def _parse_imdb_reviews(self, response):
        """Extract detailed user reviews from IMDB"""
        reviews = response.css('div.review-container')
        
        for review in reviews[:50]:  # Get more reviews for comprehensive analysis
            review_data = {
                'source': 'imdb_user_review',
                'data_type': 'user_review',
                'scraped_at': datetime.now().isoformat(),
                'reviewer_name': self._extract_text(review, 'span.display-name-link a::text'),
                'reviewer_profile_url': self._extract_url(review, 'span.display-name-link a::attr(href)', response),
                'rating': self._extract_text(review, 'span.rating-other-user-rating span::text'),
                'review_title': self._extract_text(review, 'a.title::text'),
                'review_text': self._extract_text(review, 'div.text::text'),
                'review_date': self._extract_text(review, 'span.review-date::text'),
                'helpful_count': self._extract_number_from_text(
                    self._extract_text(review, 'div.actions span::text') or '0 out of 0 found this helpful'
                ),
                'total_votes': self._extract_total_votes_from_text(
                    self._extract_text(review, 'div.actions span::text') or '0 out of 0 found this helpful'
                ),
                'review_length': len(self._extract_text(review, 'div.text::text') or ''),
                'contains_spoiler': 'spoiler' in (self._extract_text(review, 'div.text::text') or '').lower(),
            }
            yield review_data
    
    def _parse_imdb_trivia(self, response):
        """Extract trivia and interesting facts"""
        trivia_items = response.css('div.sodatext')
        
        trivia_data = {
            'source': 'imdb_trivia',
            'data_type': 'trivia',
            'scraped_at': datetime.now().isoformat(),
            'trivia_items': [
                {
                    'text': self._clean_text(item.css('::text').get()),
                    'has_spoiler': 'spoiler' in item.css('::text').get().lower() if item.css('::text').get() else False,
                    'length': len(self._clean_text(item.css('::text').get()) or '')
                }
                for item in trivia_items[:30]
                if item.css('::text').get()
            ]
        }
        yield trivia_data
    
    def _parse_imdb_technical(self, response):
        """Extract technical specifications"""
        tech_data = {
            'source': 'imdb_technical',
            'data_type': 'technical_specs',
            'scraped_at': datetime.now().isoformat(),
            'aspect_ratio': self._extract_text(response, 'td:contains("Aspect Ratio") + td::text'),
            'camera': response.css('td:contains("Camera") + td::text').getall(),
            'color': self._extract_text(response, 'td:contains("Color") + td::text'),
            'sound_mix': response.css('td:contains("Sound Mix") + td::text').getall(),
            'filming_locations': response.css('a[href*="search/title?locations"]::text').getall()[:10],
            'production_dates': {
                'start_date': self._extract_text(response, 'td:contains("Start Date") + td::text'),
                'end_date': self._extract_text(response, 'td:contains("End Date") + td::text'),
            }
        }
        yield tech_data
    
    def _parse_rotten_tomatoes(self, response):
        """Extract comprehensive Rotten Tomatoes data"""
        rt_data = {
            'source': 'rotten_tomatoes',
            'data_type': 'ratings_reviews',
            'scraped_at': datetime.now().isoformat(),
            'tomatometer_score': self._extract_text(response, 'rt-text[slot="percentage"]::text'),
            'tomatometer_count': self._extract_text(response, 'rt-text[slot="info"]::text'),
            'audience_score': self._extract_text(response, 'rt-text[data-qa="audience-score"]::text'),
            'audience_count': self._extract_text(response, 'rt-text[data-qa="audience-rating-count"]::text'),
            'critics_consensus': self._extract_text(response, 'p[data-qa="critics-consensus"]::text'),
            'content_rating': self._extract_text(response, 'span[data-qa="content-rating"]::text'),
            'genre': response.css('span[data-qa="genre"]::text').getall(),
            'director': response.css('a[data-qa="movie-info-director"]::text').getall(),
            'producer': response.css('span[data-qa="movie-info-producer"]::text').getall(),
            'writer': response.css('span[data-qa="movie-info-writer"]::text').getall(),
            'release_date_theaters': self._extract_text(response, 'rt-text[data-qa="movie-info-release-date"]::text'),
            'release_date_streaming': self._extract_text(response, 'rt-text[data-qa="movie-info-streaming-date"]::text'),
            'runtime': self._extract_text(response, 'rt-text[data-qa="movie-info-runtime"]::text'),
            'studio': self._extract_text(response, 'rt-text[data-qa="movie-info-studio"]::text'),
        }
        
        # Extract critic reviews
        critic_reviews = []
        for review in response.css('div[data-qa="review-item"]')[:20]:
            critic_review = {
                'critic_name': self._extract_text(review, 'a[data-qa="review-link"]::text'),
                'publication': self._extract_text(review, 'span[data-qa="review-publication"]::text'),
                'score': self._extract_text(review, 'span[data-qa="review-score"]::text'),
                'review_text': self._extract_text(review, 'p[data-qa="review-text"]::text'),
                'review_date': self._extract_text(review, 'span[data-qa="review-date"]::text'),
                'is_fresh': 'fresh' in (review.css('span[data-qa="review-score"]::attr(class)').get() or ''),
            }
            critic_reviews.append(critic_review)
        
        rt_data['critic_reviews'] = critic_reviews
        yield rt_data
    
    def _parse_metacritic(self, response):
        """Extract comprehensive Metacritic data"""
        metacritic_data = {
            'source': 'metacritic',
            'data_type': 'ratings_reviews',
            'scraped_at': datetime.now().isoformat(),
            'metascore': self._extract_text(response, 'span.metascore_w span::text'),
            'metascore_description': self._extract_text(response, 'span.metascore_w + span::text'),
            'user_score': self._extract_text(response, 'div.user_score div.metascore_w::text'),
            'user_score_count': self._extract_text(response, 'span.count span::text'),
            'critic_review_count': self._extract_text(response, 'span.count a::text'),
            'summary': self._extract_text(response, 'span.blurb_expanded::text'),
            'genre': response.css('span.genre::text').getall(),
            'rating': self._extract_text(response, 'span.rating::text'),
            'runtime': self._extract_text(response, 'time::text'),
            'release_date': self._extract_text(response, 'span.release_date span::text'),
        }
        
        # Extract critic reviews
        critic_reviews = []
        for review in response.css('div.review_wrap')[:15]:
            critic_review = {
                'publication': self._extract_text(review, 'div.source a::text'),
                'critic_name': self._extract_text(review, 'div.author::text'),
                'score': self._extract_text(review, 'div.review_grade div::text'),
                'review_text': self._extract_text(review, 'div.review_body::text'),
                'review_date': self._extract_text(review, 'div.date::text'),
            }
            critic_reviews.append(critic_review)
        
        metacritic_data['critic_reviews'] = critic_reviews
        yield metacritic_data
    
    def _parse_letterboxd(self, response):
        """Extract Letterboxd user reviews and ratings"""
        letterboxd_data = {
            'source': 'letterboxd',
            'data_type': 'user_reviews',
            'scraped_at': datetime.now().isoformat(),
            'average_rating': self._extract_text(response, 'span.average-rating::text'),
            'rating_histogram': {},
            'total_ratings': self._extract_text(response, 'a[href*="ratings"] span::text'),
            'total_reviews': self._extract_text(response, 'a[href*="reviews"] span::text'),
            'total_likes': self._extract_text(response, 'a[href*="likes"] span::text'),
        }
        
        # Extract user reviews
        user_reviews = []
        for review in response.css('div.film-detail-content')[:25]:
            user_review = {
                'username': self._extract_text(review, 'strong.name a::text'),
                'rating': len(review.css('span.rating span.star.filled-star')),
                'review_text': self._extract_text(review, 'div.body-text p::text'),
                'review_date': self._extract_text(review, 'span.date a::text'),
                'likes_count': self._extract_text(review, 'p.like-link-target span::text'),
            }
            user_reviews.append(user_review)
        
        letterboxd_data['user_reviews'] = user_reviews
        yield letterboxd_data
    
    # Helper methods
    def _extract_text(self, selector, css_path: str) -> Optional[str]:
        """Safely extract text from CSS selector"""
        try:
            result = selector.css(css_path).get()
            return self._clean_text(result) if result else None
        except:
            return None
    
    def _extract_url(self, selector, css_path: str, response) -> Optional[str]:
        """Safely extract and resolve URL from CSS selector"""
        try:
            url = selector.css(css_path).get()
            return response.urljoin(url) if url else None
        except:
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', text.strip())
        # Remove common artifacts
        cleaned = re.sub(r'See full summary »', '', cleaned)
        cleaned = re.sub(r'See more »', '', cleaned)
        return cleaned.strip()
    
    def _extract_number_from_text(self, text: str) -> int:
        """Extract number from text like '123 out of 456 found this helpful'"""
        if not text:
            return 0
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 0
    
    def _extract_total_votes_from_text(self, text: str) -> int:
        """Extract total votes from text like '123 out of 456 found this helpful'"""
        if not text:
            return 0
        match = re.search(r'out of (\d+)', text)
        return int(match.group(1)) if match else 0
