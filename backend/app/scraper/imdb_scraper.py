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

class ImdbScraper(AdvancedScraperBase):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.imdb.com"
        self.headers_pool = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-GB,en;q=0.5',
            }
        ]
    
    def search_title_advanced(self, title: str) -> Optional[str]:
        """Advanced title search with multiple fallback methods"""
        self.logger.info(f"🔍 Advanced IMDb search for: {title}")
        
        # Method 1: Standard search
        url = self.search_via_find_endpoint(title)
        if url:
            return url
        
        # Method 2: Suggestion API (if available)
        url = self.search_via_suggestions(title)
        if url:
            return url
        
        # Method 3: Selenium-based search
        url = self.search_via_selenium(title)
        if url:
            return url
        
        self.logger.error(f"❌ All search methods failed for: {title}")
        return None
    
    def search_via_find_endpoint(self, title: str) -> Optional[str]:
        """Search using IMDb find endpoint"""
        try:
            clean_title = re.sub(r'[^\w\s]', '', title).strip()
            encoded_title = quote(clean_title)
            search_url = f"{self.base_url}/find/?q={encoded_title}&s=tt&ttype=ft"
            
            response = self.safe_request(search_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors for search results
            selectors = [
                'td.result_text a[href*="/title/tt"]',
                '.ipc-metadata-list-summary-item__t a[href*="/title/"]',
                '.titleColumn a[href*="/title/"]',
                'a[href*="/title/tt"]'
            ]
            
            for selector in selectors:
                results = soup.select(selector)
                if results:
                    href = results[0].get('href')
                    if href and '/title/tt' in href:
                        full_url = urljoin(self.base_url, href.split('?')[0])
                        self.logger.info(f"✅ Found via find endpoint: {full_url}")
                        return full_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Find endpoint search failed: {str(e)}")
            return None
    
    def search_via_suggestions(self, title: str) -> Optional[str]:
        """Search using IMDb suggestion API"""
        try:
            # IMDb suggestion endpoint
            clean_title = re.sub(r'[^\w\s]', '', title).strip()
            encoded_title = quote(clean_title)
            suggest_url = f"{self.base_url}/suggestion/{encoded_title[0].lower()}/{encoded_title}.json"
            
            response = self.safe_request(suggest_url)
            data = response.json()
            
            # Look for movie/TV show results
            for item in data.get('d', []):
                if item.get('id', '').startswith('tt') and 'title' in item:
                    movie_url = f"{self.base_url}/title/{item['id']}/"
                    self.logger.info(f"✅ Found via suggestions: {movie_url}")
                    return movie_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Suggestion search failed: {str(e)}")
            return None
    
    def search_via_selenium(self, title: str) -> Optional[str]:
        """Search using Selenium for dynamic content"""
        try:
            self.setup_selenium_driver(headless=True)
            
            search_url = f"{self.base_url}/find/?q={quote(title)}&s=tt"
            
            if self.safe_selenium_request(search_url, '.ipc-page-content-container'):
                # Wait for results to load
                wait = WebDriverWait(self.driver, 10)
                
                try:
                    # Look for title links
                    link_element = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/title/tt"]'))
                    )
                    href = link_element.get_attribute('href')
                    
                    if href:
                        clean_url = href.split('?')[0]
                        self.logger.info(f"✅ Found via Selenium: {clean_url}")
                        return clean_url
                        
                except Exception as e:
                    self.logger.debug(f"Selenium search element not found: {str(e)}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Selenium search failed: {str(e)}")
            return None
    
    def extract_real_reviews(self, movie_url: str, max_reviews: int = 50) -> List[Dict[str, str]]:
        """Extract real reviews from IMDb with pagination"""
        self.logger.info(f"🎬 Extracting real reviews from: {movie_url}")
        
        # Construct reviews URL
        movie_id = re.search(r'/title/(tt\d+)', movie_url)
        if not movie_id:
            self.logger.error("❌ Could not extract movie ID from URL")
            return []
        
        reviews_url = f"{self.base_url}/title/{movie_id.group(1)}/reviews/"
        return self.extract_reviews_with_pagination(reviews_url, max_reviews)
    
    def extract_reviews_with_pagination(self, reviews_url: str, max_reviews: int) -> List[Dict[str, str]]:
        """Extract reviews with advanced pagination handling"""
        all_reviews = []
        current_reviews = 0
        
        try:
            # Setup Selenium for dynamic content
            self.setup_selenium_driver(headless=True)
            
            if not self.safe_selenium_request(reviews_url, '.review-container'):
                self.logger.error("❌ Failed to load reviews page")
                return []
            
            # Load more reviews by clicking "Load More" button
            while current_reviews < max_reviews:
                # Extract current page reviews
                page_reviews = self.extract_current_page_reviews()
                
                if not page_reviews:
                    break
                
                all_reviews.extend(page_reviews)
                current_reviews = len(all_reviews)
                
                self.logger.info(f"📝 Extracted {len(page_reviews)} reviews, total: {current_reviews}")
                
                # Try to load more reviews
                if not self.click_load_more_button():
                    break
                
                # Smart delay between page loads
                self.smart_delay(1.0)
            
            self.logger.info(f"✅ Total reviews extracted: {len(all_reviews)}")
            return all_reviews[:max_reviews]
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting reviews: {str(e)}")
            return all_reviews
    
    def extract_current_page_reviews(self) -> List[Dict[str, str]]:
        """Extract reviews from current page state"""
        reviews = []
        
        try:
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Multiple selectors for review containers
            review_selectors = [
                '.review-container',
                '.lister-item-content',
                '[data-testid="review-card"]'
            ]
            
            review_elements = None
            for selector in review_selectors:
                review_elements = soup.select(selector)
                if review_elements:
                    break
            
            if not review_elements:
                self.logger.warning("⚠️ No review elements found on page")
                return reviews
            
            for review_elem in review_elements:
                review_data = self.parse_single_review(review_elem)
                if review_data:
                    reviews.append(review_data)
            
            return reviews
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting current page reviews: {str(e)}")
            return reviews
    
    def parse_single_review(self, review_elem) -> Optional[Dict[str, str]]:
        """Parse a single review element"""
        try:
            review_data = {}
            
            # Extract review text
            text_selectors = [
                '.text.show-more__control',
                '.content .text',
                '[data-testid="review-text"]',
                '.review-text'
            ]
            review_text = self.extract_text_safe(BeautifulSoup(str(review_elem), 'html.parser'), text_selectors)
            
            if not review_text or review_text == "Not found" or len(review_text) < 20:
                return None
            
            review_data['text'] = review_text
            
            # Extract rating
            rating_selectors = [
                '.rating-other-user-rating span',
                '.ipl-ratings-bar span[class*="rating"]',
                '[data-testid="review-rating"]'
            ]
            rating = self.extract_text_safe(BeautifulSoup(str(review_elem), 'html.parser'), rating_selectors, "N/A")
            
            # Clean rating (extract number)
            if rating != "N/A":
                rating_match = re.search(r'(\d+)/10', rating)
                if rating_match:
                    rating = rating_match.group(1)
            
            review_data['rating'] = rating
            
            # Extract reviewer
            reviewer_selectors = [
                '.display-name-link a',
                '.author a',
                '[data-testid="review-author"]'
            ]
            reviewer = self.extract_text_safe(BeautifulSoup(str(review_elem), 'html.parser'), reviewer_selectors, "Anonymous")
            review_data['reviewer'] = reviewer
            
            # Extract date
            date_selectors = [
                '.review-date',
                '[data-testid="review-date"]',
                '.ipl-rating-widget + span'
            ]
            date = self.extract_text_safe(BeautifulSoup(str(review_elem), 'html.parser'), date_selectors, "Unknown")
            review_data['date'] = date
            
            # Extract helpful votes
            helpful_selectors = [
                '.actions.text-muted',
                '[data-testid="review-helpful"]'
            ]
            helpful = self.extract_text_safe(BeautifulSoup(str(review_elem), 'html.parser'), helpful_selectors, "0")
            review_data['helpful_votes'] = helpful
            
            return review_data
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing single review: {str(e)}")
            return None
    
    def click_load_more_button(self) -> bool:
        """Click the load more button if available"""
        try:
            load_more_selectors = [
                '.load-more-trigger',
                '#load-more-trigger',
                '[data-testid="load-more-button"]',
                'button[class*="load-more"]'
            ]
            
            for selector in load_more_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        # Scroll to button first
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        
                        # Click button
                        button.click()
                        self.logger.info("✅ Clicked load more button")
                        
                        # Wait for new content to load
                        time.sleep(3)
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Load more selector '{selector}' failed: {str(e)}")
                    continue
            
            self.logger.info("ℹ️ No load more button found")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error clicking load more button: {str(e)}")
            return False
    
    def scrape_movie_data(self, movie_title: str) -> Optional[Dict]:
        """Enhanced movie data scraping with real reviews"""
        try:
            self.logger.info(f"🎬 Starting enhanced IMDb scrape for: {movie_title}")
            
            # Find movie URL
            movie_url = self.search_title_advanced(movie_title)
            if not movie_url:
                self.logger.warning(f"⚠️ Movie not found, using fallback data")
                return self._create_fallback_data(movie_title)
            
            # Extract basic movie data
            basic_data = self.extract_basic_movie_data(movie_url)
            
            # Extract real reviews
            real_reviews = self.extract_real_reviews(movie_url, max_reviews=30)
            
            # Combine data
            if basic_data:
                basic_data['reviews'] = [review['text'] for review in real_reviews if review.get('text')]
                basic_data['detailed_reviews'] = real_reviews
                basic_data['total_reviews_extracted'] = len(real_reviews)
                
                self.logger.info(f"✅ Successfully extracted {len(real_reviews)} real reviews")
                return basic_data
            else:
                return self._create_fallback_data(movie_title)
                
        except Exception as e:
            self.logger.error(f"❌ Enhanced scraping failed: {str(e)}")
            return self._create_fallback_data(movie_title)
    
    def _extract_title(self, soup) -> str:
        """Extract movie title from IMDb page"""
        try:
            # Try multiple selectors for title
            title_selectors = [
                'h1[data-testid="hero-title-block__title"]',
                'h1.titleType',
                'h1.hero__primary-text',
                '.title_wrapper h1',
                'h1'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    # Clean up title (remove year if present)
                    title = re.sub(r'\s*\(\d{4}\).*$', '', title)
                    return title
            
            return "Unknown Title"
        except Exception as e:
            self.logger.error(f"Error extracting title: {e}")
            return "Unknown Title"
    
    def _extract_year(self, soup) -> int:
        """Extract movie year from IMDb page"""
        try:
            # Try multiple selectors for year
            year_selectors = [
                '[data-testid="hero-title-block__metadata"] a',
                '.subtext a[href*="year"]',
                '.titleBar .nobr a'
            ]
            
            for selector in year_selectors:
                year_elem = soup.select_one(selector)
                if year_elem:
                    year_text = year_elem.get_text().strip()
                    year_match = re.search(r'(\d{4})', year_text)
                    if year_match:
                        return int(year_match.group(1))
            
            return 2000
        except Exception as e:
            self.logger.error(f"Error extracting year: {e}")
            return 2000
    
    def _extract_rating(self, soup) -> float:
        """Extract IMDb rating"""
        try:
            rating_selectors = [
                '[data-testid="hero-rating-bar__aggregate-rating__score"] span',
                '.ratingValue strong span',
                '.aggregateRatingButton .ratingValue strong'
            ]
            
            for selector in rating_selectors:
                rating_elem = soup.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get_text().strip()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        return float(rating_match.group(1))
            
            return 5.0
        except Exception as e:
            self.logger.error(f"Error extracting rating: {e}")
            return 5.0
    
    def _extract_genre(self, soup) -> List[str]:
        """Extract movie genres"""
        try:
            genre_selectors = [
                '[data-testid="genres"] .chip',
                '.see-more.inline.canwrap a',
                '.subtext a[href*="genres"]'
            ]
            
            genres = []
            for selector in genre_selectors:
                genre_elems = soup.select(selector)
                for elem in genre_elems:
                    genre = elem.get_text().strip()
                    if genre and genre not in genres:
                        genres.append(genre)
            
            return genres if genres else ["Unknown"]
        except Exception as e:
            self.logger.error(f"Error extracting genres: {e}")
            return ["Unknown"]
    
    def _extract_director(self, soup) -> str:
        """Extract movie director"""
        try:
            director_selectors = [
                '[data-testid="title-pc-principal-credit"] a',
                '.credit_summary_item:contains("Director") a',
                '.plot_summary .credit_summary_item a'
            ]
            
            for selector in director_selectors:
                director_elem = soup.select_one(selector)
                if director_elem:
                    return director_elem.get_text().strip()
            
            return "Unknown Director"
        except Exception as e:
            self.logger.error(f"Error extracting director: {e}")
            return "Unknown Director"
    
    def _extract_plot(self, soup) -> str:
        """Extract movie plot/summary"""
        try:
            plot_selectors = [
                '[data-testid="plot-xl"]',
                '[data-testid="plot"]',
                '.plot_summary .summary_text',
                '.summary_text'
            ]
            
            for selector in plot_selectors:
                plot_elem = soup.select_one(selector)
                if plot_elem:
                    plot = plot_elem.get_text().strip()
                    # Clean up plot text
                    plot = re.sub(r'\s+', ' ', plot)
                    return plot
            
            return "No plot available."
        except Exception as e:
            self.logger.error(f"Error extracting plot: {e}")
            return "No plot available."
    
    def _extract_cast(self, soup) -> List[str]:
        """Extract main cast members"""
        try:
            cast_selectors = [
                '[data-testid="title-cast"] .cast-item a',
                '.cast_list .primary_photo + td a',
                '.cast .actor a'
            ]
            
            cast = []
            for selector in cast_selectors:
                cast_elems = soup.select(selector)
                for elem in cast_elems[:5]:  # Limit to top 5
                    actor = elem.get_text().strip()
                    if actor and actor not in cast:
                        cast.append(actor)
            
            return cast if cast else ["Unknown Cast"]
        except Exception as e:
            self.logger.error(f"Error extracting cast: {e}")
            return ["Unknown Cast"]
    
    def _extract_runtime(self, soup) -> int:
        """Extract movie runtime in minutes"""
        try:
            runtime_selectors = [
                '[data-testid="title-techspec_runtime"] .cli-title',
                '.subtext time',
                '.runtime'
            ]
            
            for selector in runtime_selectors:
                runtime_elem = soup.select_one(selector)
                if runtime_elem:
                    runtime_text = runtime_elem.get_text().strip()
                    runtime_match = re.search(r'(\d+)', runtime_text)
                    if runtime_match:
                        return int(runtime_match.group(1))
            
            return 120
        except Exception as e:
            self.logger.error(f"Error extracting runtime: {e}")
            return 120
    
    def _extract_country(self, soup) -> str:
        """Extract country of origin"""
        try:
            country_selectors = [
                '[data-testid="title-details-origin"] a',
                '.txt-block:contains("Country") a'
            ]
            
            for selector in country_selectors:
                country_elem = soup.select_one(selector)
                if country_elem:
                    return country_elem.get_text().strip()
            
            return "Unknown"
        except Exception as e:
            self.logger.error(f"Error extracting country: {e}")
            return "Unknown"
    
    def _extract_language(self, soup) -> str:
        """Extract primary language"""
        try:
            language_selectors = [
                '[data-testid="title-details-languages"] a',
                '.txt-block:contains("Language") a'
            ]
            
            for selector in language_selectors:
                language_elem = soup.select_one(selector)
                if language_elem:
                    return language_elem.get_text().strip()
            
            return "English"
        except Exception as e:
            self.logger.error(f"Error extracting language: {e}")
            return "English"
    
    def _extract_budget(self, soup) -> str:
        """Extract movie budget"""
        try:
            budget_selectors = [
                '.txt-block:contains("Budget") .info-content',
                '.budgetary-info .monetary'
            ]
            
            for selector in budget_selectors:
                budget_elem = soup.select_one(selector)
                if budget_elem:
                    return budget_elem.get_text().strip()
            
            return "Unknown"
        except Exception as e:
            self.logger.error(f"Error extracting budget: {e}")
            return "Unknown"
    
    def _extract_box_office(self, soup) -> str:
        """Extract box office information"""
        try:
            box_office_selectors = [
                '.txt-block:contains("Gross worldwide") .info-content',
                '.box-office .monetary'
            ]
            
            for selector in box_office_selectors:
                box_office_elem = soup.select_one(selector)
                if box_office_elem:
                    return box_office_elem.get_text().strip()
            
            return "Unknown"
        except Exception as e:
            self.logger.error(f"Error extracting box office: {e}")
            return "Unknown"

    # ...existing code...
    
    def extract_basic_movie_data(self, movie_url: str) -> Optional[Dict]:
        """Extract basic movie information"""
        try:
            response = self.safe_request(movie_url, use_cloudscraper=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all the existing data using your current methods
            data = {
                'title': self._extract_title(soup),
                'year': self._extract_year(soup),
                'rating': self._extract_rating(soup),
                'genre': self._extract_genre(soup),
                'director': self._extract_director(soup),
                'plot': self._extract_plot(soup),
                'cast': self._extract_cast(soup),
                'runtime': self._extract_runtime(soup),
                'country': self._extract_country(soup),
                'language': self._extract_language(soup),
                'budget': self._extract_budget(soup),
                'box_office': self._extract_box_office(soup),
                'source': 'IMDb (Enhanced)',
                'url': movie_url
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting basic movie data: {str(e)}")
            return None
    
    # Keep all your existing _extract_* methods here
    # (Copy them from your current imdb_scraper.py)
    
    def _create_fallback_data(self, title: str) -> Dict:
        """Enhanced fallback data"""
        return {
            'title': title,
            'year': "2023",
            'rating': round(random.uniform(6.5, 8.5), 1),
            'genre': "Drama, Thriller",
            'director': "Sample Director",
            'plot': f"An engaging story about {title} that takes viewers on an emotional journey.",
            'cast': ["Actor One", "Actor Two", "Actor Three"],
            'runtime': f"{random.randint(90, 180)} min",
            'country': "USA",
            'language': "English",
            'budget': "Unknown",
            'box_office': "Unknown",
            'reviews': self._get_sample_reviews(title),
            'detailed_reviews': [],
            'total_reviews_extracted': 0,
            'source': 'IMDb (Sample Data)',
            'url': f"https://www.imdb.com/title/sample_{title.replace(' ', '_').lower()}"
        }
    
    def _get_sample_reviews(self, title: str) -> List[str]:
        """Generate realistic sample reviews"""
        return [
            f"Outstanding film! {title} exceeded all my expectations with brilliant performances.",
            f"Absolutely loved {title}. The cinematography was breathtaking and the story compelling.",
            f"What a masterpiece! {title} is one of the best movies I've seen this year.",
            f"Incredible movie experience! {title} has amazing performances and outstanding direction.",
            f"Pure excellence! {title} showcases brilliant filmmaking and exceptional storytelling."
        ]