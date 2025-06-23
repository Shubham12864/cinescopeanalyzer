"use client"

import { motion } from "framer-motion"
import { Navigation } from "@/components/navigation/navigation"
import { Hero } from "@/components/hero/hero"
import { MovieGrid } from "@/components/movie-cards/movie-grid"
import { MovieSuggestions } from "@/components/suggestions/movie-suggestions"
import { RecentlySearchedSection } from "@/components/RecentlySearchedSection"

export default function HomePage() {
  return (
    <div className="flex min-h-screen bg-black">
      <Navigation />

      <main className="flex-1 ml-0 lg:ml-64 transition-all duration-300">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="relative"
        >          <Hero />
          
          {/* Movie Suggestions */}
          <MovieSuggestions />

          <div className="container mx-auto px-4 py-8">
            {/* Recently Searched Section */}
            <RecentlySearchedSection className="mb-8" />
            
            <MovieGrid />
          </div>
        </motion.div>
      </main>
    </div>
  )
}
