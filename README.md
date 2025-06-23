# CineScopeAnalyzer

A full-stack movie analysis application built with FastAPI (backend) and Next.js (frontend).

## ✅ Status: FULLY WORKING

The application is now fully functional with:
- ✅ Backend FastAPI server running on port 8000
- ✅ Frontend Next.js app running on port 3000  
- ✅ Complete movie search and analysis functionality
- ✅ Backend connectivity detection with fallback to mock data
- ✅ Movie detail pages and analysis views
- ✅ Modern UI with shadcn/ui components

## Quick Start

### Option 1: Use the Startup Script (Recommended)
```bash
# Double-click or run from command line:
start-full-app.bat
```

This will automatically start both the backend and frontend servers in separate terminal windows.

### Option 2: Manual Start

#### Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend  
npm run dev
```

## Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Features

### Current Features
- 🎬 Movie search and browsing
- 📊 Movie analysis and sentiment analysis
- 🔍 Detailed movie information pages
- 📈 Analytics dashboard with charts
- 🌐 Backend connectivity status
- 📱 Responsive modern UI
- 🎯 Movie cards with hover effects and actions

### Backend Features
- FastAPI REST API
- Movie data management
- TMDB API integration
- Movie analysis endpoints
- CORS support for frontend

### Frontend Features
- Next.js 14 with TypeScript
- shadcn/ui component library
- Tailwind CSS styling
- Movie context for state management
- Dynamic routing for movie details
- Fallback to mock data when backend is offline

## Architecture

```
CineScopeAnalyzer/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── api/routes/       # API route handlers
│   │   ├── core/             # Core functionality (APIs)
│   │   ├── services/         # Business logic
│   │   └── models/           # Data models
│   └── requirements.txt      # Python dependencies
└── frontend/          # Next.js frontend
    ├── app/                  # Next.js 14 app directory
    ├── components/           # React components
    ├── contexts/             # React context providers
    ├── lib/                  # Utility libraries
    └── types/                # TypeScript type definitions
```

## Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or pnpm

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup  
```bash
cd frontend
npm install
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend (no build needed, Python runs directly)
```

## Troubleshooting

### Backend Not Starting
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is not in use

### Frontend Not Starting  
- Ensure Node.js 18+ is installed
- Install dependencies: `npm install`
- Check port 3000 is not in use

### Connection Issues
- The frontend will automatically fall back to mock data if the backend is offline
- Check the connection status indicator in the UI
- Ensure both servers are running on the correct ports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both backend and frontend
5. Submit a pull request

## License

This project is open source and available under the MIT License.
