#!/bin/bash
"""
Azure Cache Deployment Script
Deploy enhanced backend with Azure Cosmos DB caching to Railway
"""

echo "🚀 Deploying Enhanced Azure Cache Backend to Railway..."

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Must be run from project root directory"
    exit 1
fi

echo "📦 Installing Azure Cosmos DB dependencies..."
cd backend
pip install azure-cosmos==4.5.1 azure-storage-blob==12.19.0 motor==3.3.2
echo "✅ Dependencies installed"

echo "🔧 Updating backend requirements..."
# The requirements.txt has already been updated

echo "🐳 Building and deploying to Railway..."
cd ..

# Check if Railway CLI is available
if command -v railway &> /dev/null; then
    echo "🚂 Using Railway CLI for deployment..."
    railway up
else
    echo "⚠️ Railway CLI not available. Using git deployment method..."
    
    # Commit changes for Railway auto-deployment
    git add .
    git commit -m "feat: Add Azure Cosmos DB caching system with enhanced performance

- Azure Cosmos DB cache service with memory fallback
- Enhanced image service with intelligent caching
- High-performance API routes with background caching
- Comprehensive performance monitoring
- Intelligent cache management and cleanup
- Frontend integration with cache-aware API client"
    
    # Push to Railway (assuming Railway is connected to git)
    echo "📤 Pushing to Railway deployment branch..."
    git push origin main
fi

echo "⏱️ Waiting for deployment to complete..."
sleep 30

echo "🏥 Testing deployed backend health..."
curl -s https://cinescopeanalyzer-production.up.railway.app/health

echo ""
echo "✅ Azure Cache Deployment Script Complete!"
echo "🔗 Backend URL: https://cinescopeanalyzer-production.up.railway.app"
echo "🆕 Enhanced API v2: https://cinescopeanalyzer-production.up.railway.app/api/v2"
echo "📊 Cache Stats: https://cinescopeanalyzer-production.up.railway.app/api/v2/cache/stats"
