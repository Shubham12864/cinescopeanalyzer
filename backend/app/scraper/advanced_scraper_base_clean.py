import random
import time
import asyncio
import logging
import json
import os
from typing import List, Dict, Optional, Union, Any
from urllib.parse import urljoin, quote
import re

# Core web scraping
import requests
from bs4 import BeautifulSoup
import cloudscraper

# Selenium and browser automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc

# Anti-detection and stealth
from fake_useragent import UserAgent
try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

# Proxy and retry utilities
from retrying import retry

class AdvancedScraperBase:
    """
    Advanced base class for web scraping with comprehensive anti-detection features.
    
    Features:
    - Multiple request methods (requests, cloudscraper, selenium)
    - User agent rotation and proxy support
    - Smart delays and retry mechanisms
    - Anti-detection measures
    - Robust error handling and logging
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the advanced scraper with configuration"""
        # Configuration
        self.config = config or {}
        
        # Setup logging
        self.setup_logging()
        
        # Browser and session management
        self.driver = None
        self.session = None
        self.cloudscraper_session = None
        
        # Anti-detection setup
        self.user_agent = UserAgent()
        self.current_user_agent = self.user_agent.random
        
        # Proxy configuration
        self.proxies = []
        self.current_proxy = None
        self.load_proxy_list()
        
        # Request statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = self.config.get('min_delay', 1.0)
        self.max_delay = self.config.get('max_delay', 3.0)
        
        self.logger.info("🚀 AdvancedScraperBase initialized successfully")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)
            
            # File handler
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(
                os.path.join(log_dir, 'scraping.log'),
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)
            
            self.logger.setLevel(logging.DEBUG)
    
    def load_proxy_list(self):
        """Load proxy list from configuration"""
        try:
            proxy_file = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'proxies.txt'
            )
            
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r', encoding='utf-8') as f:
                    self.proxies = [
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    ]
                
                self.logger.info(f"📡 Loaded {len(self.proxies)} proxies")
            else:
                self.logger.info("📡 No proxy file found, using direct connection")
                
        except Exception as e:
            self.logger.error(f"❌ Error loading proxies: {str(e)}")
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        
        proxy_string = random.choice(self.proxies)
        
        # Parse proxy string (format: ip:port or ip:port:username:password)
        parts = proxy_string.split(':')
        
        if len(parts) >= 2:
            proxy_dict = {
                'http': f'http://{proxy_string}',
                'https': f'https://{proxy_string}'
            }
            return proxy_dict
        
        return None
    
    def rotate_user_agent(self):
        """Rotate to a new user agent"""
        self.current_user_agent = self.user_agent.random
        self.logger.debug(f"🔄 Rotated user agent: {self.current_user_agent[:50]}...")
    
    def smart_delay(self, base_delay: float = None):
        """Implement smart delay with jitter"""
        if base_delay is None:
            delay = random.uniform(self.min_delay, self.max_delay)
        else:
            # Add jitter (±20%)
            jitter = base_delay * 0.2
            delay = base_delay + random.uniform(-jitter, jitter)
        
        # Ensure minimum delay between requests
        time_since_last = time.time() - self.last_request_time
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            self.logger.debug(f"⏱️ Smart delay: {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_headers(self, extra_headers: Optional[Dict] = None) -> Dict:
        """Get headers with anti-detection measures"""
        headers = {
            'User-Agent': self.current_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        if extra_headers:
            headers.update(extra_headers)
        
        return headers
    
    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def safe_request(self, url: str, method: str = 'GET', use_cloudscraper: bool = False, 
                    use_proxy: bool = False, extra_headers: Optional[Dict] = None,
                    **kwargs) -> requests.Response:
        """
        Make a safe HTTP request with retry mechanism and anti-detection
        """
        self.request_count += 1
        self.smart_delay()
        
        # Prepare request parameters
        headers = self.get_headers(extra_headers)
        proxies = self.get_random_proxy() if use_proxy else None
        
        try:
            if use_cloudscraper:
                # Use cloudscraper for sites with Cloudflare protection
                if not self.cloudscraper_session:
                    self.cloudscraper_session = cloudscraper.create_scraper(
                        browser='chrome',
                        delay=1
                    )
                
                response = self.cloudscraper_session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    timeout=30,
                    **kwargs
                )
            else:
                # Use regular requests session
                if not self.session:
                    self.session = requests.Session()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    proxies=proxies,
                    timeout=30,
                    **kwargs
                )
            
            response.raise_for_status()
            self.success_count += 1
            
            self.logger.debug(f"✅ Request successful: {url} (Status: {response.status_code})")
            return response
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ Request failed: {url} - {str(e)}")
            
            # Rotate user agent on error
            self.rotate_user_agent()
            raise
    
    def setup_selenium_driver(self, headless: bool = True, use_stealth: bool = True):
        """Setup Selenium WebDriver with anti-detection measures"""
        try:
            if self.driver:
                return True
            
            # Chrome options
            options = Options()
            
            if headless:
                options.add_argument('--headless=new')
            
            # Anti-detection arguments
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins-discovery')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')
            
            # Set user agent
            options.add_argument(f'--user-agent={self.current_user_agent}')
            
            # Window size
            options.add_argument('--window-size=1920,1080')
            
            # Try undetected chromedriver first
            try:
                self.driver = uc.Chrome(options=options, version_main=None)
                self.logger.info("✅ Undetected ChromeDriver initialized")
            except Exception as chrome_error:
                self.logger.warning(f"Undetected Chrome failed: {chrome_error}")
                
                # Fallback to regular Chrome
                try:
                    from selenium.webdriver import Chrome
                    from selenium.webdriver.chrome.service import Service
                    from webdriver_manager.chrome import ChromeDriverManager
                    
                    service = Service(ChromeDriverManager().install())
                    self.driver = Chrome(service=service, options=options)
                    self.logger.info("✅ Regular ChromeDriver initialized")
                except Exception as fallback_error:
                    self.logger.error(f"All Chrome driver options failed: {fallback_error}")
                    return False
            
            # Apply stealth if available
            if use_stealth and STEALTH_AVAILABLE and self.driver:
                try:
                    stealth(self.driver,
                           languages=["en-US", "en"],
                           vendor="Google Inc.",
                           platform="Win32",
                           webgl_vendor="Intel Inc.",
                           renderer="Intel Iris OpenGL Engine",
                           fix_hairline=True)
                    self.logger.info("🥷 Stealth mode applied")
                except Exception as stealth_error:
                    self.logger.warning(f"Stealth mode failed: {stealth_error}")
            
            # Additional anti-detection
            if self.driver:
                try:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except Exception:
                    pass  # Ignore if script execution fails
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup Selenium driver: {str(e)}")
            return False
    
    def safe_selenium_request(self, url: str, wait_for_element: Optional[str] = None,
                            timeout: int = 10) -> bool:
        """Make a safe Selenium request with wait conditions"""
        try:
            if not self.driver:
                if not self.setup_selenium_driver():
                    return False
            
            self.smart_delay()
            
            self.logger.debug(f"🌐 Selenium navigating to: {url}")
            self.driver.get(url)
            
            # Wait for specific element if provided
            if wait_for_element:
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                self.logger.debug(f"✅ Element found: {wait_for_element}")
            
            self.success_count += 1
            return True
            
        except TimeoutException:
            self.logger.error(f"⏰ Timeout waiting for element: {wait_for_element}")
            return False
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"❌ Selenium request failed: {url} - {str(e)}")
            return False
    
    def extract_text_safe(self, soup: BeautifulSoup, selectors: List[str], 
                         default: str = "Not found") -> str:
        """Safely extract text using multiple selectors"""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return default
    
    def extract_attribute_safe(self, soup: BeautifulSoup, selectors: List[str], 
                              attribute: str, default: str = "Not found") -> str:
        """Safely extract attribute using multiple selectors"""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element and element.has_attr(attribute):
                    return element[attribute]
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return default
    
    def parse_number_safe(self, text: str, default: float = 0.0) -> float:
        """Safely parse number from text"""
        try:
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.-]', '', text)
            return float(cleaned) if cleaned else default
        except (ValueError, TypeError):
            return default
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,!?()-]', '', cleaned)
        
        return cleaned.strip()
    
    def wait_for_element(self, selector: str, timeout: int = 10, 
                        condition: str = 'presence') -> bool:
        """Wait for element with different conditions"""
        if not self.driver:
            return False
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            if condition == 'presence':
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif condition == 'visible':
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            elif condition == 'clickable':
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            
            return True
            
        except TimeoutException:
            self.logger.debug(f"⏰ Timeout waiting for {condition} of: {selector}")
            return False
    
    def scroll_to_element(self, selector: str) -> bool:
        """Scroll to element smoothly"""
        try:
            if not self.driver:
                return False
            
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                element
            )
            time.sleep(1)  # Wait for scroll animation
            return True
            
        except Exception as e:
            self.logger.debug(f"❌ Failed to scroll to element: {e}")
            return False
    
    def get_page_source_safe(self) -> Optional[str]:
        """Safely get page source"""
        try:
            if self.driver:
                return self.driver.page_source
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get page source: {e}")
            return None
    
    def close_driver(self):
        """Safely close the Selenium driver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.logger.info("🚪 Selenium driver closed")
        except Exception as e:
            self.logger.error(f"❌ Error closing driver: {e}")
    
    def close_sessions(self):
        """Close all active sessions"""
        try:
            if self.session:
                self.session.close()
                self.session = None
            
            if self.cloudscraper_session:
                self.cloudscraper_session.close()
                self.cloudscraper_session = None
            
            self.logger.info("🚪 HTTP sessions closed")
        except Exception as e:
            self.logger.error(f"❌ Error closing sessions: {e}")
    
    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            'total_requests': self.request_count,
            'successful_requests': self.success_count,
            'failed_requests': self.error_count,
            'success_rate': (self.success_count / max(self.request_count, 1)) * 100,
            'current_user_agent': self.current_user_agent,
            'proxies_loaded': len(self.proxies)
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.close_driver()
        self.close_sessions()
        
        # Log final statistics
        stats = self.get_stats()
        self.logger.info(f"📊 Final stats: {stats}")
    
    def __del__(self):
        """Destructor - ensure cleanup"""
        try:
            self.close_driver()
            self.close_sessions()
        except:
            pass  # Ignore errors during destruction
    
    def click_element_safe(self, selector: str, timeout: int = 10) -> bool:
        """Safely click an element"""
        try:
            if not self.driver:
                return False
            
            if self.wait_for_element(selector, timeout, 'clickable'):
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.click()
                self.logger.debug(f"✅ Clicked element: {selector}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to click element {selector}: {e}")
            return False

    def type_text_safe(self, selector: str, text: str, timeout: int = 10) -> bool:
        """Safely type text into an element"""
        try:
            if not self.driver:
                return False
            
            if self.wait_for_element(selector, timeout, 'visible'):
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.clear()
                element.send_keys(text)
                self.logger.debug(f"✅ Typed text into: {selector}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to type text into {selector}: {e}")
            return False

    def get_current_url(self) -> Optional[str]:
        """Get current URL safely"""
        try:
            if self.driver:
                return self.driver.current_url
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get current URL: {e}")
            return None

    def take_screenshot(self, filename: str = None) -> bool:
        """Take a screenshot for debugging"""
        try:
            if not self.driver:
                return False
            
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            
            filepath = os.path.join(screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.info(f"📸 Screenshot saved: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to take screenshot: {e}")
            return False
