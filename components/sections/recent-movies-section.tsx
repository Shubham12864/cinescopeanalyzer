"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Clock, ChevronLeft, ChevronRight } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useMovieContext } from '@/contexts/movie-context'
import { movieApi } from '@/lib/api'
import type { Movie } from '@/types/movie'
import { UnifiedMovieImage } from '@/components/ui/unified-movie-image'

export function RecentMoviesSection() {
  const [recentMovies, setRecentMovies] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)
  const { setSelectedMovie, isBackendConnected } = useMovieContext()
  const router = useRouter()

  useEffect(() => {
    loadRecentMovies()
  }, [isBackendConnected])

  const loadRecentMovies = async () => {
    try {
      setIsLoading(true)
      
      if (isBackendConnected) {
        const movies = await movieApi.getRecentMovies(12)
        if (movies && movies.length > 0) {
          setRecentMovies(movies)
        }
      }
    } catch (error) {
      console.error('Error loading recent movies:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMovieClick = (movie: Movie) => {
    setSelectedMovie(movie)
    router.push(`/movies/${movie.id}`)
  }

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % Math.max(1, recentMovies.length - 5))
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + Math.max(1, recentMovies.length - 5)) % Math.max(1, recentMovies.length - 5))
  }

  const visibleMovies = recentMovies.slice(currentIndex, currentIndex + 6)

  if (isLoading) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-6 h-6 text-blue-500" />
          <h2 className="text-2xl font-bold text-white">Recent Movies</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-gray-800 animate-pulse rounded-lg" />
          ))}
        </div>
      </section>
    )
  }

  if (!recentMovies.length) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-6 h-6 text-blue-500" />
          <h2 className="text-2xl font-bold text-white">Recent Movies</h2>
        </div>
        <p className="text-gray-400">No recent movies available at the moment.</p>
      </section>
    )
  }

  return (
    <section className="py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-blue-500" />
          <h2 className="text-2xl font-bold text-white">Recent Movies</h2>
          <span className="text-sm text-gray-400">({recentMovies.length} movies)</span>
        </div>
        
        {recentMovies.length > 6 && (
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
              disabled={currentIndex >= recentMovies.length - 6}
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
                src={movie.poster}
                alt={movie.title}
                fill
                className="object-cover transition-transform duration-300 group-hover:scale-105"
              />
              
              {/* New Badge for recent movies */}
              <div className="absolute top-2 left-2 bg-blue-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                NEW
              </div>
              
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
              <h3 className="text-white text-sm font-medium line-clamp-1 group-hover:text-blue-500 transition-colors">
                {movie.title}
              </h3>
              <div className="flex items-center justify-between">
                <p className="text-gray-400 text-xs">{movie.year}</p>
                {movie.rating && (
                  <div className="flex items-center gap-1">
                    <span className="text-yellow-400 text-xs">★</span>
                    <span className="text-yellow-500 text-xs">{movie.rating}</span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
