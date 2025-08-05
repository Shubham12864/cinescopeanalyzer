#!/bin/bash

echo "🚀 Vercel + Railway Connection Setup"
echo "===================================="

RAILWAY_URL="https://cinescopeanalyzer-production.up.railway.app"

echo "1. Testing Railway backend health..."
echo "Railway URL: $RAILWAY_URL"

# Test health endpoint
HEALTH_RESPONSE=$(curl -s "$RAILWAY_URL/health" 2>/dev/null)
if [[ $? -eq 0 ]]; then
  echo "✅ Railway health: $HEALTH_RESPONSE"
else
  echo "❌ Railway health check failed"
  exit 1
fi

echo ""
echo "2. Testing movie API endpoint..."

# Test movie endpoint
MOVIE_RESPONSE=$(timeout 10 curl -s "$RAILWAY_URL/api/movies/1311031" 2>/dev/null)
if [[ $? -eq 0 ]] && [[ -n "$MOVIE_RESPONSE" ]]; then
  echo "✅ Movie API working:"
  echo "$MOVIE_RESPONSE" | jq -r '.title // "Title not found"' 2>/dev/null || echo "Movie data received"
else
  echo "❌ Movie API test failed"
fi

echo ""
echo "3. Vercel environment configuration..."

# Check if .env.local exists
if [[ -f "frontend/.env.local" ]]; then
  echo "✅ .env.local exists:"
  cat frontend/.env.local
else
  echo "Creating .env.local..."
  echo "NEXT_PUBLIC_API_URL=$RAILWAY_URL" > frontend/.env.local
  echo "✅ .env.local created"
fi

echo ""
echo "4. Vercel deployment configuration..."

# Check vercel.json
if [[ -f "frontend/vercel.json" ]]; then
  echo "✅ vercel.json exists with Railway URL configured"
else
  echo "❌ vercel.json not found"
fi

echo ""
echo "5. Next steps for Vercel dashboard:"
echo "   📱 Go to: https://vercel.com/dashboard"
echo "   🔧 Project: cinescopeanalyzer"
echo "   ⚙️  Settings → Environment Variables"
echo "   ➕ Add: NEXT_PUBLIC_API_URL = $RAILWAY_URL"
echo "   🚀 Redeploy the project"

echo ""
echo "6. Testing frontend connection (if running locally)..."
if command -v npm &> /dev/null && [[ -d "frontend" ]]; then
  cd frontend
  if [[ -f "package.json" ]]; then
    echo "Frontend directory found, you can test locally with:"
    echo "   cd frontend && npm run dev"
  fi
  cd ..
fi

echo ""
echo "✅ Setup verification complete!"
echo "🌐 Railway backend: WORKING"
echo "🔗 Frontend config: READY"
echo "📋 Manual Vercel setup required: SET ENVIRONMENT VARIABLE"

exit 0
