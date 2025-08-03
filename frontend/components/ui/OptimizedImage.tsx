"use client"

import React, { useState, useEffect, useRef } from 'react'
import Image from 'next/image'
import { motion } from 'framer-motion'

interface OptimizedImageProps {
  src: string
  alt: string
  width: number
  height: number
  className?: string
  priority?: boolean
  sizes?: string
  placeholder?: 'blur' | 'empty'
  blurDataURL?: string
  onLoad?: () => void
  onError?: () => void
  fallbackSrc?: string
  enableWebP?: boolean
  enableProgressive?: boolean
  quality?: number
}

const BLUR_DATA_URL = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R+Kic5O0corBaM7eLVNYkO5bCVgSl39BrGjg"

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  priority = false,
  sizes,
  placeholder = 'blur',
  blurDataURL = BLUR_DATA_URL,
  onLoad,
  onError,
  fallbackSrc,
  enableWebP = true,
  enableProgressive = true,
  quality = 80
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [currentSrc, setCurrentSrc] = useState(src)
  const [isInView, setIsInView] = useState(priority) // If priority, assume in view
  const imgRef = useRef<HTMLDivElement>(null)
  
  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || isInView) return
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          observer.disconnect()
        }
      },
      {
        rootMargin: '50px' // Load images 50px before they come into view
      }
    )
    
    if (imgRef.current) {
      observer.observe(imgRef.current)
    }
    
    return () => observer.disconnect()
  }, [priority, isInView])
  
  // Construct optimized image URL
  const getOptimizedImageUrl = (imageUrl: string): string => {
    if (!imageUrl) return fallbackSrc || '/placeholder-movie.jpg'
    
    // If it's already a full URL, use our proxy
    if (imageUrl.startsWith('http')) {
      const proxyUrl = `/api/images/proxy?url=${encodeURIComponent(imageUrl)}`
      
      // Add size parameter based on width
      let sizeParam = 'w500'
      if (width <= 200) sizeParam = 'w200'
      else if (width >= 600) sizeParam = 'w780'
      
      return `${proxyUrl}&size=${sizeParam}`
    }
    
    // If it's a TMDB path, use the path-based proxy
    let sizeParam = 'w500'
    if (width <= 200) sizeParam = 'w200'
    else if (width >= 600) sizeParam = 'w780'
    
    return `/api/images/proxy${imageUrl}?size=${sizeParam}`
  }
  
  // Get WebP version if supported
  const getWebPUrl = (imageUrl: string): string => {
    const optimizedUrl = getOptimizedImageUrl(imageUrl)
    
    // Check WebP support
    if (typeof window !== 'undefined' && enableWebP) {
      const canvas = document.createElement('canvas')
      const supportsWebP = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0
      
      if (supportsWebP) {
        return `${optimizedUrl}&format=webp`
      }
    }
    
    return optimizedUrl
  }
  
  const handleLoad = () => {
    setIsLoaded(true)
    onLoad?.()
  }
  
  const handleError = () => {
    if (currentSrc !== fallbackSrc && fallbackSrc) {
      setCurrentSrc(fallbackSrc)
      setHasError(false)
    } else {
      setHasError(true)
      onError?.()
    }
  }
  
  // Progressive enhancement sizes
  const generateSizes = (): string => {
    if (sizes) return sizes
    
    // Generate responsive sizes based on width
    if (width <= 200) {
      return '(max-width: 640px) 150px, (max-width: 768px) 180px, 200px'
    } else if (width <= 300) {
      return '(max-width: 640px) 200px, (max-width: 768px) 250px, 300px'
    } else {
      return '(max-width: 640px) 280px, (max-width: 768px) 350px, 400px'
    }
  }
  
  if (!isInView) {
    return (
      <div
        ref={imgRef}
        className={`bg-gray-200 dark:bg-gray-800 animate-pulse ${className}`}
        style={{ width, height }}
      />
    )
  }
  
  if (hasError) {
    return (
      <div
        className={`bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center text-gray-400 ${className}`}
        style={{ width, height }}
      >
        <div className="text-center">
          <div className="text-2xl mb-1">🎬</div>
          <div className="text-xs">Image Error</div>
        </div>
      </div>
    )
  }
  
  return (
    <div ref={imgRef} className={`relative overflow-hidden ${className}`} style={{ width, height }}>
      {/* Progressive loading: low quality first */}
      {enableProgressive && !isLoaded && (
        <Image
          src={getOptimizedImageUrl(currentSrc)}
          alt={alt}
          fill
          className="object-cover filter blur-sm scale-110"
          quality={20}
          sizes={generateSizes()}
          priority={priority}
        />
      )}
      
      {/* Main high-quality image */}
      <Image
        src={getWebPUrl(currentSrc)}
        alt={alt}
        fill
        className={`object-cover transition-opacity duration-300 ${
          isLoaded ? 'opacity-100' : 'opacity-0'
        }`}
        quality={quality}
        sizes={generateSizes()}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        priority={priority}
        onLoad={handleLoad}
        onError={handleError}
      />
      
      {/* Loading overlay */}
      {!isLoaded && (
        <motion.div
          className="absolute inset-0 bg-gray-200 dark:bg-gray-800 flex items-center justify-center"
          initial={{ opacity: 1 }}
          animate={{ opacity: isLoaded ? 0 : 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
        </motion.div>
      )}
      
      {/* Preload next size on hover */}
      <link
        rel="prefetch"
        href={getOptimizedImageUrl(currentSrc).replace(/&size=\w+/, '&size=w780')}
        as="image"
      />
    </div>
  )
}

export default OptimizedImage