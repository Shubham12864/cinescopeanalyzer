# 🚀 How to Run CineScope Analyzer

## Prerequisites

### System Requirements
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **Git** (for version control)
- **Chrome Browser** (for web scraping features)

### Check Your Versions
```bash
python --version    # Should be 3.11+
node --version      # Should be 18+
npm --version       # Should be 9+
git --version       # Any recent version
```

## 🏃‍♂️ Quick Start (Recommended)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd CineScopeAnalyzer

# Make setup script executable (Linux/Mac)
chmod +x setup.sh
```

### 2. Automated Setup
```bash
# Run the automated setup script
./setup.sh

# Or manually follow the steps below
```

## 🔧 Manual Setup

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings
# Add your API keys if you have them (optional for basic functionality)
```

5. **Test backend installation**
```bash
python -c "from app.main import app; print('✅ Backend setup successful!')"
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend  # From backend directory
# or
cd frontend     # From root directory
```

2. **Install dependencies**
```bash
npm install
# or if you prefer yarn:
yarn install
```

3. **Set up environment variables**
```bash
# Copy environment template
cp .env.template .env.local

# The default settings should work for local development
```

4. **Test frontend installation**
```bash
npm run build
```

## 🚀 Running the Application

### Option 1: Run Both Services Simultaneously (Recommended)

From the frontend directory:
```bash
npm run dev:full
```

This command will:
- Start the backend server on `http://localhost:8000`
- Start the frontend server on `http://localhost:3000`
- Both services will auto-reload on changes

### Option 2: Run Services Separately

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 3: Using Docker (Production-like)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

## 🌐 Access Your Application

Once running, you can access:

- **Frontend (Main App)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing Your Setup

### Quick Health Check
```bash
# Test backend health
curl http://localhost:8000/health

# Test API endpoint
curl http://localhost:8000/api/movies/suggestions?limit=3
```

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Backend Issues

**1. Import Errors**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Port Already in Use**
```bash
# Kill process on port 8000
# Linux/Mac:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**3. Database Issues**
```bash
# Clear cache and restart
rm -rf backend/cache/*
rm -rf backend/logs/*
```

#### Frontend Issues

**1. Node Modules Issues**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**2. Build Errors**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

**3. CORS Errors**
- Make sure backend is running on port 8000
- Check that `NEXT_PUBLIC_API_URL` is set correctly in `.env.local`

### Environment Variables

**Backend (.env):**
```bash
# Optional - for enhanced features
OMDB_API_KEY=your_omdb_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Database (optional - uses SQLite by default)
DATABASE_URL=sqlite:///./cache/cache.db
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=CineScope Analyzer
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 🚀 Production Deployment

### Deploy to Railway (Backend)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway deploy
```

### Deploy to Vercel (Frontend)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

## 📊 Features Available

### Basic Features (No API Keys Required)
- ✅ Movie search and display
- ✅ Basic movie information
- ✅ Movie suggestions
- ✅ Responsive UI
- ✅ Movie details and reviews

### Enhanced Features (With API Keys)
- 🔑 Real-time movie data from OMDB
- 🔑 Reddit discussion analysis
- 🔑 Advanced web scraping
- 🔑 Sentiment analysis
- 🔑 Comprehensive movie analytics

## 🆘 Getting Help

### Check Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (in browser console)
# Open Developer Tools → Console
```

### Common Commands
```bash
# Restart everything
pkill -f uvicorn  # Kill backend
pkill -f next     # Kill frontend
npm run dev:full  # Restart both

# Reset database
rm -rf backend/cache/cache.db
rm -rf backend/scraped_data/

# Clear all caches
rm -rf backend/cache/*
rm -rf backend/logs/*
rm -rf frontend/.next/
```

### Still Having Issues?

1. **Check the logs** in `backend/logs/` directory
2. **Verify all dependencies** are installed correctly
3. **Ensure ports 3000 and 8000** are available
4. **Check environment variables** are set correctly
5. **Try running in Docker** for a clean environment

## 🎉 Success!

If everything is working correctly, you should see:
- ✅ Backend API responding at http://localhost:8000/health
- ✅ Frontend loading at http://localhost:3000
- ✅ Movie suggestions displaying on the homepage
- ✅ Search functionality working
- ✅ No CORS errors in browser console

**Enjoy exploring movies with CineScope Analyzer!** 🎬