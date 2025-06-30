import type { Movie, Review, AnalyticsData, SearchFilters, ApiResponse, PaginatedResponse } from '@/types/movie'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }
  try {
    console.log(`🔗 API Call: ${url}`)
    const response = await fetch(url, config)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error(`❌ API Error: ${response.status} - ${errorData.detail || response.statusText}`)
      throw new ApiError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status
      )
    }
    const data = await response.json()
    console.log(`✅ API Response:`, data)
    return data
  } catch (error) {
    console.error('🚨 API call failed:', error)
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError('Network error occurred')
  }
}

export const movieApi = {
  async testConnection() {
    return fetchApi<{status: string, message: string}>('/api/health')
  },
  async getMovies() {
    return fetchApi<Movie[]>('/api/movies')
  },
  async searchMovies(query: string, filters?: SearchFilters) {
    if (!query.trim()) return []
    
    const params = new URLSearchParams({ q: query })
    if (filters?.genre?.length) params.append('genre', filters.genre.join(','))
    if (filters?.year) params.append('year', filters.year.toString())
    if (filters?.rating) params.append('rating', filters.rating.toString())
    if (filters?.sortBy) params.append('sort', filters.sortBy)
    if (filters?.sortOrder) params.append('order', filters.sortOrder)
    
    return fetchApi<Movie[]>(`/api/movies/search?${params.toString()}`)
  },
  async getMovieById(id: string) {
    return fetchApi<Movie>(`/api/movies/${id}`)
  },
  async analyzeMovie(movieId: string) {
    return fetchApi<{taskId: string, message: string}>(`/api/movies/${movieId}/analyze`, {
      method: 'POST'
    })
  },  async getMovieAnalysis(movieId: string) {
    return fetchApi<AnalyticsData>(`/api/movies/${movieId}/analysis`)
  },
  async getAnalytics() {
    return fetchApi<AnalyticsData>('/api/analytics')
  },
  async getPopularMovies() {
    return fetchApi<Movie[]>('/api/movies/popular')
  },
  async getRecentMovies() {
    return fetchApi<Movie[]>('/api/movies/recent')
  },
  async getTrendingMovies() {
    return fetchApi<Movie[]>('/api/movies/trending')
  },
  async getSuggestions() {
    return fetchApi<Movie[]>('/api/movies/suggestions')
  },
  async getMovieReviews(movieId: string) {
    return fetchApi<Review[]>(`/api/movies/${movieId}/reviews`)
  },
  async addMovieReview(movieId: string, reviewData: {
    author: string
    content: string
    rating: number
    sentiment?: string
  }) {
    return fetchApi<{message: string, review: Review}>(`/api/movies/${movieId}/reviews`, {
      method: 'POST',
      body: JSON.stringify(reviewData)
    })
  },
  async updateMovieReview(movieId: string, reviewId: string, reviewData: {
    author?: string
    content?: string
    rating?: number
    sentiment?: string
  }) {
    return fetchApi<{message: string, review: Review}>(`/api/movies/${movieId}/reviews/${reviewId}`, {
      method: 'PUT',
      body: JSON.stringify(reviewData)
    })
  },
  async deleteMovieReview(movieId: string, reviewId: string) {
    return fetchApi<{message: string}>(`/api/movies/${movieId}/reviews/${reviewId}`, {
      method: 'DELETE'
    })
  }
}

// Utility functions
export const formatRating = (rating: number): string => {
  return rating.toFixed(1)
}

export const formatYear = (year: string | number): string => {
  return year.toString()
}

export const getSentimentColor = (sentiment?: string): string => {
  switch (sentiment) {
    case 'positive': return 'text-green-400'
    case 'negative': return 'text-red-400'
    case 'neutral': return 'text-gray-400'
    default: return 'text-gray-400'
  }
}

export const getSentimentBadgeColor = (sentiment?: string): string => {
  switch (sentiment) {
    case 'positive': return 'bg-green-600/20 text-green-300 border-green-600'
    case 'negative': return 'bg-red-600/20 text-red-300 border-red-600'
    case 'neutral': return 'bg-gray-600/20 text-gray-300 border-gray-600'
    default: return 'bg-gray-600/20 text-gray-300 border-gray-600'
  }
}

export { ApiError }
