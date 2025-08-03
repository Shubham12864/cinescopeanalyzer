"use client"

import { motion } from "framer-motion"
import { Navigation } from "@/components/navigation/navigation"
import { Hero } from "@/components/hero/hero"
import { MovieGrid } from "@/components/movie-cards/movie-grid"
import { DynamicMovieSections } from "@/components/sections/DynamicMovieSections"
import { useMovieContext } from "@/contexts/movie-context"
import { useRouter } from "next/navigation"

export default function HomePage() {
  const { searchQuery, movies } = useMovieContext()
  const router = useRouter()
  
  // Show search results immediately when user searches
  const hasSearchResults = searchQuery && searchQuery.trim().length > 0

  const handleMoviePlay = (movie: any) => {
    // Navigate to movie details page or open player
    router.push(`/movies/${movie.id}`)
  }

  const handleMovieInfo = (movie: any) => {
    // Navigate to movie details page
    router.push(`/movies/${movie.id}`)
  }

  const handleViewAll = (section: string) => {
    // Navigate to category page
    router.push(`/movies/category/${section}`)
  }

  return (
    <div className="flex min-h-screen bg-black">
      <Navigation />

      <main className="flex-1 ml-0 lg:ml-64 transition-all duration-300">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="relative"
        >
          {/* Hero Section */}
          <Hero />
          
          {/* Search Results Section - Show at TOP when searching */}
          {hasSearchResults ? (
            <div id="search-results" className="container mx-auto px-4 py-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="mb-8"
              >
                <h2 className="text-3xl font-bold text-white mb-2">
                  Search Results for "{searchQuery}"
                </h2>
                <p className="text-gray-400">
                  {movies.length === 0 ? 'No results found' : `Found ${movies.length} movie${movies.length !== 1 ? 's' : ''}`}
                </p>
              </motion.div>
              <MovieGrid />
            </div>
          ) : (
            /* Enhanced Dynamic Movie Sections - Only show when NOT searching */
            <div className="container mx-auto px-4 py-8">
              <DynamicMovieSections
                onMoviePlay={handleMoviePlay}
                onMovieInfo={handleMovieInfo}
                onViewAll={handleViewAll}
              />
              
              {/* All Movies Grid - General movie browsing */}
              <div className="mt-16">
                <h2 className="text-2xl font-bold text-white mb-6">Browse All Movies</h2>
                <MovieGrid />
              </div>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}
