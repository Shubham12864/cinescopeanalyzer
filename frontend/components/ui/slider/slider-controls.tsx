'use client'

import React from 'react'
import { ChevronLeft, ChevronRight, Play, Pause, RotateCcw, Settings } from 'lucide-react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

export interface SliderControlsProps {
  onPrev?: () => void
  onNext?: () => void
  onPlay?: () => void
  onPause?: () => void
  onReset?: () => void
  onSettings?: () => void
  isPlaying?: boolean
  isBeginning?: boolean
  isEnd?: boolean
  currentSlide?: number
  totalSlides?: number
  showPlayControls?: boolean
  showProgress?: boolean
  showSettings?: boolean
  className?: string
  variant?: 'default' | 'minimal' | 'floating' | 'compact'
  position?: 'top' | 'bottom' | 'center' | 'inline'
}

export const SliderControls: React.FC<SliderControlsProps> = ({
  onPrev,
  onNext,
  onPlay,
  onPause,
  onReset,
  onSettings,
  isPlaying = false,
  isBeginning = false,
  isEnd = false,
  currentSlide = 0,
  totalSlides = 0,
  showPlayControls = false,
  showProgress = false,
  showSettings = false,
  className = '',
  variant = 'default',
  position = 'inline'
}) => {
  const buttonBaseClasses = 'flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/50'
  
  const getVariantClasses = () => {
    switch (variant) {
      case 'minimal':
        return {
          container: 'bg-transparent',
          button: 'h-8 w-8 rounded-full bg-black/40 text-white hover:bg-black/60 backdrop-blur-sm',
          buttonDisabled: 'opacity-30 cursor-not-allowed'
        }
      case 'floating':
        return {
          container: 'bg-black/20 backdrop-blur-md rounded-full border border-white/10',
          button: 'h-10 w-10 rounded-full text-white hover:bg-white/20',
          buttonDisabled: 'opacity-30 cursor-not-allowed'
        }
      case 'compact':
        return {
          container: 'bg-gray-800/80 backdrop-blur-sm rounded-lg border border-gray-700',
          button: 'h-7 w-7 rounded text-gray-300 hover:text-white hover:bg-gray-700',
          buttonDisabled: 'opacity-30 cursor-not-allowed'
        }
      default:
        return {
          container: 'bg-gray-900/90 backdrop-blur-sm rounded-lg border border-gray-700',
          button: 'h-9 w-9 rounded-lg text-gray-300 hover:text-white hover:bg-gray-700',
          buttonDisabled: 'opacity-30 cursor-not-allowed hover:bg-transparent hover:text-gray-300'
        }
    }
  }

  const getPositionClasses = () => {
    switch (position) {
      case 'top':
        return 'absolute top-4 right-4 z-10'
      case 'bottom':
        return 'absolute bottom-4 right-4 z-10'
      case 'center':
        return 'absolute top-1/2 right-4 z-10 -translate-y-1/2'
      default:
        return 'flex items-center justify-end'
    }
  }

  const variantClasses = getVariantClasses()
  const positionClasses = getPositionClasses()

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        positionClasses,
        position !== 'inline' && variantClasses.container,
        className
      )}
    >
      <div className={cn(
        'flex items-center gap-1',
        position === 'inline' && variantClasses.container,
        variant !== 'minimal' && 'p-2'
      )}>
        {/* Play/Pause Controls */}
        {showPlayControls && (
          <>
            <button
              onClick={isPlaying ? onPause : onPlay}
              className={cn(buttonBaseClasses, variantClasses.button)}
              title={isPlaying ? 'Pause autoplay' : 'Start autoplay'}
            >
              {isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </button>
            
            {onReset && (
              <button
                onClick={onReset}
                className={cn(buttonBaseClasses, variantClasses.button)}
                title="Reset to first slide"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
            )}
            
            <div className="mx-1 h-4 w-px bg-gray-600" />
          </>
        )}

        {/* Navigation Controls */}
        <button
          onClick={onPrev}
          disabled={isBeginning}
          className={cn(
            buttonBaseClasses,
            variantClasses.button,
            isBeginning && variantClasses.buttonDisabled
          )}
          title="Previous slide"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>

        <button
          onClick={onNext}
          disabled={isEnd}
          className={cn(
            buttonBaseClasses,
            variantClasses.button,
            isEnd && variantClasses.buttonDisabled
          )}
          title="Next slide"
        >
          <ChevronRight className="h-4 w-4" />
        </button>

        {/* Progress Display */}
        {showProgress && totalSlides > 0 && (
          <>
            <div className="mx-1 h-4 w-px bg-gray-600" />
            <div className="px-2 text-xs text-gray-400 font-medium min-w-[3rem] text-center">
              {currentSlide + 1}/{totalSlides}
            </div>
          </>
        )}

        {/* Settings */}
        {showSettings && onSettings && (
          <>
            <div className="mx-1 h-4 w-px bg-gray-600" />
            <button
              onClick={onSettings}
              className={cn(buttonBaseClasses, variantClasses.button)}
              title="Slider settings"
            >
              <Settings className="h-4 w-4" />
            </button>
          </>
        )}
      </div>
    </motion.div>
  )
}

// Preset configurations for common use cases
export const SLIDER_CONTROL_PRESETS = {
  movieRow: {
    variant: 'default' as const,
    position: 'inline' as const,
    showPlayControls: false,
    showProgress: false,
    showSettings: false
  },
  heroBanner: {
    variant: 'floating' as const,
    position: 'bottom' as const,
    showPlayControls: true,
    showProgress: true,
    showSettings: false
  },
  gallery: {
    variant: 'minimal' as const,
    position: 'top' as const,
    showPlayControls: true,
    showProgress: true,
    showSettings: true
  },
  compact: {
    variant: 'compact' as const,
    position: 'inline' as const,
    showPlayControls: false,
    showProgress: true,
    showSettings: false
  }
}

// Floating navigation arrows for overlay positioning
export interface FloatingArrowsProps {
  onPrev?: () => void
  onNext?: () => void
  isBeginning?: boolean
  isEnd?: boolean
  className?: string
  variant?: 'default' | 'minimal' | 'large'
  showOnHover?: boolean
}

export const FloatingArrows: React.FC<FloatingArrowsProps> = ({
  onPrev,
  onNext,
  isBeginning = false,
  isEnd = false,
  className = '',
  variant = 'default',
  showOnHover = true
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'minimal':
        return 'h-8 w-8 bg-black/40 hover:bg-black/60'
      case 'large':
        return 'h-12 w-12 bg-black/60 hover:bg-black/80'
      default:
        return 'h-10 w-10 bg-black/50 hover:bg-black/70'
    }
  }

  const baseClasses = cn(
    'absolute top-1/2 z-10 -translate-y-1/2 flex items-center justify-center rounded-full text-white backdrop-blur-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/50',
    getVariantClasses(),
    showOnHover && 'opacity-0 group-hover:opacity-100'
  )

  return (
    <div className={cn('absolute inset-0 pointer-events-none', className)}>
      {/* Previous Arrow */}
      <button
        onClick={onPrev}
        disabled={isBeginning}
        className={cn(
          baseClasses,
          'left-4 pointer-events-auto',
          isBeginning && 'opacity-30 cursor-not-allowed hover:bg-black/50'
        )}
        title="Previous slide"
      >
        <ChevronLeft className={variant === 'large' ? 'h-6 w-6' : 'h-5 w-5'} />
      </button>

      {/* Next Arrow */}
      <button
        onClick={onNext}
        disabled={isEnd}
        className={cn(
          baseClasses,
          'right-4 pointer-events-auto',
          isEnd && 'opacity-30 cursor-not-allowed hover:bg-black/50'
        )}
        title="Next slide"
      >
        <ChevronRight className={variant === 'large' ? 'h-6 w-6' : 'h-5 w-5'} />
      </button>
    </div>
  )
}

// Custom pagination dots
export interface SliderPaginationProps {
  totalSlides: number
  currentSlide: number
  onSlideClick: (index: number) => void
  className?: string
  variant?: 'dots' | 'lines' | 'thumbnails'
  showLabels?: boolean
}

export const SliderPagination: React.FC<SliderPaginationProps> = ({
  totalSlides,
  currentSlide,
  onSlideClick,
  className = '',
  variant = 'dots',
  showLabels = false
}) => {
  const getDotClasses = (index: number, isActive: boolean) => {
    const baseClasses = 'transition-all duration-300 cursor-pointer'
    
    switch (variant) {
      case 'lines':
        return cn(
          baseClasses,
          'h-1 rounded-full',
          isActive ? 'w-8 bg-white' : 'w-4 bg-white/50 hover:bg-white/75'
        )
      case 'thumbnails':
        return cn(
          baseClasses,
          'h-2 w-8 rounded-full',
          isActive ? 'bg-white' : 'bg-white/50 hover:bg-white/75'
        )
      default:
        return cn(
          baseClasses,
          'rounded-full',
          isActive 
            ? 'h-3 w-3 bg-white' 
            : 'h-2 w-2 bg-white/50 hover:bg-white/75 hover:h-3 hover:w-3'
        )
    }
  }

  return (
    <div className={cn('flex items-center justify-center gap-2', className)}>
      {Array.from({ length: totalSlides }).map((_, index) => (
        <button
          key={index}
          onClick={() => onSlideClick(index)}
          className={getDotClasses(index, index === currentSlide)}
          title={showLabels ? `Go to slide ${index + 1}` : undefined}
        />
      ))}
    </div>
  )
}
