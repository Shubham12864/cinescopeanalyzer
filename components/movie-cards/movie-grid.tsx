"use client"

import { motion } from "framer-motion"
import { useMovieContext } from "@/contexts/movie-context"
import { MovieRow } from "./movie-row"
import { NetflixHeroBanner } from "./netflix-hero-banner"
import { MovieCard } from "./movie-card"
import { MovieCardSkeleton } from "./movie-card-skeleton"
import { useState, useEffect } from "react"
import { movieApi } from "@/lib/api"
import type { Movie } from "@/types/movie"

// Search history management
const getSearchHistory = (): string[] => {
  if (typeof window === 'undefined') return []
  try {
    const history = localStorage.getItem('movie-search-history')
    return history ? JSON.parse(history) : []
  } catch {
    return []
  }
}

const addToSearchHistory = (query: string) => {
  if (typeof window === 'undefined') return
  try {
    const history = getSearchHistory()
    const updatedHistory = [query, ...history.filter(h => h !== query)].slice(0, 10)
    localStorage.setItem('movie-search-history', JSON.stringify(updatedHistory))
  } catch {
    // Silently fail if localStorage is not available
  }
}

export function MovieGrid() {
  const { movies, isLoading, searchQuery, error, clearSearch, isDemoMode, isBackendConnected } = useMovieContext()
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([])
  const [popularMovies, setPopularMovies] = useState<Movie[]>([])
  const [topRatedMovies, setTopRatedMovies] = useState<Movie[]>([])
  const [featuredMovie, setFeaturedMovie] = useState<any>(null)
  const [loadingSpecialData, setLoadingSpecialData] = useState(true)

  // Add current search to history when searching
  useEffect(() => {
    if (searchQuery && searchQuery.trim()) {
      addToSearchHistory(searchQuery.trim())
    }
  }, [searchQuery])
  
  useEffect(() => {
    const loadSpecialData = async () => {
      try {
        setLoadingSpecialData(true)
        console.log('🎬 Loading special movie data for grid...')
        
        // Always try to fetch from backend first
        let trending: Movie[] = []
        let popular: Movie[] = []
        
        try {
          console.log('📡 Fetching trending movies...')
          trending = await movieApi.getTrendingMovies()
          console.log(`✅ Loaded ${trending?.length || 0} trending movies`)
        } catch (error) {
          console.warn('⚠️ Trending movies API failed, using fallback:', error)
          trending = movies.slice(0, 15)
        }
        
        try {
          console.log('📡 Fetching popular movies...')
          popular = await movieApi.getPopularMovies(15)
          console.log(`✅ Loaded ${popular?.length || 0} popular movies`)
        } catch (error) {
          console.warn('⚠️ Popular movies API failed, using fallback:', error)
          popular = movies.slice(5, 20)
        }
        
        setTrendingMovies(trending || [])
        setPopularMovies(popular || [])
        
        // Get top rated movies (rating > 8.0)
        const topRated = (popular.length > 0 ? popular : movies)
          .filter(m => m.rating && m.rating > 8.0)
          .slice(0, 15)
        setTopRatedMovies(topRated)
        
        // Set featured movie from trending or popular movies
        const featuredSource = trending.length > 0 ? trending : popular.length > 0 ? popular : movies
        if (featuredSource.length > 0) {
          const featured = featuredSource[0]
          setFeaturedMovie({
            id: featured.id,
            title: featured.title,
            description: featured.plot || "An amazing movie experience awaits.",
            backdrop: featured.poster && featured.poster.includes('/api/movies/image-proxy') 
              ? featured.poster 
              : featured.poster 
                ? `http://localhost:8000/api/movies/image-proxy?url=${encodeURIComponent(featured.poster)}`
                : "https://via.placeholder.com/1920x1080/1a1a1a/ffffff?text=" + encodeURIComponent(featured.title),
            rating: featured.rating || 8.0,
            year: featured.year || 2023,
            genre: featured.genre || ["Action", "Adventure"]
          })
        }
        
      } catch (error) {
        console.error("❌ Failed to load special data:", error)
        // Use fallback data only as last resort
        console.log('📦 Using fallback movie data')
        setTrendingMovies(movies.slice(0, 15))
        setPopularMovies(movies.slice(5, 20))
        setTopRatedMovies(movies.filter(m => m.rating && m.rating > 7.0).slice(0, 15))
      } finally {
        setLoadingSpecialData(false)
      }
    }

    if (!searchQuery && movies.length > 0) {
      loadSpecialData()
    }
  }, [searchQuery, movies])

  if (isLoading) {
    return (
      <div className="space-y-8">
        {searchQuery && (
          <div className="px-4 lg:px-8">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-6 h-6 border-2 border-red-600/30 border-t-red-600 rounded-full animate-spin" />
              <h2 className="text-2xl font-bold text-white">
                Searching for "{searchQuery}"...
              </h2>
            </div>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-8 px-6 lg:px-12 max-w-screen-2xl mx-auto">
          {Array.from({ length: searchQuery ? 8 : 12 }).map((_, index) => (
            <MovieCardSkeleton key={index} />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    const getErrorType = (errorMessage: string) => {
      if (errorMessage.includes('Network') || errorMessage.includes('fetch') || errorMessage.includes('connection')) {
        return 'network'
      }
      if (errorMessage.includes('timeout')) {
        return 'timeout'
      }
      if (errorMessage.includes('404') || errorMessage.includes('not found')) {
        return 'not_found'
      }
      if (errorMessage.includes('500') || errorMessage.includes('server')) {
        return 'server'
      }
      return 'unknown'
    }

    const errorType = getErrorType(error.toLowerCase())
    
    const getErrorConfig = (type: string) => {
      switch (type) {
        case 'network':
          return {
            icon: '🌐',
            title: 'Connection Error',
            description: 'Unable to connect to the movie database server.',
            suggestion: 'Please check your internet connection and try again.',
            showRetry: true
          }
        case 'timeout':
          return {
            icon: '⏱️',
            title: 'Request Timeout',
            description: 'The server is taking too long to respond.',
            suggestion: 'The server may be busy. Please try again in a moment.',
            showRetry: true
          }
        case 'server':
          return {
            icon: '🔧',
            title: 'Server Error',
            description: 'The movie database server encountered an error.',
            suggestion: 'This is usually temporary. Please try again later.',
            showRetry: true
          }
        case 'not_found':
          return {
            icon: '🔍',
            title: 'No Results Found',
            description: 'No movies found matching your search.',
            suggestion: 'Try different keywords or check your spelling.',
            showRetry: false
          }
        default:
          return {
            icon: '⚠️',
            title: 'Search Failed',
            description: error,
            suggestion: 'Please try again or contact support if the problem persists.',
            showRetry: true
          }
      }
    }

    const errorConfig = getErrorConfig(errorType)

    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12 px-4">
        <div className="bg-gray-900/80 backdrop-blur-sm rounded-2xl p-8 max-w-md mx-auto border border-red-800/50">
          <div className="text-4xl mb-4">{errorConfig.icon}</div>
          <h3 className="text-xl font-semibold text-red-400 mb-3">{errorConfig.title}</h3>
          <p className="text-gray-300 mb-4">{errorConfig.description}</p>
          <p className="text-gray-400 text-sm mb-6">{errorConfig.suggestion}</p>
          
          {isDemoMode && (
            <div className="bg-yellow-900/30 border border-yellow-600 rounded-lg p-3 mb-4">
              <p className="text-yellow-300 text-sm">
                🔄 Demo Mode Active - Limited functionality available
              </p>
            </div>
          )}
          
          <div className="space-y-3">
            {errorConfig.showRetry && searchQuery && (
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                🔄 Try Again
              </button>
            )}
            <button
              onClick={clearSearch}
              className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </motion.div>
    )
  }  if (!searchQuery) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
        {isDemoMode && (
          <div className="bg-yellow-900/20 border-b border-yellow-600/30 px-4 py-3 mb-6">
            <div className="max-w-screen-2xl mx-auto flex items-center justify-center">
              <div className="flex items-center space-x-2 text-yellow-300">
                <span className="text-lg">⚠️</span>
                <span className="text-sm font-medium">
                  Demo Mode: Backend unavailable - showing limited sample data
                </span>
              </div>
            </div>
          </div>
        )}
        <NetflixHeroBanner featuredMovie={featuredMovie} />
        <div className="space-y-8 mt-8">
          <MovieRow 
            title="🔥 Trending Now" 
            movies={trendingMovies.length > 0 ? trendingMovies : movies.slice(0, 15)} 
            isLoading={loadingSpecialData && trendingMovies.length === 0}
          />
          <MovieRow 
            title="⭐ Popular Movies" 
            movies={popularMovies.length > 0 ? popularMovies : movies.slice(10, 25)} 
            isLoading={loadingSpecialData && popularMovies.length === 0}
          />
          <MovieRow 
            title="🏆 Top Rated" 
            movies={topRatedMovies.length > 0 ? topRatedMovies : movies.filter(m => m.rating && m.rating > 8.0).slice(0, 15)} 
            isLoading={loadingSpecialData && topRatedMovies.length === 0}
          />
          <MovieRow 
            title="💎 Suggested Movies" 
            movies={movies.slice(2, 17)} 
            isLoading={loadingSpecialData}
          />
        </div>
      </motion.div>
    )
  }
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <div className="px-4 lg:px-8 mb-8">
        {searchQuery && (
          <div className="flex justify-between items-center mb-8 px-4 lg:px-8">
            <div>
              <h2 className="text-3xl font-bold font-poppins text-white mb-2">Search Results for "{searchQuery}"</h2>
              <div className="text-gray-400">
                {isLoading ? "Searching..." : `${movies.length} result${movies.length !== 1 ? "s" : ""} found`}
              </div>
            </div>
            <button
              onClick={clearSearch}
              className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        )}
      </div>

      {/* FIXED: Show actual movies when search results are available */}
      {searchQuery && !isLoading && movies.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-8 px-6 lg:px-12 max-w-screen-2xl mx-auto">
          {movies.map((movie, index) => (
            <motion.div
              key={movie.id || movie.imdbId}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <MovieCard movie={movie} />
            </motion.div>
          ))}
        </div>
      )}

      {/* Show loading skeletons only when actually loading */}
      {searchQuery && isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-8 px-6 lg:px-12 max-w-screen-2xl mx-auto">
          {Array.from({ length: 12 }).map((_, index) => (
            <MovieCardSkeleton key={index} />
          ))}
        </div>
      )}

      {/* Show no results message instead of empty space */}
      {searchQuery && !isLoading && movies.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">No movies found for "{searchQuery}"</p>
          <button 
            onClick={() => clearSearch()}
            className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Clear Search
          </button>
        </div>
      )}
    </motion.div>
  )
}
