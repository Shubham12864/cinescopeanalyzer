"use client"

import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center p-8">
          <div className="max-w-md text-center">
            <div className="text-6xl mb-6">🎬</div>
            <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
            <p className="text-gray-400 mb-6">
              We're having trouble loading this part of CineScopeAnalyzer. 
              Please try refreshing the page.
            </p>
            <div className="space-y-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                Refresh Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false, error: undefined })}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                Try Again
              </button>
            </div>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 mb-2">
                  Error Details (Development)
                </summary>
                <pre className="text-xs text-red-400 bg-gray-900 p-3 rounded overflow-auto">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// React Suspense Fallback Component
export function LoadingFallback({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-red-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-400">{message}</p>
      </div>
    </div>
  )
}

// API Error Component
export function APIErrorFallback({ 
  error, 
  retry, 
  message = "Failed to load data" 
}: { 
  error?: Error
  retry?: () => void
  message?: string 
}) {
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 text-center">
      <div className="text-4xl mb-4">⚠️</div>
      <h3 className="text-lg font-semibold text-white mb-2">{message}</h3>
      <p className="text-gray-400 text-sm mb-4">
        There was a problem connecting to our servers. Please check your internet connection and try again.
      </p>
      
      {retry && (
        <button
          onClick={retry}
          className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded transition-colors"
        >
          Try Again
        </button>
      )}
      
      {process.env.NODE_ENV === 'development' && error && (
        <details className="mt-4 text-left">
          <summary className="cursor-pointer text-sm text-gray-500 mb-2">
            Technical Details
          </summary>
          <pre className="text-xs text-red-400 bg-gray-800 p-3 rounded overflow-auto">
            {error.toString()}
          </pre>
        </details>
      )}
    </div>
  )
}

// Movie Card Error Fallback
export function MovieCardErrorFallback() {
  return (
    <div className="bg-gray-900 rounded-lg aspect-[2/3] flex flex-col items-center justify-center p-4 text-center">
      <div className="text-4xl mb-2 opacity-50">🎬</div>
      <p className="text-sm text-gray-500">Failed to load movie</p>
    </div>
  )
}
