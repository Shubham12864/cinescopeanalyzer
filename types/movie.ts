export interface Movie {
  id: string
  title: string
  year: number
  poster: string
  rating: number
  genre: string[]
  plot: string
  reviews?: Review[]
  imdbId?: string
  tmdbId?: string
  runtime?: number
  director?: string
  cast?: string[]
  country?: string
  language?: string
  // Additional poster sources (prioritized over TMDB)
  omdbPoster?: string
  scrapedPoster?: string
  imdbPoster?: string
}

export interface Review {
  id: string
  author: string
  content: string
  rating: number
  sentiment: "positive" | "negative" | "neutral"
  date: string
  source?: string
  helpfulVotes?: number
}

export interface AnalyticsData {
  totalMovies: number
  totalReviews: number
  averageRating: number
  sentimentDistribution: {
    positive: number
    negative: number
    neutral: number
  }
  ratingDistribution: number[]
  genrePopularity: { genre: string; count: number }[]
  reviewTimeline: { date: string; count: number; sentiment?: string }[]
  topRatedMovies: Movie[]
  recentlyAnalyzed: Movie[]
}

export interface SearchFilters {
  genre?: string[]
  year?: number
  rating?: number
  sortBy?: 'rating' | 'year' | 'title' | 'reviews'
  sortOrder?: 'asc' | 'desc'
}

export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  page: number
  totalPages: number
  totalItems: number
  hasNext: boolean
  hasPrevious: boolean
}
