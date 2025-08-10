"use client"

import React, { useState, useEffect, useCallback } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

interface UnifiedMovieImageProps {
  src?: string | null
  alt: string
  className?: string
  priority?: boolean
  fill?: boolean
  width?: number
  height?: number
  fallbackSrc?: string
  loadingClassName?: string
  errorClassName?: string
  onLoadComplete?: () => void
  onError?: () => void
}

export function UnifiedMovieImage({ 
  src, 
  alt, 
  className, 
  priority = false, 
  fill = false,
  width = 300,
  height = 450,
  fallbackSrc,
  loadingClassName,
  errorClassName,
  onLoadComplete,
  onError
}: UnifiedMovieImageProps) {
  const [imageSrc, setImageSrc] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  
  // Maximum retry attempts
  const MAX_RETRIES = 2
  
  // Generate proxy URL to avoid CORS issues
  const generateProxyUrl = useCallback((imageUrl: string): string => {
    if (!imageUrl || imageUrl === 'N/A' || imageUrl === 'null') {
      return ''
    }
    
    // Clean the URL
    const cleanUrl = imageUrl.replace(/\s+/g, '').trim()
    
    // Already proxied?
    if (cleanUrl.includes('/api/movies/image-proxy')) {
      return cleanUrl
    }
    
    // Skip proxy for placeholder URLs
    if (cleanUrl.includes('placeholder.com') || cleanUrl.includes('via.placeholder.com')) {
      return cleanUrl
    }
    
    // Generate proxy URL
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return `${API_BASE}/api/movies/image-proxy?url=${encodeURIComponent(cleanUrl)}`
  }, [])
  
  // Generate fallback placeholder
  const generateFallback = useCallback((movieTitle?: string): string => {
    const title = movieTitle || alt || 'Movie'
    const encodedTitle = encodeURIComponent(title.slice(0, 20))
    return `https://via.placeholder.com/${width}x${height}/1a1a1a/ffffff?text=${encodedTitle}`
  }, [alt, width, height])
  
  // Handle image load success
  const handleLoadComplete = useCallback(() => {
    setIsLoading(false)
    setHasError(false)
    onLoadComplete?.()
  }, [onLoadComplete])
  
  // Handle image load error with retry logic
  const handleError = useCallback(() => {
    console.warn(`Image load failed for: ${imageSrc}`)
    setIsLoading(false)
    
    if (retryCount < MAX_RETRIES) {
      // Retry with different approach
      setTimeout(() => {
        setRetryCount(prev => prev + 1)
        setIsLoading(true)
        setHasError(false)
        
        if (retryCount === 0 && src) {
          // First retry: try original URL without proxy
          setImageSrc(src)
        } else if (retryCount === 1 && fallbackSrc) {
          // Second retry: try fallback URL
          setImageSrc(generateProxyUrl(fallbackSrc))
        }
      }, 500 * (retryCount + 1)) // Exponential backoff
    } else {
      // All retries failed, show placeholder
      setHasError(true)
      setImageSrc(generateFallback())
    }
    
    onError?.()
  }, [imageSrc, retryCount, src, fallbackSrc, generateProxyUrl, generateFallback, onError])
  
  // Initialize image source when src prop changes
  useEffect(() => {
    setRetryCount(0)
    setIsLoading(true)
    setHasError(false)
    
    if (src) {
      setImageSrc(generateProxyUrl(src))
    } else if (fallbackSrc) {
      setImageSrc(generateProxyUrl(fallbackSrc))
    } else {
      setImageSrc(generateFallback())
      setIsLoading(false)
    }
  }, [src, fallbackSrc, generateProxyUrl, generateFallback])
  
  // Base image properties
  const imageProps = {
    src: imageSrc,
    alt: alt || 'Movie poster',
    priority,
    onLoad: handleLoadComplete,
    onError: handleError,
    className: cn(
      "transition-all duration-300",
      isLoading && (loadingClassName || "opacity-50 blur-sm"),
      hasError && (errorClassName || "opacity-75 grayscale"),
      !isLoading && !hasError && "opacity-100",
      className
    ),
  }
  
  // Render with appropriate sizing
  if (fill) {
    return (
      <div className="relative overflow-hidden">
        <Image
          {...imageProps}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
        {isLoading && (
          <div className="absolute inset-0 bg-gray-800 animate-pulse flex items-center justify-center">
            <div className="text-gray-400 text-sm">Loading...</div>
          </div>
        )}
      </div>
    )
  }
  
  return (
    <div className="relative">
      <Image
        {...imageProps}
        width={width}
        height={height}
      />
      {isLoading && (
        <div 
          className="absolute inset-0 bg-gray-800 animate-pulse flex items-center justify-center"
          style={{ width, height }}
        >
          <div className="text-gray-400 text-sm">Loading...</div>
        </div>
      )}
    </div>
  )
}

// Export as default for easier imports
export default UnifiedMovieImage
