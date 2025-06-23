"use client"

import { motion } from "framer-motion"
import { useState, useEffect } from "react"
import { SentimentChart } from "./sentiment-chart"
import { RatingDistribution } from "./rating-distribution"
import { GenrePopularity } from "./genre-popularity"
import { ReviewTimeline } from "./review-timeline"
import { TrendingUp, Users, Star, MessageSquare } from "lucide-react"
import { movieApi } from "@/lib/api"
import type { AnalyticsData } from "@/types/movie"

const stats = [
  {
    title: "Total Reviews",
    value: "12,847",
    change: "+12.5%",
    icon: MessageSquare,
    color: "from-blue-500 to-cyan-500",
  },
  {
    title: "Average Rating",
    value: "7.8",
    change: "+0.3",
    icon: Star,
    color: "from-yellow-500 to-orange-500",
  },
  {
    title: "Active Users",
    value: "3,421",
    change: "+8.2%",
    icon: Users,
    color: "from-green-500 to-emerald-500",
  },
  {
    title: "Trending Score",
    value: "94.2",
    change: "+5.7%",
    icon: TrendingUp,
    color: "from-purple-500 to-pink-500",
  },
]

export function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await movieApi.getAnalytics()
        setAnalytics(data)
      } catch (error) {
        console.error('Failed to fetch analytics:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-500"></div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Failed to load analytics data</p>
      </div>
    )
  }

  const stats = [
    {
      title: "Total Reviews", 
      value: analytics.totalReviews.toLocaleString(),
      change: "+12.5%",
      icon: MessageSquare,
      color: "from-blue-500 to-cyan-500",
    },
    {
      title: "Average Rating",
      value: analytics.averageRating.toFixed(1),
      change: "+0.3",
      icon: Star,
      color: "from-yellow-500 to-orange-500",
    },
    {
      title: "Total Movies",
      value: analytics.totalMovies.toLocaleString(),
      change: "+8.2%",
      icon: Users,
      color: "from-green-500 to-emerald-500",
    },
    {
      title: "Positive Sentiment",
      value: analytics.totalReviews > 0 
        ? `${Math.round((analytics.sentimentDistribution.positive / analytics.totalReviews) * 100)}%`
        : "0%",
      change: "+2.1%",
      icon: TrendingUp,
      color: "from-purple-500 to-pink-500",
    },
  ]
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold font-poppins text-white">Analytics Dashboard</h2>
        <div className="flex gap-2">
          <button className="glass px-4 py-2 rounded-lg text-gray-300 hover:text-white transition-colors">
            Last 7 days
          </button>
          <button className="bg-gradient-to-r from-coral to-teal px-4 py-2 rounded-lg text-white font-medium">
            Export Data
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="glass-strong rounded-2xl p-6 relative overflow-hidden"
          >
            <div
              className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${stat.color} opacity-10 rounded-full -mr-10 -mt-10`}
            />
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <stat.icon className="w-8 h-8 text-gray-400" />
                <span className="text-sm text-green-400 font-medium">{stat.change}</span>
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-gray-400 text-sm">{stat.title}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <SentimentChart data={{
            positive: analytics.sentimentDistribution.positive,
            negative: analytics.sentimentDistribution.negative,
            neutral: analytics.sentimentDistribution.neutral,
          }} />
        </motion.div>        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <RatingDistribution data={{
            ratings: analytics.ratingDistribution,
          }} />
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <GenrePopularity />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >          <ReviewTimeline data={{
            months: analytics.reviewTimeline.map(item => item.date),
            reviewCounts: analytics.reviewTimeline.map(item => typeof item.count === 'string' ? parseInt(item.count) : item.count),
          }} />
        </motion.div>
      </div>
    </motion.div>
  )
}
