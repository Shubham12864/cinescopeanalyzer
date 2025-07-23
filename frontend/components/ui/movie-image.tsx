"use client"

import React, { useState, useEffect, useRef } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { queueImageLoad } from '@/lib/request-queue'

interface MovieImageProps {
  src?: string | null
  alt: string
  className?: string
  priority?: boolean
  fill?: boolean
  width?: number
  height?: number
  fallbackSrc?: string
  loadingPriority?: number // For request queue prioritization
}

export function MovieImage({ 
  src, 
  alt, 
  className, 
  priority = false, 
  fill = false,
  width = 300,
  height = 450,
  fallbackSrc,
  loadingPriority = 0
}: MovieImageProps) {
  // Standardized proxy URL generation
  const generateProxyUrl = (imageUrl: string): string => {
    try {
      // Clean the URL first
      const cleanUrl = imageUrl.replace(/\s+/g, '').trim()
      
      // Check if URL is already a proxy URL to avoid double-proxying
      if (cleanUrl.includes('/api/images/image-proxy') || cleanUrl.includes('/api/movies/image-proxy')) {
        return cleanUrl
      }
      
      // Use the enhanced image proxy service
      return `/api/images/image-proxy?url=${encodeURIComponent(cleanUrl)}`
    } catch (error) {
      console.warn('Error generating proxy URL:', error)
      return imageUrl
    }
  }

  // Generate fallback image with movie title - use backend fallback service
  const generateFallback = (title: string) => {
    const encodedTitle = encodeURIComponent(title.slice(0, 30))
    // Use backend fallback generation instead of external service
    return `/api/images/image-proxy?url=fallback&title=${encodedTitle}`
  }

  const defaultFallback = fallbackSrc || generateFallback(alt || 'Movie')
  
  // Loading states: skeleton -> loading -> image/fallback
  const [loadingState, setLoadingState] = useState<'skeleton' | 'loading' | 'loaded' | 'error'>('skeleton')
  const [imgSrc, setImgSrc] = useState<string>('')
  const [fallbackAttempted, setFallbackAttempted] = useState(false)
  
  const [retryCount, setRetryCount] = useState(0)
  const [retryTimeout, setRetryTimeout] = useState<NodeJS.Timeout | null>(null)
  const maxRetries = 2
  const abortControllerRef = useRef<AbortController | null>(null)
  const [isInViewport, setIsInViewport] = useState(false)
  const imageRef = useRef<HTMLDivElement>(null)

  const handleError = () => {
    console.warn('Image load error for:', imgSrc, 'Retry count:', retryCount)
    
    // Clear any existing retry timeout
    if (retryTimeout) {
      clearTimeout(retryTimeout)
      setRetryTimeout(null)
    }
    
    if (!fallbackAttempted && src && !src.includes('/api/')) {
      // First error from proxy: try direct image loading
      console.log('Proxy failed, trying direct image loading:', src)
      setImgSrc(src)
      setLoadingState('loading')
      setFallbackAttempted(true)
      return
    }
    
    // Retry mechanism for transient failures
    if (retryCount < maxRetries && src && !src.includes('fallback')) {
      console.log(`Retrying image load (${retryCount + 1}/${maxRetries}) for:`, alt)
      
      const timeout = setTimeout(() => {
        setRetryCount(prev => prev + 1)
        setLoadingState('loading')
        // Force reload by adding timestamp
        const retryUrl = src.includes('?') 
          ? `${src}&retry=${Date.now()}` 
          : `${src}?retry=${Date.now()}`
        setImgSrc(retryUrl)
      }, 1000 * (retryCount + 1)) // Exponential backoff
      
      setRetryTimeout(timeout)
      return
    }
    
    // Final fallback: use generated fallback (maintains layout integrity)
    console.log('All image sources failed, using generated fallback for:', alt)
    setImgSrc(defaultFallback)
    setLoadingState('error')
  }

  const handleLoad = () => {
    setLoadingState('loaded')
  }

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!imageRef.current || priority) {
      setIsInViewport(true) // Load immediately if priority or no ref
      return
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInViewport(true)
          observer.disconnect()
        }
      },
      { 
        rootMargin: '50px', // Start loading 50px before entering viewport
        threshold: 0.1 
      }
    )

    observer.observe(imageRef.current)

    return () => {
      observer.disconnect()
    }
  }, [priority])

  // Enhanced image loading with request queue and progressive enhancement
  const loadImageWithQueue = async (imageUrl: string): Promise<void> => {
    try {
      // Cancel any existing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      
      abortControllerRef.current = new AbortController()
      
      // Use request queue for optimized concurrent loading with priority
      const priorityLevel = priority ? 10 : loadingPriority
      await queueImageLoad(imageUrl, priorityLevel)
      
      // Check if request was cancelled
      if (abortControllerRef.current.signal.aborted) {
        return
      }
      
      setImgSrc(imageUrl)
      setLoadingState('loaded')
      
    } catch (error) {
      // Check if error is due to cancellation
      if (abortControllerRef.current?.signal.aborted) {
        return
      }
      
      console.warn('Queued image load failed:', error)
      handleError()
    }
  }

  // Cleanup timeout and abort controller on unmount
  useEffect(() => {
    return () => {
      if (retryTimeout) {
        clearTimeout(retryTimeout)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [retryTimeout])

  // Update image source when src prop changes or when in viewport
  useEffect(() => {
    // Don't start loading until in viewport (unless priority)
    if (!isInViewport && !priority) {
      return
    }

    setFallbackAttempted(false)
    setRetryCount(0)
    
    // Clear any existing retry timeout
    if (retryTimeout) {
      clearTimeout(retryTimeout)
      setRetryTimeout(null)
    }
    
    if (!src || src === 'N/A' || src.includes('placeholder') || src.toLowerCase() === 'null' || src.trim() === '') {
      // Invalid source: use fallback immediately with smooth transition
      setLoadingState('skeleton')
      setImgSrc(defaultFallback)
      
      // Brief skeleton before showing error state for consistency
      setTimeout(() => {
        setLoadingState('error')
      }, 300)
    } else {
      // Valid source: start progressive loading process
      setLoadingState('skeleton')
      
      // Use proxy for external URLs
      const processedSrc = generateProxyUrl(src)
      
      // Progressive loading: skeleton -> loading -> loaded
      setTimeout(() => {
        setLoadingState('loading')
        
        // Use queued loading for better performance
        loadImageWithQueue(processedSrc)
      }, 150) // Brief skeleton display for smooth UX
    }
  }, [src, defaultFallback, alt, retryTimeout, isInViewport, priority, loadingPriority])

  return (
    <div 
      ref={imageRef}
      className={cn("relative overflow-hidden bg-gray-900", className)} 
      style={{ minHeight: fill ? 'auto' : height }}
    >
      {/* Skeleton loading state with enhanced shimmer effect */}
      {loadingState === 'skeleton' && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-700 transition-all duration-500 ease-out">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-600/40 to-transparent animate-shimmer" />
          {/* Subtle movie icon with fade-in */}
          <div className="absolute inset-0 flex items-center justify-center opacity-20 animate-fade-in">
            <div className="text-4xl transition-transform duration-300 hover:scale-110">🎬</div>
          </div>
        </div>
      )}
      
      {/* Loading spinner state with smooth transition and enhanced animation */}
      {loadingState === 'loading' && (
        <div className="absolute inset-0 bg-gray-800 flex items-center justify-center transition-all duration-700 ease-in-out animate-fade-in">
          <div className="relative">
            {/* Primary spinner */}
            <div className="w-12 h-12 border-4 border-red-600/30 border-t-red-600 rounded-full animate-spin" />
            {/* Secondary counter-rotating spinner for visual appeal */}
            <div className="absolute inset-0 w-12 h-12 border-4 border-transparent border-t-red-400 rounded-full animate-spin animate-reverse" style={{ animationDuration: '1.5s' }} />
            {/* Pulsing center dot */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            </div>
          </div>
        </div>
      )}
      
      {/* Image element with progressive enhancement */}
      {imgSrc && (
        <Image
          src={imgSrc}
          alt={alt}
          fill={fill}
          width={!fill ? width : undefined}
          height={!fill ? height : undefined}
          className={cn(
            "transition-all duration-700 ease-out object-cover",
            loadingState === 'loaded' 
              ? "opacity-100 scale-100 blur-0" 
              : "opacity-0 scale-105 blur-sm"
          )}
          priority={priority}
          onError={handleError}
          onLoad={handleLoad}
          unoptimized={imgSrc.includes('fallback') || imgSrc.includes('placeholder') || imgSrc.includes('dummyimage')}
          sizes={fill ? "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw" : undefined}
        />
      )}
      
      {/* Error state with smooth fade-in and enhanced fallback */}
      {loadingState === 'error' && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex flex-col items-center justify-center text-gray-300 transition-all duration-500 ease-in-out animate-fade-in">
          <div className="text-6xl mb-4 opacity-60 transition-all duration-500 hover:scale-110 hover:opacity-80">🎬</div>
          <div className="text-sm text-center px-4 font-medium leading-tight max-w-full overflow-hidden transition-all duration-300">
            <div className="truncate">{alt || 'Movie'}</div>
          </div>
          <div className="text-xs text-gray-500 mt-2 opacity-75 transition-opacity duration-300">No Image Available</div>
        </div>
      )}
    </div>
  )
}
