"use client"

import { useEffect } from 'react'

export default function ChunkErrorHandler() {
  useEffect(() => {
    // Handle runtime chunk errors
    const handleChunkError = (event: ErrorEvent) => {
      const { message, filename, error } = event
      
      if (
        message.includes('Loading chunk') ||
        message.includes('Loading CSS chunk') ||
        filename?.includes('_next/static') ||
        error?.name === 'ChunkLoadError'
      ) {
        console.warn('Chunk load error detected, attempting reload...', { message, filename })
        
        // Show user-friendly message
        const shouldReload = window.confirm(
          'The application needs to reload to fix a loading issue. Click OK to reload.'
        )
        
        if (shouldReload) {
          window.location.reload()
        }
      }
    }

    // Handle unhandled promise rejections (often chunk errors)
    const handlePromiseRejection = (event: PromiseRejectionEvent) => {
      const error = event.reason
      
      if (
        error?.message?.includes('Loading chunk') ||
        error?.name === 'ChunkLoadError' ||
        error?.stack?.includes('_next/static')
      ) {
        console.warn('Chunk load promise rejection, attempting reload...', error)
        event.preventDefault() // Prevent default error handling
        
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      }
    }

    // Add event listeners
    window.addEventListener('error', handleChunkError)
    window.addEventListener('unhandledrejection', handlePromiseRejection)

    // Cleanup
    return () => {
      window.removeEventListener('error', handleChunkError)
      window.removeEventListener('unhandledrejection', handlePromiseRejection)
    }
  }, [])

  return null // This component doesn't render anything
}
