# CineScopeAnalyzer - Full Flow Test

## Backend + Frontend Integration Test

### 1. Backend Health ✅
- URL: http://localhost:8000/health
- Status: ✅ Running with web scrapers enabled

### 2. Frontend Health ✅
- URL: http://localhost:3001
- Status: ✅ Running and accessible

### 3. API Endpoints Test ✅

#### Search Movies
```bash
curl "http://localhost:8000/api/movies/search?q=batman"
```
**Expected**: List of Batman movies with real OMDB/TMDB data + potential scraping enhancement

#### Get Movie Details  
```bash
curl "http://localhost:8000/api/movies/tt0372784"
```
**Expected**: Detailed Batman Begins movie information

#### Get Suggestions
```bash
curl "http://localhost:8000/api/movies/suggestions"
```
**Expected**: List of suggested movies with rich data

### 4. Frontend Features to Test

#### A. Search Functionality
1. Go to: http://localhost:3001
2. Type "batman" in the search box
3. Press Enter or click Search
4. **Expected**: Should show Batman movies with posters and details
5. **Debug**: Check browser console for search logs

#### B. Movie Details Navigation
1. On search results or suggestions, click on any movie card
2. **Expected**: Should navigate to `/movies/{id}` and show full movie details
3. **Expected**: Should display movie poster, plot, rating, genre, cast, director
4. **Debug**: Check browser console for navigation logs

#### C. Movie Analysis
1. On any movie details page, click "Analyze" button
2. **Expected**: Should navigate to analysis page with charts and data
3. **Expected**: Should show rating distribution, genre analysis, review timeline

### 5. Data Sources Verification

#### API + Scraping Integration
- **Primary**: OMDB API (comprehensive movie data)
- **Secondary**: TMDB API (trending/popular movies)  
- **Enhancement**: Web Scraping (additional reviews from IMDB, RT, Metacritic)
- **Fallback**: Demo data (if all above fail)

### 6. Troubleshooting

If any issues occur, check:
1. Backend logs in terminal
2. Frontend console in browser (F12)
3. Network tab for failed API calls
4. CORS errors (should be fixed)

### 7. Expected Console Logs

**Frontend Search:**
```
🔍 Hero: Search submitted with query: batman
🔍 Hero: Setting search query and calling search handler
🔗 API Call: http://localhost:8000/api/movies/search?q=batman
✅ API Response: [array of movies]
```

**Movie Details Click:**
```
🎬 MovieCard: Clicking on movie details for: Batman Begins ID: tt0372784
🎬 MovieCard: Navigating to: /movies/tt0372784
🎬 MovieDetails: Loading movie with ID: tt0372784
🎬 MovieDetails: Received movie data: {movie object}
🎬 MovieDetails: Movie loaded successfully: Batman Begins
```

**Backend Logs:**
```
🔑 OMDB API initialized with key: REAL/DEMO
🔑 TMDB API initialized with key: REAL/DEMO  
🕷️ Web scraping: ENABLED
🔍 Searching for: 'batman' (limit: 20)
🎬 Trying OMDB API...
✅ Got X real movies from OMDB
```
