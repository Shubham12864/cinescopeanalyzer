# 🎬 CineScopeAnalyzer

A modern, full-stack movie discovery and analysis platform with React/Next.js frontend and FastAPI backend.

## ✨ Features

### 🎯 Core Features
- **Movie Search**: Search for movies with real-time results
- **Movie Discovery**: Browse trending, popular, and top-rated movies
- **Detailed Movie Info**: Get comprehensive movie details, ratings, cast, and plot
- **Real Poster Images**: High-quality movie posters from OMDB/IMDB
- **Responsive Design**: Modern, Netflix-style UI that works on all devices

### 🔧 Technical Features
- **Real-time API**: Fast movie data from OMDB API
- **Smart Fallbacks**: Graceful degradation when APIs are unavailable  
- **Caching System**: Efficient data caching for better performance
- **Modern UI**: Built with Tailwind CSS and Framer Motion
- **Type Safety**: Full TypeScript support

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ 
- **Python** 3.8+
- **npm** or **pnpm**

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/CineScopeAnalyzer.git
cd CineScopeAnalyzer
```

### 2. Setup Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Setup Frontend
```bash
cd frontend
npm install
# or
pnpm install

npm run dev
# or
pnpm dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
CineScopeAnalyzer/
├── frontend/                 # Next.js React frontend
│   ├── app/                 # App router pages
│   ├── components/          # Reusable React components
│   ├── contexts/           # React context providers
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility libraries
│   └── types/              # TypeScript type definitions
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Data models
│   │   └── services/       # Business logic services
│   └── requirements.txt    # Python dependencies
├── cache/                  # Application cache
├── logs/                   # Application logs
└── README.md
```

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Lucide React** - Modern icon library

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type hints
- **HTTPX** - Async HTTP client for API calls
- **Uvicorn** - ASGI server for FastAPI

### APIs & Data
- **OMDB API** - Movie database and poster images
- **SQLite** - Local caching database

## 🔧 Configuration

### Environment Variables

Create `.env` files in both frontend and backend directories:

**Backend (.env)**
```bash
OMDB_API_KEY=your_omdb_api_key_here
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Getting OMDB API Key
1. Visit [OMDB API](http://www.omdbapi.com/apikey.aspx)
2. Register for a free API key
3. Add it to your backend `.env` file

## 📖 API Documentation

The backend provides a comprehensive REST API:

- **GET /api/movies/** - Get all movies
- **GET /api/movies/search?q={query}** - Search movies
- **GET /api/movies/trending** - Get trending movies
- **GET /api/movies/popular** - Get popular movies
- **GET /api/movies/suggestions** - Get movie suggestions

Visit http://localhost:8000/docs for interactive API documentation.

## 🎨 UI Components

The frontend includes reusable components:

- **MovieCard** - Individual movie display card
- **MovieGrid** - Responsive movie grid layout
- **SearchBar** - Movie search input with autocomplete
- **MovieRow** - Horizontal scrollable movie rows
- **Navigation** - Sidebar navigation component

## 🚀 Deployment

### Frontend (Vercel)
```bash
npm run build
```
Deploy to Vercel by connecting your GitHub repository.

### Backend (Railway/Heroku)
The backend includes `railway.json` and `Dockerfile` for easy deployment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/CineScopeAnalyzer/issues)

## 🙏 Acknowledgments

- [OMDB API](http://www.omdbapi.com/) for movie data
- [Next.js](https://nextjs.org/) team for the amazing framework
- [FastAPI](https://fastapi.tiangolo.com/) for the beautiful Python framework
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework

---

Made with ❤️ for movie enthusiasts
