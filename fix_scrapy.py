#!/usr/bin/env python3
"""
Fix Scrapy installation and dependencies
"""
import subprocess
import sys
import os

def install_scrapy_dependencies():
    """Install Scrapy and related dependencies"""
    print("🔧 FIXING SCRAPY INSTALLATION")
    print("=" * 50)
    
    # List of required packages for Scrapy
    scrapy_packages = [
        "scrapy==2.11.0",
        "twisted",
        "crochet",
        "itemadapter",
        "itemloaders",
        "w3lib",
        "parsel",
        "queuelib",
        "service_identity",
        "cryptography",
        "pywin32; sys_platform == 'win32'",
        "pypiwin32; sys_platform == 'win32'"
    ]
    
    print("📦 Installing Scrapy dependencies...")
    
    for package in scrapy_packages:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"⚠️ {package} installation warning: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {package} installation timed out")
        except Exception as e:
            print(f"❌ {package} installation failed: {e}")
    
    print("\n🧪 Testing Scrapy imports...")
    
    # Test imports
    test_imports = [
        ("scrapy", "Scrapy core"),
        ("scrapy.crawler", "Scrapy crawler"),
        ("twisted.internet.reactor", "Twisted reactor"),
        ("crochet", "Crochet async"),
        ("scrapy.utils.project", "Scrapy utils")
    ]
    
    success_count = 0
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description}: OK")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description}: {e}")
    
    print(f"\n📊 Import Test Results: {success_count}/{len(test_imports)} successful")
    
    if success_count == len(test_imports):
        print("🎉 Scrapy is fully available!")
        return True
    else:
        print("⚠️ Some Scrapy components are missing")
        return False

def create_scrapy_fallback():
    """Create a simplified Scrapy service that works without full Scrapy"""
    print("\n🛠️ Creating Scrapy fallback implementation...")
    
    fallback_code = '''"""
Scrapy fallback implementation using requests and BeautifulSoup
"""
import asyncio
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import re
import json

class ScrapySearchService:
    """Simplified Scrapy service using requests + BeautifulSoup"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def search_movies(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for movies using web scraping fallback"""
        try:
            # Use IMDb search as fallback
            search_url = f"https://www.imdb.com/find/?q={query}&ref_=nv_sr_sm"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                # Parse IMDb search results
                for item in soup.find_all('td', class_='result_text')[:limit]:
                    title_link = item.find('a')
                    if title_link:
                        title = title_link.text
                        imdb_id = re.search(r'tt\\d+', title_link.get('href', ''))
                        year_match = re.search(r'\\((\\d{4})\\)', item.text)
                        
                        results.append({
                            'title': title,
                            'imdb_id': imdb_id.group() if imdb_id else None,
                            'year': int(year_match.group(1)) if year_match else None,
                            'source': 'scrapy_fallback'
                        })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Scrapy fallback search failed: {e}")
            return []
    
    async def get_movie_poster(self, title: str) -> Optional[str]:
        """Get movie poster using web scraping"""
        try:
            search_url = f"https://www.imdb.com/find/?q={title}"
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                poster_img = soup.find('img', class_='ipc-image')
                if poster_img:
                    return poster_img.get('src')
                    
        except Exception as e:
            self.logger.error(f"Poster scraping failed: {e}")
            
        return None
    
    async def get_movie_reviews(self, movie_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get movie reviews using web scraping"""
        try:
            reviews_url = f"https://www.imdb.com/title/{movie_id}/reviews"
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.session.get, reviews_url)
            
            reviews = []
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for review in soup.find_all('div', class_='review-container')[:limit]:
                    title_elem = review.find('a', class_='title')
                    content_elem = review.find('div', class_='text')
                    rating_elem = review.find('span', class_='rating-other-user-rating')
                    
                    if content_elem:
                        reviews.append({
                            'title': title_elem.text.strip() if title_elem else '',
                            'content': content_elem.text.strip(),
                            'rating': rating_elem.text.strip() if rating_elem else None,
                            'source': 'imdb_scrapy_fallback'
                        })
            
            return reviews
            
        except Exception as e:
            self.logger.error(f"Reviews scraping failed: {e}")
            return []
'''
    
    try:
        fallback_path = "backend/app/services/scrapy_search_service_fallback.py"
        with open(fallback_path, 'w') as f:
            f.write(fallback_code)
        print(f"✅ Scrapy fallback created at {fallback_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create fallback: {e}")
        return False

if __name__ == "__main__":
    print("🕷️ SCRAPY AVAILABILITY FIX")
    print("=" * 50)
    
    # Try to install Scrapy properly
    scrapy_success = install_scrapy_dependencies()
    
    if not scrapy_success:
        print("\\n⚠️ Full Scrapy installation failed, creating fallback...")
        fallback_success = create_scrapy_fallback()
        
        if fallback_success:
            print("\\n✅ Scrapy fallback is available")
        else:
            print("\\n❌ Could not create Scrapy fallback")
    
    print("\n🔍 Scrapy setup complete. Restart the server to apply changes.")
