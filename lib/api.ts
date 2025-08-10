import type { Movie, Review, AnalyticsData, SearchFilters } from '@/types/movie'
import { clientCache, ClientCache } from './cache'
import { queueApiCall, queuePriorityRequest } from './request-queue'

// Robust API URL detection with fallbacks
const getApiBaseUrl = () => {
  // Check environment variable first
  if (typeof window !== 'undefined') {
    // Client-side: check for runtime environment
    const envUrl = process.env.NEXT_PUBLIC_API_URL
    if (envUrl) {
      console.log('🔗 Using API URL from environment:', envUrl)
      return envUrl
    }
  }
  
  // Fallback URLs based on current environment
  if (typeof window !== 'undefined') {
    const currentHost = window.location.hostname
    if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
      console.log('🔗 Using localhost fallback API URL')
      return 'http://localhost:8000'
    }
  }
  
  // Default fallback
  console.log('🔗 Using default API URL fallback')
  return 'http://localhost:8000'
}

const API_BASE_URL = getApiBaseUrl()

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
    
    // Add timeout to fetch
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000)
    
    const response = await fetch(url, {
      ...config,
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error(`❌ API Error: ${response.status} - ${errorData.detail || response.statusText}`)
      throw new ApiError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status
      )
    }

    const data = await response.json()
    console.log(`✅ API Success: ${url} - ${Array.isArray(data) ? data.length + ' items' : 'object'}`)
    return data
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    
    // Handle network errors
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error(`⏱️ API Timeout: ${url}`)
        throw new ApiError('Request timeout - please try again', 408)
      }
      
      if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
        console.error(`🌐 Network Error: ${url}`)
        throw new ApiError('Network error - please check your connection and ensure the backend is running', 0)
      }
    }
    
    console.error(`💥 API Unexpected Error: ${url}`, error)
    throw new ApiError(`Unexpected error: ${error}`, 500)
  }
}

export const movieApi = {
  async testConnection() {
    console.log(`🔗 Testing connection to: ${API_BASE_URL}`)
    
    // Try multiple endpoints for connection testing
    const endpoints = ['/health', '/api/health', '/']
    
    for (const endpoint of endpoints) {
      try {
        console.log(`🔗 Attempting connection to: ${API_BASE_URL}${endpoint}`)
        const result = await fetchApi<{status?: string, message?: string}>(endpoint)
        console.log(`✅ Connection successful via ${endpoint}:`, result)
        return result
      } catch (error) {
        console.warn(`⚠️ Connection failed via ${endpoint}:`, error)
        if (endpoint === endpoints[endpoints.length - 1]) {
          // This was the last endpoint, throw the error
          throw error
        }
        // Continue to next endpoint
        continue
      }
    }
  },
  async getMovies() {
    const cacheKey = 'movies:all'
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached

    const result = await fetchApi<Movie[]>('/api/movies')
    clientCache.set(cacheKey, result, 30 * 60 * 1000) // Cache for 30 minutes
    return result
  },
  async searchMovies(query: string, filters?: SearchFilters) {
    if (!query.trim()) return []
    
    // Generate cache key for search
    const cacheKey = ClientCache.generateSearchKey(query, filters)
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached
    
    const params = new URLSearchParams({ q: query })
    if (filters?.genre?.length) params.append('genre', filters.genre.join(','))
    if (filters?.year) params.append('year', filters.year.toString())
    if (filters?.rating) params.append('rating', filters.rating.toString())
    if (filters?.sortBy) params.append('sort', filters.sortBy)
    if (filters?.sortOrder) params.append('order', filters.sortOrder)
    
    // Use priority queue for search requests (high priority)
    const result = await queuePriorityRequest(
      () => fetchApi<Movie[]>(`/api/movies/search?${params.toString()}`),
      `search:${query}`
    )
    
    // Cache successful search results for 2 hours
    clientCache.set(cacheKey, result, 2 * 60 * 60 * 1000)
    return result
  },
  async getMovieById(id: string) {
    const cacheKey = ClientCache.generateMovieKey(id)
    const cached = clientCache.get<Movie>(cacheKey)
    if (cached) return cached

    const result = await fetchApi<Movie>(`/api/movies/${id}`)
    clientCache.set(cacheKey, result, 60 * 60 * 1000) // Cache for 1 hour
    return result
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
  async getPopularMovies(limit?: number) {
    const cacheKey = ClientCache.generatePopularKey(limit)
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached

    const params = limit ? `?limit=${limit}` : ''
    
    // Use API queue for better concurrent request handling
    const result = await queueApiCall(
      () => fetchApi<Movie[]>(`/api/movies/popular${params}`),
      `popular:${limit || 'all'}`,
      5 // Medium-high priority
    )
    
    clientCache.set(cacheKey, result, 30 * 60 * 1000) // Cache for 30 minutes
    return result
  },
  async getRecentMovies(limit?: number) {
    const cacheKey = `recent:${limit || 'all'}`
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached

    const params = limit ? `?limit=${limit}` : ''
    const result = await fetchApi<Movie[]>(`/api/movies/recent${params}`)
    clientCache.set(cacheKey, result, 15 * 60 * 1000) // Cache for 15 minutes (more recent data)
    return result
  },
  async getTrendingMovies(limit?: number) {
    const cacheKey = `trending:${limit || 'all'}`
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached

    const params = limit ? `?limit=${limit}` : ''
    
    // Use API queue for trending movies with high priority
    const result = await queueApiCall(
      () => fetchApi<Movie[]>(`/api/movies/trending${params}`),
      `trending:${limit || 'all'}`,
      8 // High priority for trending content
    )
    
    clientCache.set(cacheKey, result, 15 * 60 * 1000) // Cache for 15 minutes (trending changes frequently)
    return result
  },
  async getSuggestions(limit?: number) {
    const cacheKey = `suggestions:${limit || 'all'}`
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached

    const params = limit ? `?limit=${limit}` : ''
    const result = await fetchApi<Movie[]>(`/api/movies/suggestions${params}`)
    clientCache.set(cacheKey, result, 30 * 60 * 1000) // Cache for 30 minutes
    return result
  },
  async getTopRatedMovies(limit?: number) {
    const cacheKey = `top-rated:${limit || 'all'}`
    const cached = clientCache.get<Movie[]>(cacheKey)
    if (cached) return cached

    const params = limit ? `?limit=${limit}` : ''
    const result = await fetchApi<Movie[]>(`/api/movies/top-rated${params}`)
    clientCache.set(cacheKey, result, 60 * 60 * 1000) // Cache for 1 hour (top rated changes slowly)
    return result
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
