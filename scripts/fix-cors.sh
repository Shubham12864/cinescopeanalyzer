#!/bin/bash
# Quick CORS Fix and Test Script

echo "🔧 Deploying CORS fix..."

# Commit and push changes
git add .
git commit -m "Fix CORS - allow all origins for Vercel"
git push origin main

echo "⏳ Waiting for Railway deployment (30 seconds)..."
sleep 30

echo "🧪 Testing backend health..."
curl -f https://cinescopeanalyzer-production.up.railway.app/api/health

echo "🧪 Testing movie search..."
curl -f "https://cinescopeanalyzer-production.up.railway.app/api/movies/search?q=batman"

echo "✅ CORS fix complete! Your frontend should work now."
