"use client"

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, TrendingUp, Users, Star, MessageCircle, BarChart3, PieChart } from 'lucide-react'
import { useMovieContext } from '@/contexts/movie-context'
import { movieApi } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import type { Movie, AnalyticsData } from '@/types/movie'

export default function MovieAnalysisPage() {
  const params = useParams()
  const router = useRouter()
  const { getMovieById, isBackendConnected } = useMovieContext()
  const [movie, setMovie] = useState<Movie | null>(null)
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const movieId = params.id as string

  useEffect(() => {
    if (movieId) {
      loadAnalysis(movieId)
    }
  }, [movieId])

  const loadAnalysis = async (id: string) => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Load movie details
      const movieData = await getMovieById(id)
      if (movieData) {
        setMovie(movieData)
      }

      // Load analytics if backend is connected
      if (isBackendConnected) {
        try {
          const analyticsData = await movieApi.getMovieAnalysis(id)
          setAnalytics(analyticsData)
        } catch (err) {
          // If movie-specific analysis fails, try general analytics
          try {
            const generalAnalytics = await movieApi.getAnalytics()
            setAnalytics(generalAnalytics)
          } catch (generalErr) {
            console.error('Failed to load analytics:', generalErr)
            // Create mock analytics based on movie data
            createMockAnalytics(movieData)
          }
        }
      } else {
        // Create mock analytics when backend is not connected
        createMockAnalytics(movieData)
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load analysis')
    } finally {
      setIsLoading(false)
    }
  }

  const createMockAnalytics = (movieData: Movie | null) => {
    if (!movieData) return

    const mockAnalytics: AnalyticsData = {
      totalMovies: 1,
      totalReviews: movieData.reviews?.length || 0,
      averageRating: movieData.rating,
      sentimentDistribution: {
        positive: Math.floor((movieData.reviews?.length || 10) * 0.6),
        negative: Math.floor((movieData.reviews?.length || 10) * 0.2),
        neutral: Math.floor((movieData.reviews?.length || 10) * 0.2)
      },
      ratingDistribution: [2, 5, 12, 25, 35, 15, 6],
      genrePopularity: movieData.genre.map(genre => ({ genre, count: Math.floor(Math.random() * 20) + 5 })),
      reviewTimeline: Array.from({ length: 12 }, (_, i) => ({
        date: `2024-${String(i + 1).padStart(2, '0')}`,
        count: Math.floor(Math.random() * 10) + 1
      })),
      topRatedMovies: [movieData],
      recentlyAnalyzed: [movieData]
    }
    setAnalytics(mockAnalytics)
  }

  const handleBack = () => {
    router.push(`/movies/${movieId}`)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-red-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-white text-xl">Loading analysis...</div>
        </div>
      </div>
    )
  }

  if (error || !movie || !analytics) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">{error || 'Analysis not found'}</div>
          <Button onClick={handleBack} variant="destructive">
            Back to Movie
          </Button>
        </div>
      </div>
    )
  }

  const sentimentTotal = analytics.sentimentDistribution.positive + 
                        analytics.sentimentDistribution.negative + 
                        analytics.sentimentDistribution.neutral

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            onClick={handleBack}
            variant="secondary"
            className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Movie
          </Button>
          
          <div className="flex items-center gap-4 mb-4">
            <h1 className="text-4xl font-bold font-poppins">Analysis Results</h1>
            {!isBackendConnected && (
              <div className="bg-yellow-600/20 border border-yellow-600 px-3 py-1 rounded text-sm">
                Demo Data
              </div>
            )}
          </div>
          <h2 className="text-2xl text-gray-400 mb-2">{movie.title}</h2>
          <p className="text-gray-400">Comprehensive movie review analysis and insights</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 p-6 border-blue-600/30">
              <div className="flex items-center gap-3 mb-2">
                <MessageCircle className="w-6 h-6 text-blue-400" />
                <span className="text-blue-300 font-medium">Total Reviews</span>
              </div>
              <div className="text-3xl font-bold text-white">{analytics.totalReviews}</div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-gradient-to-br from-yellow-600/20 to-yellow-800/20 p-6 border-yellow-600/30">
              <div className="flex items-center gap-3 mb-2">
                <Star className="w-6 h-6 text-yellow-400" />
                <span className="text-yellow-300 font-medium">Average Rating</span>
              </div>
              <div className="text-3xl font-bold text-white">{analytics.averageRating.toFixed(1)}</div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-gradient-to-br from-green-600/20 to-green-800/20 p-6 border-green-600/30">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="w-6 h-6 text-green-400" />
                <span className="text-green-300 font-medium">Positive Reviews</span>
              </div>
              <div className="text-3xl font-bold text-white">{analytics.sentimentDistribution.positive}</div>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-gradient-to-br from-red-600/20 to-red-800/20 p-6 border-red-600/30">
              <div className="flex items-center gap-3 mb-2">
                <Users className="w-6 h-6 text-red-400" />
                <span className="text-red-300 font-medium">Negative Reviews</span>
              </div>
              <div className="text-3xl font-bold text-white">{analytics.sentimentDistribution.negative}</div>
            </Card>
          </motion.div>
        </div>

        {/* Sentiment Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8"
        >
          <Card className="bg-gray-900/50 p-6 border-gray-800">
            <div className="flex items-center gap-3 mb-6">
              <PieChart className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-bold">Sentiment Distribution</h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <span className="w-20 text-green-300 font-medium">Positive</span>
                <div className="flex-1 bg-gray-800 rounded-full h-4">
                  <div 
                    className="bg-green-500 h-4 rounded-full transition-all duration-1000"
                    style={{ width: `${sentimentTotal > 0 ? (analytics.sentimentDistribution.positive / sentimentTotal) * 100 : 0}%` }}
                  />
                </div>
                <span className="text-white font-semibold w-12 text-right">
                  {analytics.sentimentDistribution.positive}
                </span>
                <span className="text-gray-400 text-sm w-12">
                  ({sentimentTotal > 0 ? Math.round((analytics.sentimentDistribution.positive / sentimentTotal) * 100) : 0}%)
                </span>
              </div>
              
              <div className="flex items-center gap-4">
                <span className="w-20 text-gray-300 font-medium">Neutral</span>
                <div className="flex-1 bg-gray-800 rounded-full h-4">
                  <div 
                    className="bg-gray-500 h-4 rounded-full transition-all duration-1000"
                    style={{ width: `${sentimentTotal > 0 ? (analytics.sentimentDistribution.neutral / sentimentTotal) * 100 : 0}%` }}
                  />
                </div>
                <span className="text-white font-semibold w-12 text-right">
                  {analytics.sentimentDistribution.neutral}
                </span>
                <span className="text-gray-400 text-sm w-12">
                  ({sentimentTotal > 0 ? Math.round((analytics.sentimentDistribution.neutral / sentimentTotal) * 100) : 0}%)
                </span>
              </div>
              
              <div className="flex items-center gap-4">
                <span className="w-20 text-red-300 font-medium">Negative</span>
                <div className="flex-1 bg-gray-800 rounded-full h-4">
                  <div 
                    className="bg-red-500 h-4 rounded-full transition-all duration-1000"
                    style={{ width: `${sentimentTotal > 0 ? (analytics.sentimentDistribution.negative / sentimentTotal) * 100 : 0}%` }}
                  />
                </div>
                <span className="text-white font-semibold w-12 text-right">
                  {analytics.sentimentDistribution.negative}
                </span>
                <span className="text-gray-400 text-sm w-12">
                  ({sentimentTotal > 0 ? Math.round((analytics.sentimentDistribution.negative / sentimentTotal) * 100) : 0}%)
                </span>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Genre Analysis */}
        {analytics.genrePopularity.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="mb-8"
          >
            <Card className="bg-gray-900/50 p-6 border-gray-800">
              <div className="flex items-center gap-3 mb-6">
                <BarChart3 className="w-6 h-6 text-purple-400" />
                <h2 className="text-2xl font-bold">Genre Analysis</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {analytics.genrePopularity.map((genre, index) => (
                  <div key={genre.genre} className="text-center">
                    <div className="bg-purple-600/20 border border-purple-600/30 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white mb-1">{genre.count}</div>
                      <div className="text-purple-300 text-sm font-medium">{genre.genre}</div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>
        )}

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card className="bg-gray-900/50 p-6 border-gray-800">
            <h2 className="text-2xl font-bold mb-6">Analysis Summary</h2>
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300 leading-relaxed">
                This movie has received <strong className="text-white">{analytics.totalReviews}</strong> reviews 
                with an average rating of <strong className="text-yellow-400">{analytics.averageRating.toFixed(1)}</strong>. 
                The sentiment analysis shows that{' '}
                <strong className="text-green-400">
                  {sentimentTotal > 0 ? Math.round((analytics.sentimentDistribution.positive / sentimentTotal) * 100) : 0}%
                </strong>{' '}
                of reviews are positive, indicating {analytics.sentimentDistribution.positive > analytics.sentimentDistribution.negative ? 'strong audience approval' : 'mixed reception'}.
              </p>
              
              {movie.genre.length > 0 && (
                <p className="text-gray-300 leading-relaxed mt-4">
                  The movie belongs to the <strong className="text-blue-400">{movie.genre.join(', ')}</strong> genre{movie.genre.length > 1 ? 's' : ''}, 
                  which contributes to its unique appeal and target audience engagement.
                </p>
              )}
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
