"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, ChevronLeft, ChevronRight } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useMovieContext } from '@/contexts/movie-context'
import { movieApi } from '@/lib/api'
import type { Movie } from '@/types/movie'
import { UnifiedMovieImage } from '@/components/ui/unified-movie-image'

export function PopularMoviesSection() {
  const [popularMovies, setPopularMovies] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)
  const { setSelectedMovie, isBackendConnected, movies } = useMovieContext()
  const router = useRouter()

  useEffect(() => {
    loadPopularMovies()
  }, [isBackendConnected])

  const loadPopularMovies = async () => {
    try {
      setIsLoading(true)
      console.log('🎬 Loading popular movies section...')
      
      // First try to get dedicated popular movies from API
      if (isBackendConnected) {
        try {
          console.log('📡 Fetching popular movies from backend...')
          const movies = await movieApi.getPopularMovies(12)
          if (movies && movies.length > 0) {
            console.log(`✅ Popular movies section loaded ${movies.length} movies`)
            setPopularMovies(movies)
          } else {
            console.log('⚠️ No popular movies returned, falling back to context movies')
            // Fallback to movies from context if available
            setPopularMovies(movies.slice(0, 12))
          }
        } catch (error) {
          console.warn('⚠️ Popular movies API failed, using context movies:', error)
          // Use movies from context as fallback
          setPopularMovies(movies.slice(0, 12))
        }
      } else {
        console.log('⚠️ Backend not connected, using context movies for popular section')
        // Use movies from context
        setPopularMovies(movies.slice(0, 12))
      }
    } catch (error) {
      console.error('❌ Error in popular movies section:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMovieClick = (movie: Movie) => {
    setSelectedMovie(movie)
    router.push(`/movies/${movie.id}`)
  }

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % Math.max(1, popularMovies.length - 5))
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + Math.max(1, popularMovies.length - 5)) % Math.max(1, popularMovies.length - 5))
  }

  const visibleMovies = popularMovies.slice(currentIndex, currentIndex + 6)

  if (isLoading) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="w-6 h-6 text-orange-500" />
          <h2 className="text-2xl font-bold text-white">Popular Movies</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-gray-800 animate-pulse rounded-lg" />
          ))}
        </div>
      </section>
    )
  }

  if (!popularMovies.length) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="w-6 h-6 text-orange-500" />
          <h2 className="text-2xl font-bold text-white">Popular Movies</h2>
        </div>
        <p className="text-gray-400">No popular movies available at the moment.</p>
      </section>
    )
  }

  return (
    <section className="py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-orange-500" />
          <h2 className="text-2xl font-bold text-white">Popular Movies</h2>
          <span className="text-sm text-gray-400">({popularMovies.length} movies)</span>
        </div>
        
        {popularMovies.length > 6 && (
          <div className="flex items-center gap-2">
            <button
              onClick={prevSlide}
              className="p-2 rounded-full bg-gray-800 hover:bg-gray-700 transition-colors"
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={nextSlide}
              className="p-2 rounded-full bg-gray-800 hover:bg-gray-700 transition-colors"
              disabled={currentIndex >= popularMovies.length - 6}
            >
              <ChevronRight className="w-5 h-5 text-white" />
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {visibleMovies.map((movie, index) => (
          <motion.div
            key={movie.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group cursor-pointer"
            onClick={() => handleMovieClick(movie)}
          >
            <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-800">
              <UnifiedMovieImage
                src={(() => {
                  // Ensure proper image proxy handling for popular movies
                  if (movie.poster && movie.poster !== "N/A") {
                    if (movie.poster.includes('/api/movies/image-proxy') || movie.poster.startsWith('http://localhost:8000/api/movies/image-proxy')) {
                      return movie.poster
                    }
                    if (movie.poster.includes('m.media-amazon.com')) {
                      return `http://localhost:8000/api/movies/image-proxy?url=${encodeURIComponent(movie.poster)}`
                    }
                    return movie.poster
                  }
                  return movie.omdbPoster || null
                })()}
                alt={movie.title}
                fill
                className="object-cover transition-transform duration-300 group-hover:scale-105"
              />
              
              {/* Overlay */}
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                <div className="text-center p-4">
                  <h3 className="text-white font-semibold text-sm mb-1 line-clamp-2">
                    {movie.title}
                  </h3>
                  <p className="text-gray-300 text-xs">{movie.year}</p>
                  {movie.rating && (
                    <div className="flex items-center justify-center gap-1 mt-2">
                      <span className="text-yellow-400 text-xs">★</span>
                      <span className="text-white text-xs">{movie.rating}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="mt-2">
              <h3 className="text-white text-sm font-medium line-clamp-1 group-hover:text-orange-500 transition-colors">
                {movie.title}
              </h3>
              <p className="text-gray-400 text-xs">{movie.year}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
