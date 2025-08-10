#!/usr/bin/env python3
"""
Test script to verify all scraping functionality works
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)

def test_scrapy_imports():
    """Test Scrapy imports"""
    try:
        from app.services.scrapy_search_service import ScrapySearchService
        print("✅ Scrapy Search Service: Available")
        return True
    except ImportError as e:
        print(f"❌ Scrapy Search Service: {e}")
        return False

def test_selenium_imports():
    """Test Selenium imports"""
    try:
        from selenium import webdriver
        print("✅ Selenium WebDriver: Available")
        return True
    except ImportError as e:
        print(f"❌ Selenium WebDriver: {e}")
        return False

def test_scraper_imports():
    """Test Web Scrapers"""
    try:
        from app.scraper.imdb_scraper import ImdbScraper
        from app.scraper.rotten_tomatoes_scraper import RottenTomatoesScraper
        from app.scraper.metacritic_scraper import MetacriticScraper
        print("✅ Web Scrapers: Available")
        return True
    except ImportError as e:
        print(f"❌ Web Scrapers: {e}")
        return False

def test_api_manager():
    """Test API Manager"""
    try:
        from app.core.api_manager import APIManager
        print("✅ API Manager: Available")
        return True
    except ImportError as e:
        print(f"❌ API Manager: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing CineScope Scraping Functionality...")
    print("=" * 50)
    
    tests = [
        test_api_manager,
        test_scrapy_imports,
        test_selenium_imports,
        test_scraper_imports
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        sys.exit(0)
    else:
        print(f"⚠️ Some tests failed. ({passed}/{total} passed)")
        print("💡 Install missing dependencies or check import paths")
        sys.exit(1)

if __name__ == "__main__":
    main()
