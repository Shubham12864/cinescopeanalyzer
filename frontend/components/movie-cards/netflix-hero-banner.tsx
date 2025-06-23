"use client"

import { motion } from "framer-motion"
import { Info, Star } from "lucide-react"
import Image from "next/image"
import { useEffect, useState } from "react"
import Link from "next/link"

interface FeaturedMovie {
  id: string
  title: string
  description: string
  backdrop: string
  rating: number
  year: number
  genre: string[]
  poster?: string
  plot?: string
}

interface NetflixHeroBannerProps {
  featuredMovie?: FeaturedMovie | null
}

export function NetflixHeroBanner({ featuredMovie }: NetflixHeroBannerProps) {
  const [currentMovie, setCurrentMovie] = useState<FeaturedMovie | null>(null)
  const [movies, setMovies] = useState<FeaturedMovie[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  // Fallback movies for when API fails
  const fallbackMovies: FeaturedMovie[] = [
    {
      id: "trending-1",
      title: "Spider-Man: No Way Home",
      description:
        "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear, forcing Peter to discover what it truly means to be Spider-Man.",
      backdrop: "https://via.placeholder.com/1920x1080/1a1a1a/ffffff?text=Spider-Man%3A%20No%20Way%20Home",
      rating: 8.2,
      year: 2021,
      genre: ["Action", "Adventure", "Fantasy"],
    },
    {
      id: "trending-2", 
      title: "Avengers: Endgame",
      description:
        "After the devastating events of Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos' actions and restore balance to the universe.",
      backdrop: "https://via.placeholder.com/1920x1080/2c1810/ffffff?text=Avengers%3A%20Endgame",
      rating: 8.4,
      year: 2019,
      genre: ["Action", "Adventure", "Drama"],
    },
    {
      id: "trending-3",
      title: "Dune",
      description:
        "Paul Atreides, a brilliant and gifted young man born into a great destiny beyond his understanding, must travel to the most dangerous planet in the universe to ensure the future of his family and his people.",
      backdrop: "https://via.placeholder.com/1920x1080/8B4513/ffffff?text=Dune",
      rating: 8.0,
      year: 2021,
      genre: ["Adventure", "Drama", "Sci-Fi"],
    }
  ]

  // Fetch dynamic movie data
  const fetchFeaturedMovies = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/movies/suggestions?limit=6')
      
      if (!response.ok) {
        throw new Error('Failed to fetch movies')
      }
      
      const data = await response.json()
      
      if (data.success && data.movies && data.movies.length > 0) {
        // Transform API movies to featured movie format
        const transformedMovies: FeaturedMovie[] = data.movies.map((movie: any) => ({
          id: movie.id,
          title: movie.title,
          description: movie.plot || movie.description || `${movie.title} is a ${movie.genre?.join(', ')} movie from ${movie.year}.`,
          backdrop: movie.poster ? `/api/images/proxy?url=${encodeURIComponent(movie.poster)}` : '/placeholder.svg',
          rating: movie.rating || 0,
          year: movie.year || new Date().getFullYear(),
          genre: movie.genre || [],
          poster: movie.poster,
          plot: movie.plot
        }))
        
        setMovies(transformedMovies)
        console.log(`🎬 Loaded ${transformedMovies.length} dynamic featured movies`)
      } else {
        // Use fallback movies
        setMovies(fallbackMovies)
        console.log('📺 Using fallback featured movies')
      }
    } catch (error) {
      console.error('Error fetching featured movies:', error)
      setMovies(fallbackMovies)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (featuredMovie) {
      setCurrentMovie(featuredMovie)
    } else {
      fetchFeaturedMovies()
    }
  }, [featuredMovie])

  useEffect(() => {
    if (movies.length > 0) {
      setCurrentMovie(movies[0])
      
      // Rotate through movies every 8 seconds
      const interval = setInterval(() => {
        setCurrentIndex((prevIndex) => {
          const newIndex = (prevIndex + 1) % movies.length
          setCurrentMovie(movies[newIndex])
          return newIndex
        })
      }, 8000)

      return () => clearInterval(interval)
    }
  }, [movies])

  if (isLoading) {
    return (
      <div className="relative h-[80vh] overflow-hidden bg-gradient-to-r from-gray-900 to-gray-800 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-red-600 border-t-transparent rounded-full"
        />
      </div>
    )
  }

  if (!currentMovie) return null

  return (
    <div className="relative h-[80vh] overflow-hidden">
      <div className="absolute inset-0">
        <Image
          src={currentMovie.backdrop || "/placeholder.svg"}
          alt={currentMovie.title}
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black via-black/50 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
      </div>

      <div className="relative z-10 h-full flex items-center">
        <div className="container mx-auto px-4 lg:px-8">
          <motion.div
            key={currentMovie.id} // Add key to trigger re-animation on movie change
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="max-w-2xl"
          >
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-5xl md:text-7xl font-bold text-white mb-4 font-poppins"
            >
              {currentMovie.title}
            </motion.h1>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="flex items-center gap-4 mb-6"
            >
              <div className="flex items-center gap-1 bg-red-500/20 px-3 py-1 rounded-lg">
                <Star className="w-4 h-4 text-red-400 fill-current" />
                <span className="text-red-400 font-medium">{currentMovie.rating}/10</span>
              </div>
              <span className="text-gray-300">{currentMovie.year}</span>
              <div className="flex gap-2">
                {currentMovie.genre.slice(0, 3).map((g) => (
                  <span key={g} className="text-gray-300 text-sm bg-gray-700/50 px-2 py-1 rounded">
                    {g}
                  </span>
                ))}
              </div>
            </motion.div>            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-lg text-gray-300 mb-8 leading-relaxed max-w-2xl text-justify"
            >
              {(() => {
                const description = currentMovie.description || currentMovie.plot || '';
                if (!description || description === 'No plot available.' || description === 'N/A') {
                  return `Experience ${currentMovie.title}, a compelling ${currentMovie.genre?.[0]?.toLowerCase() || 'story'} from ${currentMovie.year} that will captivate your imagination.`;
                }
                
                // For hero banner, we can show more text (up to 300 characters)
                if (description.length > 300) {
                  const truncated = description.slice(0, 300);
                  const lastPeriod = truncated.lastIndexOf('.');
                  const lastSpace = truncated.lastIndexOf(' ');
                  
                  // Prefer ending at a sentence if possible
                  if (lastPeriod > 200) {
                    return description.slice(0, lastPeriod + 1);
                  } else if (lastSpace > 250) {
                    return `${truncated.slice(0, lastSpace)}...`;
                  }
                  return `${truncated}...`;
                }
                
                return description;
              })()}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="flex gap-4"
            >
              <Link href={`/movies/${currentMovie.id}`}>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center gap-3 bg-red-600 text-white px-10 py-4 rounded-lg font-semibold hover:bg-red-700 transition-colors shadow-lg"
                >
                  <Info className="w-5 h-5" />
                  More Info
                </motion.button>
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Movie rotation indicator */}
      <div className="absolute bottom-6 right-6 flex gap-2">
        {movies.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-colors ${
              index === currentIndex ? 'bg-white' : 'bg-white/30'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
