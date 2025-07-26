"use client"

import Image from 'next/image'
import { useState, useEffect } from 'react'

interface MovieImageProps {
  src?: string | null
  alt: string
  className?: string
  width?: number
  height?: number
  priority?: boolean
}

export function MovieImage({ 
  src, 
  alt, 
  className = "", 
  width = 300, 
  height = 450,
  priority = false
}: MovieImageProps) {
  const [imageError, setImageError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [imgSrc, setImgSrc] = useState<string>('')

  const generatePlaceholder = (title: string) => {
    const encodedTitle = encodeURIComponent(title.slice(0, 20))
    return `https://via.placeholder.com/${width}x${height}/1a1a1a/ffffff?text=${encodedTitle}`
  }

  const getImageSrc = () => {
    if (!src || imageError || src === 'N/A' || src === '' || src === 'null') {
      return generatePlaceholder(alt)
    }
    
    // Check if it's a FanArt URL - use directly
    if (src.includes('fanart.tv') || src.includes('assets.fanart.tv')) {
      return src
    }
    
    // If it's already a full URL, use it directly
    if (src.startsWith('http')) {
      return src
    }
    
    // If it's a relative URL, prepend the API base
    if (src.startsWith('/api/')) {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      return `${apiBase}${src}`
    }
    
    return src
  }

  // Update image source when src prop changes
  useEffect(() => {
    const newSrc = getImageSrc()
    setImgSrc(newSrc)
    setIsLoading(true)
    setImageError(false)
  }, [src, alt])

  const handleImageLoad = () => {
    setIsLoading(false)
    setImageError(false)
  }

  const handleImageError = () => {
    console.warn(`Image failed to load: ${src}`)
    if (!imageError) {
      setImageError(true)
      setImgSrc(generatePlaceholder(alt))
      setIsLoading(false)
    }
  }

  return (
    <div className={`relative ${className}`}>
      {isLoading && (
        <div 
          className="absolute inset-0 bg-gray-800 animate-pulse rounded flex items-center justify-center"
          style={{ width, height }}
        >
          <div className="text-gray-400 text-sm">Loading...</div>
        </div>
      )}
      
      <Image
        src={imgSrc}
        alt={alt}
        width={width}
        height={height}
        className={`rounded transition-opacity duration-300 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
        onLoad={handleImageLoad}
        onError={handleImageError}
        unoptimized={imgSrc.includes('fanart.tv') || imgSrc.includes('placeholder')}
        priority={priority}
        style={{ objectFit: 'cover' }}
      />
      
      {/* Debug info in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-xs text-white p-1 truncate">
          {imgSrc}
        </div>
      )}
    </div>
  )
}
