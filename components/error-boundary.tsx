"use client"

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  retryCount: number
}

export class ErrorBoundary extends Component<Props, State> {
  private retryTimeoutId: NodeJS.Timeout | null = null

  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('🚨 Error Boundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Log error details for debugging
    this.logErrorDetails(error, errorInfo)
  }

  componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId)
    }
  }

  private logErrorDetails = (error: Error, errorInfo: ErrorInfo) => {
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'Unknown',
      url: typeof window !== 'undefined' ? window.location.href : 'Unknown'
    }

    console.group('🚨 Error Boundary Details')
    console.error('Error:', error)
    console.error('Error Info:', errorInfo)
    console.error('Full Details:', errorDetails)
    console.groupEnd()

    // Store error in localStorage for debugging
    try {
      const existingErrors = JSON.parse(localStorage.getItem('cinescope_errors') || '[]')
      existingErrors.push(errorDetails)
      // Keep only last 10 errors
      const recentErrors = existingErrors.slice(-10)
      localStorage.setItem('cinescope_errors', JSON.stringify(recentErrors))
    } catch (storageError) {
      console.warn('Failed to store error in localStorage:', storageError)
    }
  }

  private handleRetry = () => {
    const { retryCount } = this.state
    
    if (retryCount >= 3) {
      console.warn('Maximum retry attempts reached')
      return
    }

    console.log(`🔄 Retrying... (attempt ${retryCount + 1}/3)`)
    
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: retryCount + 1
    })

    // Auto-retry after a delay for the first attempt
    if (retryCount === 0) {
      this.retryTimeoutId = setTimeout(() => {
        if (this.state.hasError) {
          this.handleRetry()
        }
      }, 2000)
    }
  }

  private handleReset = () => {
    console.log('🔄 Resetting error boundary')
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0
    })
  }

  private handleReload = () => {
    console.log('🔄 Reloading page')
    if (typeof window !== 'undefined') {
      window.location.reload()
    }
  }

  private getErrorType = (error: Error): string => {
    if (error.message.includes('ChunkLoadError') || error.message.includes('Loading chunk')) {
      return 'chunk_load'
    }
    if (error.message.includes('Network') || error.message.includes('fetch')) {
      return 'network'
    }
    if (error.message.includes('TypeError') && error.message.includes('Cannot read prop')) {
      return 'component'
    }
    return 'unknown'
  }

  private getErrorMessage = (error: Error): { title: string; description: string; suggestion: string } => {
    const errorType = this.getErrorType(error)

    switch (errorType) {
      case 'chunk_load':
        return {
          title: 'Loading Error',
          description: 'Failed to load application resources. This usually happens after an app update.',
          suggestion: 'Please refresh the page to load the latest version.'
        }
      case 'network':
        return {
          title: 'Connection Error',
          description: 'Unable to connect to the movie database server.',
          suggestion: 'Please check your internet connection and try again.'
        }
      case 'component':
        return {
          title: 'Display Error',
          description: 'A component failed to render properly.',
          suggestion: 'This is usually temporary. Try refreshing the page.'
        }
      default:
        return {
          title: 'Unexpected Error',
          description: 'Something went wrong while displaying this content.',
          suggestion: 'Please try refreshing the page or contact support if the problem persists.'
        }
    }
  }

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      const { title, description, suggestion } = this.getErrorMessage(this.state.error)
      const errorType = this.getErrorType(this.state.error)
      const canRetry = this.state.retryCount < 3

      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-gray-800/90 backdrop-blur-sm rounded-2xl border border-red-800/50 shadow-2xl">
            <div className="p-8 text-center">
              {/* Error Icon */}
              <div className="mb-6">
                <div className="mx-auto w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-8 h-8 text-red-400" />
                </div>
              </div>

              {/* Error Title */}
              <h1 className="text-2xl font-bold text-white mb-3">
                {title}
              </h1>

              {/* Error Description */}
              <p className="text-gray-300 mb-4 leading-relaxed">
                {description}
              </p>

              {/* Error Suggestion */}
              <p className="text-gray-400 text-sm mb-6">
                {suggestion}
              </p>

              {/* Action Buttons */}
              <div className="space-y-3">
                {canRetry && (
                  <button
                    onClick={this.handleRetry}
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Try Again ({3 - this.state.retryCount} attempts left)</span>
                  </button>
                )}

                <button
                  onClick={this.handleReload}
                  className="w-full bg-gray-700 hover:bg-gray-600 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh Page</span>
                </button>

                <button
                  onClick={() => window.location.href = '/'}
                  className="w-full bg-gray-600 hover:bg-gray-500 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
                >
                  <Home className="w-4 h-4" />
                  <span>Go Home</span>
                </button>
              </div>

              {/* Error Details (Development) */}
              {process.env.NODE_ENV === 'development' && (
                <details className="mt-6 text-left">
                  <summary className="cursor-pointer text-gray-400 hover:text-gray-300 flex items-center space-x-2">
                    <Bug className="w-4 h-4" />
                    <span>Error Details (Development)</span>
                  </summary>
                  <div className="mt-3 p-3 bg-gray-900/50 rounded-lg text-xs text-gray-300 font-mono overflow-auto max-h-40">
                    <div className="mb-2">
                      <strong>Error:</strong> {this.state.error.message}
                    </div>
                    {this.state.error.stack && (
                      <div className="mb-2">
                        <strong>Stack:</strong>
                        <pre className="whitespace-pre-wrap text-xs mt-1">
                          {this.state.error.stack}
                        </pre>
                      </div>
                    )}
                    {this.state.errorInfo?.componentStack && (
                      <div>
                        <strong>Component Stack:</strong>
                        <pre className="whitespace-pre-wrap text-xs mt-1">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}

              {/* Retry Count Indicator */}
              {this.state.retryCount > 0 && (
                <div className="mt-4 text-xs text-gray-500">
                  Retry attempts: {this.state.retryCount}/3
                </div>
              )}
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook for functional components to handle errors
export const useErrorHandler = () => {
  const handleError = React.useCallback((error: Error, errorInfo?: any) => {
    console.error('🚨 Error caught by useErrorHandler:', error, errorInfo)
    
    // Store error details
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      context: errorInfo
    }

    try {
      const existingErrors = JSON.parse(localStorage.getItem('cinescope_errors') || '[]')
      existingErrors.push(errorDetails)
      const recentErrors = existingErrors.slice(-10)
      localStorage.setItem('cinescope_errors', JSON.stringify(recentErrors))
    } catch (storageError) {
      console.warn('Failed to store error:', storageError)
    }
  }, [])

  return { handleError }
}

// Utility function to clear stored errors
export const clearStoredErrors = () => {
  try {
    localStorage.removeItem('cinescope_errors')
    console.log('✅ Cleared stored errors')
  } catch (error) {
    console.warn('Failed to clear stored errors:', error)
  }
}

// Utility function to get stored errors
export const getStoredErrors = () => {
  try {
    return JSON.parse(localStorage.getItem('cinescope_errors') || '[]')
  } catch (error) {
    console.warn('Failed to get stored errors:', error)
    return []
  }
}