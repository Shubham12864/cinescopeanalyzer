"use client"

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { movieApi } from '@/lib/api'
import type { Movie, SearchFilters } from '@/types/movie'
import { useRecentlySearched } from '@/hooks/useRecentlySearched'

interface ToastData {
  id: string
  type: 'success' | 'error' | 'info'
  title: string
  description?: string
  duration?: number
}

interface MovieContextType {
  movies: Movie[]
  isLoading: boolean
  error: string | null
  searchQuery: string
  selectedMovie: Movie | null
  filters: SearchFilters
  isBackendConnected: boolean
  toasts: ToastData[]
  setSearchQuery: (query: string) => void
  setSelectedMovie: (movie: Movie | null) => void
  setFilters: (filters: SearchFilters) => void
  refreshMovies: () => Promise<void>
  searchMoviesHandler: (query: string) => Promise<void>
  clearSearch: () => Promise<void>
  getMovieById: (id: string) => Promise<Movie | null>
  analyzeMovie: (movieId: string) => Promise<void>
  clearError: () => void
  testConnection: () => Promise<void>
  addToast: (toast: Omit<ToastData, 'id'>) => void
  removeToast: (id: string) => void
}

const MovieContext = createContext<MovieContextType | undefined>(undefined)

export function useMovieContext() {
  const context = useContext(MovieContext)
  if (!context) {
    throw new Error('useMovieContext must be used within a MovieProvider')
  }
  return context
}

export function MovieProvider({ children }: { children: React.ReactNode }) {
  const [movies, setMovies] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null)
  const [filters, setFilters] = useState<SearchFilters>({})
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [toasts, setToasts] = useState<ToastData[]>([])
  const { addRecentlySearched } = useRecentlySearched()

  // Toast functions
  const addToast = useCallback((toast: Omit<ToastData, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    setToasts(prev => [...prev, { ...toast, id }])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])
  // Track connection state changes for notifications
  const [previousConnectionState, setPreviousConnectionState] = useState<boolean | null>(null)
  const [isInitialLoad, setIsInitialLoad] = useState(true)
  
  useEffect(() => {
    // Don't show notifications on initial load
    if (isInitialLoad) {
      setIsInitialLoad(false)
      setPreviousConnectionState(isBackendConnected)
      return
    }
    
    // Show notifications for connection state changes
    if (previousConnectionState !== null && previousConnectionState !== isBackendConnected) {
      if (isBackendConnected) {
        addToast({
          type: 'success',
          title: 'Backend Connected',
          description: 'Successfully connected to server',
          duration: 3000
        })
      } else {
        addToast({
          type: 'error',
          title: 'Backend Disconnected',
          description: 'Switched to demo mode',
          duration: 4000
        })
      }
    }
    setPreviousConnectionState(isBackendConnected)
  }, [isBackendConnected, addToast, isInitialLoad])
  const clearError = useCallback(() => {
    setError(null)
  }, [])
  const loadMockData = useCallback(() => {
    // Fallback mock data when backend is not available
    const mockMovies: Movie[] = [
      {
        id: '1',
        title: 'The Dark Knight',
        plot: 'Batman faces the Joker in Gotham City',
        rating: 9.0,
        genre: ['Action', 'Crime', 'Drama'],
        year: 2008,
        poster: 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
        omdbPoster: 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg',
        reviews: [],
        imdbId: 'tt0468569',
        runtime: 152,
        cast: ['Christian Bale', 'Heath Ledger', 'Aaron Eckhart'],
        director: 'Christopher Nolan'
      },      {
        id: '2',
        title: 'Inception',
        plot: 'A thief enters dreams to steal secrets',
        rating: 8.8,
        genre: ['Action', 'Sci-Fi', 'Thriller'],
        year: 2010,
        poster: 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
        omdbPoster: 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg',
        reviews: [],
        imdbId: 'tt1375666',
        runtime: 148,
        cast: ['Leonardo DiCaprio', 'Marion Cotillard', 'Tom Hardy'],
        director: 'Christopher Nolan'
      },
      {
        id: '3',
        title: 'The Matrix',
        plot: 'A computer hacker discovers reality is a simulation',
        rating: 8.7,
        genre: ['Action', 'Sci-Fi'],
        year: 1999,
        poster: 'https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg',
        omdbPoster: 'https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg',
        reviews: [],
        imdbId: 'tt0133093',
        runtime: 136,
        cast: ['Keanu Reeves', 'Laurence Fishburne', 'Carrie-Anne Moss'],
        director: 'The Wachowskis'
      }
    ]
    setMovies(mockMovies)
    console.log('📦 Loaded mock data with', mockMovies.length, 'movies')
  }, [])

  const getMovieById = useCallback(async (id: string): Promise<Movie | null> => {
    try {
      const movie = await movieApi.getMovieById(id)
      return movie
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch movie')
      return null
    }
  }, [])

  const refreshMovies = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      console.log('🔄 Refreshing movies...')
      
      // Always try backend first, even if we think it's disconnected
      let data: Movie[] = []
      
      try {
        // First try to get popular movies
        console.log('📡 Attempting to fetch popular movies from backend...')
        data = await movieApi.getPopularMovies(12)
        console.log(`✅ Loaded ${data.length} popular movies from backend`)
        setIsBackendConnected(true)
      } catch (popularError) {
        console.warn('⚠️ Popular movies failed, trying general movies endpoint:', popularError)
        try {
          data = await movieApi.getMovies()
          console.log(`✅ Loaded ${data.length} movies from general endpoint`)
          setIsBackendConnected(true)
        } catch (generalError) {
          console.warn('⚠️ General movies endpoint also failed:', generalError)
          throw generalError
        }
      }
      
      if (data && data.length > 0) {
        setMovies(data)
        console.log(`✅ Successfully set ${data.length} movies in state`)
      } else {
        console.warn('⚠️ Backend returned empty data, falling back to mock data')
        throw new Error('Empty response from backend')
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch movies')
      console.error('❌ Failed to load movies from backend:', err)
      
      // Only use mock data if backend is truly unreachable
      if (!isBackendConnected) {
        console.log('📦 Backend unavailable, loading mock data')
        loadMockData()
      } else {
        console.log('🔄 Backend seems connected but request failed, retrying connection test...')
        setIsBackendConnected(false)
        loadMockData()
      }
    } finally {
      setIsLoading(false)
    }
  }, [isBackendConnected, loadMockData])
  const clearSearch = useCallback(async () => {
    setSearchQuery('')
    setError(null)
    await refreshMovies()
  }, [refreshMovies])

  const searchMoviesHandler = useCallback(async (query: string) => {
    console.log(`🔍 Search triggered for: "${query}"`)
    
    // Always set the search query to trigger UI update
    setSearchQuery(query)
    
    if (!query.trim()) {
      console.log('🔄 Empty query, refreshing movies')
      setSearchQuery('') // Clear search query for empty searches
      await refreshMovies()
      return
    }

    if (!isBackendConnected) {
      // Filter mock data for search
      const filtered = movies.filter(movie => 
        movie.title.toLowerCase().includes(query.toLowerCase()) ||
        movie.genre.some(g => g.toLowerCase().includes(query.toLowerCase())) ||
        movie.plot.toLowerCase().includes(query.toLowerCase())
      )
      setMovies(filtered)
      console.log(`🔍 Mock search found ${filtered.length} movies for "${query}"`)
      
      // Add to recently searched with first result if available
      const firstResult = filtered.length > 0 ? filtered[0] : undefined
      addRecentlySearched(query, firstResult)
      return
    }

    setIsLoading(true)
    setError(null)
    try {
      console.log(`🔍 Searching backend for: "${query}"`)
      const data = await movieApi.searchMovies(query, filters)
      setMovies(data)
      console.log(`✅ Search found ${data.length} movies for "${query}"`)
      
      // Add to recently searched with first result if available
      const firstResult = data.length > 0 ? data[0] : undefined
      addRecentlySearched(query, firstResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search movies')
      console.error('❌ Search failed:', err)
      // Still add to recently searched even if search failed
      addRecentlySearched(query)
    } finally {
      setIsLoading(false)
    }
  }, [refreshMovies, isBackendConnected, movies, filters, addRecentlySearched])
  const testConnection = useCallback(async () => {
    try {
      console.log('🔗 Testing backend connection...')
      const result = await movieApi.testConnection()
      console.log('✅ Backend connection successful:', result)
      setIsBackendConnected(true)
      
      // Load real movies data immediately after successful connection
      try {
        console.log('📡 Loading movies from backend after connection test...')
        
        // Try multiple endpoints to get real data
        let moviesData: Movie[] = []
        
        try {
          moviesData = await movieApi.getPopularMovies(20)
          console.log(`✅ Loaded ${moviesData.length} popular movies`)
        } catch (popularError) {
          console.warn('⚠️ Popular movies failed, trying suggestions...', popularError)
          try {
            moviesData = await movieApi.getSuggestions(20)
            console.log(`✅ Loaded ${moviesData.length} movie suggestions`)
          } catch (suggestionsError) {
            console.warn('⚠️ Suggestions failed, trying general movies...', suggestionsError)
            moviesData = await movieApi.getMovies()
            console.log(`✅ Loaded ${moviesData.length} general movies`)
          }
        }
        
        if (moviesData && moviesData.length > 0) {
          setMovies(moviesData)
          console.log(`✅ Successfully loaded ${moviesData.length} real movies from backend`)
        } else {
          console.warn('⚠️ All endpoints returned empty data')
          throw new Error('No movies available from backend')
        }
        
      } catch (movieError) {
        console.error('❌ Failed to load any movies from backend:', movieError)
        setIsBackendConnected(false)
        loadMockData()
      }
    } catch (error) {
      console.error('❌ Backend connection failed:', error)
      setIsBackendConnected(false)
      loadMockData()
    }
  }, [loadMockData])

  const analyzeMovie = useCallback(async (movieId: string) => {
    if (!isBackendConnected) {
      setError('Cannot analyze movie: Backend not connected')
      return
    }

    try {
      setIsLoading(true)
      const result = await movieApi.analyzeMovie(movieId)
      console.log(`✅ Movie analysis started: ${result.taskId}`)
      
      // Clear any previous errors
      setError(null)
      
      // You can add navigation logic here if needed
      // For now, we'll just log success
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed'
      setError(errorMessage)
      console.error('❌ Movie analysis failed:', error)
    } finally {
      setIsLoading(false)
    }
  }, [isBackendConnected])  // Test connection and load data on mount
  useEffect(() => {
    const initializeApp = async () => {
      console.log('🚀 Initializing CineScope app...')
      
      // Always try to connect to backend first
      try {
        await testConnection()
        console.log('✅ App initialization completed with backend connection')
      } catch (error) {
        console.warn('⚠️ App initialized with mock data fallback:', error)
      }
    }
    
    initializeApp()
  }, [testConnection])
  
  // Also load movies when backend connection state changes
  useEffect(() => {
    if (isBackendConnected) {
      console.log('🔄 Backend connected, loading fresh movies...')
      refreshMovies()
    }
  }, [isBackendConnected, refreshMovies])
    const value: MovieContextType = {
    movies,
    isLoading,
    error,
    searchQuery,
    selectedMovie,
    filters,
    isBackendConnected,
    toasts,
    setSearchQuery,
    setSelectedMovie,
    setFilters,
    refreshMovies,
    searchMoviesHandler,
    clearSearch,
    getMovieById,
    analyzeMovie,
    clearError,
    testConnection,
    addToast,
    removeToast,
  }

  return (
    <MovieContext.Provider value={value}>
      {children}
    </MovieContext.Provider>
  )
}
