@echo off
REM Enhanced CineScope Movie Analyzer - Installation and Setup Script
echo.
echo ============================================================
echo CineScope Movie Analyzer - Enhanced Edition Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Upgrading pip...
python -m pip install --upgrade pip

echo [4/6] Installing enhanced dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo [5/6] Setting up environment configuration...
if not exist .env (
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your API keys:
    echo - Reddit API credentials (reddit.com/prefs/apps)
    echo - TMDB API key (themoviedb.org/settings/api)
    echo.
) else (
    echo .env file already exists
)

echo [6/6] Creating necessary directories...
if not exist logs mkdir logs
if not exist scraped_data mkdir scraped_data
if not exist temp mkdir temp

echo.
echo ============================================================
echo Enhanced Setup Complete!
echo ============================================================
echo.
echo New Features Installed:
echo + Reddit Discussion Analysis
echo + Multi-platform Web Scraping (IMDB, RT, Metacritic, Letterboxd)
echo + Advanced Sentiment Analysis with NLP
echo + Cross-platform Rating Comparison
echo + Parallel Processing for 3-5x faster analysis
echo + Real-time Discussion Trending
echo + Comprehensive Movie Insights
echo.
echo Quick Start:
echo 1. Edit .env file with your API keys
echo 2. Run: python test_enhanced_analysis.py
echo 3. Or start server: python -m uvicorn app.main:app --reload
echo.
echo API Endpoints (when server is running):
echo - Comprehensive Analysis: POST /api/v1/movies/analyze/comprehensive
echo - Quick Analysis: POST /api/v1/movies/analyze/quick
echo - Batch Analysis: GET /api/v1/movies/analyze/batch
echo - Trending Discussions: GET /api/v1/movies/trending-discussions
echo - Platform Comparison: GET /api/v1/analytics/platform-comparison
echo.
echo Documentation: http://localhost:8000/docs
echo.
pause
