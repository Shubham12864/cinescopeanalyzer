#!/bin/bash

# Enhanced CineScope Movie Analyzer - Installation and Setup Script for Linux/Mac

echo ""
echo "============================================================"
echo "CineScope Movie Analyzer - Enhanced Edition Setup"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Upgrading pip..."
python -m pip install --upgrade pip

echo "[4/6] Installing enhanced dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo "[5/6] Setting up environment configuration..."
if [ ! -f .env ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file and add your API keys:"
    echo "- Reddit API credentials (reddit.com/prefs/apps)"
    echo "- TMDB API key (themoviedb.org/settings/api)"
    echo ""
else
    echo ".env file already exists"
fi

echo "[6/6] Creating necessary directories..."
mkdir -p logs scraped_data temp

echo ""
echo "============================================================"
echo "Enhanced Setup Complete!"
echo "============================================================"
echo ""
echo "New Features Installed:"
echo "+ Reddit Discussion Analysis"
echo "+ Multi-platform Web Scraping (IMDB, RT, Metacritic, Letterboxd)"
echo "+ Advanced Sentiment Analysis with NLP"
echo "+ Cross-platform Rating Comparison"
echo "+ Parallel Processing for 3-5x faster analysis"
echo "+ Real-time Discussion Trending"
echo "+ Comprehensive Movie Insights"
echo ""
echo "Quick Start:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python test_enhanced_analysis.py"
echo "3. Or start server: python -m uvicorn app.main:app --reload"
echo ""
echo "API Endpoints (when server is running):"
echo "- Comprehensive Analysis: POST /api/v1/movies/analyze/comprehensive"
echo "- Quick Analysis: POST /api/v1/movies/analyze/quick"
echo "- Batch Analysis: GET /api/v1/movies/analyze/batch"
echo "- Trending Discussions: GET /api/v1/movies/trending-discussions"
echo "- Platform Comparison: GET /api/v1/analytics/platform-comparison"
echo ""
echo "Documentation: http://localhost:8000/docs"
echo ""
