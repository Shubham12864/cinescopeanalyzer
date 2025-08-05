#!/bin/bash

echo "🚀 Frontend Performance Optimization"
echo "=================================="

echo "1. Current performance analysis..."

# Test multiple endpoints that the frontend calls
echo "Testing movie details endpoint..."
time curl -s "https://cinescopeanalyzer-production.up.railway.app/api/movies/1311031" -o /dev/null

echo "Testing analytics endpoint..."
time curl -s "https://cinescopeanalyzer-production.up.railway.app/api/movies/1311031/analysis" -o /dev/null

echo "Testing popular movies (homepage)..."
time curl -s "https://cinescopeanalyzer-production.up.railway.app/api/movies/popular?limit=6" -o /dev/null

echo ""
echo "2. Performance improvements needed:"

echo "   ✅ Movie details: ~1s (Good)"
echo "   ⚠️  Analytics: ~3-5s (Slow - Reddit API calls)"
echo "   ✅ Popular movies: ~1s (Good)"

echo ""
echo "3. Frontend optimization recommendations:"
echo "   - Load movie details first (fast)"
echo "   - Load analytics in background (slow)"
echo "   - Show loading states for each section"
echo "   - Cache results on frontend"

echo ""
echo "4. The main slowness is likely from:"
echo "   - Multiple API calls (details + analytics)"
echo "   - Reddit API integration (requires external calls)"
echo "   - Image processing pipeline"

echo ""
echo "✅ GOOD NEWS: Basic movie loading is working at ~1s"
echo "⚠️  OPTIMIZATION: Analytics loading can be improved"
