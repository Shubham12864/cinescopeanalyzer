"use client"

import { motion } from "framer-motion"
import dynamic from "next/dynamic"
import { Suspense, lazy } from "react"
import { Navigation } from "@/components/navigation/navigation"
import { Hero } from "@/components/hero/hero"
import { useMovieContext } from "@/contexts/movie-context"

// Lazy load components that are not immediately visible
const MovieGrid = dynamic(
  () => import("@/components/movie-cards/movie-grid").then(mod => ({ default: mod.MovieGrid })),
  { 
    loading: () => <div className="animate-pulse bg-gray-800 h-96 rounded-lg" />,
    ssr: false 
  }
)

const MovieSuggestions = dynamic(
  () => import("@/components/suggestions/movie-suggestions").then(mod => ({ default: mod.MovieSuggestions })),
  { 
    loading: () => <div className="animate-pulse bg-gray-800 h-64 rounded-lg" />,
    ssr: false 
  }
)

const PopularMoviesSection = dynamic(
  () => import("@/components/sections/popular-movies-section").then(mod => ({ default: mod.PopularMoviesSection })),
  { 
    loading: () => <div className="animate-pulse bg-gray-800 h-96 rounded-lg" />,
    ssr: false 
  }
)

const TopRatedMoviesSection = dynamic(
  () => import("@/components/sections/top-rated-movies-section").then(mod => ({ default: mod.TopRatedMoviesSection })),
  { 
    loading: () => <div className="animate-pulse bg-gray-800 h-96 rounded-lg" />,
    ssr: false 
  }
)

const RecentMoviesSection = dynamic(
  () => import("@/components/sections/recent-movies-section").then(mod => ({ default: mod.RecentMoviesSection })),
  { 
    loading: () => <div className="animate-pulse bg-gray-800 h-96 rounded-lg" />,
    ssr: false 
  }
)

// Loading component for sections
function SectionLoader() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="animate-pulse">
        <div className="h-8 bg-gray-700 rounded mb-4 w-48"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-gray-800 h-64 rounded-lg"></div>
          ))}
        </div>
      </div>
    </div>
  )
}

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
              <Suspense fallback={<SectionLoader />}>
                <MovieSuggestions />
              </Suspense>

              {/* Popular Movies - Most popular movies */}
              <Suspense fallback={<SectionLoader />}>
                <PopularMoviesSection />
              </Suspense>

              {/* Top Rated Movies - Highest rated movies */}
              <Suspense fallback={<SectionLoader />}>
                <TopRatedMoviesSection />
              </Suspense>

              {/* Recent Movies - Latest movies */}
              <Suspense fallback={<SectionLoader />}>
                <RecentMoviesSection />
              </Suspense>
              
              {/* All Movies Grid - General movie browsing */}
              <div className="mt-12">
                <h2 className="text-2xl font-bold text-white mb-6">Browse All Movies</h2>
                <Suspense fallback={<SectionLoader />}>
                  <MovieGrid />
                </Suspense>
              </div>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}
