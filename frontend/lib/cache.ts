/**
 * Client-side caching utility for search results and API responses
 */

interface CacheEntry<T> {
  data: T
  timestamp: number
  expiresAt: number
}

class ClientCache {
  private cache = new Map<string, CacheEntry<any>>()
  private readonly DEFAULT_TTL = 2 * 60 * 60 * 1000 // 2 hours in milliseconds

  /**
   * Set a cache entry with optional TTL
   */
  set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    const now = Date.now()
    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      expiresAt: now + ttl
    }
    
    this.cache.set(key, entry)
    console.log(`💾 Cache SET: ${key} (expires in ${ttl / 1000}s)`)
  }

  /**
   * Get a cache entry if it exists and hasn't expired
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    
    if (!entry) {
      console.log(`💾 Cache MISS: ${key}`)
      return null
    }

    const now = Date.now()
    if (now > entry.expiresAt) {
      console.log(`💾 Cache EXPIRED: ${key}`)
      this.cache.delete(key)
      return null
    }

    console.log(`💾 Cache HIT: ${key} (age: ${(now - entry.timestamp) / 1000}s)`)
    return entry.data as T
  }

  /**
   * Check if a key exists and is valid
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * Delete a specific cache entry
   */
  delete(key: string): boolean {
    const deleted = this.cache.delete(key)
    if (deleted) {
      console.log(`💾 Cache DELETE: ${key}`)
    }
    return deleted
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    const size = this.cache.size
    this.cache.clear()
    console.log(`💾 Cache CLEAR: ${size} entries removed`)
  }

  /**
   * Clean up expired entries
   */
  cleanup(): void {
    const now = Date.now()
    let cleaned = 0
    
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key)
        cleaned++
      }
    }
    
    if (cleaned > 0) {
      console.log(`💾 Cache CLEANUP: ${cleaned} expired entries removed`)
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const now = Date.now()
    let valid = 0
    let expired = 0
    
    for (const entry of this.cache.values()) {
      if (now > entry.expiresAt) {
        expired++
      } else {
        valid++
      }
    }
    
    return {
      total: this.cache.size,
      valid,
      expired
    }
  }

  /**
   * Generate cache key for search queries
   */
  static generateSearchKey(query: string, filters?: any): string {
    const normalizedQuery = query.toLowerCase().trim()
    const filterStr = filters ? JSON.stringify(filters) : ''
    return `search:${normalizedQuery}:${filterStr}`
  }

  /**
   * Generate cache key for movie details
   */
  static generateMovieKey(movieId: string): string {
    return `movie:${movieId}`
  }

  /**
   * Generate cache key for popular movies
   */
  static generatePopularKey(limit?: number): string {
    return `popular:${limit || 'all'}`
  }
}

// Create singleton instance
export const clientCache = new ClientCache()

// Cleanup expired entries every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(() => {
    clientCache.cleanup()
  }, 5 * 60 * 1000)
}

// Export the class for static method access
export { ClientCache }
export default clientCache