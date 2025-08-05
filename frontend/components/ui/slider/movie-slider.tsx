'use client'

import React, { useRef, useState, useEffect } from 'react'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Scrollbar, A11y, Autoplay, EffectFade, EffectCube, EffectCoverflow, EffectFlip, EffectCards, FreeMode, Thumbs } from 'swiper/modules'
import { Swiper as SwiperType } from 'swiper/types'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, Play, Info } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SLIDER_PRESETS, SliderConfig, SLIDER_ANIMATIONS, A11Y_SETTINGS, PERFORMANCE_SETTINGS } from './slider-config'
import type { Movie } from '@/types/movie'

// Import Swiper styles
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'
import 'swiper/css/effect-fade'
import 'swiper/css/effect-cube'
import 'swiper/css/effect-coverflow'
import 'swiper/css/effect-flip'
import 'swiper/css/effect-cards'
import 'swiper/css/free-mode'
import 'swiper/css/thumbs'

// Extended Movie interface for slider-specific properties
export interface SliderMovie extends Movie {
  overview?: string
  poster_path?: string
  backdrop_path?: string
  fanart_url?: string
  release_date?: string
  vote_average?: number
  genre_ids?: number[]
  genres?: Array<{ id: number; name: string }>
  images?: Array<{ file_path: string; aspect_ratio: number; height: number; width: number }>
  crew?: Array<{ id: number; name: string; job: string; profile_path?: string }>
}

export interface MovieSliderProps {
  movies: SliderMovie[]
  title?: string
  subtitle?: string
  preset?: keyof typeof SLIDER_PRESETS
  customConfig?: Partial<SliderConfig>
  showNavigation?: boolean
  showPagination?: boolean
  showScrollbar?: boolean
  autoplay?: boolean
  className?: string
  slideClassName?: string
  onMovieClick?: (movie: SliderMovie) => void
  onMovieHover?: (movie: SliderMovie | null) => void
  renderSlide?: (movie: SliderMovie, index: number) => React.ReactNode
  loading?: boolean
  error?: string
  emptyMessage?: string
  thumbsSlider?: SwiperType | null
  isThumbsSlider?: boolean
}

export const MovieSlider: React.FC<MovieSliderProps> = ({
  movies = [],
  title,
  subtitle,
  preset = 'movieRow',
  customConfig = {},
  showNavigation = true,
  showPagination = false,
  showScrollbar = false,
  autoplay = false,
  className = '',
  slideClassName = '',
  onMovieClick,
  onMovieHover,
  renderSlide,
  loading = false,
  error,
  emptyMessage = 'No movies found',
  thumbsSlider,
  isThumbsSlider = false
}) => {
  const swiperRef = useRef<SwiperType>()
  const [isBeginning, setIsBeginning] = useState(true)
  const [isEnd, setIsEnd] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)

  // Get base config from preset and merge with custom config
  const baseConfig = SLIDER_PRESETS[preset] || SLIDER_PRESETS.movieRow
  const config: SliderConfig = {
    ...baseConfig,
    ...customConfig,
    navigation: showNavigation && baseConfig.navigation,
    pagination: showPagination && baseConfig.pagination,
    scrollbar: showScrollbar && baseConfig.scrollbar,
    autoplay: autoplay && baseConfig.autoplay
  }

  // Handle swiper events
  const handleSlideChange = (swiper: SwiperType) => {
    setActiveIndex(swiper.realIndex || swiper.activeIndex)
    setIsBeginning(swiper.isBeginning)
    setIsEnd(swiper.isEnd)
  }

  const handleSwiperInit = (swiper: SwiperType) => {
    swiperRef.current = swiper
    setIsBeginning(swiper.isBeginning)
    setIsEnd(swiper.isEnd)
  }

  // Navigation handlers
  const goToPrev = () => swiperRef.current?.slidePrev()
  const goToNext = () => swiperRef.current?.slideNext()
  const goToSlide = (index: number) => swiperRef.current?.slideTo(index)

  // Get required Swiper modules based on config
  const getModules = () => {
    const modules = [Navigation, Pagination, Scrollbar, A11y, FreeMode]
    
    if (config.autoplay) modules.push(Autoplay)
    if (config.effect === 'fade') modules.push(EffectFade)
    if (config.effect === 'cube') modules.push(EffectCube)
    if (config.effect === 'coverflow') modules.push(EffectCoverflow)
    if (config.effect === 'flip') modules.push(EffectFlip)
    if (config.effect === 'cards') modules.push(EffectCards)
    if (thumbsSlider) modules.push(Thumbs)
    
    return modules
  }

  // Default slide renderer
  const defaultSlideRenderer = (movie: SliderMovie, index: number) => (
    <motion.div
      key={movie.id}
      className={cn(
        'group relative cursor-pointer transition-transform duration-300 hover:scale-105',
        slideClassName
      )}
      onClick={() => onMovieClick?.(movie)}
      onMouseEnter={() => onMovieHover?.(movie)}
      onMouseLeave={() => onMovieHover?.(null)}
      {...SLIDER_ANIMATIONS.slide}
    >
      <div className="relative overflow-hidden rounded-lg bg-gray-800">
        {/* Movie Poster */}
        <div className="aspect-[2/3] w-full">
          <img
            src={movie.fanart_url || movie.poster_path || movie.poster || '/placeholder-movie.jpg'}
            alt={movie.title}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
            loading="lazy"
            onError={(e) => {
              const target = e.target as HTMLImageElement
              target.src = '/placeholder-movie.jpg'
            }}
          />
        </div>

        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <h3 className="mb-2 text-sm font-semibold text-white line-clamp-2">
              {movie.title}
            </h3>
            {(movie.vote_average || movie.rating) && (
              <div className="mb-2 flex items-center gap-1">
                <span className="text-yellow-400">★</span>
                <span className="text-xs text-gray-300">
                  {(movie.vote_average || movie.rating)?.toFixed(1)}
                </span>
              </div>
            )}
            <div className="flex gap-2">
              <button className="flex items-center gap-1 rounded bg-white/20 px-2 py-1 text-xs text-white backdrop-blur-sm transition-colors hover:bg-white/30">
                <Play className="h-3 w-3" />
                Play
              </button>
              <button className="flex items-center gap-1 rounded bg-white/20 px-2 py-1 text-xs text-white backdrop-blur-sm transition-colors hover:bg-white/30">
                <Info className="h-3 w-3" />
                Info
              </button>
            </div>
          </div>
        </div>

        {/* Rating Badge */}
        {(movie.vote_average || movie.rating) && (
          <div className="absolute right-2 top-2 rounded bg-black/60 px-2 py-1 text-xs font-medium text-white backdrop-blur-sm">
            {(movie.vote_average || movie.rating)?.toFixed(1)}
          </div>
        )}
      </div>
    </motion.div>
  )

  if (loading) {
    return (
      <div className={cn('space-y-4', className)}>
        {title && (
          <div className="space-y-1">
            <div className="h-8 w-48 animate-pulse bg-gray-700 rounded"></div>
            {subtitle && <div className="h-4 w-32 animate-pulse bg-gray-600 rounded"></div>}
          </div>
        )}
        <div className="flex gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="aspect-[2/3] w-48 animate-pulse bg-gray-700 rounded-lg flex-shrink-0"></div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn('space-y-4', className)}>
        {title && (
          <div className="space-y-1">
            <h2 className="text-2xl font-bold text-white">{title}</h2>
            {subtitle && <p className="text-gray-400">{subtitle}</p>}
          </div>
        )}
        <div className="flex items-center justify-center p-8 text-red-400 bg-red-900/20 rounded-lg">
          <p>Error: {error}</p>
        </div>
      </div>
    )
  }

  if (!movies.length) {
    return (
      <div className={cn('space-y-4', className)}>
        {title && (
          <div className="space-y-1">
            <h2 className="text-2xl font-bold text-white">{title}</h2>
            {subtitle && <p className="text-gray-400">{subtitle}</p>}
          </div>
        )}
        <div className="flex items-center justify-center p-8 text-gray-400 bg-gray-900/20 rounded-lg">
          <p>{emptyMessage}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('relative space-y-4', className)}>
      {/* Header */}
      {title && (
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h2 className="text-2xl font-bold text-white">{title}</h2>
            {subtitle && <p className="text-gray-400">{subtitle}</p>}
          </div>
          
          {/* Custom Navigation */}
          {showNavigation && !isThumbsSlider && (
            <div className="flex items-center gap-2">
              <button
                onClick={goToPrev}
                disabled={isBeginning}
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border border-gray-600 transition-colors',
                  isBeginning 
                    ? 'cursor-not-allowed border-gray-700 text-gray-500' 
                    : 'hover:border-white hover:text-white text-gray-300'
                )}
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={goToNext}
                disabled={isEnd}
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border border-gray-600 transition-colors',
                  isEnd 
                    ? 'cursor-not-allowed border-gray-700 text-gray-500' 
                    : 'hover:border-white hover:text-white text-gray-300'
                )}
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Swiper */}
      <div className="relative">
        <Swiper
          modules={getModules()}
          onSwiper={handleSwiperInit}
          onSlideChange={handleSlideChange}
          thumbs={thumbsSlider ? { swiper: thumbsSlider } : undefined}
          className={cn('movie-slider', preset)}
          a11y={A11Y_SETTINGS}
          {...PERFORMANCE_SETTINGS}
          {...config}
        >
          <AnimatePresence mode="wait">
            {movies.map((movie, index) => (
              <SwiperSlide key={movie.id} className="!h-auto">
                {renderSlide ? renderSlide(movie, index) : defaultSlideRenderer(movie, index)}
              </SwiperSlide>
            ))}
          </AnimatePresence>
        </Swiper>

        {/* Progress indicator for certain presets */}
        {(preset === 'heroBanner' || preset === 'popular') && (
          <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 gap-2">
            {movies.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={cn(
                  'h-1 rounded-full transition-all duration-300',
                  index === activeIndex 
                    ? 'w-8 bg-white' 
                    : 'w-2 bg-white/50 hover:bg-white/75'
                )}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
