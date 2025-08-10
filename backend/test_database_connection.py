#!/usr/bin/env python3
"""
Database Connection Tester and Fixer
Tests database connections and provides fixes for common issues.
"""

import os
import sys
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sqlite_connection():
    """Test SQLite database connection"""
    try:
        db_path = "movie_analysis.db"
        
        # Create database file if it doesn't exist
        if not Path(db_path).exists():
            print(f"📁 Creating SQLite database: {db_path}")
            
        # Test connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test_connection",))
        conn.commit()
        
        # Query test data
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        
        # Clean up
        cursor.execute("DROP TABLE test_table")
        conn.commit()
        conn.close()
        
        print(f"✅ SQLite connection successful! Database: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")
        return False

def create_basic_schema():
    """Create basic database schema for the application"""
    try:
        db_path = "movie_analysis.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                imdb_id TEXT UNIQUE,
                year INTEGER,
                director TEXT,
                genre TEXT,
                plot TEXT,
                poster_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER,
                source TEXT NOT NULL,
                rating REAL,
                review_text TEXT,
                author TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies (id)
            )
        ''')
        
        # Create analysis_cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_title TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(movie_title, analysis_type)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False

def main():
    """Main function to test and fix database connections"""
    print("🔍 CineScope Database Connection Tester")
    print("=" * 50)
    
    # Test SQLite connection
    print("\n📋 Testing SQLite Connection...")
    sqlite_ok = test_sqlite_connection()
    
    if sqlite_ok:
        print("\n📋 Creating Database Schema...")
        schema_ok = create_basic_schema()
        
        if schema_ok:
            print("\n✅ Database setup completed successfully!")
            print("🎯 Your application should now be able to connect to the database.")
        else:
            print("\n❌ Database schema creation failed.")
    else:
        print("\n❌ Database connection failed.")
        print("💡 Try running this script with administrator privileges.")
    
    print("\n" + "=" * 50)
    print("🏁 Database test completed.")

if __name__ == "__main__":
    main()
