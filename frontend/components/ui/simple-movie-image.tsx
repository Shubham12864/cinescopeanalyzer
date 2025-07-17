"use client"

import React, { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface SimpleMovieImageProps {
  src?: string | null
  alt: string
  className?: string
  width?: number
  height?: number
}

export function SimpleMovieImage({ 
  src, 
  alt, 
  className, 
  width = 300,
  height = 450
}: SimpleMovieImageProps) {
  const generateFallback = (title: string) => {
    const encodedTitle = encodeURIComponent(title.slice(0, 20))
    return `https://dummyimage.com/300x450/1a1a1a/ffffff.png&text=${encodedTitle}`
  }

  const defaultFallback = generateFallback(alt || 'Movie')
  const [imgSrc, setImgSrc] = useState(src || defaultFallback)
  const [error, setError] = useState(false)

  const handleError = () => {
    console.error('🖼️ Simple image failed to load:', imgSrc)
    if (!error && imgSrc !== defaultFallback) {
      setError(true)
      setImgSrc(defaultFallback)
    }
  }

  const handleLoad = () => {
    console.log('🖼️ Simple image loaded successfully:', imgSrc)
  }

  useEffect(() => {
    if (!src || src === 'N/A' || src.includes('placeholder')) {
      console.log('🖼️ Using fallback for invalid src:', src)
      setImgSrc(defaultFallback)
      setError(false)
    } else {
      // Clean the URL by removing any line breaks or whitespace
      const cleanSrc = src.replace(/\s+/g, '').trim()
      console.log('🖼️ Setting clean simple image src:', cleanSrc)
      setImgSrc(cleanSrc)
      setError(false)
    }
  }, [src, defaultFallback])

  return (
    <div className={cn("relative overflow-hidden", className)}>
      <img
        src={imgSrc}
        alt={alt}
        style={{ width: `${width}px`, height: `${height}px` }}
        className="object-cover transition-opacity duration-300"
        onError={handleError}
        onLoad={handleLoad}
      />
      
      {error && imgSrc === defaultFallback && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 flex flex-col items-center justify-center text-gray-300">
          <div className="text-6xl mb-4 opacity-50">🎬</div>
          <div className="text-sm text-center px-4 font-medium">
            {alt}
          </div>
        </div>
      )}
    </div>
  )
}
