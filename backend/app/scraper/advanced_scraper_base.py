import random
import time
import logging
import os
from typing import List, Dict, Optional, Union, Any
from urllib.parse import urljoin, quote
import re

# Core web scraping
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# Advanced scraping tools
try:
    import selenium
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import (
        TimeoutException, 
        NoSuchElementException, 
        WebDriverException,
        ElementNotInteractableException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False

# Proxy configuration for faster and more reliable scraping
PROXY_LIST = [
    # Free proxy services (add more as needed)
    None,  # Direct connection first
    # Add your proxy servers here:
    # "http://proxy1:port",
    # "http://proxy2:port", 
    # "http://proxy3:port",
]

# Fast user agents for requests
FAST_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

class AdvancedScraperBase:
    """Advanced web scraping base class with fixed Chrome driver compatibility"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = self._load_config(config)
        self.setup_logging()
        self.user_agent_manager = self._setup_user_agent_manager()
        self.session = None
        self.driver = None
        self.cloudscraper_session = None
        self.setup_sessions()
        self.proxy_list = self._load_proxy_list()
        
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retries_used': 0,
            'proxy_switches': 0
        }
        
        self.logger.info("🚀 Advanced Scraper initialized successfully")
    
    def _load_config(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        default_config = {
            'request_delay_min': 2,
            'request_delay_max': 8,
            'max_retries': 3,
            'timeout': 20,
            'headless': True,
            'stealth_mode': True,
            'disable_images': True,
            'window_width': 1920,
            'window_height': 1080,
            'use_proxy': False,
            'proxy_file': 'config/proxies.txt',
            'log_level': 'INFO',
            'log_file': 'logs/scraping.log'
        }
        
        if ENV_AVAILABLE:
            env_overrides = {
                'use_proxy': os.getenv('USE_PROXY', 'false').lower() == 'true',
                'proxy_file': os.getenv('PROXY_FILE', default_config['proxy_file']),
                'request_delay_min': int(os.getenv('SCRAPING_DELAY_MIN', default_config['request_delay_min'])),
                'request_delay_max': int(os.getenv('SCRAPING_DELAY_MAX', default_config['request_delay_max'])),
                'max_retries': int(os.getenv('MAX_RETRIES', default_config['max_retries'])),
                'log_level': os.getenv('LOG_LEVEL', default_config['log_level'])
            }
            default_config.update(env_overrides)
        
        if config:
            default_config.update(config)
        
        return default_config
    
    def setup_logging(self):
        log_dir = os.path.dirname(self.config['log_file'])
        os.makedirs(log_dir, exist_ok=True)
        
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        try:
            file_handler = logging.FileHandler(self.config['log_file'], encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)
    
    def _setup_user_agent_manager(self):
        if FAKE_UA_AVAILABLE:
            try:
                return UserAgent()
            except Exception as e:
                self.logger.warning(f"FakeUserAgent failed: {e}")
        
        return {
            'agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        }
    
    def _load_proxy_list(self) -> List[str]:
        if not self.config['use_proxy']:
            return []
        
        proxy_file = self.config['proxy_file']
        if not os.path.exists(proxy_file):
            return []
        
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                proxies = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '://' in line:
                            proxies.append(line)
                        else:
                            proxies.append(f'http://{line}')
                return proxies
        except Exception as e:
            self.logger.error(f"Error loading proxy file: {e}")
            return []
    
    def setup_sessions(self):
        self._setup_requests_session()
        if CLOUDSCRAPER_AVAILABLE:
            self._setup_cloudscraper_session()
    
    def _setup_requests_session(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.config['max_retries'],
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.timeout = self.config['timeout']
    
    def _setup_cloudscraper_session(self):
        try:
            self.cloudscraper_session = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
        except Exception as e:
            self.logger.warning(f"CloudScraper setup failed: {e}")
            self.cloudscraper_session = None
    
    def get_random_user_agent(self) -> str:
        if FAKE_UA_AVAILABLE and hasattr(self.user_agent_manager, 'random'):
            try:
                return self.user_agent_manager.random
            except:
                pass
        
        if isinstance(self.user_agent_manager, dict):
            return random.choice(self.user_agent_manager['agents'])
        
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def get_random_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def smart_delay(self, multiplier: float = 1.0):
        base_delay = random.uniform(
            self.config['request_delay_min'],
            self.config['request_delay_max']
        )
        actual_delay = base_delay * multiplier
        
        if random.random() < 0.1:
            actual_delay *= random.uniform(2, 4)
        
        actual_delay = max(actual_delay, 0.5)
        time.sleep(actual_delay)
    
    def safe_request(self, url: str, method: str = 'GET', use_cloudscraper: bool = False, 
                    retry_count: int = 0, **kwargs) -> Optional[requests.Response]:
        
        self.stats['requests_made'] += 1
        if retry_count > 0:
            self.stats['retries_used'] += 1
        
        delay_multiplier = 1.0 + (retry_count * 0.5)
        self.smart_delay(delay_multiplier)
        
        session = self.cloudscraper_session if (use_cloudscraper and self.cloudscraper_session) else self.session
        
        request_kwargs = {
            'headers': self.get_random_headers(),
            'timeout': self.config['timeout'],
            'allow_redirects': True,
            **kwargs
        }
        
        try:
            response = session.request(method, url, **request_kwargs)
            
            if response.status_code == 200:
                self.stats['successful_requests'] += 1
                return response
            elif response.status_code in [403, 429, 503] and retry_count < self.config['max_retries']:
                backoff_delay = (2 ** retry_count) * random.uniform(1, 3)
                time.sleep(backoff_delay)
                use_cloudscraper = not use_cloudscraper and CLOUDSCRAPER_AVAILABLE
                return self.safe_request(url, method, use_cloudscraper, retry_count + 1, **kwargs)
            else:
                self.stats['failed_requests'] += 1
                return None
                
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            if retry_count < self.config['max_retries']:
                return self.safe_request(url, method, use_cloudscraper, retry_count + 1, **kwargs)
            self.stats['failed_requests'] += 1
            return None
    
    def setup_selenium_driver(self, headless: Optional[bool] = None) -> Optional[webdriver.Chrome]:
        """Setup Selenium WebDriver with FIXED Chrome options and auto-driver management"""
        if not SELENIUM_AVAILABLE:
            self.logger.error("❌ Selenium not available")
            return None
        
        headless = headless if headless is not None else self.config['headless']
        
        self.logger.info("🚗 Setting up Chrome WebDriver with auto-installation...")
        
        try:
            # Use compatible Chrome options
            options = Options()
            
            # Basic options (FIXED - using correct format)
            if headless:
                options.add_argument('--headless=new')
            
            # Standard Chrome arguments (these work with all Chrome versions)
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-extensions')
            
            # Window size
            options.add_argument(f'--window-size={self.config["window_width"]},{self.config["window_height"]}')
            
            # User agent
            user_agent = self.get_random_user_agent()
            options.add_argument(f'--user-agent={user_agent}')
            
            # Performance options
            if self.config['disable_images']:
                options.add_argument('--disable-images')
                # Use add_experimental_option instead of excludeSwitches
                prefs = {
                    "profile.managed_default_content_settings.images": 2,
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.default_content_settings.popups": 0
                }
                options.add_experimental_option("prefs", prefs)
            
            # FIXED: Use correct experimental options format
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # Additional stealth options
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-sync')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # Try different driver approaches in order of preference
            driver = None
            
            # 1. Try undetected-chromedriver first (most reliable)
            if UC_AVAILABLE:
                try:
                    self.logger.debug("🔄 Attempting undetected-chromedriver...")
                    driver = uc.Chrome(options=options, version_main=None)
                    self.logger.info("✅ Undetected Chrome driver initialized successfully")
                except Exception as e:
                    self.logger.warning(f"⚠️ Undetected Chrome failed: {e}")
                    driver = None
            
            # 2. Try with webdriver-manager for auto-installation
            if not driver:
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    from selenium.webdriver.chrome.service import Service
                    
                    self.logger.debug("🔄 Using webdriver-manager for auto-installation...")
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    self.logger.info("✅ Chrome driver with webdriver-manager initialized successfully")
                except ImportError:
                    self.logger.debug("webdriver-manager not available, trying standard approach")
                except Exception as e:
                    self.logger.warning(f"⚠️ webdriver-manager failed: {e}")
            
            # 3. Fallback to standard ChromeDriver
            if not driver:
                try:
                    self.logger.debug("🔄 Using standard ChromeDriver...")
                    driver = webdriver.Chrome(options=options)
                    self.logger.info("✅ Standard Chrome driver initialized successfully")
                except Exception as e:
                    self.logger.error(f"❌ Standard Chrome driver also failed: {e}")
                    
                    # 4. Last resort: try without any service
                    try:
                        self.logger.debug("🔄 Last resort: minimal Chrome setup...")
                        minimal_options = Options()
                        minimal_options.add_argument('--headless=new')
                        minimal_options.add_argument('--no-sandbox')
                        minimal_options.add_argument('--disable-dev-shm-usage')
                        driver = webdriver.Chrome(options=minimal_options)
                        self.logger.info("✅ Minimal Chrome driver initialized successfully")
                    except Exception as final_e:
                        self.logger.error(f"❌ All Chrome driver approaches failed: {final_e}")
                        return None
            
            if driver:
                # Apply anti-detection measures
                try:
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
                    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                except Exception as e:
                    self.logger.warning(f"⚠️ Anti-detection script failed: {e}")
                
                # Set timeouts
                try:
                    driver.set_page_load_timeout(self.config['timeout'])
                    driver.implicitly_wait(10)
                except Exception as e:
                    self.logger.warning(f"⚠️ Timeout setting failed: {e}")
                
                self.driver = driver
                return driver
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in Chrome driver setup: {str(e)}")
            return None
    
    def safe_selenium_request(self, url: str, wait_for_element: Optional[str] = None,
                             wait_timeout: Optional[int] = None) -> bool:
        if not self.driver:
            if not self.setup_selenium_driver():
                return False
        
        wait_timeout = wait_timeout or self.config['timeout']
        
        try:
            self.smart_delay(0.5)
            self.driver.get(url)
            
            if wait_for_element:
                wait = WebDriverWait(self.driver, wait_timeout)
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                except TimeoutException:
                    self.logger.warning(f"⚠️ Timeout waiting for element: {wait_for_element}")
            
            self.smart_delay(0.3)
            
            if "404" in self.driver.title.lower() or "not found" in self.driver.page_source.lower()[:1000]:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading {url}: {str(e)}")
            return False
    
    def extract_text_safe(self, soup: BeautifulSoup, selectors: List[str], 
                         default: str = "Not found") -> str:
        if soup is None:
            return default
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    if element:
                        text = element.get_text(strip=True)
                        if text and len(text.strip()) > 0:
                            return text.strip()
            except Exception:
                continue
        
        return default
    
    def extract_elements_safe(self, soup: BeautifulSoup, selectors: List[str]) -> List:
        if soup is None:
            return []
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    return elements
            except Exception:
                continue
        
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        success_rate = (
            (self.stats['successful_requests'] / self.stats['requests_made'] * 100)
            if self.stats['requests_made'] > 0 else 0
        )
        
        return {
            **self.stats,
            'success_rate': round(success_rate, 2)
        }
    
    def cleanup(self):
        try:
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.info("🚗 Chrome driver closed")
                except Exception as e:
                    self.logger.error(f"Error closing driver: {str(e)}")
                finally:
                    self.driver = None
            
            if self.session:
                try:
                    self.session.close()
                    self.logger.info("🌐 HTTP sessions closed")
                except Exception:
                    pass
                finally:
                    self.session = None
            
            if self.cloudscraper_session:
                try:
                    self.cloudscraper_session.close()
                except Exception:
                    pass
                finally:
                    self.cloudscraper_session = None
                    
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False