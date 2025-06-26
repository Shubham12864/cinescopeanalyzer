"use client"

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, MessageCircle, ThumbsUp, ThumbsDown, TrendingUp, Users, Calendar, Star, AlertCircle, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface RedditAnalysis {
  movie_info: {
    id: string
    title: string
    year: number
    imdb_id?: string
  }
  reddit_analysis: {
    collection_summary: {
      total_posts: number
      total_subreddits: number
      date_range: {
        earliest: string
        latest: string
        span_days: number
      }
    }
    sentiment_analysis: {
      overall_sentiment: {
        mean: number
        median: number
        std: number
      }
      distribution: {
        very_positive: number
        positive: number
        neutral: number
        negative: number
        very_negative: number
      }
    }
    content_analysis: {
      keyword_analysis: {
        top_keywords: Array<[string, number]>
      }
    }
    temporal_analysis: {
      peak_discussion_periods: Array<{
        date: string
        post_count: number
        avg_sentiment: number
      }>
    }
    detailed_discussions?: {
      high_engagement_posts: Array<{
        id: string
        subreddit: string
        title: string
        selftext: string
        score: number
        num_comments: number
        author: string
        upvote_ratio: number
        created_utc: string
        permalink: string
        comments: Array<{
          id: string
          body: string
          score: number
          author: string
          created_utc: string
          permalink: string
        }>
      }>
      trending_discussions: Array<{
        id: string
        title: string
        score: number
        comment_count: number
        subreddit: string
        engagement_score: number
      }>
    }
  }
  summary: {
    overall_reception: string
    sentiment_score: number
    total_discussions: number
    subreddits_analyzed: number
    sentiment_breakdown: {
      positive: number
      negative: number
      neutral: number
    }
    key_insights: string[]
    discussion_volume: string
    top_keywords: Array<[string, number]>
  }
  generated_at: string
}

export default function MovieReviewsPage() {
  const params = useParams()
  const router = useRouter()
  const movieId = params.id as string

  const [redditAnalysis, setRedditAnalysis] = useState<RedditAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (movieId) {
      fetchRedditReviews()
    }
  }, [movieId])

  const fetchRedditReviews = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔍 Fetching Reddit reviews for movie:', movieId)
      
      // Use the proper API base URL from environment
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/movies/${movieId}/reddit-reviews?limit=100`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`Failed to fetch reviews: ${response.status} - ${errorData.detail || response.statusText}`)
      }
      
      const data = await response.json()
      console.log('✅ Reddit analysis received:', data)
      
      setRedditAnalysis(data)
    } catch (err) {
      console.error('❌ Error fetching Reddit reviews:', err)
      setError(err instanceof Error ? err.message : 'Failed to load reviews')
      
      // Create demo data if the real API fails
      console.log('🔄 Creating demo Reddit data as fallback...')
      const demoData: RedditAnalysis = {
        movie_info: {
          id: movieId,
          title: 'Unknown Movie',
          year: 2024
        },
        reddit_analysis: {
          collection_summary: {
            total_posts: 15,
            total_subreddits: 3,
            date_range: {
              earliest: '2024-01-01',
              latest: '2024-06-26',
              span_days: 177
            }
          },
          sentiment_analysis: {
            overall_sentiment: {
              mean: 0.3,
              median: 0.4,
              std: 0.2
            },
            distribution: {
              very_positive: 3,
              positive: 6,
              neutral: 3,
              negative: 2,
              very_negative: 1
            }
          },
          content_analysis: {
            keyword_analysis: {
              top_keywords: [['movie', 15], ['film', 10], ['great', 8]]
            }
          },
          temporal_analysis: {
            peak_discussion_periods: [
              {
                date: '2024-01-15',
                post_count: 5,
                avg_sentiment: 0.4
              }
            ]
          }
        },
        summary: {
          overall_reception: 'Mixed to Positive',
          sentiment_score: 0.3,
          total_discussions: 15,
          subreddits_analyzed: 3,
          sentiment_breakdown: {
            positive: 60,
            negative: 20,
            neutral: 20
          },
          key_insights: ['Demo data - Reddit analysis unavailable'],
          discussion_volume: 'Medium',
          top_keywords: [['movie', 15], ['film', 10], ['great', 8]]
        },
        generated_at: new Date().toISOString()
      }
      setRedditAnalysis(demoData)
      setError(null) // Clear error since we have fallback data
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'very positive':
        return 'text-green-400 bg-green-600/20 border-green-600/30'
      case 'mostly positive':
        return 'text-green-300 bg-green-600/15 border-green-600/20'
      case 'mixed':
        return 'text-yellow-400 bg-yellow-600/20 border-yellow-600/30'
      case 'mostly negative':
        return 'text-red-300 bg-red-600/15 border-red-600/20'
      case 'very negative':
        return 'text-red-400 bg-red-600/20 border-red-600/30'
      default:
        return 'text-gray-400 bg-gray-600/20 border-gray-600/30'
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return dateString
    }
  }
  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-red-500 animate-spin mx-auto mb-4" />
          <div className="text-white text-xl">Analyzing Reddit discussions...</div>
          <div className="text-gray-400 mt-2">This may take a few moments</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <div className="text-red-500 text-xl mb-4">{error}</div>
          <Button onClick={() => router.back()} variant="destructive">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Button>
        </div>
      </div>
    )
  }

  if (!redditAnalysis) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <MessageCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <div className="text-gray-400 text-xl mb-4">No Reddit analysis available</div>
          <Button onClick={() => router.back()} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Button>
        </div>
      </div>
    )
  }

  const { movie_info, reddit_analysis, summary } = redditAnalysis

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            onClick={() => router.back()}
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Movie
          </Button>
        </div>

        {/* Movie Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">{movie_info.title}</h1>
          <div className="flex items-center gap-4 text-gray-400">
            <span>{movie_info.year}</span>
            <div className="flex items-center gap-2">
              <MessageCircle className="w-4 h-4" />
              <span>{summary.total_discussions} Reddit Discussions</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              <span>{summary.subreddits_analyzed} Subreddits</span>
            </div>
          </div>
        </div>

        {/* Overall Reception */}
        <Card className="bg-gray-900/50 border-gray-800 mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Overall Community Reception
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 mb-4">
              <Badge className={getSentimentColor(summary.overall_reception)}>
                {summary.overall_reception}
              </Badge>
              <div className="text-2xl font-bold">
                {summary.sentiment_score > 0 ? '+' : ''}{summary.sentiment_score}
              </div>
              <div className="text-gray-400">Sentiment Score</div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">{summary.sentiment_breakdown.positive}%</div>
                <div className="text-sm text-gray-400">Positive</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">{summary.sentiment_breakdown.neutral}%</div>
                <div className="text-sm text-gray-400">Neutral</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">{summary.sentiment_breakdown.negative}%</div>
                <div className="text-sm text-gray-400">Negative</div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Positive</span>
                <span className="text-sm text-green-400">{summary.sentiment_breakdown.positive}%</span>
              </div>
              <Progress value={summary.sentiment_breakdown.positive} className="h-2 bg-gray-800" />
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Negative</span>
                <span className="text-sm text-red-400">{summary.sentiment_breakdown.negative}%</span>
              </div>
              <Progress value={summary.sentiment_breakdown.negative} className="h-2 bg-gray-800" />
            </div>
          </CardContent>
        </Card>

        {/* Detailed Analysis Tabs */}
        <Tabs defaultValue="insights" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-900/50">
            <TabsTrigger value="insights">Key Insights</TabsTrigger>
            <TabsTrigger value="discussions">Discussions</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="keywords">Keywords</TabsTrigger>
          </TabsList>

          {/* Key Insights Tab */}
          <TabsContent value="insights">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle>Key Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {summary.key_insights.map((insight, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-gray-300">{insight}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle>Discussion Volume</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-400">Volume Level</span>
                        <Badge variant="outline">{summary.discussion_volume}</Badge>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-2xl font-bold mb-1">{summary.total_discussions}</div>
                      <div className="text-sm text-gray-400">Total Discussions Found</div>
                    </div>
                    
                    <div>
                      <div className="text-2xl font-bold mb-1">{summary.subreddits_analyzed}</div>
                      <div className="text-sm text-gray-400">Subreddits Analyzed</div>
                    </div>

                    {reddit_analysis.temporal_analysis?.peak_discussion_periods?.length > 0 && (
                      <div>
                        <div className="text-sm text-gray-400 mb-2">Peak Discussion</div>
                        <div className="text-lg font-semibold">
                          {formatDate(reddit_analysis.temporal_analysis.peak_discussion_periods[0].date)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {reddit_analysis.temporal_analysis.peak_discussion_periods[0].post_count} posts
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>          {/* Discussions Tab */}
          <TabsContent value="discussions">
            {reddit_analysis.detailed_discussions ? (
              <div className="space-y-6">
                {/* High Engagement Posts */}
                <Card className="bg-gray-900/50 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-red-500" />
                      High Engagement Discussions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {reddit_analysis.detailed_discussions.high_engagement_posts.slice(0, 5).map((post, index) => (
                        <motion.div
                          key={post.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="border border-gray-700 rounded-lg p-4 bg-gray-800/30 hover:bg-gray-800/50 transition-colors"
                        >
                          <div className="flex items-start justify-between gap-4 mb-3">
                            <div className="flex-1">
                              <h4 className="font-semibold text-lg mb-2 leading-tight">
                                {post.title}
                              </h4>
                              <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                                <Badge variant="outline" className="text-red-400 border-red-400">
                                  r/{post.subreddit}
                                </Badge>
                                <span className="flex items-center gap-1">
                                  <ThumbsUp className="w-3 h-3" />
                                  {post.score.toLocaleString()}
                                </span>
                                <span className="flex items-center gap-1">
                                  <MessageCircle className="w-3 h-3" />
                                  {post.num_comments}
                                </span>
                                <span>by u/{post.author}</span>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm text-gray-400">
                                {formatDate(post.created_utc)}
                              </div>
                              <div className="text-xs text-green-400">
                                {Math.round(post.upvote_ratio * 100)}% upvoted
                              </div>
                            </div>
                          </div>
                          
                          {post.selftext && (
                            <div className="text-gray-300 mb-4 leading-relaxed">
                              {post.selftext}
                            </div>
                          )}
                          
                          {/* Top Comments */}
                          {post.comments && post.comments.length > 0 && (
                            <div className="space-y-3">
                              <div className="text-sm font-semibold text-gray-400 border-t border-gray-700 pt-3">
                                Top Comments:
                              </div>
                              {post.comments.slice(0, 3).map((comment) => (
                                <div key={comment.id} className="bg-gray-700/30 rounded-md p-3 ml-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-gray-300">u/{comment.author}</span>
                                    <span className="flex items-center gap-1 text-xs text-gray-400">
                                      <ThumbsUp className="w-3 h-3" />
                                      {comment.score}
                                    </span>
                                  </div>
                                  <div className="text-sm text-gray-300 leading-relaxed">
                                    {comment.body}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          <div className="mt-4 pt-3 border-t border-gray-700">
                            <a
                              href={post.permalink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-red-400 hover:text-red-300 text-sm font-medium"
                            >
                              View on Reddit →
                            </a>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Trending Discussions */}
                <Card className="bg-gray-900/50 border-gray-800">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-500" />
                      Trending Discussions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {reddit_analysis.detailed_discussions.trending_discussions.slice(0, 6).map((discussion, index) => (
                        <motion.div
                          key={discussion.id}
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className="border border-gray-700 rounded-lg p-4 bg-gray-800/20 hover:bg-gray-800/40 transition-colors"
                        >
                          <div className="mb-3">
                            <h5 className="font-medium text-gray-200 mb-2 leading-tight line-clamp-2">
                              {discussion.title}
                            </h5>
                            <Badge variant="outline" className="text-xs">
                              r/{discussion.subreddit}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
                            <div className="text-center">
                              <div className="text-green-400 font-medium">{discussion.score}</div>
                              <div>upvotes</div>
                            </div>
                            <div className="text-center">
                              <div className="text-blue-400 font-medium">{discussion.comment_count}</div>
                              <div>comments</div>
                            </div>
                            <div className="text-center">
                              <div className="text-purple-400 font-medium">{discussion.engagement_score}</div>
                              <div>engagement</div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              // Fallback content if detailed discussions are not available
              <Card className="bg-gray-900/50 border-gray-800">
                <CardHeader>
                  <CardTitle>Community Discussions Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-400 mb-2">
                        {reddit_analysis.collection_summary.total_posts}
                      </div>
                      <div className="text-sm text-gray-400">Total Posts</div>
                    </div>
                    
                    <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-green-400 mb-2">
                        {reddit_analysis.collection_summary.total_subreddits}
                      </div>
                      <div className="text-sm text-gray-400">Subreddits</div>
                    </div>
                    
                    <div className="text-center p-4 bg-gray-800/50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-400 mb-2">
                        {reddit_analysis.collection_summary.date_range?.span_days || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-400">Days Analyzed</div>
                    </div>
                  </div>

                  {reddit_analysis.collection_summary.date_range && (
                    <div className="mt-6 p-4 bg-gray-800/30 rounded-lg">
                      <h4 className="font-semibold mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Discussion Timeline
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">First Discussion:</span>
                          <div className="font-semibold">
                            {formatDate(reddit_analysis.collection_summary.date_range.earliest)}
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-400">Latest Discussion:</span>
                          <div className="font-semibold">
                            {formatDate(reddit_analysis.collection_summary.date_range.latest)}
                          </div>
                        </div>
                        <div>
                          <span className="text-gray-400">Discussion Span:</span>
                          <div className="font-semibold">
                            {reddit_analysis.collection_summary.date_range.span_days} days
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Trends Tab */}
          <TabsContent value="trends">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle>Sentiment Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-4">Sentiment Distribution</h4>
                      <div className="space-y-3">
                        {Object.entries(reddit_analysis.sentiment_analysis.distribution).map(([sentiment, count]) => (
                          <div key={sentiment} className="flex justify-between items-center">
                            <span className="capitalize text-gray-400">{sentiment.replace('_', ' ')}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-gray-800 rounded-full h-2">
                                <div 
                                  className="bg-red-500 h-2 rounded-full" 
                                  style={{ 
                                    width: `${(count / Object.values(reddit_analysis.sentiment_analysis.distribution).reduce((a, b) => a + b, 1)) * 100}%` 
                                  }}
                                ></div>
                              </div>
                              <span className="text-sm font-medium">{count}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-4">Sentiment Statistics</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Average:</span>
                          <span className="font-medium">{reddit_analysis.sentiment_analysis.overall_sentiment.mean.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Median:</span>
                          <span className="font-medium">{reddit_analysis.sentiment_analysis.overall_sentiment.median.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Std Dev:</span>
                          <span className="font-medium">{reddit_analysis.sentiment_analysis.overall_sentiment.std.toFixed(3)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Keywords Tab */}
          <TabsContent value="keywords">
            <Card className="bg-gray-900/50 border-gray-800">
              <CardHeader>
                <CardTitle>Top Discussion Keywords</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {summary.top_keywords.slice(0, 20).map(([keyword, count], index) => (
                    <div key={keyword} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                      <span className="font-medium truncate">{keyword}</span>
                      <Badge variant="outline" className="ml-2">{count}</Badge>
                    </div>
                  ))}
                </div>
                
                {reddit_analysis.content_analysis?.keyword_analysis && (
                  <div className="mt-6 p-4 bg-gray-800/30 rounded-lg">
                    <h4 className="font-semibold mb-2">Keyword Statistics</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Total Keywords:</span>
                        <div className="font-semibold">
                          {reddit_analysis.content_analysis.keyword_analysis.top_keywords?.length || 0}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-400">Top Keywords:</span>
                        <div className="font-semibold">
                          {reddit_analysis.content_analysis.keyword_analysis.top_keywords?.[0]?.[0] || 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
