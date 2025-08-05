'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { MovieSlider, SliderMovie } from '@/components/ui/slider/movie-slider'
import { MovieCardSkeleton } from '@/components/movie-cards/movie-card-skeleton'

interface MovieRowSliderProps {
  title: string
  subtitle?: string
  movies: SliderMovie[]
  isLoading?: boolean
  error?: string
  preset?: 'movieRow' | 'popular' | 'topRated' | 'recent' | 'related'
  customConfig?: any
  showNavigation?: boolean
  showPagination?: boolean
  showScrollbar?: boolean
  autoplay?: boolean
  className?: string
  onMovieClick?: (movie: SliderMovie) => void
  onMovieHover?: (movie: SliderMovie | null) => void
  renderSlide?: (movie: SliderMovie, index: number) => React.ReactNode
  emptyMessage?: string
}

export const MovieRowSlider: React.FC<MovieRowSliderProps> = ({
  title,
  subtitle,
  movies = [],
  isLoading = false,
  error,
  preset = 'movieRow',
  customConfig = {},
  showNavigation = true,
  showPagination = false,
  showScrollbar = false,
  autoplay = false,
  className = 'mb-12',
  onMovieClick,
  onMovieHover,
  renderSlide,
  emptyMessage = 'No movies available'
}) => {
  
  // Loading state with skeletons
  if (isLoading) {
    return (
      <div className={className}>
        <div className="px-4 lg:px-8 mb-6">
          <div className="h-8 w-48 bg-gray-700 animate-pulse rounded mb-2"></div>
          {subtitle && <div className="h-4 w-32 bg-gray-600 animate-pulse rounded"></div>}
        </div>
        
        <div className="flex gap-4 px-4 lg:px-8 overflow-hidden">
          {Array.from({ length: 15 }).map((_, index) => (
            <div key={index} className="flex-shrink-0 w-64">
              <MovieCardSkeleton delay={index * 30} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={className}>
        <div className="px-4 lg:px-8 mb-6">
          <h2 className="text-2xl font-bold text-white font-poppins">{title}</h2>
          {subtitle && <p className="text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className="px-4 lg:px-8">
          <div className="flex items-center justify-center p-8 text-red-400 bg-red-900/20 rounded-lg">
            <p>Error loading movies: {error}</p>
          </div>
        </div>
      </div>
    )
  }

  // Empty state
  if (!movies.length) {
    return (
      <div className={className}>
        <div className="px-4 lg:px-8 mb-6">
          <h2 className="text-2xl font-bold text-white font-poppins">{title}</h2>
          {subtitle && <p className="text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className="px-4 lg:px-8">
          <div className="flex items-center justify-center p-8 text-gray-400 bg-gray-900/20 rounded-lg">
            <p>{emptyMessage}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={className}
    >
      <MovieSlider
        movies={movies}
        title={title}
        subtitle={subtitle}
        preset={preset}
        customConfig={customConfig}
        showNavigation={showNavigation}
        showPagination={showPagination}
        showScrollbar={showScrollbar}
        autoplay={autoplay}
        onMovieClick={onMovieClick}
        onMovieHover={onMovieHover}
        renderSlide={renderSlide}
        emptyMessage={emptyMessage}
      />
    </motion.div>
  )
}

// Enhanced MovieRow that supports both legacy and new slider modes
interface EnhancedMovieRowProps extends MovieRowSliderProps {
  useSlider?: boolean // Toggle between old scrolling and new slider
}

export const EnhancedMovieRow: React.FC<EnhancedMovieRowProps> = ({
  useSlider = true,
  ...props
}) => {
  if (useSlider) {
    return <MovieRowSlider {...props} />
  }

  // Fallback to original MovieRow implementation
  const { MovieRow } = require('../../movie-cards/movie-row')
  return <MovieRow title={props.title} movies={props.movies} isLoading={props.isLoading} />
}
