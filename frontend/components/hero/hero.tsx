"use client"

import type React from "react"
import { motion } from "framer-motion"
import { Search } from "lucide-react"
import { useState } from "react"
import { useMovieContext } from "@/contexts/movie-context"
import { ParticleBackground } from "./particle-background"

export function Hero() {
  const [searchInput, setSearchInput] = useState("")
  const { setSearchQuery, searchMoviesHandler, isLoading } = useMovieContext()
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (searchInput.trim()) {
      setSearchQuery(searchInput)
      try {
        // Scroll to search results after searching
        await searchMoviesHandler(searchInput)
        
        // Smooth scroll to results section
        setTimeout(() => {
          const searchResultsSection = document.getElementById('search-results')
          if (searchResultsSection) {
            searchResultsSection.scrollIntoView({ 
              behavior: 'smooth', 
              block: 'start' 
            })
          } else {
            // If no specific section, scroll past hero
            window.scrollTo({ 
              top: window.innerHeight * 0.7, 
              behavior: 'smooth' 
            })
          }
        }, 100)
      } catch (error) {
        console.error('Search failed:', error)
      }
    }
  }

  return (
    <section className="relative min-h-[70vh] flex items-center justify-center overflow-hidden bg-gradient-to-b from-black via-gray-900/50 to-black">
      {/* Particle Background with error boundary */}
      <div className="absolute inset-0">
        <ParticleBackground />
      </div>

      {/* Gradient overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30" />

      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <h1 className="text-5xl sm:text-6xl md:text-8xl font-bold font-poppins mb-6 bg-gradient-to-r from-white via-red-500 to-red-600 bg-clip-text text-transparent drop-shadow-2xl">
            CineAnalyzer
          </h1>

          <p className="text-lg sm:text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed max-w-3xl mx-auto">
            Discover movies and series with AI-powered insights
            <br />
            <span className="text-red-500 font-semibold">Search, analyze, and explore cinema</span>
          </p>
        </motion.div>

        <motion.form
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          onSubmit={handleSearch}
          className="relative max-w-3xl mx-auto"
        >
          <div className="bg-black/80 backdrop-blur-sm rounded-2xl p-2 shadow-2xl border border-red-900/30 hover:border-red-800/50 transition-all duration-300">
            <div className="flex items-center gap-4">
              <Search className="w-6 h-6 text-gray-400 ml-4 flex-shrink-0" />
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search movies, series, actors, directors..."
                className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none text-lg py-4 min-w-0"
                disabled={isLoading}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                disabled={isLoading || !searchInput.trim()}
                className="bg-gradient-to-r from-red-600 to-red-500 text-white px-6 sm:px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-red-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span className="hidden sm:inline">Searching...</span>
                  </div>
                ) : (
                  'Search'
                )}
              </motion.button>
            </div>
          </div>
        </motion.form>

        {/* Additional visual elements */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.8 }}
          className="mt-8 text-gray-500 text-sm"
        >
          <p>Powered by AI • Real-time Analysis • Comprehensive Reviews</p>
        </motion.div>
      </div>
    </section>
  )
}
