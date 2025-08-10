"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Clock, X, Search } from 'lucide-react'
import Image from 'next/image'
import { useRecentlySearched } from '@/hooks/useRecentlySearched'
import { useMovieContext } from '@/contexts/movie-context'

interface RecentlySearchedSectionProps {
  className?: string
}

export function RecentlySearchedSection({ className = '' }: RecentlySearchedSectionProps) {
  const { 
    recentlySearched, 
    removeRecentlySearched, 
    clearRecentlySearched, 
    hasRecentSearches 
  } = useRecentlySearched()
  
  const { setSearchQuery, searchMoviesHandler } = useMovieContext()

  if (!hasRecentSearches) {
    return null
  }

  const handleSearchAgain = (query: string) => {
    setSearchQuery(query)
    searchMoviesHandler(query)
  }

  return (
    <motion.section 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-gradient-to-r from-gray-900/50 to-black/50 backdrop-blur-sm rounded-xl p-6 border border-gray-800/50 ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-red-500" />
          <h2 className="text-xl font-semibold text-white">Recently Searched</h2>
        </div>
        <button
          onClick={clearRecentlySearched}
          className="text-gray-400 hover:text-white transition-colors text-sm"
        >
          Clear All
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {recentlySearched.map((item, index) => (
          <motion.div
            key={`${item.query}-${item.timestamp}`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="group relative bg-black/40 rounded-lg p-4 border border-gray-700/50 hover:border-red-500/50 transition-all duration-200 cursor-pointer"
            onClick={() => handleSearchAgain(item.query)}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Search className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <p className="text-white font-medium truncate group-hover:text-red-400 transition-colors">
                    {item.query}
                  </p>
                </div>
                  {item.movie && (
                  <div className="flex items-center gap-2">
                    {item.movie.poster && (
                      <Image 
                        src={item.movie.poster} 
                        alt={item.movie.title}
                        width={32}
                        height={48}
                        className="object-cover rounded"
                      />
                    )}
                    <div className="min-w-0">
                      <p className="text-sm text-gray-300 truncate">
                        {item.movie.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {item.movie.year} • {item.movie.genre?.slice(0, 2).join(', ')}
                      </p>
                    </div>
                  </div>
                )}
                
                <p className="text-xs text-gray-500 mt-2">
                  {new Date(item.timestamp).toLocaleDateString()}
                </p>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation()
                  removeRecentlySearched(item.query)
                }}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-400 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Hover effect overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-lg pointer-events-none" />
          </motion.div>
        ))}
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          Click any item to search again • {recentlySearched.length} recent searches
        </p>
      </div>
    </motion.section>
  )
}
