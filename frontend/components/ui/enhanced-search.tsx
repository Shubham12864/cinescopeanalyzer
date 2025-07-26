/**
 * ENHANCED SEARCH COMPONENT
 * Fast, smooth, dynamic search with debouncing and caching
 * Works with the new robust backend API
 */
"use client"

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Search, X, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Movie } from '@/types/movie'

interface EnhancedSearchProps {
  onResults: (movies: Movie[], query: string) => void
  onLoading: (loading: boolean) => void
  placeholder?: string
  className?: string
  autoFocus?: boolean
}

export function EnhancedSearch({
  onResults,
  onLoading,
  placeholder = "Search movies...",
  className,
  autoFocus = false
}: EnhancedSearchProps) {
  
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const searchInputRef = useRef<HTMLInputElement>(null)
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const searchCacheRef = useRef<Map<string, { results: Movie[], timestamp: number }>>(new Map())
  
  // Cache TTL (5 minutes)
  const CACHE_TTL = 5 * 60 * 1000
  
  // Debounce delay
  const DEBOUNCE_DELAY = 300
  
  // Popular search suggestions
  const popularSearches = [
    'Batman', 'Inception', 'Marvel', 'Avatar', 'Star Wars',
    'Lord of the Rings', 'Harry Potter', 'John Wick', 'Mission Impossible',
    'Fast and Furious', 'Transformers', 'Jurassic Park'
  ]

  // Get API base URL
  const getApiUrl = useCallback(() => {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }, [])

  // Check cache for existing results
  const getCachedResults = useCallback((searchQuery: string): Movie[] | null => {
    const cached = searchCacheRef.current.get(searchQuery.toLowerCase())
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
      return cached.results
    }
    return null
  }, [])

  // Cache search results
  const cacheResults = useCallback((searchQuery: string, results: Movie[]) => {
    searchCacheRef.current.set(searchQuery.toLowerCase(), {
      results,
      timestamp: Date.now()
    })
    
    // Clean old cache entries (keep only last 50)
    if (searchCacheRef.current.size > 50) {
      const entries = Array.from(searchCacheRef.current.entries())
      entries.sort((a, b) => b[1].timestamp - a[1].timestamp)
      searchCacheRef.current.clear()
      entries.slice(0, 50).forEach(([key, value]) => {
        searchCacheRef.current.set(key, value)
      })
    }
  }, [])

  // Perform search with enhanced error handling
  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      onResults([], '')
      setSuggestions([])
      return
    }

    // Check cache first
    const cachedResults = getCachedResults(searchQuery)
    if (cachedResults) {
      console.log('📦 Using cached results for:', searchQuery)
      onResults(cachedResults, searchQuery)
      return
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    abortControllerRef.current = new AbortController()
    
    try {
      setIsLoading(true)
      setError(null)
      onLoading(true)
      
      const apiUrl = getApiUrl()
      const searchUrl = `${apiUrl}/api/movies/search?q=${encodeURIComponent(searchQuery)}&limit=20`
      
      console.log('🔍 Searching:', searchUrl)
      
      const response = await fetch(searchUrl, {
        signal: abortControllerRef.current.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`)
      }

      const movies: Movie[] = await response.json()
      
      console.log(`✅ Search results: ${movies.length} movies for "${searchQuery}"`)
      
      // Cache results
      cacheResults(searchQuery, movies)
      
      // Update results
      onResults(movies, searchQuery)
      
      // Update suggestions based on successful search
      if (movies.length > 0) {
        const newSuggestions = movies.slice(0, 5).map(movie => movie.title)
        setSuggestions(newSuggestions)
      }
      
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('🚫 Search aborted')
        return
      }
      
      console.error('❌ Search error:', error)
      setError(error.message || 'Search failed')
      
      // Show empty results on error
      onResults([], searchQuery)
      
    } finally {
      setIsLoading(false)
      onLoading(false)
    }
  }, [onResults, onLoading, getCachedResults, cacheResults, getApiUrl])

  // Debounced search
  const debouncedSearch = useCallback((searchQuery: string) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }
    
    searchTimeoutRef.current = setTimeout(() => {
      performSearch(searchQuery)
    }, DEBOUNCE_DELAY)
  }, [performSearch])

  // Handle input change
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    
    if (value.trim()) {
      debouncedSearch(value.trim())
      // Show suggestions that match the current query
      const filteredSuggestions = popularSearches.filter(suggestion =>
        suggestion.toLowerCase().includes(value.toLowerCase())
      )
      setSuggestions(filteredSuggestions.slice(0, 5))
      setShowSuggestions(true)
    } else {
      setSuggestions(popularSearches.slice(0, 5))
      setShowSuggestions(false)
      onResults([], '')
    }
  }, [debouncedSearch, onResults])

  // Handle suggestion click
  const handleSuggestionClick = useCallback((suggestion: string) => {
    setQuery(suggestion)
    setShowSuggestions(false)
    performSearch(suggestion)
  }, [performSearch])

  // Clear search
  const clearSearch = useCallback(() => {
    setQuery('')
    setSuggestions([])
    setShowSuggestions(false)
    setError(null)
    onResults([], '')
    if (searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [onResults])

  // Handle key events
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false)
    }
    if (e.key === 'Enter' && query.trim()) {
      setShowSuggestions(false)
      performSearch(query.trim())
    }
  }, [query, performSearch])

  // Focus handling
  const handleFocus = useCallback(() => {
    if (query.trim()) {
      setShowSuggestions(true)
    } else {
      setSuggestions(popularSearches.slice(0, 5))
      setShowSuggestions(true)
    }
  }, [query])

  const handleBlur = useCallback(() => {
    // Delay hiding suggestions to allow clicking
    setTimeout(() => setShowSuggestions(false), 200)
  }, [])

  // Auto focus
  useEffect(() => {
    if (autoFocus && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [autoFocus])

  // Cleanup
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return (
    <div className={cn("relative w-full max-w-2xl mx-auto", className)}>
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          {isLoading ? (
            <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
          ) : (
            <Search className="h-5 w-5 text-gray-400" />
          )}
        </div>
        
        <input
          ref={searchInputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          className={cn(
            "block w-full pl-10 pr-10 py-3 text-lg",
            "bg-gray-800 border border-gray-700 rounded-xl",
            "text-white placeholder-gray-400",
            "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "transition-all duration-200 ease-in-out",
            "hover:border-gray-600"
          )}
        />
        
        {query && (
          <button
            onClick={clearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-300 transition-colors"
          >
            <X className="h-5 w-5 text-gray-400" />
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-2 p-3 bg-red-900/20 border border-red-500/20 rounded-lg">
          <p className="text-red-400 text-sm">❌ {error}</p>
        </div>
      )}

      {/* Suggestions Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl overflow-hidden">
          <div className="py-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className={cn(
                  "w-full px-4 py-2 text-left text-white hover:bg-gray-700",
                  "transition-colors duration-150 flex items-center space-x-2"
                )}
              >
                <Search className="h-4 w-4 text-gray-400" />
                <span>{suggestion}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
