import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any
from itemadapter import ItemAdapter
import os

class MovieDataValidationPipeline:
    """Validate scraped movie data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Validate required fields
        required_fields = ['source', 'data_type', 'scraped_at']
        for field in required_fields:
            if field not in adapter or not adapter[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate data types
        if adapter.get('scraped_at'):
            try:
                datetime.fromisoformat(adapter['scraped_at'].replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(f"Invalid date format: {adapter['scraped_at']}")
        
        return item

class MovieDataCleaningPipeline:
    """Clean and normalize scraped movie data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean text fields
        text_fields = ['title', 'plot', 'review_text', 'description']
        for field in text_fields:
            if adapter.get(field):
                # Remove extra whitespace
                cleaned_text = ' '.join(adapter[field].split())
                # Remove common artifacts
                cleaned_text = cleaned_text.replace('See full summary »', '')
                cleaned_text = cleaned_text.replace('See more »', '')
                adapter[field] = cleaned_text.strip()
        
        # Normalize ratings
        if adapter.get('rating'):
            try:
                rating = float(adapter['rating'])
                adapter['rating'] = round(rating, 1)
            except (ValueError, TypeError):
                adapter['rating'] = None
        
        # Clean lists
        list_fields = ['genre', 'cast', 'directors', 'writers']
        for field in list_fields:
            if adapter.get(field) and isinstance(adapter[field], list):
                cleaned_list = [item.strip() for item in adapter[field] if item and item.strip()]
                adapter[field] = cleaned_list[:20]  # Limit to 20 items
        
        return item

class MovieDataStoragePipeline:
    """Store scraped data in JSON files and database"""
    
    def __init__(self):
        self.files = {}
        self.items_count = {}
        
    def open_spider(self, spider):
        """Create storage files for the spider"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        os.makedirs('scraped_data', exist_ok=True)
        
        # Create JSON file for this spider run
        filename = f"scraped_data/{spider.name}_{timestamp}.json"
        self.files[spider.name] = open(filename, 'w', encoding='utf-8')
        self.items_count[spider.name] = 0
        
        # Write JSON array start
        self.files[spider.name].write('[\n')
        
        spider.logger.info(f"Opened storage file: {filename}")
    
    def close_spider(self, spider):
        """Close storage files"""
        if spider.name in self.files:
            # Close JSON array
            self.files[spider.name].write('\n]')
            self.files[spider.name].close()
            
            spider.logger.info(f"Stored {self.items_count[spider.name]} items for spider {spider.name}")
    
    def process_item(self, item, spider):
        """Store individual item"""
        adapter = ItemAdapter(item)
        
        # Add separator for JSON array
        if self.items_count[spider.name] > 0:
            self.files[spider.name].write(',\n')
        
        # Write item to JSON file
        json.dump(dict(adapter), self.files[spider.name], ensure_ascii=False, indent=2)
        self.items_count[spider.name] += 1
        
        # Also store in database if needed
        self._store_in_database(adapter, spider)
        
        return item
    
    def _store_in_database(self, adapter: ItemAdapter, spider):
        """Store item in SQLite database for quick access"""
        try:
            # Ensure directory exists
            os.makedirs('scraped_data', exist_ok=True)
            
            # Create/connect to database
            db_path = 'scraped_data/movie_data.db'
            conn = sqlite3.connect(db_path, timeout=30.0)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_movie_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    movie_title TEXT,
                    imdb_id TEXT,
                    scraped_at TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert data
            cursor.execute('''
                INSERT INTO scraped_movie_data 
                (source, data_type, movie_title, imdb_id, scraped_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                adapter.get('source'),
                adapter.get('data_type'),
                adapter.get('title') or adapter.get('movie_title'),
                adapter.get('imdb_id'),
                adapter.get('scraped_at'),
                json.dumps(dict(adapter), ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            spider.logger.error(f"Database storage failed: {e}")
        except Exception as e:
            spider.logger.error(f"Unexpected error in database storage: {e}")

class DuplicateFilterPipeline:
    """Filter out duplicate items"""
    
    def __init__(self):
        self.seen_items = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Create unique identifier for the item
        identifier_parts = [
            adapter.get('source', ''),
            adapter.get('data_type', ''),
            adapter.get('title', ''),
            adapter.get('imdb_id', ''),
            adapter.get('reviewer_name', ''),
            adapter.get('review_text', '')[:100] if adapter.get('review_text') else ''
        ]
        
        identifier = '|'.join(str(part) for part in identifier_parts)
        identifier_hash = hash(identifier)
        
        if identifier_hash in self.seen_items:
            spider.logger.debug(f"Duplicate item filtered: {adapter.get('source')} - {adapter.get('title')}")
            return None
        
        self.seen_items.add(identifier_hash)
        return item

class StatisticsPipeline:
    """Collect statistics about scraped data"""
    
    def __init__(self):
        self.stats = {
            'items_by_source': {},
            'items_by_type': {},
            'total_items': 0,
            'start_time': None,
            'end_time': None
        }
    
    def open_spider(self, spider):
        self.stats['start_time'] = datetime.now()
        spider.logger.info("Statistics collection started")
    
    def close_spider(self, spider):
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # Log statistics
        spider.logger.info(f"Scraping completed in {duration:.2f} seconds")
        spider.logger.info(f"Total items scraped: {self.stats['total_items']}")
        spider.logger.info(f"Items by source: {self.stats['items_by_source']}")
        spider.logger.info(f"Items by type: {self.stats['items_by_type']}")
        
        # Save statistics to file
        stats_file = f"scraped_data/stats_{spider.name}_{self.stats['start_time'].strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            stats_data = {
                **self.stats,
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': self.stats['end_time'].isoformat(),
                'duration_seconds': duration,
                'items_per_second': self.stats['total_items'] / duration if duration > 0 else 0
            }
            json.dump(stats_data, f, indent=2, ensure_ascii=False)
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Update statistics
        self.stats['total_items'] += 1
        
        source = adapter.get('source', 'unknown')
        if source not in self.stats['items_by_source']:
            self.stats['items_by_source'][source] = 0
        self.stats['items_by_source'][source] += 1
        
        data_type = adapter.get('data_type', 'unknown')
        if data_type not in self.stats['items_by_type']:
            self.stats['items_by_type'][data_type] = 0
        self.stats['items_by_type'][data_type] += 1
        
        return item
