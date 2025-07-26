"use client"

import React from 'react'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

class ChunkErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Check if it's a chunk load error
    if (
      error.name === 'ChunkLoadError' ||
      error.message.includes('Loading chunk') ||
      error.message.includes('Loading CSS chunk')
    ) {
      return { hasError: true, error }
    }
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ChunkErrorBoundary caught an error:', error, errorInfo)
    
    // Auto-reload for chunk errors after a short delay
    if (
      error.name === 'ChunkLoadError' ||
      error.message.includes('Loading chunk') ||
      error.message.includes('Loading CSS chunk')
    ) {
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black flex items-center justify-center">
          <div className="text-center p-8 bg-gray-800 rounded-lg shadow-lg max-w-md mx-4">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Loading Error
            </h2>
            <p className="text-gray-300 mb-6">
              The application failed to load properly. This usually happens due to cached files.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                🔄 Reload Page
              </button>
              <button
                onClick={() => {
                  // Clear all caches
                  if ('caches' in window) {
                    caches.keys().then(names => {
                      names.forEach(name => caches.delete(name))
                    })
                  }
                  localStorage.clear()
                  sessionStorage.clear()
                  window.location.reload()
                }}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                🗑️ Clear Cache & Reload
              </button>
            </div>
            <div className="mt-4 text-xs text-gray-400">
              Error: {this.state.error?.message}
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ChunkErrorBoundary
