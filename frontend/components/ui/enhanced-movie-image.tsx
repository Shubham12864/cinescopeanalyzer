/**
 * ENHANCED MOVIE IMAGE COMPONENT
 * Works with the new PIL-free backend image proxy
 * Optimized for smooth UI and fast loading
 */
"use client"

import React, { useState, useEffect, useRef, useCallback } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

interface EnhancedMovieImageProps {
  src?: string | null
  alt: string
  className?: string
  priority?: boolean
  fill?: boolean
  width?: number
  height?: number
  fallbackSrc?: string
  onLoad?: () => void
  onError?: () => void
}

export function EnhancedMovieImage({ 
  src, 
  alt, 
  className, 
  priority = false, 
  fill = false,
  width = 300,
  height = 450,
  fallbackSrc,
  onLoad,
  onError
}: EnhancedMovieImageProps) {
  
  // State management for smooth loading
  const [imageState, setImageState] = useState<'loading' | 'loaded' | 'error' | 'skeleton'>('skeleton')
  const [currentSrc, setCurrentSrc] = useState<string>('')
  const [retryCount, setRetryCount] = useState(0)
  const maxRetries = 2
  const imageRef = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  // Enhanced proxy URL generation for new backend
  const generateProxyUrl = useCallback((imageUrl: string): string => {
    try {
      if (!imageUrl || imageUrl === 'N/A') {
        return generatePlaceholder(alt)
      }

      // Clean the URL
      const cleanUrl = imageUrl.trim()
      
      // Avoid double-proxying
      if (cleanUrl.includes('/api/images/image-proxy')) {
        return cleanUrl
      }

      // Skip proxy for placeholder URLs
      if (cleanUrl.includes('placeholder.com') || cleanUrl.includes('via.placeholder')) {
        return cleanUrl
      }

      // Get API base URL
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // Use the enhanced image proxy endpoint
      return `${API_BASE_URL}/api/images/image-proxy?url=${encodeURIComponent(cleanUrl)}`
      
    } catch (error) {
      console.warn('❌ Error generating proxy URL:', error)
      return generatePlaceholder(alt)
    }
  }, [alt])

  // Generate smart placeholder
  const generatePlaceholder = useCallback((title: string) => {
    const encodedTitle = encodeURIComponent(title.slice(0, 20))
    return `https://via.placeholder.com/300x450/1a1a1a/ffffff?text=${encodedTitle}`
  }, [])

  // Intersection Observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
            observer.disconnect()
          }
        })
      },
      { threshold: 0.1, rootMargin: '50px' }
    )

    if (imageRef.current) {
      observer.observe(imageRef.current)
    }

    return () => observer.disconnect()
  }, [])

  // Initialize image loading
  useEffect(() => {
    if (!isVisible && !priority) return

    if (src) {
      const proxyUrl = generateProxyUrl(src)
      setCurrentSrc(proxyUrl)
      setImageState('loading')
    } else {
      const placeholder = fallbackSrc || generatePlaceholder(alt)
      setCurrentSrc(placeholder)
      setImageState('loading')
    }
  }, [src, alt, isVisible, priority, generateProxyUrl, fallbackSrc, generatePlaceholder])

  // Handle image load success
  const handleLoad = useCallback(() => {
    setImageState('loaded')
    setRetryCount(0)
    onLoad?.()
  }, [onLoad])

  // Handle image load error with smart retry
  const handleError = useCallback(() => {
    console.warn(`🖼️ Image failed to load: ${currentSrc}`)
    
    if (retryCount < maxRetries) {
      // Retry with exponential backoff
      setTimeout(() => {
        setRetryCount(prev => prev + 1)
        setImageState('loading')
      }, Math.pow(2, retryCount) * 1000)
      return
    }

    // All retries failed - use fallback
    const fallback = fallbackSrc || generatePlaceholder(alt)
    if (currentSrc !== fallback) {
      setCurrentSrc(fallback)
      setImageState('loading')
      setRetryCount(0)
    } else {
      setImageState('error')
      onError?.()
    }
  }, [currentSrc, retryCount, maxRetries, fallbackSrc, alt, generatePlaceholder, onError])

  // Render skeleton while loading
  if (imageState === 'skeleton' || (!isVisible && !priority)) {
    return (
      <div 
        ref={imageRef}
        className={cn(
          "animate-pulse bg-gray-800 rounded-lg flex items-center justify-center",
          className
        )}
        style={{ width, height }}
      >
        <svg 
          className="w-8 h-8 text-gray-600"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
        </svg>
      </div>
    )
  }

  // Show loading spinner
  if (imageState === 'loading') {
    return (
      <div 
        className={cn(
          "bg-gray-800 rounded-lg flex items-center justify-center relative overflow-hidden",
          className
        )}
        style={{ width, height }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 animate-pulse" />
        <div className="relative z-10">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
        {/* Hidden image to trigger loading */}
        <Image
          src={currentSrc}
          alt={alt}
          width={width}
          height={height}
          className="opacity-0 absolute"
          onLoad={handleLoad}
          onError={handleError}
          priority={priority}
        />
      </div>
    )
  }

  // Show error state
  if (imageState === 'error') {
    return (
      <div 
        className={cn(
          "bg-gray-800 rounded-lg flex items-center justify-center border border-red-500/20",
          className
        )}
        style={{ width, height }}
      >
        <div className="text-center text-gray-400">
          <svg className="w-8 h-8 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <p className="text-xs">Image Error</p>
        </div>
      </div>
    )
  }

  // Show loaded image with smooth transition
  return (
    <div 
      className={cn("relative overflow-hidden rounded-lg transition-opacity duration-300", className)}
      style={{ width, height }}
    >
      <Image
        src={currentSrc}
        alt={alt}
        fill={fill}
        width={fill ? undefined : width}
        height={fill ? undefined : height}
        className={cn(
          "object-cover transition-all duration-300",
          imageState === 'loaded' ? 'opacity-100 scale-100' : 'opacity-0 scale-105'
        )}
        onLoad={handleLoad}
        onError={handleError}
        priority={priority}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
    </div>
  )
}
