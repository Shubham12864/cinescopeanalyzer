# Azure Cosmos DB for MongoDB Setup Guide

## 1. Create Azure Cosmos DB Account

### Via Azure Portal:
1. Go to https://portal.azure.com/
2. Click "Create a resource"
3. Search for "Azure Cosmos DB"
4. Click "Create" → "Azure Cosmos DB for MongoDB"

### Configuration:
```
Subscription: Your Azure subscription
Resource Group: Create new "cinescope-rg"
Account Name: cinescope-cosmosdb
API: Azure Cosmos DB for MongoDB
Location: (Choose closest to your users)
Capacity mode: Provisioned throughput (or Serverless for dev)
```

## 2. Configure Database Settings

### Free Tier (400 RU/s):
- Good for development and testing
- Free 1000 RU/s and 25 GB storage

### Networking:
- Selected networks: Add your IP
- Allow access from Azure Portal: Yes
- Allow access from Azure services: Yes

## 3. Get Connection String

### After deployment:
1. Go to your Cosmos DB account
2. Navigate to "Connection strings" (left menu)
3. Copy "Primary Connection String"

Format will be:
```
mongodb://cinescope-cosmosdb:<password>@cinescope-cosmosdb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@cinescope-cosmosdb@
```

## 4. Create Database and Collections

### Using Azure Portal:
1. Go to "Data Explorer"
2. Create new database: "cinescope"
3. Create collections:
   - movies (Partition key: /id)
   - reviews (Partition key: /movieId)
   - analysis (Partition key: /movieId)
   - cache (Partition key: /key)

### Using Connection String:
```python
from pymongo import MongoClient

# Connect to Azure Cosmos DB
client = MongoClient("your_connection_string")
db = client.cinescope

# Create collections
movies = db.movies
reviews = db.reviews
analysis = db.analysis
cache = db.cache
```

## 5. Environment Variables

### For Railway (Backend):
```bash
MONGODB_URI=mongodb://cinescope-cosmosdb:<password>@cinescope-cosmosdb.mongo.cosmos.azure.com:10255/cinescope?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@cinescope-cosmosdb@
DATABASE_TYPE=cosmosdb
AZURE_COSMOSDB_ENDPOINT=https://cinescope-cosmosdb.documents.azure.com:443/
```

## 6. Backend Code Updates

### Install Dependencies:
```bash
pip install motor pymongo azure-cosmos
```

### Connection Code:
```python
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI")
        self.client = None
        self.db = None
    
    async def connect(self):
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client.cinescope
        
    async def get_collection(self, collection_name: str):
        return self.db[collection_name]
```

## 7. Pricing (Free Tier Available):
- Free tier: 1000 RU/s + 25 GB storage
- Pay-as-you-go: $0.008 per 100 RU/s per hour
- Serverless: $0.25 per million requests

## 8. Monitoring:
- Azure Monitor integration
- Request units (RU) consumption tracking
- Query performance insights
- Automatic scaling options
