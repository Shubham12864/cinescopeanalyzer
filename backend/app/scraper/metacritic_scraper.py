import re
import random
import time
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote, urljoin
try:
    from .advanced_scraper_base import AdvancedScraperBase
except ImportError:
    from advanced_scraper_base import AdvancedScraperBase

class MetacriticScraper(AdvancedScraperBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.metacritic.com"
        self.movie_base = f"{self.base_url}/movie"
        self.tv_base = f"{self.base_url}/tv"
    
    def search_title_advanced(self, title: str) -> Optional[str]:
        """Advanced Metacritic search with multiple methods"""
        self.logger.info(f"📊 Advanced Metacritic search for: {title}")
        
        # Method 1: Direct URL construction
        url = self.search_via_url_construction(title)
        if url:
            return url
        
        # Method 2: Search API endpoint
        url = self.search_via_search_endpoint(title)
        if url:
            return url
        
        # Method 3: Selenium-based search
        url = self.search_via_selenium(title)
        if url:
            return url
        
        self.logger.error(f"❌ All Metacritic search methods failed for: {title}")
        return None
    
    def search_via_url_construction(self, title: str) -> Optional[str]:
        """Try to construct direct URLs based on common patterns"""
        try:
            # Format title for Metacritic URL style
            formatted_title = self.format_title_for_url(title)
            
            # Common URL patterns for movies
            movie_patterns = [
                f"{self.movie_base}/{formatted_title}",
                f"{self.movie_base}/{formatted_title}-2024",
                f"{self.movie_base}/{formatted_title}-2023",
                f"{self.movie_base}/{formatted_title}-2022",
                f"{self.movie_base}/the-{formatted_title}",
            ]
            
            # Common URL patterns for TV shows
            tv_patterns = [
                f"{self.tv_base}/{formatted_title}",
                f"{self.tv_base}/{formatted_title}/season-1",
                f"{self.tv_base}/the-{formatted_title}",
            ]
            
            all_patterns = movie_patterns + tv_patterns
            
            for url in all_patterns:
                try:
                    response = self.safe_request(url, use_cloudscraper=True)
                    if response.status_code == 200:
                        # Check if it's actually a valid page
                        if self.validate_metacritic_page(response.text):
                            self.logger.info(f"✅ Found Metacritic URL via construction: {url}")
                            return url
                except Exception as e:
                    self.logger.debug(f"URL construction attempt failed for {url}: {str(e)}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ URL construction search failed: {str(e)}")
            return None
    
    def format_title_for_url(self, title: str) -> str:
        """Format title for Metacritic URL format"""
        # Convert to lowercase
        formatted = title.lower()
        
        # Remove special characters except spaces and hyphens
        formatted = re.sub(r'[^\w\s\-]', '', formatted)
        
        # Replace spaces with hyphens
        formatted = re.sub(r'\s+', '-', formatted)
        
        # Remove multiple consecutive hyphens
        formatted = re.sub(r'-+', '-', formatted)
        
        # Remove leading/trailing hyphens
        formatted = formatted.strip('-')
        
        return formatted
    
    def validate_metacritic_page(self, html_content: str) -> bool:
        """Validate if the page is a valid Metacritic content page"""
        # Check for common Metacritic page elements
        validation_indicators = [
            'metascore',
            'critic-reviews',
            'user-reviews',
            'metacritic-score',
            'product-title'
        ]
        
        html_lower = html_content.lower()
        return any(indicator in html_lower for indicator in validation_indicators)
    
    def search_via_search_endpoint(self, title: str) -> Optional[str]:
        """Search using Metacritic's search functionality"""
        try:
            # Metacritic search URL
            search_url = f"{self.base_url}/search/{quote(title)}/"
            
            response = self.safe_request(search_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors for search results
            result_selectors = [
                '.search_results .result a[href*="/movie/"]',
                '.search_results .result a[href*="/tv/"]',
                '.result .product_title a',
                'a[href*="/movie/"][class*="title"]',
                'a[href*="/tv/"][class*="title"]'
            ]
            
            for selector in result_selectors:
                results = soup.select(selector)
                if results:
                    href = results[0].get('href')
                    if href:
                        # Ensure it's a full URL
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        
                        self.logger.info(f"✅ Found via search endpoint: {href}")
                        return href
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Search endpoint method failed: {str(e)}")
            return None
    
    def search_via_selenium(self, title: str) -> Optional[str]:
        """Search using Selenium for dynamic content"""
        try:
            self.setup_selenium_driver(headless=True)
            
            # Navigate to search page
            search_url = f"{self.base_url}/search/{quote(title)}/"
            
            if self.safe_selenium_request(search_url):
                wait = WebDriverWait(self.driver, 15)
                
                try:
                    # Wait for search results to load
                    search_results = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.search_results, .search-results'))
                    )
                    
                    # Look for movie/TV show links
                    link_selectors = [
                        'a[href*="/movie/"]',
                        'a[href*="/tv/"]'
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            href = link_element.get_attribute('href')
                            
                            if href and ('/movie/' in href or '/tv/' in href):
                                self.logger.info(f"✅ Found via Selenium: {href}")
                                return href
                                
                        except Exception as e:
                            self.logger.debug(f"Selenium selector '{selector}' failed: {str(e)}")
                            continue
                
                except Exception as e:
                    self.logger.debug(f"Selenium search failed: {str(e)}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Selenium search failed: {str(e)}")
            return None
    
    def extract_real_reviews(self, movie_url: str, max_reviews: int = 40) -> List[Dict[str, str]]:
        """Extract real reviews from Metacritic with pagination"""
        self.logger.info(f"📊 Extracting real Metacritic reviews from: {movie_url}")
        
        all_reviews = []
        
        # Extract critic reviews
        critic_reviews = self.extract_critic_reviews(movie_url)
        all_reviews.extend(critic_reviews)
        
        # Extract user reviews
        user_reviews = self.extract_user_reviews(movie_url, max_reviews - len(critic_reviews))
        all_reviews.extend(user_reviews)
        
        self.logger.info(f"✅ Total Metacritic reviews extracted: {len(all_reviews)}")
        return all_reviews[:max_reviews]
    
    def extract_critic_reviews(self, movie_url: str) -> List[Dict[str, str]]:
        """Extract professional critic reviews"""
        reviews = []
        
        try:
            # Navigate to critic reviews section
            critic_url = movie_url.rstrip('/') + '/critic-reviews'
            
            response = self.safe_request(critic_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors for critic reviews
            review_selectors = [
                '.review.critic_review',
                '.critic_review',
                '[class*="critic-review"]',
                '.review_section .review'
            ]
            
            review_elements = None
            for selector in review_selectors:
                review_elements = soup.select(selector)
                if review_elements:
                    self.logger.debug(f"Found critic reviews with selector: {selector}")
                    break
            
            if not review_elements:
                self.logger.warning("⚠️ No critic review elements found")
                return reviews
            
            for elem in review_elements[:15]:  # Limit critic reviews
                review_data = self.parse_critic_review(elem)
                if review_data:
                    reviews.append(review_data)
            
            self.logger.info(f"📝 Extracted {len(reviews)} critic reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting critic reviews: {str(e)}")
            return reviews
    
    def extract_user_reviews(self, movie_url: str, max_user_reviews: int = 25) -> List[Dict[str, str]]:
        """Extract user reviews with pagination"""
        reviews = []
        
        try:
            # Use Selenium for user reviews as they're often dynamically loaded
            self.setup_selenium_driver(headless=True)
            
            user_reviews_url = movie_url.rstrip('/') + '/user-reviews'
            
            if self.safe_selenium_request(user_reviews_url):
                # Load more reviews by scrolling or clicking load more
                self.load_more_user_reviews()
                
                # Extract reviews from current page state
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Multiple selectors for user reviews
                user_review_selectors = [
                    '.review.user_review',
                    '.user_review',
                    '[class*="user-review"]',
                    '.review_section .user_reviews .review'
                ]
                
                review_elements = None
                for selector in user_review_selectors:
                    review_elements = soup.select(selector)
                    if review_elements:
                        self.logger.debug(f"Found user reviews with selector: {selector}")
                        break
                
                if review_elements:
                    for elem in review_elements[:max_user_reviews]:
                        review_data = self.parse_user_review(elem)
                        if review_data:
                            reviews.append(review_data)
                else:
                    self.logger.warning("⚠️ No user review elements found")
            
            self.logger.info(f"📝 Extracted {len(reviews)} user reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting user reviews: {str(e)}")
            return reviews
    
    def parse_critic_review(self, review_elem) -> Optional[Dict[str, str]]:
        """Parse a single critic review element"""
        try:
            soup = BeautifulSoup(str(review_elem), 'html.parser')
            
            # Extract review text
            text_selectors = [
                '.review_body',
                '.review_text',
                '.summary',
                '[class*="review-body"]'
            ]
            review_text = self.extract_text_safe(soup, text_selectors)
            
            if not review_text or review_text == "Not found" or len(review_text) < 15:
                return None
            
            # Extract critic score
            score_selectors = [
                '.review_grade .metascore',
                '.metascore',
                '.score',
                '[class*="critic-score"]'
            ]
            score = self.extract_text_safe(soup, score_selectors, "N/A")
            
            # Clean score (should be 0-100)
            if score != "N/A":
                score_match = re.search(r'(\d+)', score)
                if score_match:
                    score = score_match.group(1)
            
            # Extract publication
            publication_selectors = [
                '.review_critic .source',
                '.source',
                '.publication',
                '[class*="publication"]'
            ]
            publication = self.extract_text_safe(soup, publication_selectors, "Unknown Publication")
            
            # Extract critic name
            critic_selectors = [
                '.review_critic .author',
                '.author',
                '.critic-name',
                '[class*="critic-name"]'
            ]
            critic = self.extract_text_safe(soup, critic_selectors, "Unknown Critic")
            
            # Extract review date
            date_selectors = [
                '.review_date',
                '.date',
                '[class*="review-date"]'
            ]
            date = self.extract_text_safe(soup, date_selectors, "Unknown")
            
            return {
                'text': review_text,
                'score': score,
                'publication': publication,
                'critic': critic,
                'date': date,
                'type': 'critic'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing critic review: {str(e)}")
            return None
    
    def parse_user_review(self, review_elem) -> Optional[Dict[str, str]]:
        """Parse a single user review element"""
        try:
            soup = BeautifulSoup(str(review_elem), 'html.parser')
            
            # Extract review text
            text_selectors = [
                '.review_body',
                '.review_text',
                '.blurb.blurb_expanded',
                '[class*="review-body"]'
            ]
            review_text = self.extract_text_safe(soup, text_selectors)
            
            if not review_text or review_text == "Not found" or len(review_text) < 15:
                return None
            
            # Extract user score
            score_selectors = [
                '.review_grade .metascore',
                '.user_score .metascore',
                '.score',
                '[class*="user-score"]'
            ]
            score = self.extract_text_safe(soup, score_selectors, "N/A")
            
            # Clean score (should be 0-10 for users)
            if score != "N/A":
                score_match = re.search(r'(\d+(?:\.\d+)?)', score)
                if score_match:
                    score = score_match.group(1)
            
            # Extract username
            user_selectors = [
                '.review_critic .author',
                '.author',
                '.user-name',
                '[class*="username"]'
            ]
            username = self.extract_text_safe(soup, user_selectors, "Anonymous")
            
            # Extract review date
            date_selectors = [
                '.review_date',
                '.date',
                '[class*="review-date"]'
            ]
            date = self.extract_text_safe(soup, date_selectors, "Unknown")
            
            # Extract helpful votes (if available)
            helpful_selectors = [
                '.helpful_summary',
                '.helpful-count',
                '[class*="helpful"]'
            ]
            helpful = self.extract_text_safe(soup, helpful_selectors, "0")
            
            return {
                'text': review_text,
                'score': score,
                'username': username,
                'date': date,
                'helpful_votes': helpful,
                'type': 'user'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing user review: {str(e)}")
            return None
    
    def load_more_user_reviews(self):
        """Load more user reviews by scrolling or clicking load more"""
        try:
            # Method 1: Try clicking "Load More" button
            for _ in range(3):
                try:
                    load_more_selectors = [
                        '.load_more',
                        '.btn.load-more',
                        '[data-action="load-more"]',
                        'button[class*="load-more"]'
                    ]
                    
                    button_found = False
                    for selector in load_more_selectors:
                        try:
                            button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if button.is_displayed() and button.is_enabled():
                                # Scroll to button
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(1)
                                
                                # Click button
                                self.driver.execute_script("arguments[0].click();", button)
                                self.logger.info("✅ Clicked load more reviews button")
                                
                                # Wait for content to load
                                time.sleep(3)
                                button_found = True
                                break
                        except Exception as e:
                            continue
                    
                    if not button_found:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Load more attempt failed: {str(e)}")
                    break
            
            # Method 2: Scroll to bottom to trigger infinite scroll
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
        except Exception as e:
            self.logger.debug(f"Load more reviews failed: {str(e)}")
    
    def extract_basic_movie_data(self, movie_url: str) -> Optional[Dict]:
        """Extract basic movie information from Metacritic"""
        try:
            response = self.safe_request(movie_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'title': self._extract_title(soup),
                'year': self._extract_year(soup),
                'metascore': self._extract_metascore(soup),
                'user_score': self._extract_user_score(soup),
                'genre': self._extract_genre(soup),
                'director': self._extract_director(soup),
                'summary': self._extract_summary(soup),
                'publisher': self._extract_publisher(soup),
                'release_date': self._extract_release_date(soup),
                'rating': self._extract_rating(soup),
                'runtime': self._extract_runtime(soup),
                'cast': self._extract_cast(soup),
                'source': 'Metacritic (Enhanced)',
                'url': movie_url
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting basic Metacritic data: {str(e)}")
            return None
    
    def _extract_title(self, soup) -> str:
        """Extract movie title"""
        selectors = [
            'h1.product_title a',
            'h1.product_title',
            '.product_page_title h1',
            'h1[class*="title"]'
        ]
        return self.extract_text_safe(soup, selectors, "Unknown Title")
    
    def _extract_year(self, soup) -> str:
        """Extract release year"""
        selectors = [
            '.product_year',
            '.release_year', 
            'span[class*="year"]',
            '.product_data .data'
        ]
        year = self.extract_text_safe(soup, selectors, "Unknown")
        
        # Extract year from text
        if year != "Unknown":
            year_match = re.search(r'(\d{4})', year)
            if year_match:
                year = year_match.group(1)
        
        return year
    
    def _extract_metascore(self, soup) -> str:
        """Extract Metascore (critic score)"""
        selectors = [
            '.metascore_w.xlarge.movie.positive',
            '.metascore_w.xlarge.movie.mixed',
            '.metascore_w.xlarge.movie.negative',
            '.metascore_w.xlarge.movie',
            '.metascore',
            '[class*="metascore"]'
        ]
        score = self.extract_text_safe(soup, selectors, "N/A")
        
        # Clean score
        if score != "N/A":
            score_match = re.search(r'(\d+)', score)
            if score_match:
                score = score_match.group(1)
        
        return score
    
    def _extract_user_score(self, soup) -> str:
        """Extract user score"""
        selectors = [
            '.metascore_w.user.large.movie',
            '.user_score .metascore_w',
            '.user_score',
            '[class*="user-score"]'
        ]
        score = self.extract_text_safe(soup, selectors, "N/A")
        
        # Clean score
        if score != "N/A":
            score_match = re.search(r'(\d+(?:\.\d+)?)', score)
            if score_match:
                score = score_match.group(1)
        
        return score
    
    def _extract_genre(self, soup) -> str:
        """Extract genre"""
        selectors = [
            '.product_genre .data',
            '.genres .data',
            'td:contains("Genre:") + td',
            '[class*="genre"]'
        ]
        return self.extract_text_safe(soup, selectors, "Unknown")
    
    def _extract_director(self, soup) -> str:
        """Extract director"""
        selectors = [
            '.director .data',
            '.summary_detail.director .data', 
            'td:contains("Director:") + td',
            '[class*="director"]'
        ]
        return self.extract_text_safe(soup, selectors, "Unknown")
    
    def _extract_summary(self, soup) -> str:
        """Extract plot summary"""
        selectors = [
            '.summary_deck',
            '.blurb.blurb_expanded',
            '.product_summary .data',
            '[class*="summary"]'
        ]
        return self.extract_text_safe(soup, selectors, "No summary available")
    
    def _extract_publisher(self, soup) -> str:
        """Extract publisher/studio"""
        selectors = [
            '.publisher .data',
            '.summary_detail.publisher .data',
            'td:contains("Publisher:") + td',
            '[class*="publisher"]'
        ]
        return self.extract_text_safe(soup, selectors, "Unknown")
    
    def _extract_release_date(self, soup) -> str:
        """Extract release date"""
        selectors = [
            '.release_date .data',
            '.summary_detail.release_date .data',
            'td:contains("Release Date:") + td',
            '[class*="release-date"]'
        ]
        return self.extract_text_safe(soup, selectors, "Unknown")
    
    def _extract_rating(self, soup) -> str:
        """Extract MPAA rating"""
        selectors = [
            '.rating .data',
            '.summary_detail.rating .data',
            'td:contains("Rating:") + td',
            '[class*="mpaa-rating"]'
        ]
        return self.extract_text_safe(soup, selectors, "Not Rated")
    
    def _extract_runtime(self, soup) -> str:
        """Extract runtime"""
        selectors = [
            '.runtime .data',
            '.summary_detail.runtime .data',
            'td:contains("Runtime:") + td',
            '[class*="runtime"]'
        ]
        return self.extract_text_safe(soup, selectors, "Unknown")
    
    def _extract_cast(self, soup) -> List[str]:
        """Extract main cast"""
        try:
            cast_selectors = [
                '.summary_detail.starring .data',
                '.cast .data',
                'td:contains("Starring:") + td'
            ]
            
            cast_text = self.extract_text_safe(soup, cast_selectors, "")
            
            if cast_text and cast_text != "Not found":
                # Split by common delimiters
                cast_list = re.split(r'[,;]', cast_text)
                return [actor.strip() for actor in cast_list if actor.strip()][:5]
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting cast: {str(e)}")
            return []
    
    def scrape_movie_data(self, movie_title: str) -> Optional[Dict]:
        """Enhanced Metacritic scraping with real reviews"""
        try:
            self.logger.info(f"📊 Starting enhanced Metacritic scrape for: {movie_title}")
            
            # Find movie URL
            movie_url = self.search_title_advanced(movie_title)
            if not movie_url:
                self.logger.warning(f"⚠️ Movie not found on Metacritic, using fallback data")
                return self._create_fallback_data(movie_title)
            
            # Extract basic movie data
            basic_data = self.extract_basic_movie_data(movie_url)
            
            # Extract real reviews
            real_reviews = self.extract_real_reviews(movie_url, max_reviews=35)
            
            # Combine data
            if basic_data:
                # Separate review types
                critic_reviews = [r for r in real_reviews if r.get('type') == 'critic']
                user_reviews = [r for r in real_reviews if r.get('type') == 'user']
                
                basic_data['reviews'] = [r['text'] for r in real_reviews if r.get('text')]
                basic_data['detailed_reviews'] = real_reviews
                basic_data['critic_reviews'] = critic_reviews
                basic_data['user_reviews'] = user_reviews
                basic_data['total_reviews_extracted'] = len(real_reviews)
                
                self.logger.info(f"✅ Metacritic: {len(critic_reviews)} critic + {len(user_reviews)} user reviews")
                return basic_data
            else:
                return self._create_fallback_data(movie_title)
                
        except Exception as e:
            self.logger.error(f"❌ Enhanced Metacritic scraping failed: {str(e)}")
            return self._create_fallback_data(movie_title)
    
    def _create_fallback_data(self, title: str) -> Dict:
        """Enhanced fallback data for Metacritic"""
        return {
            'title': title,
            'year': "2023",
            'metascore': str(random.randint(60, 85)),
            'user_score': str(round(random.uniform(6.5, 8.5), 1)),
            'genre': "Drama, Thriller",
            'director': "Sample Director",
            'summary': f"A compelling story about {title} that showcases exceptional filmmaking.",
            'publisher': "Sample Studio",
            'release_date': "Unknown",
            'rating': "PG-13",
            'runtime': f"{random.randint(90, 180)} minutes",
            'cast': ["Lead Actor", "Supporting Actor", "Character Actor"],
            'reviews': self._get_sample_reviews(title),
            'detailed_reviews': [],
            'critic_reviews': [],
            'user_reviews': [],
            'total_reviews_extracted': 0,
            'source': 'Metacritic (Sample Data)',
            'url': f"https://www.metacritic.com/movie/sample_{title.replace(' ', '-').lower()}"
        }
    
    def _get_sample_reviews(self, title: str) -> List[str]:
        """Generate realistic sample reviews for Metacritic"""
        return [
            f"{title} delivers outstanding performances with exceptional direction and cinematography.",
            f"A masterful film that showcases {title} at its finest. Highly recommended viewing.",
            f"Brilliant storytelling and compelling characters make {title} a standout production.",
            f"Exceptional filmmaking with {title} offering both entertainment and artistic merit.",
            f"Outstanding work that elevates {title} above typical genre expectations."
        ]
    
    # Add this method around line 200
    def scrape_movie_data(self, title: str) -> Optional[Dict]:
        """Main method to scrape movie data from Metacritic"""
        try:
            self.logger.info(f"🎬 Starting Metacritic scrape for: {title}")
            
            # Find the movie URL
            movie_url = self.search_title_advanced(title)
            if not movie_url:
                self.logger.error(f"❌ Could not find Metacritic page for: {title}")
                return None
            
            # Extract movie details
            movie_data = self.extract_movie_details(movie_url)
            if not movie_data:
                self.logger.error(f"❌ Could not extract data from: {movie_url}")
                return None
            
            # Extract reviews
            reviews = self.extract_reviews(movie_url)
            movie_data['reviews'] = reviews
            movie_data['review_count'] = len(reviews)
            
            self.logger.info(f"✅ Successfully scraped Metacritic data for: {title}")
            return movie_data
            
        except Exception as e:
            self.logger.error(f"❌ Metacritic scraping failed for {title}: {str(e)}")
            return None

    def extract_movie_details(self, url: str) -> Optional[Dict]:
        """Extract movie details from Metacritic page"""
        try:
            response = self.safe_request(url, use_cloudscraper=True)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            data = {
                'title': self.extract_text_safe(soup, [
                    '.product_title h1',
                    '.c-productHero_title',
                    'h1'
                ]),
                'year': self.extract_year_from_page(soup),
                'genre': self.extract_genre(soup),
                'director': self.extract_director(soup),
                'metascore': self.extract_metascore(soup),
                'user_score': self.extract_user_score(soup),
                'summary': self.extract_summary(soup),
                'url': url
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract movie details: {str(e)}")
            return None

    def extract_reviews(self, url: str, max_reviews: int = 15) -> List[Dict]:
        """Extract user reviews from Metacritic"""
        try:
            reviews = []
            
            # Navigate to user reviews section
            if '/movie/' in url:
                reviews_url = url.rstrip('/') + '/user-reviews'
            elif '/tv/' in url:
                reviews_url = url.rstrip('/') + '/user-reviews'
            else:
                reviews_url = url
            
            if self.safe_selenium_request(reviews_url):
                # Load more reviews if possible
                self.load_more_user_reviews()
                
                # Extract reviews from current page
                page_source = self.get_page_source_safe()
                if page_source:
                    soup = BeautifulSoup(page_source, 'html.parser')
                    reviews = self.parse_reviews_from_soup(soup, max_reviews)
            
            return reviews[:max_reviews]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract reviews: {str(e)}")
            return []

    def parse_reviews_from_soup(self, soup: BeautifulSoup, max_reviews: int) -> List[Dict]:
        """Parse reviews from BeautifulSoup object"""
        reviews = []
        
        review_selectors = [
            '.review_content',
            '.user_review',
            '.c-siteReview'
        ]
        
        for selector in review_selectors:
            review_elements = soup.select(selector)
            if review_elements:
                break
        
        for element in review_elements[:max_reviews]:
            try:
                review = {
                    'text': self.extract_text_safe(element, ['.review_body', '.c-siteReview_quote']),
                    'rating': self.extract_rating_from_review(element),
                    'author': self.extract_text_safe(element, ['.author', '.c-siteReview_author']),
                    'date': self.extract_text_safe(element, ['.date', '.c-siteReview_date'])
                }
                
                if review['text'] and len(review['text']) > 10:
                    reviews.append(review)
                    
            except Exception as e:
                self.logger.debug(f"Failed to parse review: {str(e)}")
                continue
        
        return reviews

    def extract_year_from_page(self, soup: BeautifulSoup) -> str:
        """Extract year from Metacritic page"""
        try:
            # Multiple selectors for year extraction
            year_selectors = [
                '.product_year',
                '.release_year', 
                'span[class*="year"]',
                '.product_data .data'
            ]
            
            year_text = self.extract_text_safe(soup, year_selectors, "Unknown")
            
            # Extract 4-digit year
            if year_text != "Unknown":
                year_match = re.search(r'(\d{4})', year_text)
                if year_match:
                    return year_match.group(1)
            
            return "Unknown"
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting year: {str(e)}")
            return "Unknown"

    def extract_genre(self, soup: BeautifulSoup) -> str:
        """Extract genre from Metacritic page"""
        try:
            genre_selectors = [
                '.product_genre .data',
                '.genres .data',
                'td:contains("Genre:") + td',
                '[class*="genre"]'
            ]
            return self.extract_text_safe(soup, genre_selectors, "Unknown")
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting genre: {str(e)}")
            return "Unknown"

    def extract_director(self, soup: BeautifulSoup) -> str:
        """Extract director from Metacritic page"""
        try:
            director_selectors = [
                '.director .data',
                '.summary_detail.director .data', 
                'td:contains("Director:") + td',
                '[class*="director"]'
            ]
            return self.extract_text_safe(soup, director_selectors, "Unknown")
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting director: {str(e)}")
            return "Unknown"

    def extract_metascore(self, soup: BeautifulSoup) -> str:
        """Extract Metascore from Metacritic page"""
        try:
            metascore_selectors = [
                '.metascore_w.xlarge.movie.positive',
                '.metascore_w.xlarge.movie.mixed', 
                '.metascore_w.xlarge.movie.negative',
                '.metascore_w.xlarge.movie',
                '.metascore',
                '[class*="metascore"]'
            ]
            
            score = self.extract_text_safe(soup, metascore_selectors, "N/A")
            
            # Clean score
            if score != "N/A":
                score_match = re.search(r'(\d+)', score)
                if score_match:
                    score = score_match.group(1)
            
            return score
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting metascore: {str(e)}")
            return "N/A"

    def extract_user_score(self, soup: BeautifulSoup) -> str:
        """Extract user score from Metacritic page"""
        try:
            user_score_selectors = [
                '.metascore_w.user.large.movie',
                '.user_score .metascore_w',
                '.user_score',
                '[class*="user-score"]'
            ]
            
            score = self.extract_text_safe(soup, user_score_selectors, "N/A")
            
            # Clean score
            if score != "N/A":
                score_match = re.search(r'(\d+(?:\.\d+)?)', score)
                if score_match:
                    score = score_match.group(1)
            
            return score
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting user score: {str(e)}")
            return "N/A"

    def extract_summary(self, soup: BeautifulSoup) -> str:
        """Extract plot summary from Metacritic page"""
        try:
            summary_selectors = [
                '.summary_deck',
                '.blurb.blurb_expanded',
                '.product_summary .data',
                '[class*="summary"]'
            ]
            return self.extract_text_safe(soup, summary_selectors, "No summary available")
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting summary: {str(e)}")
            return "No summary available"

    def extract_rating_from_review(self, element) -> str:
        """Extract rating from review element"""
        try:
            rating_selectors = [
                '.metascore',
                '.score',
                '.rating',
                '[class*="score"]'
            ]
            
            soup = BeautifulSoup(str(element), 'html.parser')
            rating = self.extract_text_safe(soup, rating_selectors, "N/A")
            
            # Extract numeric rating
            if rating != "N/A":
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating)
                if rating_match:
                    return rating_match.group(1)
            
            return "N/A"
            
        except Exception as e:
            self.logger.debug(f"Failed to extract rating: {str(e)}")
            return "N/A"