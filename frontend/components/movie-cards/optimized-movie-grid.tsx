"use client"

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MovieCard } from './movie-card'
import { MovieCardSkeleton } from './movie-card-skeleton'
import { useMovieContext } from '@/contexts/movie-context'
import { cn } from '@/lib/utils'

interface OptimizedMovieGridProps {
  className?: string
  itemsPerPage?: number
  enablePagination?: boolean
}

export function OptimizedMovieGrid({
  className,
  itemsPerPage = 24,
  enablePagination = true
}: OptimizedMovieGridProps) {
  const { movies, isLoading, error } = useMovieContext()
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerRow, setItemsPerRow] = useState(6)
  
  // Handle responsive grid
  useEffect(() => {
    const updateLayout = () => {
      if (typeof window !== 'undefined') {
        const width = window.innerWidth
        if (width < 640) setItemsPerRow(2)        // sm
        else if (width < 768) setItemsPerRow(3)   // md
        else if (width < 1024) setItemsPerRow(4)  // lg
        else if (width < 1280) setItemsPerRow(5)  // xl
        else setItemsPerRow(6)                    // 2xl
      }
    }
    
    updateLayout()
    window.addEventListener('resize', updateLayout)
    return () => window.removeEventListener('resize', updateLayout)
  }, [])
  
  // Paginated movies
  const paginatedMovies = useMemo(() => {
    if (!enablePagination) return movies
    
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    return movies.slice(startIndex, endIndex)
  }, [movies, currentPage, itemsPerPage, enablePagination])
  
  // Total pages
  const totalPages = useMemo(() => {
    if (!enablePagination) return 1
    return Math.ceil(movies.length / itemsPerPage)
  }, [movies.length, itemsPerPage, enablePagination])
  
  // Reset page when movies change
  useEffect(() => {
    setCurrentPage(1)
  }, [movies])
  
  // Memoized movie cards
  const movieCards = useMemo(() => {
    return paginatedMovies.map((movie, index) => (
      <motion.div
        key={movie.id || `movie-${index}`}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ 
          duration: 0.2, 
          delay: index * 0.02,
          ease: "easeOut"
        }}
        layout
      >
        <MovieCard movie={movie} />
      </motion.div>
    ))
  }, [paginatedMovies])
  
  // Loading skeleton
  const renderSkeleton = useCallback(() => (
    <div className={cn("grid gap-4", className)} style={{
      gridTemplateColumns: `repeat(${itemsPerRow}, minmax(0, 1fr))`
    }}>
      {Array.from({ length: itemsPerPage }).map((_, i) => (
        <MovieCardSkeleton key={i} />
      ))}
    </div>
  ), [itemsPerRow, itemsPerPage, className])
  
  // Pagination controls
  const renderPagination = () => {
    if (!enablePagination || totalPages <= 1) return null
    
    const pages = []
    const maxVisiblePages = 5
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2))
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)
    
    if (endPage - startPage < maxVisiblePages - 1) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1)
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }
    
    return (
      <div className="flex justify-center items-center gap-2 mt-8">
        <button
          onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="px-3 py-2 rounded bg-gray-800 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
        >
          Previous
        </button>
        
        {startPage > 1 && (
          <>
            <button
              onClick={() => setCurrentPage(1)}
              className="px-3 py-2 rounded bg-gray-800 text-white hover:bg-gray-700 transition-colors"
            >
              1
            </button>
            {startPage > 2 && <span className="text-gray-400">...</span>}
          </>
        )}
        
        {pages.map(page => (
          <button
            key={page}
            onClick={() => setCurrentPage(page)}
            className={cn(
              "px-3 py-2 rounded transition-colors",
              page === currentPage
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-white hover:bg-gray-700"
            )}
          >
            {page}
          </button>
        ))}
        
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="text-gray-400">...</span>}
            <button
              onClick={() => setCurrentPage(totalPages)}
              className="px-3 py-2 rounded bg-gray-800 text-white hover:bg-gray-700 transition-colors"
            >
              {totalPages}
            </button>
          </>
        )}
        
        <button
          onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          className="px-3 py-2 rounded bg-gray-800 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
        >
          Next
        </button>
      </div>
    )
  }
  
  // Error state
  if (error) {
    return (
      <div className={cn("flex items-center justify-center min-h-96", className)}>
        <div className="text-center p-8">
          <div className="text-red-500 text-xl mb-2">⚠️ Error</div>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    )
  }
  
  // Empty state
  if (!isLoading && movies.length === 0) {
    return (
      <div className={cn("flex items-center justify-center min-h-96", className)}>
        <div className="text-center p-8">
          <div className="text-gray-500 text-6xl mb-4">🎬</div>
          <h3 className="text-xl text-white mb-2">No movies found</h3>
          <p className="text-gray-400">Try adjusting your search or filters</p>
        </div>
      </div>
    )
  }
  
  // Loading state
  if (isLoading) {
    return renderSkeleton()
  }
  
  // Main grid
  return (
    <div className="w-full">
      <div
        className={cn("grid gap-4", className)}
        style={{
          gridTemplateColumns: `repeat(${itemsPerRow}, minmax(0, 1fr))`
        }}
      >
        <AnimatePresence mode="popLayout">
          {movieCards}
        </AnimatePresence>
      </div>
      
      {/* Pagination */}
      {renderPagination()}
      
      {/* Results info */}
      <div className="mt-4 text-center text-gray-400 text-sm">
        {enablePagination ? (
          <>
            Showing {(currentPage - 1) * itemsPerPage + 1}-{Math.min(currentPage * itemsPerPage, movies.length)} of {movies.length} movies
          </>
        ) : (
          <>
            Showing {movies.length} movie{movies.length !== 1 ? 's' : ''}
          </>
        )}
      </div>
    </div>
  )
}

// Export as default for easier imports
export default OptimizedMovieGrid
