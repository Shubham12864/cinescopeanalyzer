"use client"

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Play, Star, Calendar, Tag, User } from 'lucide-react'
import { useMovieContext } from '@/contexts/movie-context'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatRating, getSentimentBadgeColor } from '@/lib/api'
import type { Movie } from '@/types/movie'
import Image from 'next/image'
import AnalyticsDashboard from '@/components/analysis/analytics-dashboard'

export default function MovieDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { getMovieById, analyzeMovie, isBackendConnected, isLoading } = useMovieContext()
  const [movie, setMovie] = useState<Movie | null>(null)
  const [analyticsData, setAnalyticsData] = useState<any>(null)
  const [loadingMovie, setLoadingMovie] = useState(true)
  const [loadingAnalytics, setLoadingAnalytics] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showAnalytics, setShowAnalytics] = useState(false)

  const movieId = params.id as string

  useEffect(() => {
    if (movieId) {
      loadMovie(movieId)
    }
  }, [movieId])
  const loadMovie = async (id: string) => {
    try {
      console.log('🎬 MovieDetails: Loading movie with ID:', id)
      setLoadingMovie(true)
      setError(null)
      const movieData = await getMovieById(id)
      console.log('🎬 MovieDetails: Received movie data:', movieData)
      if (movieData) {
        setMovie(movieData)
        console.log('🎬 MovieDetails: Movie loaded successfully:', movieData.title)
      } else {
        console.error('🎬 MovieDetails: Movie not found for ID:', id)
        setError('Movie not found')
      }
    } catch (error) {
      console.error('🎬 MovieDetails: Error loading movie:', error)
      setError(error instanceof Error ? error.message : 'Failed to load movie')
    } finally {
      setLoadingMovie(false)
    }
  }
  const loadAnalytics = async (id: string) => {
    try {
      setLoadingAnalytics(true)
      console.log('📊 Loading analytics for:', id)
      const response = await fetch(`http://localhost:8000/api/movies/${id}/analysis`)
      console.log('📊 Analytics response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('📊 Analytics data received:', data)
        if (data.success) {
          setAnalyticsData(data.analytics)
          setShowAnalytics(true)
        } else {
          // Even if success is false, try to use the data if it exists
          if (data.data) {
            setAnalyticsData(data.data)
            setShowAnalytics(true)
          }
        }
      } else {
        console.error('📊 Analytics request failed:', response.status)
      }
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoadingAnalytics(false)
    }
  }
    const handleAnalyze = async () => {
    if (!movie) return
    
    try {
      setIsAnalyzing(true)
      console.log('🎬 Starting analysis for movie:', movie.id)
      
      // Call the backend analyze endpoint directly
      const response = await fetch(`http://localhost:8000/api/movies/${movie.id}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('📊 Analysis response:', data)
        
        // The backend returns analytics data in the 'data' field
        if (data.data) {
          setAnalyticsData(data.data)
          setShowAnalytics(true)
          console.log('✅ Analytics loaded and showing')
        } else {
          console.error('❌ No analytics data in response')
        }
      } else {
        console.error('❌ Analysis request failed:', response.status)
      }
      
    } catch (error) {
      console.error('❌ Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleBack = () => {
    router.push('/')
  }

  if (loadingMovie) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-white text-xl">Loading movie details...</div>
        </div>
      </div>
    )
  }

  if (error || !movie) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">{error || 'Movie not found'}</div>
          <Button onClick={handleBack} variant="destructive">
            Back to Home
          </Button>
        </div>
      </div>
    )
  }  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header with Back Button */}
      <div className="relative bg-gradient-to-br from-red-900/20 via-gray-900 to-black border-b border-red-600/20 py-8">
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 to-transparent"></div>
        <div className="relative container mx-auto px-8">
          <Button
            onClick={handleBack}
            variant="secondary"
            className="flex items-center gap-2 mb-6 bg-red-600/20 hover:bg-red-600/30 text-white border-red-600/30"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Movies
          </Button>
          
          {/* Movie Title and Basic Info */}
          <h1 className="text-5xl font-bold mb-4 font-poppins text-white drop-shadow-lg">{movie.title}</h1>          <div className="flex flex-wrap items-center gap-6 mb-4">
            <div className="flex items-center gap-2 bg-red-600/10 px-3 py-1 rounded-lg border border-red-600/30">
              <Star className="w-5 h-5 text-red-400 fill-current" />
              <span className="text-xl font-semibold text-red-400">{formatRating(movie.rating)}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-400" />
              <span className="text-gray-300">{movie.year}</span>
            </div>
          </div>

          {/* Genres */}
          <div className="flex flex-wrap gap-2">
            {movie.genre.map((genre) => (
              <Badge key={genre} variant="secondary" className="bg-red-600/20 text-red-300 border-red-600/30 shadow-lg">
                {genre}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      {/* Content - Two Column Layout */}
      <div className="container mx-auto px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">          {/* Left Column - Main Content */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              {/* Enhanced Plot/Description Section */}
              <div className="mb-8">                <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
                  <div className="w-1 h-6 bg-red-600 rounded"></div>
                  Plot Summary
                </h2>
                
                {/* Enhanced IMDb-style Description */}
                <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
                  {(() => {
                    const plot = movie.plot || '';
                    if (!plot || plot === 'No plot available.' || plot === 'N/A') {
                      return (
                        <div className="space-y-4">
                          <div className="flex items-start gap-4">
                            <div className="flex-shrink-0 mt-2">
                              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                            </div>                            <p className="text-lg text-gray-300 leading-relaxed">
                              Explore the captivating world of <strong className="text-red-400">{movie.title}</strong>, a {movie.genre?.[0]?.toLowerCase() || 'compelling'} {movie.genre?.[1]?.toLowerCase() || 'story'} from {movie.year}.
                            </p>
                          </div>
                          {movie.director && (                            <div className="flex items-start gap-4">
                              <div className="flex-shrink-0 mt-2">
                                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                              </div>
                              <p className="text-lg text-gray-300 leading-relaxed">
                                Directed by <strong className="text-red-400">{movie.director}</strong>, this {movie.runtime ? `${movie.runtime}-minute` : ''} film promises an engaging cinematic experience.
                              </p>
                            </div>
                          )}
                        </div>
                      );
                    }
                    
                    // Split description into logical points for better readability
                    const sentences = plot.match(/[^\.!?]+[\.!?]+/g) || [plot];
                    const points = [];
                    
                    // Group sentences into logical points (2-3 sentences per point)
                    for (let i = 0; i < sentences.length; i += 2) {
                      const point = sentences.slice(i, i + 2).join(' ').trim();
                      if (point.length > 20) {
                        points.push(point);
                      }
                    }
                    
                    // If we don't have clear sentence breaks, split by length
                    if (points.length <= 1 && plot.length > 200) {
                      const words = plot.split(' ');
                      const chunkSize = Math.ceil(words.length / 3);
                      for (let i = 0; i < words.length; i += chunkSize) {
                        const chunk = words.slice(i, i + chunkSize).join(' ');
                        if (chunk.trim().length > 20) {
                          points.push(chunk.trim());
                        }
                      }
                    } else if (points.length === 0) {
                      points.push(plot);
                    }
                    
                    return (
                      <div className="space-y-5">
                        {points.map((point, index) => (
                          <div key={index} className="flex items-start gap-4">
                            <div className="flex-shrink-0 mt-2">                            <div className={`w-2 h-2 rounded-full ${
                                index === 0 ? 'bg-red-500' : 
                                index === 1 ? 'bg-red-400' : 
                                'bg-red-300'
                              }`}></div>
                            </div>
                            <p className="text-lg text-gray-300 leading-relaxed text-justify flex-1">
                              {point}
                            </p>
                          </div>
                        ))}
                          {/* Additional contextual information */}
                        {movie.director && points.length > 0 && (
                          <div className="flex items-start gap-4 pt-4 border-t border-gray-700/30">
                            <div className="flex-shrink-0 mt-2">
                              <div className="w-2 h-2 bg-red-200 rounded-full"></div>
                            </div>
                            <p className="text-base text-gray-400 leading-relaxed">
                              <strong className="text-red-300">Direction:</strong> Under the skilled direction of <span className="text-red-400">{movie.director}</span>, this {movie.genre?.[0]?.toLowerCase() || 'film'} showcases masterful storytelling and compelling character development.
                            </p>
                          </div>
                        )}
                          {movie.cast && movie.cast.length > 0 && (
                          <div className="flex items-start gap-4">
                            <div className="flex-shrink-0 mt-2">
                              <div className="w-2 h-2 bg-red-100 rounded-full"></div>
                            </div>
                            <p className="text-base text-gray-400 leading-relaxed">
                              <strong className="text-red-300">Cast:</strong> Features outstanding performances by <span className="text-red-400">{movie.cast.slice(0, 3).join(', ')}</span>{movie.cast.length > 3 && <span>, and {movie.cast.length - 3} other talented actors</span>}.
                            </p>
                          </div>
                        )}
                      </div>                    );
                  })()}
                </div>
              </div>              {/* Action Buttons - Enhanced and moved up */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8 pt-6">
                <Button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-3 text-lg shadow-lg hover:shadow-xl"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Analyzing Movie...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Analyze Movie
                    </>
                  )}
                </Button>
                
                <Button
                  onClick={() => router.push(`/movies/${movie.id}/reviews`)}
                  variant="outline"
                  className="border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white px-8 py-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-3 text-lg shadow-lg hover:shadow-xl"
                >
                  <User className="w-5 h-5" />
                  View Reviews
                </Button>
              </div>
            </motion.div>
          </div>

          {/* Right Column - Movie Poster & Additional Info */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="sticky top-8 space-y-6"
            >
              {/* Large Movie Poster */}
              <div className="relative group">
                <div className="aspect-[2/3] relative overflow-hidden rounded-xl border border-gray-800 bg-gray-900">
                  <Image
                    src={movie.poster || '/placeholder.svg?height=600&width=400'}
                    alt={`${movie.title} poster`}
                    fill
                    className="object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
              </div>

              {/* Quick Stats Card */}
              <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-800">
                <h3 className="text-lg font-semibold mb-4 text-center">Movie Statistics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">IMDb Rating</span>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="font-medium">{formatRating(movie.rating)}/10</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Release Year</span>
                    <span className="font-medium">{movie.year}</span>
                  </div>
                  {movie.runtime && (
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Duration</span>
                      <span className="font-medium">{movie.runtime} min</span>
                    </div>
                  )}
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Genres</span>
                    <span className="font-medium">{movie.genre.length}</span>
                  </div>
                </div>
              </div>

              {/* Genre Breakdown */}
              <div className="bg-gray-900/50 p-6 rounded-xl border border-gray-800">
                <h3 className="text-lg font-semibold mb-4 text-center">Genres</h3>
                <div className="flex flex-wrap gap-2 justify-center">
                  {movie.genre.map((genre, index) => (
                    <div key={genre} className="text-center">
                      <Badge 
                        variant="secondary" 
                        className="bg-red-600/20 text-red-300 border border-red-600/30"
                      >
                        {genre}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Movie ID & Technical Info */}
              <div className="bg-gray-900/30 p-4 rounded-lg border border-gray-800">
                <h4 className="text-sm font-medium text-gray-400 mb-2">Technical Information</h4>
                <div className="space-y-1 text-xs text-gray-500">
                  <div>Movie ID: <span className="text-gray-400">{movie.id}</span></div>
                  {movie.imdbId && (
                    <div>IMDb ID: <span className="text-gray-400">{movie.imdbId}</span></div>
                  )}
                </div>
              </div>            </motion.div>
          </div>
        </div>

        {/* Reviews Section - Full Width Below Grid */}
        {movie.reviews && movie.reviews.length > 0 && (
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mt-12"
          >
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <div className="w-1 h-6 bg-red-600 rounded"></div>
              Reviews ({movie.reviews.length})
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {movie.reviews.slice(0, 4).map((review) => (
                <motion.div 
                  key={review.id} 
                  className="bg-gray-900/50 p-4 rounded-lg border border-gray-800"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="flex items-center gap-4 mb-2">
                    <span className="font-semibold text-white">{review.author}</span>
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span>{review.rating}</span>
                    </div>
                    {review.sentiment && (
                      <Badge 
                        variant="outline" 
                        className={getSentimentBadgeColor(review.sentiment)}
                      >
                        {review.sentiment}
                      </Badge>
                    )}
                    {review.date && (
                      <span className="text-sm text-gray-500">{review.date}</span>
                    )}
                  </div>
                  <p className="text-gray-300 leading-relaxed text-justify">{review.content}</p>
                </motion.div>
              ))}
            </div>
            
            {movie.reviews.length > 4 && (
              <div className="text-center pt-6">
                <Button 
                  variant="outline" 
                  onClick={() => router.push(`/movies/${movie.id}/reviews`)}
                >
                  View All {movie.reviews.length} Reviews
                </Button>
              </div>
            )}
          </motion.div>
        )}        {/* Analytics Dashboard - Full Width */}
        {analyticsData && (
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="mt-12"
          >
            <AnalyticsDashboard movieData={movie} analyticsData={analyticsData} />
          </motion.div>
        )}
        </div>
    </div>
  )
}
