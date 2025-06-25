# 🚀 Deployment Guide

## Deployment Order & Checklist

### ✅ **STEP 1: GitHub Repository**
1. Create GitHub repository: `CineScopeAnalyzer`
2. Push code to GitHub:
   ```bash
   git remote add origin https://github.com/yourusername/CineScopeAnalyzer.git
   git branch -M main
   git push -u origin main
   ```

### ✅ **STEP 2: MongoDB Atlas (Database)**
1. Create MongoDB Atlas account: https://cloud.mongodb.com/
2. Create free M0 cluster
3. Add network access: `0.0.0.0/0`
4. Create database user
5. Get connection string
6. Update environment variables

### ✅ **STEP 3: Railway (Backend)**
1. Connect to GitHub: https://railway.app/
2. Create new project from GitHub repo
3. Set environment variables:
   ```
   OMDB_API_KEY=your_key_here
   MONGODB_URI=your_mongodb_connection_string
   PORT=8000
   ```
4. Deploy automatically

### ✅ **STEP 4: Vercel (Frontend)**
1. Connect to GitHub: https://vercel.com/
2. Import project from GitHub
3. Set framework: Next.js
4. Set root directory: `frontend`
5. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
   ```
6. Deploy automatically

### ✅ **STEP 5: GitHub Actions CI/CD**
1. Set repository secrets:
   ```
   VERCEL_TOKEN=your_vercel_token
   VERCEL_ORG_ID=your_org_id
   VERCEL_PROJECT_ID=your_project_id
   ```
2. Push code to trigger deployment

## 🔧 **Environment Variables Setup**

### Railway (Backend)
```bash
OMDB_API_KEY=your_omdb_api_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/cinescope
PORT=8000
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

### Vercel (Frontend)
```bash
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

### GitHub Secrets
```bash
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_vercel_org_id  
VERCEL_PROJECT_ID=your_vercel_project_id
```

## 🌐 **Expected URLs**
- **Frontend**: https://cine-scope-analyzer.vercel.app
- **Backend**: https://your-app.railway.app
- **Database**: MongoDB Atlas cluster

## 🔍 **Testing Deployment**
1. Test backend health: `GET /api/health`
2. Test movie search: `GET /api/movies/search?q=batman`
3. Test frontend loads and connects to backend
4. Test search functionality works end-to-end

## 🐛 **Troubleshooting**
- **CORS issues**: Check backend CORS settings
- **Environment variables**: Verify all secrets are set
- **Build failures**: Check logs in Railway/Vercel dashboards
- **Database connection**: Test MongoDB connection string

## 📊 **Monitoring**
- Railway: Built-in metrics and logs
- Vercel: Analytics and performance monitoring
- MongoDB Atlas: Database monitoring
- GitHub Actions: CI/CD pipeline status
