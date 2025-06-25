# 🔷 Azure Deployment Guide for CineScopeAnalyzer

## 🚀 **Azure Deployment Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Frontend      │    │    Backend       │    │    Database        │
│   (Vercel)      │───▶│   (Railway)      │───▶│ Azure Cosmos DB    │
│   Next.js       │    │   FastAPI        │    │ or MongoDB Atlas   │
└─────────────────┘    └──────────────────┘    └────────────────────┘
         │                       │                        │
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   GitHub        │    │  GitHub Actions  │    │   Azure Monitor    │
│   Repository    │    │     CI/CD        │    │   (Monitoring)     │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

## 📋 **Step-by-Step Azure Deployment**

### **STEP 1: Create Azure Resources**

#### 1.1 Create Resource Group
```bash
# Via Azure CLI (optional)
az group create --name cinescope-rg --location eastus
```

#### 1.2 Create MongoDB Database (Choose One)

**Option A: Azure Cosmos DB for MongoDB**
1. Go to https://portal.azure.com/
2. Create resource → Azure Cosmos DB → Azure Cosmos DB for MongoDB
3. Configuration:
   ```
   Account Name: cinescope-cosmosdb
   API: Azure Cosmos DB for MongoDB
   Resource Group: cinescope-rg
   Location: East US (or your preferred region)
   Capacity mode: Serverless (for dev) or Provisioned (for prod)
   ```

**Option B: MongoDB Atlas on Azure**
1. Azure Marketplace → Search "MongoDB Atlas"
2. Create MongoDB Atlas resource
3. Link to your Azure subscription
4. Follow Atlas setup wizard

### **STEP 2: Configure Database**

#### For Azure Cosmos DB:
```bash
# Environment Variables
MONGODB_URI=mongodb://cinescope-cosmosdb:<password>@cinescope-cosmosdb.mongo.cosmos.azure.com:10255/cinescope?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000
DATABASE_TYPE=cosmosdb
MONGODB_DB_NAME=cinescope
```

#### For MongoDB Atlas on Azure:
```bash
# Environment Variables
MONGODB_URI=mongodb+srv://user:password@cluster.xxxxx.mongodb.net/cinescope?retryWrites=true&w=majority
DATABASE_TYPE=atlas
MONGODB_DB_NAME=cinescope
```

### **STEP 3: Deploy Backend to Railway**

1. **Connect Railway to GitHub:**
   - Go to https://railway.app/
   - Sign in with GitHub
   - New Project → Deploy from GitHub repo

2. **Configure Environment Variables:**
   ```bash
   # Railway Environment Variables
   OMDB_API_KEY=your_omdb_api_key_here
   MONGODB_URI=your_azure_mongodb_connection_string
   DATABASE_TYPE=cosmosdb  # or "atlas"
   MONGODB_DB_NAME=cinescope
   PORT=8000
   PYTHONPATH=/app
   PYTHONUNBUFFERED=1
   ```

3. **Verify Deployment:**
   - Check Railway logs for successful deployment
   - Test health endpoint: `https://your-app.railway.app/api/health`

### **STEP 4: Deploy Frontend to Vercel**

1. **Connect Vercel to GitHub:**
   - Go to https://vercel.com/
   - Import project from GitHub
   - Select your repository

2. **Configure Build Settings:**
   ```bash
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

3. **Environment Variables:**
   ```bash
   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
   ```

### **STEP 5: Configure Azure Monitoring (Optional)**

#### Azure Application Insights:
1. Create Application Insights resource
2. Add connection string to Railway:
   ```bash
   APPLICATIONINSIGHTS_CONNECTION_STRING=your_app_insights_connection_string
   ```

#### Azure Monitor Integration:
```python
# Add to backend (optional)
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string="your_connection_string"
)
```

## 🔧 **Configuration Files Update**

### Update Railway Configuration:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "environments": {
    "production": {
      "variables": {
        "DATABASE_TYPE": "cosmosdb",
        "MONGODB_DB_NAME": "cinescope"
      }
    }
  }
}
```

## 🔍 **Testing Azure Deployment**

### Backend Health Check:
```bash
curl https://your-railway-app.railway.app/api/health
```

### Database Connection Test:
```bash
curl https://your-railway-app.railway.app/api/movies/trending
```

### Frontend Test:
```bash
# Visit your Vercel URL
https://your-app.vercel.app
```

### Search Functionality Test:
```bash
curl "https://your-railway-app.railway.app/api/movies/search?q=batman"
```

## 💰 **Azure Cost Optimization**

### Free Tier Usage:
- **Cosmos DB**: 1000 RU/s + 25 GB storage (free forever)
- **Application Insights**: 1 GB/month (free)
- **Monitor**: Basic metrics (free)

### Scaling Options:
- **Cosmos DB**: Auto-scale, serverless, or provisioned
- **Railway**: Automatic scaling based on usage
- **Vercel**: Automatic edge deployment

## 🔒 **Security Best Practices**

### Network Security:
```bash
# Cosmos DB firewall rules
- Add Railway IP ranges
- Add Vercel IP ranges  
- Add your development IP
```

### Secret Management:
```bash
# Use Azure Key Vault (optional)
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
```

### CORS Configuration:
```python
# Backend CORS for Azure
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 📊 **Monitoring & Alerts**

### Set up Azure Alerts:
1. Resource Health alerts
2. Performance alerts (high RU consumption)
3. Cost alerts
4. Availability alerts

### Dashboard Creation:
1. Azure Portal dashboard
2. Application Insights dashboard
3. Railway metrics dashboard
4. Vercel analytics dashboard

## 🚀 **Production Checklist**

- [ ] Azure Cosmos DB created and configured
- [ ] Railway backend deployed with environment variables
- [ ] Vercel frontend deployed and connected
- [ ] Database collections created with proper indexes
- [ ] CORS configured for production domains
- [ ] Monitoring and alerts set up
- [ ] SSL certificates configured (automatic with Railway/Vercel)
- [ ] Custom domains configured (optional)
- [ ] Backup strategy implemented
- [ ] Performance testing completed

Your CineScopeAnalyzer is now ready for production on Azure! 🎉
