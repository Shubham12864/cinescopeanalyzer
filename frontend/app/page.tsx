"use client"

import { motion } from "framer-motion"
import { Navigation } from "@/components/navigation/navigation"
import { Hero } from "@/components/hero/hero"
import { MovieGrid } from "@/components/movie-cards/movie-grid"
import { MovieSuggestions } from "@/components/suggestions/movie-suggestions"
import { PopularMoviesSection } from "@/components/sections/popular-movies-section"
import { TopRatedMoviesSection } from "@/components/sections/top-rated-movies-section"
import { RecentMoviesSection } from "@/components/sections/recent-movies-section"
import { DebugConnection } from "@/components/debug-connection"
import { ImageDebugTest } from "@/components/debug/image-debug-test"
import { ApiResponseTest } from "@/components/debug/api-response-test"
import { BasicImageTest } from "@/components/debug/basic-image-test"
import { ProxyImageTest } from "@/components/debug/proxy-image-test"

export default function HomePage() {
  return (
    <div className="flex min-h-screen bg-black">
      <Navigation />
      <DebugConnection />

      <main className="flex-1 ml-0 lg:ml-64 transition-all duration-300">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="relative"
        >
          {/* Hero Section */}
          <Hero />
          
          {/* Dynamic Movie Sections */}
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

          {/* Debugging Components - Uncomment to use */}
          <ImageDebugTest />
          <ApiResponseTest />
          <BasicImageTest />
          <ProxyImageTest />
        </motion.div>
      </main>
    </div>
  )
}
