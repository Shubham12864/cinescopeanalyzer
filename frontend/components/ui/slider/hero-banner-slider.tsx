'use client'

import React, { useState, useRef } from 'react'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Autoplay, EffectFade, A11y } from 'swiper/modules'
import { Swiper as SwiperType } from 'swiper/types'
import { motion } from 'framer-motion'
import { Play, Info, Star, Calendar, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SliderMovie } from './movie-slider'
import { FloatingArrows, SliderPagination } from './slider-controls'
import { SLIDER_PRESETS } from './slider-config'

// Import Swiper styles
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/effect-fade'

export interface HeroBannerSliderProps {
  movies: SliderMovie[]
  autoplay?: boolean
  autoplayDelay?: number
  onMovieClick?: (movie: SliderMovie) => void
  onPlayClick?: (movie: SliderMovie) => void
  onInfoClick?: (movie: SliderMovie) => void
  className?: string
  showOverlay?: boolean
  showMetadata?: boolean
  overlayOpacity?: number
}

export const HeroBannerSlider: React.FC<HeroBannerSliderProps> = ({
  movies = [],
  autoplay = true,
  autoplayDelay = 8000,
  onMovieClick,
  onPlayClick,
  onInfoClick,
  className = '',
  showOverlay = true,
  showMetadata = true,
  overlayOpacity = 0.7
}) => {
  const swiperRef = useRef<SwiperType>()
  const [isBeginning, setIsBeginning] = useState(true)
  const [isEnd, setIsEnd] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(autoplay)

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

  // Autoplay control
  const toggleAutoplay = () => {
    if (swiperRef.current) {
      if (isPlaying) {
        swiperRef.current.autoplay.stop()
      } else {
        swiperRef.current.autoplay.start()
      }
      setIsPlaying(!isPlaying)
    }
  }

  // Format runtime
  const formatRuntime = (minutes?: number) => {
    if (!minutes) return ''
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
  }

  // Format release date
  const formatReleaseDate = (dateString?: string) => {
    if (!dateString) return ''
    try {
      return new Date(dateString).getFullYear().toString()
    } catch {
      return ''
    }
  }

  // Get movie backdrop image
  const getBackdropImage = (movie: SliderMovie) => {
    return movie.backdrop_path || movie.fanart_url || movie.poster_path || movie.poster || '/placeholder-backdrop.jpg'
  }

  if (!movies.length) {
    return (
      <div className={cn('relative h-[70vh] bg-gray-900 flex items-center justify-center', className)}>
        <p className="text-gray-400">No featured movies available</p>
      </div>
    )
  }

  const config = {
    ...SLIDER_PRESETS.heroBanner,
    autoplay: autoplay ? {
      delay: autoplayDelay,
      disableOnInteraction: false,
      pauseOnMouseEnter: true
    } : false
  }

  return (
    <div className={cn('relative w-full h-[70vh] overflow-hidden', className)}>
      <Swiper
        modules={[Navigation, Pagination, Autoplay, EffectFade, A11y]}
        onSwiper={handleSwiperInit}
        onSlideChange={handleSlideChange}
        className="hero-banner-slider h-full"
        {...config}
      >
        {movies.map((movie, index) => (
          <SwiperSlide key={movie.id} className="relative">
            {/* Background Image */}
            <div className="absolute inset-0">
              <img
                src={getBackdropImage(movie)}
                alt={movie.title}
                className="h-full w-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement
                  target.src = '/placeholder-backdrop.jpg'
                }}
              />
              
              {/* Gradient Overlay */}
              {showOverlay && (
                <div 
                  className="absolute inset-0 bg-gradient-to-r from-black via-black/50 to-transparent"
                  style={{ 
                    background: `linear-gradient(to right, rgba(0,0,0,${overlayOpacity}), rgba(0,0,0,${overlayOpacity * 0.7}) 50%, transparent)` 
                  }}
                />
              )}
            </div>

            {/* Content */}
            <div className="relative z-10 flex h-full items-center">
              <div className="container mx-auto px-4 lg:px-8">
                <div className="max-w-2xl">
                  <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="space-y-6"
                  >
                    {/* Title */}
                    <h1 className="text-4xl font-bold text-white lg:text-6xl">
                      {movie.title}
                    </h1>

                    {/* Metadata */}
                    {showMetadata && (
                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-300">
                        {(movie.vote_average || movie.rating) && (
                          <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="font-medium text-white">
                              {(movie.vote_average || movie.rating)?.toFixed(1)}
                            </span>
                          </div>
                        )}
                        
                        {(movie.release_date || movie.year) && (
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            <span>{formatReleaseDate(movie.release_date) || movie.year}</span>
                          </div>
                        )}
                        
                        {movie.runtime && (
                          <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            <span>{formatRuntime(movie.runtime)}</span>
                          </div>
                        )}

                        {(movie.genres || movie.genre) && (
                          <div className="flex gap-2">
                            {((movie.genres && movie.genres.length > 0) ? movie.genres.slice(0, 3) : 
                              (movie.genre && movie.genre.length > 0) ? movie.genre.slice(0, 3).map((g, i) => ({ id: i, name: g })) : []
                            ).map((genre) => (
                              <span
                                key={genre.id || genre.name}
                                className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm"
                              >
                                {genre.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Overview */}
                    {(movie.overview || movie.plot) && (
                      <p className="max-w-xl text-lg leading-relaxed text-gray-200 line-clamp-3">
                        {movie.overview || movie.plot}
                      </p>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-4">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => onPlayClick?.(movie)}
                        className="flex items-center gap-2 rounded-lg bg-white px-6 py-3 font-semibold text-black transition-colors hover:bg-gray-200"
                      >
                        <Play className="h-5 w-5 fill-current" />
                        Play Now
                      </motion.button>
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => onInfoClick?.(movie)}
                        className="flex items-center gap-2 rounded-lg bg-gray-600/80 px-6 py-3 font-semibold text-white backdrop-blur-sm transition-colors hover:bg-gray-600"
                      >
                        <Info className="h-5 w-5" />
                        More Info
                      </motion.button>
                    </div>
                  </motion.div>
                </div>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* Floating Navigation Arrows */}
      <FloatingArrows
        onPrev={goToPrev}
        onNext={goToNext}
        isBeginning={isBeginning}
        isEnd={isEnd}
        variant="large"
        showOnHover={true}
      />

      {/* Custom Pagination */}
      <div className="absolute bottom-8 left-1/2 z-20 -translate-x-1/2">
        <SliderPagination
          totalSlides={movies.length}
          currentSlide={activeIndex}
          onSlideClick={goToSlide}
          variant="lines"
        />
      </div>

      {/* Autoplay Control */}
      {autoplay && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={toggleAutoplay}
          className="absolute bottom-8 right-8 z-20 flex h-10 w-10 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-sm transition-colors hover:bg-black/70"
          title={isPlaying ? 'Pause autoplay' : 'Resume autoplay'}
        >
          {isPlaying ? (
            <div className="flex gap-1">
              <div className="h-3 w-1 bg-white rounded"></div>
              <div className="h-3 w-1 bg-white rounded"></div>
            </div>
          ) : (
            <Play className="h-4 w-4 fill-current ml-0.5" />
          )}
        </motion.button>
      )}

      {/* Movie Counter */}
      <div className="absolute top-8 right-8 z-20 rounded-full bg-black/50 px-3 py-1 text-sm text-white backdrop-blur-sm">
        {activeIndex + 1} / {movies.length}
      </div>
    </div>
  )
}
