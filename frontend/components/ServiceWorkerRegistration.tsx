"use client"

import { useEffect } from 'react'

export function ServiceWorkerRegistration() {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      registerServiceWorker()
    }
  }, [])

  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      })

      console.log('Service Worker registered successfully:', registration)

      // Handle updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing

        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New service worker is available
              console.log('New service worker available')
              
              // Optionally show update notification to user
              if (window.confirm('A new version is available. Reload to update?')) {
                newWorker.postMessage({ type: 'SKIP_WAITING' })
                window.location.reload()
              }
            }
          })
        }
      })

      // Listen for service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        const { type, payload } = event.data
        
        switch (type) {
          case 'CACHE_SIZE':
            console.log('Cache size:', formatBytes(payload.size))
            break
        }
      })

    } catch (error) {
      console.error('Service Worker registration failed:', error)
    }
  }

  // Utility functions for cache management
  const preloadImages = (urls: string[]) => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'CACHE_IMAGES',
        payload: { urls }
      })
    }
  }

  const clearCache = () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'CLEAR_CACHE'
      })
    }
  }

  const getCacheSize = () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      const messageChannel = new MessageChannel()
      
      messageChannel.port1.onmessage = (event) => {
        console.log('Cache size:', formatBytes(event.data.size))
      }
      
      navigator.serviceWorker.controller.postMessage(
        { type: 'GET_CACHE_SIZE' },
        [messageChannel.port2]
      )
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Expose cache management functions globally for debugging
  if (typeof window !== 'undefined') {
    ;(window as any).cacheManager = {
      preloadImages,
      clearCache,
      getCacheSize
    }
  }

  return null // This component doesn't render anything
}

export default ServiceWorkerRegistration