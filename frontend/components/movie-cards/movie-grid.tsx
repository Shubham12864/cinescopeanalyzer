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
  const { movies, isLoading, searchQuery, error, clearSearch } = useMovieContext()
  const [trendingMovies, setTrendingMovies] = useState<Movie[]>([])
  const [popularMovies, setPopularMovies] = useState<Movie[]>([])
  const [topRatedMovies, setTopRatedMovies] = useState<Movie[]>([])
  const [recentlyAddedMovies, setRecentlyAddedMovies] = useState<Movie[]>([])
  const [featuredMovie, setFeaturedMovie] = useState<any>(null)
  const [loadingSpecialData, setLoadingSpecialData] = useState(true)
  const [hasSearchHistory, setHasSearchHistory] = useState(false)

  // Check if user has search history on component mount
  useEffect(() => {
    const history = getSearchHistory()
    setHasSearchHistory(history.length > 0)
  }, [])

  // Add current search to history when searching
  useEffect(() => {
    if (searchQuery && searchQuery.trim()) {
      addToSearchHistory(searchQuery.trim())
      setHasSearchHistory(true)
    }
  }, [searchQuery])
  useEffect(() => {
    const loadSpecialData = async () => {
      try {
        setLoadingSpecialData(true)
        
        // Fetch trending movies
        const trending = await movieApi.getTrendingMovies()
        setTrendingMovies(trending || [])
        
        // Fetch popular movies  
        const popular = await movieApi.getPopularMovies()
        setPopularMovies(popular || [])
        
        // Get top rated movies (rating > 8.0)
        const topRated = movies.filter(m => m.rating && m.rating > 8.0).slice(0, 15)
        setTopRatedMovies(topRated)
        
        // Set recently added based on search history or fallback to latest movies
        const history = getSearchHistory()
        let recentMovies: Movie[] = []
        
        if (history.length > 0 && hasSearchHistory) {
          // Get movies from search history
          const historyMovies = movies.filter(m => 
            history.some(term => 
              m.title.toLowerCase().includes(term.toLowerCase()) ||
              m.genre?.some(g => g.toLowerCase().includes(term.toLowerCase()))
            )
          ).slice(0, 15)
          recentMovies = historyMovies
        } else {
          // Fallback to latest movies for new users
          recentMovies = movies.slice(0, 15)
        }
        setRecentlyAddedMovies(recentMovies)
        
        // Set featured movie from trending
        if (trending && trending.length > 0) {
          const featured = trending[0]
          setFeaturedMovie({
            id: featured.id,
            title: featured.title,
            description: featured.plot || "An amazing movie experience awaits.",
            backdrop: featured.poster || "https://via.placeholder.com/1920x1080/1a1a1a/ffffff?text=Featured%20Movie",
            rating: featured.rating || 8.0,
            year: featured.year || 2023,
            genre: featured.genre || ["Action", "Adventure"]
          })
        }
        
      } catch (error) {
        console.error("Failed to load special data:", error)
        // Use fallback data
        setTrendingMovies(movies.slice(0, 15))
        setPopularMovies(movies.slice(5, 20))
        setTopRatedMovies(movies.filter(m => m.rating && m.rating > 7.0).slice(0, 15))
        setRecentlyAddedMovies(movies.slice(1, 16))
      } finally {
        setLoadingSpecialData(false)
      }
    }

    if (!searchQuery) {
      loadSpecialData()
    }
  }, [searchQuery, movies, hasSearchHistory])

  if (isLoading || (loadingSpecialData && !searchQuery)) {
    return (
      <div className="space-y-12">        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-8 px-6 lg:px-12 max-w-screen-2xl mx-auto">
          {Array.from({ length: 8 }).map((_, index) => (
            <MovieCardSkeleton key={index} />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12 px-4">
        <div className="bg-gray-900/80 backdrop-blur-sm rounded-2xl p-8 max-w-md mx-auto border border-red-800">
          <h3 className="text-xl font-semibold text-red-400 mb-2">Error</h3>
          <p className="text-gray-400">{error}</p>
        </div>
      </motion.div>
    )
  }  if (!searchQuery) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
        <NetflixHeroBanner featuredMovie={featuredMovie} />
        <div className="space-y-8 mt-8">
          <MovieRow title="🔥 Trending Now" movies={trendingMovies.length > 0 ? trendingMovies : movies.slice(0, 15)} />
          <MovieRow title="⭐ Popular Movies" movies={popularMovies.length > 0 ? popularMovies : movies.slice(10, 25)} />
          <MovieRow title="� Top Rated" movies={topRatedMovies.length > 0 ? topRatedMovies : movies.filter(m => m.rating && m.rating > 8.0).slice(0, 15)} />
          <MovieRow title="� Suggested Movies" movies={movies.slice(2, 17)} />
          {hasSearchHistory && (
            <MovieRow title="� Recently Added" movies={recentlyAddedMovies} />
          )}
        </div>
      </motion.div>
    )
  }
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <div className="px-4 lg:px-8 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold font-poppins text-white mb-2">Search Results for "{searchQuery}"</h2>
            <div className="text-gray-400">
              {movies.length} result{movies.length !== 1 ? "s" : ""} found
            </div>
          </div>
          <button
            onClick={clearSearch}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-8 px-6 lg:px-12 max-w-screen-2xl mx-auto">
        {movies.map((movie, index) => (
          <motion.div
            key={movie.id}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.05 }}
            className="h-full"
          >
            <MovieCard movie={movie} />
          </motion.div>
        ))}
      </div>

      {movies.length === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12 px-4">
          <div className="bg-gray-900/80 backdrop-blur-sm rounded-2xl p-8 max-w-md mx-auto border border-gray-800">
            <div className="text-6xl mb-4 opacity-50">🔍</div>
            <h3 className="text-xl font-semibold text-white mb-2">No results found</h3>
            <p className="text-gray-400">Try searching with different keywords or check the spelling</p>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
