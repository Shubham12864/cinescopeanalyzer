"use client"

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { movieApi } from '@/lib/api'
import type { Movie, SearchFilters } from '@/types/movie'
import type { ToastData } from '@/components/ui/toast'
import { useRecentlySearched } from '@/hooks/useRecentlySearched'
import { SearchDebouncer } from '@/lib/debounce'
import { clientCache, ClientCache } from '@/lib/cache'

interface MovieContextType {
  movies: Movie[]
  isLoading: boolean
  error: string | null
  searchQuery: string
  selectedMovie: Movie | null
  filters: SearchFilters
  isBackendConnected: boolean
  isDemoMode: boolean
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
  
  // Create search debouncer with 500ms delay as per requirements
  const searchDebouncerRef = useRef(new SearchDebouncer(500))

  // Toast functions
  const addToast = useCallback((toast: Omit<ToastData, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 11)
    setToasts(prev => [...prev, { ...toast, id }])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])
  // Track connection state changes for notifications
  const [previousConnectionState, setPreviousConnectionState] = useState<boolean | null>(null)
  const [isInitialLoad, setIsInitialLoad] = useState(true)
  const [isDemoMode, setIsDemoMode] = useState(false)
  
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
        setIsDemoMode(false)
        addToast({
          type: 'success',
          title: 'Backend Connected',
          description: 'Real movie data is now available',
          duration: 3000
        })
      } else {
        setIsDemoMode(true)
        addToast({
          type: 'error',
          title: 'Backend Unavailable',
          description: 'Using demo mode - limited functionality available',
          duration: 5000
        })
      }
    }
    setPreviousConnectionState(isBackendConnected)
  }, [isBackendConnected, addToast, isInitialLoad])
  const clearError = useCallback(() => {
    setError(null)
  }, [])
  // Remove demo data - force real backend connection
  const loadMockData = useCallback(() => {
    console.log('❌ No demo data - backend connection required')
    setMovies([])
    setError('Backend connection required for movie data')
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
      console.error('❌ Failed to load movies from backend:', err)
      
      // Provide user-friendly error messages
      if (err instanceof Error) {
        if (err.message.includes('Network error') || err.message.includes('Failed to fetch')) {
          setError('Unable to load movies - please check your internet connection')
        } else if (err.message.includes('timeout')) {
          setError('Request timed out - server may be busy')
        } else {
          setError('Failed to load movies from server')
        }
      } else {
        setError('Failed to fetch movies')
      }
      
      // Only use mock data if backend is truly unreachable
      console.log('❌ Backend unavailable - no movies to display')
      setError('Backend connection required - no demo data available')
      setMovies([])
      setIsBackendConnected(false)
      setIsDemoMode(false) // No demo mode
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
      // Cancel any pending debounced searches
      searchDebouncerRef.current.cancel()
      await refreshMovies()
      return
    }

    // Show loading state immediately for better UX
    setIsLoading(true)
    setError(null)
    
    try {
      // Use debounced search to reduce API calls with enhanced caching
      const debouncedSearchFn = async (searchQuery: string, signal?: AbortSignal) => {
        console.log(`🔍 Debounced search executing for: "${searchQuery}"`)
        
        try {
          // Pass abort signal to API call if supported
          const result = await movieApi.searchMovies(searchQuery, filters)
          
          // Cache successful results for 2 hours as per requirements
          if (result && result.length > 0) {
            clientCache.set(cacheKey, result, 2 * 60 * 60 * 1000) // 2 hours
            console.log(`💾 Cached search results for: "${searchQuery}" (${result.length} movies)`)
          }
          
          return result
        } catch (error) {
          console.error(`❌ Search API call failed for "${searchQuery}":`, error)
          throw error
        }
      }
      
      const data = await searchDebouncerRef.current.search(debouncedSearchFn, query)
      
      if (data && data.length > 0) {
        setMovies(data)
        setIsBackendConnected(true) // Update connection state on successful search
        console.log(`✅ Debounced search found ${data.length} movies for "${query}"`)
        
        // Add to recently searched with first result
        const firstResult = data[0]
        addRecentlySearched(query, firstResult)
      } else {
        // Backend responded but no results found - this is a valid response
        setMovies([])
        setIsBackendConnected(true) // Backend is working, just no results
        console.log(`ℹ️ Debounced search returned no results for "${query}"`)
        addRecentlySearched(query)
      }
      
    } catch (err) {
      // Don't handle errors if the search was cancelled (debounced)
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('🚫 Search was cancelled due to debouncing')
        return
      }
      
      console.error('❌ Debounced search failed:', err)
      setIsBackendConnected(false) // Mark backend as disconnected
      setIsDemoMode(false) // No demo mode
      
      // Provide specific, user-friendly error messages
      if (err instanceof Error) {
        if (err.message.includes('Network error') || err.message.includes('Failed to fetch')) {
          setError('Unable to connect to server. Please check your internet connection and try again.')
          addToast({
            type: 'error',
            title: 'Connection Failed',
            description: 'Cannot reach the movie database server',
            duration: 4000
          })
        } else if (err.message.includes('timeout')) {
          setError('Search request timed out. The server may be busy - please try again.')
          addToast({
            type: 'error',
            title: 'Request Timeout',
            description: 'Server is taking too long to respond',
            duration: 4000
          })
        } else if (err.message.includes('404')) {
          setError('Movie database service is temporarily unavailable.')
        } else if (err.message.includes('500')) {
          setError('Server error occurred. Please try again in a few moments.')
        } else {
          setError(`Search failed: ${err.message}`)
        }
      } else {
        setError('Unable to search movies. Please check your connection and try again.')
      }
      
      // Set empty results - no demo data fallback
      setMovies([])
      console.log(`❌ Debounced search failed for "${query}" - showing empty results with clear error message`)
      
      // Still add to recently searched to track the attempt
      addRecentlySearched(query)
    } finally {
      setIsLoading(false)
    }
  }, [refreshMovies, filters, addRecentlySearched])
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
        setError('Backend connection required - no movies available')
        setMovies([])
      }
    } catch (error) {
      console.error('❌ Backend connection failed:', error)
      setIsBackendConnected(false)
      setError('Backend connection failed - no movies available')
      setMovies([])
    }
  }, [loadMockData])

  const analyzeMovie = useCallback(async (movieId: string) => {
    if (!isBackendConnected) {
      setError('Cannot analyze movie: Backend not connected')
      addToast({
        type: 'error',
        title: 'Analysis Unavailable',
        description: 'Backend connection required for movie analysis',
        duration: 4000
      })
      return
    }

    try {
      setIsLoading(true)
      const result = await movieApi.analyzeMovie(movieId)
      console.log(`✅ Movie analysis started: ${result.taskId}`)
      
      // Clear any previous errors
      setError(null)
      
      // Show success notification
      addToast({
        type: 'success',
        title: 'Analysis Started',
        description: 'Movie analysis is now in progress',
        duration: 3000
      })
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed'
      setError(errorMessage)
      console.error('❌ Movie analysis failed:', error)
      
      // Show error notification
      addToast({
        type: 'error',
        title: 'Analysis Failed',
        description: 'Unable to start movie analysis - please try again',
        duration: 4000
      })
    } finally {
      setIsLoading(false)
    }
  }, [isBackendConnected, addToast])  // Test connection and load data on mount
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
    isDemoMode,
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
