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
  width = 300,
  height = 450,
  fallbackSrc
}: MovieImageProps) {
  // Generate fallback image with movie title
  const generateFallback = (title: string) => {
    const encodedTitle = encodeURIComponent(title.slice(0, 20))
    return `https://dummyimage.com/300x450/1a1a1a/ffffff.png&text=${encodedTitle}`
  }

  const defaultFallback = fallbackSrc || generateFallback(alt || 'Movie')
  const [imgSrc, setImgSrc] = useState(src || defaultFallback)
  const [loading, setLoading] = useState(!!src)
  const [error, setError] = useState(false)
  
  const handleError = () => {
    if (!error && imgSrc !== defaultFallback) {
      setError(true)
      setImgSrc(defaultFallback)
      setLoading(false)
    }
  }

  const handleLoad = () => {
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
      // Clean the URL by removing any line breaks or whitespace
      const cleanSrc = src.replace(/\s+/g, '').trim()
      setImgSrc(cleanSrc)
      setLoading(!!cleanSrc)
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
        width={!fill ? width : undefined}
        height={!fill ? height : undefined}
        className={cn(
          "transition-opacity duration-300",
          loading ? "opacity-0" : "opacity-100",
          "object-cover"
        )}
        priority={priority}
        onError={handleError}
        onLoad={handleLoad}
        unoptimized={imgSrc.includes('placeholder') || imgSrc.includes('via.placeholder') || imgSrc.includes('dummyimage')}
        sizes={fill ? "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw" : undefined}
      />
      
      {error && imgSrc === defaultFallback && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex flex-col items-center justify-center text-gray-300">
          <div className="text-6xl mb-4 opacity-50">🎬</div>
          <div className="text-sm text-center px-4 font-medium">
            {alt || 'Movie'}
          </div>
        </div>
      )}
    </div>
  )
}
