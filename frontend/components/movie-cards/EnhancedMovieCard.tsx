"use client"

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Info, Star, Clock, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

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

interface EnhancedMovieCardProps {
  movie: Movie
  className?: string
  onPlay?: (movie: Movie) => void
  onInfo?: (movie: Movie) => void
  size?: 'small' | 'medium' | 'large'
}

const sizeConfig = {
  small: {
    width: 200,
    height: 300,
    imageWidth: 200,
    imageHeight: 300
  },
  medium: {
    width: 250,
    height: 375,
    imageWidth: 250,
    imageHeight: 375
  },
  large: {
    width: 300,
    height: 450,
    imageWidth: 300,
    imageHeight: 450
  }
}

export function EnhancedMovieCard({ 
  movie, 
  className = '', 
  onPlay, 
  onInfo,
  size = 'medium'
}: EnhancedMovieCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)
  
  const config = sizeConfig[size]
  
  // Construct image proxy URL for fast loading
  const getProxyImageUrl = (imageUrl: string, imageSize: string = 'w500') => {
    if (!imageUrl) return '/placeholder-movie.jpg'
    
    // If it's already a full URL, proxy it
    if (imageUrl.startsWith('http')) {
      return `/api/images/proxy?url=${encodeURIComponent(imageUrl)}&size=${imageSize}`
    }
    
    // If it's a TMDB path, use the path-based proxy
    return `/api/images/proxy${imageUrl}?size=${imageSize}`
  }
  
  const formatRuntime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
  }
  
  return (
    <motion.div
      className={`relative group cursor-pointer select-none movie-card-hover ${className}`}
      style={{ width: config.width, height: config.height }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.05 }}
    >
      {/* Main Movie Card */}
      <div className="relative w-full h-full rounded-lg overflow-hidden bg-gray-900 shadow-lg border-glow">
        {/* Movie Poster */}
        <div className="relative w-full h-full">
          {!imageError ? (
            <Image
              src={getProxyImageUrl(movie.poster, size === 'small' ? 'w200' : size === 'large' ? 'w780' : 'w500')}
              alt={movie.title}
              fill
              className={`object-cover transition-all duration-300 scale-smooth ${
                imageLoaded ? 'opacity-100 image-fade-in loaded' : 'opacity-0'
              } ${isHovered ? 'scale-110' : 'scale-100'}`}
              onLoad={() => setImageLoaded(true)}
              onError={() => setImageError(true)}
              priority={size === 'large'} // Priority loading for large cards
              sizes={`${config.width}px`}
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
              <div className="text-center text-gray-400">
                <div className="text-4xl mb-2">🎬</div>
                <div className="text-sm font-medium">{movie.title}</div>
              </div>
            </div>
          )}
          
          {/* Loading Skeleton */}
          {!imageLoaded && !imageError && (
            <div className="absolute inset-0 bg-gray-800 shimmer">
              <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-800" />
            </div>
          )}
          
          {/* Rating Badge */}
          <motion.div 
            className="absolute top-2 right-2 backdrop-blur-custom rounded-full px-2 py-1 flex items-center gap-1"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Star className="w-3 h-3 text-yellow-400 fill-current" />
            <span className="text-white text-xs font-medium">
              {movie.rating ? movie.rating.toFixed(1) : 'N/A'}
            </span>
          </motion.div>
          
          {/* Gradient Overlay */}
          <div className="card-overlay" />
        </div>
        
        {/* Hover Info Panel */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              className="absolute inset-x-0 bottom-0 backdrop-blur-custom p-4 text-white"
              initial={{ y: '100%', opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: '100%', opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
            >
              {/* Movie Title */}
              <h3 className="font-bold text-lg mb-2 line-clamp-2 leading-tight text-glow">
                {movie.title}
              </h3>
              
              {/* Movie Details */}
              <div className="flex items-center gap-3 mb-3 text-sm text-gray-300">
                {movie.year && (
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span>{movie.year}</span>
                  </div>
                )}
                {movie.runtime && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatRuntime(movie.runtime)}</span>
                  </div>
                )}
              </div>
              
              {/* Genres */}
              {movie.genre && movie.genre.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {movie.genre.slice(0, 2).map((genre, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="text-xs px-2 py-0.5 glass text-white border-0"
                    >
                      {genre}
                    </Badge>
                  ))}
                  {movie.genre.length > 2 && (
                    <Badge 
                      variant="secondary" 
                      className="text-xs px-2 py-0.5 glass text-white border-0"
                    >
                      +{movie.genre.length - 2}
                    </Badge>
                  )}
                </div>
              )}
              
              {/* Plot */}
              {movie.plot && (
                <p className="text-sm text-gray-300 line-clamp-2 mb-3 movie-description">
                  {movie.plot}
                </p>
              )}
              
              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  className="bg-white text-black hover:bg-gray-200 flex-1 focus-ring"
                  onClick={(e) => {
                    e.stopPropagation()
                    onPlay?.(movie)
                  }}
                >
                  <Play className="w-4 h-4 mr-1 fill-current" />
                  Play
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-white/30 text-white hover:bg-white/10 focus-ring"
                  onClick={(e) => {
                    e.stopPropagation()
                    onInfo?.(movie)
                  }}
                >
                  <Info className="w-4 h-4" />
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {/* Progressive Enhancement: Preload next image size on hover */}
      {isHovered && (
        <link
          rel="prefetch"
          href={getProxyImageUrl(movie.poster, 'w780')}
          as="image"
        />
      )}
    </motion.div>
  )
}

export default EnhancedMovieCard