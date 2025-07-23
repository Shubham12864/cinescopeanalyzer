#!/usr/bin/env python3
"""
CineScopeAnalyzer Enhanced Startup Script
Handles dependency checks, environment setup, and graceful startup
"""

import os
import sys
import subprocess
import logging
import asyncio
from typing import List, Dict, Any

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    logger = logging.getLogger(__name__)
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required. Current version: %s", sys.version)
        return False
    logger.info("✅ Python version compatible: %s", sys.version.split()[0])
    return True

def install_missing_packages(required_packages: List[str]):
    """Install missing packages"""
    logger = logging.getLogger(__name__)
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.split('==')[0].replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.info("📦 Installing missing packages: %s", missing_packages)
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                '--upgrade', '--no-warn-script-location'
            ] + missing_packages)
            logger.info("✅ Successfully installed missing packages")
            return True
        except subprocess.CalledProcessError as e:
            logger.error("❌ Failed to install packages: %s", e)
            return False
    
    logger.info("✅ All required packages are installed")
    return True

def check_environment_variables():
    """Check and create environment file if needed"""
    logger = logging.getLogger(__name__)
    
    env_file = '.env'
    env_template = '.env.template'
    
    # Check if .env exists
    if not os.path.exists(env_file):
        if os.path.exists(env_template):
            logger.info("📋 Creating .env from template...")
            try:
                with open(env_template, 'r') as template:
                    content = template.read()
                with open(env_file, 'w') as env:
                    env.write(content)
                logger.info("✅ Created .env file from template")
            except Exception as e:
                logger.error("❌ Failed to create .env file: %s", e)
                return False
        else:
            logger.warning("⚠️ No .env or .env.template found - creating minimal .env")
            minimal_env = '''# Minimal CineScopeAnalyzer Configuration
DATABASE_TYPE=local
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=cinescope
ENVIRONMENT=development
DEBUG=true
CACHE_TTL=3600
SCRAPING_ENABLED=true
'''
            try:
                with open(env_file, 'w') as f:
                    f.write(minimal_env)
                logger.info("✅ Created minimal .env file")
            except Exception as e:
                logger.error("❌ Failed to create minimal .env: %s", e)
                return False
    
    # Load and validate critical environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    critical_vars = ['DATABASE_TYPE', 'MONGODB_DB_NAME']
    missing_vars = [var for var in critical_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning("⚠️ Missing environment variables: %s", missing_vars)
        logger.info("💡 Consider setting these in your .env file for full functionality")
    
    return True

def check_directories():
    """Create necessary directories"""
    logger = logging.getLogger(__name__)
    
    directories = [
        'cache',
        'cache/images', 
        'logs',
        'data'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug("📁 Directory ensured: %s", directory)
        except Exception as e:
            logger.error("❌ Failed to create directory %s: %s", directory, e)
            return False
    
    logger.info("✅ All directories verified")
    return True

def test_database_connection():
    """Test database connectivity"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import here to avoid circular imports
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.core.azure_database import AzureDatabaseManager
        
        async def test_db():
            db_manager = AzureDatabaseManager()
            try:
                await db_manager.connect()
                logger.info("✅ Database connection successful")
                return True
            except Exception as e:
                logger.warning("⚠️ Database connection failed, will use fallback: %s", e)
                return False
        
        # Run the async test
        return asyncio.run(test_db())
        
    except Exception as e:
        logger.warning("⚠️ Database test failed, will use fallback: %s", e)
        return False

def start_application():
    """Start the FastAPI application"""
    logger = logging.getLogger(__name__)
    
    try:
        import uvicorn
        from app.main import app
        
        logger.info("🚀 Starting CineScopeAnalyzer Backend Server...")
        logger.info("📡 Server will be available at: http://localhost:8000")
        logger.info("📚 API Documentation: http://localhost:8000/docs")
        logger.info("🔄 Auto-reload enabled for development")
        
        # Start uvicorn server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error("❌ Failed to start server: %s", e)
        sys.exit(1)

def main():
    """Main startup routine"""
    logger = setup_logging()
    
    logger.info("🎬 CineScopeAnalyzer Enhanced Startup")
    logger.info("=" * 50)
    
    # Critical packages for basic functionality
    basic_packages = [
        'fastapi',
        'uvicorn',
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        'motor',
        'pymongo'
    ]
    
    # Optional packages for enhanced features
    optional_packages = [
        'selenium',
        'undetected-chromedriver',
        'webdriver-manager',
        'fake-useragent',
        'cloudscraper'
    ]
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install basic packages
    if not install_missing_packages(basic_packages):
        logger.error("❌ Failed to install basic packages")
        sys.exit(1)
    
    # Step 3: Try to install optional packages (don't fail if these don't work)
    logger.info("📦 Installing optional enhancement packages...")
    install_missing_packages(optional_packages)
    
    # Step 4: Setup environment
    if not check_environment_variables():
        logger.error("❌ Environment setup failed")
        sys.exit(1)
    
    # Step 5: Create directories
    if not check_directories():
        logger.error("❌ Directory setup failed")
        sys.exit(1)
    
    # Step 6: Test database (non-blocking)
    logger.info("🔍 Testing database connection...")
    test_database_connection()
    
    # Step 7: Start application
    logger.info("✅ All checks complete - starting application")
    start_application()

if __name__ == "__main__":
    main()
