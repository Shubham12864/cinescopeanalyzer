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

class RottenTomatoesScraper(AdvancedScraperBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.rottentomatoes.com"
    
    def search_title_advanced(self, title: str) -> Optional[str]:
        """Advanced RT search with multiple methods"""
        self.logger.info(f"🍅 Advanced RT search for: {title}")
        
        # Method 1: Direct URL construction
        url = self.search_via_url_construction(title)
        if url:
            return url
        
        # Method 2: Search page
        url = self.search_via_search_page(title)
        if url:
            return url
        
        # Method 3: Selenium-based search
        url = self.search_via_selenium(title)
        if url:
            return url
        
        return None
    
    def search_via_url_construction(self, title: str) -> Optional[str]:
        """Try common URL patterns"""
        try:
            # Format title for RT URL style
            formatted_title = title.lower()
            formatted_title = re.sub(r'[^\w\s]', '', formatted_title)
            formatted_title = formatted_title.replace(' ', '_')
            
            # Common patterns
            patterns = [
                f"{self.base_url}/m/{formatted_title}",
                f"{self.base_url}/tv/{formatted_title}",
                f"{self.base_url}/m/{formatted_title}_2023",
                f"{self.base_url}/m/{formatted_title}_2024",
                f"{self.base_url}/m/{formatted_title}_2022",
            ]
            
            for url in patterns:
                try:
                    response = self.safe_request(url)
                    if response.status_code == 200 and "Page Not Found" not in response.text:
                        self.logger.info(f"✅ Found RT URL: {url}")
                        return url
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ URL construction search failed: {str(e)}")
            return None
    
    def search_via_search_page(self, title: str) -> Optional[str]:
        """Search via RT search page"""
        try:
            search_url = f"{self.base_url}/search?search={quote(title)}"
            response = self.safe_request(search_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for movie/TV show links
            link_selectors = [
                'search-page-media-row a[href*="/m/"]',
                'search-page-media-row a[href*="/tv/"]',
                'a[data-qa="info-name"][href*="/m/"]',
                'a[href*="/m/"]:contains("' + title + '")'
            ]
            
            for selector in link_selectors:
                results = soup.select(selector)
                if results:
                    href = results[0].get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        self.logger.info(f"✅ Found via search page: {full_url}")
                        return full_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Search page method failed: {str(e)}")
            return None
    
    def search_via_selenium(self, title: str) -> Optional[str]:
        """Search using Selenium"""
        try:
            self.setup_selenium_driver(headless=True)
            
            search_url = f"{self.base_url}/search?search={quote(title)}"
            
            if self.safe_selenium_request(search_url):
                wait = WebDriverWait(self.driver, 10)
                
                try:
                    # Look for movie links
                    link_element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/m/"], a[href*="/tv/"]'))
                    )
                    href = link_element.get_attribute('href')
                    
                    if href:
                        self.logger.info(f"✅ Found via Selenium: {href}")
                        return href
                        
                except Exception as e:
                    self.logger.debug(f"Selenium search failed: {str(e)}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Selenium search failed: {str(e)}")
            return None
    
    def extract_real_reviews(self, movie_url: str, max_reviews: int = 30) -> List[Dict[str, str]]:
        """Extract real reviews from RT"""
        self.logger.info(f"🍅 Extracting real RT reviews from: {movie_url}")
        
        all_reviews = []
        
        # Extract critic reviews
        critic_reviews = self.extract_critic_reviews(movie_url)
        all_reviews.extend(critic_reviews)
        
        # Extract audience reviews
        audience_reviews = self.extract_audience_reviews(movie_url)
        all_reviews.extend(audience_reviews)
        
        self.logger.info(f"✅ Total RT reviews extracted: {len(all_reviews)}")
        return all_reviews[:max_reviews]
    
    def extract_critic_reviews(self, movie_url: str) -> List[Dict[str, str]]:
        """Extract critic reviews"""
        reviews = []
        
        try:
            # Navigate to reviews page
            reviews_url = movie_url.rstrip('/') + '/reviews'
            response = self.safe_request(reviews_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors for critic reviews
            review_selectors = [
                '.review_table_row',
                '[data-qa="review-item"]',
                '.critic-review-item'
            ]
            
            review_elements = None
            for selector in review_selectors:
                review_elements = soup.select(selector)
                if review_elements:
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
    
    def extract_audience_reviews(self, movie_url: str) -> List[Dict[str, str]]:
        """Extract audience reviews"""
        reviews = []
        
        try:
            # Navigate to audience reviews
            audience_url = movie_url.rstrip('/') + '/reviews?type=user'
            
            # Use Selenium for dynamic audience reviews
            self.setup_selenium_driver(headless=True)
            
            if self.safe_selenium_request(audience_url):
                # Load more reviews
                self.load_more_audience_reviews()
                
                # Parse reviews
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                audience_selectors = [
                    '[data-qa="audience-review-item"]',
                    '.audience-review-item',
                    '.user-review'
                ]
                
                review_elements = None
                for selector in audience_selectors:
                    review_elements = soup.select(selector)
                    if review_elements:
                        break
                
                if review_elements:
                    for elem in review_elements:
                        review_data = self.parse_audience_review(elem)
                        if review_data:
                            reviews.append(review_data)
            
            self.logger.info(f"📝 Extracted {len(reviews)} audience reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting audience reviews: {str(e)}")
            return reviews
    
    def parse_critic_review(self, review_elem) -> Optional[Dict[str, str]]:
        """Parse a critic review element"""
        try:
            soup = BeautifulSoup(str(review_elem), 'html.parser')
            
            # Extract review text
            text_selectors = [
                '.the_review',
                '[data-qa="review-text"]',
                '.review-text'
            ]
            review_text = self.extract_text_safe(soup, text_selectors)
            
            if not review_text or review_text == "Not found" or len(review_text) < 20:
                return None
            
            # Extract critic name
            critic_selectors = [
                '.critic-name a',
                '[data-qa="review-critic-name"]',
                '.reviewer-name'
            ]
            critic = self.extract_text_safe(soup, critic_selectors, "Unknown Critic")
            
            # Extract publication
            publication_selectors = [
                '.publication',
                '[data-qa="review-publication"]',
                '.critic-publication'
            ]
            publication = self.extract_text_safe(soup, publication_selectors, "Unknown Publication")
            
            # Extract fresh/rotten status
            fresh_selectors = [
                '.fresh',
                '.rotten',
                '[data-qa="review-status"]'
            ]
            status = "Fresh"  # Default
            for selector in fresh_selectors:
                elem = soup.select_one(selector)
                if elem:
                    if 'rotten' in elem.get('class', []):
                        status = "Rotten"
                    break
            
            return {
                'text': review_text,
                'critic': critic,
                'publication': publication,
                'status': status,
                'type': 'critic'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing critic review: {str(e)}")
            return None
    
    def parse_audience_review(self, review_elem) -> Optional[Dict[str, str]]:
        """Parse an audience review element"""
        try:
            soup = BeautifulSoup(str(review_elem), 'html.parser')
            
            # Extract review text
            text_selectors = [
                '[data-qa="review-text"]',
                '.user-review-text',
                '.audience-review-text'
            ]
            review_text = self.extract_text_safe(soup, text_selectors)
            
            if not review_text or review_text == "Not found" or len(review_text) < 20:
                return None
            
            # Extract rating
            rating_selectors = [
                '[data-qa="review-rating"]',
                '.star-rating',
                '.audience-rating'
            ]
            rating = self.extract_text_safe(soup, rating_selectors, "N/A")
            
            # Extract reviewer name
            reviewer_selectors = [
                '[data-qa="review-username"]',
                '.reviewer-name',
                '.user-name'
            ]
            reviewer = self.extract_text_safe(soup, reviewer_selectors, "Anonymous")
            
            return {
                'text': review_text,
                'rating': rating,
                'reviewer': reviewer,
                'type': 'audience'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing audience review: {str(e)}")
            return None
    
    def load_more_audience_reviews(self):
        """Load more audience reviews by clicking load more"""
        try:
            for _ in range(3):  # Try to load more 3 times
                try:
                    load_more = self.driver.find_element(By.CSS_SELECTOR, '[data-qa="load-more-btn"], .load-more-btn')
                    if load_more.is_displayed():
                        self.driver.execute_script("arguments[0].click();", load_more)
                        time.sleep(2)
                    else:
                        break
                except:
                    break
                    
        except Exception as e:
            self.logger.debug(f"Load more failed: {str(e)}")
    
    def scrape_movie_data(self, movie_title: str) -> Optional[Dict]:
        """Enhanced RT scraping with real reviews"""
        try:
            self.logger.info(f"🍅 Starting enhanced RT scrape for: {movie_title}")
            
            movie_url = self.search_title_advanced(movie_title)
            if not movie_url:
                return self._create_fallback_data(movie_title)
            
            # Extract basic data
            basic_data = self.extract_basic_movie_data(movie_url)
            
            # Extract real reviews
            real_reviews = self.extract_real_reviews(movie_url, max_reviews=25)
            
            if basic_data:
                # Separate review types
                critic_reviews = [r for r in real_reviews if r.get('type') == 'critic']
                audience_reviews = [r for r in real_reviews if r.get('type') == 'audience']
                
                basic_data['reviews'] = [r['text'] for r in real_reviews if r.get('text')]
                basic_data['detailed_reviews'] = real_reviews
                basic_data['critic_reviews'] = critic_reviews
                basic_data['audience_reviews'] = audience_reviews
                basic_data['total_reviews_extracted'] = len(real_reviews)
                
                self.logger.info(f"✅ RT: {len(critic_reviews)} critic + {len(audience_reviews)} audience reviews")
                return basic_data
            else:
                return self._create_fallback_data(movie_title)
                
        except Exception as e:
            self.logger.error(f"❌ Enhanced RT scraping failed: {str(e)}")
            return self._create_fallback_data(movie_title)
    
    # Keep all your existing RT extraction methods here
    # Add the enhanced review extraction capabilities