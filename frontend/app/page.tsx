"use client"

import { motion } from "framer-motion"
import { Navigation } from "@/components/navigation/navigation"
import { Hero } from "@/components/hero/hero"
import { MovieGrid } from "@/components/movie-cards/movie-grid"
import { MovieSuggestions } from "@/components/suggestions/movie-suggestions"
import { PopularMoviesSection } from "@/components/sections/popular-movies-section"
import { TopRatedMoviesSection } from "@/components/sections/top-rated-movies-section"
import { RecentMoviesSection } from "@/components/sections/recent-movies-section"
import { useMovieContext } from "@/contexts/movie-context"

export default function HomePage() {
  const { searchQuery, movies } = useMovieContext()
  
  // Show search results immediately when user searches
  const hasSearchResults = searchQuery && searchQuery.trim().length > 0

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
            /* Default Home Sections - Only show when NOT searching */
            <div className="container mx-auto px-4 py-8 space-y-12">
              {/* Movie Suggestions - Dynamic suggestions that change every minute */}
              <MovieSuggestions />

              {/* Popular Movies - Most popular movies */}
              <PopularMoviesSection />

              {/* Top Rated Movies - Highest rated movies */}
              <TopRatedMoviesSection />

              {/* Recent Movies - Latest movies */}
              <RecentMoviesSection />
              
              {/* All Movies Grid - General movie browsing */}
              <div className="mt-12">
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
