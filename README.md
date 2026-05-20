# CineScope Analyzer 🎬

CineScope Analyzer is an intelligent, full-stack web application designed to help movie enthusiasts discover films, read authentic community reviews, and get AI-powered insights. By combining data from the largest movie databases with real community discussions and advanced generative AI, CineScope provides a comprehensive breakdown of any film.

## 🚀 Key Features

- **Movie Discovery & Search**: Find any movie instantly with real-time search, powered by the TMDB API.
- **Dynamic Content**: Enjoy high-quality movie posters (smartly proxied to bypass CORS) and beautiful UI built with Next.js and Tailwind CSS.
- **Reddit Community Sentiment**: Automatically scrapes and analyzes real user reviews and discussions from Reddit communities like `r/movies` and `r/TrueFilm`.
- **Gemini AI Analysis**: Synthesizes massive amounts of text from Reddit reviews into a clean, easy-to-read summary of community sentiment using Google's Gemini AI.
- **Performance Optimized**: Uses Google Cloud Firestore to cache AI analysis and Reddit scraping results to provide lightning-fast loads for previously searched movies.

## 🏗️ Architecture

CineScope Analyzer is built with a modern, decoupled architecture. The frontend is a React application built on Next.js, and the backend is a Python REST API powered by FastAPI.

```mermaid
graph TD
    %% Frontend Layer
    Client[Browser / User]
    NextJS[Next.js Frontend\nFirebase Hosting]
    
    %% Backend Layer
    FastAPI[FastAPI Backend\nGoogle Cloud Run]
    
    %% External APIs & Databases
    TMDB[TMDB API\nMovie Metadata]
    Reddit[Reddit API\nCommunity Reviews]
    Gemini[Google Gemini API\nAI Sentiment Analysis]
    Firestore[(Cloud Firestore\nData Cache)]
    
    %% Connections
    Client <-->|HTTPS / API Calls| NextJS
    NextJS <-->|REST API| FastAPI
    
    %% Backend Connections
    FastAPI <-->|Fetch Movies| TMDB
    FastAPI <-->|Fetch Discussions| Reddit
    FastAPI <-->|Analyze Text| Gemini
    FastAPI <-->|Read/Write Cache| Firestore
    
    %% Styling
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef backend fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef external fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef db fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff;
    
    class NextJS frontend;
    class FastAPI backend;
    class TMDB,Reddit,Gemini external;
    class Firestore db;
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS & Framer Motion
- **Hosting**: Firebase Hosting

### Backend
- **Framework**: FastAPI (Python)
- **AI Integration**: Google Generative AI (Gemini Pro)
- **Database/Cache**: Google Cloud Firestore
- **Hosting**: Google Cloud Run (Dockerized)

### Third-Party APIs
- The Movie Database (TMDB)
- Reddit API (OAuth Client Credentials)
- OMDB API

## 💻 Getting Started (Local Development)

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- A Google Cloud Project with Firestore enabled
- API Keys for TMDB, Reddit, and Gemini

### Backend Setup
1. Navigate to the `backend/` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment.
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.template` to `.env` and fill in your API keys.
6. Run the server: `python -m uvicorn app.main:app --reload --port 8080`

### Frontend Setup
1. Ensure you are in the root directory.
2. Install dependencies: `npm install`
3. Set up the local `.env.local` to point to the backend (e.g., `NEXT_PUBLIC_API_URL=http://localhost:8080/api`).
4. Run the development server: `npm run dev`

---
*Built with ❤️ for movie lovers.*