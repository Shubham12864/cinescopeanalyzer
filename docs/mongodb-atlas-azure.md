# MongoDB Atlas on Azure Marketplace Setup

## 1. Deploy from Azure Marketplace

### Steps:
1. Go to https://portal.azure.com/
2. Click "Create a resource"
3. Search for "MongoDB Atlas"
4. Select "MongoDB Atlas" by MongoDB, Inc.
5. Click "Create"

### Configuration:
```
Subscription: Your Azure subscription
Resource Group: cinescope-rg
Resource name: cinescope-mongodb
Plan: Pay As You Go (or Free if available)
Region: Same as your other Azure resources
```

## 2. Complete MongoDB Atlas Setup

### After Azure deployment:
1. You'll be redirected to MongoDB Atlas
2. Create MongoDB Atlas account (or sign in)
3. Link your Azure subscription
4. Create a new cluster

### Cluster Configuration:
```
Cloud Provider: Microsoft Azure
Region: Same region as Azure resources
Cluster Tier: M0 Sandbox (Free) or M2/M5 for production
Cluster Name: cinescope-cluster
```

## 3. Database Access & Network

### Database Access:
1. Create database user:
   - Username: cinescope_user
   - Password: [Generate strong password]
   - Role: Atlas Admin or readWriteAnyDatabase

### Network Access:
1. Add IP addresses:
   - 0.0.0.0/0 (for Railway/Vercel access)
   - Your current IP for development

### Azure Private Endpoint (Optional):
- For production, set up Azure Private Endpoint
- Secure connection within Azure network

## 4. Get Connection String

### From Atlas Dashboard:
1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Driver: Python, Version: 3.12 or later
4. Copy connection string:

```
mongodb+srv://cinescope_user:<password>@cinescope-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

## 5. Environment Variables

### For Railway:
```bash
MONGODB_URI=mongodb+srv://cinescope_user:<password>@cinescope-cluster.xxxxx.mongodb.net/cinescope?retryWrites=true&w=majority
DATABASE_TYPE=atlas
MONGODB_DB_NAME=cinescope
```

## 6. Azure Integration Benefits

### Billing Integration:
- Charges appear on Azure bill
- Use Azure credits/commitments
- Unified cost management

### Security Integration:
- Azure Active Directory integration
- Azure Key Vault for secrets
- VNet peering for private access

### Monitoring Integration:
- Azure Monitor integration
- Log Analytics workspace
- Application Insights correlation

## 7. Database Structure

### Collections:
```javascript
// cinescope database
use cinescope

// Create collections with schema validation
db.createCollection("movies", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["id", "title", "year"],
         properties: {
            id: { bsonType: "string" },
            title: { bsonType: "string" },
            year: { bsonType: "int" },
            rating: { bsonType: "double" },
            poster: { bsonType: "string" }
         }
      }
   }
})

db.createCollection("reviews")
db.createCollection("analysis") 
db.createCollection("cache")
```

## 8. Comparison: Cosmos DB vs Atlas

| Feature | Azure Cosmos DB | MongoDB Atlas |
|---------|----------------|---------------|
| **Pricing** | Free tier: 1000 RU/s | Free tier: 512 MB |
| **Azure Integration** | Native | Via Marketplace |
| **MongoDB Compatibility** | API compatible | Full MongoDB |
| **Scaling** | Automatic | Manual/Auto |
| **Global Distribution** | Built-in | Available |
| **SLA** | 99.999% | 99.95% |

## Recommendation:
- **Development**: MongoDB Atlas (easier setup)
- **Production**: Azure Cosmos DB (better Azure integration)
- **Hybrid**: Atlas on Azure Marketplace (best of both)
