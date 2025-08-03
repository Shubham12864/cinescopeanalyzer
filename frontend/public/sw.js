// Service Worker for Enhanced Image Caching
const CACHE_NAME = 'cinescopeanalyzer-v1'
const IMAGE_CACHE_NAME = 'cinescopeanalyzer-images-v1'
const API_CACHE_NAME = 'cinescopeanalyzer-api-v1'

// URLs to cache on install
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/manifest.json'
]

// Image domains to cache
const IMAGE_DOMAINS = [
  'image.tmdb.org',
  'm.media-amazon.com',
  'images-amazon.com'
]

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/movies/popular',
  '/api/movies/trending',
  '/api/movies/top-rated',
  '/api/movies/recent'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static assets')
        return cache.addAll(STATIC_ASSETS)
      })
      .then(() => self.skipWaiting())
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...')
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== IMAGE_CACHE_NAME && 
                cacheName !== API_CACHE_NAME) {
              console.log('Service Worker: Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      })
      .then(() => self.clients.claim())
  )
})

// Fetch event - intercept network requests
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Handle different types of requests
  if (isImageRequest(url)) {
    event.respondWith(handleImageRequest(request))
  } else if (isAPIRequest(url)) {
    event.respondWith(handleAPIRequest(request))
  } else if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request))
  } else {
    // Default: network first, then cache
    event.respondWith(
      fetch(request)
        .catch(() => caches.match(request))
    )
  }
})

// Check if request is for an image
function isImageRequest(url) {
  return (
    IMAGE_DOMAINS.some(domain => url.hostname.includes(domain)) ||
    url.pathname.includes('/api/images/') ||
    request.destination === 'image'
  )
}

// Check if request is for API data
function isAPIRequest(url) {
  return url.pathname.startsWith('/api/') && !url.pathname.includes('/api/images/')
}

// Check if request is for static asset
function isStaticAsset(url) {
  return (
    url.pathname.startsWith('/_next/') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.ico')
  )
}

// Handle image requests with aggressive caching
async function handleImageRequest(request) {
  const cache = await caches.open(IMAGE_CACHE_NAME)
  
  try {
    // Check cache first
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      console.log('Service Worker: Serving image from cache:', request.url)
      return cachedResponse
    }
    
    // Fetch from network
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      // Cache successful responses
      console.log('Service Worker: Caching image:', request.url)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.log('Service Worker: Image request failed:', error)
    
    // Try to return cached version
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return placeholder image
    return new Response(
      generatePlaceholderSVG(),
      {
        headers: {
          'Content-Type': 'image/svg+xml',
          'Cache-Control': 'public, max-age=300'
        }
      }
    )
  }
}

// Handle API requests with cache-first strategy for GET requests
async function handleAPIRequest(request) {
  const cache = await caches.open(API_CACHE_NAME)
  
  // Only cache GET requests
  if (request.method !== 'GET') {
    return fetch(request)
  }
  
  try {
    // For cached endpoints, try cache first
    const url = new URL(request.url)
    const shouldCacheFirst = API_ENDPOINTS.some(endpoint => 
      url.pathname.includes(endpoint)
    )
    
    if (shouldCacheFirst) {
      const cachedResponse = await cache.match(request)
      if (cachedResponse) {
        console.log('Service Worker: Serving API from cache:', request.url)
        
        // Refresh cache in background
        fetch(request)
          .then(response => {
            if (response.ok) {
              cache.put(request, response.clone())
            }
          })
          .catch(() => {}) // Ignore background refresh errors
        
        return cachedResponse
      }
    }
    
    // Fetch from network
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok && shouldCacheFirst) {
      // Cache successful API responses for 5 minutes
      const responseToCache = networkResponse.clone()
      const headers = new Headers(responseToCache.headers)
      headers.set('sw-cached-at', Date.now().toString())
      
      const cachedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: headers
      })
      
      cache.put(request, cachedResponse)
      console.log('Service Worker: Cached API response:', request.url)
    }
    
    return networkResponse
  } catch (error) {
    console.log('Service Worker: API request failed:', error)
    
    // Try to return cached version
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline response
    return new Response(
      JSON.stringify({ 
        error: 'Network unavailable', 
        offline: true,
        cached: false 
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  const cache = await caches.open(CACHE_NAME)
  
  try {
    // Check cache first
    const cachedResponse = await cache.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Fetch from network and cache
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    // Return cached version if available
    return cache.match(request)
  }
}

// Generate placeholder SVG for failed image requests
function generatePlaceholderSVG() {
  return `
    <svg width="300" height="450" xmlns="http://www.w3.org/2000/svg">
      <rect width="300" height="450" fill="#1f1f1f"/>
      <text x="150" y="200" font-family="Arial, sans-serif" font-size="20" fill="#666" text-anchor="middle">
        🎬
      </text>
      <text x="150" y="240" font-family="Arial, sans-serif" font-size="14" fill="#666" text-anchor="middle">
        Image Unavailable
      </text>
    </svg>
  `
}

// Message handler for cache management
self.addEventListener('message', (event) => {
  const { type, payload } = event.data
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting()
      break
      
    case 'CACHE_IMAGES':
      if (payload && payload.urls) {
        cacheImages(payload.urls)
      }
      break
      
    case 'CLEAR_CACHE':
      clearAllCaches()
      break
      
    case 'GET_CACHE_SIZE':
      getCacheSize().then(size => {
        event.ports[0].postMessage({ type: 'CACHE_SIZE', size })
      })
      break
  }
})

// Cache multiple images (for preloading)
async function cacheImages(urls) {
  const cache = await caches.open(IMAGE_CACHE_NAME)
  
  const cachePromises = urls.map(async (url) => {
    try {
      const request = new Request(url)
      const response = await fetch(request)
      
      if (response.ok) {
        await cache.put(request, response)
        console.log('Service Worker: Preloaded image:', url)
      }
    } catch (error) {
      console.log('Service Worker: Failed to preload image:', url, error)
    }
  })
  
  await Promise.allSettled(cachePromises)
}

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys()
  await Promise.all(cacheNames.map(name => caches.delete(name)))
  console.log('Service Worker: All caches cleared')
}

// Get total cache size
async function getCacheSize() {
  let totalSize = 0
  
  const cacheNames = await caches.keys()
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName)
    const keys = await cache.keys()
    
    for (const request of keys) {
      const response = await cache.match(request)
      if (response) {
        const blob = await response.blob()
        totalSize += blob.size
      }
    }
  }
  
  return totalSize
}