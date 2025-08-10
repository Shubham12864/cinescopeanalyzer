"use client"

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { motion, AnimatePresence } from 'framer-motion'
import { MovieCard } from './movie-card'
import { MovieCardSkeleton } from './movie-card-skeleton'
import { useMovieContext } from '@/contexts/movie-context'
import { cn } from '@/lib/utils'

interface VirtualizedMovieGridProps {
  className?: string
  itemsPerRow?: number
  itemHeight?: number
  containerHeight?: number
  overscan?: number
}

export function VirtualizedMovieGrid({
  className,
  itemsPerRow = 6,
  itemHeight = 400,
  containerHeight = 600,
  overscan = 5
}: VirtualizedMovieGridProps) {
  const { movies, isLoading, error } = useMovieContext()
  const parentRef = useRef<HTMLDivElement>(null)
  
  // Calculate grid rows from flat movie array
  const rows = useMemo(() => {
    const result = []
    for (let i = 0; i < movies.length; i += itemsPerRow) {
      result.push(movies.slice(i, i + itemsPerRow))
    }
    return result
  }, [movies, itemsPerRow])
  
  // Virtual scrolling setup
  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => itemHeight,
    overscan: overscan,
  })
  
  // Handle responsive grid
  const [responsiveItemsPerRow, setResponsiveItemsPerRow] = useState(itemsPerRow)
  
  useEffect(() => {
    const updateLayout = () => {
      if (typeof window !== 'undefined') {
        const width = window.innerWidth
        if (width < 640) setResponsiveItemsPerRow(2)        // sm
        else if (width < 768) setResponsiveItemsPerRow(3)   // md
        else if (width < 1024) setResponsiveItemsPerRow(4)  // lg
        else if (width < 1280) setResponsiveItemsPerRow(5)  // xl
        else setResponsiveItemsPerRow(6)                    // 2xl
      }
    }
    
    updateLayout()
    window.addEventListener('resize', updateLayout)
    return () => window.removeEventListener('resize', updateLayout)
  }, [])
  
  // Memoized row renderer
  const renderRow = useCallback((index: number, row: typeof rows[0]) => {
    return (
      <motion.div
        key={index}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.05 }}
        className="grid gap-4"
        style={{
          gridTemplateColumns: `repeat(${responsiveItemsPerRow}, minmax(0, 1fr))`
        }}
      >
        {row.map((movie, movieIndex) => (
          <MovieCard
            key={movie.id || `movie-${index}-${movieIndex}`}
            movie={movie}
            priority={index < 2} // Prioritize first 2 rows
          />
        ))}
        
        {/* Fill empty slots in last row */}
        {row.length < responsiveItemsPerRow && 
          Array.from({ length: responsiveItemsPerRow - row.length }).map((_, i) => (
            <div key={`empty-${i}`} className="invisible" />
          ))
        }
      </motion.div>
    )
  }, [responsiveItemsPerRow])
  
  // Loading skeleton
  const renderSkeleton = () => (
    <div className="grid gap-4" style={{
      gridTemplateColumns: `repeat(${responsiveItemsPerRow}, minmax(0, 1fr))`
    }}>
      {Array.from({ length: responsiveItemsPerRow * 3 }).map((_, i) => (
        <MovieCardSkeleton key={i} />
      ))}
    </div>
  )
  
  // Error state
  if (error) {
    return (
      <div className={cn("flex items-center justify-center", className)} style={{ height: containerHeight }}>
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
      <div className={cn("flex items-center justify-center", className)} style={{ height: containerHeight }}>
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
    return (
      <div className={cn("space-y-6", className)}>
        {renderSkeleton()}
      </div>
    )
  }
  
  // Virtual scrolled grid
  return (
    <div className={cn("w-full", className)}>
      <div
        ref={parentRef}
        style={{ height: containerHeight, overflow: 'auto' }}
        className="scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800"
      >
        <div
          style={{
            height: `${virtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          <AnimatePresence mode="wait">
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const row = rows[virtualItem.index]
              if (!row) return null
              
              return (
                <div
                  key={virtualItem.key}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${virtualItem.size}px`,
                    transform: `translateY(${virtualItem.start}px)`,
                  }}
                >
                  {renderRow(virtualItem.index, row)}
                </div>
              )
            })}
          </AnimatePresence>
        </div>
      </div>
      
      {/* Show total count */}
      <div className="mt-4 text-center text-gray-400 text-sm">
        Showing {movies.length} movie{movies.length !== 1 ? 's' : ''}
      </div>
    </div>
  )
}

// Export as default for easier imports
export default VirtualizedMovieGrid
