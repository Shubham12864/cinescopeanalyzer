"use client"

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

interface MovieImageProps {
  src?: string | null
  alt: string
  className?: string
  priority?: boolean
  fill?: boolean
  width?: number
  height?: number
  fallbackSrc?: string
}

export function MovieImage({ 
  src, 
  alt, 
  className, 
  priority = false, 
  fill = false,
  width = 300,      // ADD DEFAULT WIDTH
  height = 450,     // ADD DEFAULT HEIGHT
  fallbackSrc
}: MovieImageProps) {
  const generateFallback = (title: string) => {
    const encodedTitle = encodeURIComponent(title.slice(0, 20))
    return `https://via.placeholder.com/300x450/1a1a1a/ffffff?text=${encodedTitle}`
  }

  const defaultFallback = fallbackSrc || generateFallback(alt || 'Movie')
  const [imgSrc, setImgSrc] = useState(src || defaultFallback)
  const [loading, setLoading] = useState(!!src)
  const [error, setError] = useState(false)

  const handleError = () => {
    console.log('Image failed to load:', imgSrc)
    if (!error && imgSrc !== defaultFallback) {
      setError(true)
      setImgSrc(defaultFallback)
      setLoading(false)
    }
  }

  const handleLoad = () => {
    console.log('Image loaded successfully:', imgSrc)
    setLoading(false)
    setError(false)
  }

  // Update image source when src prop changes
  useEffect(() => {
    if (!src || src === 'N/A' || src.includes('placeholder')) {
      setImgSrc(defaultFallback)
      setLoading(false)
      setError(false)
    } else {
      setImgSrc(src)
      setLoading(!!src)
      setError(false)
    }
  }, [src, defaultFallback])

  return (
    <div className={cn("relative overflow-hidden", className)}>
      {loading && (
        <div className="absolute inset-0 bg-gray-800 animate-pulse flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      
      <Image
        src={imgSrc}
        alt={alt}
        fill={fill}
        width={fill ? undefined : width}
        height={fill ? undefined : height}
        className={cn(
          "transition-opacity duration-300",
          loading ? "opacity-0" : "opacity-100",
          "object-cover"
        )}
        priority={priority}
        onError={handleError}
        onLoad={handleLoad}
        sizes={fill ? "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw" : undefined}
        unoptimized={imgSrc.includes('placeholder') || imgSrc.includes('via.placeholder')}
      />
    </div>
  )
}
