"use client"

import React, { useRef, useState, useEffect } from 'react'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, FreeMode, Mousewheel } from 'swiper/modules'
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EnhancedMovieCard } from './EnhancedMovieCard'

// Import Swiper styles
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/free-mode'

interface Movie {
  id: string
  title: string
  poster: string
  year: number
  rating: number
  runtime?: number
  genre: string[]
  plot?: string
}

interface MovieCarouselProps {
  title: string
  movies: Movie[]
  loading?: boolean
  error?: string
  onMoviePlay?: (movie: Movie) => void
  onMovieInfo?: (movie: Movie) => void
  onViewAll?: () => void
  cardSize?: 'small' | 'medium' | 'large'
  autoHeight?: boolean
  showNavigation?: boolean
  showPagination?: boolean
  spaceBetween?: number
  slidesPerView?: number | 'auto'
  breakpoints?: any
}

const defaultBreakpoints = {
  320: {
    slidesPerView: 2,
    spaceBetween: 10
  },
  640: {
    slidesPerView: 3,
    spaceBetween: 15
  },
  768: {
    slidesPerView: 4,
    spaceBetween: 20
  },
  1024: {
    slidesPerView: 5,
    spaceBetween: 20
  },
  1280: {
    slidesPerView: 6,
    spaceBetween: 25
  },
  1536: {
    slidesPerView: 7,
    spaceBetween: 30
  }
}

export function MovieCarousel({
  title,
  movies,
  loading = false,
  error,
  onMoviePlay,
  onMovieInfo,
  onViewAll,
  cardSize = 'medium',
  autoHeight = false,
  showNavigation = true,
  showPagination = false,
  spaceBetween = 20,
  slidesPerView = 'auto',
  breakpoints = defaultBreakpoints
}: MovieCarouselProps) {
  const [swiper, setSwiper] = useState<any>(null)
  const [isBeginning, setIsBeginning] = useState(true)
  const [isEnd, setIsEnd] = useState(false)
  const prevRef = useRef<HTMLButtonElement>(null)
  const nextRef = useRef<HTMLButtonElement>(null)
  
  // Update navigation state
  useEffect(() => {
    if (swiper) {
      const updateNavigation = () => {
        setIsBeginning(swiper.isBeginning)
        setIsEnd(swiper.isEnd)
      }
      
      swiper.on('slideChange', updateNavigation)
      swiper.on('reachBeginning', () => setIsBeginning(true))
      swiper.on('reachEnd', () => setIsEnd(true))
      swiper.on('fromEdge', () => {
        setIsBeginning(false)
        setIsEnd(false)
      })
      
      // Initial check
      updateNavigation()
      
      return () => {
        swiper.off('slideChange', updateNavigation)
      }
    }
  }, [swiper])
  
  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="flex gap-4 overflow-hidden">
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          key={index}
          className="flex-shrink-0 w-48 h-72 bg-gray-200 dark:bg-gray-800 rounded-lg animate-pulse"
        />
      ))}
    </div>
  )
  
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-48 animate-pulse" />
          <div className="h-8 bg-gray-200 dark:bg-gray-800 rounded w-20 animate-pulse" />
        </div>
        <LoadingSkeleton />
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">{title}</h2>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">
            Failed to load movies: {error}
          </p>
        </div>
      </div>
    )
  }
  
  if (!movies || movies.length === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">{title}</h2>
        <div className="bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-600 dark:text-gray-400">
            No movies available
          </p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-4 relative">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {title}
        </h2>
        {onViewAll && (
          <Button 
            variant="ghost" 
            onClick={onViewAll}
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            View All
          </Button>
        )}
      </div>
      
      {/* Carousel Container */}
      <div className="relative group carousel-container">
        {/* Navigation Buttons */}
        {showNavigation && movies.length > 4 && (
          <>
            <Button
              ref={prevRef}
              variant="secondary"
              size="icon"
              className={`absolute left-2 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full carousel-nav-btn ${
                isBeginning ? 'opacity-0 pointer-events-none' : ''
              }`}
              onClick={() => swiper?.slidePrev()}
              disabled={isBeginning}
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
            
            <Button
              ref={nextRef}
              variant="secondary"
              size="icon"
              className={`absolute right-2 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full carousel-nav-btn ${
                isEnd ? 'opacity-0 pointer-events-none' : ''
              }`}
              onClick={() => swiper?.slideNext()}
              disabled={isEnd}
            >
              <ChevronRight className="w-5 h-5" />
            </Button>
          </>
        )}
        
        {/* Swiper Carousel */}
        <Swiper
          modules={[Navigation, Pagination, FreeMode, Mousewheel]}
          spaceBetween={spaceBetween}
          slidesPerView={slidesPerView}
          freeMode={{
            enabled: true,
            sticky: false,
            momentum: true,
            momentumRatio: 0.8,
            momentumVelocityRatio: 1.4
          }}
          mousewheel={{
            forceToAxis: true,
            sensitivity: 0.5
          }}
          breakpoints={breakpoints}
          navigation={false} // We handle navigation manually
          pagination={showPagination ? {
            clickable: true,
            dynamicBullets: true
          } : false}
          className="!overflow-visible"
          onSwiper={setSwiper}
          style={{
            paddingLeft: '8px',
            paddingRight: '8px'
          }}
        >
          {movies.map((movie, index) => (
            <SwiperSlide key={movie.id || index} className="!w-auto">
              <EnhancedMovieCard
                movie={movie}
                size={cardSize}
                onPlay={onMoviePlay}
                onInfo={onMovieInfo}
                className="mb-2" // Add margin for shadow
              />
            </SwiperSlide>
          ))}
        </Swiper>
        
        {/* Pagination Dots */}
        {showPagination && (
          <div className="flex justify-center mt-4">
            <div className="swiper-pagination" />
          </div>
        )}
      </div>
    </div>
  )
}

export default MovieCarousel