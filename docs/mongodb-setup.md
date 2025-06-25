# MongoDB Atlas Configuration Guide

## 1. Create MongoDB Atlas Account
- Go to https://cloud.mongodb.com/
- Sign up for free account
- Create a new cluster (M0 Sandbox - Free)

## 2. Network Access
- Add IP address: 0.0.0.0/0 (for Railway/Vercel access)
- Or specific Railway/Vercel IP ranges

## 3. Database User
- Create database user with read/write permissions
- Username: cinescope_user
- Password: [Generate strong password]

## 4. Connection String
```
mongodb+srv://cinescope_user:<password>@cluster0.xxxxx.mongodb.net/cinescope?retryWrites=true&w=majority
```

## 5. Environment Variables
Add to Railway and Vercel:
```
MONGODB_URI=mongodb+srv://cinescope_user:<password>@cluster0.xxxxx.mongodb.net/cinescope?retryWrites=true&w=majority
DATABASE_TYPE=mongodb
```

## 6. Update Backend Code
- Install: `pip install motor pymongo`
- Create MongoDB models and connection
- Update movie service to use MongoDB

## 7. Collections Structure
```
cinescope/
├── movies          # Movie data
├── reviews         # User reviews
├── analysis        # Analysis results
├── cache           # API cache
└── users           # User data (future)
```
