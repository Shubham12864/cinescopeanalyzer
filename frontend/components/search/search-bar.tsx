"use client"

import { useState, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import { useMovieContext } from '@/contexts/movie-context'
import { Button } from '@/components/ui/button'

export function SearchBar() {
  const { searchQuery, setSearchQuery, searchMoviesHandler, isLoading } = useMovieContext()
  const [inputValue, setInputValue] = useState(searchQuery)

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (inputValue !== searchQuery) {
        setSearchQuery(inputValue)
        if (inputValue.trim()) {
          searchMoviesHandler(inputValue)
        }
      }
    }, 500) // 500ms debounce

    return () => clearTimeout(timeoutId)
  }, [inputValue, searchQuery, setSearchQuery, searchMoviesHandler])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value)
  }

  const handleClear = () => {
    setInputValue('')
    setSearchQuery('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      searchMoviesHandler(inputValue)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-2xl mx-auto">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search for movies, genres, actors..."
          value={inputValue}
          onChange={handleInputChange}
          disabled={isLoading}
          className="w-full pl-12 pr-20 py-4 bg-gray-900/50 border border-gray-700 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-200 disabled:opacity-50"
        />
        {inputValue && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-14 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
        <Button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded-full px-4 py-2"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            'Search'
          )}
        </Button>
      </div>
    </form>
  )
}
