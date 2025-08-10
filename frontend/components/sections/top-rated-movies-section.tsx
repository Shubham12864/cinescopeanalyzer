"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Star, ChevronLeft, ChevronRight } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useMovieContext } from '@/contexts/movie-context'
import { movieApi } from '@/lib/api'
import type { Movie } from '@/types/movie'
import { UnifiedMovieImage } from '@/components/ui/unified-movie-image'

export function TopRatedMoviesSection() {
  const [topRatedMovies, setTopRatedMovies] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [currentIndex, setCurrentIndex] = useState(0)
  const { setSelectedMovie, isBackendConnected } = useMovieContext()
  const router = useRouter()

  useEffect(() => {
    loadTopRatedMovies()
  }, [isBackendConnected])

  const loadTopRatedMovies = async () => {
    try {
      setIsLoading(true)
      
      if (isBackendConnected) {
        const movies = await movieApi.getTopRatedMovies(12)
        if (movies && movies.length > 0) {
          setTopRatedMovies(movies)
        }
      }
    } catch (error) {
      console.error('Error loading top rated movies:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMovieClick = (movie: Movie) => {
    setSelectedMovie(movie)
    router.push(`/movies/${movie.id}`)
  }

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % Math.max(1, topRatedMovies.length - 5))
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + Math.max(1, topRatedMovies.length - 5)) % Math.max(1, topRatedMovies.length - 5))
  }

  const visibleMovies = topRatedMovies.slice(currentIndex, currentIndex + 6)

  if (isLoading) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-3 mb-6">
          <Star className="w-6 h-6 text-yellow-500" />
          <h2 className="text-2xl font-bold text-white">Top Rated Movies</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-gray-800 animate-pulse rounded-lg" />
          ))}
        </div>
      </section>
    )
  }

  if (!topRatedMovies.length) {
    return (
      <section className="py-8">
        <div className="flex items-center gap-3 mb-6">
          <Star className="w-6 h-6 text-yellow-500" />
          <h2 className="text-2xl font-bold text-white">Top Rated Movies</h2>
        </div>
        <p className="text-gray-400">No top rated movies available at the moment.</p>
      </section>
    )
  }

  return (
    <section className="py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Star className="w-6 h-6 text-yellow-500" />
          <h2 className="text-2xl font-bold text-white">Top Rated Movies</h2>
          <span className="text-sm text-gray-400">({topRatedMovies.length} movies)</span>
        </div>
        
        {topRatedMovies.length > 6 && (
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
              disabled={currentIndex >= topRatedMovies.length - 6}
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
              
              {/* Rating Badge */}
              {movie.rating && (
                <div className="absolute top-2 right-2 bg-yellow-500 text-black px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                  <Star className="w-3 h-3 fill-current" />
                  {movie.rating}
                </div>
              )}
              
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
              <h3 className="text-white text-sm font-medium line-clamp-1 group-hover:text-yellow-500 transition-colors">
                {movie.title}
              </h3>
              <div className="flex items-center justify-between">
                <p className="text-gray-400 text-xs">{movie.year}</p>
                {movie.rating && (
                  <div className="flex items-center gap-1">
                    <Star className="w-3 h-3 text-yellow-500 fill-current" />
                    <span className="text-yellow-500 text-xs font-medium">{movie.rating}</span>
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
