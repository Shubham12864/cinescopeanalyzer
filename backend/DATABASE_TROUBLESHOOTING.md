# Database Connection Troubleshooting Guide

## Current Issue
The Azure Cosmos DB connection is failing with DNS resolution error:
```
❌ DNS resolution failed: [Errno 11001] getaddrinfo failed
```

This means the hostname `cinescopeanalyzer.mongo.cosmos.azure.com` cannot be found.

## Solution Options

### Option 1: Fix Azure Cosmos DB (Recommended if you want to use Azure)

#### Step 1: Verify Account Exists
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Cosmos DB" 
3. Look for account named `cinescopeanalyzer`
4. If not found → the account creation failed, recreate it

#### Step 2: Get Correct Connection String
1. Click on your Cosmos DB account
2. Go to "Keys" section
3. Copy the **Primary Connection String** (not individual keys)
4. It should look like:
   ```
   mongodb://accountname:key@accountname.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&maxIdleTimeMS=120000&appName=@accountname@
   ```

#### Step 3: Configure Firewall
1. Go to "Firewall and virtual networks"
2. Choose one of:
   - **Enable "Allow access from Azure services"** (easiest)
   - **Add your current IP address** to allowed IPs
   - **Allow access from all networks** (less secure, for testing only)

#### Step 4: Test Connection
1. Update the `.env` file with the correct connection string
2. Run the test script again

### Option 2: Use MongoDB Atlas (Alternative - Easier Setup)

MongoDB Atlas is free, reliable, and easier to set up:

#### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for free account
3. Create a new cluster (choose free tier)

#### Step 2: Configure Database
1. Create database user with username/password
2. Add your IP address to IP Access List
3. Get connection string from "Connect" → "Connect your application"

#### Step 3: Update Environment
```env
DATABASE_TYPE=atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/cinescope?retryWrites=true&w=majority
```

## Current Status
- ✅ Backend database code is ready
- ✅ Connection string format is correct
- ❌ DNS resolution failing (account might not exist)
- ⏳ Waiting for database access to be resolved

## Next Steps
1. **Choose your preferred option** (Azure Cosmos DB or MongoDB Atlas)
2. **Follow the appropriate steps** above
3. **Update the connection string** in `.env`
4. **Test the connection** using our test script
5. **Deploy to production** once connection is verified

## Testing Commands
```bash
# Test connection string validation
python test_connection_string.py

# Test full database operations
python test_db_connection.py

# Start the backend server
python -m uvicorn app.main:app --reload
```
