"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Info } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useMovieContext } from '@/contexts/movie-context'
import { movieApi } from '@/lib/api'
import { UnifiedMovieImage } from '@/components/ui/unified-movie-image'
import type { Movie } from '@/types/movie'

const SUGGESTED_TITLES = [
  'Game of Thrones',
  'Stranger Things', 
  'Breaking Bad',
  'The Witcher',
  'House of the Dragon',
  'Wednesday',
  'The Crown',
  'Ozark'
]

export function MovieSuggestions() {
  const [suggestions, setSuggestions] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { searchMoviesHandler, setSelectedMovie, isBackendConnected } = useMovieContext()
  const router = useRouter()

  useEffect(() => {
    loadSuggestions()
  }, [isBackendConnected])
  const loadSuggestions = async () => {
    try {
      setIsLoading(true)
      
      if (isBackendConnected) {
        // Try to get suggestions from backend
        const backendSuggestions = await movieApi.getSuggestions(12)
        if (backendSuggestions && backendSuggestions.length > 0) {
          setSuggestions(backendSuggestions.slice(0, 4))
          return
        }
      }

      // Fallback: Try to search for individual titles
      const loadedSuggestions: Movie[] = []
      const shuffled = [...SUGGESTED_TITLES].sort(() => 0.5 - Math.random())
      const selectedTitles = shuffled.slice(0, 4)

      for (const title of selectedTitles) {
        try {
          if (isBackendConnected) {
            const results = await movieApi.searchMovies(title)
            if (results && results.length > 0) {
              loadedSuggestions.push(results[0])
            }
          }
        } catch (error) {
          console.error(`Failed to fetch ${title}:`, error)
        }
      }      // If we didn't get enough from API, add some fallback data with OMDB-style placeholder
      if (loadedSuggestions.length < 4) {
        const fallbackSuggestions = [
          {
            id: 'suggestion-1',
            title: 'Game of Thrones',
            year: 2011,
            poster: 'https://via.placeholder.com/400x600/2c1810/ffffff?text=Game%20of%20Thrones',
            rating: 9.2,
            genre: ['Drama', 'Fantasy', 'Adventure'],
            plot: 'Nine noble families wage war against each other in order to gain control over the mythical land of Westeros.',
            director: 'Various',
            cast: ['Peter Dinklage', 'Lena Headey', 'Emilia Clarke'],
            reviews: [],
            runtime: 57
          },
          {
            id: 'suggestion-2', 
            title: 'Stranger Things',
            year: 2016,
            poster: 'https://via.placeholder.com/400x600/0f1419/ffffff?text=Stranger%20Things',
            rating: 8.7,
            genre: ['Drama', 'Fantasy', 'Horror'],
            plot: 'When a young boy vanishes, a small town uncovers a mystery involving secret experiments and supernatural forces.',
            director: 'The Duffer Brothers',
            cast: ['Millie Bobby Brown', 'Finn Wolfhard', 'Winona Ryder'],
            reviews: [],
            runtime: 51
          },
          {
            id: 'suggestion-3',
            title: 'Breaking Bad', 
            year: 2008,
            poster: 'https://via.placeholder.com/400x600/1e3a1e/ffffff?text=Breaking%20Bad',
            rating: 9.5,
            genre: ['Crime', 'Drama', 'Thriller'],
            plot: 'A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.',
            director: 'Vince Gilligan',
            cast: ['Bryan Cranston', 'Aaron Paul', 'Anna Gunn'],
            reviews: [],            runtime: 47
          },
          {
            id: 'suggestion-4',
            title: 'The Witcher',
            year: 2019,
            poster: 'https://via.placeholder.com/400x600/2d1b2d/ffffff?text=The%20Witcher', 
            rating: 8.2,
            genre: ['Action', 'Adventure', 'Drama'],
            plot: 'Geralt of Rivia, a mutated monster-hunter for hire, journeys toward his destiny in a turbulent world.',
            director: 'Lauren Schmidt',
            cast: ['Henry Cavill', 'Anya Chalotra', 'Freya Allan'],
            reviews: [],
            runtime: 60
          }
        ]

        // Fill remaining slots with fallback data
        const needed = 4 - loadedSuggestions.length
        loadedSuggestions.push(...fallbackSuggestions.slice(0, needed))
      }

      setSuggestions(loadedSuggestions.slice(0, 4))
    } catch (error) {
      console.error('Failed to load suggestions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = async (movie: Movie) => {
    setSelectedMovie(movie)
    
    // Trigger a search to get more data about this movie
    if (isBackendConnected) {
      await searchMoviesHandler(movie.title)
    }
    
    // Navigate to movie details
    router.push(`/movies/${movie.id}`)
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-white mb-6">Suggested for You</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="aspect-[2/3] bg-gray-800/50 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="container mx-auto px-4 py-8"
    >
      <h2 className="text-2xl font-bold text-white mb-6">Suggested for You</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {suggestions.map((movie, index) => (
          <motion.div
            key={movie.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="group cursor-pointer"
            onClick={() => handleSuggestionClick(movie)}
          >
            <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-gray-900">
              <UnifiedMovieImage
                src={movie.poster || '/placeholder.svg?height=600&width=400'}
                alt={movie.title}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                width={300}
                height={450}
              />
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                <div className="flex gap-2">
                  <button className="p-2 bg-white/20 rounded-full backdrop-blur-sm hover:bg-white/30 transition-colors">
                    <Info className="w-5 h-5 text-white" />
                  </button>
                  <button className="p-2 bg-red-600 rounded-full hover:bg-red-700 transition-colors">
                    <Play className="w-5 h-5 text-white" />
                  </button>
                </div>
              </div>
            </div>
            <div className="mt-2">
              <h3 className="text-white font-semibold truncate">{movie.title}</h3>
              <p className="text-gray-400 text-sm">{movie.year} • {movie.genre[0]}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
