"use client"

import React, { useState, useEffect } from 'react'
import { MovieCarousel } from '../movie-cards/MovieCarousel'
import { useQuery } from '@tanstack/react-query'
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

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

interface DynamicMovieSectionsProps {
  onMoviePlay?: (movie: Movie) => void
  onMovieInfo?: (movie: Movie) => void
  onViewAll?: (section: string) => void
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// API functions
const fetchPopularMovies = async (): Promise<Movie[]> => {
  const response = await fetch(`${API_BASE_URL}/api/movies/popular?limit=20`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch popular movies: ${response.statusText}`)
  }
  
  const data = await response.json()
  return Array.isArray(data) ? data : []
}

const fetchTrendingMovies = async (): Promise<Movie[]> => {
  const response = await fetch(`${API_BASE_URL}/api/movies/trending?limit=20`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch trending movies: ${response.statusText}`)
  }
  
  const data = await response.json()
  return Array.isArray(data) ? data : []
}

const fetchTopRatedMovies = async (): Promise<Movie[]> => {
  const response = await fetch(`${API_BASE_URL}/api/movies/top-rated?limit=20`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch top rated movies: ${response.statusText}`)
  }
  
  const data = await response.json()
  return Array.isArray(data) ? data : []
}

const fetchRecentMovies = async (): Promise<Movie[]> => {
  const response = await fetch(`${API_BASE_URL}/api/movies/recent?limit=20`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    credentials: 'include'
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch recent movies: ${response.statusText}`)
  }
  
  const data = await response.json()
  return Array.isArray(data) ? data : []
}

export function DynamicMovieSections({
  onMoviePlay,
  onMovieInfo,
  onViewAll
}: DynamicMovieSectionsProps) {
  const [retryCount, setRetryCount] = useState(0)
  
  // React Query for data fetching with caching
  const {
    data: popularMovies,
    isLoading: popularLoading,
    error: popularError,
    refetch: refetchPopular
  } = useQuery({
    queryKey: ['popularMovies', retryCount],
    queryFn: fetchPopularMovies,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  })
  
  const {
    data: trendingMovies,
    isLoading: trendingLoading,
    error: trendingError,
    refetch: refetchTrending
  } = useQuery({
    queryKey: ['trendingMovies', retryCount],
    queryFn: fetchTrendingMovies,
    staleTime: 5 * 60 * 1000, // 5 minutes (trending changes more frequently)
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  })
  
  const {
    data: topRatedMovies,
    isLoading: topRatedLoading,
    error: topRatedError,
    refetch: refetchTopRated
  } = useQuery({
    queryKey: ['topRatedMovies', retryCount],
    queryFn: fetchTopRatedMovies,
    staleTime: 30 * 60 * 1000, // 30 minutes (top rated changes less frequently)
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  })
  
  const {
    data: recentMovies,
    isLoading: recentLoading,
    error: recentError,
    refetch: refetchRecent
  } = useQuery({
    queryKey: ['recentMovies', retryCount],
    queryFn: fetchRecentMovies,
    staleTime: 15 * 60 * 1000, // 15 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
  })
  
  const handleRetryAll = () => {
    setRetryCount(prev => prev + 1)
    refetchPopular()
    refetchTrending()
    refetchTopRated()
    refetchRecent()
  }
  
  const hasAnyError = popularError || trendingError || topRatedError || recentError
  const isAnyLoading = popularLoading || trendingLoading || topRatedLoading || recentLoading
  
  // Show global error if all sections fail
  if (hasAnyError && !popularMovies && !trendingMovies && !topRatedMovies && !recentMovies) {
    return (
      <div className="space-y-6 p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>Failed to load movie data. Please check your connection and try again.</span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetryAll}
              className="ml-4"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }
  
  return (
    <div className="space-y-12 p-6">
      {/* Popular Movies Section */}
      <MovieCarousel
        title="🔥 Popular Movies"
        movies={popularMovies || []}
        loading={popularLoading}
        error={popularError?.message}
        onMoviePlay={onMoviePlay}
        onMovieInfo={onMovieInfo}
        onViewAll={() => onViewAll?.('popular')}
        cardSize="medium"
        showNavigation={true}
      />
      
      {/* Trending Movies Section */}
      <MovieCarousel
        title="📈 Trending Now"
        movies={trendingMovies || []}
        loading={trendingLoading}
        error={trendingError?.message}
        onMoviePlay={onMoviePlay}
        onMovieInfo={onMovieInfo}
        onViewAll={() => onViewAll?.('trending')}
        cardSize="medium"
        showNavigation={true}
      />
      
      {/* Top Rated Movies Section */}
      <MovieCarousel
        title="⭐ Top Rated"
        movies={topRatedMovies || []}
        loading={topRatedLoading}
        error={topRatedError?.message}
        onMoviePlay={onMoviePlay}
        onMovieInfo={onMovieInfo}
        onViewAll={() => onViewAll?.('top-rated')}
        cardSize="medium"
        showNavigation={true}
      />
      
      {/* Recent Movies Section */}
      <MovieCarousel
        title="🎬 Recently Added"
        movies={recentMovies || []}
        loading={recentLoading}
        error={recentError?.message}
        onMoviePlay={onMoviePlay}
        onMovieInfo={onMovieInfo}
        onViewAll={() => onViewAll?.('recent')}
        cardSize="medium"
        showNavigation={true}
      />
      
      {/* Loading Indicator for Background Refreshes */}
      {isAnyLoading && (popularMovies || trendingMovies || topRatedMovies || recentMovies) && (
        <div className="fixed bottom-4 right-4 bg-black/80 text-white px-4 py-2 rounded-full flex items-center gap-2 z-50">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Updating...</span>
        </div>
      )}
    </div>
  )
}

export default DynamicMovieSections