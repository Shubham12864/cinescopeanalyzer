"use client"

import { useState, useEffect, useCallback } from 'react'
import type { Movie } from '@/types/movie'

interface RecentlySearchedItem {
  query: string
  movie?: Movie
  timestamp: number
}

const STORAGE_KEY = 'cinescope-recently-searched'
const MAX_RECENT_ITEMS = 10

export function useRecentlySearched() {
  const [recentlySearched, setRecentlySearched] = useState<RecentlySearchedItem[]>([])

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        setRecentlySearched(parsed)
      }
    } catch (error) {
      console.error('Failed to load recently searched items:', error)
    }
  }, [])

  // Save to localStorage whenever items change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recentlySearched))
    } catch (error) {
      console.error('Failed to save recently searched items:', error)
    }
  }, [recentlySearched])

  const addRecentlySearched = useCallback((query: string, movie?: Movie) => {
    if (!query.trim()) return

    setRecentlySearched(prev => {
      // Remove existing item with same query (if any)
      const filtered = prev.filter(item => 
        item.query.toLowerCase() !== query.toLowerCase()
      )

      // Add new item at the beginning
      const newItem: RecentlySearchedItem = {
        query: query.trim(),
        movie,
        timestamp: Date.now()
      }

      const updated = [newItem, ...filtered]

      // Keep only the most recent items
      return updated.slice(0, MAX_RECENT_ITEMS)
    })
  }, [])

  const removeRecentlySearched = useCallback((query: string) => {
    setRecentlySearched(prev => 
      prev.filter(item => item.query.toLowerCase() !== query.toLowerCase())
    )
  }, [])

  const clearRecentlySearched = useCallback(() => {
    setRecentlySearched([])
  }, [])

  const getRecentQueries = useCallback(() => {
    return recentlySearched.map(item => item.query)
  }, [recentlySearched])

  const getRecentMovies = useCallback(() => {
    return recentlySearched
      .filter(item => item.movie)
      .map(item => item.movie!)
  }, [recentlySearched])

  return {
    recentlySearched,
    addRecentlySearched,
    removeRecentlySearched,
    clearRecentlySearched,
    getRecentQueries,
    getRecentMovies,
    hasRecentSearches: recentlySearched.length > 0
  }
}
